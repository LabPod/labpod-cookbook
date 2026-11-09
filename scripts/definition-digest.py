#!/usr/bin/env python3
"""Compute LabPod's canonical v1 build-input digest for a Docker context.

This must agree byte-for-byte with LabPod's Go implementation
(`backend/internal/template/bundle/format.DefinitionDigest`), which is what
decides whether an imported bundle pulls its published image or builds
locally. A digest this helper computes differently is not a build failure —
it silently degrades every import to a local build. `tests/` pins the
divergence-prone cases (untagged FROM, scratch, stage aliases, ARG after the
first FROM, nested ARG expansion) against vectors produced by that Go code.
"""

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path, PurePosixPath


MAGIC = b"labpod.build-input.v1\0"
ARG_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
VARIABLE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def record(kind, key, value):
    fields = (
        kind.encode("utf-8") if isinstance(kind, str) else kind,
        key.encode("utf-8") if isinstance(key, str) else key,
        value.encode("utf-8") if isinstance(value, str) else value,
    )
    return b"".join(struct.pack(">Q", len(field)) + field for field in fields)


def dockerfile_raw_words(line):
    # Keep quotes and escapes: a literal "<<EOF" is not a heredoc operand.
    words = []
    start = index = 0
    quote = ""
    while index < len(line):
        char = line[index]
        if char == "\\" and quote != "'" and index + 1 < len(line):
            index += 1
        elif quote:
            if char == quote:
                quote = ""
        elif char in "'\"":
            quote = char
        elif char in " \t\r\n\v\f":
            if start < index:
                words.append(line[start:index])
            start = index + 1
        index += 1
    if quote:
        raise ValueError("unterminated quote in Dockerfile instruction")
    if start < len(line):
        words.append(line[start:])
    return words


def dockerfile_heredocs(line):
    if "<<" not in line:
        return []
    words = dockerfile_raw_words(line)
    if len(words) > 1 and words[0].upper() == "ONBUILD":
        words = words[1:]
    if len(words) < 2 or words[0].upper() not in {"RUN", "COPY", "ADD"}:
        return []
    args = words[1:]
    while args and args[0].startswith("--"):
        args = args[1:]
    try:
        json_args = json.loads(" ".join(args))
    except ValueError:
        pass
    else:
        if json_args is None or (
            isinstance(json_args, list) and all(isinstance(arg, str) for arg in json_args)
        ):
            return []
    docs = []
    for word in args:
        match = re.fullmatch(r"[0-9]*<<(-?)([^<]+)", word)
        if not match:
            continue
        raw = match[2]
        delimiter = ""
        quote = ""
        index = 0
        # Heredoc operands use shell backslash quoting even with # escape=`.
        while index < len(raw):
            char = raw[index]
            if char == "\\" and quote != "'" and index + 1 < len(raw):
                following = raw[index + 1]
                if quote == '"' and following not in '"$\\':
                    delimiter += char
                    index += 1
                    continue
                index += 1
                delimiter += following
            elif quote:
                if char == quote:
                    quote = ""
                else:
                    delimiter += char
            elif char in "'\"":
                quote = char
            else:
                delimiter += char
            index += 1
        docs.append((delimiter, match[1] == "-"))
    return docs


def logical_lines(contents):
    text = contents.decode("utf-8")
    physical = iter(text.replace("\r\n", "\n").split("\n"))
    current = ""
    escape = "\\"
    continued = False
    directives = True
    for raw in physical:
        trimmed = raw.strip()
        if not continued and directives:
            key, separator, value = trimmed.removeprefix("#").strip().partition("=")
            key, value = key.strip().lower(), value.strip()
            if trimmed.startswith("#") and separator and key in {"escape", "syntax", "check"}:
                if key == "escape":
                    if value not in {"\\", "`"}:
                        raise ValueError(f"unsupported Dockerfile escape directive: {value!r}")
                    escape = value
                elif key == "syntax" and not value:
                    raise ValueError("dockerfile syntax directive missing image reference")
                continue
            directives = False
        if trimmed.startswith("#") or (continued and not trimmed):
            continue
        segment = raw.rstrip(" \t\r")
        continued = segment.endswith(escape)
        current += segment[:-1] if continued else raw
        if continued:
            continue
        logical = current.strip()
        current = ""
        yield logical
        for delimiter, strip_tabs in dockerfile_heredocs(logical):
            for candidate in physical:
                if strip_tabs:
                    candidate = candidate.lstrip("\t")
                if candidate == delimiter:
                    break
            else:
                raise ValueError(f"unterminated Dockerfile heredoc {delimiter!r}")
    if continued:
        raise ValueError("dockerfile has dangling line continuation")


def parse_build_args(values):
    result = {}
    for item in values:
        name, separator, value = item.partition("=")
        if not separator or not ARG_NAME.fullmatch(name):
            raise ValueError(f"invalid build argument {item!r}; expected NAME=VALUE")
        if name in result:
            raise ValueError(f"duplicate build argument {name!r}")
        result[name] = value
    return result


def expand(raw, arguments):
    current = raw
    for _ in range(len(arguments) + 1):
        missing = []

        def replacement(match):
            name = match.group(1) or match.group(2)
            value = arguments.get(name, "")
            if not value:
                missing.append(name)
                return match.group(0)
            return value

        following = VARIABLE.sub(replacement, current)
        if missing:
            raise ValueError(f"unresolved FROM ARG {missing[0]}")
        if following == current:
            match = VARIABLE.search(following)
            if match:
                raise ValueError(f"cyclic FROM ARG {match.group(1) or match.group(2)}")
            return following
        current = following
    raise ValueError("cyclic FROM ARG expansion")


def normalize_reference(reference):
    if reference.lower() == "scratch":
        return "scratch"
    first, separator, _ = reference.partition("/")
    if not separator:
        normalized = "docker.io/library/" + reference
    elif "." in first or ":" in first or first == "localhost":
        normalized = reference
    else:
        normalized = "docker.io/" + reference
    if "@" in normalized:
        return normalized
    if normalized.rfind(":") <= normalized.rfind("/"):
        normalized += ":latest"
    return normalized


def external_base_images(dockerfile, explicit_build_args):
    arguments = {}
    aliases = set()
    images = []
    seen_from = False
    for line in logical_lines(dockerfile):
        fields = line.split()
        if not fields:
            continue
        instruction = fields[0].upper()
        if instruction == "ARG":
            if seen_from or len(fields) < 2:
                continue
            name, _, default = fields[1].partition("=")
            arguments[name] = explicit_build_args.get(name, default)
            continue
        if instruction != "FROM":
            continue

        seen_from = True
        rest = fields[1:]
        while rest and rest[0].startswith("--"):
            rest.pop(0)
        if not rest:
            raise ValueError("malformed FROM instruction")
        source = expand(rest[0], arguments)
        if source.lower() not in aliases:
            images.append(normalize_reference(source))
        if len(rest) >= 3 and rest[1].upper() == "AS":
            aliases.add(rest[2].lower())
    if not images:
        raise ValueError("Dockerfile has no external FROM image")
    return images


def context_files(context):
    dockerfile = context / "Dockerfile"
    if not dockerfile.is_file() or dockerfile.is_symlink():
        raise ValueError(f"{dockerfile} must be a regular file")
    if (context / ".dockerignore").exists():
        raise ValueError(".dockerignore is not supported by the v1 cookbook digest helper")
    entries = []
    for path in context.rglob("*"):
        if path == dockerfile or path.is_dir():
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"unsupported non-regular context entry: {path}")
        relative = PurePosixPath(path.relative_to(context).as_posix())
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"invalid context path: {relative}")
        entries.append((relative.as_posix(), path.read_bytes()))
    return dockerfile.read_bytes(), sorted(entries)


def definition_digest(context, build_args):
    dockerfile, context_entries = context_files(context)
    stream = bytearray(MAGIC)
    stream.extend(record("dockerfile", "Dockerfile", dockerfile))
    for path, contents in context_entries:
        stream.extend(record("context", path, contents))
    for name, value in sorted(build_args.items()):
        stream.extend(record("build-arg", name, value))
    for index, reference in enumerate(external_base_images(dockerfile, build_args)):
        stream.extend(record("base-image", str(index), reference))
    return "sha256:" + hashlib.sha256(stream).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=True, type=Path)
    parser.add_argument("--build-arg", action="append", default=[])
    parser.add_argument("--expect")
    args = parser.parse_args(argv)
    try:
        digest = definition_digest(args.context, parse_build_args(args.build_arg))
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    if args.expect and digest != args.expect:
        print(f"definition digest mismatch: got {digest}, want {args.expect}", file=sys.stderr)
        return 1
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

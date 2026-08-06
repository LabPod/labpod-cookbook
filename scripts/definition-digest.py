#!/usr/bin/env python3
"""Compute LabPod's canonical v1 build-input digest for a Docker context."""

import argparse
import hashlib
import re
import struct
import sys
from pathlib import Path, PurePosixPath


MAGIC = b"labpod.build-input.v1\0"
ARG_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
VARIABLE = re.compile(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))")


def record(kind, key, value):
    fields = (
        kind.encode("utf-8") if isinstance(kind, str) else kind,
        key.encode("utf-8") if isinstance(key, str) else key,
        value.encode("utf-8") if isinstance(value, str) else value,
    )
    return b"".join(struct.pack(">Q", len(field)) + field for field in fields)


def logical_lines(contents):
    pending = ""
    for raw_line in contents.decode("utf-8").splitlines():
        line = raw_line.rstrip()
        if line.endswith("\\"):
            pending += line[:-1] + " "
            continue
        yield pending + line
        pending = ""
    if pending:
        yield pending


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


def expand(value, arguments):
    def replacement(match):
        name = match.group(1) or match.group(2)
        if name not in arguments:
            raise ValueError(f"FROM references undefined build argument {name!r}")
        return arguments[name]

    return VARIABLE.sub(replacement, value)


def normalize_reference(reference):
    reference = reference.strip()
    if not reference:
        raise ValueError("empty FROM image reference")
    first, separator, remainder = reference.partition("/")
    if not separator:
        reference = "docker.io/library/" + reference
    elif "." not in first and ":" not in first and first != "localhost":
        reference = "docker.io/" + reference
    elif first == "index.docker.io":
        reference = "docker.io/" + remainder
    return reference


def external_base_images(dockerfile, explicit_build_args):
    arguments = {}
    aliases = set()
    images = []
    for line in logical_lines(dockerfile):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        instruction, separator, rest = stripped.partition(" ")
        if not separator:
            continue
        instruction = instruction.upper()
        rest = rest.strip()
        if instruction == "ARG":
            declaration = rest.split()[0]
            name, has_default, default = declaration.partition("=")
            if not ARG_NAME.fullmatch(name):
                raise ValueError(f"invalid ARG name {name!r}")
            if name in explicit_build_args:
                arguments[name] = explicit_build_args[name]
            elif has_default:
                arguments[name] = default
            continue
        if instruction != "FROM":
            continue

        fields = rest.split()
        while fields and fields[0].startswith("--"):
            fields.pop(0)
        if not fields:
            raise ValueError("FROM is missing its image reference")
        source = expand(fields[0], arguments)
        if source.lower() not in aliases:
            images.append(normalize_reference(source))
        if len(fields) >= 3 and fields[-2].upper() == "AS":
            aliases.add(fields[-1].lower())
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

#!/usr/bin/env python3
"""Generate index.json — the machine-readable catalogue of this repo's bundles.

LabPod's template gallery has two sections split by source: Built-in is the
catalogue embedded in the server binary, Cookbook is this repository. The
server never fetches it — the browser does (pkgpl/labpod#1177: no server SSRF
surface, and a LabPod server still needs no internet). So this file is the
whole contract between the two repos, served over raw.githubusercontent.com.

Every field is derived from the bundles themselves. Nothing here is
hand-maintained, because a hand-copied catalogue drifts from the bundles
silently and the first symptom is a gallery card that installs something
other than what it advertises. `tests/test_index.py` fails on any drift.

Usage:
  scripts/build-index.py            # rewrite index.json
  scripts/build-index.py --check    # exit 1 if index.json is stale
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "index.json"
RAW_BASE = "https://raw.githubusercontent.com/LabPod/labpod-cookbook/main"
REPO_BASE = "https://github.com/LabPod/labpod-cookbook/tree/main"

SCHEMA_VERSION = "1"


def bundle_dirs():
    return sorted(p.parent.parent for p in REPO_ROOT.glob("*/template/bundle.json"))


def entry_for(cookbook_dir):
    cookbook = cookbook_dir.name
    bundle = json.loads((cookbook_dir / "template" / "bundle.json").read_text())
    image = bundle.get("image") or {}
    published = image.get("published") or {}
    defaults = bundle.get("defaults") or {}

    tar_path = REPO_ROOT / "dist" / f"{cookbook}.labpod-bundle.tar"
    if not tar_path.is_file():
        raise SystemExit(f"error: {cookbook} has no built tar at {tar_path}")
    tar_bytes = tar_path.read_bytes()

    # The ref a researcher actually receives. A published bundle pulls its
    # pinned image; everything else resolves to the bundle's own ref, which
    # for a `localhost/` entry means an administrator has to build it.
    effective_ref = published.get("ref") or image.get("ref", "")

    entry = {
        "id": cookbook,
        "name": bundle.get("name", ""),
        "description": bundle.get("description", ""),
        "type": bundle.get("type", ""),
        "image": effective_ref,
        "published": bool(published),
        "requires_build": effective_ref.startswith("localhost/"),
        "gpu_required": bool(defaults.get("gpu_required", False)),
        "gpu_default": bool(defaults.get("gpu_default", False)),
        "ports": [p.get("name", "") for p in (bundle.get("ports") or [])],
        "bundle_url": f"{RAW_BASE}/dist/{cookbook}.labpod-bundle.tar",
        "bundle_bytes": len(tar_bytes),
        "bundle_sha256": "sha256:" + hashlib.sha256(tar_bytes).hexdigest(),
        "docs_url": f"{REPO_BASE}/{cookbook}",
    }
    if published.get("variants"):
        entry["image_variants"] = [v["ref"] for v in published["variants"]]
    return entry


def build():
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "labpod.cookbook.index",
        "bundles": [entry_for(d) for d in bundle_dirs()],
    }


def render(doc):
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = render(build())
    if not args.check:
        INDEX_PATH.write_text(rendered)
        return 0

    if not INDEX_PATH.is_file():
        print("error: index.json is missing; run scripts/build-index.py", file=sys.stderr)
        return 1
    if INDEX_PATH.read_text() != rendered:
        print(
            "error: index.json is stale; run scripts/build-index.py and commit the result",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

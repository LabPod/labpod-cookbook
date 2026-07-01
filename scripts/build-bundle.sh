#!/usr/bin/env bash
# Pack a cookbook's template/ directory into a LabPod template bundle tar.
# <cookbook-dir>/template/ holds bundle.json, README.md, and an optional
# context/ directory; <cookbook-dir>/notebook.ipynb sits outside it and is
# never bundled - see this repo's README for why.
#
# LabPod's bundle decoder expects a plain, uncompressed POSIX tar containing
# bundle.json, README.md, and an optional context/ directory - see
# docs/02-tech-spec.md §2.24 in the labpod repo for the authoritative format
# (size/entry-count caps, context/ extension whitelist, path-safety rules).
#
# Usage: scripts/build-bundle.sh <cookbook-dir>
set -euo pipefail

if [[ $# -ne 1 ]]; then
	echo "usage: $0 <cookbook-dir>" >&2
	exit 1
fi

cookbook_dir="${1%/}"
cookbook_id="$(basename "$cookbook_dir")"
template_dir="$cookbook_dir/template"

if [[ ! -f "$template_dir/bundle.json" ]]; then
	echo "error: $template_dir/bundle.json not found" >&2
	exit 1
fi
if [[ ! -f "$template_dir/README.md" ]]; then
	echo "error: $template_dir/README.md not found" >&2
	exit 1
fi

out_dir="dist"
out_file="$out_dir/${cookbook_id}.labpod-bundle.tar"
mkdir -p "$out_dir"

tar_args=(-cf "$out_file" -C "$template_dir" bundle.json README.md)
if [[ -d "$template_dir/context" ]]; then
	tar_args+=(context)
fi

tar "${tar_args[@]}"
echo "wrote $out_file"

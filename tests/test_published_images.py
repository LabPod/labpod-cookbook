import json
import os
import re
import subprocess
import tarfile
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATLAB = "matlab-deep-learning"
CUDA_COOKBOOKS = {"huggingface", "pytorch-scientific-ml"}
CUDA_LINES = {"cu121", "cu126", "cu129"}
REF_PATTERN = re.compile(
    r"^ghcr\.io/labpod/labpod-cookbook-[a-z0-9-]+:v[0-9]+-(?:cpu|cu12[169])$"
)
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


def bundle_directories():
    return sorted(path.parent.parent for path in ROOT.glob("*/template/bundle.json"))


def buildable_directories():
    return [path for path in bundle_directories() if (path / "template/context/Dockerfile").is_file()]


class PublishedBundleMetadataTest(unittest.TestCase):
    def test_every_redistributable_build_has_a_published_image(self):
        for cookbook in buildable_directories():
            with self.subTest(cookbook=cookbook.name):
                bundle = json.loads((cookbook / "template/bundle.json").read_text())
                published = bundle["image"].get("published")
                if cookbook.name == MATLAB:
                    self.assertIsNone(published)
                    continue

                self.assertIsInstance(published, dict)
                self.assertRegex(published["ref"], REF_PATTERN)
                self.assertNotIn(":latest", published["ref"])
                self.assertRegex(published["definition_digest"], DIGEST_PATTERN)
                variants = published.get("variants", [])
                expected_variant_count = 2 if cookbook.name in CUDA_COOKBOOKS else 0
                self.assertEqual(len(variants), expected_variant_count)
                for variant in variants:
                    self.assertRegex(variant["ref"], REF_PATTERN)
                    self.assertRegex(variant["definition_digest"], DIGEST_PATTERN)
                self.assertTrue(bundle["image"]["ref"].startswith("localhost/"))
                self.assertEqual(bundle["image"]["dockerfile"]["path"], "Dockerfile")

    def test_build_contexts_remain_in_the_bundle(self):
        for cookbook in buildable_directories():
            with self.subTest(cookbook=cookbook.name):
                self.assertTrue((cookbook / "template/context/Dockerfile").is_file())
                self.assertTrue(any((cookbook / "template/context").iterdir()))


class PublishingWorkflowTest(unittest.TestCase):
    INSPECTION_ERRORS = (
        "ERROR: unexpected status from HEAD request: 503 Service Unavailable",
        "ERROR: failed to authorize: 401 Unauthorized",
        "ERROR: failed to do request: dial tcp: connection refused",
        "ERROR: unexpected status from HEAD request: 429 Too Many Requests",
        "ERROR: httpReadSeeker: failed open: referenced content not found: not found",
    )

    def setUp(self):
        self.matrix = json.loads((ROOT / ".github/cookbook-image-matrix.json").read_text())
        self.workflow = (ROOT / ".github/workflows/publish-images.yml").read_text()

    def test_matrix_covers_every_published_bundle_and_cuda_line(self):
        variants = self.matrix["variants"]
        expected_buildable = {path.name for path in buildable_directories()} - {MATLAB}
        self.assertEqual({variant["cookbook"] for variant in variants}, expected_buildable)

        for cookbook in expected_buildable:
            with self.subTest(cookbook=cookbook):
                actual = {variant["cuda"] for variant in variants if variant["cookbook"] == cookbook}
                expected = CUDA_LINES if cookbook in CUDA_COOKBOOKS else {"cpu"}
                self.assertEqual(actual, expected)

    def test_matrix_uses_bundle_refs_and_canonical_definition_digests(self):
        for variant in self.matrix["variants"]:
            with self.subTest(variant=variant):
                self.assertRegex(variant["ref"], REF_PATTERN)
                self.assertRegex(variant["definition_digest"], DIGEST_PATTERN)
                self.assertNotIn(":latest", variant["ref"])

            if variant["cuda"] in {"cpu", "cu126"}:
                bundle = json.loads(
                    (ROOT / variant["cookbook"] / "template/bundle.json").read_text()
                )
                self.assertEqual(variant["ref"], bundle["image"]["published"]["ref"])
                self.assertEqual(
                    variant["definition_digest"],
                    bundle["image"]["published"]["definition_digest"],
                )
            else:
                bundle = json.loads(
                    (ROOT / variant["cookbook"] / "template/bundle.json").read_text()
                )
                declared = {
                    item["ref"]: item
                    for item in bundle["image"]["published"]["variants"]
                }
                declared_variant = declared[variant["ref"]]
                self.assertEqual(
                    declared_variant["definition_digest"], variant["definition_digest"]
                )
                name, value = variant["build_args"].split("=", 1)
                self.assertEqual(declared_variant["build_args"], {name: value})

    def test_workflow_builds_prs_but_only_pushes_trusted_main(self):
        self.assertIn("pull_request:", self.workflow)
        self.assertIn("packages: write", self.workflow)
        self.assertIn("github.ref == 'refs/heads/main'", self.workflow)
        self.assertIn("push: ${{ github.ref == 'refs/heads/main'", self.workflow)
        self.assertIn(".github/cookbook-image-matrix.json", self.workflow)
        pr_job = self.workflow.split("  build-pr:", 1)[1].split("  build-release:", 1)[0]
        release_job = self.workflow.split("  build-release:", 1)[1].split("  promote:", 1)[0]
        self.assertIn("push: false", pr_job)
        self.assertNotIn("packages: write", pr_job)
        self.assertIn("packages: write", release_job)

    def test_workflow_labels_and_checks_the_definition_digest(self):
        self.assertIn("ai.labpod.image.build-input-digest", self.workflow)
        self.assertIn("scripts/definition-digest.py", self.workflow)
        self.assertIn("definition_digest", self.workflow)

    def test_preflight_skips_matching_tags_and_rejects_conflicting_tags(self):
        preflight = self.workflow.split("  preflight:\n", 1)[1].split("  build-pr:\n", 1)[0]
        guard = preflight.split("      - name: Refuse to overwrite immutable release tags\n", 1)[1]
        script = textwrap.dedent(re.search(r"        run: \|\n((?:          .*\n|\n)+)", guard)[1])
        # Run the actual workflow shell offline; every Docker call is intercepted.
        mock_docker = """
docker() {
  [[ "$1 $2 $3" == 'buildx imagetools inspect' ]] || return 2
  if [[ "$4" == "$ERROR_REF" && -n "$INSPECT_ERROR" ]]; then
    echo "$INSPECT_ERROR" >&2
    return 1
  fi
  if ! jq -e --arg ref "$4" 'has($ref)' <<<"$PUBLISHED" >/dev/null; then
    echo "ERROR: $4: not found" >&2
    return 1
  fi
  if (( $# > 4 )); then
    [[ "$5 $6" == '--format {{json .Image.Config.Labels}}' ]] || return 2
    jq -c --arg ref "$4" '.[$ref]' <<<"$PUBLISHED"
  fi
}
"""
        variants = self.matrix["variants"]
        label = "ai.labpod.image.build-input-digest"
        published = {variant["ref"]: {label: variant["definition_digest"]} for variant in variants}
        unpublished = [variants[0], variants[3], variants[4]]
        mixed = {ref: labels for ref, labels in published.items() if ref not in {v["ref"] for v in unpublished}}
        cases = [
            ("all published", published, [], ""),
            ("mixed", mixed, unpublished, ""),
            ("all unpublished", {}, variants, ""),
            ("digest mismatch", {**published, variants[0]["ref"]: {label: "sha256:" + "0" * 64}}, None, ""),
            ("missing label", {**published, variants[0]["ref"]: {}}, None, ""),
            ("null labels", {**published, variants[0]["ref"]: None}, None, ""),
        ]
        cases += [(error, mixed, None, error) for error in self.INSPECTION_ERRORS]
        for name, existing, expected, inspection_error in cases:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "output"
                output.touch()
                result = subprocess.run(
                    ["bash", "-c", mock_docker + script],
                    cwd=ROOT,
                    env={
                        **os.environ,
                        "PUBLISHED": json.dumps(existing),
                        "GITHUB_OUTPUT": str(output),
                        "ERROR_REF": variants[1]["ref"],
                        "INSPECT_ERROR": inspection_error,
                    },
                    capture_output=True,
                    text=True,
                )
                if expected is None:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(inspection_error or "immutable release tag", result.stderr)
                    self.assertEqual(output.read_text(), "")
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    outputs = dict(line.split("=", 1) for line in output.read_text().splitlines())
                    self.assertIn("matrix", outputs)
                    self.assertIn("has_unpublished", outputs)
                    self.assertEqual(json.loads(outputs["matrix"]), {"include": expected})
                    self.assertEqual(outputs["has_unpublished"], str(bool(expected)).lower())

    def test_promotion_only_creates_a_confirmed_missing_tag(self):
        guard = self.workflow.split("      - name: Promote the validated candidate once\n", 1)[1]
        script = textwrap.dedent(re.search(r"        run: \|\n((?:          .*\n|\n)+)", guard)[1])
        # Synthetic manifests make an accidental overwrite observable without a registry.
        mock_docker = """
docker() {
  case "$*" in
    "buildx imagetools inspect $RELEASE_REF")
      if [[ -n "$INSPECT_ERROR" ]]; then
        echo "$INSPECT_ERROR" >&2
        return 1
      fi
      [[ -f "$RELEASE" ]] && return 0
      echo "ERROR: $RELEASE_REF: not found" >&2
      return 1 ;;
    "buildx imagetools create --tag $RELEASE_REF $CANDIDATE_REF")
      cp "$CANDIDATE" "$RELEASE" ;;
    "buildx imagetools inspect --raw $CANDIDATE_REF") cat "$CANDIDATE" ;;
    "buildx imagetools inspect --raw $RELEASE_REF") cat "$RELEASE" ;;
    *) return 2 ;;
  esac
}
"""
        cases = [("missing", False, ""), ("existing", True, "")]
        cases += [(error, True, error) for error in self.INSPECTION_ERRORS]
        for name, exists, inspection_error in cases:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as temporary:
                release = Path(temporary) / "release"
                candidate = Path(temporary) / "candidate"
                candidate.write_text("new-manifest")
                if exists:
                    release.write_text("old-manifest")
                result = subprocess.run(
                    ["bash", "-c", mock_docker + script],
                    env={
                        **os.environ,
                        "RELEASE_REF": "ghcr.io/example/cookbook:v1-cpu",
                        "CANDIDATE_REF": "ghcr.io/example/cookbook:v1-cpu-candidate-test",
                        "RELEASE": str(release),
                        "CANDIDATE": str(candidate),
                        "INSPECT_ERROR": inspection_error,
                    },
                    capture_output=True,
                    text=True,
                )
                if exists:
                    self.assertEqual(release.read_text(), "old-manifest")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(inspection_error or "immutable release tag", result.stderr)
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(release.read_text(), candidate.read_text())

    def test_release_jobs_and_access_probes_use_only_the_unpublished_matrix(self):
        preflight = self.workflow.split("  preflight:\n", 1)[1].split("  build-pr:\n", 1)[0]
        self.assertIn("matrix: ${{ steps.unpublished.outputs.matrix }}", preflight)
        self.assertIn("has_unpublished: ${{ steps.unpublished.outputs.has_unpublished }}", preflight)
        self.assertIn("id: unpublished", preflight)
        for name in ("Publish an access probe for every package", "Verify every package pulls anonymously"):
            step = preflight.split(f"      - name: {name}\n", 1)[1].split("      - name:", 1)[0]
            self.assertIn("if: steps.unpublished.outputs.has_unpublished == 'true'", step)
            self.assertIn("PUBLISH_MATRIX: ${{ steps.unpublished.outputs.matrix }}", step)
            self.assertIn(".include[].ref", step)
            self.assertNotIn(".github/cookbook-image-matrix.json", step)
        for name in ("build-release", "promote"):
            job = re.split(r"\n  [a-z-]+:\n", self.workflow.split(f"  {name}:\n", 1)[1], 1)[0]
            self.assertIn("needs.preflight.outputs.has_unpublished == 'true'", job)
            self.assertRegex(job, r"needs: \[[^\]\n]*\bpreflight\b[^\]\n]*\]")
            self.assertIn("matrix: ${{ fromJSON(needs.preflight.outputs.matrix) }}", job)
        pr_job = self.workflow.split("  build-pr:\n", 1)[1].split("  build-release:\n", 1)[0]
        self.assertIn("matrix: ${{ fromJSON(needs.contract.outputs.matrix) }}", pr_job)


class DefinitionDigestTest(unittest.TestCase):
    """Differential vectors against LabPod's Go `format.DefinitionDigest`.

    A digest this helper computes differently never surfaces as an error: the
    server just decides the definition was modified and builds locally forever.
    `digest_vectors.json` is generated from the Go implementation and covers the
    normalization rules the two could plausibly drift on.
    """

    def digest(self, context, build_args):
        arguments = []
        for name, value in build_args.items():
            arguments += ["--build-arg", f"{name}={value}"]
        return subprocess.run(
            [ROOT / "scripts/definition-digest.py", "--context", context, *arguments],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def test_matches_the_go_implementation_on_every_vector(self):
        vectors = json.loads((ROOT / "tests/digest_vectors.json").read_text())
        self.assertGreaterEqual(len(vectors), 10)
        for vector in vectors:
            with self.subTest(vector=vector["name"]), tempfile.TemporaryDirectory() as temporary:
                context = Path(temporary)
                (context / "Dockerfile").write_text(vector["dockerfile"])
                for relative, contents in vector["context"].items():
                    target = context / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(contents)
                self.assertEqual(self.digest(context, vector["build_args"]), vector["digest"])

    def test_malformed_heredoc_instructions_do_not_produce_a_digest(self):
        for instruction, error in (
            ("RUN <<-EOF\n EOF\n", "unterminated Dockerfile heredoc"),
            ("RUN <<''\n", "unterminated Dockerfile heredoc"),
            ("RUN <<'EOF\n", "unterminated quote"),
            ("RUN <<EOF \\\n", "dangling line continuation"),
        ):
            with self.subTest(instruction=instruction), tempfile.TemporaryDirectory() as temporary:
                context = Path(temporary)
                (context / "Dockerfile").write_text("FROM scratch\n" + instruction)
                result = subprocess.run(
                    [ROOT / "scripts/definition-digest.py", "--context", context],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn(error, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_every_shipped_context_reproduces_its_declared_digest(self):
        matrix = json.loads((ROOT / ".github/cookbook-image-matrix.json").read_text())
        for variant in matrix["variants"]:
            with self.subTest(ref=variant["ref"]):
                build_args = {}
                if variant["build_args"]:
                    name, value = variant["build_args"].split("=", 1)
                    build_args[name] = value
                context = ROOT / variant["cookbook"] / "template/context"
                self.assertEqual(self.digest(context, build_args), variant["definition_digest"])


class ShippedBundleTarTest(unittest.TestCase):
    """`dist/*.labpod-bundle.tar` is what researchers actually import.

    Editing `bundle.json` without rebuilding the tar leaves the published
    metadata stranded in the source tree, so the import keeps building locally
    while every other check here passes.
    """

    def bundled_files(self, cookbook):
        archive = ROOT / "dist" / f"{cookbook}.labpod-bundle.tar"
        self.assertTrue(archive.is_file(), f"missing {archive}")
        with tarfile.open(archive) as tar:
            return {
                member.name: tar.extractfile(member).read()
                for member in tar.getmembers()
                if member.isfile()
            }

    def test_every_tar_matches_its_source_template(self):
        for cookbook in bundle_directories():
            with self.subTest(cookbook=cookbook.name):
                bundled = self.bundled_files(cookbook.name)
                source = {}
                template = cookbook / "template"
                for path in template.rglob("*"):
                    if path.is_file():
                        source[path.relative_to(template).as_posix()] = path.read_bytes()
                self.assertEqual(bundled, source)

    def test_every_tar_carries_a_v2_manifest_without_the_retired_eula_gate(self):
        for cookbook in bundle_directories():
            with self.subTest(cookbook=cookbook.name):
                bundled = self.bundled_files(cookbook.name)
                manifest = json.loads(bundled["bundle.json"])
                self.assertEqual(manifest["schema_version"], "2")
                self.assertNotIn("requires_eula", manifest)


class BaseImagePinningTest(unittest.TestCase):
    IMMUTABLE_LABPOD_BASE = re.compile(r"^ghcr\.io/labpod/[a-z0-9-]+:v[0-9]+-[a-z0-9.]+$")

    def labpod_base_refs(self):
        for cookbook in buildable_directories():
            dockerfile = (cookbook / "template/context/Dockerfile").read_text()
            for match in re.finditer(r"ghcr\.io/labpod/\S+", dockerfile):
                yield cookbook.name, match.group(0)
        matrix = json.loads((ROOT / ".github/cookbook-image-matrix.json").read_text())
        for variant in matrix["variants"]:
            for match in re.finditer(r"ghcr\.io/labpod/\S+", variant["build_args"]):
                yield variant["cookbook"], match.group(0)

    def test_labpod_base_images_are_pinned_to_an_immutable_tag(self):
        refs = list(self.labpod_base_refs())
        self.assertTrue(refs)
        for cookbook, ref in refs:
            with self.subTest(cookbook=cookbook, ref=ref):
                # A floating base tag breaks the promise the definition digest
                # makes: the digest records the reference, not its contents, so
                # a moving base silently decouples a local rebuild from the
                # published image. labpod-images publishes immutable v<N>-* tags.
                self.assertRegex(ref, self.IMMUTABLE_LABPOD_BASE)


class PullSizeDocumentationTest(unittest.TestCase):
    def test_every_published_bundle_readme_lists_an_approximate_pull_size(self):
        for cookbook in buildable_directories():
            if cookbook.name == MATLAB:
                continue
            with self.subTest(cookbook=cookbook.name):
                readme = (cookbook / "template/README.md").read_text()
                self.assertRegex(readme, r"(?i)approximate pull size[^\n]*[0-9.]+\s*(?:MB|GB)")

    def test_matlab_explains_why_it_remains_a_local_build(self):
        readme = (ROOT / MATLAB / "template/README.md").read_text()
        self.assertRegex(readme, r"(?is)not published.*licen[cs].*redistribut")
        self.assertRegex(readme, r"(?i)local(?:ly)? build")


if __name__ == "__main__":
    unittest.main()

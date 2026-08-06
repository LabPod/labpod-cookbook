import json
import re
import subprocess
import tempfile
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


class DefinitionDigestTest(unittest.TestCase):
    def test_v1_framing_context_args_and_stage_alias_vector(self):
        with tempfile.TemporaryDirectory() as temporary:
            context = Path(temporary)
            (context / "Dockerfile").write_text(
                "ARG BASE=ubuntu:24.04\n"
                "FROM ${BASE} AS build\n"
                "COPY a.txt /a\n"
                "FROM build\n"
            )
            (context / "a.txt").write_bytes(b"hello\n")
            result = subprocess.run(
                [
                    ROOT / "scripts/definition-digest.py",
                    "--context",
                    context,
                    "--build-arg",
                    "Z=last",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertEqual(
            result.stdout.strip(),
            "sha256:89ce5e1e05a465b01e1b7d422c7886fcba08c8ab4be9ec1048d90171ae7575ca",
        )


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

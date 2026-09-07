import json
import re
import subprocess
import tarfile
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

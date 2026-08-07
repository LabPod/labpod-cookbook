"""index.json is the whole contract between this repo and LabPod's gallery.

LabPod's browser fetches it to render the Cookbook section, so a field that
drifts from the bundle it describes shows a researcher one thing and installs
another. These tests pin the properties that make the file safe to consume:
it must be regenerable, it must agree with every bundle.json, and the tar it
advertises must be the tar that is committed.
"""

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX = json.loads((REPO_ROOT / "index.json").read_text())
BUNDLE_DIRS = sorted(p.parent.parent for p in REPO_ROOT.glob("*/template/bundle.json"))


def entry(cookbook):
    for item in INDEX["bundles"]:
        if item["id"] == cookbook:
            return item
    raise AssertionError(f"index.json has no entry for {cookbook}")


class TestIndexIsRegenerable(unittest.TestCase):
    def test_committed_index_matches_the_generator(self):
        result = subprocess.run(
            ["python3", "scripts/build-index.py", "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_declares_its_schema(self):
        self.assertEqual(INDEX["schema_version"], "1")
        self.assertEqual(INDEX["kind"], "labpod.cookbook.index")


class TestIndexCoversEveryBundle(unittest.TestCase):
    def test_every_bundle_appears_exactly_once(self):
        listed = [item["id"] for item in INDEX["bundles"]]
        self.assertEqual(listed, sorted(d.name for d in BUNDLE_DIRS))
        self.assertEqual(len(listed), len(set(listed)))

    def test_no_entry_invents_a_bundle(self):
        for item in INDEX["bundles"]:
            self.assertTrue((REPO_ROOT / item["id"] / "template" / "bundle.json").is_file())


class TestEntriesAgreeWithTheirBundle(unittest.TestCase):
    def test_name_description_and_type_come_from_the_bundle(self):
        for cookbook_dir in BUNDLE_DIRS:
            bundle = json.loads((cookbook_dir / "template" / "bundle.json").read_text())
            item = entry(cookbook_dir.name)
            self.assertEqual(item["name"], bundle["name"], cookbook_dir.name)
            self.assertEqual(item["description"], bundle["description"], cookbook_dir.name)
            self.assertEqual(item["type"], bundle["type"], cookbook_dir.name)

    # The advertised ref is what the researcher actually receives: a published
    # bundle pulls its pinned image, anything else falls back to the bundle's
    # own ref. Getting this backwards would promise a pull and deliver a build.
    def test_image_is_the_ref_the_user_receives(self):
        for cookbook_dir in BUNDLE_DIRS:
            bundle = json.loads((cookbook_dir / "template" / "bundle.json").read_text())
            image = bundle.get("image") or {}
            published = image.get("published") or {}
            item = entry(cookbook_dir.name)
            expected = published.get("ref") or image.get("ref")
            self.assertEqual(item["image"], expected, cookbook_dir.name)
            self.assertEqual(item["published"], bool(published), cookbook_dir.name)

    def test_requires_build_tracks_a_localhost_ref(self):
        for item in INDEX["bundles"]:
            self.assertEqual(
                item["requires_build"], item["image"].startswith("localhost/"), item["id"]
            )

    def test_published_entries_never_require_a_build(self):
        for item in INDEX["bundles"]:
            if item["published"]:
                self.assertFalse(item["requires_build"], item["id"])

    def test_variants_match_the_published_block(self):
        for cookbook_dir in BUNDLE_DIRS:
            bundle = json.loads((cookbook_dir / "template" / "bundle.json").read_text())
            published = (bundle.get("image") or {}).get("published") or {}
            expected = [v["ref"] for v in published.get("variants", [])]
            item = entry(cookbook_dir.name)
            self.assertEqual(item.get("image_variants", []), expected, cookbook_dir.name)

    def test_ports_match_the_bundle(self):
        for cookbook_dir in BUNDLE_DIRS:
            bundle = json.loads((cookbook_dir / "template" / "bundle.json").read_text())
            expected = [p["name"] for p in (bundle.get("ports") or [])]
            self.assertEqual(entry(cookbook_dir.name)["ports"], expected, cookbook_dir.name)


class TestBundleArtifactIsTrustworthy(unittest.TestCase):
    # The browser fetches bundle_url and hands the bytes to LabPod's importer.
    # If the size or digest describes a different tar than the committed one,
    # an integrity check on the client is worse than useless.
    def test_size_and_digest_match_the_committed_tar(self):
        for item in INDEX["bundles"]:
            tar = REPO_ROOT / "dist" / f"{item['id']}.labpod-bundle.tar"
            payload = tar.read_bytes()
            self.assertEqual(item["bundle_bytes"], len(payload), item["id"])
            self.assertEqual(
                item["bundle_sha256"], "sha256:" + hashlib.sha256(payload).hexdigest(), item["id"]
            )

    def test_urls_point_at_this_repository_over_https(self):
        for item in INDEX["bundles"]:
            self.assertEqual(
                item["bundle_url"],
                "https://raw.githubusercontent.com/LabPod/labpod-cookbook/main"
                f"/dist/{item['id']}.labpod-bundle.tar",
                item["id"],
            )
            self.assertTrue(item["docs_url"].startswith("https://github.com/LabPod/labpod-cookbook/"))

    # LabPod rejects a bundle over 1 MiB, so an entry above the cap advertises
    # an import that cannot succeed.
    def test_every_bundle_is_within_labpod_import_cap(self):
        for item in INDEX["bundles"]:
            self.assertLessEqual(item["bundle_bytes"], 1024 * 1024, item["id"])


if __name__ == "__main__":
    unittest.main()

"""Exercise acquisition trust boundaries using small synthetic local files."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.acquisition import acquire, validate_archive, verify_manifest


class AcquisitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "config").mkdir()
        catalog = json.loads((ROOT / "config/datasets.json").read_text(encoding="utf-8"))
        (self.root / "config/datasets.json").write_text(json.dumps(catalog))

    def archive(self, member: str = "fixture.txt") -> Path:
        path = self.root / "fixture.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(member, "Synthetic fixture")
        return path

    def test_rejects_html_error_page(self) -> None:
        path = self.root / "blocked.zip"
        path.write_text("<html>Access denied</html>")
        with self.assertRaises(ValueError):
            validate_archive(path)

    def test_rejects_unsafe_zip_member(self) -> None:
        with self.assertRaises(ValueError):
            validate_archive(self.archive("../escape.txt"))

    def test_requires_workbook_container(self) -> None:
        with self.assertRaises(ValueError):
            validate_archive(self.archive(), workbook=True)

    def test_preserves_manifest_on_identical_reacquisition(self) -> None:
        source = self.archive()
        manifest = acquire(self.root, "onet_31_0", source)
        original = manifest.read_bytes()
        self.assertEqual(manifest, acquire(self.root, "onet_31_0", source))
        self.assertEqual(original, manifest.read_bytes())

    def test_detects_tampered_source(self) -> None:
        manifest = acquire(self.root, "onet_31_0", self.archive())
        _, asset = verify_manifest(self.root, manifest)
        asset.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "checksum"):
            verify_manifest(self.root, manifest)

    def test_rejects_manifest_outside_raw_directory(self) -> None:
        manifest = acquire(self.root, "onet_31_0", self.archive())
        metadata = json.loads(manifest.read_text())
        metadata["local_relative_path"] = "../../external.zip"
        manifest.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(ValueError, "inside data/raw"):
            verify_manifest(self.root, manifest)

    def test_rejects_changed_publisher_bytes_before_registering(self) -> None:
        with self.assertRaisesRegex(ValueError, "pinned snapshot"):
            acquire(self.root, "onet_31_0", self.archive(), expected_sha256="0" * 64)
        self.assertEqual(list((self.root / "data/manifest").glob("*.json")), [])

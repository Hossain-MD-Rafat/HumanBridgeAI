"""Acquire public core assets and register immutable, checksum-addressed manifests."""
from __future__ import annotations

import hashlib
import json
import logging
import shutil
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

LOGGER = logging.getLogger(__name__)
CORE_IDS = (
    "onet_31_0", "bls_oews_2025", "bls_projections_2025_2035",
    "onet_soc_crosswalk", "onet_nem_crosswalk",
)


def digest(path: Path) -> str:
    """Return a streaming SHA-256 fingerprint of local bytes."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate_archive(path: Path, workbook: bool = False) -> None:
    """Reject error pages, corrupt archives, unsafe members and oversized content."""
    if not zipfile.is_zipfile(path):
        raise ValueError("Expected ZIP/XLSX bytes; received another payload")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if not names:
            raise ValueError("Empty archive")
        total = 0
        for item in archive.infolist():
            parts = Path(item.filename.replace("\\", "/")).parts
            if item.filename.startswith(("/", "\\")) or ".." in parts or ":" in item.filename:
                raise ValueError("Unsafe archive member")
            total += item.file_size
        if total > 2_000_000_000:
            raise ValueError("Uncompressed content exceeds 2 GB limit")
        if workbook and "[Content_Types].xml" not in names:
            raise ValueError("Expected an XLSX workbook")
        bad_member = archive.testzip()
        if bad_member:
            raise ValueError(f"Corrupt ZIP member: {bad_member}")


def acquire(root: Path, dataset_id: str, local_file: Path | None = None,
            expected_sha256: str | None = None) -> Path:
    """Download one catalog asset, or register permitted manually downloaded bytes.

    Existing snapshots are never overwritten. The first catalog download URL is the
    core asset; state/metro wage extensions are deliberately not fetched here.
    """
    catalog = json.loads((root / "config/datasets.json").read_text(encoding="utf-8"))
    entry = next(item for item in catalog["datasets"] if item["id"] == dataset_id)
    if dataset_id not in CORE_IDS:
        raise ValueError("Only the five reviewed core assets are supported")
    url = entry["download_urls"][0]
    suffix = ".xlsx" if ".xlsx" in url else ".zip"
    raw_dir = root / "data/raw" / dataset_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=raw_dir) as temp_dir:
        temporary = Path(temp_dir) / ("download" + suffix)
        resolved_url = url
        if local_file is not None:
            shutil.copyfile(local_file, temporary)
        else:
            request = urllib.request.Request(url, headers={"User-Agent": "HumanBridgeAI/0.1"})
            with urllib.request.urlopen(request, timeout=45) as response:
                resolved_url = response.url
                with temporary.open("wb") as output:
                    size = 0
                    while chunk := response.read(1024 * 1024):
                        size += len(chunk)
                        if size > 250_000_000:
                            raise ValueError("Download exceeds 250 MB limit")
                        output.write(chunk)
        validate_archive(temporary, workbook=suffix == ".xlsx")
        checksum = digest(temporary)
        if expected_sha256 is not None and checksum != expected_sha256:
            raise ValueError("Publisher bytes differ from the pinned snapshot; review the new release")
        relative = Path("data/raw") / dataset_id / (checksum + suffix)
        destination = root / relative
        if destination.exists():
            if digest(destination) != checksum:
                raise ValueError("Existing content-addressed asset has changed")
        else:
            temporary.replace(destination)

    manifest_dir = root / "data/manifest"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / f"{dataset_id}-{checksum[:16]}.json"
    manifest = {
        "dataset_id": dataset_id, "release": entry["release"],
        "publisher": entry["publisher"], "landing_url": entry["landing_url"],
        "resolved_download_url": resolved_url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "local_relative_path": relative.as_posix(), "bytes": destination.stat().st_size,
        "sha256": checksum, "license_url": entry["license_url"],
        "license_review_status": entry["license_review_status"],
        "dictionary_url": entry["dictionary_url"], "coverage": entry["geography"],
        "taxonomy": entry["keys"], "acquisition_method": "manual" if local_file else "download",
        "validation": "ZIP CRC and safe members; workbook container if applicable",
        "notes": "Structural validation only; release labels require workbook review.",
    }
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous["sha256"] != checksum or previous["local_relative_path"] != relative.as_posix():
            raise ValueError("Manifest conflicts with acquired bytes")
    else:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("Registered %s: %s", dataset_id, checksum)
    return manifest_path


def verify_manifest(root: Path, path: Path) -> tuple[dict, Path]:
    """Resolve a manifest inside the project and verify bytes before ingestion."""
    manifest = json.loads(path.read_text(encoding="utf-8"))
    relative = Path(manifest["local_relative_path"])
    asset = (root / relative).resolve()
    if relative.is_absolute() or not asset.is_relative_to((root / "data/raw").resolve()):
        raise ValueError("Asset must be inside data/raw")
    if digest(asset) != manifest["sha256"]:
        raise ValueError("Asset checksum mismatch")
    return manifest, asset

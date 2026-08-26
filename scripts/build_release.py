#!/usr/bin/env python3
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from check_for_private_stuff import scan
from check_package import check_package


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "release", "__pycache__", ".pytest_cache"}


def included_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in SKIP_PARTS for part in relative.parts) or path.suffix == ".pyc":
            continue
        yield path, relative


def release_datetime(version):
    changelog = (ROOT / "CHANGELOG.md").read_text()
    match = re.search(rf"^## {re.escape(version)} [—-] (\d{{4}}-\d{{2}}-\d{{2}})$", changelog, re.MULTILINE)
    if not match:
        raise SystemExit(f"CHANGELOG.md needs a dated heading for version {version}")
    return datetime.strptime(match.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)


def main():
    errors = check_package(ROOT)
    if errors:
        raise SystemExit("Package check failed:\n" + "\n".join(errors))
    findings = scan(ROOT)
    if findings:
        raise SystemExit("Private-stuff check failed:\n" + "\n".join(f"{item['file']}: {item['reason']}" for item in findings))

    version = (ROOT / "VERSION").read_text().strip()
    released_at = release_datetime(version)
    zip_timestamp = (released_at.year, released_at.month, released_at.day, 0, 0, 0)
    release = ROOT / "release"
    release.mkdir(exist_ok=True)
    archive = release / f"make-brand-assets-for-me-{version}.zip"
    inventory = []
    files = list(included_files())
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for path, relative in files:
            name = Path("make-brand-assets-for-me") / relative
            info = zipfile.ZipInfo(str(name), date_time=zip_timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            package.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            inventory.append(str(name))

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    manifest = {
        "name": "make-brand-assets-for-me",
        "version": version,
        "built_at": released_at.isoformat(),
        "archive": archive.name,
        "sha256": digest,
        "file_count": len(inventory),
        "files": inventory,
    }
    (release / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(archive)
    print(f"sha256 {digest}")


if __name__ == "__main__":
    main()

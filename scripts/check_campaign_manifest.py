#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

from PIL import Image, UnidentifiedImageError


REQUIRED_TOP_LEVEL = (
    "schema_version",
    "campaign_id",
    "brand_id",
    "title",
    "launch_subject",
    "canonical_url",
    "cta",
    "utm",
    "source_facts",
    "assets",
)
FORBIDDEN_PUBLICATION_FIELDS = {
    "account_id",
    "provider_id",
    "public_url",
    "published_at",
    "publication_status",
    "retry_at",
}
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]{16,}"),
)


def _walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _load_placements(root):
    path = (
        Path(root)
        / "plugins/make-brand-assets-for-me/skills/brand-assets-make-launch-pack"
        / "references/channel-placements.json"
    )
    data = json.loads(path.read_text())
    return {item["id"]: item for item in data["placements"]}


def _duplicates(values):
    seen = set()
    duplicates = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _inside(child, parent):
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def check_campaign_manifest(root, manifest_path):
    root = Path(root).resolve()
    manifest_path = Path(manifest_path)
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    errors = []

    try:
        data = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        return [f"Cannot read campaign manifest: {error}"]

    if not isinstance(data, dict):
        return ["Campaign manifest must be a JSON object"]

    for field in REQUIRED_TOP_LEVEL:
        if field not in data:
            errors.append(f"Missing top-level field: {field}")

    for key, value in _walk(data):
        if key in FORBIDDEN_PUBLICATION_FIELDS:
            errors.append(f"Public manifest contains forbidden publication field: {key}")
        if isinstance(value, str) and any(pattern.search(value) for pattern in SECRET_PATTERNS):
            errors.append(f"Public manifest contains a token-like value in: {key}")

    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    canonical_url = data.get("canonical_url", "")
    if not isinstance(canonical_url, str) or not canonical_url.startswith("https://"):
        errors.append("canonical_url must use HTTPS")

    utm = data.get("utm")
    if not isinstance(utm, dict):
        errors.append("utm must be an object")
        utm = {}
    for field in ("source", "medium", "campaign"):
        if not isinstance(utm.get(field), str) or not utm.get(field, "").strip():
            errors.append(f"utm.{field} is required")

    facts = data.get("source_facts")
    if not isinstance(facts, list) or not facts:
        errors.append("source_facts must contain at least one approved fact")
        facts = []
    fact_ids = [fact.get("id") for fact in facts if isinstance(fact, dict)]
    for duplicate in _duplicates(fact_ids):
        errors.append(f"Duplicate source fact ID: {duplicate}")
    known_fact_ids = {value for value in fact_ids if isinstance(value, str) and value}

    try:
        placements = _load_placements(root)
    except (OSError, KeyError, json.JSONDecodeError) as error:
        errors.append(f"Cannot read channel placements: {error}")
        placements = {}

    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("assets must contain at least one file")
        assets = []
    asset_ids = [asset.get("id") for asset in assets if isinstance(asset, dict)]
    for duplicate in _duplicates(asset_ids):
        errors.append(f"Duplicate asset ID: {duplicate}")

    campaign_root = manifest_path.parent.resolve()
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            errors.append(f"Asset {index + 1} must be an object")
            continue
        asset_id = asset.get("id") or f"#{index + 1}"
        placement_id = asset.get("placement_id")
        placement = placements.get(placement_id)
        if not placement:
            errors.append(f"Asset {asset_id} uses unknown placement: {placement_id}")
        else:
            expected_width = placement["width"]
            expected_height = placement["height"]
            if asset.get("width") != expected_width or asset.get("height") != expected_height:
                errors.append(
                    f"Asset {asset_id} dimensions must match placement {placement_id}: "
                    f"{expected_width} x {expected_height}"
                )
            asset_format = str(asset.get("format", "")).lower()
            if asset_format not in placement.get("formats", []):
                errors.append(f"Asset {asset_id} format is not allowed for placement {placement_id}: {asset_format}")
            page_count = asset.get("page_count", 1)
            if page_count > placement.get("page_limit", 1):
                errors.append(f"Asset {asset_id} exceeds the placement page limit")

        alt_text = asset.get("alt_text")
        if not isinstance(alt_text, str) or not alt_text.strip():
            errors.append(f"Asset {asset_id} needs alt text")

        claim_ids = asset.get("claim_ids")
        if not isinstance(claim_ids, list) or not claim_ids:
            errors.append(f"Asset {asset_id} needs at least one claim ID")
        else:
            for claim_id in claim_ids:
                if claim_id not in known_fact_ids:
                    errors.append(f"Asset {asset_id} uses unknown claim ID: {claim_id}")

        raw_path = asset.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            errors.append(f"Asset {asset_id} needs a relative path")
            continue
        portable_path = PurePosixPath(raw_path)
        if portable_path.is_absolute() or ".." in portable_path.parts or "" in portable_path.parts:
            errors.append(f"Asset {asset_id} path must stay inside the campaign folder")
            continue
        file_path = campaign_root.joinpath(*portable_path.parts)
        try:
            resolved_path = file_path.resolve(strict=True)
        except OSError:
            errors.append(f"Asset {asset_id} file does not exist")
            continue
        if not _inside(resolved_path, campaign_root):
            errors.append(f"Asset {asset_id} path must stay inside the campaign folder")
            continue

        actual_digest = hashlib.sha256(resolved_path.read_bytes()).hexdigest()
        if asset.get("sha256") != actual_digest:
            errors.append(f"Asset {asset_id} SHA-256 does not match the saved file")

        asset_format = str(asset.get("format", "")).lower()
        if asset_format in {"png", "jpg", "jpeg", "gif"}:
            try:
                with Image.open(resolved_path) as image:
                    actual_width, actual_height = image.size
            except (OSError, UnidentifiedImageError):
                errors.append(f"Asset {asset_id} is not a readable image")
                continue
            expected_width = asset.get("width")
            expected_height = asset.get("height")
            if (actual_width, actual_height) != (expected_width, expected_height):
                errors.append(
                    f"Asset {asset_id} file is {actual_width} x {actual_height}, "
                    f"expected {expected_width} x {expected_height}"
                )

    return errors


def main():
    parser = argparse.ArgumentParser(description="Check a public launch campaign manifest and its saved files.")
    parser.add_argument("manifest")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check_campaign_manifest(args.root, args.manifest)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("PASS: campaign manifest, assets, facts, links, dimensions, and digests are valid.")


if __name__ == "__main__":
    main()

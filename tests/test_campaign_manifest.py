import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image


ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests/fixtures/campaign-manifest-valid.json"
SCRIPT = ROOT / "scripts/check_campaign_manifest.py"


def load_checker():
    assert SCRIPT.exists(), "Missing campaign manifest checker"
    spec = importlib.util.spec_from_file_location("check_campaign_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.check_campaign_manifest


def make_campaign(tmp_path):
    campaign = tmp_path / "campaign"
    asset = campaign / "assets/square-launch.png"
    asset.parent.mkdir(parents=True)
    Image.new("RGB", (1080, 1080), "#f4f0df").save(asset)

    data = json.loads(FIXTURE.read_text())
    data["assets"][0]["sha256"] = hashlib.sha256(asset.read_bytes()).hexdigest()
    manifest = campaign / "campaign-manifest.json"
    manifest.write_text(json.dumps(data, indent=2) + "\n")
    return campaign, manifest, data


def write_manifest(manifest, data):
    manifest.write_text(json.dumps(data, indent=2) + "\n")


def test_accepts_a_complete_manifest_with_real_asset_bytes(tmp_path):
    campaign, manifest, _ = make_campaign(tmp_path)
    check = load_checker()

    assert check(ROOT, manifest) == []


@pytest.mark.parametrize(
    ("case", "mutate", "expected"),
    [
        (
            "duplicate asset IDs",
            lambda data: data["assets"].append(copy.deepcopy(data["assets"][0])),
            "Duplicate asset ID: square-launch",
        ),
        (
            "path traversal",
            lambda data: data["assets"][0].update(path="../square-launch.png"),
            "Asset square-launch path must stay inside the campaign folder",
        ),
        (
            "missing file",
            lambda data: data["assets"][0].update(path="assets/missing.png"),
            "Asset square-launch file does not exist",
        ),
        (
            "declared dimension mismatch",
            lambda data: data["assets"][0].update(width=1079),
            "Asset square-launch dimensions must match placement social-square: 1080 x 1080",
        ),
        (
            "unknown placement",
            lambda data: data["assets"][0].update(placement_id="unknown-feed-shape"),
            "Asset square-launch uses unknown placement: unknown-feed-shape",
        ),
        (
            "missing alt text",
            lambda data: data["assets"][0].update(alt_text=""),
            "Asset square-launch needs alt text",
        ),
        (
            "missing claim IDs",
            lambda data: data["assets"][0].update(claim_ids=[]),
            "Asset square-launch needs at least one claim ID",
        ),
        (
            "unknown claim ID",
            lambda data: data["assets"][0].update(claim_ids=["fact-not-approved"]),
            "Asset square-launch uses unknown claim ID: fact-not-approved",
        ),
        (
            "non-HTTPS canonical URL",
            lambda data: data.update(canonical_url="http://example.com/launch"),
            "canonical_url must use HTTPS",
        ),
        (
            "missing UTM parameter",
            lambda data: data["utm"].update(medium=""),
            "utm.medium is required",
        ),
        (
            "provider publication field",
            lambda data: data.update(provider_id="remote-post-123"),
            "Public manifest contains forbidden publication field: provider_id",
        ),
        (
            "token-like value",
            lambda data: data["assets"][0].update(alt_text="sk-" + "exampleTokenValue1234567890"),
            "Public manifest contains a token-like value in: alt_text",
        ),
    ],
)
def test_rejects_invalid_public_campaign_contract(tmp_path, case, mutate, expected):
    _, manifest, data = make_campaign(tmp_path)
    mutate(data)
    write_manifest(manifest, data)
    check = load_checker()

    assert expected in check(ROOT, manifest), case


def test_rejects_real_image_dimension_mismatch(tmp_path):
    campaign, manifest, data = make_campaign(tmp_path)
    asset = campaign / data["assets"][0]["path"]
    Image.new("RGB", (1080, 1079), "#f4f0df").save(asset)
    data["assets"][0]["sha256"] = hashlib.sha256(asset.read_bytes()).hexdigest()
    write_manifest(manifest, data)
    check = load_checker()

    assert "Asset square-launch file is 1080 x 1079, expected 1080 x 1080" in check(ROOT, manifest)


def test_rejects_digest_mismatch(tmp_path):
    _, manifest, data = make_campaign(tmp_path)
    data["assets"][0]["sha256"] = "0" * 64
    write_manifest(manifest, data)
    check = load_checker()

    assert "Asset square-launch SHA-256 does not match the saved file" in check(ROOT, manifest)


def test_rejects_symlink_that_escapes_campaign_folder(tmp_path):
    campaign, manifest, data = make_campaign(tmp_path)
    outside = tmp_path / "outside.png"
    Image.new("RGB", (1080, 1080), "#f4f0df").save(outside)
    escaped = campaign / "assets/escaped.png"
    escaped.symlink_to(outside)
    data["assets"][0]["path"] = "assets/escaped.png"
    data["assets"][0]["sha256"] = hashlib.sha256(outside.read_bytes()).hexdigest()
    write_manifest(manifest, data)
    check = load_checker()

    assert "Asset square-launch path must stay inside the campaign folder" in check(ROOT, manifest)

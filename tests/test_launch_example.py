import importlib.util
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).parents[1]
CAMPAIGN = ROOT / "examples/launch-pack/lemonbrand"
SCRIPT = ROOT / "scripts/build_launch_example.py"


def load_builder():
    assert SCRIPT.exists(), "Missing deterministic launch-pack builder"
    spec = importlib.util.spec_from_file_location("build_launch_example", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_launch_pack


def load_builder_module():
    assert SCRIPT.exists(), "Missing deterministic launch-pack builder"
    spec = importlib.util.spec_from_file_location("build_launch_example_module", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builds_the_complete_lemonbrand_launch_pack():
    build_launch_pack = load_builder()

    result = build_launch_pack(ROOT, CAMPAIGN)

    required_assets = {
        "profile-avatar.png": (400, 400),
        "cover-wide.png": (1500, 500),
        "linkedin-profile-cover.png": (1584, 396),
        "linkedin-page-cover.png": (4200, 700),
        "social-square.png": (1080, 1080),
        "social-portrait.png": (1080, 1350),
        "social-landscape.png": (1200, 627),
        "story-vertical.png": (1080, 1920),
        "open-graph.png": (1200, 630),
        "email-header.png": (1200, 600),
        "product-hunt-thumbnail.png": (240, 240),
        "product-hunt-gallery-01.png": (1270, 760),
        "product-hunt-gallery-02.png": (1270, 760),
        "youtube-thumbnail.png": (3840, 2160),
    }
    for filename, size in required_assets.items():
        path = CAMPAIGN / "assets" / filename
        assert path.exists(), filename
        with Image.open(path) as image:
            assert image.size == size

    linkedin_pages = sorted((CAMPAIGN / "carousels/linkedin").glob("page-*.png"))
    social_pages = sorted((CAMPAIGN / "carousels/social").glob("page-*.png"))
    assert len(linkedin_pages) == 5
    assert len(social_pages) == 10
    assert all(Image.open(path).size == (1080, 1350) for path in linkedin_pages)
    assert all(Image.open(path).size == (1080, 1080) for path in social_pages)
    assert (CAMPAIGN / "carousels/linkedin/make-brand-assets-for-me.pdf").exists()
    assert (CAMPAIGN / "proofs/contact-sheet.png").exists()

    manifest_path = CAMPAIGN / "campaign-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    assert result["manifest"] == str(manifest_path)
    assert manifest["schema_version"] == "1.0"
    assert manifest["canonical_url"] == "https://github.com/Lemonbrand/make-brand-assets-for-me"
    assert manifest["cta"] == {
        "label": "Get the free inbox audit",
        "action": "Book a free 60-minute inbox audit",
    }
    assert len(manifest["assets"]) == 30


def test_launch_copy_has_one_supported_offer_and_clear_labels():
    load_builder()(ROOT, CAMPAIGN)
    copy = json.loads((CAMPAIGN / "copy.json").read_text())
    source_facts = json.loads((CAMPAIGN / "source-facts.json").read_text())
    fact_ids = {fact["id"] for fact in source_facts["facts"]}

    assert {item["channel"] for item in copy["posts"]} >= {
        "linkedin",
        "instagram",
        "facebook",
        "x",
        "youtube",
        "product-hunt",
        "email",
    }
    assert all(item["claim_ids"] for item in copy["posts"])
    assert all(set(item["claim_ids"]) <= fact_ids for item in copy["posts"])
    assert all("utm_source=" in item["url"] for item in copy["posts"])
    assert all("—" not in json.dumps(item) for item in copy["posts"])
    assert "fictional" in json.dumps(source_facts).lower()


def test_generated_manifest_passes_the_public_checker():
    load_builder()(ROOT, CAMPAIGN)
    spec = importlib.util.spec_from_file_location(
        "check_campaign_manifest", ROOT / "scripts/check_campaign_manifest.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.check_campaign_manifest(ROOT, CAMPAIGN / "campaign-manifest.json") == []


def test_small_product_thumbnail_uses_a_readable_single_mark():
    load_builder()(ROOT, CAMPAIGN)
    with Image.open(CAMPAIGN / "assets/product-hunt-thumbnail.png") as image:
        pixels = list(image.convert("RGB").get_flattened_data())
    orange_pixels = sum(pixel == (230, 126, 34) for pixel in pixels)

    assert orange_pixels / len(pixels) > 0.35


def test_carousel_preview_and_body_regions_do_not_overlap():
    module = load_builder_module()

    regions = module.carousel_regions(1080, 1350, has_preview=True)

    assert regions["body"][1] + regions["body"][3] <= regions["preview"][1]


def test_package_gate_requires_the_worked_launch_manifest(tmp_path):
    spec = importlib.util.spec_from_file_location("check_package", ROOT / "scripts/check_package.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert (
        "Missing: examples/launch-pack/lemonbrand/campaign-manifest.json"
        in module.check_package(tmp_path)
    )


def test_two_launch_builds_have_identical_public_digests():
    build = load_builder()
    build(ROOT, CAMPAIGN)
    first = json.loads((CAMPAIGN / "campaign-manifest.json").read_text())
    first_digests = {asset["id"]: asset["sha256"] for asset in first["assets"]}

    build(ROOT, CAMPAIGN)
    second = json.loads((CAMPAIGN / "campaign-manifest.json").read_text())
    second_digests = {asset["id"]: asset["sha256"] for asset in second["assets"]}

    assert second_digests == first_digests

import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(__file__).parents[1]
CAMPAIGN = ROOT / "examples/launch-pack/lemonbrand"
SCRIPT = ROOT / "scripts/build_launch_example.py"
FONT = ROOT / "plugins/make-brand-assets-for-me/assets/fonts/InstrumentSans-Variable.ttf"


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


def test_generated_background_masters_have_real_negative_space():
    backgrounds = CAMPAIGN / "backgrounds"
    protected_regions = {
        "landscape-16x9.png": lambda w, h: (int(w * .55), 0, w, h),
        "banner-3x1.png": lambda w, h: (0, 0, int(w * .55), h),
        "square-1x1.png": lambda w, h: (0, 0, int(w * .52), int(h * .52)),
        "portrait-4x5.png": lambda w, h: (0, 0, w, int(h * .52)),
        "vertical-9x16.png": lambda w, h: (0, 0, w, int(h * .52)),
    }

    assert {path.name for path in backgrounds.glob("*.png")} == set(protected_regions)
    for filename, region in protected_regions.items():
        with Image.open(backgrounds / filename) as image:
            assert min(image.size) >= 800
            quiet = image.convert("RGB").crop(region(*image.size))
            assert max(ImageStat.Stat(quiet).stddev) < 12, filename


def test_every_raster_uses_a_background_and_fewer_than_fifteen_overlay_words():
    load_builder()(ROOT, CAMPAIGN)
    manifest = json.loads((CAMPAIGN / "campaign-manifest.json").read_text())

    for asset in manifest["assets"]:
        if asset["format"] != "png":
            continue
        receipt = json.loads((CAMPAIGN / "receipts" / f"{asset['id']}.json").read_text())
        background = CAMPAIGN / receipt["background_source"]
        assert background.exists(), asset["id"]
        assert background.parent.name == "backgrounds"
        assert 0 <= receipt["overlay_word_count"] < 15, asset["id"]


def test_every_raster_uses_the_bundled_bold_condensed_brand_font():
    load_builder()(ROOT, CAMPAIGN)
    manifest = json.loads((CAMPAIGN / "campaign-manifest.json").read_text())

    assert FONT.exists()
    for asset in manifest["assets"]:
        if asset["format"] != "png":
            continue
        receipt = json.loads((CAMPAIGN / "receipts" / f"{asset['id']}.json").read_text())
        assert receipt["font"] == {
            "family": "Instrument Sans",
            "file": "plugins/make-brand-assets-for-me/assets/fonts/InstrumentSans-Variable.ttf",
            "license": "SIL Open Font License 1.1",
            "weight": 700,
            "width": 82,
            "variation_applied": True,
        }


def test_launch_builder_refuses_to_fall_back_when_the_brand_font_is_missing(tmp_path):
    module = load_builder_module()

    missing = tmp_path / "missing-font.ttf"
    try:
        module.load_brand_font(36, path=missing)
    except FileNotFoundError as error:
        assert str(missing) in str(error)
    else:
        raise AssertionError("A missing brand font must fail instead of using a generic fallback")


def test_finished_pngs_use_a_compact_indexed_palette():
    load_builder()(ROOT, CAMPAIGN)

    with Image.open(CAMPAIGN / "assets/social-square.png") as image:
        assert image.mode == "P"
        assert len(image.getcolors(maxcolors=256)) <= 256


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

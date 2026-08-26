import json
import importlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load_function(module_name, function_name):
    assert (SCRIPTS / f"{module_name}.py").exists(), f"Missing script: {module_name}.py"
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def test_png_reports_alpha_and_padding(tmp_path):
    inspect_png = load_function("check_png", "inspect_png")
    path = tmp_path / "cutout.png"
    image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle((20, 20, 79, 79), fill=(0, 0, 0, 255))
    image.save(path)

    report = inspect_png(path)

    assert report["has_alpha"] is True
    assert report["padding_px"] == {
        "left": 20,
        "top": 20,
        "right": 20,
        "bottom": 20,
    }
    assert len(report["sha256"]) == 64


def test_copy_space_finds_intrusion_and_writes_overlay(tmp_path):
    check_copy_space = load_function("check_copy_space", "check_copy_space")
    path = tmp_path / "scene.png"
    overlay = tmp_path / "proof.png"
    image = Image.new("RGB", (100, 50), "white")
    ImageDraw.Draw(image).rectangle((80, 10, 90, 20), fill="black")
    image.save(path)

    report = check_copy_space(path, "right", 55, overlay)

    assert report["clean"] is False
    assert report["changed_pixels"] > 0
    assert overlay.exists()


def test_brand_rules_reports_missing_required_fields(tmp_path):
    check_brand_rules = load_function("check_brand_rules", "check_brand_rules")
    path = tmp_path / "brand-rules.yaml"
    path.write_text('version: "1.0"\nbrand_name: "Example"\n')
    errors = check_brand_rules(path)
    assert "Missing key: references" in errors
    assert "Missing key: look" in errors
    assert "Missing key: rights" in errors


def test_asset_record_accepts_complete_record(tmp_path):
    check_asset_record = load_function("check_asset_record", "check_asset_record")
    output = tmp_path / "asset.png"
    Image.new("RGBA", (20, 20), (0, 0, 0, 0)).save(output)
    record = {
        "version": "1.0",
        "asset_job": "human approval",
        "brand_id": "example",
        "route": "new",
        "parts": [{"name": "check", "source": "new"}],
        "prompt": "A clear approval symbol",
        "output_path": "asset.png",
        "checks": {"result": "pass"},
        "publish_status": "review_required",
    }
    path = tmp_path / "asset-record.json"
    path.write_text(json.dumps(record))
    assert check_asset_record(path) == []


def test_shared_rule_sync_detects_and_repairs_drift(tmp_path):
    sync_shared_rules = load_function("sync_shared_rules", "sync_shared_rules")
    root = tmp_path
    master = root / "source/shared-rules"
    master.mkdir(parents=True)
    (master / "five-steps.md").write_text("SHOW PLAN MAKE CHECK SAVE\n")
    skill = root / "plugins/make-brand-assets-for-me/skills/example"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text("skill\n")

    assert sync_shared_rules(root, check_only=True)
    assert sync_shared_rules(root, check_only=False) == []
    assert sync_shared_rules(root, check_only=True) == []


def test_contact_sheet_has_requested_canvas(tmp_path):
    make_contact_sheet = load_function("make_contact_sheet", "make_contact_sheet")
    paths = []
    for index, color in enumerate(("red", "blue")):
        path = tmp_path / f"asset-{index}.png"
        Image.new("RGB", (80, 80), color).save(path)
        paths.append(path)
    output = tmp_path / "sheet.png"
    make_contact_sheet(paths, output, title="Two assets", columns=2)
    with Image.open(output) as sheet:
        assert sheet.width == 1200
        assert sheet.height > 500


def test_schema_files_have_required_fields():
    schema_dir = ROOT / "source/schemas"
    brand = json.loads((schema_dir / "brand-rules.schema.json").read_text())
    record = json.loads((schema_dir / "asset-record.schema.json").read_text())
    assert set(brand["required"]) >= {"version", "brand_name", "references", "look", "rights"}
    assert set(record["required"]) >= {"asset_job", "route", "output_path", "checks"}

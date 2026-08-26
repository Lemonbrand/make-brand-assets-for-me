import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_baseline_has_ten_pngs():
    files = sorted((ROOT / "examples/gallery/outputs").glob("*.png"))
    assert len(files) == 10


def test_every_png_has_a_valid_record():
    outputs = {path.name for path in (ROOT / "examples/gallery/outputs").glob("*.png")}
    records = sorted((ROOT / "examples/records").glob("*.json"))
    assert len(records) == 10
    recorded_outputs = set()
    for path in records:
        data = json.loads(path.read_text())
        output = (path.parent / data["output_path"]).resolve()
        assert output.exists()
        recorded_outputs.add(output.name)
        assert data["publish_status"] in {"approved", "baseline"}
        assert data["checks"]["format"] == "pass"
    assert recorded_outputs == outputs


def test_gallery_has_four_proof_sheets_and_three_screenshots():
    assert len(list((ROOT / "examples/gallery/proofs").glob("*.png"))) == 4
    plugin_assets = ROOT / "plugins/make-brand-assets-for-me/assets"
    assert len(list(plugin_assets.glob("screenshot-*.png"))) == 3

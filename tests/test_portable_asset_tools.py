import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/make-brand-assets-for-me"
FONT = PLUGIN / "assets/fonts/InstrumentSans-Variable.ttf"
COPY_SKILLS = {
    "brand-assets-make-scene",
    "brand-assets-make-launch-pack",
}
PORTABLE_TOOLS = {"compose_text_overlay.py", "check_background_fit.py"}


def load_compositor():
    path = ROOT / "scripts/compose_text_overlay.py"
    assert path.exists(), "Missing canonical exact-copy compositor"
    spec = importlib.util.spec_from_file_location("compose_text_overlay", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_copy_bearing_skills_ship_the_same_self_contained_compositor(tmp_path):
    for name in PORTABLE_TOOLS:
        canonical = ROOT / "scripts" / name
        expected = hashlib.sha256(canonical.read_bytes()).hexdigest()
        for skill in COPY_SKILLS:
            for base in (PLUGIN / "skills", ROOT / "skills"):
                script = base / skill / "scripts" / name
                assert script.exists(), script
                assert hashlib.sha256(script.read_bytes()).hexdigest() == expected
                result = subprocess.run(
                    [sys.executable, str(script), "--help"],
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert result.returncode == 0, result.stderr


def test_compositor_fails_closed_on_font_identity_safe_area_and_contrast(tmp_path):
    overlay = load_compositor()
    background = tmp_path / "background.png"
    Image.new("RGB", (600, 400), "#f2ede2").save(background)
    digest = hashlib.sha256(FONT.read_bytes()).hexdigest()
    common = {
        "background": background,
        "output": tmp_path / "output.png",
        "text": "MAKE THE IMAGE WORK",
        "font_path": FONT,
        "font_family": "Instrument Sans",
        "font_sha256": digest,
        "box": (70, 70, 460, 260),
        "safe_area": {"top": 50, "right": 50, "bottom": 50, "left": 50},
        "weight": 700,
        "width": 82,
        "color": "#171526",
    }

    with pytest.raises(ValueError, match="SHA-256"):
        overlay.compose(**{**common, "font_sha256": "0" * 64})
    with pytest.raises(ValueError, match="family"):
        overlay.compose(**{**common, "font_family": "Arial"})
    with pytest.raises(ValueError, match="safe area"):
        overlay.compose(**{**common, "box": (20, 20, 460, 260)})
    with pytest.raises(ValueError, match="contrast"):
        overlay.compose(**{**common, "color": "#eee9df", "min_contrast": 3.0})
    with pytest.raises(ValueError, match="minimum contrast"):
        overlay.compose(**{**common, "min_contrast": 0.0})
    with pytest.raises(ValueError, match="finite"):
        overlay.compose(**{**common, "min_contrast": float("nan")})
    with pytest.raises(ValueError, match="contrast"):
        overlay.compose(**{**common, "color": "#00000000"})
    with pytest.raises(ValueError, match="Weight"):
        overlay.compose(**{**common, "weight": 900})


def test_compositor_receipt_records_observed_evidence(tmp_path):
    overlay = load_compositor()
    background = tmp_path / "background.png"
    output = tmp_path / "output.png"
    Image.new("RGB", (600, 400), "#f2ede2").save(background)
    digest = hashlib.sha256(FONT.read_bytes()).hexdigest()

    result = overlay.compose(
        background=background,
        output=output,
        text="MAKE THE IMAGE WORK",
        font_path=FONT,
        font_family="Instrument Sans",
        font_sha256=digest,
        box=(70, 70, 460, 260),
        safe_area={"top": 50, "right": 50, "bottom": 50, "left": 50},
        weight=700,
        width=82,
        color="#171526",
    )

    assert output.exists()
    assert result["font"]["family"] == "Instrument Sans"
    assert result["font"]["sha256"] == digest
    assert result["font"]["applied_axes"] == {"weight": 700, "width": 82}
    assert result["word_count"] == 4
    assert result["text_bounds"][0] >= result["safe_rectangle"][0]
    assert result["text_bounds"][1] >= result["safe_rectangle"][1]
    assert result["contrast"]["p10_ratio"] >= 3.0
    assert result["checks"] == {
        "font_identity": "pass",
        "safe_area": "pass",
        "contrast": "pass",
        "copy_length": "pass",
    }


def test_compositor_accounts_for_font_offsets_when_fitting_the_box(tmp_path):
    overlay = load_compositor()
    background = tmp_path / "linkedin-cover-background.png"
    output = tmp_path / "linkedin-cover.png"
    Image.new("RGB", (1584, 396), "#f2ede2").save(background)
    digest = hashlib.sha256(FONT.read_bytes()).hexdigest()

    result = overlay.compose(
        background=background,
        output=output,
        text="YOUR BRAND SHOULD NOT START OVER",
        font_path=FONT,
        font_family="Instrument Sans",
        font_sha256=digest,
        box=(360, 67, 550, 269),
        safe_area={"top": 48, "right": 80, "bottom": 48, "left": 360},
        weight=700,
        width=82,
        color="#171526",
        max_size=102,
        min_size=12,
    )

    x, y, width, height = result["text_box"]
    left, top, right, bottom = result["text_bounds"]
    assert left >= x
    assert top >= y
    assert right <= x + width
    assert bottom <= y + height


def test_compositor_uses_canonical_placement_safe_area(tmp_path):
    overlay = load_compositor()
    background = tmp_path / "linkedin-page-background.png"
    output = tmp_path / "linkedin-page.png"
    Image.new("RGB", (4200, 700), "#f2ede2").save(background)
    placements = (
        PLUGIN
        / "skills/brand-assets-make-launch-pack/references/channel-placements.json"
    )
    digest = hashlib.sha256(FONT.read_bytes()).hexdigest()

    result = overlay.compose(
        background=background,
        output=output,
        text="SHOW MAKE CHECK SAVE",
        font_path=FONT,
        font_family="Instrument Sans",
        font_sha256=digest,
        box=(600, 90, 2200, 500),
        safe_area=None,
        placement_id="linkedin-page-cover",
        weight=700,
        width=82,
        color="#171526",
    )
    assert result["placement_id"] == "linkedin-page-cover"
    assert result["safe_area"] == {
        "top": 90,
        "right": 210,
        "bottom": 90,
        "left": 600,
    }

    with pytest.raises(ValueError, match="does not match canonical"):
        overlay.compose(
            background=background,
            output=output,
            text="SHOW MAKE CHECK SAVE",
            font_path=FONT,
            font_family="Instrument Sans",
            font_sha256=digest,
            box=(600, 90, 2200, 500),
            safe_area={"top": 0, "right": 0, "bottom": 0, "left": 0},
            placement_id="linkedin-page-cover",
            weight=700,
            width=82,
            color="#171526",
        )

    wrong_size = tmp_path / "wrong-size.png"
    Image.new("RGB", (1200, 630), "#f2ede2").save(wrong_size)
    with pytest.raises(ValueError, match="dimensions"):
        overlay.compose(
            background=wrong_size,
            output=output,
            text="SHOW MAKE CHECK SAVE",
            font_path=FONT,
            font_family="Instrument Sans",
            font_sha256=digest,
            box=(600, 90, 400, 400),
            safe_area=None,
            placement_id="linkedin-page-cover",
            weight=700,
            width=82,
            color="#171526",
        )


def test_compositor_measures_and_saves_the_final_palette_pixels(tmp_path):
    overlay = load_compositor()
    background = tmp_path / "background.png"
    output = tmp_path / "output.png"
    Image.new("RGB", (600, 400), "#f2ede2").save(background)
    digest = hashlib.sha256(FONT.read_bytes()).hexdigest()

    result = overlay.compose(
        background=background,
        output=output,
        text="MAKE THE IMAGE WORK",
        font_path=FONT,
        font_family="Instrument Sans",
        font_sha256=digest,
        box=(70, 70, 460, 260),
        safe_area={"top": 50, "right": 50, "bottom": 50, "left": 50},
        weight=700,
        width=82,
        color="#171526",
        palette_colors=256,
    )

    with Image.open(output) as image:
        assert image.mode == "P"
    assert result["output_mode"] == "P"
    assert result["contrast_basis"] == "saved output pixels against clean background"


def test_background_checker_blocks_upscale_and_destructive_crop(tmp_path):
    script = ROOT / "scripts/check_background_fit.py"
    small = tmp_path / "small.png"
    wide = tmp_path / "wide.png"
    Image.new("RGB", (100, 100), "white").save(small)
    Image.new("RGB", (400, 100), "white").save(wide)

    upscale = subprocess.run(
        [sys.executable, str(script), str(small), "--target", "200x200"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    crop = subprocess.run(
        [sys.executable, str(script), str(wide), "--target", "100x100"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    safe = subprocess.run(
        [sys.executable, str(script), str(wide), "--target", "200x50"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert upscale.returncode == 1 and "upscale" in upscale.stdout
    assert crop.returncode == 1 and "crop" in crop.stdout
    assert safe.returncode == 0 and '"ok": true' in safe.stdout.lower()

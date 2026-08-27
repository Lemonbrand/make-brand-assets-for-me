from pathlib import Path

from PIL import Image
import importlib.util


ROOT = Path(__file__).parents[1]
ASSETS = ROOT / "plugins/make-brand-assets-for-me/assets"
FONT = ASSETS / "fonts/InstrumentSans-Variable.ttf"


def test_brand_png_dimensions():
    expected = {
        "icon.png": (512, 512),
        "logo-light.png": (1600, 480),
        "logo-dark.png": (1600, 480),
        "social-preview.png": (1280, 640),
    }
    for name, size in expected.items():
        with Image.open(ASSETS / name) as image:
            assert image.size == size
            assert image.format == "PNG"


def test_editable_identity_source_exists():
    source = ROOT / "assets/source"
    assert (source / "mark.svg").exists()
    assert (source / "lockup.svg").exists()


def test_exporter_uses_the_bundled_brand_font():
    script = ROOT / "scripts/export_brand_assets.py"
    spec = importlib.util.spec_from_file_location("export_brand_assets", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    exported_font = module.font(36, bold=True)
    assert FONT.exists()
    assert module.FONT_PATH == FONT
    assert exported_font.getname()[0] == "Instrument Sans"
    assert exported_font.get_variation_axes()[0]["default"] == 100


def test_exporter_uses_ascii_for_portable_step_labels():
    source = (ROOT / "scripts/export_brand_assets.py").read_text()
    assert "→" not in source

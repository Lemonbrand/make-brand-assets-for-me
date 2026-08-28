"""Deterministic typography shared by the package's generated examples."""

import hashlib

from pathlib import Path

from PIL import ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = ROOT / "plugins/make-brand-assets-for-me/assets/fonts/InstrumentSans-Variable.ttf"
FONT_RELATIVE_PATH = "plugins/make-brand-assets-for-me/assets/fonts/InstrumentSans-Variable.ttf"
FONT_LICENSE = "SIL Open Font License 1.1"
FONT_SHA256 = hashlib.sha256(FONT_PATH.read_bytes()).hexdigest()


def load_brand_font(size, weight=700, width=82, path=None):
    """Load the bundled variable font and apply exact axes; never silently fall back."""
    font_path = Path(path) if path is not None else FONT_PATH
    if not font_path.is_file():
        raise FileNotFoundError(f"Required brand font is missing: {font_path}")

    face = ImageFont.truetype(str(font_path), size=max(10, int(size)))
    axes = face.get_variation_axes()
    axis_names = [axis["name"].decode("ascii") for axis in axes]
    if axis_names != ["Width", "Weight"]:
        raise ValueError(f"Unexpected Instrument Sans axes: {axis_names}")
    face.set_variation_by_axes([int(width), int(weight)])
    return face


def font_receipt(weight=700, width=82):
    return {
        "family": "Instrument Sans",
        "file": FONT_RELATIVE_PATH,
        "license": FONT_LICENSE,
        "sha256": FONT_SHA256,
        "weight": int(weight),
        "width": int(width),
        "variation_applied": True,
    }

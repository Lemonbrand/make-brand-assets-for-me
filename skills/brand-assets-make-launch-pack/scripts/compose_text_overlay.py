#!/usr/bin/env python3
"""Add exact short copy to an approved text-free background and emit QA evidence."""

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont


WORD_RE = re.compile(r"[\w’'-]+", re.UNICODE)


def word_count(text):
    return len(WORD_RE.findall(text))


def _font(font_path, size, family, expected_sha256, weight, width):
    font_path = Path(font_path)
    if not font_path.is_file():
        raise FileNotFoundError(f"Approved font file not found: {font_path}")
    observed_sha256 = hashlib.sha256(font_path.read_bytes()).hexdigest()
    if observed_sha256.lower() != expected_sha256.lower():
        raise ValueError(
            f"Approved font SHA-256 mismatch: expected {expected_sha256}, got {observed_sha256}"
        )

    font = ImageFont.truetype(str(font_path), size=size)
    observed_family, style = font.getname()
    if observed_family.casefold() != family.casefold():
        raise ValueError(
            f"Approved font family mismatch: expected {family}, got {observed_family}"
        )

    try:
        axes = font.get_variation_axes()
    except (AttributeError, OSError):
        axes = []
    values = []
    applied = {}
    for axis in axes:
        name = axis["name"].decode("ascii", errors="replace").casefold()
        if name not in {"weight", "width"}:
            label = axis["name"].decode("ascii", errors="replace")
            raise ValueError(f"Unsupported font axis needs an explicit compositor update: {label}")
        requested = axis["default"]
        receipt_name = name
        if name == "weight":
            requested = weight
            receipt_name = "weight"
        elif name == "width":
            requested = width
            receipt_name = "width"
        if not axis["minimum"] <= requested <= axis["maximum"]:
            label = axis["name"].decode("ascii", errors="replace")
            raise ValueError(
                f"{label} axis value {requested} is outside "
                f"{axis['minimum']}..{axis['maximum']}"
            )
        values.append(requested)
        if name in {"weight", "width"}:
            applied[receipt_name] = requested
    if values:
        try:
            font.set_variation_by_axes(values)
        except OSError as error:
            raise ValueError(f"Approved font could not apply its requested axes: {error}") from error
    else:
        style_lower = style.casefold()
        if weight >= 600 and not any(
            token in style_lower for token in ("bold", "black", "heavy", "semibold")
        ):
            raise ValueError("Static font file is not an approved bold face")
        if width < 95 and not any(
            token in style_lower for token in ("condensed", "narrow", "compressed")
        ):
            raise ValueError("Static font file is not an approved condensed face")
        applied = {"weight": weight, "width": width}
    return font, {
        "family": observed_family,
        "style": style,
        "sha256": observed_sha256,
        "file": str(font_path),
        "applied_axes": applied,
        "variation_applied": bool(values),
    }


def _wrap(draw, text, font, max_width):
    lines = []
    current = []
    for word in text.split():
        trial = " ".join([*current, word])
        width = draw.textbbox((0, 0), trial, font=font)[2]
        if current and width > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def _fit(draw, text, font_args, box, max_size, min_size, leading):
    _, _, box_width, box_height = box
    for size in range(max_size, min_size - 1, -2):
        font, font_receipt = _font(size=size, **font_args)
        wrapped = _wrap(draw, text, font, box_width)
        spacing = round(size * leading)
        bounds = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=spacing)
        if (
            bounds[0] >= 0
            and bounds[1] >= 0
            and bounds[2] <= box_width
            and bounds[3] <= box_height
        ):
            return font, wrapped, spacing, font_receipt
    raise ValueError("Copy does not fit the protected text box with the approved font")


def _safe_rectangle(size, safe_area):
    width, height = size
    required = {"top", "right", "bottom", "left"}
    if set(safe_area) < required:
        raise ValueError("safe_area needs top, right, bottom, and left")
    rectangle = (
        int(safe_area["left"]),
        int(safe_area["top"]),
        width - int(safe_area["right"]),
        height - int(safe_area["bottom"]),
    )
    if rectangle[0] >= rectangle[2] or rectangle[1] >= rectangle[3]:
        raise ValueError("safe_area leaves no usable canvas")
    return rectangle


def _placement_registry_path():
    script = Path(__file__).resolve()
    candidates = (
        script.parents[1] / "references/channel-placements.json",
        script.parents[1]
        / "plugins/make-brand-assets-for-me/skills/brand-assets-make-launch-pack/references/channel-placements.json",
    )
    for path in candidates:
        if path.is_file():
            return path
    raise ValueError("Could not locate the bundled canonical placement registry")


def _canonical_placement(placement_id):
    placements_path = _placement_registry_path()
    try:
        data = json.loads(placements_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read placement registry: {error}") from error
    for placement in data.get("placements", []):
        if placement.get("id") == placement_id:
            return {
                "id": placement_id,
                "width": int(placement["width"]),
                "height": int(placement["height"]),
                "safe_area": {
                    key: int(placement["safe_area"][key])
                    for key in ("top", "right", "bottom", "left")
                },
            }
    raise ValueError(f"Unknown placement ID: {placement_id}")


def _contains(outer, inner):
    return (
        inner[0] >= outer[0]
        and inner[1] >= outer[1]
        and inner[2] <= outer[2]
        and inner[3] <= outer[3]
    )


def _linear_luminance(rgb):
    channels = []
    for value in rgb[:3]:
        value = value / 255
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast(a, b):
    light, dark = sorted((_linear_luminance(a), _linear_luminance(b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def _contrast_report(background, rendered, mask):
    pixels = []
    image_pixels = background.convert("RGB").load()
    rendered_pixels = rendered.convert("RGB").load()
    mask_pixels = mask.load()
    bounds = mask.getbbox()
    if not bounds:
        raise ValueError("Text renderer produced no visible glyph pixels")
    for y in range(bounds[1], bounds[3]):
        for x in range(bounds[0], bounds[2]):
            if mask_pixels[x, y] >= 240:
                pixels.append(_contrast(rendered_pixels[x, y], image_pixels[x, y]))
    pixels.sort()
    p10 = pixels[min(len(pixels) - 1, math.floor(len(pixels) * 0.10))]
    median = pixels[len(pixels) // 2]
    return {
        "minimum_ratio": round(pixels[0], 3),
        "p10_ratio": round(p10, 3),
        "median_ratio": round(median, 3),
        "sampled_mask_alpha_min": 240,
    }


def compose(
    *,
    background,
    output,
    text,
    font_path,
    font_family,
    font_sha256,
    box,
    safe_area,
    placement_id=None,
    weight=700,
    width=82,
    color="#171526",
    max_size=160,
    min_size=24,
    leading=0.08,
    uppercase=True,
    min_contrast=3.0,
    palette_colors=None,
):
    count = word_count(text)
    if count >= 15:
        raise ValueError("Marketing overlay copy must contain fewer than 15 words")
    if count == 0:
        raise ValueError("Marketing overlay copy cannot be empty")
    min_contrast = float(min_contrast)
    if not math.isfinite(min_contrast):
        raise ValueError("The minimum contrast threshold must be finite")
    if min_contrast < 3.0:
        raise ValueError("The minimum contrast threshold cannot be lower than 3.0")
    if palette_colors is not None and not 2 <= int(palette_colors) <= 256:
        raise ValueError("palette_colors must be between 2 and 256")
    if ImageColor.getcolor(color, "RGBA")[3] != 255:
        raise ValueError("Rendered text contrast requires a fully opaque color")

    background = Path(background)
    output = Path(output)
    if not background.is_file():
        raise FileNotFoundError(f"Background not found: {background}")
    with Image.open(background) as source:
        image = source.convert("RGBA")

    if placement_id:
        placement = _canonical_placement(placement_id)
        if image.size != (placement["width"], placement["height"]):
            raise ValueError(
                f"Canvas dimensions {image.width}x{image.height} do not match canonical "
                f"placement {placement_id}: {placement['width']}x{placement['height']}"
            )
        canonical = placement["safe_area"]
        if safe_area is not None:
            supplied = {
                key: int(safe_area[key]) for key in ("top", "right", "bottom", "left")
            }
            if supplied != canonical:
                raise ValueError(
                    f"Supplied safe area does not match canonical placement {placement_id}"
                )
        safe_area = canonical
    if safe_area is None:
        raise ValueError("safe_area or placement_id is required")
    safe_rectangle = _safe_rectangle(image.size, safe_area)
    x, y, box_width, box_height = (int(value) for value in box)
    box_rectangle = (x, y, x + box_width, y + box_height)
    if box_width <= 0 or box_height <= 0 or not _contains(safe_rectangle, box_rectangle):
        raise ValueError("Protected text box must stay inside the placement safe area")

    rendered_text = text.upper() if uppercase else text
    draw = ImageDraw.Draw(image)
    font, wrapped, spacing, font_receipt = _fit(
        draw,
        rendered_text,
        {
            "font_path": font_path,
            "family": font_family,
            "expected_sha256": font_sha256,
            "weight": weight,
            "width": width,
        },
        (x, y, box_width, box_height),
        max_size,
        min_size,
        leading,
    )
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).multiline_text(
        (x, y), wrapped, font=font, fill=255, spacing=spacing
    )
    text_bounds = mask.getbbox()
    if not text_bounds or not _contains(safe_rectangle, text_bounds):
        raise ValueError("Rendered text must stay inside the placement safe area")
    rendered = image.copy()
    ImageDraw.Draw(rendered).multiline_text(
        (x, y), wrapped, font=font, fill=color, spacing=spacing
    )
    delivery = rendered
    if palette_colors is not None:
        delivery = rendered.convert("RGB").quantize(
            colors=int(palette_colors),
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.FLOYDSTEINBERG,
        )
    contrast = _contrast_report(image, delivery, mask)
    if contrast["minimum_ratio"] < float(min_contrast):
        raise ValueError(
            f"Rendered text contrast {contrast['minimum_ratio']} is below {min_contrast}"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    delivery.save(output, optimize=True)
    return {
        "background": str(background),
        "output": str(output),
        "text": text,
        "rendered_text": rendered_text,
        "word_count": count,
        "font": font_receipt,
        "text_box": [x, y, box_width, box_height],
        "text_bounds": list(text_bounds),
        "safe_area": {key: int(safe_area[key]) for key in ("top", "right", "bottom", "left")},
        "safe_rectangle": list(safe_rectangle),
        "placement_id": placement_id,
        "contrast": contrast,
        "contrast_basis": "saved output pixels against clean background",
        "output_mode": delivery.mode,
        "checks": {
            "font_identity": "pass",
            "safe_area": "pass",
            "contrast": "pass",
            "copy_length": "pass",
        },
    }


def _box(value):
    parts = tuple(int(part) for part in value.split(","))
    if len(parts) != 4 or any(part < 0 for part in parts):
        raise argparse.ArgumentTypeError("box must be x,y,width,height using non-negative integers")
    return parts


def _safe_area(value):
    parts = tuple(int(part) for part in value.split(","))
    if len(parts) != 4 or any(part < 0 for part in parts):
        raise argparse.ArgumentTypeError("safe area must be top,right,bottom,left")
    return dict(zip(("top", "right", "bottom", "left"), parts))


def main():
    parser = argparse.ArgumentParser(
        description="Composite exact short copy over a text-free background with font, safe-area, and contrast checks."
    )
    parser.add_argument("--background", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--font", required=True)
    parser.add_argument("--font-family", required=True)
    parser.add_argument("--font-sha256", required=True)
    parser.add_argument("--box", required=True, type=_box)
    parser.add_argument("--safe-area", type=_safe_area)
    parser.add_argument("--placement")
    parser.add_argument("--color", default="#171526")
    parser.add_argument("--weight", type=int, default=700)
    parser.add_argument("--width", type=int, default=82)
    parser.add_argument("--max-size", type=int, default=160)
    parser.add_argument("--min-size", type=int, default=24)
    parser.add_argument("--min-contrast", type=float, default=3.0)
    parser.add_argument("--palette-colors", type=int)
    parser.add_argument("--keep-case", action="store_true")
    args = parser.parse_args()
    result = compose(
        background=args.background,
        output=args.output,
        text=args.text,
        font_path=args.font,
        font_family=args.font_family,
        font_sha256=args.font_sha256,
        box=args.box,
        safe_area=args.safe_area,
        placement_id=args.placement,
        weight=args.weight,
        width=args.width,
        color=args.color,
        max_size=args.max_size,
        min_size=args.min_size,
        min_contrast=args.min_contrast,
        palette_colors=args.palette_colors,
        uppercase=not args.keep_case,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

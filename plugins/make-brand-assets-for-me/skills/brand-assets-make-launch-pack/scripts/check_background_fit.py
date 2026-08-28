#!/usr/bin/env python3
"""Fail when crop-to-fill would enlarge a background or discard over 25%."""

import argparse
import json
from pathlib import Path

from PIL import Image


MAX_CROP_LOSS = 0.25


def check_background_fit(path, target):
    path = Path(path)
    with Image.open(path) as image:
        source_width, source_height = image.size
    target_width, target_height = target
    issues = []
    if source_width < target_width or source_height < target_height:
        issues.append(
            f"upscale blocked: source {source_width}x{source_height}, "
            f"target {target_width}x{target_height}"
        )
    scale = max(target_width / source_width, target_height / source_height)
    scaled_width = source_width * scale
    scaled_height = source_height * scale
    kept = (target_width * target_height) / (scaled_width * scaled_height)
    crop_loss = max(0.0, 1.0 - kept)
    if crop_loss > MAX_CROP_LOSS:
        issues.append(
            f"crop blocked: crop-to-fill would discard {crop_loss:.1%}; "
            f"maximum is {MAX_CROP_LOSS:.0%}"
        )
    return {
        "ok": not issues,
        "source": str(path),
        "source_dimensions": [source_width, source_height],
        "target_dimensions": [target_width, target_height],
        "crop_loss": round(crop_loss, 6),
        "maximum_crop_loss": MAX_CROP_LOSS,
        "issues": issues,
    }


def _target(value):
    try:
        width, height = (int(part) for part in value.lower().split("x", 1))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError("target must be WIDTHxHEIGHT") from error
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("target dimensions must be positive")
    return width, height


def main():
    parser = argparse.ArgumentParser(
        description="Check a text-free background for source upscaling and destructive crop-to-fill."
    )
    parser.add_argument("background")
    parser.add_argument("--target", required=True, type=_target)
    args = parser.parse_args()
    report = check_background_fit(args.background, args.target)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()

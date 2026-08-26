#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def inspect_png(path):
    path = Path(path)
    with Image.open(path) as image:
        width, height = image.size
        has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
        if has_alpha:
            alpha = image.convert("RGBA").getchannel("A")
            box = alpha.getbbox()
            if box:
                left, top, right, bottom = box
                padding = {
                    "left": left,
                    "top": top,
                    "right": width - right,
                    "bottom": height - bottom,
                }
            else:
                padding = {edge: width if edge in {"left", "right"} else height for edge in ("left", "top", "right", "bottom")}
        else:
            padding = {edge: 0 for edge in ("left", "top", "right", "bottom")}
        return {
            "path": str(path),
            "width_px": width,
            "height_px": height,
            "mode": image.mode,
            "has_alpha": has_alpha,
            "padding_px": padding,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }


def main():
    parser = argparse.ArgumentParser(description="Check a PNG file.")
    parser.add_argument("path")
    args = parser.parse_args()
    print(json.dumps(inspect_png(args.path), indent=2))


if __name__ == "__main__":
    main()

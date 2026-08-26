#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


def _distance(a, b):
    return sum(abs(int(x) - int(y)) for x, y in zip(a[:3], b[:3]))


def check_copy_space(path, side="right", percent=55, overlay_path=None):
    path = Path(path)
    with Image.open(path) as source:
        image = source.convert("RGB")
        width, height = image.size
        zone_width = round(width * float(percent) / 100)
        if side == "right":
            box = (width - zone_width, 0, width, height)
        elif side == "left":
            box = (0, 0, zone_width, height)
        else:
            raise ValueError("side must be 'left' or 'right'")
        background = image.getpixel((box[0], 0))
        zone = image.crop(box)
        changed = sum(1 for pixel in zone.get_flattened_data() if _distance(pixel, background) > 45)
        total = zone.width * zone.height
        clean = changed <= max(1, round(total * 0.005))

        if overlay_path:
            proof = source.convert("RGBA")
            draw = ImageDraw.Draw(proof, "RGBA")
            draw.rectangle((box[0], 0, box[2] - 1, box[3] - 1), fill=(255, 0, 0, 36), outline=(255, 0, 0, 255), width=max(2, width // 300))
            Path(overlay_path).parent.mkdir(parents=True, exist_ok=True)
            proof.save(overlay_path)

        return {
            "path": str(path),
            "side": side,
            "percent": float(percent),
            "box": list(box),
            "changed_pixels": changed,
            "total_pixels": total,
            "clean": clean,
        }


def main():
    parser = argparse.ArgumentParser(description="Check room reserved for copy.")
    parser.add_argument("path")
    parser.add_argument("--side", choices=["left", "right"], default="right")
    parser.add_argument("--percent", type=float, default=55)
    parser.add_argument("--overlay")
    args = parser.parse_args()
    print(json.dumps(check_copy_space(args.path, args.side, args.percent, args.overlay), indent=2))


if __name__ == "__main__":
    main()

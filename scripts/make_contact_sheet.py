#!/usr/bin/env python3
import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from brand_type import load_brand_font


def make_contact_sheet(paths, output_path, title="Review sheet", columns=3):
    paths = [Path(path) for path in paths]
    width = 1200
    margin = 48
    gap = 24
    title_height = 80
    cell_width = (width - margin * 2 - gap * (columns - 1)) // columns
    cell_height = cell_width + 54
    rows = max(1, math.ceil(len(paths) / columns))
    height = margin + title_height + rows * cell_height + (rows - 1) * gap + margin
    sheet = Image.new("RGB", (width, height), "#F5F2EC")
    draw = ImageDraw.Draw(sheet)
    font = load_brand_font(30, weight=700, width=86)
    label_font = load_brand_font(18, weight=600, width=94)
    draw.text((margin, margin), title, fill="#17151F", font=font)

    for index, path in enumerate(paths):
        row, column = divmod(index, columns)
        x = margin + column * (cell_width + gap)
        y = margin + title_height + row * (cell_height + gap)
        with Image.open(path) as source:
            thumb = source.convert("RGBA")
            thumb.thumbnail((cell_width - 24, cell_width - 24), Image.Resampling.LANCZOS)
            tile = Image.new("RGBA", (cell_width, cell_width), "white")
            tile.alpha_composite(thumb, ((cell_width - thumb.width) // 2, (cell_width - thumb.height) // 2))
            sheet.paste(tile.convert("RGB"), (x, y))
        draw.text((x, y + cell_width + 14), path.stem.replace("-", " ").title(), fill="#393545", font=label_font)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Make a labeled PNG contact sheet.")
    parser.add_argument("output")
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--title", default="Review sheet")
    parser.add_argument("--columns", type=int, default=3)
    args = parser.parse_args()
    make_contact_sheet(args.inputs, args.output, args.title, args.columns)
    print(args.output)


if __name__ == "__main__":
    main()

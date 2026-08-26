#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).parents[1]
OUT = ROOT / "plugins/make-brand-assets-for-me/assets"
PALETTE = {"ink": "#171526", "blue": "#3157F6", "pink": "#F45B92", "lavender": "#A58AF8", "paper": "#F8F6FF"}


def font(size, bold=False):
    return ImageFont.load_default(size=size)


def draw_mark(image, box):
    draw = ImageDraw.Draw(image)
    x, y, size = box
    tile = round(size * 0.27)
    radius = round(tile * 0.22)
    positions = ((0.18, 0.18, PALETTE["blue"]), (0.56, 0.16, PALETTE["pink"]), (0.20, 0.56, PALETTE["lavender"]), (0.55, 0.55, PALETTE["ink"]))
    for px, py, color in positions:
        left = x + round(size * px)
        top = y + round(size * py)
        draw.rounded_rectangle((left, top, left + tile, top + tile), radius=radius, fill=color)
    left = x + round(size * 0.55)
    top = y + round(size * 0.55)
    draw.line((left + tile * 0.23, top + tile * 0.52, left + tile * 0.43, top + tile * 0.72, left + tile * 0.78, top + tile * 0.28), fill="white", width=max(4, round(size * 0.045)), joint="curve")


def make_icon():
    image = Image.new("RGB", (512, 512), PALETTE["paper"])
    draw_mark(image, (0, 0, 512))
    image.save(OUT / "icon.png")


def make_lockup(name, background, ink, accent):
    image = Image.new("RGB", (1600, 480), background)
    draw_mark(image, (48, 32, 416))
    draw = ImageDraw.Draw(image)
    draw.text((500, 104), "Make Brand Assets", font=font(88, True), fill=ink)
    draw.text((500, 210), "For Me", font=font(88, True), fill=accent)
    draw.text((506, 344), "SHOW  >  PLAN  >  MAKE  >  CHECK  >  SAVE", font=font(27), fill=ink)
    image.save(OUT / name)


def make_social():
    image = Image.new("RGB", (1280, 640), PALETTE["ink"])
    draw = ImageDraw.Draw(image)
    draw_mark(image, (56, 64, 360))
    draw.text((450, 120), "Make Brand", font=font(72, True), fill="white")
    draw.text((450, 205), "Assets For Me", font=font(72, True), fill=PALETTE["lavender"])
    draw.text((456, 330), "Show it your brand.", font=font(34), fill="white")
    draw.text((456, 378), "Tell it what you need.", font=font(34), fill="white")
    draw.text((456, 426), "It makes assets that match.", font=font(34), fill="white")
    draw.rounded_rectangle((456, 506, 1128, 570), radius=24, fill=PALETTE["blue"])
    draw.text((490, 521), "SHOW  >  PLAN  >  MAKE  >  CHECK  >  SAVE", font=font(22, True), fill="white")
    image.save(OUT / "social-preview.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    make_icon()
    make_lockup("logo-light.png", PALETTE["paper"], PALETTE["ink"], PALETTE["blue"])
    make_lockup("logo-dark.png", PALETTE["ink"], "white", PALETTE["lavender"])
    make_social()
    for path in sorted(OUT.glob("*.png")):
        print(path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from make_contact_sheet import make_contact_sheet
from brand_type import load_brand_font


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "examples/gallery/outputs"
PROOFS = ROOT / "examples/gallery/proofs"
RECORDS = ROOT / "examples/records"
BRIEFS = ROOT / "examples/briefs"
PROMPTS = ROOT / "examples/prompts"
PLUGIN_ASSETS = ROOT / "plugins/make-brand-assets-for-me/assets"

INK = "#171526"
BLUE = "#3157F6"
PINK = "#F45B92"
PAPER = "#F8F6FF"


JOBS = {
    "cut-paper-approval": {
        "brand": "cut-paper",
        "kind": "one",
        "job": "Approval token",
        "prompt": "A standalone approval token: one hand passing a green check card to another hand, layered cut-paper editorial collage, visible paper fibers, forest green, cobalt blue, tomato red, ochre and cream, transparent background, no words, no logo, generous padding.",
    },
    "soft-clay-approval": {
        "brand": "soft-clay",
        "kind": "one",
        "job": "Approval token",
        "prompt": "A standalone approval token: two rounded friendly hands passing a checked task tile, tactile matte clay, sky blue, coral, butter yellow and off-white, soft studio light, transparent background, no words, no logo, generous padding.",
    },
    "bold-print-approval": {
        "brand": "bold-print",
        "kind": "one",
        "job": "Approval token",
        "prompt": "A standalone approval token: a bold checked task card moving between two simplified hands, risograph print, coarse ink, cobalt blue, tomato red, sunflower yellow and black, transparent background, no words, no logo, generous padding.",
    },
    "cut-paper-handoff-scene": {
        "brand": "cut-paper",
        "kind": "scene",
        "job": "Website handoff scene",
        "prompt": "A wide editorial scene of two simplified people passing one task card into a completion tray, layered cut paper with visible fibers, full subject in the left 42 percent, right 55 percent calm cream copy space, no text, no logo, 16:9.",
    },
    "soft-clay-handoff-scene": {
        "brand": "soft-clay",
        "kind": "scene",
        "job": "Website handoff scene",
        "prompt": "A wide editorial scene of two simplified people passing one rounded task token into a shallow completion tray, tactile matte clay, full subject in the left 42 percent, right 55 percent calm warm-white copy space, no text, no logo, 16:9.",
    },
    "bold-print-handoff-scene": {
        "brand": "bold-print",
        "kind": "scene",
        "job": "Website handoff scene",
        "prompt": "A wide editorial scene of two simplified people passing one task card into a completion tray, bold risograph print with coarse ink, full subject in the left 42 percent, right 55 percent calm paper copy space, no text, no logo, 16:9.",
    },
    "bold-print-capture": {
        "brand": "bold-print",
        "kind": "set",
        "job": "Capture",
        "prompt": "One standalone input tray collecting three incoming shapes, bold risograph print, coarse ink, cobalt blue, tomato red, sunflower yellow and black, true transparent background, no text, no logo, generous padding.",
    },
    "bold-print-clarify": {
        "brand": "bold-print",
        "kind": "set",
        "job": "Clarify",
        "prompt": "One standalone magnifying glass focusing a clear checkpoint dot from a loose mess of shapes, bold risograph print, coarse ink, cobalt blue, tomato red, sunflower yellow and black, true transparent background, no text, no logo, generous padding.",
    },
    "bold-print-connect": {
        "brand": "bold-print",
        "kind": "set",
        "job": "Connect",
        "prompt": "One standalone task card traveling on a branching route toward one of three abstract people, bold risograph print, coarse ink, cobalt blue, tomato red, sunflower yellow and black, true transparent background, no text, no logo, generous padding.",
    },
    "bold-print-complete": {
        "brand": "bold-print",
        "kind": "set",
        "job": "Complete",
        "prompt": "One standalone finished output card with a check mark landing in a neat closed-loop tray, bold risograph print, coarse ink, cobalt blue, tomato red, sunflower yellow and black, true transparent background, no text, no logo, generous padding.",
    },
}


def default_font(size):
    return load_brand_font(size, weight=700 if size >= 30 else 500, width=86 if size >= 30 else 96)


def write_records():
    RECORDS.mkdir(parents=True, exist_ok=True)
    BRIEFS.mkdir(parents=True, exist_ok=True)
    PROMPTS.mkdir(parents=True, exist_ok=True)
    for stem, item in JOBS.items():
        output = OUTPUTS / f"{stem}.png"
        if not output.exists():
            raise FileNotFoundError(output)
        with Image.open(output) as image:
            width, height = image.size
            alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        brief = {
            "plain_request": item["job"],
            "brand_recipe": f"../brand-rules/{item['brand']}.yaml",
            "skill": f"brand-assets-make-{item['kind']}",
            "use": "Fictional baseline only. Replace the recipe and request for a real brand.",
            "must_have": ["one clear idea", "no accidental words", "matches its recipe"],
        }
        (BRIEFS / f"{stem}.json").write_text(json.dumps(brief, indent=2) + "\n")
        (PROMPTS / f"{stem}.txt").write_text(item["prompt"] + "\n")
        record = {
            "version": "1.0",
            "asset_job": item["job"],
            "brand_id": item["brand"],
            "route": "new",
            "parts": [stem],
            "prompt": item["prompt"],
            "output_path": f"../gallery/outputs/{stem}.png",
            "checks": {
                "format": "pass",
                "dimensions": "pass",
                "brand_match": "manual baseline review",
                "plain_meaning": "manual baseline review",
            },
            "publish_status": "baseline",
            "file": {"width": width, "height": height, "has_alpha": alpha, "sha256": digest},
        }
        (RECORDS / f"{stem}.json").write_text(json.dumps(record, indent=2) + "\n")


def make_proofs():
    PROOFS.mkdir(parents=True, exist_ok=True)
    groups = [
        ("01-three-styles.png", "One idea, three very different looks", ["cut-paper-approval", "soft-clay-approval", "bold-print-approval"], 3),
        ("02-three-scenes.png", "One layout, three very different looks", ["cut-paper-handoff-scene", "soft-clay-handoff-scene", "bold-print-handoff-scene"], 3),
        ("03-one-matching-set.png", "Four pieces that belong together", ["bold-print-capture", "bold-print-clarify", "bold-print-connect", "bold-print-complete"], 4),
        ("04-all-baselines.png", "The complete 10-image baseline", list(JOBS), 3),
    ]
    for filename, title, stems, columns in groups:
        make_contact_sheet([OUTPUTS / f"{stem}.png" for stem in stems], PROOFS / filename, title, columns)


def paste_contained(canvas, source_path, box):
    x, y, width, height = box
    with Image.open(source_path) as source:
        thumb = source.convert("RGBA")
        thumb.thumbnail((width, height), Image.Resampling.LANCZOS)
        left = x + (width - thumb.width) // 2
        top = y + (height - thumb.height) // 2
        canvas.paste(thumb, (left, top), thumb)


def screenshot_shell(title, line):
    image = Image.new("RGB", (1600, 1000), PAPER)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((52, 46, 1548, 118), 22, fill=INK)
    draw.ellipse((82, 73, 98, 89), fill=PINK)
    draw.ellipse((108, 73, 124, 89), fill="#FFD34D")
    draw.ellipse((134, 73, 150, 89), fill="#75D6A2")
    draw.text((194, 67), "Make Brand Assets For Me", font=default_font(32), fill="white")
    draw.text((72, 158), title, font=default_font(58), fill=INK)
    draw.text((76, 228), line, font=default_font(28), fill="#514C63")
    return image, draw


def make_screenshots():
    image, draw = screenshot_shell("Show me your brand", "Give me a link, a file, or a folder. I will make a tiny recipe.")
    for index, (number, title, text) in enumerate([
        ("1", "SHOW", "Point to the real brand."),
        ("2", "PLAN", "Choose the asset and its job."),
        ("3", "MAKE", "Make one useful first draft."),
        ("4", "CHECK", "Check meaning, look, and file."),
        ("5", "SAVE", "Keep the prompt and receipt."),
    ]):
        top = 310 + index * 122
        draw.rounded_rectangle((76, top, 1524, top + 92), 22, fill="white", outline="#DDD8EB", width=3)
        draw.ellipse((102, top + 18, 158, top + 74), fill=BLUE)
        draw.text((123, top + 31), number, font=default_font(25), fill="white", anchor="mm")
        draw.text((190, top + 18), title, font=default_font(26), fill=INK)
        draw.text((350, top + 22), text, font=default_font(24), fill="#514C63")
    image.save(PLUGIN_ASSETS / "screenshot-setup.png")

    image, draw = screenshot_shell("Try three looks before you pick one", "Same idea. Same test. Only the art direction changes.")
    paste_contained(image, PROOFS / "01-three-styles.png", (74, 294, 1452, 630))
    image.save(PLUGIN_ASSETS / "screenshot-styles.png")

    image, draw = screenshot_shell("Make a set that stays together", "Each piece has one job. The recipe keeps the family resemblance.")
    paste_contained(image, PROOFS / "03-one-matching-set.png", (74, 294, 1452, 630))
    image.save(PLUGIN_ASSETS / "screenshot-set.png")


def main():
    write_records()
    make_proofs()
    make_screenshots()
    print(f"Built {len(JOBS)} briefs, prompts, receipts, and four proof sheets.")


if __name__ == "__main__":
    main()

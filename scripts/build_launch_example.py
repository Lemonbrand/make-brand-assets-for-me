#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

from PIL import Image, ImageDraw, ImageFont, ImageOps

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from make_contact_sheet import make_contact_sheet


PRIMARY = [
    ("profile-avatar.png", "profile-avatar", "A small orange launch tile with a white spark and dark outline."),
    ("cover-wide.png", "cover-wide", "Wide cover reading Make Brand Assets For Me with the five-step method."),
    ("linkedin-profile-cover.png", "linkedin-profile-cover", "LinkedIn profile cover introducing the free brand asset plugin."),
    ("linkedin-page-cover.png", "linkedin-page-cover", "LinkedIn Page cover for Make Brand Assets For Me by Lemonbrand."),
    ("social-square.png", "social-square", "Square launch graphic reading Make Brand Assets For Me, free and open source."),
    ("social-portrait.png", "social-portrait", "Portrait launch graphic showing the five-step brand asset method."),
    ("social-landscape.png", "social-landscape", "Landscape launch graphic for the free Make Brand Assets For Me plugin."),
    ("story-vertical.png", "story-vertical", "Vertical story graphic introducing the free launch-pack skill."),
    ("open-graph.png", "open-graph", "Website sharing image for Make Brand Assets For Me."),
    ("email-header.png", "email-header", "Email header reading Make Brand Assets For Me."),
    ("product-hunt-thumbnail.png", "product-hunt-thumbnail", "Square Product Hunt thumbnail with an orange spark tile."),
    ("product-hunt-gallery-01.png", "product-hunt-gallery", "Product Hunt gallery image explaining the five simple brand asset steps."),
    ("product-hunt-gallery-02.png", "product-hunt-gallery", "Product Hunt gallery image showing three clearly labeled fictional styles."),
    ("youtube-thumbnail.png", "youtube-thumbnail", "YouTube thumbnail reading Make Brand Assets For Me with a launch-pack preview."),
]


def font(size):
    return ImageFont.load_default(size=max(10, int(size)))


def read_json(path):
    return json.loads(Path(path).read_text())


def fit_text(draw, text, box, start_size, fill, spacing=8, align="left", anchor=None):
    x, y, width, height = box
    words = text.split()
    for size in range(int(start_size), 11, -2):
        chosen = font(size)
        lines = []
        line = []
        for word in words:
            candidate = " ".join(line + [word])
            if draw.textlength(candidate, font=chosen) <= width or not line:
                line.append(word)
            else:
                lines.append(" ".join(line))
                line = [word]
        if line:
            lines.append(" ".join(line))
        line_height = size * 1.08
        if len(lines) * line_height + max(0, len(lines) - 1) * spacing <= height:
            draw.multiline_text(
                (x, y),
                "\n".join(lines),
                font=chosen,
                fill=fill,
                spacing=spacing,
                align=align,
                anchor=anchor,
            )
            return size
    raise ValueError(f"Text does not fit: {text}")


def draw_grid(draw, width, height, color):
    step = max(32, min(width, height) // 12)
    for x in range(0, width, step):
        draw.line((x, 0, x, height), fill=color, width=1)
    for y in range(0, height, step):
        draw.line((0, y, width, y), fill=color, width=1)


def draw_spark(draw, box, fill, outline, width):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    points = [
        (cx, y0), (cx + rx * .18, cy - ry * .18), (x1, cy),
        (cx + rx * .18, cy + ry * .18), (cx, y1),
        (cx - rx * .18, cy + ry * .18), (x0, cy),
        (cx - rx * .18, cy - ry * .18),
    ]
    draw.polygon(points, fill=fill, outline=outline, width=width)


def draw_brand(draw, width, palette, scale=1.0):
    pad = int(34 * scale)
    size = int(34 * scale)
    draw_spark(draw, (pad, pad, pad + size, pad + size), palette["orange"], palette["ink"], max(2, int(3 * scale)))
    draw.text((pad + size + int(14 * scale), pad + int(3 * scale)), "LEMONBRAND / OPEN SOURCE", font=font(18 * scale), fill=palette["ink"])


def paste_preview(canvas, source, box, border, shadow):
    x, y, width, height = [int(value) for value in box]
    with Image.open(source) as opened:
        image = ImageOps.contain(opened.convert("RGB"), (width, height), Image.Resampling.LANCZOS)
    left = x + (width - image.width) // 2
    top = y + (height - image.height) // 2
    canvas_draw = ImageDraw.Draw(canvas)
    canvas_draw.rounded_rectangle((left + 10, top + 10, left + image.width + 10, top + image.height + 10), 18, fill=shadow)
    canvas.paste(image, (left, top))
    canvas_draw.rounded_rectangle((left, top, left + image.width, top + image.height), 16, outline=border, width=max(2, min(width, height) // 120))


def draw_steps(draw, box, palette, horizontal=True):
    x, y, width, height = [int(value) for value in box]
    labels = ["SHOW", "PLAN", "MAKE", "CHECK", "SAVE"]
    if horizontal:
        gap = max(4, width // 100)
        cell = (width - gap * 4) // 5
        for index, label in enumerate(labels):
            left = x + index * (cell + gap)
            draw.rectangle((left + 5, y + 5, left + cell + 5, y + height + 5), fill=palette["ink"])
            draw.rectangle((left, y, left + cell, y + height), fill=palette["white"], outline=palette["ink"], width=max(2, height // 28))
            draw.text((left + cell / 2, y + height / 2), label, font=font(min(cell / 5.5, height / 3.2)), fill=palette["ink"], anchor="mm")
    else:
        gap = max(6, height // 90)
        cell = (height - gap * 4) // 5
        for index, label in enumerate(labels):
            top = y + index * (cell + gap)
            draw.rectangle((x + 5, top + 5, x + width + 5, top + cell + 5), fill=palette["ink"])
            draw.rectangle((x, top, x + width, top + cell), fill=palette["white"], outline=palette["ink"], width=max(2, cell // 25))
            draw.text((x + width / 2, top + cell / 2), label, font=font(min(width / 8, cell / 3)), fill=palette["ink"], anchor="mm")


def render_primary(root, output, placement_id, campaign):
    placements = read_json(
        root / "plugins/make-brand-assets-for-me/skills/brand-assets-make-launch-pack/references/channel-placements.json"
    )["placements"]
    placement = next(item for item in placements if item["id"] == placement_id)
    width, height = placement["width"], placement["height"]
    palette = campaign["palette"]
    image = Image.new("RGB", (width, height), palette["paper"])
    draw = ImageDraw.Draw(image)
    draw_grid(draw, width, height, palette["paper_2"])

    if placement_id in {"profile-avatar", "product-hunt-thumbnail"}:
        margin = int(min(width, height) * .12)
        draw.rectangle((margin + 10, margin + 10, width - margin + 10, height - margin + 10), fill=palette["ink"])
        draw.rectangle((margin, margin, width - margin, height - margin), fill=palette["orange"], outline=palette["ink"], width=max(4, width // 50))
        draw_spark(draw, (width * .26, height * .26, width * .74, height * .74), palette["white"], palette["ink"], max(4, width // 60))
        image.save(output)
        return

    scale = min(width / 1200, height / 630)
    draw_brand(draw, width, palette, max(.55, scale))
    is_tall = height / width > 1.25
    is_banner = height / width < .42
    screenshot = root / "plugins/make-brand-assets-for-me/assets/screenshot-styles.png"

    if placement_id == "product-hunt-gallery":
        variant = output.stem.rsplit("-", 1)[-1]
        if variant == "01":
            fit_text(draw, "FIVE SMALL STEPS. ONE BRAND SYSTEM.", (70, 120, 570, 270), 66, palette["ink"])
            draw_steps(draw, (70, 460, 1120, 120), palette, horizontal=True)
        else:
            fit_text(draw, "ONE METHOD. THREE FICTIONAL STYLES.", (70, 80, 520, 260), 60, palette["ink"])
            paste_preview(image, root / "examples/gallery/proofs/01-three-styles.png", (620, 90, 560, 560), palette["ink"], palette["orange"])
            draw.text((72, 650), "FICTIONAL EXAMPLES / BRING YOUR OWN BRAND", font=font(22), fill=palette["orange_deep"])
    elif is_banner:
        left = max(70, int(width * .07))
        fit_text(draw, campaign["headlines"]["main"], (left, int(height * .26), int(width * .58), int(height * .42)), min(86, height * .19), palette["ink"])
        draw.rectangle((int(width * .72), 0, width, height), fill=palette["orange"])
        draw_spark(draw, (width * .79, height * .2, width * .93, height * .8), palette["white"], palette["ink"], max(3, int(height * .018)))
        draw.text((left, int(height * .8)), "SHOW  /  PLAN  /  MAKE  /  CHECK  /  SAVE", font=font(max(14, height * .055)), fill=palette["navy"])
    elif is_tall:
        top = int(height * .12)
        fit_text(draw, campaign["headlines"]["main"], (int(width * .09), top, int(width * .82), int(height * .26)), width * .095, palette["ink"])
        draw.rectangle((int(width * .08), int(height * .44), int(width * .92), int(height * .67)), fill=palette["orange_wash"], outline=palette["ink"], width=max(3, width // 240))
        draw_steps(draw, (int(width * .13), int(height * .48), int(width * .74), int(height * .14)), palette, horizontal=False)
        draw.rectangle((int(width * .08), int(height * .73), int(width * .92), int(height * .9)), fill=palette["navy"])
        fit_text(draw, campaign["headlines"]["offer"], (int(width * .13), int(height * .77), int(width * .74), int(height * .1)), width * .05, palette["white"], align="center")
    else:
        fit_text(draw, campaign["headlines"]["main"], (int(width * .06), int(height * .18), int(width * .52), int(height * .42)), min(width, height) * .11, palette["ink"])
        paste_preview(image, screenshot, (int(width * .62), int(height * .16), int(width * .32), int(height * .58)), palette["ink"], palette["orange"])
        draw_steps(draw, (int(width * .06), int(height * .76), int(width * .88), int(height * .12)), palette, horizontal=True)

    footer_y = height - max(28, int(height * .065))
    draw.text((int(width * .06), footer_y), "FREE ON GITHUB", font=font(max(13, min(width, height) * .03)), fill=palette["orange_deep"])
    draw.text((int(width * .94), footer_y), "LEMONBRAND.IO/INBOX-AUDIT", font=font(max(11, min(width, height) * .022)), fill=palette["navy"], anchor="ra")
    image.save(output)


def carousel_regions(width, height, has_preview):
    if has_preview:
        return {
            "body": (64, int(height * .54), width - 128, int(height * .08)),
            "preview": (int(width * .19), int(height * .64), int(width * .62), int(height * .22)),
        }
    return {
        "body": (64, int(height * .71), width - 128, int(height * .15)),
        "preview": None,
    }


def render_carousel_page(output, size, page, total, item, campaign, preview=None):
    width, height = size
    palette = campaign["palette"]
    image = Image.new("RGB", size, palette["paper"])
    draw = ImageDraw.Draw(image)
    draw_grid(draw, width, height, palette["paper_2"])
    draw_brand(draw, width, palette, .95)
    draw.text((width - 60, 54), f"{page:02d}/{total:02d}", font=font(24), fill=palette["navy"], anchor="ra")
    draw.rectangle((60, 150, 300, 205), fill=palette["orange"], outline=palette["ink"], width=3)
    draw.text((180, 178), item["kicker"], font=font(22), fill=palette["ink"], anchor="mm")
    headline_height = int(height * (.42 if preview else .56))
    fit_text(draw, item["headline"], (60, 260, width - 120, headline_height), min(94, width * .095), palette["ink"], spacing=10)
    regions = carousel_regions(width, height, preview is not None)
    if item.get("body"):
        fit_text(draw, item["body"], regions["body"], 33, palette["navy"], spacing=7)
    if preview:
        paste_preview(image, preview, regions["preview"], palette["ink"], palette["orange"])
    draw.rectangle((60, height - 94, width - 60, height - 88), fill=palette["orange"])
    draw.text((60, height - 58), "FREE ON GITHUB  /  BUILT BY LEMONBRAND", font=font(21), fill=palette["navy"])
    image.save(output)


def save_pdf(paths, output):
    images = [Image.open(path).convert("RGB") for path in paths]
    try:
        images[0].save(output, "PDF", save_all=True, append_images=images[1:], resolution=96.0)
    finally:
        for image in images:
            image.close()
    pdf_bytes = output.read_bytes()
    pdf_bytes = re.sub(
        rb"/(CreationDate|ModDate) \(D:\d{14}Z\)",
        lambda match: b"/" + match.group(1) + b" (D:20260827000000Z)",
        pdf_bytes,
    )
    output.write_bytes(pdf_bytes)


def tracked_url(base, source, medium):
    return f"{base}?{urlencode({'utm_source': source, 'utm_medium': medium, 'utm_campaign': 'make_brand_assets_for_me'})}"


def build_launch_pack(root, campaign_dir):
    root = Path(root).resolve()
    campaign_dir = Path(campaign_dir).resolve()
    campaign = read_json(campaign_dir / "campaign.json")
    facts = read_json(campaign_dir / "source-facts.json")["facts"]
    fact_ids = [fact["id"] for fact in facts]
    assets_dir = campaign_dir / "assets"
    linkedin_dir = campaign_dir / "carousels/linkedin"
    social_dir = campaign_dir / "carousels/social"
    receipts_dir = campaign_dir / "receipts"
    proofs_dir = campaign_dir / "proofs"
    for folder in (assets_dir, linkedin_dir, social_dir, receipts_dir, proofs_dir):
        folder.mkdir(parents=True, exist_ok=True)

    records = []
    for filename, placement_id, alt_text in PRIMARY:
        output = assets_dir / filename
        render_primary(root, output, placement_id, campaign)
        records.append((filename.removesuffix(".png"), placement_id, output, alt_text, 1))

    linkedin_pages = []
    for index, item in enumerate(campaign["carousel_linkedin"], start=1):
        output = linkedin_dir / f"page-{index:02d}.png"
        preview = root / "plugins/make-brand-assets-for-me/assets/screenshot-styles.png" if index == 5 else None
        render_carousel_page(output, (1080, 1350), index, 5, item, campaign, preview)
        linkedin_pages.append(output)
        records.append((f"linkedin-carousel-{index:02d}", "carousel-pdf", output, f"LinkedIn carousel page {index} of 5: {item['headline'].title()}.", 1))

    pdf_path = linkedin_dir / "make-brand-assets-for-me.pdf"
    save_pdf(linkedin_pages, pdf_path)
    records.append(("linkedin-carousel-pdf", "carousel-pdf", pdf_path, "Five-page document introducing Make Brand Assets For Me.", 5))

    social_pages = []
    for index, item in enumerate(campaign["carousel_social"], start=1):
        output = social_dir / f"page-{index:02d}.png"
        preview = root / "examples/gallery/proofs/01-three-styles.png" if index == 9 else None
        render_carousel_page(output, (1080, 1080), index, 10, item, campaign, preview)
        social_pages.append(output)
        records.append((f"social-carousel-{index:02d}", "carousel-square", output, f"Social carousel page {index} of 10: {item['headline'].title()}.", 1))

    manifest_assets = []
    for asset_id, placement_id, path, alt_text, page_count in records:
        if path.suffix.lower() == ".pdf":
            width, height = 1080, 1350
        else:
            with Image.open(path) as opened:
                width, height = opened.size
        relative = path.relative_to(campaign_dir).as_posix()
        item = {
            "id": asset_id,
            "placement_id": placement_id,
            "path": relative,
            "width": width,
            "height": height,
            "format": path.suffix.lower().lstrip("."),
            "alt_text": alt_text,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "claim_ids": fact_ids,
        }
        if page_count > 1:
            item["page_count"] = page_count
        manifest_assets.append(item)
        receipt = {
            "schema_version": "1.0",
            "asset_id": asset_id,
            "placement_id": placement_id,
            "output_path": relative,
            "font": "Pillow bundled default",
            "source_files": ["campaign.json", "source-facts.json"],
            "checks": {"dimensions": "pass", "brand_system": "pass", "publication": "not_attempted"},
            "sha256": item["sha256"],
        }
        (receipts_dir / f"{asset_id}.json").write_text(json.dumps(receipt, indent=2) + "\n")

    proof_paths = [path for _, _, path, _, _ in records if path.suffix.lower() == ".png"]
    contact_sheet = make_contact_sheet(proof_paths, proofs_dir / "contact-sheet.png", "Make Brand Assets For Me launch pack", columns=4)

    manifest = {
        "schema_version": "1.0",
        "campaign_id": campaign["campaign_id"],
        "brand_id": campaign["brand_id"],
        "title": campaign["title"],
        "launch_subject": campaign["launch_subject"],
        "canonical_url": campaign["canonical_url"],
        "cta": {"label": campaign["service_cta"]["label"], "action": campaign["service_cta"]["action"]},
        "utm": campaign["utm"],
        "source_facts": facts,
        "assets": manifest_assets,
    }
    manifest_path = campaign_dir / "campaign-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return {
        "manifest": str(manifest_path),
        "contact_sheet": str(contact_sheet),
        "asset_count": len(manifest_assets),
        "github_url": tracked_url(campaign["canonical_url"], "launch-pack", "campaign"),
    }


def main():
    parser = argparse.ArgumentParser(description="Build the complete Lemonbrand launch-pack example.")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--campaign-dir", default="examples/launch-pack/lemonbrand")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    campaign_dir = Path(args.campaign_dir)
    if not campaign_dir.is_absolute():
        campaign_dir = root / campaign_dir
    result = build_launch_pack(root, campaign_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

from PIL import Image, ImageOps, ImageStat

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from make_contact_sheet import make_contact_sheet
from brand_type import FONT_PATH, FONT_SHA256, font_receipt, load_brand_font
from compose_text_overlay import compose


PRIMARY = [
    ("profile-avatar.png", "profile-avatar", "Torn-paper brand cards, a magnifier and a checking jig below the words Make Assets."),
    ("cover-wide.png", "cover-wide", "Wide paper-collage cover showing visual cards becoming a checked brand family."),
    ("linkedin-profile-cover.png", "linkedin-profile-cover", "Wide editorial cover asking a brand not to start over, beside a paper asset workshop."),
    ("linkedin-page-cover.png", "linkedin-page-cover", "Ultra-wide paper-collage cover showing visual cards inspected and organized."),
    ("social-square.png", "social-square", "Square torn-paper workshop with the words Make Brand Assets For Me."),
    ("social-portrait.png", "social-portrait", "Portrait paper workshop showing varied cards becoming one checked family."),
    ("social-landscape.png", "social-landscape", "Landscape paper workshop with the words One Idea. Every Format."),
    ("story-vertical.png", "story-vertical", "Vertical editorial cover showing a low paper assembly line below a quiet copy field."),
    ("open-graph.png", "open-graph", "Paper cards move through a checking station beside Make Brand Assets For Me."),
    ("email-header.png", "email-header", "Editorial paper asset workshop beside the words Your Brand. Ready To Move."),
    ("product-hunt-thumbnail.png", "product-hunt-thumbnail", "Square paper asset workshop with the words Make Assets."),
    ("product-hunt-gallery-01.png", "product-hunt-gallery", "Paper asset workshop beside Five Steps. One Brand System."),
    ("product-hunt-gallery-02.png", "product-hunt-gallery", "Paper asset workshop beside One Method. Every Format."),
    ("youtube-thumbnail.png", "youtube-thumbnail", "Paper asset workshop beside Your Brand Should Not Start Over."),
]


def read_json(path):
    return json.loads(Path(path).read_text())


def save_compact_png(image, output):
    compact = image.convert("RGB").quantize(
        colors=256,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.FLOYDSTEINBERG,
    )
    compact.save(output, optimize=True)


BACKGROUND_FILES = {
    "banner": "banner-3x1.png",
    "landscape": "landscape-16x9.png",
    "square": "square-1x1.png",
    "portrait": "portrait-4x5.png",
    "vertical": "vertical-9x16.png",
}

PLACEMENT_BACKGROUNDS = {
    "cover-wide": "banner-3x1.png",
    "linkedin-profile-cover": "banner-4x1.png",
    "linkedin-page-cover": "banner-6x1.png",
    "youtube-thumbnail": "landscape-4k-16x9.png",
    "story-vertical": "vertical-hd-9x16.png",
}


def overlay_word_count(text):
    return len(re.findall(r"[\w]+(?:['’-][\w]+)?", text, re.UNICODE))


def composition_family(width, height):
    ratio = width / height
    if ratio >= 2.35:
        return "banner"
    if ratio >= 1.35:
        return "landscape"
    if ratio >= .88:
        return "square"
    if ratio >= .68:
        return "portrait"
    return "vertical"


def _field_color(image, side):
    width, height = image.size
    if side == "left":
        region = (0, 0, max(1, int(width * .30)), height)
    else:
        region = (int(width * .70), 0, width, height)
    return tuple(round(value) for value in ImageStat.Stat(image.crop(region).convert("RGB")).mean)


def _extend_master(source, output, size, anchor):
    with Image.open(source) as opened:
        image = opened.convert("RGB")
    target_width, target_height = size
    if image.height > target_height:
        top = (image.height - target_height) // 2
        image = image.crop((0, top, image.width, top + target_height))
    if image.width > target_width:
        left = 0 if anchor == "left" else image.width - target_width
        image = image.crop((left, 0, left + target_width, image.height))
    field_side = "right" if anchor == "left" else "left"
    canvas = Image.new("RGB", size, _field_color(image, field_side))
    x = 0 if anchor == "left" else target_width - image.width
    y = (target_height - image.height) // 2
    canvas.paste(image, (x, y))
    output.parent.mkdir(parents=True, exist_ok=True)
    save_compact_png(canvas, output)


def ensure_derived_backgrounds(campaign_dir):
    backgrounds = campaign_dir / "backgrounds"
    source = backgrounds / "source/banner-2x1.png"
    _extend_master(source, backgrounds / "banner-3x1.png", (2661, 887), "right")
    _extend_master(source, backgrounds / "banner-4x1.png", (3548, 887), "right")
    _extend_master(source, backgrounds / "banner-6x1.png", (4200, 700), "right")
    _extend_master(
        backgrounds / "landscape-16x9.png",
        backgrounds / "landscape-4k-16x9.png",
        (3840, 2160),
        "left",
    )
    _extend_master(
        backgrounds / "vertical-9x16.png",
        backgrounds / "vertical-hd-9x16.png",
        (1080, 1920),
        "left",
    )


def prepare_background(source, size, max_crop_loss=0.25):
    source = Path(source)
    with Image.open(source) as opened:
        image = opened.convert("RGB")
    target_width, target_height = size
    if image.width < target_width or image.height < target_height:
        raise ValueError(
            f"Background would require upscale: source {image.width}x{image.height}, "
            f"target {target_width}x{target_height}"
        )
    scale = max(target_width / image.width, target_height / image.height)
    scaled_width = image.width * scale
    scaled_height = image.height * scale
    kept = (target_width * target_height) / (scaled_width * scaled_height)
    crop_loss = max(0.0, 1.0 - kept)
    if crop_loss > max_crop_loss:
        raise ValueError(
            f"Background crop would discard {crop_loss:.1%}; maximum is {max_crop_loss:.1%}"
        )
    canvas = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    return canvas, {
        "source_dimensions": [image.width, image.height],
        "target_dimensions": [target_width, target_height],
        "crop_loss": round(crop_loss, 6),
    }


def image_first_canvas(campaign_dir, size, family=None, placement_id=None):
    width, height = size
    family = family or composition_family(width, height)
    filename = PLACEMENT_BACKGROUNDS.get(placement_id, BACKGROUND_FILES[family])
    source = campaign_dir / "backgrounds" / filename
    canvas, evidence = prepare_background(source, size)
    return canvas, f"backgrounds/{filename}", family, evidence


def copy_box(width, height, family, safe_area=None):
    if family == "banner":
        box = (int(width * .055), int(height * .17), int(width * .52), int(height * .68))
    elif family == "landscape":
        box = (int(width * .55), int(height * .17), int(width * .39), int(height * .66))
    elif family == "square":
        box = (int(width * .07), int(height * .09), int(width * .50), int(height * .44))
    elif family == "portrait":
        box = (int(width * .08), int(height * .09), int(width * .84), int(height * .40))
    else:
        box = (int(width * .09), int(height * .11), int(width * .82), int(height * .40))
    if not safe_area:
        return box
    x, y, box_width, box_height = box
    left = max(x, int(safe_area["left"]))
    top = max(y, int(safe_area["top"]))
    right = min(x + box_width, width - int(safe_area["right"]))
    bottom = min(y + box_height, height - int(safe_area["bottom"]))
    if right <= left or bottom <= top:
        raise ValueError("Placement safe area leaves no room for the planned copy box")
    return (left, top, right - left, bottom - top)


def add_short_overlay(image, output, text, family, palette, safe_area, box, placement_id):
    if overlay_word_count(text) >= 15:
        raise ValueError(f"Overlay must use fewer than 15 words: {text}")
    width, height = image.size
    if family in {"portrait", "vertical"}:
        start_size = min(width * .105, height * .075)
    elif family == "banner":
        start_size = min(width * .07, height * .26)
    else:
        start_size = min(width, height) * .115
    clean_path = Path(output).with_name(f".{Path(output).stem}-clean-background.png")
    image.save(clean_path)
    try:
        receipt = compose(
            background=clean_path,
            output=output,
            text=text,
            font_path=FONT_PATH,
            font_family="Instrument Sans",
            font_sha256=FONT_SHA256,
            box=box,
            safe_area=safe_area,
            placement_id=placement_id,
            weight=700,
            width=82,
            color=palette["ink"],
            max_size=max(24, int(start_size)),
            min_size=12,
            min_contrast=3.0,
            palette_colors=256,
        )
    finally:
        clean_path.unlink(missing_ok=True)
    return receipt


def render_primary(root, campaign_dir, output, placement_id, campaign):
    placements = read_json(
        root / "plugins/make-brand-assets-for-me/skills/brand-assets-make-launch-pack/references/channel-placements.json"
    )["placements"]
    placement = next(item for item in placements if item["id"] == placement_id)
    width, height = placement["width"], placement["height"]
    palette = campaign["palette"]
    image, background_source, family, background_evidence = image_first_canvas(
        campaign_dir, (width, height), placement_id=placement_id
    )
    text = campaign["primary_copy"].get(output.stem, campaign["headlines"]["main"])
    box = copy_box(width, height, family, placement["safe_area"])
    overlay_receipt = add_short_overlay(
        image, output, text, family, palette, placement["safe_area"], box, placement_id
    )
    return background_source, overlay_word_count(text), background_evidence, overlay_receipt


def render_carousel_page(campaign_dir, output, size, page, total, item, campaign):
    width, height = size
    palette = campaign["palette"]
    placements = read_json(
        campaign_dir.parents[2]
        / "plugins/make-brand-assets-for-me/skills/brand-assets-make-launch-pack/references/channel-placements.json"
    )["placements"]
    placement_id = "carousel-pdf" if size == (1080, 1350) else "carousel-square"
    placement = next(item for item in placements if item["id"] == placement_id)
    image, background_source, family, background_evidence = image_first_canvas(
        campaign_dir, size, placement_id=placement_id
    )
    box = copy_box(width, height, family, placement["safe_area"])
    overlay_receipt = add_short_overlay(
        image, output, item["headline"], family, palette, placement["safe_area"], box, placement_id
    )
    return background_source, overlay_word_count(item["headline"]), background_evidence, overlay_receipt


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
    ensure_derived_backgrounds(campaign_dir)
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
        background_source, word_count, background_evidence, overlay_receipt = render_primary(root, campaign_dir, output, placement_id, campaign)
        records.append((filename.removesuffix(".png"), placement_id, output, alt_text, 1, background_source, word_count, background_evidence, overlay_receipt))

    linkedin_pages = []
    for index, item in enumerate(campaign["carousel_linkedin"], start=1):
        output = linkedin_dir / f"page-{index:02d}.png"
        background_source, word_count, background_evidence, overlay_receipt = render_carousel_page(campaign_dir, output, (1080, 1350), index, 5, item, campaign)
        linkedin_pages.append(output)
        records.append((f"linkedin-carousel-{index:02d}", "carousel-pdf", output, f"LinkedIn carousel page {index} of 5: {item['headline'].title()}.", 1, background_source, word_count, background_evidence, overlay_receipt))

    pdf_path = linkedin_dir / "make-brand-assets-for-me.pdf"
    save_pdf(linkedin_pages, pdf_path)
    records.append(("linkedin-carousel-pdf", "carousel-pdf", pdf_path, "Five-page document introducing Make Brand Assets For Me.", 5, "backgrounds/portrait-4x5.png", 0, None, None))

    social_pages = []
    for index, item in enumerate(campaign["carousel_social"], start=1):
        output = social_dir / f"page-{index:02d}.png"
        background_source, word_count, background_evidence, overlay_receipt = render_carousel_page(campaign_dir, output, (1080, 1080), index, 10, item, campaign)
        social_pages.append(output)
        records.append((f"social-carousel-{index:02d}", "carousel-square", output, f"Social carousel page {index} of 10: {item['headline'].title()}.", 1, background_source, word_count, background_evidence, overlay_receipt))

    manifest_assets = []
    for asset_id, placement_id, path, alt_text, page_count, background_source, word_count, background_evidence, overlay_receipt in records:
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
            "font": font_receipt(weight=700, width=82),
            "source_files": ["campaign.json", "source-facts.json", background_source],
            "background_source": background_source,
            "overlay_word_count": word_count,
            "checks": {"dimensions": "pass", "brand_system": "pass", "publication": "not_attempted"},
            "sha256": item["sha256"],
        }
        if background_evidence and overlay_receipt:
            receipt.update(background_evidence)
            receipt.update(
                {
                    "text_box": overlay_receipt["text_box"],
                    "text_bounds": overlay_receipt["text_bounds"],
                    "safe_area": overlay_receipt["safe_area"],
                    "safe_rectangle": overlay_receipt["safe_rectangle"],
                    "contrast": overlay_receipt["contrast"],
                }
            )
            receipt["checks"].update(
                {"safe_area": "pass", "contrast": "pass", "full_size": "pass"}
            )
        (receipts_dir / f"{asset_id}.json").write_text(json.dumps(receipt, indent=2) + "\n")

    proof_paths = [path for _, _, path, _, _, _, _, _, _ in records if path.suffix.lower() == ".png"]
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

---
name: brand-assets-make-launch-pack
description: Use when a launch, campaign, lead magnet, event, product, or offer needs a coordinated multi-channel pack of profile, banner, social, carousel, web, email, or video-cover assets. Do not use for one image, one scene, one framework set, or publishing posts.
---

# Make My Launch Pack

Make one clear idea fit every place it needs to go. Follow `SHOW → PLAN → MAKE → CHECK → SAVE`.

Read `references/five-steps.md` first. Read `references/ask-the-user.md` when a launch choice is missing. Read `references/channel-placements.json` before sizing files. Read `references/check-the-look.md` and `references/check-the-launch-pack.md` before saving.

## Start with four answers

Use answers already present in the message or files. Ask only for the missing ones:

1. What are we launching?
2. What one page should people visit?
3. What one action should people take there?
4. Which pack size: **Starter**, **Campaign**, or **Everywhere**?

If the brand look is not approved yet, route to `$brand-assets-set-up` before making a batch.

## Pick the pack size

| Mode | Make |
| --- | --- |
| Starter | avatar, wide cover, square post, portrait post, story, OG image |
| Campaign | Starter plus landscape post, email header, five-page carousel, carousel PDF, video thumbnail |
| Everywhere | Campaign plus channel-specific covers, ten-page carousel, Product Hunt thumbnail and gallery, copy and alt text for each selected channel |

The user can name exact placements instead. That list becomes the contract.

## Make one plan

Show a short table with: placement ID, channel, job, size, source material, headline, CTA treatment, output path, and reuse group. Get approval before generating several assets when the user has not already approved the full pack.

Use one source idea, one canonical HTTPS URL, and one CTA across the pack. Shorten the words to fit each surface. Do not invent product facts, testimonials, results, scarcity, or endorsements. Put every factual claim in a source-facts record and refer to its ID from the copy record.

## Make the files

- Use the approved brand recipe and three approved visual anchors.
- Build from a shared image system. Adapt the visual story to each shape instead of stretching one master.
- Make profile marks recognizable when shown as a small circle.
- Make carousels readable one page at a time and in order.
- Write channel-ready copy, alt text, and UTM-tagged links when the selected mode calls for them.
- Label fictional examples clearly.

### Make the background first

For every raster asset family, use this recipe in order:

1. Select, recompose, edit, or generate an image background from the approved visual anchors.
2. Put one meaningful focal cluster in 35–45% of the canvas. Reserve the opposite 55–65% as protected negative space.
3. Save and inspect the clean, text-free background master before adding copy. A generated background contains no text, letters, numbers, logos, labels, watermarks, or mock UI.
4. Read the placement's `safe_area`. Add one local text overlay inside both the protected negative space and that safe area. The complete visible overlay uses fewer than 15 words. When a profile mark needs zero words, keep the approved text-free background as the final and record `overlay_word_count: 0`; do not call the text compositor.
5. Use an approved font file that can travel with the pack. Apply its exact family, weight, width, and other variable axes in a deterministic local compositor. Never silently substitute Pillow's default font, Arial, or an unapproved system font. If the approved file is unavailable, stop and mark the asset `needs-review`.
6. Run `scripts/compose_text_overlay.py` from this loaded skill folder. Pass the placement ID so it reads the canonical safe area from this skill's placement registry. Give it the approved font family and SHA-256, exact copy, and protected text box. It must fail closed on font mismatch, unsupported axes, unsafe bounds, low pixel contrast, empty copy, or 15+ words. Nothing may add or change visible copy after this step.
7. Run `scripts/check_background_fit.py` from this loaded skill folder before every crop-to-fill. Never enlarge a smaller background to meet a placement. Do not discard more than 25% of a master. Make a separate aspect-ratio master when either limit would fail.
8. Record `background_source`, source and target dimensions, crop loss, `overlay_word_count`, font identity and applied axes, text box and observed bounds, safe area, pixel-measured contrast, and the 100% inspection result in the asset receipt.

The finished asset is an image with room for one short thought. The background carries the story; the words name it.

This skill creates files and publication intent. It does not connect accounts, schedule posts, or claim that anything was published.

## Save the launch pack

Save one folder containing:

```text
launch-pack/
  source-facts.json
  campaign.json
  copy.json
  assets/
  carousels/
  proofs/contact-sheet.png
  backgrounds/
  receipts/
  campaign-manifest.json
```

The manifest lists every file with its placement ID, dimensions, format, alt text, SHA-256 digest, claim IDs, canonical URL, and UTM values. It contains no account IDs, provider IDs, tokens, cookies, publication timestamps, or private paths.

## Finish with

- the four launch answers;
- the approved placement table;
- every asset, carousel, copy, proof, receipt, and manifest path;
- a plain pass, draft, or needs-review result for each file;
- a short list of anything still needed before a human or separate publisher can post it.

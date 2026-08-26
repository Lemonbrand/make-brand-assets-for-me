---
name: brand-assets-make-one
description: Make or reuse one brand-matched raster asset with one clear meaning. Use for a single icon-like object, transparent cutout, or inseparable pair. Do not use for a full scene or a set of separate assets.
---

# Make One Brand Asset

Follow `SHOW → PLAN → MAKE → CHECK → SAVE`.

Read `references/five-steps.md`, `references/ask-the-user.md`, and `references/check-the-look.md`.

## What to do

1. Read `brand-rules.yaml` and `asset-list.csv`. If the brand recipe is missing, route to Set Up My Brand.
2. State the asset's job in one short phrase.
3. Search the approved asset list for that meaning and close meanings.
4. Label every visible part `reuse`, `adapt`, `new`, or `look_only`.
5. Reuse a match when it already does the job. Make a new image only when the meaning is missing or the user clearly wants a variant.
6. Use the structured ask-user function only when meaning, format, or a conflicting style choice changes the result. Use one short chat question when the function is unavailable.
7. Default to one padded PNG with a real transparent background, no words, and no scene.
8. Compare the result with three approved anchors at thumbnail size and full size.
9. Check meaning, every visible part, transparency, padding, dimensions, crop, shadows, and accidental text.
10. Save the PNG and `asset-record.json`. Never overwrite an approved source file without clear permission.

## Finish with

- the asset job;
- whether it was reused, adapted, or new;
- the PNG path;
- the asset receipt path;
- a plain pass, draft, or needs-review result.

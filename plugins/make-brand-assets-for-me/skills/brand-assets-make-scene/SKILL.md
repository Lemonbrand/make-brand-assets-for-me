---
name: brand-assets-make-scene
description: Make one integrated brand scene with several visual parts and deliberate room for copy. Use for website art, editorial scenes, heroes, or social images. Do not use for one isolated object or several separate files.
---

# Make A Brand Scene

Follow `SHOW → PLAN → MAKE → CHECK → SAVE`.

Read `references/five-steps.md`, `references/ask-the-user.md`, and `references/check-the-look.md`.

## What to do

1. Read the brand recipe and approved asset list.
2. Set the surface, image size or ratio, main subject side, copy side, copy percentage, and required objects.
3. When any of those choices is missing and changes the layout, use the structured ask-user function. Use one short chat question when it is unavailable.
4. State the reading order and protected copy area.
5. Label every visible part `reuse`, `adapt`, `new`, or `look_only`.
6. Choose the smallest useful route: select, recompose, edit, or generate.
7. Keep supplied words outside the PNG unless the user clearly asks for baked text. When they do, save and approve the text-free background first. Run `scripts/check_background_fit.py` from this loaded skill folder before crop-to-fill, then run `scripts/compose_text_overlay.py`. Give the compositor the approved font family and SHA-256, platform safe-area margins, exact copy, and protected text box. Never ask an image model to draw the words and never use a silent fallback font.
8. Compare the result with three approved anchors at thumbnail and full size.
9. Check meaning, clutter, contrast, crop, every visible part, and accidental text.
10. Check the actual pixels in the protected copy area and save a proof overlay. Inspect the clean background and final image separately at thumbnail size and 100%. The final receipt must record the observed font identity, applied axes, text bounds, safe area, and pixel-measured contrast.
11. Save the scene PNG, copy-space proof PNG, and asset receipt.

## Finish with

- surface and dimensions;
- main subject and copy sides;
- scene path;
- proof path;
- receipt path;
- pass, draft, or needs-review result.

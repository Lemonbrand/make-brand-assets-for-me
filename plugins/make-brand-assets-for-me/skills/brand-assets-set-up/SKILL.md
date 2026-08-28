---
name: brand-assets-set-up
description: Set up simple local brand rules from user-supplied visual references before making brand assets. Use for a new brand or a major style change. Do not use when an approved brand-rules.yaml already answers the request.
---

# Set Up My Brand

Turn approved examples into a brand recipe that the other skills can follow.

Read `references/five-steps.md`, `references/ask-the-user.md`, and `references/check-the-look.md`.

## What to do

1. Find the reference files the user supplied. Do not search private accounts or upload files unless asked.
2. Sort each reference into `reuse`, `adapt`, `look_only`, or `do_not_use`.
3. Use the host's structured ask-user function when a missing choice changes the result. In Codex, use `request_user_input` when available. Ask one to three short questions with the recommended choice first. If the function is missing, ask one short chat question.
4. Do not ask for facts the files already show. State what you found before asking.
5. Write `brand-rules.yaml`, `asset-list.csv`, and `brand-rules-summary.md` with relative local paths.
6. Show the short summary and ask the user to approve it before another skill makes images.
7. Stop after setup. Do not generate artwork in this workflow.

## Brand recipe

Record materials, colors, lines and shapes, texture, shadows and depth, layout, type, motion, three approved anchors, and things to avoid. For baked copy, record the approved font file, family, SHA-256, source or license, weight, width, case, color, and fallback rule. Missing font evidence means `stop-and-ask`, not permission to use a default.

Record whether the user confirmed permission to use the references. Do not make a legal-clearance claim.

## Finish with

- the three saved paths;
- what is approved;
- what still needs a decision;
- the next plain action, such as “Use Make One Brand Asset.”

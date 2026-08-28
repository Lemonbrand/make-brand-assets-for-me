---
name: brand-assets-start-here
description: Guide the first use of Make Brand Assets For Me. Use when someone just installed the plugin, asks how to use it, wants help starting, or wants to make a first brand asset. Do not use when the user already named a specific brand-assets workflow.
---

# Start Making Brand Assets

Help the user begin. Keep this shorter than a product tour.

## First response

Say what will happen in plain language:

1. They show the model two or three approved visual examples.
2. The model writes a small reusable brand recipe.
3. They approve the recipe before any new image is made.

Then use the host's structured ask-user function when it is available. In Codex, use `request_user_input`. Ask one question with these choices:

- **Add my examples (Recommended):** continue with the user's approved logo, artwork, screenshots, or brand guide.
- **Use the demo:** explain the workflow with the fictional examples bundled with this plugin.

If the function is unavailable, ask the same single question in normal chat. Do not print tool JSON or pretend a function exists.

## Continue

- When the user supplies references, state which files you found and hand the work to `$brand-assets-set-up`.
- If the user already supplied references, do not ask for them again. Hand the work to `$brand-assets-set-up` immediately.
- When the user chooses the demo, point to `examples/gallery/proofs/01-three-styles.png` when it is reachable. Explain **Show → Plan → Make → Check → Save** in five short lines, then ask whether to use their own examples.
- If the user asks for the full menu, name the six production workflows in one compact list. Otherwise, do not make them choose a workflow yet.

## Boundaries

- Approved references come from the user. Do not search private accounts.
- Do not generate artwork before the brand recipe is approved.
- Do not upload, publish, or replace files without explicit permission.
- If image generation is unavailable in the current host, say so before setup and preserve the recipe so it can be used in a visual host.

Finish this workflow when `$brand-assets-set-up` begins or when the user has a clear next action.

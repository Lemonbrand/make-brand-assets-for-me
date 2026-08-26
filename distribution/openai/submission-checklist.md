# OpenAI Submission Checklist

Use the [OpenAI plugin submission portal](https://platform.openai.com/apps-manage) after the public GitHub repository is live.

## Account

- Select the OpenAI organization that should own the listing.
- Confirm the submitter has **Apps Management: Write**.
- Complete any identity or organization verification requested by the portal.

## Package

- Choose a skills-only plugin.
- Use `plugins/make-brand-assets-for-me/` as the plugin folder.
- Confirm version `0.1.0` and license `MIT`.
- Validate all five skills before upload.
- Do not upload screenshots. This is a skills-only plugin with no plugin UI. Keep the proof images in the GitHub README instead.

## Listing

- Paste the copy from `distribution/openai/listing.md`.
- Add all three starter prompts.
- Add the five positive and three negative cases from `test-cases.json`.
- Use `https://lemonbrand.io/privacy` for privacy.
- Use `https://lemonbrand.io/terms` for terms.
- Use `hello@lemonbrand.io` for support.

## Final check

- Make sure the plugin does not advertise inside generated assets or ordinary skill output.
- Make sure every example brand is fictional.
- Submit once, record the submission ID, and keep review feedback with the release notes.

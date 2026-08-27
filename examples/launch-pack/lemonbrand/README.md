# Lemonbrand worked launch pack

This folder is the public proof for **Make My Launch Pack**. One campaign file renders the profile, banner, feed, story, carousel, website, email, Product Hunt and YouTube graphics used to launch the free plugin.

Every raster starts as a clean editorial image background. Each background uses one compact focal story and a protected field of negative space. The words are added afterwards as a local layout layer, and every finished overlay uses fewer than 15 words.

The five clean masters are in `backgrounds/`. Their generated pixels contain no text, logos, labels, or mock interface. Each raster receipt names the background it used and records its overlay word count.

Rebuild everything from the repository root:

```bash
python3 scripts/build_launch_example.py --root .
python3 scripts/check_campaign_manifest.py examples/launch-pack/lemonbrand/campaign-manifest.json
```

Start with `proofs/contact-sheet.png`. Read `campaign-manifest.json` for sizes, alt text, claim links and digests. Read `copy.json` for channel-ready copy and tracked links. Read `backgrounds/generation-receipts.json` for the reusable image-first composition contract.

The package creates publication-ready files. It does not claim they were posted. Provider IDs and publication receipts belong in a separate private distribution system.

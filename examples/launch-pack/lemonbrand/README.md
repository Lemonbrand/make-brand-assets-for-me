# Lemonbrand worked launch pack

This folder is the public proof for **Make My Launch Pack**. One campaign file renders the profile, banner, feed, story, carousel, website, email, Product Hunt and YouTube graphics used to launch the free plugin.

The cut-paper, soft-clay and bold-print images shown inside the layouts are fictional brand examples. They prove that the method can keep different visual systems separate. They are not a customer portfolio.

Rebuild everything from the repository root:

```bash
python3 scripts/build_launch_example.py --root .
python3 scripts/check_campaign_manifest.py examples/launch-pack/lemonbrand/campaign-manifest.json
```

Start with `proofs/contact-sheet.png`. Read `campaign-manifest.json` for sizes, alt text, claim links and digests. Read `copy.json` for channel-ready copy and tracked links.

The package creates publication-ready files. It does not claim they were posted. Provider IDs and publication receipts belong in a separate private distribution system.

# Make A Release

1. Run every test.
2. Check both shared-rule and public-skill synchronization.
3. Run the private-stuff scan.
4. Check both plugin manifests.
5. Update `VERSION`, both manifests, both marketplaces, and `CHANGELOG.md`.
6. Run `python3 scripts/build_release.py`.
7. Open the ZIP list and confirm the Codex, Claude, and top-level skill files are inside.

Share the ZIP only after the release manifest has a passing result.

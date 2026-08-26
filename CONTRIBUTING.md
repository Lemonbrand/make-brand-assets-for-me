# Contributing

Thanks for helping make this clearer and more useful.

## Good contributions

- clearer steps;
- better routing examples;
- safer checks;
- fixes for Codex, Claude Code, or Agent Skills compatibility;
- fictional test styles that prove the method without copying a customer;
- accessibility improvements to docs and screenshots.

## Before you open a pull request

```bash
python3 scripts/sync_shared_rules.py --check
python3 scripts/sync_distribution_skills.py --check
pytest -q tests
python3 scripts/check_package.py
python3 scripts/check_for_private_stuff.py
```

Do not submit customer artwork, private links, credentials, or brand materials you do not have permission to share.

Keep user-facing writing simple. Explain technical file names in plain language the first time they appear.

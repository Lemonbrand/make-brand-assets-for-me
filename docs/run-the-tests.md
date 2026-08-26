# Run The Tests

From the repo root:

```bash
pytest -q tests
python3 scripts/sync_shared_rules.py --root . --check
python3 scripts/sync_distribution_skills.py --root . --check
python3 scripts/check_package.py .
python3 scripts/check_for_private_stuff.py .
```

Do not make a release while a check is failing.

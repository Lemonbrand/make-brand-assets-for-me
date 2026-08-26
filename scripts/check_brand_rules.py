#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


REQUIRED = ("version", "brand_name", "brand_id", "references", "look", "checks", "rights")


def _top_level_keys(text):
    return {
        match.group(1)
        for line in text.splitlines()
        if (match := re.match(r"^([a-z][a-z0-9_]*)\s*:\s*", line))
    }


def check_brand_rules(path):
    path = Path(path)
    if not path.exists():
        return [f"File not found: {path}"]
    keys = _top_level_keys(path.read_text())
    return [f"Missing key: {key}" for key in REQUIRED if key not in keys]


def main():
    parser = argparse.ArgumentParser(description="Check a brand recipe.")
    parser.add_argument("path")
    args = parser.parse_args()
    errors = check_brand_rules(args.path)
    print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()

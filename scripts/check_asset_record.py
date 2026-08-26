#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


REQUIRED = ("version", "asset_job", "brand_id", "route", "parts", "prompt", "output_path", "checks", "publish_status")
ROUTES = {"reuse", "adapt", "new", "look_only"}


def check_asset_record(path):
    path = Path(path)
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        return [f"Could not read asset receipt: {error}"]
    errors = [f"Missing key: {key}" for key in REQUIRED if key not in data]
    if data.get("route") not in ROUTES:
        errors.append("route must be reuse, adapt, new, or look_only")
    output = data.get("output_path")
    if output and not (path.parent / output).exists():
        errors.append(f"Output file not found: {output}")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Check an asset receipt.")
    parser.add_argument("path")
    args = parser.parse_args()
    errors = check_asset_record(args.path)
    print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()

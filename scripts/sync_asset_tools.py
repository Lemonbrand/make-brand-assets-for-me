#!/usr/bin/env python3
"""Keep portable raster tools identical inside every copy-bearing skill."""

import argparse
import shutil
from pathlib import Path


SKILLS = ("brand-assets-make-scene", "brand-assets-make-launch-pack")
TOOLS = ("compose_text_overlay.py", "check_background_fit.py")


def sync_asset_tools(root, check_only=False):
    root = Path(root).resolve()
    errors = []
    for skill in SKILLS:
        folder = root / "plugins/make-brand-assets-for-me/skills" / skill / "scripts"
        for name in TOOLS:
            source = root / "scripts" / name
            target = folder / name
            if not source.exists():
                errors.append(f"Missing canonical tool: scripts/{name}")
                continue
            if target.exists() and target.read_bytes() == source.read_bytes():
                continue
            if check_only:
                errors.append(f"Portable tool is out of sync: {target.relative_to(root)}")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return errors


def main():
    parser = argparse.ArgumentParser(description="Synchronize portable brand-asset tools.")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = sync_asset_tools(args.root, check_only=args.check)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("PASS: portable asset tools are synchronized")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import hashlib
import shutil
from pathlib import Path


def file_digests(root):
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def sync_skills(root, check_only=False):
    root = Path(root)
    source = root / "plugins/make-brand-assets-for-me/skills"
    target = root / "skills"
    if not source.exists():
        return ["Missing canonical plugin skills"]

    if check_only:
        if file_digests(source) == file_digests(target):
            return []
        return ["Top-level skills do not match the canonical plugin skills"]

    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    return []


def main():
    parser = argparse.ArgumentParser(description="Keep public Agent Skills copies in sync with the plugin.")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = sync_skills(args.root, check_only=args.check)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("PASS: public skills match the canonical plugin skills.")


if __name__ == "__main__":
    main()

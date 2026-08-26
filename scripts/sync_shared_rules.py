#!/usr/bin/env python3
import argparse
import hashlib
import shutil
from pathlib import Path


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sync_shared_rules(root, check_only=False):
    root = Path(root)
    master = root / "source/shared-rules"
    skills = root / "plugins/make-brand-assets-for-me/skills"
    problems = []
    for skill in sorted(path for path in skills.iterdir() if (path / "SKILL.md").exists()):
        target_dir = skill / "references"
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in sorted(master.glob("*.md")):
            target = target_dir / source.name
            matches = target.exists() and _digest(target) == _digest(source)
            if matches:
                continue
            if check_only:
                problems.append(f"Shared rule is missing or out of date: {target.relative_to(root)}")
            else:
                shutil.copy2(source, target)
    return problems


def main():
    parser = argparse.ArgumentParser(description="Copy or check shared skill rules.")
    parser.add_argument("--root", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    problems = sync_shared_rules(args.root, args.check)
    for problem in problems:
        print(problem)
    raise SystemExit(bool(problems))


if __name__ == "__main__":
    main()

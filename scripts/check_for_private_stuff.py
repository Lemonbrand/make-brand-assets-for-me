#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".toml", ".svg"}
SKIP_PARTS = {".git", "release", "__pycache__", ".pytest_cache"}
PATTERNS = {
    "private Drive link": "drive." + "google.com",
    "local Mac home path": "/" + "Users" + "/",
    "source project name": "DA" + "WN",
    "unfinished marker": "[TO" + "DO",
    "unfinished text": "T" + "BD",
}
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^'\"]{8,}"),
]


def scan(root):
    root = Path(root)
    findings = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_PARTS for part in path.relative_to(root).parts):
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for label, needle in PATTERNS.items():
            if needle in text:
                findings.append({"file": str(path.relative_to(root)), "reason": label})
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"file": str(path.relative_to(root)), "reason": "possible secret"})
    return findings


def main():
    parser = argparse.ArgumentParser(description="Find private links, local paths, secrets, and unfinished notes.")
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    findings = scan(args.root)
    if findings:
        for finding in findings:
            print(f"FAIL {finding['file']}: {finding['reason']}")
        raise SystemExit(1)
    print("PASS: no private links, internal project names, local home paths, likely secrets, or unfinished notes found.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


SKILLS = {
    "brand-assets-set-up",
    "brand-assets-make-one",
    "brand-assets-make-scene",
    "brand-assets-make-set",
    "brand-assets-make-move",
    "brand-assets-make-launch-pack",
}


def check_package(root):
    root = Path(root)
    errors = []
    required = [
        "README.md",
        "LICENSE.md",
        "TRADEMARKS.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "VERSION",
        ".agents/plugins/marketplace.json",
        ".claude-plugin/marketplace.json",
        "plugins/make-brand-assets-for-me/.codex-plugin/plugin.json",
        "plugins/make-brand-assets-for-me/.claude-plugin/plugin.json",
        "distribution/openai/test-cases.json",
        "distribution/launch/launch-copy.md",
        "plugins/make-brand-assets-for-me/assets/icon.png",
        "plugins/make-brand-assets-for-me/assets/logo-light.png",
        "plugins/make-brand-assets-for-me/assets/logo-dark.png",
        "plugins/make-brand-assets-for-me/assets/social-preview.png",
    ]
    for relative in required:
        if not (root / relative).exists():
            errors.append(f"Missing: {relative}")

    skills_dir = root / "plugins/make-brand-assets-for-me/skills"
    found = {path.name for path in skills_dir.iterdir() if path.is_dir()} if skills_dir.exists() else set()
    if found != SKILLS:
        errors.append(f"Expected six skills, found: {', '.join(sorted(found))}")
    for name in SKILLS:
        for relative in ("SKILL.md", "agents/openai.yaml"):
            if not (skills_dir / name / relative).exists():
                errors.append(f"Missing: skills/{name}/{relative}")

    public_skills_dir = root / "skills"
    public_found = {path.name for path in public_skills_dir.iterdir() if path.is_dir()} if public_skills_dir.exists() else set()
    if public_found != SKILLS:
        errors.append(f"Expected six public skills, found: {', '.join(sorted(public_found))}")

    counts = {
        "baseline PNGs": (root / "examples/gallery/outputs", "*.png", 10),
        "asset receipts": (root / "examples/records", "*.json", 10),
        "proof sheets": (root / "examples/gallery/proofs", "*.png", 4),
        "plugin screenshots": (root / "plugins/make-brand-assets-for-me/assets", "screenshot-*.png", 3),
    }
    for label, (folder, pattern, expected) in counts.items():
        actual = len(list(folder.glob(pattern))) if folder.exists() else 0
        if actual != expected:
            errors.append(f"Expected {expected} {label}, found {actual}")

    manifest_path = root / "plugins/make-brand-assets-for-me/.codex-plugin/plugin.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            if manifest.get("version") != (root / "VERSION").read_text().strip():
                errors.append("VERSION and plugin version do not match")
            if manifest.get("author", {}).get("name") != "Lemonbrand":
                errors.append("Codex plugin author must be Lemonbrand")
            if manifest.get("license") != "MIT":
                errors.append("Codex plugin license must be MIT")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"Bad plugin manifest: {error}")

    claude_manifest_path = root / "plugins/make-brand-assets-for-me/.claude-plugin/plugin.json"
    if claude_manifest_path.exists():
        try:
            manifest = json.loads(claude_manifest_path.read_text())
            if manifest.get("version") != (root / "VERSION").read_text().strip():
                errors.append("VERSION and Claude plugin version do not match")
            if manifest.get("author", {}).get("name") != "Lemonbrand":
                errors.append("Claude plugin author must be Lemonbrand")
            if manifest.get("license") != "MIT":
                errors.append("Claude plugin license must be MIT")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"Bad Claude plugin manifest: {error}")

    workflow_path = root / ".github/workflows/test.yml"
    if workflow_path.exists():
        workflow = workflow_path.read_text()
        if "cache: pip" in workflow and "cache-dependency-path:" not in workflow:
            errors.append("GitHub Actions pip cache must declare cache-dependency-path")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Check that the share package has every promised part.")
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check_package(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("PASS: the public package has six synchronized skills, two plugin adapters, ten baselines, four proofs, three screenshots, and its required files.")


if __name__ == "__main__":
    main()

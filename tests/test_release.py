import importlib.util
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_private_scan_flags_a_bad_file(tmp_path):
    checker = load_script("check_for_private_stuff")
    bad = tmp_path / "notes.md"
    bad.write_text("Secret reference: " + "drive." + "google.com/example")
    findings = checker.scan(tmp_path)
    assert findings
    assert findings[0]["file"] == "notes.md"


def test_package_checker_accepts_the_repo():
    checker = load_script("check_package")
    assert checker.check_package(ROOT) == []


def test_release_zip_is_clean_and_complete():
    subprocess.run([sys.executable, str(ROOT / "scripts/build_release.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    archive = ROOT / "release/make-brand-assets-for-me-0.1.0.zip"
    manifest = ROOT / "release/manifest.json"
    assert archive.exists()
    assert manifest.exists()
    data = json.loads(manifest.read_text())
    first_manifest = manifest.read_text()
    first_digest = data["sha256"]
    readme = ROOT / "README.md"
    original_times = (readme.stat().st_atime_ns, readme.stat().st_mtime_ns)
    try:
        os.utime(readme, ns=(original_times[0], original_times[1] + 10_000_000_000))
        subprocess.run([sys.executable, str(ROOT / "scripts/build_release.py")], cwd=ROOT, check=True, capture_output=True, text=True)
        assert manifest.read_text() == first_manifest
        assert json.loads(manifest.read_text())["sha256"] == first_digest
    finally:
        os.utime(readme, ns=original_times)
    assert data["version"] == "0.1.0"
    assert data["sha256"]
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        assert "make-brand-assets-for-me/README.md" in names
        assert "make-brand-assets-for-me/plugins/make-brand-assets-for-me/.codex-plugin/plugin.json" in names
        assert "make-brand-assets-for-me/plugins/make-brand-assets-for-me/.claude-plugin/plugin.json" in names
        assert "make-brand-assets-for-me/.claude-plugin/marketplace.json" in names
        assert "make-brand-assets-for-me/skills/brand-assets-set-up/SKILL.md" in names
        assert "make-brand-assets-for-me/distribution/openai/test-cases.json" in names
        assert not any("__pycache__" in name or name.endswith(".pyc") for name in names)
        assert not any(name.startswith("make-brand-assets-for-me/release/") for name in names)

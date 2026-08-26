import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "plugins" / "make-brand-assets-for-me"


def test_plugin_and_skills_exist():
    manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "make-brand-assets-for-me"
    assert manifest["version"] == "0.1.0"

    expected = {
        "brand-assets-set-up",
        "brand-assets-make-one",
        "brand-assets-make-scene",
        "brand-assets-make-set",
        "brand-assets-make-move",
    }
    actual = {
        path.name
        for path in (PLUGIN / "skills").iterdir()
        if (path / "SKILL.md").exists()
    }
    assert actual == expected


def test_marketplace_points_to_plugin():
    marketplace = json.loads(
        (ROOT / ".agents/plugins/marketplace.json").read_text()
    )
    entry = marketplace["plugins"][0]
    assert entry["name"] == "make-brand-assets-for-me"
    assert entry["source"]["path"] == "./plugins/make-brand-assets-for-me"


def test_each_skill_has_plain_ui_metadata():
    for skill in (PLUGIN / "skills").iterdir():
        if not (skill / "SKILL.md").exists():
            continue
        metadata = (skill / "agents/openai.yaml").read_text()
        assert "display_name:" in metadata
        assert "short_description:" in metadata
        assert f"${skill.name}" in metadata

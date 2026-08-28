import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "plugins" / "make-brand-assets-for-me"


def test_plugin_and_skills_exist():
    manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "make-brand-assets-for-me"
    assert manifest["version"] == "0.2.3"

    expected = {
        "brand-assets-set-up",
        "brand-assets-make-one",
        "brand-assets-make-scene",
        "brand-assets-make-set",
        "brand-assets-make-move",
        "brand-assets-make-launch-pack",
    }
    actual = {
        path.name
        for path in (PLUGIN / "skills").iterdir()
        if (path / "SKILL.md").exists()
    }
    assert actual == expected


def test_launch_pack_skill_has_complete_entrypoint():
    skill = PLUGIN / "skills" / "brand-assets-make-launch-pack"
    required = {
        "SKILL.md",
        "agents/openai.yaml",
        "references/ask-the-user.md",
        "references/check-the-launch-pack.md",
        "references/five-steps.md",
        "references/channel-placements.json",
    }
    actual = {
        str(path.relative_to(skill))
        for path in skill.rglob("*")
        if path.is_file()
    } if skill.exists() else set()
    assert required <= actual


def test_launch_pack_skill_teaches_the_image_first_asset_contract():
    skill = (
        PLUGIN / "skills/brand-assets-make-launch-pack/SKILL.md"
    ).read_text().lower()
    review = (
        PLUGIN / "skills/brand-assets-make-launch-pack/references/check-the-launch-pack.md"
    ).read_text().lower()

    assert "background first" in skill
    assert "protected negative space" in skill
    assert "fewer than 15 words" in skill
    assert "no text" in skill and "generated background" in skill
    assert "overlay_word_count" in review


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

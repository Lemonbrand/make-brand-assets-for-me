import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "make-brand-assets-for-me"
CANONICAL_SKILLS = PLUGIN / "skills"
PUBLIC_SKILLS = ROOT / "skills"
EXPECTED_SKILLS = {
    "brand-assets-start-here",
    "brand-assets-set-up",
    "brand-assets-make-one",
    "brand-assets-make-scene",
    "brand-assets-make-set",
    "brand-assets-make-move",
    "brand-assets-make-launch-pack",
}
REPOSITORY = "https://github.com/Lemonbrand/make-brand-assets-for-me"
GITHUB_OFFER = (
    "https://lemonbrand.io/inbox-audit?utm_source=github"
    "&utm_medium=referral&utm_campaign=make_brand_assets_for_me"
)


def load_script(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree_digests(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_public_owner_and_license():
    codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    claude = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text())
    assert codex["author"]["name"] == "Lemonbrand"
    assert claude["author"]["name"] == "Lemonbrand"
    assert codex["license"] == claude["license"] == "MIT"
    assert codex["repository"] == claude["repository"] == REPOSITORY
    assert (ROOT / "LICENSE.md").read_text().startswith("# MIT License")


def test_codex_metadata_leads_with_the_first_run_and_shows_real_proof():
    codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    interface = codex["interface"]
    assert codex["homepage"] == "https://lemonbrand.io/resources/make-brand-assets-for-me"
    assert interface["websiteURL"] == "https://lemonbrand.io/resources/make-brand-assets-for-me"
    assert interface["defaultPrompt"][0] == "Help me make my first brand asset."
    assert len(interface["defaultPrompt"]) == 3
    assert interface["screenshots"] == [
        "./assets/screenshot-setup.png",
        "./assets/screenshot-styles.png",
        "./assets/screenshot-set.png",
    ]
    for relative in interface["screenshots"]:
        assert (PLUGIN / relative).exists()


def test_codex_and_claude_marketplaces_point_to_one_plugin():
    codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert codex["name"] == "lemonbrand"
    assert claude["name"] == "lemonbrand"
    assert claude["owner"]["name"] == "Lemonbrand"
    assert claude["plugins"][0]["source"] == "./plugins/make-brand-assets-for-me"
    assert codex["plugins"][0]["source"]["path"] == "./plugins/make-brand-assets-for-me"


def test_agent_skills_copy_matches_plugin():
    assert {path.name for path in PUBLIC_SKILLS.iterdir() if path.is_dir()} == EXPECTED_SKILLS
    assert tree_digests(PUBLIC_SKILLS) == tree_digests(CANONICAL_SKILLS)
    sync = load_script("sync_distribution_skills")
    assert sync.sync_skills(ROOT, check_only=True) == []


def test_copy_bearing_skills_name_the_portable_compositor():
    for name in {
        "brand-assets-make-scene",
        "brand-assets-make-launch-pack",
    }:
        text = (CANONICAL_SKILLS / name / "SKILL.md").read_text()
        assert "scripts/compose_text_overlay.py" in text, name
        assert "scripts/check_background_fit.py" in text, name
        assert "text-free background" in text.lower(), name


def test_readme_has_every_install_path_and_offer():
    text = (ROOT / "README.md").read_text()
    assert "# Make Brand Assets For Me" in text
    assert "Lemonbrand/make-brand-assets-for-me" in text
    assert "npx skills add Lemonbrand/make-brand-assets-for-me" in text
    assert "/plugin marketplace add Lemonbrand/make-brand-assets-for-me" in text
    assert text.index("### ChatGPT") < text.index("### Claude Desktop")
    assert "Best experience" in text
    assert "Customize → Plugins" in text
    assert "Claude Code (terminal)" in text
    assert "start a new task" in text.lower()
    assert GITHUB_OFFER in text


def test_openai_submission_cases_are_complete():
    data = json.loads((ROOT / "distribution/openai/test-cases.json").read_text())
    assert len(data["positive"]) == 7
    assert len(data["negative"]) == 3
    assert len(data["starter_prompts"]) == 3
    assert {item["expected_skill"] for item in data["positive"]} == EXPECTED_SKILLS
    assert all(item["expected_result"] == "do_not_trigger" for item in data["negative"])


def test_start_here_docs_are_action_first_and_platform_specific():
    start = (ROOT / "docs/start-here.md").read_text()
    claude = (ROOT / "distribution/claude/listing.md").read_text()
    openai = (ROOT / "distribution/openai/listing.md").read_text()
    assert "Help me make my first brand asset." in start
    assert "ChatGPT" in start and "Best experience" in start
    assert "Claude Desktop" in start and "Customize → Plugins" in start
    assert "Claude Code (terminal)" in start
    assert "Start Making Brand Assets" in openai
    assert "Claude Desktop" in claude and "Add from a repository" in claude
    assert "Claude Code (terminal)" in claude


def test_distribution_kit_is_ready_to_copy():
    expected = [
        "distribution/openai/listing.md",
        "distribution/openai/submission-checklist.md",
        "distribution/claude/listing.md",
        "distribution/claude/submission-checklist.md",
        "distribution/skills-sh/README.md",
        "distribution/github/repository-settings.md",
        "distribution/github/release-notes.md",
        "distribution/launch/launch-copy.md",
        "distribution/launch/tracked-links.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "TRADEMARKS.md",
        "requirements-dev.txt",
        ".github/workflows/test.yml",
    ]
    for relative in expected:
        path = ROOT / relative
        assert path.exists(), relative
        assert path.read_text().strip(), relative

    launch = (ROOT / "distribution/launch/launch-copy.md").read_text()
    assert "LinkedIn" in launch
    assert "Product Hunt" in launch
    assert "Community" in launch


def test_lemonbrand_attribution_is_not_inside_skill_output_rules():
    for path in CANONICAL_SKILLS.rglob("*.md"):
        assert "lemonbrand.io/inbox-audit" not in path.read_text().lower()

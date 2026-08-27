import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
EXPECTED_SKILLS = {
    "brand-assets-set-up",
    "brand-assets-make-one",
    "brand-assets-make-scene",
    "brand-assets-make-set",
    "brand-assets-make-move",
    "brand-assets-make-launch-pack",
}


def test_docs_use_plain_product_name():
    readme = (ROOT / "README.md").read_text()
    assert readme.startswith("# Make Brand Assets For Me")
    assert "SHOW → PLAN → MAKE → CHECK → SAVE" in readme
    assert "docs/start-here.md" in readme


def test_every_skill_has_five_routing_cases():
    cases = json.loads((ROOT / "tests/routing/cases.json").read_text())
    assert {item["skill"] for item in cases} == EXPECTED_SKILLS
    assert all(len(item["cases"]) == 5 for item in cases)
    assert all("should_ask" in case for item in cases for case in item["cases"])


def test_three_fictional_brand_recipes_exist():
    recipes = list((ROOT / "examples/brand-rules").glob("*.yaml"))
    assert {path.stem for path in recipes} == {"cut-paper", "soft-clay", "bold-print"}


def test_required_docs_exist():
    expected = {
        "start-here.md",
        "set-up-your-brand.md",
        "choose-a-skill.md",
        "check-your-work.md",
        "change-it-for-a-new-brand.md",
        "run-the-tests.md",
        "make-a-release.md",
        "what-you-own-and-what-you-share.md",
        "how-to-sell-it.md",
        "free-vs-paid.md",
    }
    actual = {path.name for path in (ROOT / "docs").glob("*.md")}
    assert expected <= actual

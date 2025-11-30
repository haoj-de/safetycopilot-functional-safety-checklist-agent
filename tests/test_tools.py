import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from mini_standard import mini_standard
from tools import (
    standard_lookup_tool,
    risk_estimator_tool,
    checklist_formatter_tool,
)


def test_mini_standard_keys():
    """Basic sanity check: mini_standard defines expected profiles."""
    keys = set(mini_standard.keys())
    assert "iso26262" in keys
    assert "generic_safety" in keys


def test_mini_standard_entry_shape():
    """Each entry should have the expected fields."""
    for profile in mini_standard.values():
        for entry in profile:
            assert "id" in entry
            assert "phase" in entry
            assert "topic" in entry
            assert "priority" in entry
            assert "summary" in entry


def test_standard_lookup_tool_iso26262_concept():
    """Lookup for iso26262 / concept should include HARA and safety goals."""
    concept_items = standard_lookup_tool("iso26262", "concept")
    topics = {item["topic"] for item in concept_items}
    assert "HARA" in topics
    assert "safety_goals" in topics


def test_risk_estimator_tool_high_risk():
    """Systems mentioning braking and high-voltage should be classified as high risk."""
    desc = (
        "An automotive brake control ECU that manages hydraulic braking "
        "for a high-voltage electric powertrain."
    )
    risk = risk_estimator_tool(desc)
    assert risk == "high"


def test_risk_estimator_tool_low_risk():
    """Non-safety-critical descriptions should be classified as low risk."""
    desc = "A mobile app for tracking daily steps and showing basic statistics."
    risk = risk_estimator_tool(desc)
    assert risk == "low"


def test_checklist_formatter_tool_groups_by_phase():
    """Checklist formatter should group tasks by phase and render Markdown checkboxes."""
    tasks = [
        {"phase": "concept", "description": "Perform hazard analysis and risk assessment"},
        {"phase": "concept", "description": "Define safety goals"},
        {"phase": "verification", "description": "Create a verification plan"},
    ]
    grouped = checklist_formatter_tool(tasks)

    assert "concept" in grouped
    assert "verification" in grouped

    # Concept phase should have 2 items
    assert len(grouped["concept"]) == 2

    # Each item should start with "- [ ] "
    for _, items in grouped.items():
        for line in items:
            assert line.startswith("- [ ] ")

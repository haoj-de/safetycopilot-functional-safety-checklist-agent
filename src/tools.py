"""
Tools for SafetyCopilot.

- standard_lookup_tool:    look up entries in the mini-standard by standard + phase
- risk_estimator_tool:     very simple keyword-based risk estimation (low/medium/high)
- checklist_formatter_tool:group tasks by phase and render Markdown checklists
"""

from typing import Dict, List, Any

from mini_standard import mini_standard


def standard_lookup_tool(standard: str, phase: str) -> List[Dict[str, Any]]:
    """
    Look up mini-standard entries for a given standard and phase.

    Args:
        standard: Name of the standard profile, e.g. "iso26262" or "generic_safety".
        phase:    Development phase, e.g. "concept", "design", "implementation",
                  "verification", "safety_case".

    Returns:
        A list of entries (dict) matching the requested phase.
    """
    items = mini_standard.get(standard, [])
    return [item for item in items if item["phase"] == phase]


def risk_estimator_tool(system_description: str) -> str:
    """
    Very simple, non-normative risk estimation based on keywords.

    This is purely for demo purposes and should NOT be used as a real
    hazard or risk analysis. It returns one of: "low", "medium", "high".
    """
    text = system_description.lower()
    score = 0

    high_risk_keywords = [
        "brake",
        "braking",
        "steering",
        "train",
        "railway",
        "high-voltage",
        "high voltage",
        "battery",
        "bms",
        "powertrain",
        "airbag",
        "collision avoidance",
    ]

    medium_risk_keywords = [
        "monitor",
        "monitoring",
        "diagnostic",
        "diagnostics",
        "emergency",
        "fail-safe",
        "failsafe",
        "stability control",
        "safety monitoring",
    ]

    for kw in high_risk_keywords:
        if kw in text:
            score += 2

    for kw in medium_risk_keywords:
        if kw in text:
            score += 1

    if score >= 3:
        return "high"
    elif score >= 1:
        return "medium"
    else:
        return "low"


def checklist_formatter_tool(tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Group generated tasks by phase to create a Markdown checklist.

    Each task is expected to have at least:
      - "phase":       phase name (e.g. "concept", "design", "verification", ...)
      - "description": short imperative description for the checklist item

    Returns:
        A dict: phase -> list of Markdown checkbox strings.
    """
    grouped: Dict[str, List[str]] = {}

    for t in tasks:
        phase = t.get("phase", "general")
        desc = t.get("description", "").strip()
        if not desc:
            continue  # skip empty descriptions

        grouped.setdefault(phase, []).append(f"- [ ] {desc}")

    return grouped

"""
Evaluation helpers for SafetyCopilot.

This module provides:

- run_pipeline_get_text: run the Planner + Checker pipeline for a single system
                         and return the final CheckerAgent text.
- evaluate_systems:      run the pipeline over a list of systems and compute
                         simple coverage metrics.
"""

from typing import Dict, List, Any

import pandas as pd
from google.genai import types

from agents import (
    planner_runner,
    checker_runner,
    USER_ID,
    SESSION_ID_PLANNER,
    SESSION_ID_CHECKER,
)
from tools import risk_estimator_tool


async def run_pipeline_get_text(
    system: Dict[str, Any],
    standard: str = "iso26262",
) -> str:
    """
    Run the full Planner + Checker pipeline for evaluation and return
    the final text produced by the CheckerAgent.

    This function:
      1. Calls the PlannerAgent via its Runner to generate an initial plan.
      2. Calls the CheckerAgent via its Runner to review and refine the plan.
      3. Returns the CheckerAgent's final text output.
    """
    if planner_runner is None or checker_runner is None:
        raise RuntimeError("Agents (Planner/Checker) are not initialized.")

    description = system["description"]
    domain = system["domain"]
    risk_level = risk_estimator_tool(description)

    # ---- 1) Call PlannerAgent to get an initial plan/checklist ----
    planner_input = (
        f"System description:\n{description}\n\n"
        f"Domain: {domain}\n"
        f"Target standard: {standard}\n"
        f"Risk level (pre-estimated): {risk_level}\n\n"
        "Your task:\n"
        "1. Propose a safety and compliance work plan for this system, "
        "grouped by phase.\n"
        "2. Mention key concepts such as HARA / risk assessment, safety goals,\n"
        "   safety requirements, verification / test plan, and safety case "
        "where appropriate.\n"
        "3. Keep the answer concise (ideally under 200 words).\n"
    )

    planner_content = types.Content(
        role="user",
        parts=[types.Part(text=planner_input)],
    )

    planner_text = ""
    async for event in planner_runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID_PLANNER,
        new_message=planner_content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            planner_text = event.content.parts[0].text

    # ---- 2) Call CheckerAgent to refine / complete the checklist ----
    checker_input = (
        f"System description:\n{description}\n\n"
        f"Domain: {domain}\n"
        f"Target standard: {standard}\n"
        f"Risk level: {risk_level}\n\n"
        "Current checklist or plan from the PlannerAgent:\n"
        f"\"\"\"{planner_text}\"\"\"\n\n"
        "Your task:\n"
        "1. Check whether the checklist includes at least the following "
        "critical concepts for medium and high risk systems: HARA / "
        "risk assessment, safety goals, verification or test plan, and "
        "safety case or safety documentation.\n"
        "2. If something is missing, add additional checklist items to fill "
        "the gaps.\n"
        "3. Return an updated grouped checklist plus a short textual review "
        "(2–4 bullet points).\n"
        "4. Keep the whole answer concise (ideally under 200 words).\n"
    )

    checker_content = types.Content(
        role="user",
        parts=[types.Part(text=checker_input)],
    )

    checker_text = ""
    async for event in checker_runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID_CHECKER,
        new_message=checker_content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            checker_text = event.content.parts[0].text

    return checker_text


async def evaluate_systems(
    systems: List[Dict[str, Any]],
    standard: str = "iso26262",
) -> pd.DataFrame:
    """
    Evaluate the combined Planner + Checker pipeline on a small set of example
    systems by checking how many expected key concepts appear in the final text.

    Args:
        systems:  A list of system dicts with keys including:
                  - "id", "name", "domain", "description",
                    "expected_must_have" (list of keywords)
        standard: Standard profile name, e.g. "iso26262".

    Returns:
        A pandas DataFrame with one row per system, including a coverage
        percentage over expected key topics.
    """
    rows: List[Dict[str, Any]] = []

    for s in systems:
        final_text = await run_pipeline_get_text(s, standard=standard)
        text_lower = final_text.lower()

        expected = s["expected_must_have"]
        covered = 0

        for kw in expected:
            # Allow some flexibility in matching; e.g., "HARA" or "hazard analysis"
            key = kw.lower()
            if key == "hara":
                match = ("hara" in text_lower) or ("hazard analysis" in text_lower)
            elif key == "verification_plan":
                match = (
                    ("verification" in text_lower and "plan" in text_lower)
                    or ("test plan" in text_lower)
                )
            else:
                match = key.replace("_", " ") in text_lower

            if match:
                covered += 1

        coverage_ratio = covered / max(1, len(expected))

        rows.append(
            {
                "id": s["id"],
                "name": s["name"],
                "domain": s["domain"],
                "risk": risk_estimator_tool(s["description"]),
                "expected_topics": len(expected),
                "covered_topics": covered,
                "coverage_ratio": coverage_ratio,
            }
        )

    df = pd.DataFrame(rows)

    # Add a coverage percentage column and reorder columns for readability
    df["coverage_%"] = (df["coverage_ratio"] * 100).round(1)
    df = df[
        [
            "id",
            "name",
            "domain",
            "risk",
            "expected_topics",
            "covered_topics",
            "coverage_%",
        ]
    ]

    return df

"""
Mini-standard definitions for SafetyCopilot.

This file contains a small, paraphrased "mini-standard" knowledge base
inspired by functional safety standards such as ISO 26262 and IEC 61508.

Non-normative:
- These entries are NOT official standard text.
- They are simplified, educational summaries to drive the agent demo.
"""

from typing import Dict, List, Any

# A mapping from standard name -> list of activity entries.
# Each entry has:
# - id:        internal identifier
# - phase:     concept / design / implementation / verification / safety_case
# - topic:     short topic label (e.g. HARA, safety_goals, verification_plan)
# - priority:  "low" / "medium" / "high"
# - summary:   short paraphrased description of the activity
mini_standard: Dict[str, List[Dict[str, Any]]] = {
    "iso26262": [
        # Concept phase
        {
            "id": "iso26262-concept-hara",
            "phase": "concept",
            "topic": "HARA",
            "priority": "high",
            "summary": (
                "Perform a hazard analysis and risk assessment for the system, "
                "identifying potential hazards and their risk levels."
            ),
        },
        {
            "id": "iso26262-concept-safety-goals",
            "phase": "concept",
            "topic": "safety_goals",
            "priority": "high",
            "summary": (
                "Define safety goals that mitigate the most critical hazards "
                "and document their rationale."
            ),
        },

        # Design / development
        {
            "id": "iso26262-design-reqs",
            "phase": "design",
            "topic": "safety_requirements",
            "priority": "high",
            "summary": (
                "Derive and allocate safety requirements to system, hardware, "
                "and software elements."
            ),
        },
        {
            "id": "iso26262-design-traceability",
            "phase": "design",
            "topic": "traceability",
            "priority": "medium",
            "summary": (
                "Ensure traceability from safety goals to technical safety "
                "requirements and design elements."
            ),
        },

        # Implementation
        {
            "id": "iso26262-impl-sw-implementation",
            "phase": "implementation",
            "topic": "sw_implementation",
            "priority": "medium",
            "summary": (
                "Implement software in accordance with coding guidelines, "
                "defensive programming, and safety mechanisms."
            ),
        },

        # Verification & validation
        {
            "id": "iso262262-verif-test-plan",
            "phase": "verification",
            "topic": "verification_plan",
            "priority": "high",
            "summary": (
                "Plan verification and validation activities, including unit, "
                "integration, and system-level tests to show that safety "
                "requirements are met."
            ),
        },
        {
            "id": "iso26262-verif-independent-review",
            "phase": "verification",
            "topic": "independent_review",
            "priority": "medium",
            "summary": (
                "Schedule independent reviews or assessments for key safety "
                "work products."
            ),
        },

        # Safety case & documentation
        {
            "id": "iso26262-safety-case",
            "phase": "safety_case",
            "topic": "safety_case",
            "priority": "high",
            "summary": (
                "Plan and maintain a safety case that collects evidence and "
                "arguments for releasing the system."
            ),
        },
        {
            "id": "iso26262-safety-manual",
            "phase": "safety_case",
            "topic": "safety_manual",
            "priority": "medium",
            "summary": (
                "Prepare safety manuals or usage guidelines for integrators "
                "and downstream users."
            ),
        },
    ],

    "generic_safety": [
        {
            "id": "generic-risk-assessment",
            "phase": "concept",
            "topic": "risk_assessment",
            "priority": "high",
            "summary": (
                "Identify hazards, estimate risks, and decide which risks "
                "require mitigation."
            ),
        },
        {
            "id": "generic-controls",
            "phase": "design",
            "topic": "controls",
            "priority": "medium",
            "summary": (
                "Design technical and organizational controls to reduce "
                "or monitor risks."
            ),
        },
        {
            "id": "generic-test",
            "phase": "verification",
            "topic": "testing",
            "priority": "medium",
            "summary": (
                "Plan and execute tests or other verification activities to "
                "check that controls work as intended."
            ),
        },
        {
            "id": "generic-documentation",
            "phase": "safety_case",
            "topic": "documentation",
            "priority": "medium",
            "summary": (
                "Document assumptions, limitations, and residual risks "
                "for stakeholders."
            ),
        },
    ],
}


if __name__ == "__main__":
    # Quick sanity check: which standards are defined?
    print("Defined standards:", list(mini_standard.keys()))

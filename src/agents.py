"""
Agent construction and session setup for SafetyCopilot.

This module defines:

- PLANNER_INSTRUCTION, CHECKER_INSTRUCTION
- planner_agent, checker_agent
- APP_NAME, USER_ID, SESSION_ID_PLANNER, SESSION_ID_CHECKER
- session_service
- planner_runner, checker_runner
- setup_sessions_and_runners()  -> async function to initialize runners

Usage from a notebook:

    import sys
    sys.path.append("src")

    from agents import (
        planner_agent,
        checker_agent,
        planner_runner,
        checker_runner,
        setup_sessions_and_runners,
        APP_NAME,
        USER_ID,
        SESSION_ID_PLANNER,
        SESSION_ID_CHECKER,
    )

    await setup_sessions_and_runners()
    print("Runners ready ✅")
"""

from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from tools import standard_lookup_tool, checklist_formatter_tool


# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------

MODEL_ID = "gemini-2.0-flash"

if MODEL_ID is None:
    print(
        "ADK MODEL_ID is not set. "
        "Please ensure MODEL_ID and imports are configured."
    )
else:
    print("Using model:", MODEL_ID)


# ---------------------------------------------------------------------------
# Agent instructions
# ---------------------------------------------------------------------------

PLANNER_INSTRUCTION = """
You are SafetyCopilot, a Functional Safety Planning Agent.

Given:
- A short system description
- A target standard (e.g., iso26262, generic_safety)
- A risk level (low, medium, high)

Your job:

1. For each development phase (concept, design, implementation, verification, safety_case),
   call the `standard_lookup_tool` to retrieve relevant guideline snippets
   from the mini-standard.

2. Based on the snippets and the risk level, propose concrete, actionable
   checklist items. Each item should have:
   - phase
   - topic
   - description (short, imperative, e.g. "Define safety goals for braking hazards")

3. Use `checklist_formatter_tool(tasks)` as your final tool call to group the
   items by phase into Markdown-style checklists with checkboxes
   (always use "- [ ] ..." for each task).

4. In your final response to the user, return a readable Markdown document:
   - Start with a short one-sentence summary of the safety work plan.
   - Then, for each phase that has tasks, add a level-3 heading, for example:
       "### Concept phase", "### Design phase", etc.
   - Under each heading, list the checklist items as Markdown checkboxes:
       "- [ ] Perform hazard analysis and risk assessment (HARA)"

Important constraints:
- Do NOT return JSON or Python objects in the final response.
- Do NOT expose internal tool calls.
- Be concise but clear, and avoid copying standard wording verbatim.
"""

CHECKER_INSTRUCTION = """
You are a Safety Checklist Reviewer Agent.

You receive:
- The system description
- The risk level
- A grouped checklist (Markdown-style lists grouped by phase) produced by another agent

Your job:

1. Check whether the checklist includes at least the following critical concepts
   for medium and high risk systems:
   - HARA or risk assessment
   - Safety goals
   - A verification or test plan
   - A safety case or similar documentation plan

2. If something is missing, add additional checklist items to fill the gaps.
   Use the same phase structure as the original checklist.

3. Improve the wording of vague items where needed, so that a functional safety
   engineer could implement them without confusion.

4. When producing the updated checklist, follow these rules:
   - Reuse all relevant checklist items from the original plan.
   - For items that come from the original plan, mark them as "[x] ...".
   - For NEW items that you add during the review, mark them as "- [ ] ...".
   - Keep the phase-based structure ("### Concept phase", "### Design phase", etc.).

5. Return a Markdown response with the following structure:

   ## Executive summary
   - 2–3 short bullet points summarizing the overall quality of the checklist.

   ## Gaps & risks
   - Bullet points describing important gaps, weaknesses, or risks you observed.

   ## Updated checklist
   - Phase-based headings (e.g. "### Concept phase", "### Design phase").
   - Under each phase, checklist items with:
       "- [x] ..." for reused items
       "- [ ] ..." for new items you added.

   ## Suggested improvements
   - 2–4 bullet points describing what you added or changed.
   - Mention any remaining assumptions or limitations.

Important constraints:
- Do NOT return JSON or Python objects.
- Do NOT expose internal thought processes or tool calls.
- Keep explanations concrete and practical for a functional safety engineer.
"""


# ---------------------------------------------------------------------------
# Agent instances
# ---------------------------------------------------------------------------

planner_agent: Optional[LlmAgent] = None
checker_agent: Optional[LlmAgent] = None

try:
    if MODEL_ID is not None:
        planner_agent = LlmAgent(
            model=MODEL_ID,
            name="planner_agent",
            instruction=PLANNER_INSTRUCTION,
            tools=[standard_lookup_tool, checklist_formatter_tool],
        )
        print("✅ planner_agent created.")

        checker_agent = LlmAgent(
            model=MODEL_ID,
            name="checker_agent",
            instruction=CHECKER_INSTRUCTION,
            tools=[],  # Checker relies only on the model
        )
        print("✅ checker_agent created.")
except Exception as e:
    print("Failed to create agents.")
    print(e)


# ---------------------------------------------------------------------------
# Sessions and runners
# ---------------------------------------------------------------------------

APP_NAME = "safety_copilot_app"
USER_ID = "demo_user"

SESSION_ID_PLANNER = "planner_session"
SESSION_ID_CHECKER = "checker_session"

session_service = InMemorySessionService()

planner_runner: Optional[Runner] = None
checker_runner: Optional[Runner] = None


async def setup_sessions_and_runners() -> None:
    """
    Create sessions for planner and checker and initialize Runner instances.

    This function must be awaited once (e.g. from a notebook) before you call
    planner_runner.run_async(...) or checker_runner.run_async(...).
    """
    global planner_runner, checker_runner

    # Create sessions
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID_PLANNER,
    )
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID_CHECKER,
    )

    # Create runners
    if planner_agent is not None:
        planner_runner = Runner(
            agent=planner_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

    if checker_agent is not None:
        checker_runner = Runner(
            agent=checker_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )


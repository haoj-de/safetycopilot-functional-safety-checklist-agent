# SafetyCopilot – Functional Safety Checklist Agent (Kaggle Agents Intensive)

SafetyCopilot is an **enterprise-style workflow assistant prototype** that turns short system descriptions into **phase-based functional safety and compliance checklists**.

The agent is built with **Google's Agent Development Kit (ADK)** as part of the *Kaggle x Google Agents Intensive* capstone project.  
It targets functional safety workflows **inspired by** standards such as ISO 26262 and IEC 61508 in domains like automotive and railway.

> ️ **Disclaimer:** SafetyCopilot is an experimental prototype for learning and exploration.  
> It is **not** a certified safety tool. Any generated checklist must be reviewed and adapted by qualified functional safety engineers before use in real projects.

---

## 1. Overview

In real projects, functional safety engineers spend a lot of time translating long, dense standards into **project-specific checklists**:

- Which activities are required for this system?
- Which phase should they belong to?
- What are the high-priority items we must not forget?

This process is repetitive, error-prone, and hard to keep consistent across teams.

SafetyCopilot explores whether **AI agents** can help by:

- Looking up summarized guideline snippets from a small **mini-standard** knowledge base  
- Generating **concrete, actionable checklist items** grouped by development phase  
- Reviewing and augmenting the checklist so that critical safety activities are not missing  
- Laying the groundwork for project-level refinement with sessions and memory

---

## 2. What this project does

Given:

- A short system description in natural language  
- A target standard label (e.g. `"iso26262"` or `"generic_safety"`)

SafetyCopilot:

1. Estimates a coarse risk level (`low / medium / high`) using a small Python helper.  
2. Uses a **mini-standard JSON** containing paraphrased safety activities, tagged by phase and topic.  
3. Runs a **PlannerAgent** to propose a phase-based checklist using ADK tools:
   - `standard_lookup_tool(standard, phase)`
   - `checklist_formatter_tool(tasks)`
4. Runs a **CheckerAgent** to:
   - Check for missing critical concepts (e.g. HARA, safety goals, verification plan, safety case)
   - Add missing checklist items
   - Return an **updated checklist** plus review notes

The final output is a human-readable Markdown checklist, for example:

- `### Concept phase`  
  - `- [ ] Perform hazard analysis and risk assessment (HARA)`  
  - `- [ ] Define safety goals for critical hazards`  
- `### Verification & validation`  
  - `- [ ] Create a verification / test plan for safety requirements`  

---

## 3. ADK concepts and architecture

This project demonstrates several core ADK concepts:

- **Tools**  
  - Custom ADK tools for:
    - Mini-standard lookup (`standard_lookup_tool`)
    - Checklist formatting (`checklist_formatter_tool`)
  - A small Python helper for coarse, keyword-based risk estimation

- **Agent architecture**  
  - A two-agent workflow:
    - **PlannerAgent** – generates an initial phase-based checklist from a system description  
    - **CheckerAgent** – reviews the checklist, fills gaps, and produces an updated version

- **Memory / sessions**  
  - `user_id` and `session_id` with `InMemorySessionService` and `Runner`  
  - Lays the groundwork for project-level memory and iterative refinement

- **Evaluation & observability**  
  - A small test set of example systems:
    - Automotive brake control ECU  
    - High-voltage battery management system  
    - Railway signaling subsystem  
  - A simple coverage metric over “must-have” topics:
    - HARA, safety goals, verification plan, safety case

## 4.Notebooks

The main end-to-end experiment and demo live in:

- `notebooks/safetycopilot-functional-safety-checklist-agent.ipynb`

Open this notebook to:

- Build the mini-standard knowledge base used by the agent  
- Define and sanity-check the core tools (`standard_lookup_tool`, `risk_estimator_tool`, `checklist_formatter_tool`)  
- Construct the PlannerAgent and CheckerAgent using Google's Agent Development Kit (ADK)  
- Run the Planner + Checker pipeline on example systems (brake ECU, BMS, railway signaling)  
- Visually inspect phase-based checklists rendered as Markdown with checkboxes  
- Compute simple coverage metrics over “must-have” safety topics (e.g. HARA, safety goals, verification plan, safety case)

---

## 5. Repository structure

```text
safetycopilot/
├─ notebooks/
│  └safetycopilot-functional-safety-checklist-agent.ipynb   # Original Kaggle notebook
├─ src/
│  ├─ mini_standard.py             # Mini-standard JSON definition
│  ├─ tools.py                     # standard_lookup_tool, checklist_formatter_tool
│  ├─ agents.py                    # PlannerAgent / CheckerAgent construction
│  └─ eval.py                      # Evaluation logic (coverage)
├─ requirements.txt
├─ README.md
└─ LICENSE

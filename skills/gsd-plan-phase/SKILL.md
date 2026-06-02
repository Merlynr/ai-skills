---
name: "gsd-plan-phase"
description: "Create detailed phase plan (PLAN.md) with verification loop"
tags: [planning, planning-phase, architecture, roadmap]
triggers:
  - 创建计划
  - 规划阶段
  - 写计划
  - plan phase
  - 阶段规划
tool_chain: [gsd-plan-phase, gsd-execute-phase]

metadata:
  short-description: "Create detailed phase plan (PLAN.md) with verification loop"
---

<codex_skill_adapter>
## A. Skill Invocation
  - This skill is invoked by mentioning `$gsd-plan-phase`.
  - Treat all user text after `$gsd-plan-phase` as `{{GSD_ARGS}}`.
  - If no arguments are present, treat `{{GSD_ARGS}}` as empty.

## B. AskUserQuestion → request_user_input Mapping
GSD workflows use `AskUserQuestion` (Claude Code syntax). Translate to Codex `request_user_input`:

Parameter mapping:
  - `header` → `header`
  - `question` → `question`
  - Options formatted as `"Label" — description` → `{label: "Label", description: "description"}`
  - Generate `id` from header: lowercase, replace spaces with underscores

Batched calls:
  - `AskUserQuestion([q1, q2])` → single `request_user_input` with multiple entries in `questions[]`

Multi-select workaround:
  - Codex has no `multiSelect`. Use sequential single-selects, or present a numbered freeform list asking the user to enter comma-separated numbers.

Execute mode fallback:
  - When `request_user_input` is rejected (Execute mode), present a plain-text numbered list and pick a reasonable default.

## C. Task() → spawn_agent Mapping
GSD workflows use `Task(...)` (Claude Code syntax). Translate to Codex collaboration tools:

Direct mapping:
  - `Task(subagent_type="X", prompt="Y")` → `spawn_agent(agent_type="X", message="Y")`
  - `Task(model="...")` → omit (Codex uses per-role config, not inline model selection)
  - `fork_context: false` by default — GSD agents load their own context via `<files_to_read>` blocks

Parallel fan-out:
  - Spawn multiple agents → collect agent IDs → `wait(ids)` for all to complete

Result parsing:
  - Look for structured markers in agent output: `CHECKPOINT`, `PLAN COMPLETE`, `SUMMARY`, etc.
  - `close_agent(id)` after collecting results from each agent
</codex_skill_adapter>

<objective>
Create executable phase prompts (PLAN.md files) for a roadmap phase with integrated research and verification.

**Default flow:** Research (if needed) → Plan → Verify → Done

**Orchestrator role:** Parse arguments, validate phase, research domain (unless skipped), spawn gsd-planner, verify with gsd-plan-checker, iterate until pass or max iterations, present results.
</objective>

<execution_context>
@$HOME/.codex/get-shit-done/workflows/plan-phase.md
@$HOME/.codex/get-shit-done/references/ui-brand.md
</execution_context>

<runtime_note>
**Copilot (VS Code):** Use `vscode_askquestions` wherever this workflow calls `AskUserQuestion`. They are equivalent — `vscode_askquestions` is the VS Code Copilot implementation of the same interactive question API. Do not skip questioning steps because `AskUserQuestion` appears unavailable; use `vscode_askquestions` instead.
</runtime_note>

<context>
Phase number: {{GSD_ARGS}} (optional — auto-detects next unplanned phase if omitted)

**Flags:**
  - `--research` — Force re-research even if RESEARCH.md exists
  - `--skip-research` — Skip research, go straight to planning
  - `--gaps` — Gap closure mode (reads VERIFICATION.md, skips research)
  - `--skip-verify` — Skip verification loop
  - `--prd <file>` — Use a PRD/acceptance criteria file instead of discuss-phase. Parses requirements into CONTEXT.md automatically. Skips discuss-phase entirely.
  - `--reviews` — Replan incorporating cross-AI review feedback from REVIEWS.md (produced by `/gsd-review`)
  - `--text` — Use plain-text numbered lists instead of TUI menus (required for `/rc` remote sessions)

Normalize phase input in step 2 before any directory lookups.
</context>

<process>
Execute the plan-phase workflow from @$HOME/.codex/get-shit-done/workflows/plan-phase.md end-to-end.
Preserve all workflow gates (validation, research, planning, verification loop, routing).
</process>

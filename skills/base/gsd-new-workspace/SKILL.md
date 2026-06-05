---
name: "gsd-new-workspace"
description: "Create an isolated workspace with repo copies and independent .planning/"
tags: [workspace-create, isolated-workspace]
triggers:
  - 新建工作区
  - 创建工作区
  - new workspace
tool_chain: [gsd-new-workspace]

metadata:
  short-description: "Create an isolated workspace with repo copies and independent .planning/"
---

<codex_skill_adapter>
## A. Skill Invocation
  - This skill is invoked by mentioning `$gsd-new-workspace`.
  - Treat all user text after `$gsd-new-workspace` as `{{GSD_ARGS}}`.
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

<context>
**Flags:**
  - `--name` (required) — Workspace name
  - `--repos` — Comma-separated repo paths or names. If omitted, interactive selection from child git repos in cwd
  - `--path` — Target directory. Defaults to `~/gsd-workspaces/<name>`
  - `--strategy` — `worktree` (default, lightweight) or `clone` (fully independent)
  - `--branch` — Branch to checkout. Defaults to `workspace/<name>`
  - `--auto` — Skip interactive questions, use defaults
</context>

<objective>
Create a physical workspace directory containing copies of specified git repos (as worktrees or clones) with an independent `.planning/` directory for isolated GSD sessions.

**Use cases:**
  - Multi-repo orchestration: work on a subset of repos in parallel with isolated GSD state
  - Feature branch isolation: create a worktree of the current repo with its own `.planning/`

**Creates:**
  - `<path>/WORKSPACE.md` — workspace manifest
  - `<path>/.planning/` — independent planning directory
  - `<path>/<repo>/` — git worktree or clone for each specified repo

**After this command:** `cd` into the workspace and run `/gsd-new-project` to initialize GSD.
</objective>

<execution_context>
@$HOME/.codex/get-shit-done/workflows/new-workspace.md
@$HOME/.codex/get-shit-done/references/ui-brand.md
</execution_context>

<process>
Execute the new-workspace workflow from @$HOME/.codex/get-shit-done/workflows/new-workspace.md end-to-end.
Preserve all workflow gates (validation, approvals, commits, routing).
</process>

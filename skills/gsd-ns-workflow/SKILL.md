---
name: gsd-ns-workflow
description: "workflow | discuss plan execute verify phase progress"
tags: [gsd-workflow, phase-progress, workflow-commands]
triggers:
  - ns workflow
  - gsd ns workflow
  - GSD 工作流命令
tool_chain: [gsd-ns-workflow]
allowed-tools:
  - Read
  - Skill
---


Route to the appropriate phase-pipeline skill based on the user's intent.

**Before GSD phases**: if requirements or acceptance are unclear and the task is not trivial (S级),
read `merlynr-dev-stack` → Phase 0 / [grill-lite.md](../merlynr-dev-stack/grill-lite.md) (M ≤3 rounds, L ≤12).

Sub-skill names below are post-#2790 consolidated targets — `gsd-phase`
absorbs the former add/insert/remove/edit-phase commands and `gsd-progress`
absorbs the former next/do commands.

| User wants | Invoke |
|---|---|
| Gather context before planning | gsd-discuss-phase |
| Clarify what a phase delivers | gsd-spec-phase |
| Create a PLAN.md | gsd-plan-phase |
| Execute plans in a phase | gsd-execute-phase |
| Verify built features through UAT | gsd-verify-work |
| Add / insert / remove / edit a phase | gsd-phase |
| Advance to the next logical step | gsd-progress |
| Offload planning to the ultraplan cloud | gsd-ultraplan-phase |
| Cross-AI plan review convergence loop | gsd-plan-review-convergence |

Invoke the matched skill directly using the Skill tool.

If the sub-skill is not available in the current tool (facade targets: cursor, agents, …), Read the SSOT base layer instead:

`{SKILLSHARE_SKILLS or ~/.config/skillshare/skills}/base/{skill-name}/SKILL.md`

Then follow that file; runtime workflows still load from the platform GSD install (e.g. `~/.codex/get-shit-done/`).

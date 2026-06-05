---
name: gsd-explore
description: "Socratic ideation and idea routing — think through ideas before committing to plans"
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
tags: [socratic-ideation, brainstorm, idea-routing]
triggers:
  - 探索
  - 创意
  - explore
  - 头脑风暴
tool_chain: [gsd-explore]

---

<objective>
Open-ended Socratic ideation session. Guides the developer through exploring an idea via
probing questions, optionally spawns research, then routes outputs to the appropriate GSD
artifacts (notes, todos, seeds, research questions, requirements, or new phases).

Accepts an optional topic argument: `/gsd-explore authentication strategy`
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/explore.md
</execution_context>

<process>
Execute end-to-end.
</process>

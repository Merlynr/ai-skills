---
name: gsd-ns-context
description: "codebase intelligence | map graphify docs learnings"
tags: [codebase-intelligence, context-map, 代码库]
triggers:
  - 上下文
  - 代码库情报
  - ns context
tool_chain: [gsd-ns-context]
allowed-tools:
  - Read
  - Skill
---


Route to the appropriate codebase-intelligence skill based on the user's intent.
`gsd-scan` and `gsd-intel` were folded into `gsd-map-codebase` flags by #2790.

| User wants | Invoke |
|---|---|
| Map the full codebase structure | gsd-map-codebase |
| Quick lightweight codebase scan | gsd-map-codebase --fast |
| Query mapped intelligence files | gsd-map-codebase --query |
| Generate a knowledge graph | gsd-graphify |
| Update project documentation | gsd-docs-update |
| Extract learnings from a completed phase | gsd-extract-learnings |

Invoke the matched skill directly using the Skill tool.

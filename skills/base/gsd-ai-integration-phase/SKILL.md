---
name: gsd-ai-integration-phase
description: "Generate an AI-SPEC.md design contract for phases that involve building AI systems."
tags: [ai-integration, llm-spec, eval-planning]
triggers:
  - AI 集成
  - AI 规格
  - ai integration
tool_chain: [gsd-ai-integration-phase]
argument-hint: "[phase number]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
  - WebFetch
  - WebSearch
  - AskUserQuestion
  - mcp__context7__*
---

<objective>
Create an AI design contract (AI-SPEC.md) for a phase involving AI system development.
Orchestrates gsd-framework-selector → gsd-ai-researcher → gsd-domain-researcher → gsd-eval-planner.
Flow: Select Framework → Research Docs → Research Domain → Design Eval Strategy → Done
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/ai-integration-phase.md
@$HOME/.claude/get-shit-done/references/ai-frameworks.md
@$HOME/.claude/get-shit-done/references/ai-evals.md
</execution_context>

<context>
Phase number: $ARGUMENTS — optional, auto-detects next unplanned phase if omitted.
</context>

<process>
Execute end-to-end.
Preserve all workflow gates.
</process>

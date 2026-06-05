#!/usr/bin/env python3
"""Refine GSD skill tags: remove generic 'utility', add domain-specific tags."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from _common import resolve_gsd_base_dir  # noqa: E402

GSD_BASE_DIR = resolve_gsd_base_dir()
METADATA_PY = SCRIPT_DIR / "add-gsd-metadata.py"

# Authoritative tag map (SSOT for tag refinement)
TAG_MAP: dict[str, list[str]] = {
    # === planning ===
    "gsd-discuss-phase": ["planning", "discussion", "requirements", "discuss"],
    "gsd-plan-phase": ["planning", "planning-phase", "architecture", "roadmap"],
    "gsd-research-phase": ["research", "investigation", "technical-research"],
    "gsd-list-phase-assumptions": ["planning", "assumptions", "risk-analysis"],
    "gsd-analyze-dependencies": ["planning", "dependencies", "dependency-graph"],
    "gsd-spec-phase": ["specification", "requirements", "ambiguity"],
    "gsd-mvp-phase": ["mvp", "vertical-slice", "user-story"],
    "gsd-plan-review-convergence": ["plan-review", "convergence", "cross-ai"],
    "gsd-ultraplan-phase": ["ultraplan", "cloud-planning", "planning"],
    # === execute ===
    "gsd-execute-phase": ["implementation", "execute-phase", "development", "coding"],
    "gsd-fast": ["fast-path", "trivial-task", "inline-execution"],
    "gsd-quick": ["quick-task", "small-scope", "guaranteed-execution"],
    "gsd-autonomous": ["autonomous", "batch-execution", "multi-phase"],
    # === review / verify ===
    "gsd-code-review": ["code-review", "quality-gate", "security-review"],
    "gsd-validate-phase": ["validation-gap", "test-coverage", "nyquist"],
    "gsd-verify-work": ["uat", "acceptance-testing", "conversational-verify"],
    "gsd-review": ["peer-review", "cross-ai-review", "external-review"],
    "gsd-audit-uat": ["uat-audit", "verification-audit"],
    "gsd-audit-milestone": ["milestone-audit", "completion-audit"],
    "gsd-eval-review": ["eval-audit", "ai-evaluation", "eval-coverage"],
    "gsd-audit-fix": ["audit-fix", "auto-remediation", "fix-pipeline"],
    "gsd-secure-phase": ["security-audit", "threat-model", "mitigation"],
    "gsd-add-tests": ["testing", "unit-test", "integration-test", "test-generation"],
    # === debug ===
    "gsd-debug": ["debugging", "troubleshooting", "root-cause"],
    "gsd-forensics": ["post-mortem", "workflow-forensics", "failure-analysis"],
    # === docs ===
    "gsd-docs-update": ["documentation", "docs-update", "doc-maintenance"],
    "gsd-ingest-docs": ["doc-ingest", "planning-bootstrap", "adr-import"],
    "gsd-milestone-summary": ["milestone-report", "onboarding-summary"],
    "gsd-session-report": ["session-report", "work-summary"],
    # === project ===
    "gsd-new-project": ["project-init", "bootstrap", "roadmap-create"],
    "gsd-new-milestone": ["milestone-start", "version-cycle"],
    "gsd-complete-milestone": ["milestone-archive", "milestone-complete"],
    "gsd-progress": ["progress-check", "status-report", "situational"],
    "gsd-stats": ["project-metrics", "statistics", "timeline"],
    "gsd-manager": ["command-center", "interactive-manager"],
    # === tasks / capture ===
    "gsd-add-todo": ["todo", "task-capture", "idea-capture"],
    "gsd-check-todos": ["todo-list", "task-triage"],
    "gsd-note": ["quick-note", "idea-capture", "note-taking"],
    "gsd-add-backlog": ["backlog", "parking-lot", "idea-staging"],
    "gsd-plant-seed": ["seed-idea", "future-trigger", "forward-looking"],
    "gsd-capture": ["capture", "ideation", "task-intake"],
    # === phase CRUD ===
    "gsd-add-phase": ["phase-add", "roadmap-edit"],
    "gsd-insert-phase": ["phase-insert", "urgent-phase", "decimal-phase"],
    "gsd-remove-phase": ["phase-remove", "roadmap-edit"],
    "gsd-phase": ["phase-crud", "roadmap-management"],
    "gsd-plan-milestone-gaps": ["milestone-gaps", "gap-closure"],
    # === workspace ===
    "gsd-new-workspace": ["workspace-create", "isolated-workspace"],
    "gsd-list-workspaces": ["workspace-list", "workspace-status"],
    "gsd-remove-workspace": ["workspace-remove", "worktree-cleanup"],
    "gsd-workspace": ["workspace-manage", "isolated-environment"],
    # === UI ===
    "gsd-ui-phase": ["ui-design", "frontend-spec", "ui-spec"],
    "gsd-ui-review": ["ui-audit", "visual-review", "design-review"],
    "gsd-sketch": ["ui-sketch", "mockup", "html-prototype"],
    # === tooling (formerly utility) ===
    "gsd-do": ["intent-routing", "auto-dispatch", "command-router"],
    "gsd-help": ["help", "command-reference", "usage-guide"],
    "gsd-health": ["planning-health", "integrity-check", "repair"],
    "gsd-map-codebase": ["codebase-map", "architecture-map", "代码库"],
    "gsd-update": ["gsd-update", "upgrade", "maintenance", "changelog"],
    "gsd-reapply-patches": ["patch-restore", "upgrade-recovery", "local-customization"],
    "gsd-settings": ["workflow-settings", "model-profile", "toggle-config"],
    "gsd-set-profile": ["model-profile", "quality-tier", "budget-profile"],
    "gsd-config": ["gsd-config", "workflow-config", "integration-config"],
    "gsd-ship": ["release", "pull-request", "merge-ready"],
    "gsd-pr-branch": ["pr-branch", "clean-history", "planning-filter"],
    "gsd-thread": ["persistent-thread", "cross-session", "context-thread"],
    "gsd-pause-work": ["handoff", "pause-session", "context-save"],
    "gsd-resume-work": ["handoff-restore", "resume-session", "context-restore"],
    "gsd-workstreams": ["parallel-workstream", "multi-track", "workstream-manage"],
    "gsd-profile-user": ["developer-profile", "behavior-analysis"],
    "gsd-cleanup": ["archive-phases", "milestone-cleanup", "housekeeping"],
    "gsd-review-backlog": ["backlog-grooming", "backlog-promotion"],
    "gsd-join-discord": ["community", "discord"],
    "gsd-next": ["workflow-advance", "next-step"],
    "gsd-graphify": ["knowledge-graph", "codebase-graph", "graph-query"],
    "gsd-explore": ["socratic-ideation", "brainstorm", "idea-routing"],
    "gsd-spike": ["technical-spike", "feasibility", "exploratory"],
    "gsd-extract-learnings": ["learnings", "retrospective", "decisions"],
    "gsd-import": ["external-plan-import", "conflict-detection"],
    "gsd-inbox": ["github-inbox", "issue-triage", "pr-triage"],
    # === team / AI ===
    "gsd-team": ["team-orchestration", "multi-agent", "collaboration"],
    "gsd-ai-integration-phase": ["ai-integration", "llm-spec", "eval-planning"],
    # === namespace skills ===
    "gsd-ns-context": ["codebase-intelligence", "context-map", "代码库"],
    "gsd-ns-ideate": ["ideation", "explore-capture", "sketch-spike"],
    "gsd-ns-manage": ["workspace-admin", "skillshare-manage", "inbox-manage"],
    "gsd-ns-project": ["project-lifecycle", "milestone-cycle"],
    "gsd-ns-review": ["quality-gate", "review-cluster"],
    "gsd-ns-workflow": ["gsd-workflow", "phase-progress", "workflow-commands"],
    # === misc ===
    "gsd-surface": ["skill-surface", "profile-toggle"],
    "gsd-undo": ["git-revert", "phase-rollback"],
    # === non-GSD ===
    "merlynr-dev-stack": ["merlynr", "workflow-stack", "evidence-routing", "development", "nmem"],
    "skillshare": ["skillshare", "skills-sync", "agent-sync", "skills-management"],
}


def tags_yaml_inline(tags: list[str]) -> str:
    return f"tags: [{', '.join(tags)}]"


def replace_tags_in_skill(skill_name: str, tags: list[str]) -> bool:
    skill_file = GSD_BASE_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        print(f"  skip {skill_name}: SKILL.md missing")
        return False

    content = skill_file.read_text(encoding="utf-8")
    new_line = tags_yaml_inline(tags)

    if re.search(r"^tags:\s*\[.*\]\s*$", content, re.MULTILINE):
        new_content = re.sub(
            r"^tags:\s*\[.*\]\s*$",
            new_line,
            content,
            count=1,
            flags=re.MULTILINE,
        )
    elif re.search(r"^tags:\s*\n", content, re.MULTILINE):
        new_content = re.sub(
            r"^tags:\s*\n(?:[ \t]+-\s+.+\n?)+",
            new_line + "\n",
            content,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        print(f"  skip {skill_name}: no tags block found")
        return False

    if new_content == content:
        print(f"  unchanged {skill_name}")
        return False

    skill_file.write_text(new_content, encoding="utf-8")
    print(f"  updated {skill_name}: {tags}")
    return True


def replace_tags_in_metadata_py() -> int:
    text = METADATA_PY.read_text(encoding="utf-8")
    updated = 0

    for skill_name, tags in TAG_MAP.items():
        if not skill_name.startswith("gsd-"):
            continue
        quoted = ", ".join(f'"{t}"' for t in tags)
        pattern = rf'("{re.escape(skill_name)}": \{{\s*"tags": )\[.*?\]'
        repl = rf"\1[{quoted}]"
        new_text, count = re.subn(pattern, repl, text, count=1, flags=re.DOTALL)
        if count:
            text = new_text
            updated += 1
        else:
            print(f"  warn: {skill_name} not found in add-gsd-metadata.py", file=sys.stderr)

    METADATA_PY.write_text(text, encoding="utf-8")
    return updated


def append_missing_metadata_entries() -> None:
    text = METADATA_PY.read_text(encoding="utf-8")
    if '"merlynr-dev-stack"' in text and '"skillshare"' in text:
        return

    extra = '''    "merlynr-dev-stack": {
        "tags": ["merlynr", "workflow-stack", "evidence-routing", "development", "nmem"],
        "triggers": ["merlynr", "Merlynr", "开发工作流", "dev stack", "工作流栈", "开始开发"],
        "tool_chain": ["gsd-do", "gsd-discuss-phase", "gsd-plan-phase", "gsd-execute-phase"],
    },
    "skillshare": {
        "tags": ["skillshare", "skills-sync", "agent-sync", "skills-management"],
        "triggers": ["skillshare", "skillshare sync", "同步 skill", "skills 管理"],
        "tool_chain": ["skillshare"],
    },
'''
    text = text.replace("\n}\n\n\ndef yaml_list", "\n" + extra + "}\n\n\ndef yaml_list")
    METADATA_PY.write_text(text, encoding="utf-8")


def main() -> int:
    print("Refining GSD skill tags...")
    skill_updates = sum(
        1 for name, tags in TAG_MAP.items() if replace_tags_in_skill(name, tags)
    )
    meta_updates = replace_tags_in_metadata_py()
    append_missing_metadata_entries()
    print(f"Done: {skill_updates} SKILL.md updated, {meta_updates} metadata entries patched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

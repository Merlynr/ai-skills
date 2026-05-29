#!/usr/bin/env python3
"""Collect candidate tasks for a daily plan from an Obsidian vault.

The script scans markdown files under the selected roots, extracts open
checkbox tasks, and tags them with lightweight metadata so a planner can
prioritize them into today's plan.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Iterator


DEFAULT_ROOTS = ("00 Inbox", "10 Daily", "20 Projects")
EXCLUDED_DIRS = {".obsidian", ".git", ".github", "99 Attachments"}
EXCLUDED_NOTE_TREES = {
    ("20 Projects", "Stock Prompt+report"),
    ("20 Projects", "龟龟策略"),
}
TASK_RE = re.compile(r"^\s*[-*]\s+\[(?P<state>[ xX])\]\s+(?P<text>.+?)\s*$")
HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<text>.+?)\s*$")
DATE_RE = re.compile(r"(?:📅\s*)?(?P<date>\d{4}-\d{2}-\d{2})")


@dataclass
class CandidateTask:
    file: str
    line: int
    source: str
    heading: str
    text: str
    due: str | None
    bucket: str
    lateness_days: int | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="Path to the note vault.")
    parser.add_argument(
        "--date",
        default=None,
        help="Target date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--roots",
        nargs="*",
        default=list(DEFAULT_ROOTS),
        help="Relative roots to scan inside the vault.",
    )
    return parser.parse_args()


def read_text_any(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gbk", "cp936"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def iter_markdown_files(vault: Path, roots: Iterable[str]) -> Iterator[Path]:
    seen: set[Path] = set()
    for root in roots:
        root_path = vault / root
        if not root_path.exists():
            continue
        for path in root_path.rglob("*.md"):
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            rel_parts = path.relative_to(vault).parts
            if any(rel_parts[: len(tree)] == tree for tree in EXCLUDED_NOTE_TREES):
                continue
            if path not in seen:
                seen.add(path)
                yield path


def classify_source(path: Path, vault: Path) -> str:
    rel = path.relative_to(vault).parts
    if not rel:
        return "other"
    first = rel[0]
    if first == "00 Inbox":
        return "inbox"
    if first == "10 Daily":
        return "daily"
    if first == "20 Projects":
        return "project"
    return "other"


def parse_target_date(value: str | None) -> date:
    if value:
        return datetime.strptime(value, "%Y-%m-%d").date()
    return date.today()


def parse_due(text: str) -> str | None:
    match = DATE_RE.search(text)
    if not match:
        return None
    return match.group("date")


def bucket_for(due: str | None, target: date) -> str:
    if not due:
        return "unscheduled"
    due_date = datetime.strptime(due, "%Y-%m-%d").date()
    if due_date < target:
        return "overdue"
    if due_date == target:
        return "today"
    return "upcoming"


def lateness_days_for(due: str | None, target: date) -> int | None:
    if not due:
        return None
    due_date = datetime.strptime(due, "%Y-%m-%d").date()
    delta = (target - due_date).days
    if delta <= 0:
        return None
    return delta


def collect_candidates(vault: Path, roots: Iterable[str], target: date) -> list[CandidateTask]:
    candidates: list[CandidateTask] = []
    for path in iter_markdown_files(vault, roots):
        text = read_text_any(path)
        in_code_block = False
        heading_stack: list[str] = []
        source = classify_source(path, vault)

        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            heading_match = HEADING_RE.match(line)
            if heading_match:
                level = len(heading_match.group("marks"))
                heading_stack = heading_stack[: max(level - 1, 0)]
                heading_stack.append(heading_match.group("text").strip())
                continue

            task_match = TASK_RE.match(line)
            if not task_match or task_match.group("state").lower() == "x":
                continue

            task_text = task_match.group("text").strip()
            due = parse_due(task_text)
            heading = " > ".join(heading_stack)
            lateness_days = lateness_days_for(due, target)
            candidates.append(
                CandidateTask(
                    file=str(path.relative_to(vault)).replace("\\", "/"),
                    line=line_no,
                    source=source,
                    heading=heading,
                    text=task_text,
                    due=due,
                    bucket=bucket_for(due, target),
                    lateness_days=lateness_days,
                )
            )

    bucket_rank = {
        "overdue": 0,
        "today": 1,
        "upcoming": 2,
        "unscheduled": 3,
    }
    candidates.sort(
        key=lambda item: (
            bucket_rank.get(item.bucket, 99),
            item.due or "9999-12-31",
            item.file,
            item.line,
        )
    )
    return candidates


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    vault = Path(args.vault).resolve()
    target_date = parse_target_date(args.date)
    candidates = collect_candidates(vault, args.roots, target_date)
    payload = {
        "vault": str(vault),
        "target_date": target_date.isoformat(),
        "count": len(candidates),
        "candidates": [asdict(candidate) for candidate in candidates],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

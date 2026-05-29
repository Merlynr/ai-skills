# Vault Structure

## Root Layout

- `00 Inbox/`: quick capture and open items.
- `10 Daily/`: dated daily plan notes, one file per day, usually `YYYY-MM-DD.md`.
- `20 Projects/`: project notes, plan documents, task boards, knowledge notes, and review material.
- `90 Templates/`: note templates used by Templater or quick-add flows.
- `99 Attachments/`: images, PDFs, and other binary assets.
- `Clippings/`: clipped source material.

## Important Entry Points

- `20 Projects/高软-系统架构师/任务看板.md`
- `20 Projects/高软-系统架构师/高软-系统架构师.md`
- `20 Projects/高软-系统架构师/00 计划/系统架构师冲刺计划-阶段一.md`
- `90 Templates/Daily.md`

## Task Conventions

- `- [ ]` means open.
- `- [x]` means complete.
- Date markers usually look like `📅 YYYY-MM-DD`.
- Dataview queries are plain `dataview` blocks, not DataviewJS.
- Keep the source note untouched when building a daily plan; mirror tasks into the plan file instead.

## Selection Heuristics

1. Build the note task pool first from `00 Inbox`, `10 Daily`, and `20 Projects`.
2. Build the user task pool second from the current request.
3. Merge only after each pool is ranked internally.
4. Tasks overdue before today come before tasks due today.
5. Unfinished tasks carried over from daily notes before today come before unscheduled tasks.
6. Prefer unfinished tasks from the most recent daily note first, then move back through older daily notes before project-plan carry-over.
7. Within one project plan, surface the oldest missed task before newer tasks from the same plan, even if the newer task is due today.
8. Daily-note leftovers are not capped at 3 items; project-plan carry-over is capped at 3 items.
9. Show only the top 3 project carry-over tasks on the daily page; keep the page focused.
10. Preserve user-specified ordering inside the user task pool.
11. Recover unchecked items from any daily note before today's `今日计划` and `Carry-over` before filling other carry-over slots.

## Output Shape

- Target file: `10 Daily/YYYY-MM-DD.md`
- Managed block markers:
  - `<!-- DAILY-PLAN:BEGIN -->`
  - `<!-- DAILY-PLAN:END -->`
- Recommended sections:
  - `## Focus`
  - `## 今日计划`
  - `## Carry-over`
  - `## Notes`
  - `## Review`
- Keep project carry-over to 3 items max, but do not cap daily-note leftovers.
- Final daily output should read as: note carry-over, note today tasks, then user tasks.
- Attach plan times to every task:
  - use the invocation time as the default plan start
  - keep user-provided start times or durations when present
  - estimate the rest conservatively
- Default lunch break window is 11:50-14:00.
- If the user gives a lunch break, meeting, commute, or other blocked time window, shift the remaining plan to the next available slot.
- When a single task spans a blocked window, split it into consecutive blocks instead of overlapping the blocked time.
- If any earlier daily note still has open items, reserve at least one carry-over slot for them, prioritizing the most recent leftover items first.

## Source Priority

- Prefer the task board and phase plan inside `20 Projects/高软-系统架构师`.
- Use `00 Inbox` for unprocessed captures.
- Use `10 Daily` files before today to recover unfinished items.
- Use the current user message to add new goals, deadlines, and constraints.
- Do not scan `20 Projects/Stock Prompt+report` or `20 Projects/龟龟策略` by default; they are not part of the note workflow.

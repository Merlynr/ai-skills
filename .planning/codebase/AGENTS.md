# OpenCode Planning Context

This file is generated from all files under .planning/codebase.

## Startup Runtime Status

- context_dir: /root/.config/skillshare
- project_name: skillshare
- session_mode: continue_last
- compile_commands: not_applicable
- cymbal_warmup: succeeded
- cymbal_summary: Done in 8ms — 0 indexed, 0 symbols, 1 unchanged

## Code Navigation

Use `rtk cymbal` as the preferred tool for semantic code navigation.

Use Cymbal when you need to:
- understand a function, class, method, type, or exported variable
- find definitions, callers, references, or importers
- inspect impact before editing code
- trace what a symbol calls
- read source for a known symbol

Primary commands:

```bash
rtk cymbal index .
rtk cymbal investigate <symbol>
rtk cymbal refs <symbol>
rtk cymbal show <symbol>
rtk cymbal context <symbol>
rtk cymbal impact <symbol>
rtk cymbal trace <symbol>
rtk cymbal search <query>
rtk cymbal outline <file>
rtk cymbal structure
```

For non-git directories or shared config/workspace directories, prefer an explicit database:

```bash
rtk cymbal -d /tmp/cymbal.db index <path>
rtk cymbal -d /tmp/cymbal.db investigate <symbol>
```

Cymbal is preferred for semantic navigation. Use `rg`, `rg --files`, `sed`, and direct file reads for file discovery, literal text search, config files, Markdown, logs, generated files, or when Cymbal returns no useful result.


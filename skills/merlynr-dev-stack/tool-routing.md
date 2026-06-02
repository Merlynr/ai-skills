# 工具路由表

Merlynr Dev Stack 的工具分工。GSD 更新不影响本文件。

## 本地代码库理解

**何时用**：跨文件、架构不明、找复用、评估 refactor 影响。

| 工具 | 平台 | 命令/方式 |
|------|------|-----------|
| Cymbal | Codex/Linux | `rtk cymbal investigate <symbol>` / `rtk cymbal refs` |
| 语义搜索 | Cursor/OpenCode | IDE SemanticSearch / explore agent |
| 精确搜索 | 全平台 | Grep / ripgrep / ast-grep |
| 结构化摸底 | 有 GSD 项目 | `gsd-map-codebase` |
| 已知路径 | 全平台 | 直接 Read 文件 |

**分工**：

```plaintext
语义/关系/影响  → Cymbal 或 SemanticSearch
明确符号/字符串 → Grep
项目规范/架构   → .planning/codebase/ + AGENTS.md
```

## 外部当前知识

**何时用**：新 API、版本变更、官方文档、社区方案、工具最新用法。

| 优先级 | 工具 | 条件 |
|--------|------|------|
| 1 | OpenCode librarian | OpenCode 会话 |
| 2 | browser MCP | Cursor，需交互或动态页面 |
| 3 | WebFetch / WebSearch | Agent 内置且可用 |
| 4 | 向用户报告 blocker | 以上均不可用 |

**禁止**：在需要当前外部事实时，仅用模型训练记忆作答；**不使用 smart-search**（研发栈不集成）。

## nmem（Nowledge Mem）

### 读取

| 时机 | 命令/Skill |
|------|------------|
| 会话开始 | `nmem wm` 或 `read-working-memory` |
| 查历史决策 | `nmem m search "关键词"` 或 `search-memory` |
| 查集成形态 | 搜 `codex_smart`、`skillshare`、`Cymbal` |

### 写入

| 时机 | 方式 |
|------|------|
| 会话结束（>30s 有结论） | `distill-memory` → `nmem m add/update` 或 MCP memory_add |
| **M 级任务完成**（有结论） | Phase 4.5 模块 agent **必须**；nmem **建议** ≥1 条（排障/性能/决策） |
| **L 级任务完成** | Phase 4.5 **必须** + `distill-memory` **必须** ≥1 条 |
| 里程碑/架构决策 | `distill-memory` |
| GSD 阶段完成 | `gsd-extract-learnings` |
| gsd-team 团队任务 | 执行 agent 收尾 `--learn`（可选）；nmem 仍走 `distill-memory` |

写入由 Agent 按 skill 执行；**不会**因改代码或 commit 自动入库。

**UTF-8 安全**（Windows）：

```powershell
$c = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
nmem --json m update <id> -t "标题" -c $cjs
```

禁止：`$text | nmem m add --stdin`（易乱码）。

## GSD 命令速查（只调用）

```plaintext
意图不明     → gsd-do
讨论需求     → gsd-discuss-phase
澄清交付     → gsd-spec-phase
写计划       → gsd-plan-phase
执行         → gsd-execute-phase
多 agent     → gsd-team
验收         → gsd-verify-work
审查         → gsd-code-review
更新 GSD 后  → gsd-reapply-patches（仅当改过 GSD 安装文件时）
```

**Merlynr 定制永远写在 skillshare SSOT**，不写进 `get-shit-done/`。

## skillshare 路径

| 环境 | SSOT |
|------|------|
| Windows | `%APPDATA%\skillshare\skills\` |
| Linux | `~/.config/skillshare/skills/` |

新建 skill → 源目录创建 → `skillshare sync` → `skillshare push`（若配了 Git remote）。

## MCP 态度

按需接入；不作为工作流本体。Merlynr 栈常见保留：

- browser / Playwright（前端验证）
- GitHub（PR/issue）
- nmem MCP（记忆读写，若已配置）

Context7 / deepwiki 类文档 MCP → 按需接入，非默认；优先 librarian / browser 取证据。

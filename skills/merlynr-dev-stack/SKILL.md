---
name: merlynr-dev-stack
description: >-
  Merlynr 个人 AI 开发工作流栈（GSD + nmem + 证据优先路由）。在非琐碎编码/重构/新功能/研究任务开始时自动应用；
  不修改 GSD 本体，GSD 更新后仍有效。Use when 开发任务、工作流、改代码、重构、查库、外部文档、
  dev stack、工作流优化、开始写代码前。
tags: [workflow, stack, gsd, nmem, evidence, routing, merlynr]
triggers:
  - merlynr
  - Merlynr
  - 开发工作流
  - dev stack
  - 工作流栈
  - 开始开发
  - 写代码前
  - 怎么分工
tool_chain:
  - gsd-do
  - gsd-discuss-phase
  - gsd-plan-phase
  - gsd-execute-phase
  - gsd-verify-work
  - search-memory
  - read-working-memory
context_injection: true
---

# Merlynr Dev Stack

GSD 更新会覆盖 `get-shit-done/` 与 `gsd-*` 安装文件。**本 skill 是唯一权威的个人工作流层**——只读 GSD，不改 GSD；所有定制写在这里或 skillshare SSOT 下的兄弟 skill。

## 设计原则

1. **证据优先**：不凭模型记忆断言版本、API、项目结构。
2. **先理解再改**：跨文件任务必须先探库，再编辑。
3. **GSD 管复杂任务生命周期**；小改动直接做，不开仪式。
4. **nmem 管跨会话记忆**；会话内语境由当前工具负责。
5. **Skill 管工作流**；MCP/CLI 管工具接口，不把 MCP 当工作流本身。

## 任务分级路由

收到任务后先分级，再选路径：

| 级别 | 信号 | 路径 |
|------|------|------|
| **S** 琐碎 | 单文件、明确符号、一行修复 | 直接改；可选 `gsd-fast` |
| **M** 中等 | 2–5 文件、边界清楚 | 本地探库 → 改 → 最小验证；可选 `gsd-quick`；验收略模糊 → grill-lite **≤3 轮** |
| **L** 复杂 | 新功能、重构、多模块、验收标准模糊 | 完整 Dev Stack 流程（下文） |

**L 级完整流程（Merlynr M0–M4；≠ gsd-team 的 Phase 0/1）：**

```plaintext
M0   需求澄清（grill-lite，可选）
M1   本地/外部证据收集（tool-routing）
M2   GSD 规划（discuss → spec/plan-phase）
M3   执行（execute-phase / gsd-team）
M4   验证与沉淀（verify-work + nmem + extract-learnings）
M4.5 模块 agent 写回（M/L，见下文）
```

下文仍用 Phase 0–4.5 指同一序列；与 `gsd-team` Phase 0 Cymbal Brief 并存时以 **Merlynr M*** 为准理解上下文。

**与 gsd-team 的分工：**

| Skill | 职责 |
|-------|------|
| **merlynr-dev-stack**（本 skill） | S/M/L 路由、证据优先、Phase 0–4.5 全生命周期、模块 `AGENTS.md` 写回规范 |
| **gsd-team** | 仅 L 级（或用户 insist）的多 agent 编排；Phase 0 产出 Team Brief（含 `persist_target`） |

M 级走 Merlynr + `gsd-quick`，**不默认**组 team；L 级 Phase 3 可选用 `gsd-team`，Phase 4.5 仍由 **Merlynr** 执行写回。

## Phase 0：需求澄清（grill-lite）

模糊想法、验收标准不清、或用户说「大概想要」时，**先读 [grill-lite.md](grill-lite.md)**：

- **S 级**：跳过
- **M 级**：验收略模糊且范围 ≤5 文件 → 最多 **3 轮**；仍不清 → 升 L 或 `gsd-discuss-phase`
- **L 级**：最多 **12 轮**；一次只问一个问题
- 能从代码库答的 → 走 M1 探库，不空问
- 需要外部事实的 → 走 tool-routing 外部检索，不猜
- 出口前输出 **Grill 共识** handoff 块（见 grill-lite.md），再进 GSD 或执行

**不要**在 S 级任务上跑 grill-lite；**不要**无 handoff 直接进入 `gsd-discuss-phase`（避免重复拷问）。

## Phase 1：证据收集

**先读 [tool-routing.md](tool-routing.md)**，按平台选工具：

- **本地代码库**：Cymbal / 语义搜索 / Grep / `gsd-map-codebase`
- **外部当前信息**：OpenCode librarian / 浏览器 MCP / WebFetch（见 tool-routing.md）
- **历史决策与集成形态**：`search-memory` 或 `nmem m search`

跨文件影响必答：

- 相关模块在哪？有无可复用实现？
- 调用链与边界？类似逻辑项目里怎么写？
- 改这里会影响哪些层？

## Phase 2：GSD 规划（只调用，不修改）

项目有 `.planning/` 时：

| 阶段 | Skill | 何时 |
|------|-------|------|
| 讨论 | `gsd-discuss-phase` | 需求/约束未清 |
| 规格 | `gsd-spec-phase` | 交付物模糊 |
| 计划 | `gsd-plan-phase` | 准备实施 |
| 路由 | `gsd-do` | 不确定用哪个 GSD 命令 |

**不引入 Trellis**——GSD 的 PROJECT / ROADMAP / PLAN / STATE 已覆盖同等职责。

## Phase 3：执行

| 场景 | Skill |
|------|-------|
| 单阶段多 plan 并行 | `gsd-execute-phase` |
| 多 agent 协作 | `gsd-team` |
| 意图不明 | `gsd-do` |

执行中：

- 复用项目现有命名、工具、错误处理模式
- 小步可回滚；不顺手大范围重构
- 破坏性/远程/凭据操作 **先问用户**

## Phase 4：验证与沉淀

nmem 由 **`distill-memory` / `read-working-memory` / `search-memory`** 负责读写，是工作流 skill 引导的主动沉淀，**不是** git commit 或保存文件触发的后台同步。

### 通用交付检查（S/M/L）

- [ ] 跑了最小相关验证（测试/lint/build/诊断），或说明为何不能跑
- [ ] 说明改了什么、验证了什么、剩余风险
- [ ] 复杂任务：`gsd-verify-work` 或 `gsd-code-review`

### M/L 收尾门禁（有实质结论时必须走完）

| 步骤 | M 级 | L 级 | 入口 |
|------|------|------|------|
| 1 模块 SSOT | **必须** Phase 4.5 | **必须** Phase 4.5 | 主模块或 Brief `persist_target` → `AGENTS.md` |
| 2 nmem | **建议** ≥1 条 | **必须** ≥1 条 | `distill-memory` → `nmem m add/update` |
| 3 团队复盘 | 跳过 | 若用了 gsd-team | `gsd-team-engine.py --learn --result …`（可选） |

**执行顺序**：先 Phase 4.5 模块 agent，再 `distill-memory` 到 nmem。  
**可跳过**（任一条）：纯 S 级；无可泛化结论；用户明确说不要写 memory / 不要改 AGENTS。  
**M 级仍建议写 nmem**：排障根因、性能热点、架构取舍、跨模块教训——即使只改 2–3 个文件。

会话 >30s 且有结论的非 M/L 任务，仍按 `tool-routing.md` § nmem 写入。

## Phase 4.5：模块 agent 写回（M/L）

将**已验证**的结论沉淀到目标模块的 `AGENTS.md`（模块 SSOT）。**S 级跳过**。

### 写到哪里

| 来源 | 目标文件 |
|------|----------|
| Cymbal / Brief 主模块 | 如 `modules/ISMS/flowcollect/AGENTS.md` |
| L 级 gsd-team Brief | Brief 中的 `persist_target`（见 `gsd-team` skill） |
| 手动判定 | 改动最集中的模块目录下的 `AGENTS.md` |

**不要**把模块细节写进根 `AGENTS.md`（根文件偏全局导航）；**不要**把未验证推测写进模块 agent。

### M 级 vs L 级

| 级别 | 写回章节 | 篇幅 |
|------|----------|------|
| **M** | `## Recent Changes`；必要时 `## Performance Notes` | 3–8 行 |
| **L** | 上述 + `## Decisions`；未闭环加 `## Open Questions` | 结构化小节 |

### 模块 AGENTS 推荐章节（在现有文档末尾维护）

```markdown
## Recent Changes        ← M/L 增量，有时效（建议保留最近 5 条）
## Decisions             ← 仅 L：架构/行为选择及理由
## Performance Notes     ← 性能排查、热点符号、配置项
## Open Questions        ← L 未闭环项
```

已有稳定内容（如「维护注意点」「合包模式」）可在 L 级任务后**合并精炼**，而非重复堆在 Recent Changes。

### M 级模板

```markdown
### YYYY-MM-DD | M | 一句话标题
- **范围**: 文件/符号（含行号或 Cymbal 符号名）
- **结论**: 做了什么或排查结论；验证方式
- **注意**: 后续维护者必知的一点（可选）
```

### L 级模板（在 M 模板之上）

```markdown
## Decisions
- **D1**: …（为何选 A 不选 B；证据：符号/测试/配置键）

## Open Questions
- …（禁止伪装成已解决）
```

### 写回前门禁

1. 结论有**代码或运行证据**（符号、行号、配置键、测试命令输出）
2. reviewer / 用户已确认「可入库」
3. 多模块任务：**主模块**写完整块；次模块仅 1–2 行交叉引用

### 与 nmem 的分工

| 载体 | 存什么 | M/L 要求 |
|------|--------|----------|
| **模块 `AGENTS.md`** | 本仓库、本模块的可提交 SSOT（团队共享） | M/L **必须**（有结论时） |
| **nmem** | 跨项目习惯、个人 breakthrough、可搜索决策 | L **必须** ≥1 条；M **建议** |

先写模块 agent，再按 Phase 4 表执行 `distill-memory`（L 级不可省略）。

### Git 建议

写回单独 commit，便于 review：

```text
docs(flowcollect): update module agent after merge perf investigation
```

### 与 gsd-team 的衔接

- **gsd-team** Phase 0 Brief 应标注 `persist_target` / `persist_grade`（人工或 triage-lead 填写）
- 团队任务 **Step 7 之后**由执行 agent 按本 Phase 4.5 写回，**不由** `gsd-team-engine.py` 自动改文件
- M 级未组 team 时，执行者在交付前直接按本节写回

## 会话开场（L/M 级建议）

非琐碎任务开始时：

1. `read-working-memory` 或 `nmem wm` — 今日焦点
2. 读项目本地规则：`AGENTS.md`、`.cursor/rules`、`.planning/`
3. 有 `.planning/codebase/` → 读 ARCHITECTURE / CONVENTIONS
4. `search-memory` 查相关历史决策（如「Codex 集成」「skillshare 同步」）

## 与 L 站 Cursor 工作流的对照

本栈 **吸收其思想、替换其工具**：

| L 站组件 | Merlynr 等价 |
|----------|--------------|
| grill-me | grill-lite.md → gsd-discuss-phase |
| Trellis PRD/design | GSD spec + plan-phase |
| ACE | Cymbal + map-codebase + 语义搜索 |
| 外部资料检索 | OpenCode librarian / browser MCP / WebFetch |
| Cursor++ 多模型 | 各工具自有模型配置 + gsd-team 分角色 |
| trellis-check | gsd-verify-work / code-review |

## 平台与工具

按平台选探库/检索工具 → **[tool-routing.md § 按平台默认路径](tool-routing.md)**（唯一 SSOT，此处不重复）。

## Base 层 skill 加载（门面型 target）

门面 profile（cursor、agents、opencode 等）未 sync 完整 GSD base 层时，**不要**假设 Skill/$mention 可用：

1. 解析 SSOT：`SKILLSHARE_SKILLS` 或 `~/.config/skillshare/skills`（Windows：`%APPDATA%/skillshare/skills`）
2. Read `{SSOT}/base/{skill-name}/SKILL.md`
3. 按文件内容执行；L1 workflow 仍从平台 runtime 读取（如 `~/.codex/get-shit-done/workflows/`）

示例：`gsd-plan-phase` → Read `~/.config/skillshare/skills/base/gsd-plan-phase/SKILL.md`

执行型 target（**codex**）通常已全量 sync，优先 Skill/$mention；门面 target（cursor、agents、opencode）缺失时再 Read SSOT base 路径。

## 交付格式（对用户）

简体中文回复，包含：

1. 改了哪些文件/区域
2. 为什么这样改（证据来源）
3. 跑了什么验证
4. 剩余风险或待办

## 附加资源

- [grill-lite.md](grill-lite.md) — 轻量需求拷问
- [tool-routing.md](tool-routing.md) — 工具路由与 nmem 写入规范

---
name: merlynr-dev-stack
description: >-
  Merlynr 个人 AI 开发工作流栈（GSD + nmem + 证据优先路由）。在非琐碎编码/重构/新功能/研究任务开始时自动应用；
  不修改 GSD 本体，GSD 更新后仍有效。Use when 开发任务、工作流、改代码、重构、查库、外部文档、
  dev stack、工作流优化、开始写代码前。
tags: [workflow, stack, gsd, nmem, evidence, routing, merlynr]
triggers:
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
| **M** 中等 | 2–5 文件、边界清楚 | 本地探库 → 改 → 最小验证；可选 `gsd-quick` |
| **L** 复杂 | 新功能、重构、多模块、验收标准模糊 | 完整 Dev Stack 流程（下文） |

**L 级完整流程：**

```plaintext
Phase 0  需求澄清（grill-lite，可选）
Phase 1  本地/外部证据收集（tool-routing）
Phase 2  GSD 规划（discuss → spec/plan-phase）
Phase 3  执行（execute-phase / gsd-team）
Phase 4  验证与沉淀（verify-work + nmem + extract-learnings）
```

## Phase 0：需求澄清（grill-lite）

模糊想法、验收标准不清、或用户说「大概想要」时，**先读 [grill-lite.md](grill-lite.md)**：

- 一次只问一个问题，最多 12 轮
- 能从代码库答的 → 走本地探库，不空问
- 需要外部事实的 → 走外部检索，不猜
- 共识足够 → 进入 GSD；仍模糊 → `gsd-discuss-phase` 或 `gsd-explore`

**不要**在 S 级任务上跑 grill-lite。

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

交付前检查：

- [ ] 跑了最小相关验证（测试/lint/build/诊断），或说明为何不能跑
- [ ] 说明改了什么、验证了什么、剩余风险
- [ ] 复杂任务：`gsd-verify-work` 或 `gsd-code-review`
- [ ] 可复用经验：`gsd-extract-learnings` 或 `distill-memory`
- [ ] 会话 >30s 且有实质结论：写 nmem（见 tool-routing.md § nmem）

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

## 平台速查

| 平台 | 启动/记忆 | 本地探库 | 外部检索 |
|------|-----------|----------|----------|
| **Codex** | codex_smart → nmem | rtk cymbal investigate | librarian / WebFetch |
| **OpenCode** | read-working-memory | search-mode + explore | librarian + analyze-mode |
| **Cursor** | nmem search（可选） | IDE 搜索 + 读文件 | browser MCP / WebFetch |

## 交付格式（对用户）

简体中文回复，包含：

1. 改了哪些文件/区域
2. 为什么这样改（证据来源）
3. 跑了什么验证
4. 剩余风险或待办

## 附加资源

- [grill-lite.md](grill-lite.md) — 轻量需求拷问
- [tool-routing.md](tool-routing.md) — 工具路由与 nmem 写入规范

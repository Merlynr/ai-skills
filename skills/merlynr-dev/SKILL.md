---
name: merlynr-dev
description: >-
  Merlynr 工程方法论层：接口先行、模块拆分、适度重复、多 Agent 独立性、分模块实现、系统验证、
  接口变更回归、非编码任务路由、Handoff JSON、模块健康度、nmem 标签。
  与 merlynr-dev-stack 配合——stack 管 S/M/L 路由与 GSD 生命周期，本 skill 管 M0-pro/M2–M4 的执行规范。
  Use when 显式强调某门禁：INTERFACE.md、no-code-first、Grill-Pro、独立 subagent review、
  agent-roles、系统验证清单、接口变更影响面、设计-only/文档/Review；日常开发只需 @merlynr-dev-stack。
tags: [workflow, merlynr, interface-first, module-patterns, validation, engineering, agent-roles, handoff-json]
triggers:
  - merlynr-dev
  - M2.5 接口冻结
  - INTERFACE.md
  - no-code-first
  - Grill-Pro
  - 独立 subagent review
  - agent-roles
  - 系统验证清单
  - 热更新回滚验证
  - 接口变更影响面
  - merlynr-handoff.json
  - 设计-only
  - 非编码任务
tool_chain:
  - merlynr-dev-stack
  - gsd-spec-phase
  - gsd-plan-phase
  - gsd-execute-phase
  - gsd-add-tests
  - gsd-code-review
  - gsd-verify-work
  - gsd-team
  - distill-memory
  - search-memory
context_injection: true
---

# Merlynr Dev — 工程方法论层

**stack 做调度，dev 做规范。** 先读 [merlynr-dev-stack](../merlynr-dev-stack/SKILL.md) 完成 S/M/L 分级；stack 在 L/M 跨模块时会自动 Read 本 skill，**通常不必重复 @merlynr-dev**。

## 与 merlynr-dev-stack 的分工

| Skill | 职责 |
|-------|------|
| **merlynr-dev-stack** | S/M/L 路由、tool-routing、grill-lite、GSD M0–M4、Phase 4.5 写回、nmem |
| **merlynr-dev**（本 skill） | grill-pro、模块拆分、接口冻结/变更、抽象纪律、Agent 独立性、分模块实现、系统验证、非编码路由、Handoff JSON |

## 完整时间线（Merlynr M* + dev 插入点）

```plaintext
M0   需求澄清（stack grill-lite；L → grill-pro；设计-only → non-coding-routes）
M1   证据收集（stack tool-routing）
M2   模块拆分 + G1 健康度（module-patterns + module-health）
M2.5 接口冻结（interface-first）；变更 → interface-change-protocol（D2/G4）
M3   分模块实现（phase3-protocol + agent-roles）
M4   验证（stack + system-validation + 独立 Review/test）
M4.5 写回 + nmem（nmem-tags）；可选 merlynr-handoff.json 归档
```

## M/L 激活矩阵

| 功能 | S | M | L |
|------|---|---|---|
| E 非编码路由 | 文档单文件 | 设计/Review | grill-pro + 设计交付 |
| **M+ / L-lite** | — | [iteration-modes.md](iteration-modes.md) | L-lite 见同文档 |
| B1 grill-pro | 跳过 | 跳过 | 需求未清 **建议**（L-lite：**6 轮**） |
| G1 模块健康度 | 跳过 | 跨模块建议 | **强制** |
| A1 Interface-First | 跳过 | 跨模块/API **强制** | **强制** |
| D2 接口变更/G4 | 跳过 | public 变更 **强制** | **强制** |
| A2 抽象纪律 | 跳过 | 大 diff **自检** | **强制** |
| A3 模块 Playbook | 跳过 | 可选 | **强制** |
| C1 Agent 独立性 | 跳过 | 独立 Review **强制** | **强制** |
| D1 分模块实现 | 跳过 | 跨模块 **建议** | **强制** |
| C2 系统验证 | 跳过 | 命中信号 **叠加** | 命中 **强制** |
| G2 Handoff JSON | 跳过 | 可选 | 建议 |
| G5 nmem 标签 | 跳过 | 有结论建议 | **建议** ≥1 标签 |

## 冲突解决

1. **路由优先级**：stack 决定 S/M/L；dev 激活上表。
2. **E 非编码**：识别为设计-only → **跳过 M3/M2.5 冻结**（草案 INTERFACE 可保留）。
3. **D2**：与 A1 并存；frozen 后改签名必须 D2，不得绕过 M2.5 静默改。
4. **M4**：stack 通用 + C2（命中）+ C1 独立 Review **均过** 才 M4.5。

## 降级路径

| 缺失 | 降级行为 |
|------|----------|
| **无 `.planning/`** | Handoff 落 `INTERFACE.md` + 回复；JSON 落模块目录 |
| **无 Cymbal** | G4 用 `rg`；符号表用 `path:symbol` |
| **无 gsd-team** | agent-roles 手动 subagent；Handoff JSON 作 prompt 清单（**不**自动进引擎） |
| **无 JSON** | 仅 Markdown Handoff，不阻塞 |

## 执行顺序

### S 级 · 非编码（E）

**S 级 + 设计-only / 单文件文档** → Read [non-coding-routes.md](non-coding-routes.md)：**直接回答或改单文件文档**，跳过 M0–M4 仪式与 M2.5 冻结。由 stack 路由即可，通常不必走下列编码路径。

### L/M 级 · 跨模块编码

1. stack M0–M1。
2. L 需求未清 → [grill-pro.md](grill-pro.md) → 可选 [handoff-schema.md](handoff-schema.md) 写 JSON（**不**会被 gsd-team 自动读取，见 handoff-schema §与 team-brief）。
3. [module-patterns.md](module-patterns.md) + L 级 [module-health.md](module-health.md) → **均分 ≥3 且无任维 1 分** 才进入步骤 4；否则再拆模块或补 IO。
4. [interface-first.md](interface-first.md) **冻结（M2.5）**；Implement 中变更 → [interface-change-protocol.md](interface-change-protocol.md)。
5. stack GSD spec/plan → M3：[phase3-protocol.md](phase3-protocol.md) + [abstraction-rules.md](abstraction-rules.md) + [agent-roles.md](agent-roles.md)。
6. M4：stack 通用验证 + [system-validation.md](system-validation.md)（若命中 C2）+ **C1 独立** Review/test（见 agent-roles）。
7. stack M4.5 + [nmem-tags.md](nmem-tags.md) 沉淀。

**L/M 设计-only** → Read [non-coding-routes.md](non-coding-routes.md)，在步骤 4 **之前** 结束编码路径（INTERFACE 可保留草案，不冻结）。

**M+ / L-lite** → Read [iteration-modes.md](iteration-modes.md)，调整 M2.5 与 grill-pro/G1 重量；D2/C1/C2 **不降级**。

## 子文档索引

| 文档 | 内容 | 版本 |
|------|------|------|
| [grill-pro.md](grill-pro.md) | L 级多角度、Grill-Pro Handoff | v1.5 |
| [module-patterns.md](module-patterns.md) | Playbook、模块清单 | v1 |
| [module-health.md](module-health.md) | G1 五维评分 | v2 |
| [interface-first.md](interface-first.md) | M2.5、Handoff 模板 | v1 |
| [interface-change-protocol.md](interface-change-protocol.md) | D2 变更六步、Handoff 版本、G4 影响面 | v2.1 |
| [abstraction-rules.md](abstraction-rules.md) | 适度重复、Similar Logic Registry | v2.1 |
| [iteration-modes.md](iteration-modes.md) | M+ / L-lite 快速迭代 | v2.1 |
| [agent-roles.md](agent-roles.md) | 六角色、独立性 | v1.5 |
| [phase3-protocol.md](phase3-protocol.md) | 分模块实现 | v1.5 |
| [system-validation.md](system-validation.md) | C2 checklist、工具门禁、CONCERNS | v2.1 |
| [non-coding-routes.md](non-coding-routes.md) | E 设计/文档/Review | v2 |
| [handoff-schema.md](handoff-schema.md) | G2 merlynr-handoff.json | v2 |
| [nmem-tags.md](nmem-tags.md) | G5 标签约定 | v2 |
| [examples/README.md](examples/README.md) | G3 案例锚点 | v2 |

## 交付格式（对用户）

在 stack 交付之上，L/M 跨模块额外说明：

1. Handoff / JSON 路径与冻结状态
2. G1 健康度（L 级）或「已跳过」
3. D2 是否发生；G4 影响面摘要
4. C1/C2 与独立 subagent 情况
5. nmem 标签（若写入）

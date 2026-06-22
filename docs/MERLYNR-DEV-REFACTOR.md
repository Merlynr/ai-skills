# Merlynr Dev 方法论层改造记录

> 日期：2026-06-09  
> 仓库：`~/.config/skillshare`（Merlynr 个人 skills SSOT）  
> 远程：`https://github.com/Merlynr/ai-skills.git`  
> 关联 skill：`merlynr-dev-stack`（L3 路由层）+ `merlynr-dev`（方法论层，新增）  
> 来源文档：[个人经验分享.md](../个人经验分享.md)、[AI编程案例分享.md](../AI编程案例分享.md)

---

## 1. 改造动机

### 1.1 背景

两份经验分享文档总结了 Perseus 系底层 C 模块（插件框架、规则引擎、流量分派）在 AI 辅助下的成功实践：

- 接口先行、模块边界清晰后再分模块实现
- 适度重复、谨慎抽象（适应 AI 有限上下文）
- 多 Agent 协作，测试与 Review 必须独立
- 真实环境验证（热更新、并发、DPDK/mbuf 生命周期）

`merlynr-dev-stack` 已承担 **S/M/L 路由 + GSD M0–M4 生命周期**，但缺少可执行的 **工程方法论子文档**（接口冻结模板、抽象纪律、Agent 契约、系统验证清单等）。

### 1.2 目标

1. 将经验文档 **结构化为 skill**（`skills/merlynr-dev/`），与 stack 分工：**stack 调度，dev 规范**。
2. 覆盖 M2–M4 全链路门禁，并与 `gsd-team`、`gsd-code-review` 衔接。
3. 在方法论复盘后，补齐 **四类已知隐患** 的缓解机制（见 §6）。
4. 门面 target（cursor、agents、opencode）可通过 `skillshare sync` 加载 `merlynr-dev`。

### 1.3 非目标

- 不修改 GSD 上游（L1/L2）；所有定制仍在 L3。
- 不替代项目本地 `AGENTS.md` / `.planning/`——方法论是 **跨项目模板**，项目 SSOT 仍在仓库内。
- `gsd-team-engine.py` **不自动读取** `merlynr-handoff.json`；Handoff 与 Brief 需人工或 triage-lead 对齐。

---

## 2. 架构：Stack + Dev 双层

```text
用户任务
    │
    ▼
merlynr-dev-stack          ← S/M/L 分级、grill-lite、tool-routing、Phase 4.5 写回、nmem
    │ L/M 跨模块时 Read
    ▼
merlynr-dev                ← M2/M2.5/M3/M4 执行规范（本改造主体）
    │
    ├── gsd-discuss/spec/plan/execute（有 .planning/ 时）
    └── gsd-team（L 级可选；manual_subagents 补充接口/测试角色）
```

### Merlynr M* 时间线

| 阶段 | 内容 | dev 子文档 |
|------|------|------------|
| M0 | 需求澄清 | stack grill-lite；L → grill-pro |
| M1 | 证据收集 | stack tool-routing |
| M2 | 模块拆分 | module-patterns、module-health（G1） |
| M2.5 | 接口冻结 | interface-first（A1） |
| M3 | 分模块实现 | phase3-protocol、abstraction-rules（A2）、agent-roles（C1） |
| M4 | 验证 | system-validation（C2）+ 独立 Review |
| M4.5 | 写回 | stack Phase 4.5 + nmem-tags（G5） |

**变更路径**：Implement 中发现接口不可行 → interface-change-protocol（D2）+ 回归影响面（G4）。

---

## 3. 版本演进

### v1 — 核心方法论（2026-06）

| 文件 | 代号 | 内容 |
|------|------|------|
| `interface-first.md` | A1 | M2.5 冻结、Interface Handoff 模板 |
| `abstraction-rules.md` | A2 | 适度重复三条规则、M3 自检 |
| `module-patterns.md` | A3 | Playbook（插件/规则引擎/流量分派）、模块清单 |
| `system-validation.md` | C2 | 六类触发信号、Playbook 扩展检查 |
| `examples/*` | G3 | 三案例锚点 |

### v1.5 — 多 Agent 与 L 级拷问

| 文件 | 内容 |
|------|------|
| `grill-pro.md` | L 级 12 轮多角度 Handoff |
| `agent-roles.md` | 六角色契约、C1 独立性、gsd-team 映射 |
| `phase3-protocol.md` | 一模块一任务、分模块 implement |

### v2 — 变更、非编码、Handoff 机器可读

| 文件 | 代号 | 内容 |
|------|------|------|
| `interface-change-protocol.md` | D2/G4 | 变更六步、Cymbal/rg 影响面 |
| `non-coding-routes.md` | E | 设计-only / 文档 / Review，跳过 M3 |
| `module-health.md` | G1 | 五维 1–5 分，均分 <3 禁止 M2.5 |
| `handoff-schema.md` | G2 | `merlynr-handoff.json` schema |
| `nmem-tags.md` | G5 | nmem 标签约定 |

**引擎**：`script/gsd-team-engine.py` v3.3 解析 `team-brief.json` → `dispatch_hints.manual_subagents`。

**配置**：`config.linux.yaml` / `config.windows.yaml` facade `include` 增加 `merlynr-dev`。

### v2.1 — 方法论隐患缓解（2026-06-09）

针对经验文档四类潜在缺陷的补强：

| 隐患 | 缓解 | 文件 |
|------|------|------|
| 「适度重复」→ 长期技术债 | **不可重复类型**（内存/锁/解析安全）；**Similar Logic Registry**（L 级 Phase 4.5） | `abstraction-rules.md` |
| 多 Agent 上下文断层 | **handoff_version** + D2 **作废广播**；tester 禁止用旧版 Handoff | `interface-change-protocol.md`、`handoff-schema.md`、`agent-roles.md` |
| 审查疲劳 | **工具门禁**（ASan/TSan/压测先于眼审）；**CONCERNS 叠加** + 窄范围 Review | `system-validation.md` |
| 瀑布流过重 | **M+**（public 小步冻结）、**L-lite**（6 轮 grill、G1 三维、单模块串行） | `iteration-modes.md`、stack 路由表 |

---

## 4. 目录清单

```text
skills/merlynr-dev/
├── SKILL.md                      # 入口、M/L 激活矩阵、执行顺序
├── grill-pro.md                  # B1
├── module-patterns.md            # A3
├── module-health.md              # G1
├── interface-first.md            # A1
├── interface-change-protocol.md  # D2/G4
├── abstraction-rules.md          # A2（v2.1：Registry + 不可重复类型）
├── agent-roles.md                # C1
├── phase3-protocol.md            # D1
├── system-validation.md          # C2（v2.1：工具门禁 + CONCERNS）
├── non-coding-routes.md          # E
├── handoff-schema.md             # G2
├── nmem-tags.md                  # G5
├── iteration-modes.md            # M+ / L-lite（v2.1 新增）
└── examples/
    ├── README.md
    ├── plugin-module.md
    ├── rule-engine.md
    └── traffic-dispatch.md

skills/merlynr-dev-stack/         # 已有；本次增强 Phase 4.5、M+/L-lite 路由
script/gsd-team-engine.py         # manual_subagents 解析
skills/gsd-team/SKILL.md          # Brief dispatch_hints 文档
```

---

## 5. M/L 激活矩阵（摘要）

| 功能 | S | M | L |
|------|---|---|---|
| grill-pro | 跳过 | 跳过 | 建议（L-lite：6 轮） |
| Interface-First | 跳过 | 跨模块强制 | 强制 |
| 抽象纪律 A2 | 跳过 | 大 diff 自检 | 强制 + Registry |
| Agent 独立性 C1 | 跳过 | 独立 Review 强制 | 强制 |
| 系统验证 C2 | 跳过 | 命中叠加 | 命中强制 |
| D2 接口变更 | 跳过 | public 变更强制 | 强制 |
| M+ / L-lite | — | iteration-modes | L-lite 见同文档 |

**日常入口**：只需 `@merlynr-dev-stack`；L/M 跨模块时 stack 自动 Read `merlynr-dev`。

---

## 6. 四类隐患与对策（设计 rationale）

### 6.1 适度重复 → 技术债

- **文档原意**：两个差异较大的协议解析器可独立实现，非禁止抽象。
- **风险**：内存/锁/安全边界被复制多份，CVE 需 N 处同步修复；AI 不擅长跨模块一致性重构。
- **对策**：A2 不可重复类型 + L 级 Similar Logic Registry + 第三处相似需求触发收敛任务。

### 6.2 多 Agent 上下文断层

- **风险**：implementer 发现 DPDK/接口限制需改 Handoff，tester 仍按旧版写用例 → 假绿。
- **对策**：`handoff_version` 递增 + CHG 作废广播；tester/reviewer 输入链强制最新冻结 INTERFACE。
- **局限**：Brief 与 Handoff JSON 仍须 triage-lead **手工对齐**；引擎不自动双向 sync。

### 6.3 审查疲劳

- **风险**：AI 并发/mbuf 代码「看起来对」；Senior 通读 generated C 比手写更慢。
- **对策**：C2 工具门禁优先；CONCERNS 符号触及 → 窄范围 Review（Handoff + diff 热点 + 工具输出）。

### 6.4 瀑布 vs 敏捷

- **文档受众**：边界清楚的底层基建（插件、规则引擎、分派）。
- **对策**：S/M 跳过大部分门禁；**M+** 演进业务；**L-lite** 多模块但非锁死基建；**L** 默认不变。

---

## 7. 与 gsd-team 的集成

### team-brief.json 示例片段

```json
{
  "dispatch_hints": {
    "manual_subagents": [
      { "name": "interface-designer", "phase": "plan", "skills": ["merlynr-dev"] },
      { "name": "tester", "phase": "verify", "skills": ["gsd-add-tests"] }
    ],
    "merlynr_handoff": ".planning/merlynr-handoff.json"
  }
}
```

- `manual_subagents`：**已被** `gsd-team-engine.py` 解析并生成成员。
- `merlynr_handoff`：仅为路径备忘，**不触发**自动加载。

### 角色映射

| merlynr-dev | gsd-team |
|-------------|----------|
| 设计 | architect + researcher |
| 接口 | manual_subagent（无内置角色名） |
| 实现 | implementer |
| 测试 | manual_subagent + gsd-add-tests |
| Review | reviewer |

---

## 8. 使用指南

### 8.1 日常开发

```text
1. @merlynr-dev-stack（或 Codex/Cursor 自动加载）
2. 任务分级 S/M/L；M0 可声明 iteration_mode: M+ | L-lite
3. L/M 跨模块 → 自动 Read merlynr-dev 子文档
4. M4.5 写回模块 AGENTS.md + nmem
5. skillshare sync（改 SSOT 后）
```

### 8.2 显式触发 merlynr-dev

INTERFACE.md、Grill-Pro、独立 subagent review、接口变更影响面、设计-only 等关键词时可直接 `@merlynr-dev`。

### 8.3 emanager 等项目

- 项目本地：`.planning/MERLYNR.md`、模块 `AGENTS.md`、`public/*_public.h` 作接口 SSOT。
- 策略模块 Playbook：见项目 `docs/merlynr-playbook-policy-module.md`（未纳入本 repo SSOT 时可复制到 examples）。

---

## 9. 验证与同步

改造完成后执行：

```bash
cd ~/.config/skillshare
skillshare sync
# cursor/agents/opencode: merlynr-dev 应在 facade include 内
```

可选：`skillshare doctor` 检查 skill 路径重叠。

---

## 10. 后续可选工作

| 项 | 说明 |
|----|------|
| Handoff → Brief 自动同步脚本 | 减少 triage-lead 手工复制 |
| 引擎内置 `interface-designer` / `tester` 角色名 | 替代 manual_subagents 字符串 |
| `个人经验分享.md` §适用边界 | 与 iteration-modes 呼应 |
| emanager policy-module Playbook 回灌 examples | skillshare SSOT 案例库 |

---

## 11. 变更文件索引（本次 push）

| 路径 | 变更类型 |
|------|----------|
| `skills/merlynr-dev/` | 新增（18 文件） |
| `skills/merlynr-dev-stack/SKILL.md` | M+/L-lite 路由、Phase 4.5 Registry |
| `skills/merlynr-dev-stack/grill-lite.md` | 与 dev 交叉引用 |
| `skills/gsd-team/SKILL.md` | manual_subagents 说明 |
| `script/gsd-team-engine.py` | manual_subagents 解析 |
| `config.linux.yaml` / `config.windows.yaml` | facade include merlynr-dev |
| `docs/MERLYNR-DEV-REFACTOR.md` | 本文档 |
| `个人经验分享.md` / `AI编程案例分享.md` | 方法论来源（仓库归档） |

---

*文档版本：v2.1 | 与 `skills/merlynr-dev/SKILL.md` 子文档索引同步*

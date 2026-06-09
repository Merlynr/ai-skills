# G2：Handoff 机器可读格式

可选：在 Markdown Handoff 之外写入 `merlynr-handoff.json`，供 **人工、triage-lead、脚本** 或 `gsd-plan-phase` 上下文消费。

> **与 gsd-team 引擎**：`gsd-team-engine.py` **不会**自动读取 `merlynr-handoff.json` 内容。组 team 时请在 **`team-brief.json`** 的 `dispatch_hints.manual_subagents` 写 Agent 与 skills（v2 已解析）。Handoff JSON 与 Brief 可 **手动对齐** 字段；`dispatch_hints.merlynr_handoff` 仅为 **路径备忘**，引擎不加载该文件。

## 文件位置

| 环境 | 路径 |
|------|------|
| 有 `.planning/` | `.planning/merlynr-handoff.json` |
| 无 | `{module}/merlynr-handoff.json` 或任务目录 |

Markdown Handoff 仍为 **人类 SSOT**；JSON 与 md **不一致时以 md 为准**，并应同步修正 JSON。

## Schema（merlynr-handoff v1）

```json
{
  "$schema": "merlynr-handoff-v1",
  "version": "1",
  "updated": "YYYY-MM-DD",
  "grade": "M",
  "grill_pro": {
    "path": ".planning/notes/grill-pro-2026-06-09.md",
    "no_code_first": true
  },
  "modules": [
    {
      "name": "rule-mgr",
      "playbook": "rule-engine",
      "responsibility": "规则加载与热更新",
      "health_score_avg": 4.2,
      "verify_cmd": "make test-rule-mgr"
    }
  ],
  "interface": {
    "module": "rule-mgr",
    "path": "modules/jxh-rule/INTERFACE.md",
    "status": "frozen",
    "handoff_version": "v1",
    "public_symbols": ["jxh_rule_reload", "jxh_rule_match"]
  },
  "validation": {
    "c2_triggered": true,
    "c2_signals": ["热更新", "多线程"],
    "strategy": "integration+system",
    "tool_gates": [
      { "cmd": "make test-rule-mgr ASAN=1", "pass": "0 failures" }
    ]
  },
  "agents": {
    "required_roles": ["architect", "implementer", "reviewer"],
    "manual_subagents": [
      {
        "name": "interface-designer",
        "phase": "plan",
        "skills": ["merlynr-dev"]
      },
      {
        "name": "tester",
        "phase": "verify",
        "skills": ["gsd-add-tests"]
      }
    ]
  },
  "nmem_tags": ["#interface-first", "#rule-engine", "#hot-reload"]
}
```

## 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `grade` | 是 | S \| M \| L |
| `modules` | L/M 跨模块 | 与模块清单一致 |
| `interface.status` | M2.5 后 | `draft` \| `frozen` |
| `interface.handoff_version` | 冻结后 | `v1` 起；D2 refreeze 递增 |
| `interface.public_symbols` | 冻结时 | 供 G4 `cymbal refs` |
| `validation.tool_gates` | C2 命中时 | `{ cmd, pass }` 列表；见 system-validation |
| `agents.manual_subagents` | 可选 | **与 team-brief 对齐的文档字段**；复制到 `team-brief.json` → `dispatch_hints.manual_subagents` 后引擎才生成成员 |
| `nmem_tags` | 可选 | 见 [nmem-tags.md](nmem-tags.md) |

## 写入时机

| 阶段 | 更新内容 |
|------|----------|
| Grill-Pro 出口 | `grill_pro`, `modules` 草案, `validation.strategy` |
| M2.5 冻结 | `interface.*`, `public_symbols` |
| M4 完成 | `validation.c2_*` |
| D2 变更 | `interface.status`→`draft` 再→`frozen`；**递增 `handoff_version`**；写作废广播 |

## 降级

无 JSON 工具链 → 仅 Markdown Handoff，**不阻塞**流程。

## 与 team-brief.json 的关系

| 文件 | 谁消费 | 说明 |
|------|--------|------|
| `merlynr-handoff.json` | 人 / 脚本 / plan 上下文 | 任务方法论 SSOT；**引擎不自动读** |
| `team-brief.json` | `gsd-team-engine.py` | Cymbal 嗅探 + 编组；`dispatch_hints.manual_subagents` **已解析** |

对齐方式（二选一）：

1. **推荐**：直接在 `team-brief.json` 写 `manual_subagents` / `required_roles`。
2. 维护 Handoff JSON 后 **手工复制** `agents` 段到 Brief，或 triage-lead 对照 Handoff 填 Brief。

`dispatch_hints.merlynr_handoff` 仅为路径字符串，**不触发**自动加载：

```json
"dispatch_hints": {
  "merlynr_handoff": ".planning/merlynr-handoff.json",
  "manual_subagents": [ ... ]
}
```

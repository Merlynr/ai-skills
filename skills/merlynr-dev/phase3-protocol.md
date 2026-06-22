# Phase 3：分模块实现协议

**来源**：案例「AI 分模块实现」；个人经验「小上下文、边界清晰」。

M3 执行时：**一模块一上下文**，接口冻结后按序集成。L 级强制；M 级跨模块建议。

## 上下文预算

单 implement 任务上限（超出则再拆模块）：

| 资源 | 上限 |
|------|------|
| 相关源文件 | **≤ 8** |
| 相关符号/函数 | **≤ 12** |
| 模块数 | **1**（当前 implement 任务） |

超出 → 回到 [module-patterns.md](module-patterns.md) 拆分子模块。

## 集成顺序

```text
接口层 / 头文件 / 错误码
  → 核心逻辑（单模块）
  → 输出链路 / 回调 / sink
  → CLI / 运维
  → 文档与 demo（可并行，但不与核心混在同一 implement 任务）
```

**禁止** 在单个 implement 任务中同时改规则引擎 + 分派执行 + CLI，除非 M 级且总文件 ≤5。

## 单模块 implement 任务模板

```markdown
## Implement 任务：{模块名}

- **Interface Handoff**: {path}（状态：已冻结）
- **本任务范围**: {文件列表，≤8}
- **符号**: {列表，≤12}
- **不做**: {明确排除的相邻模块}
- **完成标准**: {Handoff 中的独立验证}
- **抽象**: 遵守 abstraction-rules.md
```

## 有 gsd-team 时

1. triage-lead 按 [agent-roles.md](agent-roles.md) 安排；接口模块先 **interface subagent** 冻结再 implement。
2. `implementer` 一次只接一个模块任务（Brief 中 `scope_summary` 对齐）。
3. 每模块 implement 完成后 → 可选独立 `reviewer` subagent → 下一模块。

## 无 gsd-team 时（降级）

| 级别 | 做法 |
|------|------|
| **M** | 顺序 implement → 全部完成后 **独立 subagent** `gsd-code-review` |
| **L** | **每模块** implement → 独立 subagent review → 下一模块；最后整体验证 + C2 |

与 [SKILL.md](SKILL.md) 降级路径一致：不合并 implement + review 到同一长对话。

## 接口冻结约束

- 已冻结 public 签名 **不得** 在本阶段静默修改 → 走 [interface-change-protocol.md](interface-change-protocol.md)（D2/G4）。
- implement 发现接口不可行 → **停止** 扩散到其他模块。

## 与 abstraction-rules 的配合

Phase 3 执行中：

- 复用项目错误码、日志、CLI 框架（stack 要求）
- **不** 为跨模块「统一」抽新基类（dev A2）
- 第三处相似需求出现前，允许模块内重复

## 模块完成检查（每模块）

- [ ] 仅改动任务范围内文件
- [ ] Handoff 独立验证命令已跑或说明阻塞
- [ ] 未改其他模块已冻结接口
- [ ] M/L：Review subagent 已跑或已排入下一 session

## 反模式

- 一个 prompt「把整个子系统写完」
- 上下文塞满全仓库 grep 结果
- 先写实现再补 INTERFACE.md
- 跳过中间模块 review 直接联调大集成

# Agent 角色契约与独立性门禁

**来源**：个人经验 §四「多 Agent 协作」；「测试和 Review 必须独立 agent」。

核心原则：**同一 Agent 不得在同一轮上下文中兼设计、实现、测试、Review。** 否则容易自证正确。

```text
代码通过测试或 Review ≠ 代码满足真实需求
```

测试与 Review 应优先依据 **需求、Grill Handoff、Interface Handoff、SPEC**，再对照实现。

## 六角色定义

| 角色 | 职责 | 输入 | 产出 | 禁止 |
|------|------|------|------|------|
| **设计** | 调研、总体设计、模块边界 | 需求、Grill-Pro、M1 证据 | 模块清单、设计要点 | 写实现代码 |
| **接口** | 定边界、头文件、错误码、生命周期 | 模块清单、M1 符号表 | INTERFACE.md / Handoff | 写业务实现 |
| **实现** | 按冻结接口编码 | Interface Handoff、plan | 代码 diff | 改架构、改 public 签名 |
| **测试** | 独立写测/测用例 | SPEC、Handoff、**非** implementer 口述 | 测试代码、覆盖说明 | 为通过而改 prod 代码 |
| **Review** | 功能/性能/安全/可维护性 | 同上 + diff | Review 意见 | 自己刚写的实现 |
| **优化** | 按 Review 修改并回归 | Review 清单 | 修复 + 回归结果 | 扩大 scope |

## 与 gsd-team 映射

| merlynr-dev 角色 | gsd-team 成员 | 说明 |
|------------------|---------------|------|
| 设计 | `architect` + `researcher` | Plan 阶段 |
| 接口 | **无内置** → triage-lead 安排 **独立 subagent** 或 architect 子阶段 | 只产出 INTERFACE.md |
| 实现 | `implementer` | Implement 阶段 |
| 测试 | **无内置** → 独立 subagent + `gsd-add-tests` | Verify 前或并行 |
| Review | `reviewer` | Verify 阶段 |
| 优化 | `debugger` 或 implementer **新 session** | Review 之后 |

### Team Brief 建议（triage-lead 填写）

> **引擎（v2）**：`manual_subagents` / `required_roles` 写入 **`team-brief.json`** → `dispatch_hints` 时，`gsd-team-engine.py` **会**生成对应成员。`merlynr-handoff.json` 内同名字段 **不会**被引擎自动读取——需手工同步到 Brief。详见 [handoff-schema.md](handoff-schema.md)。

在 `team-brief.json` 或研判 Markdown 末尾追加：

```markdown
## Agent 分工（merlynr-dev）
- required_roles: architect, implementer, reviewer
- manual_subagents:
  - interface: 冻结 {module} INTERFACE.md，不写实现
  - tester: 依据 SPEC + Handoff 写测试，不读 implementer 解释
- independence: implementer 与 tester/reviewer 不得同一 session
```

引擎现有 `skip_roles`：`architect` | `researcher` | `implementer` | `reviewer` | `debugger` | `ui-reviewer`。**接口/测试** 通过 `manual_subagents` 补充，直到引擎支持 `interface-designer` / `tester` 角色名。

## 按级别的独立性要求

| 级别 | 要求 |
|------|------|
| **S** | 跳过 |
| **M** | implement 完成后 **必须** 用独立 subagent（或新 session）跑 `gsd-code-review`；跨模块时 tester 建议独立 |
| **L** | 完整六角色语义；有 gsd-team 走 Brief；无 team 见降级 |

### M 级最小门禁（无 gsd-team）

```text
1. 主 agent / session：探库 + implement
2. 新 subagent：gsd-code-review（输入 = Handoff + diff，不看 implement 自述）
3. 若 SPEC 要求测试：新 subagent + gsd-add-tests
```

## 测试 Agent 输入链（强制）

tester subagent prompt **必须包含**：

1. Grill-Pro / grill-lite 共识中的验收标准
2. Interface Handoff（**最新 `handoff_version`**、冻结 IO、错误码、生命周期）
3. gsd-spec 或模块清单中的「独立验证」列
4. **禁止** 以「implementer 说这样是对的」为通过依据
5. D2 发生后：**禁止** 使用作废版本（见 [interface-change-protocol.md](interface-change-protocol.md) 作废广播）

可附 diff 作对照，但断言来源是需求与 Handoff。

## Review Agent 输入链

与 tester 相同，另加：

- [abstraction-rules.md](abstraction-rules.md)（L 级）
- [system-validation.md](system-validation.md)（命中 C2 时）：**窄范围** diff 热点 + 工具门禁输出，非通读全文件

Review 输出须分类：阻塞 / 建议 / 已满足。

## 优化阶段

Review 有 **阻塞** 项时：

1. 优化 agent（新 session 或 `debugger`）只改 Review 列出的项
2. 回归：相关测试 + Review 阻塞项复验
3. 不得借优化做 scope creep 或顺手抽象

## 与 Phase 3 的衔接

L/M 跨模块 implement 时 Read [phase3-protocol.md](phase3-protocol.md)：**一模块一任务**；每模块 implement 后可选独立 Review subagent，再进入下一模块。

## 反模式

- 同一长对话：写完代码 → 「帮我 review 一下」→ 「测试应该过了」
- tester 只跑 implementer 给的用例、不读 Handoff
- Review 通过即关闭 C2 系统清单（Review ≠ 系统验证）
- 跳过接口角色直接 implement 多模块

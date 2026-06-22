# D2：接口变更协议与回归影响（G4）

**来源**：案例热更新/生命周期；v1 `interface-first.md` 变更节扩展。

接口 **已冻结** 后若必须改 public 签名，走本协议；**禁止** 为实现方便静默改接口。

## 何时触发

- 编译/链接证明 Handoff 不可行
- 线程模型或性能测试证明 IO/生命周期设计错误
- 与现有符号对照表冲突且无法适配层解决
- 用户明确要求变更范围

**不触发**：纯内部实现调整、未冻结草案、仅改 private 符号。

## 触发责任

| 角色 | 何时触发 D2 | 必须动作 |
|------|-------------|----------|
| **implementer** | 编译/链接失败、性能/线程证明 Handoff 不可行 | **立即停止**本模块及下游扩散；不得静默改 public 签名 |
| **reviewer** | Review 发现接口/生命周期设计错误 | 开 **阻塞** 项；implementer **停止** 直至 D2 refreeze |
| **tester** | 测试暴露与 Handoff 矛盾的行为 | 报缺陷；按 implementer 停止 + D2 处理 |
| **用户** | 明确要求变更 API/范围 | 触发 D2；跳过 implementer 自行决定 |

**原则**：谁先发现谁 **喊停**；implementer **不得**「先改完再说」。未走 D2 的 public 变更视为违规。

## Handoff 版本与下游作废（与六步并行）

每个 Interface Handoff 带 **`handoff_version`**（从 `v1` 起；首次冻结为 `v1`）。D2 每次 refreeze **递增**（`v2`、`v3`…）。

| 字段 | 位置 | 说明 |
|------|------|------|
| `handoff_version` | INTERFACE.md 元数据、`merlynr-handoff.json` → `interface.handoff_version` | 当前有效版本 |
| `supersedes` | 变更记录 CHG-xxx | 作废的旧版本号 |
| `invalidates` | CHG-xxx 或 D2 广播块 | 须重跑的下游（tester / 已 implement 模块） |

**下游作废广播**（Step 5 UPDATE 时 **必须** 写入 INTERFACE 与回复）：

```markdown
### Handoff 作废广播 | CHG-00N
- **旧版本**: v{k}（已作废，勿再作为 tester/reviewer 输入）
- **新版本**: v{k+1}（已冻结）
- **须同步**: tester 用 v{k+1} 重写/重跑；已按 v{k} implement 的模块：{列表} → 停 M3 直至对齐
- **team-brief**: 若用 gsd-team，triage-lead 更新 Brief 中的 Handoff 路径与版本说明
```

tester / reviewer **不得** 使用 implementer 口述或旧版 Handoff；仅以 **最新 `handoff_version` + 已冻结 INTERFACE** 为准。

## 变更流程（六步）

```text
1. STOP   — 停止向其他模块扩散基于旧接口的实现
2. EVIDENCE — 收集失败证据（编译输出、栈、基准、线程报告）
3. IMPACT  — 跑「回归影响面」（见 G4）
4. PROPOSE — 向用户提交变更 diff（旧→新 IO/错误码/生命周期）
5. UPDATE  — 递增 handoff_version；更新 INTERFACE + Handoff JSON；发「作废广播」
6. REFREEZE — 用户/reviewer 确认 → 状态改回「已冻结」→ 继续 M3
```

L 级 Step 5 同步 Phase 4.5 `## Decisions` + 变更记录；M 级跨模块建议记录。

## G4：回归影响面（REF IMPACT）

变更提案 **必须** 列出受影响调用方，再 refreeze。

### 有 Cymbal

```bash
rtk cymbal refs <symbol>          # 每个将改的 public 符号
rtk cymbal impact <symbol>        # 改前评估（若可用）
```

产出 **影响面表**：

| 将改符号 | refs 数量 | 代表调用方（path:symbol） | 需同步改 |
|----------|-----------|---------------------------|----------|
| `foo_init` | 5 | `a.c:bar_setup`, … | 是 |

### 无 Cymbal

```bash
rg -n '\bfoo_init\s*\(' --glob '*.{c,h,cpp,hpp}'
rg -n '#include.*foo\.h' .
```

同样填影响面表，标注「静态搜索，可能不全」。

### 影响面门禁

| 级别 | 要求 |
|------|------|
| **M** | 影响面表 ≥1 行或说明「无 public 变更」 |
| **L** | 全表 + 独立 subagent Review 确认无遗漏 |

## 变更记录模板（写入 INTERFACE.md 末尾）

```markdown
## 变更记录

### CHG-001 | YYYY-MM-DD
- **handoff_version**: v1 → v2（supersedes: v1）
- **原因**: …（证据：命令输出 / 日志摘要）
- **变更**: `old_sig` → `new_sig`；IO 表 §… 已更新
- **影响面**: 见 IMPACT 表（N 处调用）
- **invalidates**: tester 用例；模块 {foo} implement（若已开工）
- **回归**: 已跑 …；Open Questions: …
- **确认**: 用户 / reviewer
```

## 与 phase3-protocol 的衔接

- 单模块 implement 中发现接口问题 → 只停 **本模块** 任务，不继续下一模块
- 多模块已按旧接口实现 → 列出 **回滚 vs 顺势变更** 两方案供用户选

## 反模式

- 先改头文件再补文档
- 影响面表为空却改 public API
- 把「适配层 hack」标为已 refreeze
- 跳过独立 Review 在 L 级合并变更

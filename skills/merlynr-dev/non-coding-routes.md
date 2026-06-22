# E：非编码任务路由

**来源**：个人经验 §六「AI 不只是代码生成器」。

需求分析、方案设计、文档整理、架构图、工程检查等 **不以提交代码为交付物** 的任务，走 stack 的 M0–M2，**跳过 M3 编码**。

## 任务类型识别

| 类型 | 信号 | 交付物 |
|------|------|--------|
| **需求分析** | 帮我想想、有哪些场景、风险 | 场景清单、风险表、Grill/Grill-Pro Handoff |
| **方案设计** | 架构讨论、怎么拆、design | 模块清单、INTERFACE 草案、design.md |
| **文档整理** | 写 README、整理接口说明 | Markdown、INTERFACE.md |
| **图形** | 架构图、时序图 | Mermaid / 外链图 / 描述稿 |
| **工程检查** | code review、看看有没有问题 | Review 报告（不改正文除非用户要求） |

**仍走编码路径**：用户说「实现」「改代码」「加功能」「fix bug」→ 正常 M3。

## 路由决策

```text
stack S/M/L 分级
  → 若交付物 ∈ 上表且无实现意图
      → M0（grill-lite / L 用 grill-pro）
      → M1 探库（若需对照代码）
      → M2：module-patterns / interface-first 草案（可选）
      → 交付文档 / 图 / Review 报告
      → 跳过 M3、M2.5 冻结（除非用户说「设计定了开始写」）
  → 若后续要编码
      → 本次产出作为 Grill-Pro / Handoff 输入，新开 implement 任务
```

## 各级别建议

| 级别 | 路径 |
|------|------|
| **S** | 直接回答或改单文件文档 |
| **M** | grill-lite ≤3 轮 → 交付；需要模块视角时用 module-patterns **清单 only** |
| **L** | grill-pro + no-code-first → 模块清单 + INTERFACE **草案**（状态：草案，非冻结）→ design 评审 |

## 验收标准（非编码）

- [ ] 读者能否按文档 **执行下一步**（写代码的人能开工）
- [ ] 范围与「不做什么」明确
- [ ] 未伪装成已运行验证（Review 报告注明静态分析范围）
- [ ] 若涉及模块边界：有模块清单或 INTERFACE 草案

**不用** build/test 作为唯一验收；用「可执行性」与「歧义是否消除」。

## 与 GSD 的衔接

| 有 `.planning/` | 无 `.planning/` |
|-----------------|-----------------|
| `gsd-discuss-phase` / `gsd-spec-phase` 产出 SPEC/设计 | 回复 + 项目 `docs/` 或 `.planning/` 外置 md |
| 不进入 `gsd-execute-phase` | 同上 |

## nmem 沉淀（G5）

非编码结论若有跨项目价值 → `distill-memory`，标签 `#non-coding` `#design`（见 [nmem-tags.md](nmem-tags.md)）。

## 反模式

- 用户只要 review，却大改代码
- 用 execute-phase 写「设计文档」
- 非编码任务仍跑 C2 系统压测清单
- design 草案标「已冻结」但未用户确认

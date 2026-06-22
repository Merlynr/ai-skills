# 迭代模式：M+ 与 L-lite

**来源**：方法论隐患复盘——L 级完整瀑布适合底层基建，不适合需求频繁变化的演进业务。

stack 的 S/M/L 分级不变；本页定义 **在同一级别内的轻量变体**，由路由时显式选用。

## 三种场景对照

| 场景 | 推荐模式 | 接口 | 流程重量 |
|------|----------|------|----------|
| **探索 / POC** | S 或 M | 无冻结；可丢弃 | 最小 |
| **演进中业务**（边写边改、public 小步稳定） | **M+** | 草案 → 小步冻结 public；internal 随意 | 中等 |
| **底层基建**（插件框架、规则引擎、多模块高性能） | **L**（默认） | M2.5 全冻结 | 最重 |
| **多模块但需求尚会变** | **L-lite** | 单模块串行 + 模块内冻结 | 较 L 轻 |

**原则**：可晚冻结，**不可** silent 改 public API——public 变更仍走 [interface-change-protocol.md](interface-change-protocol.md)（D2）。

## M+（M 级快速迭代）

**信号**：2–5 文件、跨模块或 public API，但需求每周可能变、边界在编码中才清晰。

| 步骤 | M+ 行为 | 相对默认 M |
|------|---------|------------|
| M0 | grill-lite ≤3 轮 | 同 M |
| M2.5 | **仅 public 符号** 写 INTERFACE **草案**；implement 稳定后再 **小步 refreeze** | 不强制开局全冻结 |
| M3 | 单 session implement 为主 | 同 M |
| M4 | C1 独立 Review **必须**；C2 命中则叠加 | 同 M |
| D2 | public 变更 **强制** | 同 M 跨模块 |

**禁止**：以 M+ 为由跳过 C1 或跳过 D2。

## L-lite（L 级轻量化）

**信号**：多模块 / 10+ 文件，但 **非** 目标锁死的底层基建（例如新业务策略层、运营配置扩展）。

| 门禁 | 默认 L | L-lite |
|------|--------|--------|
| grill-pro | 12 轮 | **6 轮**（缺角写入 Open Questions） |
| G1 module-health | 五维全评 | **三维**：边界清晰度、可测性、接口就绪 |
| M2.5 | 全模块一次冻结 | **单模块串行**：冻结 A → implement A → test/review A → 再 B |
| C2 / C1 | 命中强制 | 同 L |
| D2 / Handoff 版本 | 强制 | 同 L |

**选用方式**：stack M0 出口或 Brief 中写明 `iteration_mode: L-lite`；未写明则按默认 **L**。

## L（默认，不变）

Perseus 类：插件框架、jxh-rule、Dispatch、新运营商策略目录（边界清楚、返工代价高）→ 完整 grill-pro + G1 五维 + 全模块 M2.5 冻结。

## 与 non-coding-routes 的关系

- **设计-only**：仍走 E，INTERFACE 可永久草案，不进入 M+ / L-lite 编码路径。
- **M+ 编码**：不是设计-only；最终 public API 须 refreeze 或 D2 记录。

## 反模式

- 用 L-lite 跳过 C1/C2/D2
- M+ 下 silent 改 public 头文件
- 基建任务误标 L-lite 以省 grill-pro
- 多模块并行 implement 却标 L-lite（应单模块串行）

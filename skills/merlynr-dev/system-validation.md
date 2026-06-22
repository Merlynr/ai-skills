# 系统模块验证清单（C2）

**来源**：个人经验 §五「真实环境验证」；案例热更新/生命周期/性能路径。

在 stack Phase 4 **通用验证之上叠加**。命中触发信号时，清单未勾完不得 M4.5 写回（未跑项写入 `## Open Questions`）。

## 触发信号

任一命中即启用本清单：

| 类别 | 信号词 / 场景 |
|------|----------------|
| **热更新** | 热更新、reload、规则替换、回滚 |
| **并发** | 多线程、锁、竞争、atomic、per-thread |
| **高性能** | DPDK、热路径、ring、零拷贝、flow 缓存、NUMA |
| **资源所有权** | mbuf、refcnt、生命周期、transfer、内存域 |
| **流量** | 分派、mirror、drop、异常流量、背压 |
| **长时间运行** | 7×24、泄漏、稳定性、压测 |

未命中 → 仅跑 stack 通用验证，不强制本清单。

## 工具门禁（先于眼审）

命中 C2 时，**优先跑工具、再窄范围人审**——减轻审查 AI 并发代码的疲劳。

| 场景 | 至少一项（写进 Handoff 或 verify_cmd） | 未跑则 |
|------|----------------------------------------|--------|
| 内存/泄漏 | ASan / valgrind / 长时间计数趋势 | Open Question，禁止写「无泄漏」 |
| 并发/数据竞争 | TSan / 有界压测 + 线程配置 | Open Question |
| 热路径/性能 | 变更前后基准或统计对比 | Open Question，禁止写「已优化」 |
| 热更新 | 失败路径 + 回滚脚本/命令 | 阻塞 M4.5 |

Handoff 或 `merlynr-handoff.json` → `validation.tool_gates[]` 列出 **命令 + 通过判据**；Review 只核对输出摘要，不全文件通读 generated C。

## 高风险符号（CONCERNS 叠加）

C2 管 **类别**；项目级 **CONCERNS** 管 **具体文件/符号**。

| 来源 | 用法 |
|------|------|
| 模块 `AGENTS.md` 维护注意 / 高风险文件 | diff 触及 → **强制 C1** |
| `.planning/codebase/CONCERNS.md`（若有） | 同上 |
| Cymbal `impact` / `refs` 热点 | L 级 Review 输入必含 |

**窄范围 Review 输入**（M/L 跨模块 + 命中 C2 或触及 CONCERNS）：

1. Interface Handoff + **仅 diff 热点**（listed symbols / 文件）
2. C2 工具门禁输出摘要
3. **禁止** 以「通读全部 AI 生成实现」代替上述两项

L 级 diff 触及 CONCERNS 清单任一项 → 独立 subagent Review **阻塞项** 未清零不得 M4.5。

## 与 C1 独立 Review 的叠加

C2 **不替代** C1。M4 门禁（M/L 跨模块）：

```text
stack 通用验证（build/test/lint）
  + C2 本清单（命中触发信号时）
  + C1 独立 subagent Review/test（见 agent-roles.md）
  = 三者均过，才允许 M4.5 写回
```

| 级别 | C1 | C2 未命中时 |
|------|-----|-------------|
| **M** 跨模块 | implement 后 **独立** `gsd-code-review` subagent **必须** | 仅 stack + C1 |
| **L** | 独立 Review **且** 建议独立 tester | 仅 stack + C1 |

C2 清单勾完 **不能** 代替 C1；Review 通过 **不能** 代替 C2（命中时）。

## 通用 L 级检查（命中后必选）

- [ ] 最小 build/test/lint 已通过（stack 基线）
- [ ] 异常输入 / 非法配置有明确失败路径（非 silent corrupt）
- [ ] 关键路径有可复述的验证命令或输出摘要
- [ ] 剩余风险已列出，未伪装为已解决

## 系统模块扩展检查（按 Playbook 勾选）

### 热更新 / 规则类（规则引擎型、流量分派型、插件配置）

- [ ] 新规则构建 → 替换 → 激活任一步失败可 **回滚** 到旧状态
- [ ] 回滚路径已在 INTERFACE.md 或 Decisions 中描述
- [ ] reload 期间热路径阻塞可接受（或已测锁持有时间）

### 生命周期 / 所有权（规则引擎 Flow、Dispatch mbuf）

- [ ] 每个对象的 **创建者 / 持有者 / 释放者** 已文档化
- [ ] 跨线程 transfer 有明确 handoff 点（如 Flow transfer 到输出线程）
- [ ] refcnt / free / drain 规则与 action 类型一致（drop/dispatch/mirror）

### 并发 / 锁

- [ ] 共享结构访问有锁或 lock-free 设计说明
- [ ] 锁外构建、短写锁替换（若适用）已验证或注明风险
- [ ] 无已知死锁顺序（或已记录 Open Question）

### 性能

- [ ] 热路径变更前后有 **对比依据**（基准命令、统计计数、采样）
- [ ] flow 缓存 / 二分匹配 / 批量收包等优化点可定位到符号
- [ ] 性能退化未测 → 写入 Open Questions，禁止写「已优化」

### 真实环境 / 长时间（若可跑）

- [ ] 压力或长时间运行（或说明环境限制为何不能跑）
- [ ] 异常流量 / 空规则 / ring full 等边界已测或列为 Open Question
- [ ] 内存泄漏抽检（valgrind/ASan/计数趋势，择一）

## 与 Playbook 的默认勾选

| Playbook | 建议默认勾选章节 |
|----------|------------------|
| 插件型 | 热更新（若动态加载）、生命周期 |
| 规则引擎型 | 热更新回滚、Flow transfer、并发、性能 |
| 流量分派型 | 热更新、mbuf 生命周期、性能、异常流量 |

## Phase 4 出口格式

在交付回复中增加：

```markdown
### 系统验证（C2）
- **触发**: 是 | 否（原因）
- **Playbook**: …
- **工具门禁**: {命令} → {判据/摘要}
- **CONCERNS 触及**: 是 | 否（符号列表）
- **已验证**: …
- **未跑 / Open Questions**: …
```

## 反模式

- 仅跑单元测试即宣称系统级 OK
- 热更新未测失败路径
- 把「理论上应该」写进 Performance Notes
- 命中 C2 却跳过清单直接 M4.5
- 跳过工具门禁、靠 Senior 通读 AI 并发代码
- 触及 CONCERNS 符号却只做 implementer 自审

# 模块拆分 Playbook

**来源**：三案例「从设计阶段就模块化」；个人经验「先拆问题再写代码」。

L 级 M2 出口必须产出 **模块清单**；M 级跨模块任务建议产出。每个模块须满足：

- 输入明确
- 输出明确
- 职责单一
- 可独立验证

## 拆分流程

```text
1. 识别任务类型 → 选 Playbook（或自定义）
2. 列出模块清单（名称 + 一句话职责）
3. 每模块填 IO + 独立验证方式
4. 标注模块间依赖顺序（通常：接口 → 核心 → 输出/CLI → 文档）
5. L 级：Read [module-health.md](module-health.md) 评分（G1）；均分 <3 或任维 1 分 → 再拆
6. 进入 interface-first.md（每模块或主模块一份 Handoff）
```

## 模块清单模板

```markdown
## 模块清单（YYYY-MM-DD）

| # | 模块 | 职责 | 输入 | 输出 | 独立验证 |
|---|------|------|------|------|----------|
| 1 | … | … | … | … | `命令` / 通过标准 |
```

## 内置 Playbook

| 模式 | 适用场景 | 详例 |
|------|----------|------|
| **插件型** | 动态加载、HTTP/事件回调、第三方扩展 | [examples/plugin-module.md](examples/plugin-module.md) |
| **规则引擎型** | 规则加载、匹配、热更新、多链路输出 | [examples/rule-engine.md](examples/rule-engine.md) |
| **流量分派型** | 规则匹配 + 高性能分派 + 接收侧 + 统计 | [examples/traffic-dispatch.md](examples/traffic-dispatch.md) |

案例索引与内网分支 → [examples/README.md](examples/README.md)（G3）。

### 插件型 — 模块树

```text
统一插件 API
  → 插件管理器（加载/启用/禁用/状态）
  → HTTP 事件回调模型
  → 事务级状态 / 告警输出
  → demo 插件（HTTP/DNS/SNMP/…）
  → 开发文档 + CLI + 打包脚本
```

### 规则引擎型 — 模块树

```text
规则管理器（加载/XML/热更新/回滚）
  → matcher 索引 + 匹配引擎
  → Flow 上下文 + 跨线程 transfer
  → 输出链路（HTTP/流/文件/事件）
  → CLI 运维 + 统计
```

### 流量分派型 — 模块树

```text
规则引擎（MSISDN/IPv4/IPv6 分表、二分匹配、flow 缓存）
  → 分派执行（ring、action、mbuf 生命周期）
  → 接收侧（secondary 批量收包）
  → 统计输出 + 命中查询
  → 运维 CLI（状态/更新/清理）
```

## 粒度规则

| 信号 | 建议 |
|------|------|
| 单模块 >12 个相关符号或 >8 个文件 | 再拆 |
| 模块间循环依赖 | 引入接口层或事件边界 |
| 无法写「独立验证」 | 边界未清，回到 M0/M2 |
| 与现有目录不一致 | 优先对齐项目既有模块划分（M1 证据） |

## 产物路径

| 环境 | 模块清单 | 接口 |
|------|----------|------|
| 有 `.planning/` | 可写入 discuss/spec 笔记 | `.planning/interface/{module}.md` |
| 无 `.planning/` | 回复 Handoff + 模块目录 README | `{module}/INTERFACE.md` |

## 反模式

- 先写代码后补模块清单
- 一个「大模块」塞 matcher + CLI + 输出 + 内存管理
- 清单无 IO 表、无验证方式
- 忽视项目已有目录结构强行新命名

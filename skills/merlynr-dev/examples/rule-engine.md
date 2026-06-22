# 案例摘要：精细化规则匹配引擎（jxh-rule）

**规模**：源码口径 117 文件 / 27247 行；C/H 24022 行

**来源分支**：`perseus7-dev/-/tree/p7-2-full-traffic/jxh-rule`

## 模块拆分（规则引擎型 Playbook）

| # | 模块 | 职责 | 典型文件 |
|---|------|------|----------|
| 1 | 规则管理器 | XML 解析、加载、热更新、回滚 | `jxh-rule-mgr.c` (~2737) |
| 2 | matcher 索引 | 索引构建、查询结构 | `src/frame/index.c` |
| 3 | 匹配引擎 | 规则匹配主逻辑 | `src/frame/matcher.c` |
| 4 | Flow 上下文 | 跨线程 transfer、释放 | frame + output 联动 |
| 5 | 输出链路 | HTTP/流/文件/事件统一接入 | 各 output 模块 |
| 6 | CLI 运维 | 状态、命中、手动更新、内存域 | CLI 框架 |
| 7 | 集成测试 | 综合场景 | `test_comprehensive_integration.c` |

## 接口冻结要点

- 输出模块只调 **统一匹配接口**，不关心规则加载细节
- 热更新：构建 → 导出 → 替换 → reload；**任一步失败回滚**
- Flow：`transfer` 对象从匹配线程到输出线程，消息释放统一回收

## 独立验证

```text
加载规则集 → 注入测试 flow → 断言命中/输出 → 触发热更新失败 → 断言回滚
```

## C2 必勾项

- [x] 热更新回滚
- [x] Flow transfer 生命周期
- [x] 多链路输出一致性
- [x] CLI 状态与命中统计

## 常见陷阱

- 新规则半激活状态；旧规则已 free 仍被引用
- matcher 与 mgr 循环依赖；应通过冻结接口层切开

## AI 分工建议（L 级）

接口 Agent 冻结 mgr↔matcher↔output 边界 → 分文件 implement → 独立集成测试 → Review 热更新路径

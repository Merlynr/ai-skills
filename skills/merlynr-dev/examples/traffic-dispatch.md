# 案例摘要：Dispatch 流量分派模块

**规模**：9 文件 / 5880 行（含文档 ~2290）

**来源分支**：`perseus7-dev/-/tree/base-dpi-p7-2-add-disp-ring/dispatch`

## 模块拆分（流量分派型 Playbook）

| # | 模块 | 职责 | 典型文件 |
|---|------|------|----------|
| 1 | 规则引擎 | MSISDN/IPv4/IPv6 三表、区间合并、二分匹配、flow 缓存 | `dispatch-rule.c` (~1426) |
| 2 | 分派执行 | ring 创建、action、mbuf 生命周期、统计 | `tmodule-dispatch-ring.c` (~1525) |
| 3 | 命中信息输出 | 聚合、用户信息、流量统计 | `message-output-match-info.c` |
| 4 | 接收侧 | secondary 批量收包 | `tmodule-dispatch-recv.c` |
| 5 | 运维 CLI | 状态、规则更新、统计清理 | CLI 子命令 |
| 6 | 文档 | README、设计说明 | docs/ |

## 接口冻结要点

- 三表分离：MSISDN / IPv4 / IPv6 **不混用**
- action 与 mbuf：**drop / dispatch / mirror-ref / mirror-copy** 各自 ownership 规则
- 热更新：锁外构建新库 → 短写锁替换 → 锁外释放旧库

## 独立验证

```text
配置规则 → 注入匹配/非匹配流量 → 检查 ring 计数 → reload 规则 → mirror 高水位采样
```

## C2 必勾项

- [x] 热更新低阻塞
- [x] mbuf refcnt / free / drain
- [x] flow 缓存命中与性能
- [x] ring full / 非法规则边界

## 常见陷阱

- mirror-copy 与 refcnt 不一致导致 double-free
- 规则热更新期间读旧库指针无 barrier

## AI 分工建议（L 级）

冻结规则 API + action 所有权表 → 规则引擎与 ring 分模块实现 → 独立 subagent 压边界 → Review 热路径

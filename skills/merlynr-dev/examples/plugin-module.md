# 案例摘要：插件注册和管理模块

**规模**：24 文件 / 3858 行（C 13 + 头 3 + 文档 5 + 脚本/配置 3）

**来源分支**：`perseus7/-/tree/plugin`

## 模块拆分（插件型 Playbook）

| # | 模块 | 职责 | 典型符号/文件 |
|---|------|------|---------------|
| 1 | 统一插件 API | 注册入口、版本、事件枚举 | 插件头文件、注册宏 |
| 2 | 插件管理器 | 动态加载、启用/禁用、状态 | loader、runtime mgr |
| 3 | HTTP 事件回调 | 请求头/体、响应头/体、事务结束 | HTTP callback 表 |
| 4 | 事务状态 | 每 transaction 独立状态 | txn ctx |
| 5 | 告警/事件输出 | 插件 → 主程序输出通道 | alert sink |
| 6 | demo 插件 | HTTP/DNS/SNMP/SSH/stream 示例 | demo/ |
| 7 | 开发套件 | 打包脚本、文档、CLI | docs、Makefile |

## 接口冻结要点

- 插件 **不需要** 了解主程序全部内部；只依赖公开 API
- 生命周期：load → init → event callbacks → unload
- 错误码：加载失败 / 符号缺失 / 配置无效 分级

## 独立验证

```text
编译 demo 插件 → 放入插件目录 → CLI load/status → 触发 HTTP 事件 → 查看输出
```

## 常见陷阱

- 插件与主程序共享未文档化的全局状态
- 过早抽象「通用插件基类」；各 demo 协议差异大，宜独立

## AI 分工建议（L 级）

设计 → 接口 API → 分 demo 实现 → 独立测试加载路径 → Review 内存与 unload

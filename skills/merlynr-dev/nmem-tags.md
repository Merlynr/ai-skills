# G5：nmem 标签约定

M/L 任务收尾 `distill-memory` 时，可选以下标签便于 `search-memory` / `nmem m search`。

## 推荐标签

| 标签 | 何时打 |
|------|--------|
| `#interface-first` | 完成 M2.5 冻结或 D2 变更 lessons |
| `#no-abstract-yet` | A2 明确决定不抽象 |
| `#module-split` | 模块拆分 / Playbook 选型 |
| `#hot-reload` | 热更新 / 回滚相关 |
| `#system-validation` | C2 清单有实质结论 |
| `#agent-independence` | Review/test 独立 subagent 教训 |
| `#non-coding` | [non-coding-routes.md](non-coding-routes.md) 设计-only 任务 |
| `#grill-pro` | L 级需求澄清 breakthrough |
| `#playbook-plugin` | 插件型 |
| `#playbook-rule-engine` | 规则引擎型 |
| `#playbook-traffic-dispatch` | 流量分派型 |

## 写入示例

```bash
nmem m add -t "jxh-rule 热更新回滚：锁外构建失败路径" \
  -c "…" --tags interface-first,hot-reload,system-validation
```

或通过 `distill-memory` skill 引导，在内容首行加 `Tags: #… #…`。

## 与 merlynr-handoff.json

Handoff 中 `nmem_tags` 数组 → 沉淀时 **原样复用**，保持任务与记忆可关联。

## 与 Phase 4.5 的分工

| 载体 | 内容 |
|------|------|
| 模块 `AGENTS.md` | 本仓库 SSOT、可提交 |
| nmem | 跨项目习惯、个人 breakthrough、可搜索 |

同一结论 **可以** 两边都写：AGENTS 写模块事实，nmem 写「为什么这样选」。

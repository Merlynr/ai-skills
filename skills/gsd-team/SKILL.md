---
name: "gsd-team"
description: "根据任务描述生成 GSD 团队配置，自动匹配相关 skills 并在 OpenCode 中执行"
tags: [team, orchestration, workflow, collaboration]
triggers: ["组建团队", "生成 team", "多人协作", "团队", "team"]
tool_chain: ["gsd-execute-phase", "gsd-verify-work"]
context_injection: true
metadata:
  short-description: "Generate and execute GSD team configurations with skill awareness"
---

# GSD Team Engine (Skill-Aware)

根据任务描述自动生成 GSD 团队配置，**自动匹配相关 skills**，并在 OpenCode 中执行。

## 核心特性

- **意图识别** - 自动分析任务意图，匹配最合适的 Skills
- **动态加载** - 根据任务阶段动态加载对应 Skills
- **工具链串联** - 自动组合 Skills 的工具链
- **反馈循环** - 记录执行结果，持续优化 Skills

## 使用方式

当用户需要为复杂任务组建 AI 团队时使用此 skill。

### 触发条件

- 用户说"组建团队"、"生成 team"、"多人协作"
- 用户描述了一个需要多阶段完成的复杂任务
- 用户想要并行执行多个 agent

### 输入格式

```
$gsd-team 任务描述
```

示例：
- `$gsd-team 实现用户认证系统`
- `$gsd-team 重构数据库层，需要支持 IPv6`
- `$gsd-team 修复登录 bug 并添加单元测试`

## 执行流程

### Step 1: 解析任务

从用户输入中提取任务描述。如果没有提供，询问用户：

```
请描述需要完成的任务：
```

### Step 2: 意图识别

使用 `gsd-team-engine.py` 进行意图分析：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py --analyze "任务描述"
```

### Step 3: 动态加载 Skills

引擎会根据意图自动加载 Skills：

1. **触发词匹配** - 权重 3.0（最高）
2. **标签匹配** - 权重 2.0
3. **关键词匹配** - 权重 1.0

### Step 4: 生成团队配置

运行引擎生成配置：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --commands
```

### Step 5: 执行团队任务

如果用户确认，按阶段执行，每个成员都会使用分配的 skills。

### Step 6: 记录学习

任务完成后，记录学习：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py --learn "任务描述" --result success --learnings "学到的经验"
```

## 相关命令

```bash
# 分析任务意图
python3 ~/.config/skillshare/script/gsd-team-engine.py --analyze "任务描述"

# 生成团队配置
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --commands

# 记录学习
python3 ~/.config/skillshare/script/gsd-team-engine.py --learn "任务描述" --result success --learnings "经验"
```

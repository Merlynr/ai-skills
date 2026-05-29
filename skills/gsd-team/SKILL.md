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
- **nmem 同步** - 自动同步任务结果到 Nowledge Mem

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

### Step 6: 记录学习并同步到 nmem

任务完成后，记录学习并同步到 nmem：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py --learn "任务描述" --result success --learnings "学到的经验"
```

这会：
1. 保存学习记录到本地 `learnings/` 目录
2. 创建 nmem 线程记录任务详情
3. 将重要学习提炼为 nmem 记忆

### Step 7: 同步任务到 nmem

如果需要提前将任务同步到 nmem：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --sync-nmem
```

## nmem 集成

### 自动同步

当使用 `--learn` 命令时，引擎会自动：

1. **创建线程** - 记录任务详情、团队配置、使用的 Skills
2. **提炼记忆** - 将成功的学习内容提炼为结构化记忆
3. **保存标签** - 使用 `team-task`、`success` 等标签便于检索

### 手动同步

使用 `--sync-nmem` 命令提前同步任务：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --sync-nmem
```

### nmem 数据结构

#### 线程内容

```markdown
## 任务: {task}

**结果**: {result}
**时间**: {timestamp}

## 团队配置
- 引擎: skill-aware
- 成员数: {members_count}
- 主要意图: {primary_skill}

## 使用的 Skills
- 架构师: gsd-discuss-phase, gsd-spec-phase, gsd-plan-phase
- 研究员: gsd-map-codebase, gsd-explore
- 实现者: gsd-execute-phase, gsd-fast
- 审查者: gsd-code-review, gsd-validate-phase

## 学习记录
{learnings}
```

#### 记忆标签

- `team-task` - 团队任务
- `success` - 成功任务
- `{skill-name}` - 使用的 Skills

## 相关命令

```bash
# 分析任务意图
python3 ~/.config/skillshare/script/gsd-team-engine.py --analyze "任务描述"

# 生成团队配置
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --commands

# 记录学习并同步到 nmem
python3 ~/.config/skillshare/script/gsd-team-engine.py --learn "任务描述" --result success --learnings "经验"

# 同步任务到 nmem
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --sync-nmem
```

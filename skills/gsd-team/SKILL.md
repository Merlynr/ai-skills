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

### Step 5: 用户确认

向用户展示团队配置，等待确认：

```
======================================================================
  团队: task-team
  任务: 实现用户认证系统...
  引擎: skill-aware
  主要意图: gsd-execute-phase
======================================================================

  成员配置:
----------------------------------------------------------------------
  1. architect (架构师) - plan 阶段
  2. researcher (研究员) - plan 阶段
  3. implementer (实现者) - implement 阶段
  4. reviewer (审查者) - verify 阶段
----------------------------------------------------------------------

是否执行？(y/n)
```

### Step 6: 自动执行团队任务

用户确认后，**按阶段自动执行**：

#### 6.1 Plan 阶段（并行执行）

```python
# 架构师 - 分析需求
task(subagent_type="oracle", load_skills=["gsd-discuss-phase", "gsd-spec-phase", "gsd-plan-phase"], 
     run_in_background=true, prompt="分析任务需求，设计系统架构：任务描述")

# 研究员 - 探索代码（并行）
task(subagent_type="explore", load_skills=["gsd-map-codebase", "gsd-explore"], 
     run_in_background=true, prompt="探索代码库，查找相关模式：任务描述")
```

等待 Plan 阶段完成...

#### 6.2 Implement 阶段

```python
# 实现者 - 编写代码
task(category="unspecified-high", load_skills=["gsd-execute-phase", "gsd-fast"], 
     run_in_background=true, prompt="实现功能：任务描述")
```

等待 Implement 阶段完成...

#### 6.3 Verify 阶段

```python
# 审查者 - 代码审查
task(subagent_type="oracle", load_skills=["gsd-code-review", "gsd-validate-phase"], 
     run_in_background=true, prompt="审查代码质量：任务描述")
```

等待 Verify 阶段完成...

### Step 7: 记录学习并同步到 nmem

任务完成后，自动记录学习并同步到 nmem：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py --learn "任务描述" --result success --learnings "学到的经验"
```

这会：
1. 保存学习记录到本地 `learnings/` 目录
2. 创建 nmem 线程记录任务详情
3. 将重要学习提炼为 nmem 记忆

### Step 8: 同步任务到 nmem

如果需要提前将任务同步到 nmem：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --sync-nmem
```

## 自动执行流程图

```
用户请求
    ↓
意图分析
    ↓
生成团队配置
    ↓
用户确认 (y/n)
    ↓
┌─────────────────────────────────────────────────┐
│  Plan 阶段（并行）                                │
│  ├─ architect: 需求分析                          │
│  └─ researcher: 代码探索                         │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│  Implement 阶段                                  │
│  └─ implementer: 编写代码                        │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│  Verify 阶段                                     │
│  └─ reviewer: 代码审查                           │
└─────────────────────────────────────────────────┘
    ↓
记录学习 + nmem 同步
```

## 执行模式

### 模式 1: 完全自动执行（推荐）

```bash
# 生成配置并自动执行
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --execute
```

用户确认后，自动按阶段执行所有任务。

### 模式 2: 分步执行

```bash
# 生成配置
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --commands

# 手动复制执行命令
```

### 模式 3: 仅生成配置

```bash
# 仅生成配置，不执行
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --generate
```

## 注意事项

1. **并行执行** - Plan 阶段的成员可以并行执行
2. **阶段依赖** - Implement 依赖 Plan 的结果，Verify 依赖 Implement 的结果
3. **资源限制** - 最多同时运行 4 个 agent（可在 oh-my-openagent.jsonc 中配置）
4. **用户确认** - 自动执行前需要用户确认
5. **错误处理** - 如果某个阶段失败，会记录错误并继续执行其他阶段

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

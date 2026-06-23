---
disable-model-invocation: true
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

### 任务分级（S / M / L）

与 Merlynr Dev Stack 一致。**gsd-team 仅用于 L 级**；收到任务后先分级，再决定是否继续：

| 级别 | 信号 | 应走的路径 |
|------|------|------------|
| **S** 琐碎 | 单文件、符号明确、一处/一行修复 | **停止本 skill** → 直接改或 `gsd-fast` |
| **M** 中等 | 2–5 文件、边界清楚 | **默认不用 team** → 本地探库 + `gsd-quick`；仅当用户明确「组建团队」时才继续 |
| **L** 复杂 | 新功能、重构、多模块、验收模糊 | **继续 gsd-team**（完整 Plan → Implement → Verify） |

分级后若判定为 S 或 M（且用户未明确要求组团队），回复用户推荐路径并**不要**运行 `--execute`。

### 触发条件

- 用户说"组建团队"、"生成 team"、"多人协作"
- **L 级**复杂任务（见上表）
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

### Step 1: 解析任务与分级

从用户输入中提取任务描述，并按 **S / M / L** 分级（见上文表格）。如果没有提供，询问用户：

```
请描述需要完成的任务：
```

若判定为 **S** → 建议 `gsd-fast`；**M** 且未要求组团队 → 建议 `gsd-quick` + Cymbal/Grep；仅 **L**（或用户 insist team）进入 Step 2。

### Step 2: 意图识别（必须向用户展示）

运行引擎并**把完整终端输出贴给用户**（含主要意图、置信度/回退说明、Top 匹配 skills）：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py --analyze "任务描述"
```

### Step 2.5: Phase 0 Cymbal 研判（L 级推荐，非全量罗列）

在生成团队之前，用 **Cymbal 嗅探**任务相关的模块与接口，再结合 skill 短名单形成 **Team Brief**。  
**禁止**把全库模块/接口/skill 列表直接喂给 AI。

```bash
# 在项目仓库根目录执行（或 --repo 指定路径）
cd /path/to/your-project
python3 ~/.config/skillshare/script/gsd-team-engine.py --triage --repo . "重构 team 引擎意图识别"

# 保存 Brief 供确认
python3 ~/.config/skillshare/script/gsd-team-engine.py --triage "任务描述" --brief-out team-brief.json
```

Brief 包含：
- **需求要点**（从任务拆分）
- **Cymbal 检索词** → **相关模块**（目录级，≤8）→ **相关接口/符号**（≤12）
- **Skill 短名单**（意图引擎 Top N，非全库）
- **triage-lead prompt**（给研判负责人，基于 Brief 安排成员与 skills）
- **persist_*（写回约定，triage-lead 填写）** → 交给 Merlynr Phase 4.5 执行

#### Brief 写回与裁减字段（引擎自动推导，可覆写）

Team Brief（`team-brief.json`）字段：

```json
{
  "dispatch_hints": {
    "skip_roles": ["implementer", "architect"],
    "include_debug": true,
    "scope_summary": "modules/ISMS/flowcollect/",
    "merlynr_handoff": ".planning/merlynr-handoff.json",
    "required_roles": ["architect", "implementer", "reviewer"],
    "manual_subagents": [
      {
        "name": "interface-designer",
        "role": "接口设计",
        "phase": "plan",
        "prompt": "冻结 INTERFACE.md，不写实现",
        "skills": ["merlynr-dev"]
      },
      {
        "name": "tester",
        "role": "独立测试",
        "phase": "verify",
        "prompt": "依据 Handoff/SPEC 写测试，不依赖 implementer 解释",
        "skills": ["gsd-add-tests", "merlynr-dev"]
      }
    ]
  },
  "persist_target": "modules/ISMS/flowcollect/AGENTS.md",
  "persist_grade": "L",
  "persist_sections": ["Recent Changes", "Performance Notes", "Decisions", "Open Questions"]
}
```

| 字段 | 说明 |
|------|------|
| `dispatch_hints.skip_roles` | 生成团队时**不创建**的成员（见下表） |
| `dispatch_hints.required_roles` | 文档约定；与 skip 冲突时 triage-lead 须调整 |
| `dispatch_hints.manual_subagents` | **v2**：额外成员（接口/测试等）；见 [merlynr-dev/handoff-schema.md](../merlynr-dev/handoff-schema.md) |
| `dispatch_hints.merlynr_handoff` | 可选，指向 merlynr-handoff.json |
| `persist_target` | 主模块 `AGENTS.md`；默认由 `evidence.modules[0]` 推导 |
| `persist_grade` | `M` 或 `L` |
| `persist_sections` | Phase 4.5 写回章节 |

**可 skip 的角色名**（与 `generate_team()` 一致）：

`architect` | `researcher` | `implementer` | `reviewer` | `debugger` | `ui-reviewer`

（`triage-lead` 不会被 skip）

**引擎默认规则**（可在 JSON 中覆写）：

| 任务类型 | 默认 `skip_roles` |
|----------|-------------------|
| 性能/排查且无代码改动意图 | `implementer`；常含 `architect` |
| 文档类且无实现意图 | `implementer`, `debugger` |
| 无 UI 信号 | `ui-reviewer` |

`--from-brief` 生成团队时，`generate_team()` 读取 `skip_roles` 并调整 `workflow.phases`。

triage-lead 研判输出末尾应包含：

```markdown
## Persist（Phase 4.5）
- target: modules/.../AGENTS.md
- grade: M | L
- sections: Recent Changes, ...
- 禁止写入: 未验证推测、整段对话
```

用户确认 Brief 后，再生成团队：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py --from-brief team-brief.json --commands
```

或一步完成（嗅探 + 生成）：

```bash
python3 ~/.config/skillshare/script/gsd-team-engine.py --triage --repo . "任务描述" --commands
```

**Phase 0 成员 `triage-lead`**：读取 Brief + skill 短名单，输出最终分工（不再全库扫描）。  
**研究员**在 Brief 存在时改为 **缺口验证**（仅对 Brief 未覆盖符号做精确 Cymbal 命令）。

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

向用户展示 **两段内容**（均来自引擎输出，不要省略意图分析）：

1. **意图分析**（Step 2 的 `--analyze` 输出，或生成命令自带的第一段）
2. **团队配置摘要**（成员、各阶段匹配的 skills）

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
  ...
----------------------------------------------------------------------

是否执行？(y/n)
```

生成完整配置（含意图分析 + 团队摘要）：

```bash
python "%APPDATA%\skillshare\script\gsd-team-engine.py" "任务描述"
```

### Step 6: 自动执行团队任务

用户确认后，**按阶段自动执行**：

#### 6.1 Plan 阶段（并行执行）

```python
# 架构师 - 分析需求
task(subagent_type="oracle", load_skills=["gsd-discuss-phase", "gsd-spec-phase", "gsd-plan-phase"], 
     run_in_background=true, prompt="分析任务需求，设计系统架构：任务描述")

# 研究员 - 探索代码（并行；Phase 1 必须 Cymbal + .planning）
task(subagent_type="explore", load_skills=["gsd-map-codebase", "gsd-explore", "merlynr-dev-stack"],
     run_in_background=true, prompt="""探索代码库，查找相关模式：任务描述

Phase 1 探库（L 级）：
1. 若 Cymbal 未就绪：rtk cymbal index .
2. 已知符号：rtk cymbal investigate <symbol>；改前：rtk cymbal refs <symbol>
3. 语义/影响面 → Cymbal；字面量/配置 → rg
4. 架构边界 → .planning/codebase/ 与 AGENTS.md
""")
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

### Step 7.5: 模块 agent 写回（M/L，Merlynr Phase 4.5）

团队任务结束且结论**已验证**后：

1. 读取 Brief 的 `persist_target` / `persist_grade` / `persist_sections`（或 triage-lead 的 Persist 块）
2. 按 **merlynr-dev-stack Phase 4.5** 追加到模块 `AGENTS.md`（不覆盖「维护注意点」等稳定章节）
3. 单独 `git commit` 文档变更（若用户在版本库中工作）

**性能排查类 L 任务**示例：写 `## Performance Notes` + `FlowCollectDoTaskRun` 等符号级结论，勿把 Brief 全文粘贴进 AGENTS。

若 Brief 未填 `persist_target`：用 `evidence.modules[0]` 推导，例如 `modules/ISMS/flowcollect/` → `modules/ISMS/flowcollect/AGENTS.md`。

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
    ↓
模块 AGENTS 写回（Step 7.5 / Merlynr Phase 4.5）
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

## 与 Merlynr Dev Stack 的关系

| 问题 | 答案 |
|------|------|
| 谁先谁后？ | 开任务先 **merlynr-dev-stack** 分级；L 级 Phase 3 才进 **gsd-team** |
| 谁写模块 AGENTS？ | **merlynr Phase 4.5** 定规范；gsd-team Brief 只标 `persist_target` |
| M 级用 team 吗？ | 默认否；用 merlynr + `gsd-quick`；组 team 时仍走 Step 7.5 写回 |
| Agent 独立性？ | triage-lead 按 [merlynr-dev/agent-roles.md](../merlynr-dev/agent-roles.md) 安排；接口/测试用 manual subagent |

详见 [merlynr-dev-stack/SKILL.md](../merlynr-dev-stack/SKILL.md)、[merlynr-dev/SKILL.md](../merlynr-dev/SKILL.md)。

## 注意事项

1. **仅 L 级** - S/M 任务勿组 team；M 级默认 `gsd-quick`
2. **Plan 探库** - researcher 必须按 Phase 1 走 Cymbal（见 Step 6.1），与 `opencode_smart` 注入的 AGENTS.md 一致
3. **并行执行** - Plan 阶段的成员可以并行执行
4. **阶段依赖** - Implement 依赖 Plan 的结果，Verify 依赖 Implement 的结果
5. **资源限制** - 最多同时运行 4 个 agent（OpenCode 并发配置）
6. **用户确认** - 自动执行前需要用户确认
7. **错误处理** - 如果某个阶段失败，会记录错误并继续执行其他阶段

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
# 仅意图分析（Step 2）
python "%APPDATA%\skillshare\script\gsd-team-engine.py" --analyze "任务描述"

# 意图分析 + 团队配置 + 保存 JSON（推荐，一次看完）
python "%APPDATA%\skillshare\script\gsd-team-engine.py" "任务描述"

# 生成 OpenCode 命令
python "%APPDATA%\skillshare\script\gsd-team-engine.py" "任务描述" --commands

# 记录学习并同步到 nmem
python3 ~/.config/skillshare/script/gsd-team-engine.py --learn "任务描述" --result success --learnings "经验"

# 同步任务到 nmem
python3 ~/.config/skillshare/script/gsd-team-engine.py "任务描述" --sync-nmem
```

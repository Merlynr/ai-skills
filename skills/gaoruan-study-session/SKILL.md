---
name: gaoruan-study-session
description: Runs a 高软/系统架构师 daily study session in the Obsidian vault—opens today's study record, logs wrong answers with screenshots, classifies error types, syncs plan status, and writes a UTF-8-safe Nowledge Mem (nmem) briefing on completion. Use when the user mentions 高软、系统架构师、软考刷题、错题整理、高软学习计划、nmem简报、或发高软题目截图/说今日高软完成。
tags: [study, exam, 高软, 系统架构师, 错题, 软考]
triggers: ["高软", "系统架构师", "软考", "刷题", "错题", "错题整理", "学习计划"]
tool_chain: ["gsd-progress", "gsd-capture"]
context_injection: true
---

# 高软学习会话

## 用户要求（须遵守）

1. **开启会话**：用户说开启今天高软学习计划时，创建/打开当日学习记录，说明错题发送方式，并链到当日日计划与阶段计划。
2. **每道错题**：记录题目**全部内容**（题干、选项、你的答案、正确答案、解析）；并把这题的**错因类型**归纳进学习记录的「错因归类」表。
3. **截图必存**：用户发的题目图片必须复制到笔记库 `assets` 目录，并在学习记录中用 Obsidian 嵌入 `![[assets/...]]`，否则后期无法理解。
4. **会话结束**：用户说今日高软学习完成时，同步相关计划状态（日计划勾选、阶段计划批次、学习记录 completed），并 **写入 Nowledge Mem 简报**（须 UTF-8，避免中文乱码）。

## 路径约定（vault 根目录）

| 用途 | 路径 |
| --- | --- |
| 日计划 | `10 Daily/YYYY-MM-DD.md` |
| 阶段计划 | `20 Projects/高软-系统架构师/00 计划/系统架构师二战学习计划.md` |
| 当日学习记录 | `20 Projects/高软-系统架构师/03 错题/YYYY-MM-DD 高软学习记录.md` |
| 题目截图 | `20 Projects/高软-系统架构师/03 错题/assets/YYYY-MM-DD/第N题-简述.png` |
| 项目入口 | `20 Projects/高软-系统架构师/高软-系统架构师.md` |

日期默认 **Asia/Shanghai** 当天。

## 工作流

### A. 开启会话

1. 读 `系统架构师二战学习计划.md` 的 **当前进度指针**（章节、小节、当前批）。
2. 读 `10 Daily/YYYY-MM-DD.md` 中高软 Carry-over/今日计划项。
3. 若不存在则创建 `03 错题/YYYY-MM-DD 高软学习记录.md`（结构见 [template.md](template.md)）。
4. 在当日日计划 `## Notes` 增加一行链到学习记录。
5. 告知用户：可发错题（文字或截图）；建议含题号、选项、你的答案、标准答案、来源。

### B. 处理每道错题

```
- [ ] 复制截图 → assets/YYYY-MM-DD/第N题-简述.png
- [ ] 在学习记录「错题条目」追加完整条目（含 ![[assets/...]]）
- [ ] 更新「刷题记录」表一行
- [ ] 更新「错因归类」表（新类型追加，已有类型补题号）
- [ ] 更新进度表（错题数、状态）
```

**单题条目结构**（参照 `2026-05-21 高软学习记录`）：

- `## 第N题（章节 · 考点）` + 配图
- 题目 / 选项（标你的选择）/ 答案
- 解题思路（分步，含你错在哪）
- 相关内容（表格、对比、公式）
- 记忆点（短句口诀）

**巩固题**（做对且值得留档）：写入「刷题巩固」小节，可略简，仍要配图。

### C. 结束会话并同步计划

```
- [ ] Obsidian：学习记录 completed + 计划勾选（见下）
- [ ] nmem：写入简报并验证中文无乱码
```

1. **学习记录**：`status: completed`；今日目标全部 `[x]`；进度表状态「已完成」；今日小结写薄弱点 + 明天优先（下一批任务）。
2. **二战学习计划**：勾选已完成批次（如 `第1批 ~15题 📅 YYYY-MM-DD`）；更新指针为「上次完成 / 下一批」。
3. **日计划**：Focus 标完成；Carry-over 中高软项 `[x]`；Review 写一句复盘 + 链学习记录。
4. **项目页** `高软-系统架构师.md`：酌情更新「本周关注」（如错题已入本）。

若存在 `系统架构师五战学习计划.md` 且与二战进度镜像，**同步勾选**，避免两套计划不一致。

5. **执行 D. 写入 Nowledge Mem 简报**（用户未说「不要 nmem」时默认执行）。

### D. 写入 Nowledge Mem 简报（必做，防乱码）

从当日 `YYYY-MM-DD 高软学习记录.md` 提炼内容，写入 nmem。结构模板：[nmem-briefing-template.md](nmem-briefing-template.md)。

#### 简报字段

| 区块 | 来源 |
| --- | --- |
| 完成情况 | 计划指针、今日批次、题号范围 |
| 成绩 | 「刷题记录」表：错题 ✗ / 巩固 ✓ |
| 薄弱点 | 「错因归类」+ 今日小结 |
| 明日 | 阶段计划「下一批」 |
| 关联 | 前一日学习记录链、本 Skill 路径 |

#### 写入步骤（严格顺序）

1. **生成 UTF-8 文件**（无 BOM）  
   路径：`.cursor/skills/gaoruan-study-session/nmem-briefing-YYYY-MM-DD.md`  
   用 Write 工具写入，或 `[System.IO.File]::WriteAllText($path, $body, [System.Text.UTF8Encoding]::new($false))`。

2. **写入 nmem（二选一，均须 UTF-8）**

   **首选 — MCP**（避免 Windows 管道乱码）：
   - `memory_add` 或 `memory_update`
   - `memory_id` / `id`：`gaoruan-study-YYYY-MM-DD`（同日 upsert）
   - `title`：`高软学习简报 YYYY-MM-DD （章节·第N批）`
   - `content`：简报全文（从步骤 1 文件读取）
   - `labels`：`gaoruan,study,soft-exam`
   - `importance`：`0.7`
   - `event_start`：`YYYY-MM-DD`

   **备选 — CLI**（仅当 MCP 不可用时）：
   ```powershell
   $c = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
   nmem --json m update gaoruan-study-YYYY-MM-DD -t "标题" -c $c -i 0.7
   ```
   可选摘要线程：`nmem t create -t "高软简报 YYYY-MM-DD" -c "一段纯文本摘要" -s cursor-agent`

3. **禁止**（会导致手机端 `????` 乱码）：
   - `$text | nmem m add --stdin`
   - `Get-Content ... | nmem m add --stdin`（未指定 UTF-8 时）
   - 把超长正文只放在 shell 参数里且控制台代码页非 UTF-8

4. **验证**：`nmem m show gaoruan-study-YYYY-MM-DD`，确认 `content` 中中文正常（非 `?` 占位）。

5. **告知用户**：记忆 ID、标题；提醒在 Nowledge Mem **下拉刷新** 查看。

#### 乱码原因（备忘）

PowerShell 管道默认编码非 UTF-8 → 中文经 `--stdin` 进 nmem 已损坏；**标题参数**常仍正常，故表现为「标题对、正文乱码」。

## 节奏与计划原则

- 默认 **15 题/工作日、约 45 分钟**（见二战学习计划）；按 **批次** 勾选，不要求一天整章。
- 小节内多批（如操作系统 66 题分 5 批）时，只勾当前批，父级「操作系统」等全部批完成后再勾。

## 领域速查（错题归类时常用）

| 考点 | 要点 |
| --- | --- |
| 计数信号量 | 初值 = 资源数 N；范围 N → -(n-N)；S<0 时等待数=\|S\| |
| 段式地址 | 合法当 0 ≤ 段内地址 < 段长；越界 d ≥ 段长 |
| 页式地址 | 只换页框号，**页内偏移照抄** |
| 同步/互斥 | 等消息/条件=同步；抢临界区=互斥；调度≠制约关系 |
| 线程 | 共享进程资源；**栈/栈指针不共享** |
| 磁盘 SSTF | 先柱面最近，**同柱面按扇区升序**；磁头号通常不参与排序 |
| 实时/嵌入式 | 外部事件须在**被控对象允许时间内**；内核接口=API；嵌入式特点≠通用性 |

## 附加资源

- 学习记录模板：[template.md](template.md)
- nmem 简报模板：[nmem-briefing-template.md](nmem-briefing-template.md)

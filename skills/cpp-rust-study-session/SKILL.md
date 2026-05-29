---
name: cpp-rust-study-session
description: Runs C++ or Rust study sessions in the Obsidian vault—session open, Q&A with optional contrast notes, detailed Q&A notes on request, plan sync, Dataview-safe markdown. Use when the user mentions C++学习、Rust学习、studycpp、今日C++/Rust、疑难点、第N章学完、开启/完成今天 C++ 或 Rust 学习计划。
---

# C++ / Rust 学习会话

## 用户要求（须遵守）

1. **开启会话**：用户说开启今天 C++（或 Rust）学习计划时，确认语言、章节/Day，链到总计划与日计划；说明可随时发疑难点、逐条解答。
2. **学习中答疑**：对用户疑难点讲清原理，必要时最小示例；计划要求时可做 **C++ ↔ Rust 对比**。
3. **会话结束**：用户说今日学习完成或要总结时——写学习笔记并同步计划（见下方笔记规范）。

用户原话（会话模式）：

> 开启今天C++学习计划，接下来我会对于相关疑难点发给你，你要进行解答，同时，在最后完成今天学习任务时你再进行总结归纳

> 你只需要总结我的提问和你的解答内容即可，不需要扩展

> 相关的答疑要详细一些，最好将你的回答完整有逻辑的梳理进去

**解读**：

- 笔记默认 = **本次提问 + 完整解答梳理**，不写教材章节复述、工具链百科等**未问内容**。
- 用户要求「详细」时：每条 Q 下用分级小节（原理 → 例子 → 对照表 → 结论），逻辑完整，但仍不擅自加无关章节扩展。
- Rust 学习 **复用本 skill**，仅换教材与 Day 11–20 进度。

## 路径约定（vault 根目录）

| 用途 | 路径 |
| --- | --- |
| 总计划 | `20 Projects/C++与Rust学习/C++与Rust 20天学习计划.md` |
| 学习笔记 | `20 Projects/C++与Rust学习/学习笔记/YYYY-MM-DD {C++\|Rust} 学习答疑记录.md` |
| 日计划 | `10 Daily/YYYY-MM-DD.md` |

日期默认 **Asia/Shanghai** 当天。

## 教材与 Day 划分

| 语言 | 资源 | 计划 |
| --- | --- | --- |
| C++ | [studycpp.cn](https://www.studycpp.cn/) | Day 1–10，第 0–18 章 + 练手 |
| Rust | [The Rust Book](https://doc.rust-lang.org/book/) | Day 11–20，所有权/借用/并发等 |

对比学习（用户要求）：内存 RAII/智能指针 vs 所有权/借用；异常 vs `Result`/`Option`；虚类/接口 vs Traits。

## 工作流

### A. 开启会话

1. 读总计划当前 Day、章节勾选；读当日 `10 Daily` Carry-over。
2. 确认 **C++** 或 **Rust**。
3. 告知用户：可发章节号、疑惑、代码、报错；建议附带自己的理解；结束时说「今天学完了」或「写学习笔记/总结」。

### B. 答疑（对话中）

```
- [ ] 先结论，再原理；易混点拆开讲（如 返回值 vs 结合性）
- [ ] 表格/代码块/流程图按需使用
- [ ] 不堆砌未问及的进阶内容
- [ ] 对比另一语言仅在有助理解或用户计划相关时
- [ ] 写入 Obsidian 前遵守 Dataview 规则（见下）
```

### C. 写学习笔记

1. 用 [template.md](template.md)；文件名含日期与语言。
2. 结构：**仅 Q1/Q2/…**，每条含用户问题原文（可略压缩）+ **完整解答**（分节、表格、代码块均可）。
3. 文末简短 **进度备忘**（章节 ✅/⏳）即可，不写整章要点除非用户明确要求。
4. 同步总计划勾选、日计划 `Review`/`Carry-over`。
5. 可选 `memory_add`（labels: `cpp` 或 `rust`, `learning-plan`, `study-progress`）。

### D. 计划节奏

- 日历可顺延；理解优先；章末 quiz 后再勾章节。
- 参考 3–4h/天（阅读 40% + 实践 60%）。

## Obsidian Dataview（写笔记必查）

Dataview 把行内 `` `=` `` 当作**内联 DQL**，会显示 `PARSING FAILED`。

| 禁止 | 改用 |
| --- | --- |
| `` `=` `` | 等号、**=**、或 `` ` x = y ` ``（等号前有空格/标识符） |
| 表格单元格单独 `` `=` `` | 写「赋值 =」或放代码块 |
| `` `===` `` 等 | 放 ` ``` ` 代码块 |

完整 C++ 语句一律用 **fenced `cpp` 代码块**。更多见 [reference.md](reference.md)。

## 本次会话已验证的答疑主题（可扩展）

| 主题 | 易混点 |
| --- | --- |
| 拷贝初始化 | 效率 vs C++17 省略；`initializer_list`；≠ 凡带等号都慢 |
| I/O 缓冲 | 库缓冲 vs 内核 page cache；行/全/无缓冲 |
| `=` 与 `<<` | 都返回左操作数；**结合性相反**（右 vs 左） |

## 附加资源

- 笔记模板：[template.md](template.md)
- Dataview 与笔记示例：[reference.md](reference.md)

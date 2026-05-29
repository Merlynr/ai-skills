# C++/Rust 学习笔记 — Dataview 与格式参考

## 为何会报错

Obsidian **Dataview** 默认 **Inline Query Prefix** 为 `=`。行内代码若以 `=` 开头，例如：

```markdown
表面只差一个 `=`，但编译器…
```

会被当作 `` `= …` `` 内联查询解析，失败时出现：

```text
Dataview (inline field …): Error: PARSING FAILED
Got the end of the input
```

## 安全写法

```markdown
✅ 表面只差一个**等号**（写法上多一个 ` x = expr `）
✅ 赋值运算符 **=** 是右结合
✅ 完整语句放在 cpp 代码块里

❌ 单独 `=`
❌ 表格里 | `=` | 单独一格
```

**全局规避**（可选）：设置 → Dataview → Inline Query Prefix 改为 `dv:`。

## 笔记篇幅

| 用户说 | 笔记内容 |
| --- | --- |
| 总结 / 学习笔记 | 仅 Q&A，不扩展未问章节 |
| 详细 / 完整梳理 | 每条 Q 下多级小节，逻辑完整，仍不加无关章节百科 |

## 答疑记录示例结构

```markdown
## Q1：拷贝初始化为何效率低？

### 1.1 什么叫拷贝初始化
（定义 + 对比表）

### 1.2 效率低的原理
（分点 + 代码块）

### 1.5 一句话结论
```

## 与 gaoruan-study-session 的区别

| | 高软 | C++/Rust |
| --- | --- | --- |
| 产物 | 错题 + 截图 | 答疑 Q&A |
| 计划 | 系统架构师二战 | 20 天 C++/Rust |
| 特殊 | assets 截图 | Dataview 等号 |

---
name: unified-learning-session
description: 统一学习会话管理 - 支持高软、C++、Rust 等多种学习类型，自动创建 Obsidian vault，集成 nmem 统计和简报生成
tags: [study, learning, 高软, cpp, rust, 统一学习, 会话管理]
triggers: ["学习", "开启学习", "学习计划", "今日学习", "学习完成", "学习总结"]
tool_chain: ["gsd-progress", "gsd-capture", "gsd-docs-update"]
context_injection: true
metadata:
  short-description: "Unified learning session management with Obsidian vault and nmem integration"
---

# 统一学习会话管理

## 核心特性

- **多学习类型** - 支持高软、C++、Rust 等多种学习
- **自动创建** - 自动创建 Obsidian vault 目录结构
- **nmem 集成** - 实时统计、学习记录、简报生成
- **智能汇总** - 基于提问和 nmem 数据生成学习汇总
- **计划同步** - 同步本地计划和 nmem 统计

## 支持的学习类型

| 类型 | 触发词 | 技能 |
|------|--------|------|
| 高软学习 | 高软、系统架构师、软考 | gaoruan-study-session |
| C++ 学习 | C++、studycpp | cpp-rust-study-session |
| Rust 学习 | Rust、rust | cpp-rust-study-session |
| 通用学习 | 学习、学习计划 | 本 skill |

## 工作流

### Phase 1: 初始化学习环境

#### 1.1 检测学习类型

```python
# 根据用户输入判断学习类型
if "高软" in user_input or "系统架构师" in user_input:
    learning_type = "gaoruan"
elif "C++" in user_input or "cpp" in user_input:
    learning_type = "cpp"
elif "Rust" in user_input:
    learning_type = "rust"
else:
    learning_type = "general"
```

#### 1.2 检查 Obsidian vault

```bash
# 检查 vault 是否存在
if [ ! -d "$HOME/obsidian-vault" ]; then
    # 创建 vault 目录结构
    mkdir -p "$HOME/obsidian-vault/10 Daily"
    mkdir -p "$HOME/obsidian-vault/20 Projects"
    mkdir -p "$HOME/obsidian-vault/assets"
fi
```

#### 1.3 创建学习计划（如果不存在）

**高软学习计划**:
```markdown
# 系统架构师学习计划

## 当前进度
- 章节: [当前章节]
- 小节: [当前小节]
- 批次: [当前批次]

## 学习记录
- 日期: YYYY-MM-DD
- 状态: 进行中
```

**C++/Rust 学习计划**:
```markdown
# C++/Rust 20天学习计划

## 当前进度
- Day: [当前Day]
- 语言: C++ / Rust
- 章节: [当前章节]

## 学习记录
- 日期: YYYY-MM-DD
- 状态: 进行中
```

### Phase 2: 开启学习会话

#### 2.1 读取学习计划

```bash
# 读取本地计划
cat "$vault_path/20 Projects/$learning_type/学习计划.md"

# 查询 nmem 统计
nmem m search "学习计划" -l $learning_type -n 10
```

#### 2.2 创建当日学习记录

```markdown
# YYYY-MM-DD 学习记录

## 基本信息
- 日期: YYYY-MM-DD
- 学习类型: [高软/C++/Rust]
- 计划内容: [今日计划]

## 学习内容
[待填写]

## 疑难点/错题
[待填写]

## 学习总结
[待填写]
```

#### 2.3 同步日计划

```markdown
# 10 Daily/YYYY-MM-DD.md

## 学习计划
- [ ] [学习类型] 学习任务

## Notes
- 学习记录: [[20 Projects/$learning_type/学习记录/YYYY-MM-DD 学习记录.md]]
```

### Phase 3: 学习过程

#### 3.1 高软学习模式

```markdown
## 错题记录

### 第N题（章节 · 考点）
- 题目: [题目内容]
- 选项: [选项]
- 你的答案: [答案]
- 正确答案: [答案]
- 解析: [解析]
- 错因类型: [类型]

## 错因归类
| 类型 | 题号 |
|------|------|
| 概念混淆 | 1, 3, 5 |
| 计算错误 | 2, 4 |
```

#### 3.2 C++/Rust 学习模式

```markdown
## 答疑记录

### Q1: [问题]
**解答**:
[详细解答]

### Q2: [问题]
**解答**:
[详细解答]

## 对比学习（如有）
| 概念 | C++ | Rust |
|------|-----|------|
| 内存管理 | RAII | 所有权 |
```

#### 3.3 实时 nmem 记录

```bash
# 每次答疑/错题后，记录到 nmem
nmem m add "问题: $question\n解答: $answer" \
  -t "学习记录: $learning_type" \
  --unit-type learning \
  -i 0.6 \
  -l $learning_type,study \
  -s unified-learning
```

### Phase 4: 结束学习会话

#### 4.1 生成学习汇总

```markdown
# 学习汇总

## 今日学习内容
- 学习类型: [类型]
- 学习时长: [时长]
- 完成内容: [内容]

## 疑难点/错题统计
- 总问题数: N
- 已解决: N
- 待深入: N

## nmem 记录统计
- 记忆条目: N
- 主要主题: [主题列表]

## 明日计划
- [ ] [明日任务]
```

#### 4.2 同步计划状态

```bash
# 更新本地计划
sed -i "s/状态: 进行中/状态: 已完成/" "$vault_path/20 Projects/$learning_type/学习计划.md"

# 更新日计划
sed -i "s/- \[ \] $learning_type 学习任务/- [x] $learning_type 学习任务/" "$vault_path/10 Daily/YYYY-MM-DD.md"
```

#### 4.3 生成 nmem 简报

```bash
# 读取 nmem 中的学习记录
nmem_records=$(nmem m search "学习记录" -l $learning_type -n 20 --json)

# 生成简报
nmem m add "学习汇总内容" \
  -t "$learning_type 学习简报 YYYY-MM-DD" \
  --unit-type learning \
  -i 0.8 \
  -l $learning_type,study,summary \
  -s unified-learning
```

### Phase 5: nmem 简报结构

```markdown
# [学习类型] 学习简报 YYYY-MM-DD

## 学习概况
- 日期: YYYY-MM-DD
- 学习类型: [高软/C++/Rust]
- 学习时长: [时长]

## 学习内容
- 完成内容: [内容]
- 主要主题: [主题]

## 疑难点/错题
- 总问题数: N
- 已解决: N
- 主要问题: [问题列表]

## nmem 记录统计
- 记忆条目: N
- 主要标签: [标签]

## 明日计划
- [ ] [任务1]
- [ ] [任务2]

## 关联
- 学习记录: [路径]
- nmem 记忆: [ID]
```

## 路径约定

| 用途 | 路径 |
|------|------|
| 日计划 | `10 Daily/YYYY-MM-DD.md` |
| 学习计划 | `20 Projects/$learning_type/学习计划.md` |
| 学习记录 | `20 Projects/$learning_type/学习记录/YYYY-MM-DD 学习记录.md` |
| 截图 | `20 Projects/$learning_type/assets/YYYY-MM-DD/` |
| 项目入口 | `20 Projects/$learning_type/$learning_type.md` |

## nmem 集成

### 记忆标签

- `$learning_type` - 学习类型（gaoruan/cpp/rust）
- `study` - 学习记录
- `summary` - 学习汇总
- `learning-plan` - 学习计划
- `study-progress` - 学习进度

### 记忆类型

- `learning` - 学习记录
- `decision` - 学习决策
- `procedure` - 学习方法

### 查询命令

```bash
# 查询学习统计
nmem m search "学习记录" -l $learning_type -n 20

# 查询学习汇总
nmem m search "学习简报" -l $learning_type -n 10

# 查询特定日期
nmem m search "YYYY-MM-DD" -l $learning_type
```

## 相关命令

```bash
# 开启学习会话
$unified-learning-session 开启今天[高软/C++/Rust]学习计划

# 查看学习计划
$unified-learning-session 查看学习计划

# 结束学习会话
$unified-learning-session 今日学习完成

# 生成学习简报
$unified-learning-session 生成学习简报
```

## 注意事项

1. **Obsidian vault 路径**: 默认 `$HOME/obsidian-vault`，可配置
2. **nmem 标签**: 使用统一的标签格式，便于查询
3. **学习记录**: 每次学习必须生成学习记录
4. **简报生成**: 每次学习结束必须生成 nmem 简报
5. **计划同步**: 同步本地计划和 nmem 统计

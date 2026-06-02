---
name: unified-learning-session
description: 统一学习会话管理 - 支持任意学科（高软、C++、Rust、考研、公考等），自动创建 Obsidian vault，集成 nmem 统计和简报生成，支持对题知识点分类整理
tags: [study, learning, 统一学习, 会话管理, 知识点]
triggers: ["学习", "开启学习", "学习计划", "今日学习", "学习完成", "学习总结", "做题", "刷题"]
tool_chain: ["gsd-progress", "gsd-capture", "gsd-docs-update"]
context_injection: true
metadata:
  short-description: "Universal learning session management with knowledge point classification"
---

# 统一学习会话管理

## 核心特性

- **通用学科** - 支持任意学习内容（高软、C++、Rust、考研、公考、语言学习等）
- **自动创建** - 自动创建 Obsidian vault 目录结构
- **nmem 集成** - 实时统计、学习记录、简报生成
- **知识点整理** - 对题自动提取考点，按章节分类保存
- **计划同步** - 同步本地计划和 nmem 统计

## 工作流

### Phase 1: 初始化学习环境

#### 1.1 确定学习类型

用户输入时自动识别，支持任意学科名称：

```
用户: "开启高软学习" → learning_type = "高软"
用户: "开启C++学习" → learning_type = "cpp"
用户: "开启考研政治学习" → learning_type = "考研政治"
用户: "开启学习" → 询问用户具体学科
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

#### 1.3 创建学习目录结构

根据 learning_type 自动创建：

```
20 Projects/$learning_type/
├── 学习计划.md
├── 学习记录/
│   └── YYYY-MM-DD 学习记录.md
├── 知识点/
│   ├── 第1章-章节名.md
│   └── 第2章-章节名.md
└── assets/
    └── YYYY-MM-DD/
        └── 第N题-简述.png
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
- 学习类型: [$learning_type]
- 计划内容: [今日计划]

## 学习内容
[待填写]

## 错题记录
[待填写]

## 对题知识点
[待填写]

## 学习总结
[待填写]
```

#### 2.3 同步日计划

```markdown
# 10 Daily/YYYY-MM-DD.md

## 学习计划
- [ ] [$learning_type] 学习任务

## Notes
- 学习记录: [[20 Projects/$learning_type/学习记录/YYYY-MM-DD 学习记录.md]]
```

### Phase 3: 学习过程

#### 3.1 题目处理流程

无论是**错题**还是**对题**，都需要提取知识点并归档到对应章节。

**处理步骤：**

```
- [ ] 记录题目到学习记录（错题/对题）
- [ ] 从题目和选项中提取涉及的考点
- [ ] 将考点追加到对应章节的知识点文件
- [ ] 更新学习记录中的知识点索引
```

#### 3.2 错题记录

```markdown
## 错题记录

### 第N题（章节 · 考点）
- 题目: [题目内容]
- 选项: [选项]
- 你的答案: [答案]
- 正确答案: [答案]
- 解析: [解析]
- 错因类型: [概念混淆/计算错误/记忆错误/审题不清]
- 涉及考点: [[第X章-章节名#考点名称]]

## 错因归类
| 类型 | 题号 |
|------|------|
| 概念混淆 | 1, 3, 5 |
| 计算错误 | 2, 4 |
```

#### 3.3 对题记录

```markdown
## 对题记录

### 第N题（章节 · 考点）
- 题目: [题目内容]
- 选项: [选项]
- 正确答案: [答案]
- 考察要点: [为什么这个选项是对的]
- 涉及考点: [[第X章-章节名#考点名称]]
```

#### 3.4 知识点提取与归档（核心功能）

无论是错题还是对题，都需要从题目和选项中提取知识点，归档到对应章节。

**Step 1: 提取考点**

从题目和选项中识别涉及的知识点：
- 题干中的核心概念
- 正确选项对应的知识点
- 干扰选项涉及的易混淆点
- 错题的错因分析

**Step 2: 归档到章节文件**

将考点追加到对应章节的知识点文件：

```
20 Projects/$learning_type/知识点/第N章-章节名.md
```

**Step 3: 知识点文件格式**

```markdown
# 第N章 - 章节名

## 考点1: [考点名称]

### 基本概念
[核心知识点说明]

### 相关题目

#### 题目1（YYYY-MM-DD，错题/对题）
- 题目: [简述]
- 正确选项: [选项内容]
- 考察要点: [为什么这个选项是对的]
- 错因分析: [仅错题，说明错误原因]

### 易混淆点
[从干扰选项中提取的易混淆概念]

### 记忆口诀
[可选，便于记忆的总结]

---

## 考点2: [考点名称]

### 基本概念
...

### 相关题目
...
```

**Step 4: 更新学习记录索引**

在当日学习记录中记录知识点索引：

```markdown
## 知识点索引
- 第1题 → [[第2章-操作系统#计数信号量]]
- 第3题 → [[第3章-网络#TCP三次握手]]
- 第5题 → [[第2章-操作系统#页式地址]]
```

**Step 5: 追加规则**

- 同一考点多次出现：追加到「相关题目」，不重复创建考点
- 同一题目涉及多个考点：分别追加到各考点
- 错题和对题混合：统一归档，通过标签区分

#### 3.5 实时 nmem 记录

```bash
# 错题记录到 nmem
nmem m add "错题: $question\n正确答案: $answer\n错因: $reason\n考点: $knowledge_point" \
  -t "错题记录: $learning_type" \
  --unit-type learning \
  -i 0.6 \
  -l $learning_type,study,wrong-answer \
  -s unified-learning

# 对题记录到 nmem
nmem m add "对题: $question\n正确答案: $answer\n考点: $knowledge_point" \
  -t "对题记录: $learning_type" \
  --unit-type learning \
  -i 0.5 \
  -l $learning_type,study,correct-answer \
  -s unified-learning

# 知识点记录到 nmem（汇总）
nmem m add "章节: 第N章\n考点: $knowledge_point\n题目数: N" \
  -t "知识点: $knowledge_point" \
  --unit-type knowledge \
  -i 0.7 \
  -l $learning_type,knowledge-point \
  -s unified-learning
```

### Phase 4: 结束学习会话

#### 4.1 生成学习汇总

```markdown
# 学习汇总

## 今日学习内容
- 学习类型: [$learning_type]
- 学习时长: [时长]
- 完成内容: [内容]

## 错题统计
- 总错题数: N
- 错因分布: [概念混淆 X 题, 计算错误 Y 题]

## 知识点整理
- 新增知识点: N 个
- 涉及章节: [章节列表]
- 知识点列表:
  - [[考点1]]
  - [[考点2]]

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
# [$learning_type] 学习简报 YYYY-MM-DD

## 学习概况
- 日期: YYYY-MM-DD
- 学习类型: [$learning_type]
- 学习时长: [时长]

## 学习内容
- 完成内容: [内容]
- 主要主题: [主题]

## 错题分析
- 总错题数: N
- 主要错因: [错因列表]

## 知识点积累
- 新增知识点: N 个
- 知识点列表: [列表]

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
| **知识点文件** | `20 Projects/$learning_type/知识点/第N章-章节名.md` |
| 截图 | `20 Projects/$learning_type/assets/YYYY-MM-DD/` |
| 项目入口 | `20 Projects/$learning_type/$learning_type.md` |

## nmem 集成

### 记忆标签

- `$learning_type` - 学习类型（用户自定义）
- `study` - 学习记录
- `summary` - 学习汇总
- `wrong-answer` - 错题记录
- `correct-answer` - 对题记录
- `knowledge-point` - 知识点
- `learning-plan` - 学习计划
- `study-progress` - 学习进度

### 记忆类型

- `learning` - 学习记录
- `knowledge` - 知识点
- `decision` - 学习决策
- `procedure` - 学习方法

### 查询命令

```bash
# 查询学习统计
nmem m search "学习记录" -l $learning_type -n 20

# 查询知识点
nmem m search "知识点" -l $learning_type,knowledge-point -n 20

# 查询特定考点
nmem m search "计数信号量" -l $learning_type,knowledge-point

# 查询学习汇总
nmem m search "学习简报" -l $learning_type -n 10

# 查询特定日期
nmem m search "YYYY-MM-DD" -l $learning_type
```

## 相关命令

```bash
# 开启学习会话
开启[学科]学习

# 记录错题
[粘贴题目内容]

# 记录对题（自动提取知识点）
[粘贴做对的题目]

# 查看知识点
查看[学科]知识点

# 结束学习会话
今日学习完成

# 生成学习简报
生成学习简报
```

## 注意事项

1. **Obsidian vault 路径**: 默认 `$HOME/obsidian-vault`，可配置
2. **nmem 标签**: 使用统一的标签格式，便于查询
3. **学习记录**: 每次学习必须生成学习记录
4. **知识点整理**: 错题和对题都必须提取知识点，归档到对应章节
5. **简报生成**: 每次学习结束必须生成 nmem 简报
6. **计划同步**: 同步本地计划和 nmem 统计

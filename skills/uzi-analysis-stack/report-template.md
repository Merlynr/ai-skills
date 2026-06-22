# 报告与交付模板

UZI 跑完后，向用户交付的**中文摘要**格式。数据必须来自 `synthesis.json` / `panel.json` / HTML，不可臆造。

## 读取顺序

1. `${SCRIPTS_DIR}/.cache/<ticker>/synthesis.json` — 综合结论
2. `${SCRIPTS_DIR}/.cache/<ticker>/panel.json` — 评委分数与分歧
3. `${SCRIPTS_DIR}/reports/<ticker>_*/full-report-standalone.html` — 完整报告路径（告知用户）

**full 模式额外核对**：`synthesis.json` 或 stage2 日志中 `agent_reviewed: true`；交付标注 **执行模式: full**。  
**fast 模式**：`agent_reviewed: false` 为预期，标注 **执行模式: fast（骨架）**。

`SCRIPTS_DIR="${UZI_ROOT}/skills/deep-analysis/scripts"`

## 标准摘要（medium / deep）

```markdown
## UZI 分析 · {名称} ({代码})

**深度**: {lite|medium|deep} · **模式**: {fast|full} · **日期**: {YYYY-MM-DD}

### 一句话定调
{观望优先 / 谨慎参与 / … — 来自 synthesis}

### 综合评分
- 总分: {xx}/100
- 分项: （若有 fund / consensus / technical 等，引用 JSON 字段）

### 评委分歧（Top3）
**偏多**: …
**偏空**: …

### 估值（deep 或有 DCF 时）
- DCF 内在价值: …
- 当前价 vs 内在价值: …

### 风险
1. …
2. …

### 杀猪盘（若已跑）
- 等级: …

### 完整报告
- 本地: `{html 路径}`
- （若 --remote）公网: `{url}`

---
*数据来源: UZI-Skill 22 维 + 评委引擎；非投资建议。*
```

## lite / quick-scan 精简版

```markdown
## 速扫 · {名称} ({代码})

**定调**: … · **综合分**: … · **杀猪盘**: …

**关键风险**: …

*完整分析可说「要 medium 深度吗？」*
```

## 字段缺失

JSON 缺字段时写「数据缺失：{字段名}」，不要填占位数字。

## 免责声明

交付末尾保留：**本摘要由 UZI 工具生成，不构成投资建议。**

# /uzi:analyze-stock — 个股分析（medium / deep）

**触发**: 深度分析、全面分析、能不能买、值不值得、帮我看看 XXX

**参数**: `$ARGUMENTS` = 股票名称或代码；可选深度词（深度/deep/全面 → deep，否则 medium）

## 前置

1. Read [../analysis-routing.md](../analysis-routing.md) 解析 `UZI_ROOT`
2. Read [../report-template.md](../report-template.md)

## 步骤

### 1. 确认输入

- 解析 ticker；中文名失败则请用户提供 `600519.SH` 等形式
- 深度：含「深度/全面/研究/估值」→ `deep`；否则 `medium`

### 2. 执行

```bash
export UZI_ROOT="${UZI_ROOT:-${SKILLSHARE_SKILLS:-$HOME/.config/skillshare/skills}/uzi/_UZI-Skill}"
cd "$UZI_ROOT"
python3 run.py <TICKER> --no-browser --depth <medium|deep>
```

### 3. 读产物

```bash
SCRIPTS="$UZI_ROOT/skills/deep-analysis/scripts"
# Read: $SCRIPTS/.cache/<ticker>/synthesis.json
# Read: $SCRIPTS/.cache/<ticker>/panel.json
```

### 4. 交付

按 report-template 输出中文摘要 + HTML 路径。

### 5. 可选 U4

用户要记录 → `distill-memory`（见 analysis-routing § nmem）

## 禁止

- 未跑脚本就输出评分
- 把 medium 当 lite（维度不足）

## 上游参考

完整 agent 工作流（Task 1–5）：Read `$UZI_ROOT/skills/deep-analysis/SKILL.md`

---
disable-model-invocation: true
name: "research-report-analyzer"
description: "Batch analyze PDF research reports in a directory — supports both text-based and scanned/image-based PDFs. Invoke when user asks to analyze research reports, extract investment insights from PDFs, or mentions 研报分析/批量研报/研报提取/分析研报."
---

# Research Report Analyzer (研报批量分析) v2

## When to Use

- User says "分析当前目录的研报" / "分析研报" / "帮我看看这些PDF研报"
- User mentions "研报分析", "批量研报", "研报提取", "research report analysis"
- User wants to extract stock recommendations, hot topics, or risk warnings from report PDFs
- Current directory or specified directory contains PDF research report files

## Configuration

```yaml
# Auto-save destination for analysis results (Obsidian vault)
save_dir: "F:\\note\\20 Projects\\天才交易员\\06-每日研报分析"
```

## Date Detection

The report date is derived from **PDF filenames**, not today's date. Most filenames contain a pattern like `6.17`, `6.18`, etc. Extract the most common date across filenames and resolve it to a full `YYYY-MM-DD` using the current year. For example, if most files contain `6.17` and the current year is 2026, the report date is `2026-06-17`.

## Execution Workflow

### Step 1: Run Extraction Script

Execute the bundled Python helper to discover PDFs and extract content. The script auto-installs missing dependencies (`pdfplumber`, `pymupdf`).

```bash
python "<skill_dir>/research_report_analyzer.py" "<target_directory>" -p 15 --dpi 200
```

- `<target_directory>` defaults to the current working directory
- The script outputs **structured JSON** to stdout with this shape:

```json
{
  "pdf_count": 13,
  "text_count": 5,
  "image_count": 8,
  "error_count": 0,
  "image_dir": "<path>/_report_images",
  "reports": [
    { "filename": "...", "type": "text", "text": "..." },
    { "filename": "...", "type": "image", "image_paths": ["...p1.png", "...p2.png"], "page_count": 2 },
    { "filename": "...", "type": "error", "error": "..." }
  ]
}
```

### Step 2: Read Image-Based Reports

For every report where `type == "image"`, use the **Read tool** to view each image path listed in `image_paths`. Read images **in parallel** (batch multiple Read calls in one turn) to maximize speed.

Skip this step if all reports are `type == "text"`.

### Step 3: Per-Report Mini-Summary

Before cross-analysis, produce a **one-line summary** for each report:

```
- 《filename》: 核心观点一句话
```

This helps the user quickly see what each report covers and lets the AI verify comprehension before synthesis.

### Step 4: Cross-Report Analysis

Analyze ALL extracted content (text + images) together. Follow these analysis dimensions:

1. **Consensus signals** — What do multiple reports agree on? (strongest conviction)
2. **Divergent views** — Where do reports disagree? Which side has better evidence?
3. **Quantitative data** — Target prices, earnings forecasts, growth rates, valuation metrics
4. **Sector rotation** — Which sectors are gaining/losing momentum?
5. **Risk flags** — Timing risks, valuation risks, policy risks, liquidity risks
6. **Actionable catalysts** — Upcoming events, earnings dates, policy deadlines

### Step 5: Output Structured Report

Output in **Markdown** format (human-readable) structured as:

```markdown
## 6.XX 研报综合分析（共 N 份）

### 一、市场整体环境
（成交额、涨跌家数、情绪指标、关键数据）

### 二、核心主线与热点
（当前最强主线、各细分方向、资金流向）

### 三、个股聚焦
| 个股 | 来源 | 核心逻辑 | 风险点 |
|------|------|----------|--------|
（多篇提及的重点标的）

### 四、潜在机会（低估值/业绩支撑）
（有业绩但尚未充分反映的标的）

### 五、风险提示与规避
（建议规避的板块/个股及原因）

### 六、操作建议
（总体策略、仓位建议、关键时间节点）
```

### Step 6: Output JSON (Always)

After the Markdown report, **also** output the structured JSON for programmatic use:

```json
{
  "date": "YYYY-MM-DD",
  "current_hot_topics": ["string"],
  "future_trends": ["string"],
  "sector_rotation": ["string — 板块轮动方向"],
  "key_stocks": [
    {
      "name": "股票名",
      "sources": ["提及该股的研报"],
      "logic": "推荐逻辑",
      "risk": "风险点"
    }
  ],
  "undervalued_with_performance": ["string"],
  "avoid_or_risks": ["string"],
  "key_dates": ["string — 需关注的时间节点及原因"],
  "summary": "string — 200字以内总体策略",
  "source_reports": ["string"],
  "report_count": 0,
  "analysis_timestamp": "ISO 8601"
}
```

### Step 7: Save Results (Automatic)

**Always** save analysis results to `save_dir` after outputting to the user. Use the detected report date (see "Date Detection" above) for filenames.

Save two files using the **Write tool**:
- `{save_dir}/YYYY-MM-DD.md` — Markdown report (the full Step 5 output, prefixed with a YAML-style header containing source directory and analysis timestamp)
- `{save_dir}/YYYY-MM-DD.json` — JSON data (the full Step 6 output)

**Markdown file header** (prepend before the report body):
```markdown
# YYYY-MM-DD 研报综合分析（共 N 份）

> 来源目录：`<source_directory>`
> 分析时间：YYYY-MM-DD HH:MM CST
```

If the file already exists for that date, **overwrite** it (re-analysis replaces the previous version).

After saving, confirm to the user:
```
已保存至：
- F:\note\20 Projects\天才交易员\06-每日研报分析\YYYY-MM-DD.md
- F:\note\20 Projects\天才交易员\06-每日研报分析\YYYY-MM-DD.json
```

## Analysis Guidelines

- **Evidence over opinion**: Prioritize reports with quantitative backing over pure sentiment
- **Frequency = conviction**: A stock mentioned by 3+ reports carries more weight
- **Contradiction = opportunity**: Disagreements often flag the most interesting trades
- **Time-sensitivity**: Flag upcoming catalysts (earnings, holidays, policy dates) prominently
- **Risk-reward framing**: Don't just list bullish targets — every recommendation needs a risk assessment

## Error Handling

- If a PDF fails extraction, continue processing others; report the failure in output
- If ALL PDFs are image-based and pymupdf is unavailable, report the error and suggest: `pip install pymupdf`
- If the directory has no PDFs, inform the user immediately

## Dependencies

- `pdfplumber` — text extraction + table parsing (auto-installed by script)
- `pymupdf` — image-based PDF fallback (auto-installed by script)
- No external API calls needed; the AI performs all analysis

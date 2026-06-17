---
name: "research-report-analyzer"
description: "Extract text from PDF research reports and format it for AI analysis. Invoke when user wants to batch process research reports, extract PDF text for LLM consumption, or prepare report content for AI-powered investment analysis."
---

# Research Report Analyzer (研报批量分析)

A lightweight tool that extracts text from PDF research reports and formats it for direct AI analysis. **No API keys required** — the actual analysis is performed by the AI agent invoking this skill.

## When to Use

- User wants to analyze one or multiple PDF research reports
- User asks to extract stock recommendations, hot topics, or risk warnings from reports
- User mentions "研报分析", "批量研报", "研报提取", "research report analysis"
- User wants to feed research report data into a backtesting or quantitative dashboard
- User wants to prepare PDF content for AI analysis without calling external APIs

## Architecture

```
PDF Files → pdfplumber (text extraction) → Formatted output → AI Agent analyzes directly
```

**Key design decisions:**
- **Zero API dependencies** — no OpenAI, DeepSeek, or any external LLM API needed
- **AI-native workflow** — the AI agent reading the output performs the analysis
- **Smart formatting** — chunks text into AI-friendly segments with clear boundaries
- **Error isolation** — one PDF failure won't crash the entire batch
- **Persistent output** — results saved as formatted text and JSON metadata

## Dependencies

```bash
pip install pdfplumber
```

**No openai, no pydantic, no API keys.**

## Configuration

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `RRA_MAX_PAGES` | No | `15` | Max pages to extract per PDF |
| `RRA_OUTPUT_DIR` | No | `./output` | Directory for output files |

## How It Works

### Step 1: Extract & Format

The tool extracts text from PDFs and formats it into a structured document:

```
================ 研报批量分析输入数据 ================

--- 研报《文件名1.pdf》内容开始 ---
[提取的文本内容...]
--- 研报内容结束 ---

--- 研报《文件名2.pdf》内容开始 ---
[提取的文本内容...]
--- 研报内容结束 ---

====================================================
```

### Step 2: AI Analysis

The formatted output is designed to be fed directly into an AI conversation. The AI agent (Claude, GPT, DeepSeek, etc.) reads the formatted text and performs the analysis using its own reasoning capabilities.

### Step 3: Structured Output

The AI outputs structured JSON according to the schema below.

## Output Schema (AI-Generated)

When the AI analyzes the formatted output, it should produce:

```json
{
  "current_hot_topics": ["string — trending themes mentioned across reports"],
  "future_trends": ["string — predicted emerging trends"],
  "undervalued_with_performance": ["string — companies with solid fundamentals but low valuation"],
  "recommended_buy": ["string — strongly recommended buy targets with rationale"],
  "avoid_or_risks": ["string — sectors/stocks with downgrade or risk warnings"],
  "summary": "string — overall investment strategy recommendation",
  "source_reports": ["string — list of processed report filenames"],
  "analysis_timestamp": "string — ISO 8601 timestamp"
}
```

## Usage

### As a Python module

```python
from research_report_analyzer import extract_reports

# Extract all PDFs in a directory
result = extract_reports(
    directory_path="/path/to/reports",
    output_dir="./output"
)
# result contains: formatted_text, metadata, output_file paths

# The formatted_text is ready to paste into an AI conversation
print(result["formatted_text"])
```

### As a CLI tool

```bash
# Extract all PDFs in current directory
python research_report_analyzer.py .

# Extract specific directory
python research_report_analyzer.py /path/to/reports

# With custom output directory
python research_report_analyzer.py /path/to/reports -o ./results
```

### AI Analysis Prompt Template

After extracting the text, use this prompt with your AI:

```
你是一个资深的 A 股/港股量化研究员与行业分析师。
我将为你提供近期收集的一批券商研报文本，请你仔细阅读并进行综合交叉分析。

请严格以 JSON 格式输出你的分析结果，包含以下字段：
1. "current_hot_topics": [列表] 当下市场正在炒作、研报中频繁提及的核心热点题材。
2. "future_trends": [列表] 研报中预测的未来可能爆发的产业趋势或潜伏热点。
3. "undervalued_with_performance": [列表] 有扎实业绩支撑，但研报指出当前估值/股价仍处于低位、存在预期差的具体公司名称及逻辑简述。
4. "recommended_buy": [列表] 多篇研报共同强烈推荐买入、逻辑最硬的标的（含推荐理由）。
5. "avoid_or_risks": [列表] 研报中提示了减持评级、行业拐点向下、面临政策或财务风险，建议规避的板块或个股。
6. "summary": [字符串] 综合这批研报，给出一份简短的总体投资策略建议（200 字以内）。

确保只输出合法的 JSON 字符串，不要包含任何 markdown 代码块标记或其他多余文字。

以下是研报文本：
[粘贴提取的格式化文本]
```

## Integration with Agent Workflows

This skill is designed for **AI-native workflows**:

1. **Pre-trade screening** — Extract reports → Feed to AI agent → Get investment insights
2. **Daily briefing** — Run each morning, let AI analyze overnight reports
3. **Backtesting input** — AI outputs JSON that feeds directly into quantitative systems
4. **Dashboard data** — Load AI-generated JSON into Grafana/Obsidian dashboards

## Why No External API?

- **Cost**: No per-token charges for PDF extraction
- **Privacy**: Report text stays in your environment until you choose to share with AI
- **Flexibility**: Use any AI (Claude, GPT, DeepSeek, local models) without code changes
- **Simplicity**: Single dependency (`pdfplumber`), no API key management
- **Reliability**: No network failures, rate limits, or service outages

## Implementation Notes

- See `research_report_analyzer.py` for the full implementation
- The script handles Chinese PDFs with double-column layouts common in domestic broker reports
- For very large batches (>20 reports), the tool automatically chunks output into manageable segments
- Each report is clearly delimited with markers for easy AI parsing

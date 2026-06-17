---
name: "research-report-analyzer"
description: "Batch extract structured investment insights from PDF research reports via LLM. Invoke when user wants to analyze research reports, extract stock recommendations, or batch process PDF analyst reports."
---

# Research Report Analyzer (研报批量分析)

A skill that batch-processes PDF research reports (券商研报), extracts structured investment insights via LLM, and outputs JSON results suitable for downstream quantitative systems or dashboards.

## When to Use

- User wants to analyze one or multiple PDF research reports
- User asks to extract stock recommendations, hot topics, or risk warnings from reports
- User mentions "研报分析", "批量研报", "研报提取", "research report analysis"
- User wants to feed research report data into a backtesting or quantitative dashboard

## Architecture

```
PDF Files → pdfplumber (text extraction) → Per-report LLM analysis → Aggregation LLM → Structured JSON → Output
```

**Key design decisions vs naive approach:**
- **Per-report analysis first, then aggregate** — avoids token overflow from concatenating all reports into one prompt
- **Error isolation** — one PDF failure won't crash the entire batch
- **Configurable model** — supports OpenAI, DeepSeek, Claude, or any OpenAI-compatible API via `base_url`
- **Persistent output** — results saved as JSON and Markdown summary files
- **Retry with backoff** — resilient to transient API errors

## Dependencies

```bash
pip install openai pdfplumber pydantic
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | API key for the LLM service |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | Base URL (change for DeepSeek, local models, etc.) |
| `RRA_MODEL` | No | `gpt-4o` | Model name to use |
| `RRA_MAX_PAGES` | No | `15` | Max pages to extract per PDF |
| `RRA_OUTPUT_DIR` | No | `./output` | Directory for output files |
| `RRA_TEMPERATURE` | No | `0.2` | LLM temperature (lower = less hallucination) |

## Output Schema

The final aggregated JSON follows this structure:

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
from research_report_analyzer import analyze_research_reports

# Analyze all PDFs in a directory
result = analyze_research_reports(
    directory_path="/path/to/reports",
    output_dir="./output"
)

# Analyze specific files
result = analyze_research_reports(
    file_paths=["/path/to/report1.pdf", "/path/to/report2.pdf"],
    output_dir="./output"
)
```

### As a CLI tool

```bash
# Analyze all PDFs in current directory
python research_report_analyzer.py .

# Analyze specific directory
python research_report_analyzer.py /path/to/reports

# With custom output directory
python research_report_analyzer.py /path/to/reports -o ./results
```

## Integration with Agent Workflows

This skill is designed to be a **core tool** in AI agent workflows:

1. **Pre-trade screening** — Feed recent reports before making investment decisions
2. **Daily briefing** — Run on newly downloaded reports each morning
3. **Backtesting input** — Pipe JSON output directly into quantitative backtesting systems
4. **Dashboard data** — Load JSON into Grafana/obsidian dashboards for visualization

## Implementation Notes

- See `research_report_analyzer.py` for the full implementation
- The script handles Chinese PDFs with double-column layouts common in domestic broker reports
- Token management: each report is analyzed individually (~4K-8K tokens), then a lightweight aggregation pass combines results
- For very large batches (>20 reports), consider running in parallel with `concurrent.futures`

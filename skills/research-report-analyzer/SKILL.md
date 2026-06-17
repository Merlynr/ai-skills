---
name: "research-report-analyzer"
description: "Batch analyze PDF research reports in a directory. Invoke when user asks to analyze research reports, extract investment insights from PDFs, or mentions 研报分析/批量研报/研报提取. The AI executes the full workflow: extract PDF text via pdfplumber, then analyze directly."
---

# Research Report Analyzer (研报批量分析)

## When to Use

- User says "分析当前目录的研报"
- User says "帮我看看这些 PDF 研报"
- User mentions "研报分析", "批量研报", "研报提取", "research report analysis"
- User wants to extract stock recommendations, hot topics, or risk warnings from reports

## Execution Workflow

When this skill is invoked, the AI MUST execute the following steps:

### Step 1: Discover PDF Files

Use `Glob` or `LS` to find all `.pdf` files in the specified directory (default: current working directory).

### Step 2: Extract Text from PDFs

For each PDF found, use `pdfplumber` (via Python execution) to extract text. Limit to first 15 pages by default to avoid token overflow.

**Python extraction script:**

```python
import pdfplumber
import os

def extract_pdf_text(file_path, max_pages=15):
    text_parts = []
    try:
        with pdfplumber.open(file_path) as pdf:
            pages_to_read = min(len(pdf.pages), max_pages)
            for i in range(pages_to_read):
                text = pdf.pages[i].extract_text()
                if text and text.strip():
                    text_parts.append(text)
    except Exception as e:
        return f"[ERROR] Failed to read {file_path}: {e}"
    full_text = "\n".join(text_parts)
    # Truncate if too long
    if len(full_text) > 15000:
        full_text = full_text[:15000] + "\n...[内容过长，已截断]"
    return full_text

# Extract all PDFs in directory
pdf_files = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]
for pdf in pdf_files:
    print(f"\n=== 研报《{pdf}》===\n")
    print(extract_pdf_text(pdf))
```

### Step 3: Analyze Extracted Content

The AI reads the extracted text and performs comprehensive cross-analysis directly. Do NOT ask the user to copy-paste anything. The AI acts as the analyst.

### Step 4: Output Structured JSON

The AI MUST output the analysis result in the following JSON schema:

```json
{
  "current_hot_topics": ["string — 当下市场正在炒作、研报中频繁提及的核心热点题材"],
  "future_trends": ["string — 研报中预测的未来可能爆发的产业趋势或潜伏热点"],
  "undervalued_with_performance": ["string — 有扎实业绩支撑，但估值/股价仍处于低位的标的及逻辑"],
  "recommended_buy": ["string — 多篇研报共同强烈推荐买入的标的（含推荐理由）"],
  "avoid_or_risks": ["string — 建议规避的板块或个股（含风险说明）"],
  "summary": "string — 总体投资策略建议（200字以内）",
  "source_reports": ["string — 处理的研报文件名列表"],
  "analysis_timestamp": "string — ISO 8601 时间戳"
}
```

### Step 5: Save Results (Optional)

If the user wants persistent output, save both:
- JSON result to `analysis_result_YYYYMMDD_HHMMSS.json`
- Markdown summary to `analysis_report_YYYYMMDD_HHMMSS.md`

## Analysis Guidelines

When analyzing reports, the AI should:

1. **Identify consensus**: What do multiple reports agree on?
2. **Spot contradictions**: Where do reports disagree? Which view has stronger evidence?
3. **Extract quantitative data**: Target prices, earnings forecasts, growth rates
4. **Assess risk levels**: Distinguish between minor concerns and major red flags
5. **Cross-reference**: Connect themes across different sectors and reports

## Example User Interaction

**User**: "分析当前目录的研报"

**AI Action**:
1. Run PDF discovery → find 5 PDF files
2. Extract text from each PDF using pdfplumber
3. Read and analyze all content
4. Output structured JSON with investment insights
5. Provide a brief natural language summary

**AI Output**:
```json
{
  "current_hot_topics": ["固态电池产业化加速", "AI 算力需求爆发"],
  "future_trends": ["人形机器人零部件", "低空经济基础设施"],
  "undervalued_with_performance": [
    "宁德时代：Q2 业绩超预期，当前 PE 仅 15x，低于行业均值 20x"
  ],
  "recommended_buy": [
    "比亚迪：3 家券商上调目标价至 300+，新能源车市占率持续提升"
  ],
  "avoid_or_risks": [
    "光伏组件：产能过剩，价格战持续，行业拐点向下，建议规避"
  ],
  "summary": "建议关注新能源产业链中业绩确定性强的龙头标的，固态电池和 AI 算力为当前主线。规避产能过剩的光伏组件板块。",
  "source_reports": ["中信证券-宁德时代深度报告.pdf", "华泰证券-比亚迪季报点评.pdf"],
  "analysis_timestamp": "2026-06-17T14:30:00+08:00"
}
```

## Dependencies

- `pdfplumber` (Python package for PDF text extraction)
- No OpenAI API, no external LLM calls needed

## Notes

- For scanned/image-based PDFs, text extraction will fail. Notify the user to use OCR first.
- If a single PDF fails to extract, continue processing others. Report the failure in output.
- Default max_pages=15 captures the essence of most research reports.
- The AI performs the analysis using its own reasoning capabilities on the extracted text.

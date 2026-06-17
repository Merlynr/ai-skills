"""
Research Report Analyzer (研报批量分析器)
==========================================
批量处理 PDF 研报，通过 LLM 提取结构化投资洞察，输出 JSON 格式结果。

改进点（相比原始版本）：
1. 逐份分析再汇总，避免 Token 溢出
2. 错误隔离：单份 PDF 失败不中断整体流程
3. 结果持久化：JSON + Markdown 双格式输出
4. 可配置模型：支持 OpenAI / DeepSeek / Claude / 本地模型
5. API 重试机制：应对瞬时错误

用法:
    python research_report_analyzer.py <directory_or_files> [-o OUTPUT_DIR]
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("缺少依赖: pip install pdfplumber")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("缺少依赖: pip install openai")
    sys.exit(1)


# ============================================================
# Configuration
# ============================================================

DEFAULT_MODEL = os.environ.get("RRA_MODEL", "gpt-4o")
DEFAULT_MAX_PAGES = int(os.environ.get("RRA_MAX_PAGES", "15"))
DEFAULT_OUTPUT_DIR = os.environ.get("RRA_OUTPUT_DIR", "./output")
DEFAULT_TEMPERATURE = float(os.environ.get("RRA_TEMPERATURE", "0.2"))
DEFAULT_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds


def get_client() -> OpenAI:
    """Initialize OpenAI client with environment config."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "未设置 OPENAI_API_KEY 环境变量。\n"
            "请运行: export OPENAI_API_KEY='your-key-here'"
        )
    return OpenAI(api_key=api_key, base_url=DEFAULT_BASE_URL)


# ============================================================
# PDF Text Extraction
# ============================================================

def extract_text_from_pdf(file_path: str, max_pages: int = DEFAULT_MAX_PAGES) -> str:
    """
    Extract text from PDF using pdfplumber.
    Limits page count to avoid token overload.
    Handles double-column layouts common in Chinese broker reports.
    """
    text_parts = []
    try:
        with pdfplumber.open(file_path) as pdf:
            pages_to_read = min(len(pdf.pages), max_pages)
            for i in range(pages_to_read):
                page = pdf.pages[i]
                # pdfplumber handles double-column layouts better than PyPDF2
                text = page.extract_text()
                if text and text.strip():
                    text_parts.append(text)
    except Exception as e:
        print(f"  [WARN] 读取 {file_path} 失败: {e}")
        return ""
    return "\n".join(text_parts)


# ============================================================
# LLM Analysis (Per-Report)
# ============================================================

PER_REPORT_PROMPT = """你是一个资深的 A 股/港股行业分析师。
请仔细阅读以下券商研报文本，提取其中的核心投资信息。

请严格以 JSON 格式输出，包含以下字段：
1. "report_title": 研报标题（根据内容推断）
2. "covered_stocks": 本研报覆盖的个股列表（股票名称 + 代码，如有）
3. "key_themes": 本研报讨论的核心主题/行业（列表）
4. "investment_logic": 本研报的核心投资逻辑摘要（1-3 句话）
5. "rating": 研报给出的评级（如"买入"/"增持"/"中性"/"减持"/"未明确评级"）
6. "target_price": 目标价（如有，否则为 null）
7. "key_risks": 本研报提示的主要风险（列表）
8. "data_highlights": 关键数据亮点（如营收增速、利润率、订单量等，列表）

确保只输出合法的 JSON 字符串，不要包含 markdown 代码块标记或其他多余文字。"""


def analyze_single_report(client: OpenAI, text: str, filename: str) -> dict | None:
    """Analyze a single research report text via LLM. Returns parsed JSON or None on failure."""
    if not text.strip():
        print(f"  [SKIP] {filename}: 提取文本为空")
        return None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": PER_REPORT_PROMPT},
                    {"role": "user", "content": f"研报文件名: {filename}\n\n研报内容:\n{text}"}
                ],
                response_format={"type": "json_object"},
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=2000,
            )
            raw = response.choices[0].message.content
            result = json.loads(raw)
            result["_source_file"] = filename
            print(f"  [OK] {filename}: 分析完成")
            return result
        except json.JSONDecodeError as e:
            print(f"  [RETRY {attempt+1}/{MAX_RETRIES}] {filename}: JSON 解析失败 - {e}")
        except Exception as e:
            print(f"  [RETRY {attempt+1}/{MAX_RETRIES}] {filename}: API 错误 - {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_BACKOFF * (attempt + 1))

    print(f"  [FAIL] {filename}: 达到最大重试次数，跳过")
    return None


# ============================================================
# Aggregation (Cross-Report Synthesis)
# ============================================================

AGGREGATION_PROMPT = """你是一个资深的 A 股/港股量化研究员与首席策略师。
以下是多份券商研报的逐份分析结果（JSON 格式）。请你进行综合交叉分析。

请严格以 JSON 格式输出，包含以下字段：
1. "current_hot_topics": [列表] 当下市场正在炒作、研报中频繁提及的核心热点题材。
2. "future_trends": [列表] 研报中预测的未来可能爆发的产业趋势或潜伏热点。
3. "undervalued_with_performance": [列表] 有扎实业绩支撑，但研报指出当前估值/股价仍处于低位、存在预期差的具体公司名称及逻辑简述。
4. "recommended_buy": [列表] 多篇研报共同强烈推荐买入、逻辑最硬的标的（含推荐理由）。
5. "avoid_or_risks": [列表] 研报中提示了减持评级、行业拐点向下、面临政策或财务风险，建议规避的板块或个股。
6. "summary": [字符串] 综合这批研报，给出一份简短的总体投资策略建议（200 字以内）。

确保只输出合法的 JSON 字符串，不要包含 markdown 代码块标记或其他多余文字。"""


def aggregate_results(client: OpenAI, per_report_results: list[dict]) -> dict | None:
    """Aggregate per-report analyses into a cross-report synthesis."""
    if not per_report_results:
        return None

    # Build a concise summary of each report to avoid token overflow
    report_summaries = []
    for r in per_report_results:
        summary = {
            "file": r.get("_source_file", "unknown"),
            "title": r.get("report_title", ""),
            "stocks": r.get("covered_stocks", []),
            "themes": r.get("key_themes", []),
            "logic": r.get("investment_logic", ""),
            "rating": r.get("rating", ""),
            "risks": r.get("key_risks", []),
        }
        report_summaries.append(summary)

    combined_text = json.dumps(report_summaries, ensure_ascii=False, indent=2)

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": AGGREGATION_PROMPT},
                    {"role": "user", "content": f"以下是 {len(per_report_results)} 份研报的分析结果汇总：\n{combined_text}"}
                ],
                response_format={"type": "json_object"},
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=3000,
            )
            raw = response.choices[0].message.content
            result = json.loads(raw)
            return result
        except Exception as e:
            print(f"  [RETRY {attempt+1}/{MAX_RETRIES}] 汇总分析失败: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_BACKOFF * (attempt + 1))

    return None


# ============================================================
# Output
# ============================================================

def save_results(aggregated: dict, per_report: list[dict], output_dir: str):
    """Save results in JSON and Markdown formats."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- JSON output ---
    json_filename = os.path.join(output_dir, f"analysis_{timestamp}.json")
    output_data = {
        "aggregated": aggregated,
        "per_report": per_report,
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "model_used": DEFAULT_MODEL,
        "report_count": len(per_report),
    }
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"\n[SAVED] JSON: {json_filename}")

    # --- Markdown summary ---
    md_filename = os.path.join(output_dir, f"analysis_{timestamp}.md")
    md_lines = [
        f"# 研报综合分析报告",
        f"",
        f"> 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 研报数量: {len(per_report)} 份",
        f"> 使用模型: {DEFAULT_MODEL}",
        f"",
    ]

    if aggregated:
        sections = [
            ("当前热点题材", "current_hot_topics"),
            ("未来趋势/潜伏热点", "future_trends"),
            ("业绩好但估值低", "undervalued_with_performance"),
            ("强烈推荐买入", "recommended_buy"),
            ("风险提示/建议规避", "avoid_or_risks"),
        ]
        for title, key in sections:
            items = aggregated.get(key, [])
            md_lines.append(f"## {title}")
            md_lines.append("")
            if items:
                for item in items:
                    md_lines.append(f"- {item}")
            else:
                md_lines.append("*(无明确信号)*")
            md_lines.append("")

        summary = aggregated.get("summary", "")
        if summary:
            md_lines.append("## 总体策略建议")
            md_lines.append("")
            md_lines.append(summary)
            md_lines.append("")

    # Per-report details
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## 逐份研报分析详情")
    md_lines.append("")
    for r in per_report:
        md_lines.append(f"### {r.get('_source_file', 'unknown')}")
        md_lines.append(f"- **标题**: {r.get('report_title', 'N/A')}")
        md_lines.append(f"- **覆盖个股**: {', '.join(r.get('covered_stocks', [])) or 'N/A'}")
        md_lines.append(f"- **评级**: {r.get('rating', 'N/A')}")
        md_lines.append(f"- **核心逻辑**: {r.get('investment_logic', 'N/A')}")
        md_lines.append(f"- **主要风险**: {', '.join(r.get('key_risks', [])) or 'N/A'}")
        md_lines.append("")

    with open(md_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[SAVED] Markdown: {md_filename}")

    return json_filename, md_filename


# ============================================================
# Main Entry
# ============================================================

def analyze_research_reports(
    directory_path: str = ".",
    file_paths: list[str] | None = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
) -> dict:
    """
    Skill: Analyze research reports and extract structured investment insights.

    Args:
        directory_path: Directory containing PDF files to analyze.
        file_paths: Optional list of specific PDF file paths (overrides directory scan).
        output_dir: Directory to save output files.

    Returns:
        Aggregated analysis dict with structured investment insights.
    """
    client = get_client()

    # Collect PDF files
    if file_paths:
        pdf_files = [fp for fp in file_paths if fp.lower().endswith(".pdf")]
    else:
        pdf_files = sorted([
            f for f in os.listdir(directory_path)
            if f.lower().endswith(".pdf")
        ])

    if not pdf_files:
        print("未找到 PDF 格式的研报文件。")
        return {}

    print(f"找到 {len(pdf_files)} 份研报，开始逐份提取与分析...\n")

    # Phase 1: Per-report analysis
    per_report_results = []
    for filename in pdf_files:
        if file_paths:
            filepath = filename
        else:
            filepath = os.path.join(directory_path, filename)

        print(f"[Processing] {filename}")
        text = extract_text_from_pdf(filepath)
        if text.strip():
            result = analyze_single_report(client, text, os.path.basename(filepath))
            if result:
                per_report_results.append(result)
        print()

    if not per_report_results:
        print("所有研报分析均失败，无法生成汇总报告。")
        return {}

    print(f"逐份分析完成: {len(per_report_results)}/{len(pdf_files)} 份成功")
    print("正在进行交叉汇总分析...\n")

    # Phase 2: Aggregation
    aggregated = aggregate_results(client, per_report_results)

    if aggregated:
        aggregated["source_reports"] = [r.get("_source_file", "") for r in per_report_results]
        aggregated["analysis_timestamp"] = datetime.now(timezone.utc).isoformat()

    # Phase 3: Save output
    save_results(aggregated or {}, per_report_results, output_dir)

    return aggregated or {}


def main():
    parser = argparse.ArgumentParser(
        description="研报批量分析器 — 提取 PDF 研报中的结构化投资洞察"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="包含 PDF 研报的目录路径，或单个 PDF 文件路径"
    )
    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})"
    )
    args = parser.parse_args()

    target = args.path
    if os.path.isfile(target) and target.lower().endswith(".pdf"):
        file_paths = [target]
        directory_path = "."
    elif os.path.isdir(target):
        file_paths = None
        directory_path = target
    else:
        print(f"错误: '{target}' 不是有效的 PDF 文件或目录")
        sys.exit(1)

    result = analyze_research_reports(
        directory_path=directory_path,
        file_paths=file_paths,
        output_dir=args.output,
    )

    if result:
        print("\n================ 研报综合分析报告 ================\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

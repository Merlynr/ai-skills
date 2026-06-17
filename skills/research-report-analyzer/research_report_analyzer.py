"""
Research Report Analyzer (研报批量分析器) — AI-Native 版本
===========================================================
轻量级 PDF 文本提取工具，零 API 依赖。
提取的格式化文本直接喂给 AI 进行分析，无需单独申请 API Key。

核心变化（相比 API 版本）：
1. 移除 openai / pydantic 依赖
2. 只做 PDF 文本提取 + 格式化输出
3. 分析工作交给调用方的 AI（Claude / GPT / DeepSeek 等）
4. 输出为纯文本 + JSON 元数据，方便 AI 读取

用法:
    python research_report_analyzer.py <directory_or_files> [-o OUTPUT_DIR]
    
    提取完成后，将生成的 .txt 文件内容复制到 AI 对话中即可。
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("[ERROR] 缺少依赖: pip install pdfplumber")
    sys.exit(1)


# ============================================================
# Configuration
# ============================================================

DEFAULT_MAX_PAGES = int(os.environ.get("RRA_MAX_PAGES", "15"))
DEFAULT_OUTPUT_DIR = os.environ.get("RRA_OUTPUT_DIR", "./output")
MAX_TEXT_LENGTH_PER_REPORT = 15000  # 单份研报最大字符数，防止单份过长


# ============================================================
# PDF Text Extraction
# ============================================================

def extract_text_from_pdf(file_path: str, max_pages: int = DEFAULT_MAX_PAGES) -> str:
    """
    使用 pdfplumber 提取 PDF 文本。
    限制页数避免内容过长，兼容国内研报双栏排版。
    """
    text_parts = []
    try:
        with pdfplumber.open(file_path) as pdf:
            pages_to_read = min(len(pdf.pages), max_pages)
            for i in range(pages_to_read):
                page = pdf.pages[i]
                text = page.extract_text()
                if text and text.strip():
                    text_parts.append(text)
    except Exception as e:
        print(f"  [WARN] 读取 {os.path.basename(file_path)} 失败: {e}")
        return ""
    
    full_text = "\n".join(text_parts)
    # 截断过长内容
    if len(full_text) > MAX_TEXT_LENGTH_PER_REPORT:
        full_text = full_text[:MAX_TEXT_LENGTH_PER_REPORT] + "\n...[内容过长，已截断]"
    return full_text


# ============================================================
# Formatting for AI Consumption
# ============================================================

def format_reports_for_ai(report_data: list[dict]) -> str:
    """
    将多份研报的提取结果格式化为 AI 友好的文本。
    每份研报用清晰的分隔符标记，方便 AI 识别和解析。
    """
    lines = [
        "=" * 60,
        "研报批量分析输入数据",
        "=" * 60,
        f"共 {len(report_data)} 份研报 | 提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]
    
    for i, report in enumerate(report_data, 1):
        lines.append(f"--- 研报《{report['filename']}》内容开始 [第 {i}/{len(report_data)} 份] ---")
        lines.append("")
        lines.append(report["text"])
        lines.append("")
        lines.append(f"--- 研报《{report['filename']}》内容结束 ---")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("数据结束。请对上述研报进行综合交叉分析。")
    lines.append("=" * 60)
    
    return "\n".join(lines)


# ============================================================
# Output Saving
# ============================================================

def save_outputs(
    formatted_text: str,
    metadata: list[dict],
    output_dir: str
) -> tuple[str, str, str]:
    """
    保存三种输出文件：
    1. .txt — 格式化文本，直接复制到 AI 对话
    2. .json — 元数据（文件名、页数、提取状态等）
    3. _prompt.md — 包含分析提示词的完整模板
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # --- 1. 格式化文本 (.txt) ---
    txt_path = os.path.join(output_dir, f"reports_extracted_{timestamp}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(formatted_text)
    print(f"[SAVED] 提取文本: {txt_path}")
    
    # --- 2. 元数据 (.json) ---
    json_path = os.path.join(output_dir, f"reports_metadata_{timestamp}.json")
    meta_output = {
        "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_reports": len(metadata),
        "successful_extractions": sum(1 for m in metadata if m["success"]),
        "failed_extractions": sum(1 for m in metadata if not m["success"]),
        "reports": metadata,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meta_output, f, ensure_ascii=False, indent=2)
    print(f"[SAVED] 元数据: {json_path}")
    
    # --- 3. 带提示词的完整模板 (_prompt.md) ---
    prompt_path = os.path.join(output_dir, f"reports_analysis_prompt_{timestamp}.md")
    prompt_content = build_ai_prompt(formatted_text)
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_content)
    print(f"[SAVED] 分析模板: {prompt_path}")
    
    return txt_path, json_path, prompt_path


def build_ai_prompt(formatted_text: str) -> str:
    """构建包含分析提示词的完整模板，用户可直接复制到 AI 对话。"""
    return f"""# 研报分析任务

你是一个资深的 A 股/港股量化研究员与行业分析师。
我将为你提供近期收集的一批券商研报文本，请你仔细阅读并进行综合交叉分析。

## 输出要求

请严格以 JSON 格式输出你的分析结果，包含以下字段：

1. **"current_hot_topics"**: [列表] 当下市场正在炒作、研报中频繁提及的核心热点题材。
2. **"future_trends"**: [列表] 研报中预测的未来可能爆发的产业趋势或潜伏热点。
3. **"undervalued_with_performance"**: [列表] 有扎实业绩支撑，但研报指出当前估值/股价仍处于低位、存在预期差的具体公司名称及逻辑简述。
4. **"recommended_buy"**: [列表] 多篇研报共同强烈推荐买入、逻辑最硬的标的（含推荐理由）。
5. **"avoid_or_risks"**: [列表] 研报中提示了减持评级、行业拐点向下、面临政策或财务风险，建议规避的板块或个股。
6. **"summary"**: [字符串] 综合这批研报，给出一份简短的总体投资策略建议（200 字以内）。

## 约束条件

- 确保只输出合法的 JSON 字符串
- 不要包含任何 markdown 代码块标记（如 ```json）或其他多余文字
- 基于研报文本中的事实进行分析，不要编造数据
- 对不确定的信息标注"未明确提及"

---

## 研报文本数据

{formatted_text}

---

请直接输出 JSON 结果。
"""


# ============================================================
# Main Entry
# ============================================================

def extract_reports(
    directory_path: str = ".",
    file_paths: list[str] | None = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    max_pages: int = DEFAULT_MAX_PAGES,
) -> dict:
    """
    批量提取 PDF 研报文本并格式化为 AI 可读的输出。
    
    Args:
        directory_path: 包含 PDF 文件的目录路径
        file_paths: 可选，指定具体的 PDF 文件路径列表
        output_dir: 输出目录
        max_pages: 每份 PDF 最大提取页数
    
    Returns:
        dict 包含 formatted_text, metadata, output_files
    """
    # 收集 PDF 文件
    if file_paths:
        pdf_files = [fp for fp in file_paths if fp.lower().endswith(".pdf")]
    else:
        if not os.path.isdir(directory_path):
            print(f"[ERROR] 目录不存在: {directory_path}")
            return {}
        pdf_files = sorted([
            f for f in os.listdir(directory_path)
            if f.lower().endswith(".pdf")
        ])
        pdf_files = [os.path.join(directory_path, f) for f in pdf_files]
    
    if not pdf_files:
        print("[WARN] 未找到 PDF 格式的研报文件。")
        return {}
    
    print(f"找到 {len(pdf_files)} 份研报，开始提取文本...\n")
    
    # 逐份提取
    report_data = []
    metadata = []
    
    for filepath in pdf_files:
        filename = os.path.basename(filepath)
        print(f"[Processing] {filename}")
        
        text = extract_text_from_pdf(filepath, max_pages=max_pages)
        success = bool(text.strip())
        
        if success:
            report_data.append({"filename": filename, "text": text})
            print(f"  [OK] 提取成功 ({len(text)} 字符)")
        else:
            print(f"  [SKIP] 提取失败或文本为空")
        
        metadata.append({
            "filename": filename,
            "path": filepath,
            "success": success,
            "text_length": len(text) if success else 0,
        })
        print()
    
    if not report_data:
        print("[ERROR] 所有研报提取均失败。")
        return {}
    
    # 格式化为 AI 可读文本
    print(f"提取完成: {len(report_data)}/{len(pdf_files)} 份成功")
    print("正在格式化输出...\n")
    
    formatted_text = format_reports_for_ai(report_data)
    
    # 保存输出
    txt_path, json_path, prompt_path = save_outputs(formatted_text, metadata, output_dir)
    
    return {
        "formatted_text": formatted_text,
        "metadata": metadata,
        "output_files": {
            "text": txt_path,
            "metadata": json_path,
            "prompt": prompt_path,
        },
        "summary": {
            "total": len(pdf_files),
            "successful": len(report_data),
            "failed": len(pdf_files) - len(report_data),
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="研报批量分析器 — 提取 PDF 文本供 AI 分析（零 API 依赖）"
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
    parser.add_argument(
        "-p", "--pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f"每份 PDF 最大提取页数 (默认: {DEFAULT_MAX_PAGES})"
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
        print(f"[ERROR] '{target}' 不是有效的 PDF 文件或目录")
        sys.exit(1)
    
    result = extract_reports(
        directory_path=directory_path,
        file_paths=file_paths,
        output_dir=args.output,
        max_pages=args.pages,
    )
    
    if result:
        print("\n" + "=" * 60)
        print("提取完成！下一步：")
        print("=" * 60)
        print(f"1. 打开文件: {result['output_files']['prompt']}")
        print("2. 复制全部内容，粘贴到你的 AI 对话中")
        print("3. AI 将自动输出 JSON 格式的分析结果")
        print("=" * 60)


if __name__ == "__main__":
    main()

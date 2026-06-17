"""
Research Report Analyzer — PDF Text Extraction Helper
======================================================
辅助工具：供 AI Agent 调用，批量提取 PDF 文本。

本脚本本身不做分析，只负责：
1. 发现目录下的 PDF 文件
2. 提取每份 PDF 的文本内容
3. 格式化输出，方便 AI 读取

用法（由 AI 自动执行）:
    python research_report_analyzer.py <目录路径> [-p 页数]
    
    输出直接打印到 stdout，AI 读取后进行分析。
"""

import os
import sys
import argparse

try:
    import pdfplumber
except ImportError:
    print("[ERROR] 缺少依赖: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)


def extract_pdf_text(file_path: str, max_pages: int = 15) -> str:
    """提取单份 PDF 的文本内容。"""
    text_parts = []
    try:
        with pdfplumber.open(file_path) as pdf:
            pages_to_read = min(len(pdf.pages), max_pages)
            for i in range(pages_to_read):
                text = pdf.pages[i].extract_text()
                if text and text.strip():
                    text_parts.append(text)
    except Exception as e:
        return f"[ERROR] 读取失败: {e}"
    
    full_text = "\n".join(text_parts)
    if len(full_text) > 15000:
        full_text = full_text[:15000] + "\n...[内容过长，已截断]"
    return full_text


def main():
    parser = argparse.ArgumentParser(description="PDF 研报文本提取工具")
    parser.add_argument("path", nargs="?", default=".", help="PDF 文件或目录路径")
    parser.add_argument("-p", "--pages", type=int, default=15, help="最大提取页数 (默认: 15)")
    args = parser.parse_args()
    
    target = args.path
    
    # 收集 PDF 文件
    if os.path.isfile(target) and target.lower().endswith(".pdf"):
        pdf_files = [target]
    elif os.path.isdir(target):
        pdf_files = sorted([
            os.path.join(target, f) for f in os.listdir(target)
            if f.lower().endswith(".pdf")
        ])
    else:
        print(f"[ERROR] 无效路径: {target}", file=sys.stderr)
        sys.exit(1)
    
    if not pdf_files:
        print("[WARN] 未找到 PDF 文件。", file=sys.stderr)
        sys.exit(0)
    
    # 提取并格式化输出
    print(f"找到 {len(pdf_files)} 份研报，开始提取...\n")
    
    for i, filepath in enumerate(pdf_files, 1):
        filename = os.path.basename(filepath)
        print(f"=== 研报《{filename}》 [第 {i}/{len(pdf_files)} 份] ===")
        print()
        text = extract_pdf_text(filepath, max_pages=args.pages)
        print(text)
        print()
        print("=" * 60)
        print()


if __name__ == "__main__":
    main()

"""
Research Report Analyzer — PDF Extraction Helper (v2)
=====================================================
Batch extract text/images from PDFs for AI analysis.

Text-based PDFs  → pdfplumber extracts text (with table support)
Image-based PDFs → pymupdf converts pages to PNG for multimodal AI reading

Usage:
    python research_report_analyzer.py <directory> [-p pages] [--image-dir dir] [--dpi 200]

Output: JSON to stdout with structured extraction results.
"""

import os
import sys
import argparse
import re
import json
import subprocess

# ---------------------------------------------------------------------------
# Dependency bootstrap
# ---------------------------------------------------------------------------

def ensure_package(name, import_name=None):
    """Try importing; if missing, pip-install then retry."""
    import_name = import_name or name
    try:
        return __import__(import_name)
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", name, "--quiet"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return __import__(import_name)

pdfplumber = None
pymupdf = None

try:
    pdfplumber = ensure_package("pdfplumber")
except Exception:
    pass

try:
    pymupdf = ensure_package("pymupdf")
except Exception:
    try:
        import fitz as pymupdf
    except ImportError:
        pass

# ---------------------------------------------------------------------------
# Watermark removal
# ---------------------------------------------------------------------------

WATERMARK_PATTERNS = [
    re.compile(r"www\.\w+\.\w{2,4}", re.IGNORECASE),
    re.compile(r"仅供内部参考"),
    re.compile(r"不构成投资建议"),
    re.compile(r"如涉及.*侵权.*请联系.*删除"),
    re.compile(r"请联系.*删除"),
    re.compile(r"手盘.*Q.*微"),
]

def clean_watermarks(text: str) -> str:
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) < 60 and any(p.search(stripped) for p in WATERMARK_PATTERNS):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)

# ---------------------------------------------------------------------------
# Extraction backends
# ---------------------------------------------------------------------------

def extract_text_pdfplumber(file_path: str, max_pages: int = 15) -> str:
    if pdfplumber is None:
        return ""
    parts = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages[:max_pages]):
                text = page.extract_text()
                if text and text.strip():
                    parts.append(text)
                for table in (page.extract_tables() or []):
                    if table:
                        rows = [" | ".join(str(c or "") for c in row) for row in table]
                        parts.append("[TABLE]\n" + "\n".join(rows) + "\n[/TABLE]")
    except Exception as e:
        return f"[ERROR] pdfplumber: {e}"
    return "\n".join(parts)


def convert_to_images(file_path: str, output_dir: str,
                      max_pages: int = 15, dpi: int = 200) -> list:
    if pymupdf is None:
        return []
    paths = []
    try:
        doc = pymupdf.open(file_path)
        base = os.path.splitext(os.path.basename(file_path))[0]
        for i, page in enumerate(doc[:max_pages]):
            img_path = os.path.join(output_dir, f"{base}_p{i + 1}.png")
            page.get_pixmap(dpi=dpi).save(img_path)
            paths.append(img_path)
        doc.close()
    except Exception as e:
        print(f"[WARN] pymupdf: {e}", file=sys.stderr)
    return paths

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def is_meaningful(text: str, min_chars: int = 100) -> bool:
    cleaned = clean_watermarks(text)
    return len(re.sub(r"\s+", "", cleaned)) >= min_chars


def process_pdfs(directory: str, max_pages: int = 15,
                 image_dir: str = None, dpi: int = 200):
    pdf_files = sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(".pdf")
    )
    if not pdf_files:
        print(json.dumps({"error": "未找到 PDF 文件", "pdf_count": 0},
                          ensure_ascii=False))
        return

    if image_dir is None:
        image_dir = os.path.join(directory, "_report_images")
    os.makedirs(image_dir, exist_ok=True)

    reports = []
    for fp in pdf_files:
        name = os.path.basename(fp)
        raw = extract_text_pdfplumber(fp, max_pages)

        if is_meaningful(raw):
            cleaned = clean_watermarks(raw)
            if len(cleaned) > 15000:
                cleaned = cleaned[:15000] + "\n...[已截断]"
            reports.append({"filename": name, "type": "text", "text": cleaned})
        else:
            imgs = convert_to_images(fp, image_dir, max_pages, dpi)
            if imgs:
                reports.append({
                    "filename": name, "type": "image",
                    "image_paths": imgs, "page_count": len(imgs),
                })
            else:
                reports.append({
                    "filename": name, "type": "error",
                    "error": "无法提取文本且无法转图片 (缺少 pymupdf)",
                })

    summary = {
        "pdf_count": len(pdf_files),
        "text_count": sum(1 for r in reports if r["type"] == "text"),
        "image_count": sum(1 for r in reports if r["type"] == "image"),
        "error_count": sum(1 for r in reports if r["type"] == "error"),
        "image_dir": image_dir,
        "reports": reports,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="PDF 研报提取工具 v2")
    parser.add_argument("path", nargs="?", default=".",
                        help="PDF 目录路径 (默认: 当前目录)")
    parser.add_argument("-p", "--pages", type=int, default=15,
                        help="最大提取页数 (默认: 15)")
    parser.add_argument("--image-dir", default=None,
                        help="图片输出目录")
    parser.add_argument("--dpi", type=int, default=200,
                        help="图片 DPI (默认: 200)")
    args = parser.parse_args()

    if pdfplumber is None and pymupdf is None:
        print("[ERROR] 需要至少安装一个: pip install pdfplumber pymupdf",
              file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(args.path):
        print(f"[ERROR] 无效目录: {args.path}", file=sys.stderr)
        sys.exit(1)

    process_pdfs(args.path, args.pages, args.image_dir, args.dpi)


if __name__ == "__main__":
    main()

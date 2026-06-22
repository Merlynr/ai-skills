#!/usr/bin/env python3
"""Archive UZI deep-analysis artifacts into Obsidian vault (stock-trade-journal)."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

SKILL_VERSION = "1.0.0"


def resolve_uzi_root() -> Path:
    if env := os.environ.get("UZI_ROOT"):
        p = Path(env)
        if (p / "run.py").exists():
            return p
    default = Path(os.environ.get("APPDATA", "")) / "skillshare/skills/uzi/_UZI-Skill"
    if (default / "run.py").exists():
        return default
    raise FileNotFoundError(
        "UZI_ROOT not found. Set UZI_ROOT or install skillshare uzi/_UZI-Skill."
    )


def resolve_vault_root() -> Path:
    if env := os.environ.get("TRADER_VAULT"):
        return Path(env)
    return Path("f:/note/20 Projects/天才交易员")


def normalize_ticker(code: str) -> str:
    code = code.strip().upper()
    if "." in code:
        return code
    if code.startswith("6"):
        return f"{code}.SH"
    if code.startswith(("0", "3")):
        return f"{code}.SZ"
    return code


def list_report_dates(reports_dir: Path, ticker: str) -> list[str]:
    prefix = f"{ticker}_"
    dates: list[str] = []
    if not reports_dir.is_dir():
        return dates
    for p in reports_dir.iterdir():
        if p.is_dir() and p.name.startswith(prefix):
            suffix = p.name[len(prefix) :]
            if re.fullmatch(r"\d{8}", suffix):
                dates.append(suffix)
    return sorted(dates)


def pick_report_date(reports_dir: Path, ticker: str, explicit: str | None) -> tuple[str, Path]:
    dates = list_report_dates(reports_dir, ticker)
    if not dates:
        raise FileNotFoundError(f"No report folder for {ticker} under {reports_dir}")
    if explicit:
        if explicit not in dates:
            raise FileNotFoundError(f"Report date {explicit} not found for {ticker}")
        return explicit, reports_dir / f"{ticker}_{explicit}"
    latest = dates[-1]
    return latest, reports_dir / f"{ticker}_{latest}"


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def dig(data: dict, *keys: str, default=None):
    cur: Any = data
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def parse_html_battle_plan(html_path: Path) -> tuple[str | None, str | None]:
    if not html_path.is_file():
        return None, None
    text = html_path.read_text(encoding="utf-8", errors="replace")
    stops = re.findall(
        r'plan-field"><span class="k">Stop</span><span class="v">¥?([^<]+)</span>',
        text,
    )
    targets = re.findall(
        r'plan-field"><span class="k">Target</span><span class="v">¥?([^<]+)</span>',
        text,
    )
    stop = stops[0].strip() if stops else None
    target = targets[0].strip() if targets else None
    return stop, target


def build_snapshot(
    ticker: str,
    report_date: str,
    report_dir: Path,
    cache_dir: Path,
    uzi_root: Path,
) -> dict[str, Any]:
    raw_path = cache_dir / "raw_data.json"
    syn_path = cache_dir / "synthesis.json"
    raw = load_json(raw_path) if raw_path.is_file() else {}
    syn = load_json(syn_path) if syn_path.is_file() else {}

    dims = raw.get("dimensions", {})
    basic = dig(dims, "0_basic", "data", default={}) or {}
    kline = dig(dims, "2_kline", "data", "indicators", default={}) or {}
    fin = dig(dims, "1_financials", "data", default={}) or {}
    lhb = dig(dims, "16_lhb", "data", default={}) or {}
    trap = dig(dims, "18_trap", "data", default={}) or {}

    html = report_dir / "full-report-standalone.html"
    model_stop, model_target = parse_html_battle_plan(html)

    rev_hist = fin.get("revenue_history") or []
    np_hist = fin.get("net_profit_history") or []
    roe_hist = fin.get("roe_history") or []
    debt = dig(fin, "financial_health", "debt_ratio")

    punchline = dig(syn, "great_divide", "punchline") or dig(syn, "debate", "punchline")
    dcf_comment = dig(syn, "dim_commentary", "10_valuation", default="")
    dcf_intrinsic = None
    m = re.search(r"内在价值([\d.]+)元", dcf_comment or "")
    if m:
        dcf_intrinsic = float(m.group(1))

    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")

    return {
        "ticker": ticker,
        "name": basic.get("name") or syn.get("name"),
        "report_date": report_date,
        "archived_at": now,
        "skill_version": SKILL_VERSION,
        "source": {
            "uzi_root": str(uzi_root),
            "reports_dir": str(report_dir),
            "cache_dir": str(cache_dir),
        },
        "quote": {
            "price": basic.get("price"),
            "change_pct": basic.get("change_pct"),
            "open": basic.get("open"),
            "high": basic.get("high"),
            "low": basic.get("low"),
            "prev_close": basic.get("prev_close"),
            "pe_ttm": basic.get("pe_ttm"),
            "pb": basic.get("pb"),
            "market_cap": basic.get("market_cap"),
        },
        "score": {
            "overall": syn.get("overall_score"),
            "verdict_label": syn.get("verdict_label"),
            "fundamental_score": syn.get("fundamental_score"),
            "panel_consensus": syn.get("panel_consensus"),
            "detected_style": syn.get("detected_style"),
            "style_label_cn": syn.get("style_label_cn"),
        },
        "technical": {
            "ma20": kline.get("ma20"),
            "ma60": kline.get("ma60"),
            "ma200": kline.get("ma200"),
            "stage": kline.get("stage"),
            "stage_label": dig(dims, "2_kline", "data", "stage"),
            "rsi_14": kline.get("rsi_14"),
            "year_high": kline.get("year_high"),
            "pct_from_year_high": kline.get("pct_from_year_high"),
            "above_ma20": kline.get("above_ma20"),
            "above_ma200": kline.get("above_ma200"),
        },
        "valuation": {
            "dcf_intrinsic": dcf_intrinsic,
            "model_stop": model_stop,
            "model_target": model_target,
            "punchline": punchline,
        },
        "risk": {
            "lhb_count_30d": lhb.get("lhb_count_30d"),
            "trap_level": trap.get("trap_level"),
            "risks": syn.get("risks") or [],
        },
        "financials": {
            "revenue_latest": rev_hist[-1] if rev_hist else None,
            "net_profit_latest": np_hist[-1] if np_hist else None,
            "roe_latest": roe_hist[-1] if roe_hist else None,
            "debt_ratio": debt,
            "revenue_growth": fin.get("revenue_growth"),
        },
        "buy_zones": syn.get("buy_zones") or {},
    }


def update_readme(readme: Path, ticker: str, report_date: str, name: str) -> None:
    line = f"| {ticker} | {name or '—'} | {report_date} | [[{ticker}/{report_date}/snapshot.json\\|快照]] |"
    header = "| 代码 | 名称 | 最新报告日 | 快照 |\n|------|------|------------|------|\n"
    if readme.is_file():
        content = readme.read_text(encoding="utf-8")
        pattern = re.compile(
            rf"^\| {re.escape(ticker)} \|.*$",
            re.MULTILINE,
        )
        if pattern.search(content):
            content = pattern.sub(line, content)
        elif "| 代码 | 名称 |" in content:
            content = content.rstrip() + "\n" + line + "\n"
        else:
            content = content.rstrip() + "\n\n## 索引\n\n" + header + line + "\n"
    else:
        content = (
            "---\ntitle: UZI 快照索引\ntype: uzi-snapshot-index\n---\n\n"
            "# UZI 快照索引（笔记库归档）\n\n"
            "> 由 `stock-trade-journal` / `archive_uzi_snapshot.py` 维护。"
            " APPDATA 报告删除后，以本目录为准。\n\n"
            "## 索引\n\n"
            + header
            + line
            + "\n"
        )
    readme.write_text(content, encoding="utf-8")


def archive_one(ticker: str, report_date: str | None, force: bool) -> Path:
    uzi_root = resolve_uzi_root()
    vault = resolve_vault_root()
    scripts = uzi_root / "skills/deep-analysis/scripts"
    reports_dir = scripts / "reports"
    cache_dir = scripts / ".cache" / ticker

    date, report_dir = pick_report_date(reports_dir, ticker, report_date)
    dest = vault / "04-实操日志/uzi-snapshots" / ticker / date
    manifest_path = dest / "manifest.json"

    if manifest_path.is_file() and not force:
        existing = load_json(manifest_path)
        if existing.get("source", {}).get("reports_dir") == str(report_dir):
            print(f"[skip] {ticker}/{date} already archived")
            return dest

    dest.mkdir(parents=True, exist_ok=True)

    for fname in ("one-liner.txt", "full-report-standalone.html"):
        src = report_dir / fname
        if src.is_file():
            shutil.copy2(src, dest / fname)

    snapshot = build_snapshot(ticker, date, report_dir, cache_dir, uzi_root)
    (dest / "snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    manifest = {
        "ticker": ticker,
        "report_date": date,
        "archived_at": snapshot["archived_at"],
        "skill_version": SKILL_VERSION,
        "source_reports": str(report_dir),
        "source_cache": str(cache_dir),
        "files": sorted(p.name for p in dest.iterdir() if p.is_file()),
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    readme = vault / "04-实操日志/uzi-snapshots/README.md"
    update_readme(readme, ticker, date, snapshot.get("name") or "")

    print(f"[ok] {ticker}/{date} -> {dest}")
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive UZI reports into Obsidian vault")
    parser.add_argument("tickers", nargs="+", help="e.g. 600121.SH or 600121")
    parser.add_argument("--date", help="Report date YYYYMMDD (default: latest)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing archive")
    args = parser.parse_args()

    ok = 0
    for raw in args.tickers:
        ticker = normalize_ticker(raw)
        try:
            archive_one(ticker, args.date, args.force)
            ok += 1
        except Exception as e:
            print(f"[err] {ticker}: {e}", file=sys.stderr)
    return 0 if ok == len(args.tickers) else 1


if __name__ == "__main__":
    raise SystemExit(main())

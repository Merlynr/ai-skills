# UZI 数据归档 · stock-trade-journal 专用

复盘读取 UZI 后，**必须把证据写入笔记库**，避免 `%APPDATA%` / skillshare 缓存被清理后无法对照历史。

**SSOT**：本文件定义目录、文件、读取优先级；执行入口见 [scripts/archive_uzi_snapshot.py](scripts/archive_uzi_snapshot.py)。

---

## 1. 笔记库归档根目录

| 项 | 路径（相对天才交易员项目） |
|----|---------------------------|
| 归档根 | `04-实操日志/uzi-snapshots/` |
| 单标的 | `04-实操日志/uzi-snapshots/{TICKER}/{YYYYMMDD}/` |
| 索引 | `04-实操日志/uzi-snapshots/README.md` |

**绝对路径默认**：`f:/note/20 Projects/天才交易员/04-实操日志/uzi-snapshots/`

解析优先级：

1. 环境变量 `TRADER_VAULT` → `{TRADER_VAULT}/04-实操日志/uzi-snapshots`
2. workspace 含 `20 Projects/天才交易员` → 相对该目录
3. 否则 `f:/note/20 Projects/天才交易员/04-实操日志/uzi-snapshots`

---

## 2. 每只标的 · 每个报告日 · 归档什么

| 文件 | 必需 | 来源 | 用途 |
|------|:----:|------|------|
| `one-liner.txt` | ✅ | `reports/{TICKER}_{date}/` | 评分/定调/punchline 原文 |
| `snapshot.json` | ✅ | 由 `.cache` 合成 | 复盘表格、后续读取 SSOT |
| `manifest.json` | ✅ | 脚本生成 | 溯源、是否需更新 |
| `full-report-standalone.html` | 推荐 | `reports/.../` | 离线打开完整报告（~800KB/只） |

**不归档**（体积大、可重跑 UZI）：`panel.json` 全量、`dimensions.json`、`api_cache/`。

### `snapshot.json` 最小字段（脚本已覆盖）

```json
{
  "ticker": "600121.SH",
  "name": "郑州煤电",
  "report_date": "20260608",
  "archived_at": "2026-06-08T22:30:00+08:00",
  "source": {
    "reports_dir": ".../reports/600121.SH_20260608",
    "cache_dir": ".../.cache/600121.SH"
  },
  "quote": { "price", "change_pct", "open", "high", "low", "prev_close", "pe_ttm", "pb", "market_cap" },
  "score": { "overall", "verdict_label", "fundamental_score", "panel_consensus", "detected_style" },
  "technical": { "ma20", "ma60", "ma200", "stage", "rsi_14", "year_high", "pct_from_year_high" },
  "valuation": { "dcf_intrinsic", "model_stop", "model_target", "punchline" },
  "risk": { "lhb_count_30d", "trap_level", "risks" },
  "financials": { "revenue_latest", "net_profit_latest", "roe_latest", "debt_ratio" },
  "buy_zones": {}
}
```

`model_stop` / `model_target`：优先从 HTML `plan-field` 解析；失败则留 `null`。

---

## 3. 读取优先级（复盘第 1.11 步）

```
1. 笔记库 uzi-snapshots/{TICKER}/{YYYYMMDD}/snapshot.json + one-liner.txt
   └─ 条件：report_date 为该股最新归档日，或 ≥ 日志日 - 3 交易日
2. APPDATA reports/ 最新 {TICKER}_{date}/
3. APPDATA .cache/{TICKER}/raw_data.json + synthesis.json（注明「无 HTML，用 cache」）
```

**规则**：

- 若从 **2/3** 读到数据 → **同一回合必须执行归档**（第 1.11a 步），再写日志。
- 日志 §八 链接 **笔记库相对路径** 为主，`file:///` APPDATA 为辅（标注「可能过期」）。

Obsidian 链接示例：

```markdown
[[uzi-snapshots/600121.SH/20260608/snapshot|600121 UZI 快照 06-08]]
```

---

## 4. 何时归档

| 时机 | 动作 |
|------|------|
| 每次 `stock-trade-journal` 涉及某 ticker | 归档该股**最新**报告日（若 vault 无该日或 `--force`） |
| 用户口述持仓/观察 ≥1 只 | 同上，逐只归档 |
| 仅更新持仓对照、未写日志 | 可选单独跑脚本 |

**幂等**：同 `{TICKER}/{YYYYMMDD}` 已存在且 `manifest.json` 中 `source_reports` 未变 → 跳过（除非 `--force`）。

---

## 5. 执行方式

### 5.1 脚本（推荐）

脚本路径（skillshare SSOT）：

`%APPDATA%\skillshare\skills\stock-trade-journal\scripts\archive_uzi_snapshot.py`

```powershell
$script = "$env:APPDATA\skillshare\skills\stock-trade-journal\scripts\archive_uzi_snapshot.py"

# 单只
python $script 600121.SH

# 多只 + 指定报告日
python $script 600121.SH 600362.SH 002995.SZ --date 20260608

# 强制覆盖
python $script 600121.SH --force
```

环境变量（可选）：

| 变量 | 默认 |
|------|------|
| `UZI_ROOT` | `%APPDATA%\skillshare\skills\uzi\_UZI-Skill` |
| `TRADER_VAULT` | `f:/note/20 Projects/天才交易员` |

### 5.2 Agent 手工（脚本失败时）

1. `mkdir` 归档目录  
2. `Copy-Item` `one-liner.txt`、`full-report-standalone.html`  
3. Read `.cache/.../raw_data.json` + `synthesis.json` → Write `snapshot.json`（字段见 §2）  
4. Write `manifest.json`  
5. 更新 `uzi-snapshots/README.md` 索引行  

---

## 6. 与汇总笔记的关系

| 文件 | 关系 |
|------|------|
| `00-UZI{N}股分析-{date}.md` | 人类可读摘要；**底部必须链** `uzi-snapshots/` 各股目录 |
| `00-当前持仓对照.md` | `source_uzi` + 链最新 `snapshot` |
| `YYYY-MM-DD 实操反思.md` | frontmatter 增加 `uzi_snapshots: ["600121.SH/20260608", ...]` |

汇总笔记里的现价/评分，须注明「来自 `snapshot.json` · {report_date}」。

---

## 7. 缺失与失败

| 情况 | 动作 |
|------|------|
| APPDATA 无报告 | 日志标「未分析」；vault 有旧快照则用旧快照并注明日期 |
| 脚本失败 | 手工复制 one-liner + 写最小 snapshot；禁止跳过归档步 |
| HTML 复制失败 | 仍须 `snapshot.json` + `one-liner.txt` |
| Git 体积 | HTML 可选；`snapshot.json` 必保留 |

# UZI 报告读取 · stock-trade-journal 专用

复盘时**必须用 UZI 盘面证据**交叉验证用户口述，禁止只凭用户描述或记忆写「盘面核对」。

**读完必须归档** → [uzi-archive.md](uzi-archive.md)（`04-实操日志/uzi-snapshots/`），避免 APPDATA 缓存被删后证据丢失。

---

## 0. 读取总优先级（第 1.11 步）

| 优先级 | 来源 | 读什么 |
|:------:|------|--------|
| **1** | 笔记库 `04-实操日志/uzi-snapshots/{TICKER}/{YYYYMMDD}/` | `snapshot.json` + `one-liner.txt`（复盘 SSOT） |
| 2 | APPDATA `reports/{TICKER}_{date}/` | `one-liner.txt` + HTML 关键字段 |
| 3 | APPDATA `.cache/{TICKER}/` | `raw_data.json` + `synthesis.json` |

从 **2 或 3** 读到 → **同一回合执行第 1.11a 归档**（`scripts/archive_uzi_snapshot.py`）。

笔记库路径默认：`f:/note/20 Projects/天才交易员/04-实操日志/uzi-snapshots/`

---

## 1. 报告根目录（live · 优先级 2）

| 优先级 | 路径 |
|:------:|------|
| 1 | 当前 workspace 下 `skills/uzi/_UZI-Skill/skills/deep-analysis/scripts/reports/` |
| 2 | `%APPDATA%\skillshare\skills\uzi\_UZI-Skill\skills\deep-analysis\scripts\reports\` |
| 3 | 用户消息中的 `file:///.../reports/` 去掉 `file:///` 前缀 |

`browser` 打开：`file:///C:/Users/lcq/AppData/Roaming/skillshare/skills/uzi/_UZI-Skill/skills/deep-analysis/scripts/reports/{文件夹}/full-report-standalone.html`

---

## 2. 代码规范化

用户常说 6 位数字，报告文件夹用 **带后缀** 名：

| 输入示例 | 报告前缀 | 规则 |
|----------|----------|------|
| `000100` / `TCL` | `000100.SZ` | 0/3 开头 → `.SZ` |
| `600121` / `600362` | `600121.SH` / `600362.SH` | 6 开头 → `.SH` |
| `002995` | `002995.SZ` | 0/3 开头 → `.SZ` |

不确定时：在 `reports/` 下 `Glob` 或 `dir` 匹配 `{code}*`。

---

## 3. 选取「最新一份」报告

文件夹命名：`{TICKER}_{YYYYMMDD}/`（例 `600121.SH_20260608`）。

1. 列出所有匹配 `{TICKER}_*` 的目录  
2. 取 **日期后缀最大** 的一份（最新抓取）  
3. 若无报告 → 读同 ticker 的 `.cache/{TICKER}/raw_data.json`（与 reports 同源），并在日志注明「无 HTML，用 cache」

---

## 4. 每只股票最少读取什么

对当日日志涉及的**每一只**标的（含已清仓、仅观察），按序 Read：

| 顺序 | 文件 | 提取字段 |
|:----:|------|----------|
| 0 | `uzi-snapshots/{TICKER}/{date}/snapshot.json` | 见 [uzi-archive.md §2](uzi-archive.md)（笔记库已有则优先） |
| 1 | `{文件夹}/one-liner.txt` | 评分、定调、DCF 一句话、杀猪盘 |
| 2 | `{文件夹}/full-report-standalone.html` | 用 Grep/Read 抽：`class="price"`、`score-giant`、`score-verdict`、`battle-plan` 四行、`punchline`、龙虎榜次数 |
| 3（可选） | `.cache/{TICKER}/raw_data.json` | `dimensions.0_basic.data`、日 K、`synthesis.json` |

**禁止**：未打开报告/cache 就写「UZI 显示…」；禁止编造现价、评分、龙虎榜次数。

---

## 5. 从 HTML 快速抽取（Grep 模式）

在 `full-report-standalone.html` 上：

```
class="price"          → 现价
score-giant            → 综合分
score-verdict          → 定调一句
plan-field.*Stop       → 模型止损
plan-field.*Target     → 模型目标
punchline              → 核心矛盾
round-bull / round-bear → 多空论点
zone-price             → 技术支撑区（若有）
内在价值 / 每股内在价值  → DCF
30 天上榜|龙虎榜         → LHB 频率
year_high              → 年内高点（若有）
```

`one-liner.txt` 通常已含评分 + DCF 矛盾 + 杀猪盘，**必须先读**。

---

## 6. 与用户描述交叉验证（写入日志 §四）

每只标的填一行表（模板见 SKILL 第 3 步）：

| 列 | 来源 |
|----|------|
| 你的理解 | 用户原话 / 操作动机 |
| UZI/盘面验证 | 报告现价、日 K 关键位、LHB、评委分歧、与用户成交价对比 |
| 结论 | ✅对 / ❌错 / 🟡一半对；一句话 |

**对照要点**：

- 用户**买入价** vs 当日 K 线（追涨 / 下跌摊仓 / 合理回踩）  
- 用户**卖出价** vs 近期高点、模型止损、上影/放量描述  
- 用户**持有理由**（朋友推荐、价投、等回本）vs UZI 基本面/评委/杀猪盘  
- **DCF 低估** vs 当期亏损/营收萎缩 → 须写「模型与财报脱节，守铁律线」

---

## 7. 后续操作建议（§九）如何引用 UZI

每只持仓写 **铁律止损** + **UZI 参考** 两行，格式：

```markdown
**{代码} {名称} · {股数} @ {成本}**
- UZI（{报告日期}）：现价 ¥X · 评分 Y · {定调} · 模型止损 ¥A / 目标 ¥B
- **明日**：{铁律触发价} → {减仓%}（铁律优先；模型止损仅作背景）
```

- **铁律止损**优先于 UZI Battle Plan 的 Entry/Stop（模型常按长周期，与短线持仓成本不一致）  
- 技术支撑可取报告 `zone-price` / MA200，但须在日志写明来源  
- 无报告的股票：建议用户先跑 `uzi-analysis-stack` 或 `deep-analysis`，复盘里标「缺 UZI，仅用户口述」

---

## 8. 写回持仓/存档

**强制**（第 1.11a 步）：每只涉及标的归档至 `uzi-snapshots/` — 见 [uzi-archive.md](uzi-archive.md)。

**可选汇总**（≥2 只或持仓变动时）：

- `04-实操日志/00-当前持仓对照.md` §五「明日一条」  
- `04-实操日志/00-UZI{N}股分析-{最新报告日期}.md`（人类可读；**底部链** `uzi-snapshots/`）

frontmatter `source_uzi` 填报告日期后缀；日志 `uzi_snapshots` 列归档路径。

---

## 9. 缺失与失败处理

| 情况 | 动作 |
|------|------|
| 无 `{TICKER}_*` 目录 | 尝试 `.cache`；仍无则日志标「未分析」，建议补跑 UZI |
| 报告日期早于日志日 3 个交易日以上 | 仍可使用，但注明「行情截至 YYYY-MM-DD，盘中以券商为准」 |
| Eastmoney 字段空（industry/资金流） | 不编造；用已有 K 线/财务/龙虎榜 |
| DCF 与巨亏/营收萎缩矛盾 | 必须引用 one-liner / punchline 原话，执行以铁律为准 |

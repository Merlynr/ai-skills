---
name: uzi-analysis-stack
description: >-
  Merlynr 股票深度分析工作流栈 — 将 UZI-Skill 接入 skillshare：分级路由、证据优先、
  nmem 沉淀。Use when 分析股票、估值、DCF、杀猪盘、龙虎榜、快速扫一眼、能不能买、
  uzi、游资分析、深度分析。
tags: [workflow, stack, uzi, finance, stocks, analysis, merlynr]
triggers:
  - uzi
  - UZI
  - 分析股票
  - 深度分析
  - 能不能买
  - 杀猪盘
  - DCF
  - 游资
tool_chain:
  - stock-trade-journal
  - search-memory
  - distill-memory
context_injection: true
---

# UZI Analysis Stack

Merlynr 侧**唯一权威**的股票分析工作流层。不修改 UZI-Skill 上游；所有路由、路径、沉淀规则写在本 skill 及兄弟文件。

## 设计原则

1. **证据优先**：结论必须来自 UZI 脚本输出（JSON/HTML），不凭印象编数字。
2. **分级路由**：按用户意图选 lite / medium / deep（见 [analysis-routing.md](analysis-routing.md)）。
3. **门面 + SSOT**：cursor/opencode/agents 只 sync 本 skill；完整 UZI 引擎路径见下文「路径解析」。
4. **nmem 可选沉淀**：重要结论用 `distill-memory`；日常会话内结论不强制。
5. **与反思分工**：分析用本 stack；收盘实操反思用 `stock-trade-journal`，勿混用。

## 任务分级路由

| 用户信号 | 级别 | 命令文档 | 典型耗时 |
|----------|------|----------|----------|
| 「快速看看」「先扫一眼」「30 秒」 | **lite** | [commands/quick-scan.md](commands/quick-scan.md) | ~1–2 min |
| 「分析 XXX」「能不能买」「值不值得」 | **medium** | [commands/analyze-stock.md](commands/analyze-stock.md) | 5–8 min |
| 「深度研究」「估值」「首次覆盖」 | **deep** | [commands/analyze-stock.md](commands/analyze-stock.md) | 15–20 min |
| 「DCF」「内在价值」 | **deep** | [commands/dcf.md](commands/dcf.md) | 专项 |
| 「杀猪盘」「是不是庄」「陷阱」 | **lite+** | [commands/scan-trap.md](commands/scan-trap.md) | ~1 min |

**先读** [analysis-routing.md](analysis-routing.md) 再执行。

## 工作流（U0–U4）

```plaintext
U0   需求确认（代码/名称、级别、专项：DCF/杀猪盘/龙虎榜）
U1   环境与路径（解析 UZI_ROOT，pip 依赖）
U2   执行 UZI（run.py 或专项 skill）
U3   读产物 + 中文摘要（见 report-template.md）
U4   可选 nmem + 链 stock-trade-journal
```

### U0：需求确认

- 股票：优先标准代码（`600519.SH` / `00700.HK` / `AAPL`）；中文名可试，失败则请用户提供代码。
- 深度：用户未说明时，「分析/能不能买」→ **medium**；「看看」→ **lite**。
- 专项：DCF / 杀猪盘 / 龙虎榜 → 见 analysis-routing 专项表。

### U1：路径与环境

**路径解析（按优先级）：**

1. 环境变量 `UZI_ROOT`（若已 export）
2. `{SKILLSHARE_SKILLS}/uzi/_UZI-Skill`（tracked 上游，推荐）
3. `{SKILLSHARE_SKILLS}/../uzi/_UZI-Skill` 失败时：`~/.config/skillshare/skills/uzi/_UZI-Skill`
4. 独立安装：`~/UZI-Skill`

`SKILLSHARE_SKILLS` 默认 `~/.config/skillshare/skills`（Windows：`%APPDATA%/skillshare/skills`）。

**首次安装（本机未 clone 时）：**

```bash
cd ~/.config/skillshare
./script/setup-tracked-uzi.sh
pip install -r skills/uzi/_UZI-Skill/requirements.txt
# 若 deep 模式缺浏览器：playwright install chromium
```

**执行前检查：**

```bash
test -f "${UZI_ROOT}/run.py" && python3 --version
```

### U2：执行

**统一入口（repo 根目录，不是 scripts 子目录）：**

```bash
cd "${UZI_ROOT}"
python3 run.py <TICKER> --no-browser --depth <lite|medium|deep>
```

Codex/CI 必须加 `--no-browser`。需要公网查看报告时加 `--remote`。

深度优先级：`--depth` 参数 > `UZI_DEPTH` 环境变量 > 默认 medium。

**产物目录（相对 `skills/deep-analysis/scripts/`）：**

| 产物 | 路径 |
|------|------|
| HTML 报告 | `reports/<ticker>_<date>/full-report-standalone.html` |
| 合成 JSON | `.cache/<ticker>/synthesis.json` |
| 评委面板 | `.cache/<ticker>/panel.json` |

`SCRIPTS_DIR="${UZI_ROOT}/skills/deep-analysis/scripts"`

### U3：结论提炼

按 [report-template.md](report-template.md) 输出简体中文摘要：评分、定调、Top 看多/看空、DCF（若有）、杀猪盘等级、主要风险。

**禁止**未读 JSON/HTML 就编造分数或估值。

### U4：沉淀（可选）

| 场景 | 动作 |
|------|------|
| 用户要「记住这次分析」 | `distill-memory` → nmem |
| 用户要「写今日反思/实操日志」 | 转 `stock-trade-journal`（分析结论作输入） |
| 纯 lite 速扫 | 通常不写 nmem |

nmem 标题格式见 [analysis-routing.md § nmem](analysis-routing.md#nmem-写入格式)。

## 命令映射（Agent 话术 → 文档）

用户或 slash 提到下列意图时，Read 对应 `commands/*.md` 并按其中步骤执行：

| 用户说法 | 文档 |
|----------|------|
| `/uzi:analyze-stock` 或「深度分析 XXX」 | [commands/analyze-stock.md](commands/analyze-stock.md) |
| `/uzi:quick-scan` 或「快速看看 XXX」 | [commands/quick-scan.md](commands/quick-scan.md) |
| `/uzi:dcf` 或「算 DCF XXX」 | [commands/dcf.md](commands/dcf.md) |
| `/uzi:scan-trap` 或「查杀猪盘 XXX」 | [commands/scan-trap.md](commands/scan-trap.md) |

> UZI 官方 Claude 插件命名空间为 `stock-deep-analyzer:*`；Merlynr 统一用 `/uzi:*` 指本 stack 下的命令文档。

## 与 merlynr-dev-stack 的关系

| Stack | 职责 |
|-------|------|
| **merlynr-dev-stack** | 通用开发 S/M/L、GSD 生命周期、代码库证据 |
| **uzi-analysis-stack**（本 skill） | 股票分析 U0–U4、UZI 路径与产物 |
| **stock-trade-journal** | 天才交易员实操反思、铁律、课程对齐 |
| **UZI-Skill 上游** | Python 引擎（22 维 + 评委 + 报告） |

开发任务走 Merlynr；个股研究走 UZI；两者勿在同一 turn 混路由。

## 与 skillshare target 的关系

| Target | 暴露内容 |
|--------|----------|
| cursor / opencode / agents | **仅** `uzi-analysis-stack`（门面） |
| codex | 全量 skill；执行 UZI 时仍优先读本 SKILL 再 `run.py` |

门面 target 未 sync `uzi__deep-analysis` 时，需要读上游 SKILL ：

```plaintext
{SKILLSHARE_SKILLS}/uzi/_UZI-Skill/skills/deep-analysis/SKILL.md
```

## 附加资源

- [analysis-routing.md](analysis-routing.md) — 路由、平台、专项、nmem
- [report-template.md](report-template.md) — 交付摘要模板
- [commands/](commands/) — 分命令执行说明

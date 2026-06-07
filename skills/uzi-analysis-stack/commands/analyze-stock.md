# /uzi:analyze — 个股分析（medium / deep · fast | full）

**触发**: 分析、能不能买、值不值得、完整/增强分析、持仓决策、深度研究、首次覆盖、补救升级

**参数**: `$ARGUMENTS` = 股票名称或代码；可选深度词；可选成本价

**前置**（U0 前）:

1. Read [../analysis-routing.md](../analysis-routing.md) — **仅**平台、专项、nmem、故障（**不含** depth×mode 矩阵）
2. Read [../report-template.md](../report-template.md)

---

## U0 — 门控（必须先输出，再进 U2）

**在进入任何 Shell 或写文件之前，Agent 必须向用户（或内部 handoff）明确输出：**

```markdown
- ticker: <标准码>
- depth: lite | medium | deep
- mode: fast | full
- 入口: quick-scan | analyze-fast | analyze-full | analyze-full-remedial
```

**禁止**未输出 U0 就执行 U2。  
**禁止**把 `run.py --depth deep` 当作 full（仍是骨架，`agent_reviewed: false`）。

### 深度 × 模式矩阵（唯一 SSOT）

本表为 **depth × mode 唯一权威**；`analysis-routing.md` / `SKILL.md` 只引用本节，不重复表格。

| 用户信号 | depth | mode | 入口 |
|----------|-------|------|------|
| 快速看看 / 先扫一眼 / 30 秒 | **lite** | fast | → [quick-scan.md](quick-scan.md) **STOP** |
| 分析 / 能不能买 / 值不值得（**未**要完整） | medium | **fast** | § U2-FAST |
| 同上 + 完整/增强/不要骨架/agent 增强 | medium | **full** | § U2-FULL |
| 给了**成本价**或问**持仓怎么办** | medium | **full** | § U2-FULL |
| 深度研究 / 估值 / 首次覆盖 / DCF 级研究 | **deep** | **full** | § U2-FULL（**禁止**仅 `--depth deep` + run.py） |
| 已有 run.py 缓存 + `agent_reviewed: false` + 要更好报告 | 原 depth | **full** | § U2-FULL-REMEDIAL |
| DCF 专项演算 | deep | full | 可先 § U2-FULL，或 [dcf.md](dcf.md) |
| 杀猪盘 / 是不是庄 | lite+ | fast | → [scan-trap.md](scan-trap.md) **STOP** |

**硬规则**:

- `depth=deep` **默认** `mode=full`，除非用户明确说「deep 但不用 agent / 骨架就行」。
- `mode=fast` 时 **禁止** 写 `agent_analysis.json` 或声称「完整增强报告」。
- `mode=full` 时 **禁止** 用 `run.py` 一键代替 stage1→JSON→stage2（collect 可复用 run.py 缓存，见补救节）。

### 双轨对照（run.py vs stage1/stage2）

| 路径 | 命令 | agent_analysis | agent_reviewed |
|------|------|----------------|----------------|
| **fast** | `run.py`（v3 pipeline） | 无 | **false**（预期） |
| **full** | `stage1` 或复用 run.py 缓存 → Agent JSON → `stage2` | **有** | **true** |

`run.py` 日志出现 `skip legacy stage1/stage2` 仍属 **fast 骨架**；full 必须 stdout 含 `🧠 Agent 分析已加载`。

### 路径常量

```bash
export UZI_ROOT="${UZI_ROOT:-${SKILLSHARE_SKILLS:-$HOME/.config/skillshare/skills}/uzi/_UZI-Skill}"
export SCRIPTS="${UZI_ROOT}/skills/deep-analysis/scripts"
export CACHE="${SCRIPTS}/.cache/<TICKER>"
```

Windows（PowerShell，下文 2a/2d 均用此常量）：

```powershell
$env:UZI_ROOT = "$env:APPDATA\skillshare\skills\uzi\_UZI-Skill"
$env:SCRIPTS = "$env:UZI_ROOT\skills\deep-analysis\scripts"
$env:PYTHONUTF8 = "1"
```

---

## U1 — 环境（mode 判定后）

```bash
test -f "${UZI_ROOT}/run.py" && python3 --version
```

缺依赖：`pip install -r "${UZI_ROOT}/requirements.txt"`

---

## U2-FAST — run.py 一键（仅 mode=fast）

```bash
cd "${UZI_ROOT}"
python3 run.py <TICKER> --no-browser --depth <medium|deep>
```

- Windows：**用户 PowerShell 本地跑**（8–10 min）；Agent 只下发命令，勿单命令阻塞等待。
- 读 `${CACHE}/synthesis.json`、`panel.json`
- 交付标注 **`执行模式: fast（骨架）`**，`agent_reviewed: false` 为预期
- **升级 full**：若用户**在同一会话**改口说「完整分析 XXX」或「补救升级」→ **停止 U2-FAST**，回到 § U0 重新判定 `mode=full`，再进 § U2-FULL（**不得**在当前 fast 流程内继续写 JSON）

**STOP** — fast 路径到此结束，勿进入 U2-FULL。

---

## U2-FULL — stage1 → Agent JSON → stage2（仅 mode=full）

**full 前置（本节才 Read）:**

1. [../agent-analysis-schema.md](../agent-analysis-schema.md)
2. 字段冲突时：`$UZI_ROOT/skills/deep-analysis/SKILL.md` 中 `agent_analysis.json` 示例

### 2a. 数据采集（无缓存时）

若 `${CACHE}/raw_data.json` **不存在** → 先 stage1（8–15 min，**用户 Shell**）：

```bash
cd "${SCRIPTS}"
export PYTHONUTF8=1
python3 -c "from run_real_test import stage1; stage1('<TICKER>')"
```

PowerShell（用 § U0 路径常量 `$env:SCRIPTS`）：

```powershell
python -c "from run_real_test import stage1; stage1('600362.SH')"
```

完成标志：`panel.json` + `raw_data.json` 存在。

### 2b. U2-FULL-REMEDIAL — 已有 run.py 缓存

若用户已跑 `run.py` 且 `${CACHE}/raw_data.json` 存在 → **跳过 2a**，从 2c 开始。

交付说明：「报告已从骨架升级为增强版」。

### 2c. Agent 增强 — 写 agent_analysis.json（Agent，2–8 min）

**必须由 Agent 完成，不可跳过。**

1. Read `${CACHE}/panel.json`
2. Read `${CACHE}/raw_data.json`（过大则按 dim key 分段）
3. 可选 Read `$UZI_ROOT/skills/deep-analysis/references/task2.5-qualitative-deep-dive.md`
4. **Write** `${CACHE}/agent_analysis.json` — 见 schema
5. `"agent_reviewed": true`
6. 成本价：写入 `narrative_override` 或交付摘要；**禁止**伪造 JSON 里没有的价格

**禁止**: 未读 panel/raw_data 就写；`dim_commentary` 用 list 代替 dict。

### 2d. Stage 2 — 合并 HTML（1–3 min）

```bash
cd "${SCRIPTS}"
python3 -c "from run_real_test import stage2; stage2('<TICKER>')"
```

**成功标志**:

- stdout: `🧠 Agent 分析已加载 · agent_analysis.json`
- `synthesis.json` 中 `agent_reviewed: true`
- 无 `_agent_analysis_errors.json`（有则修正 JSON 后重跑 stage2）

```bash
python3 -c "import json; s=json.load(open('.cache/<TICKER>/synthesis.json')); print(s.get('agent_reviewed'))"
```

### Agent 超时规避

| 步骤 | 执行者 | 耗时 |
|------|--------|------|
| stage1 / run.py collect | **用户 Shell** | 8–15 min |
| 写 agent_analysis.json | **Agent** | 2–8 min |
| stage2 | Agent 或用户 Shell | 1–3 min |

---

## U3 — 交付（fast / full 共通）

Read `synthesis.json` + `panel.json`，按 [report-template.md](../report-template.md) 输出中文摘要 + HTML 路径。

| mode | 必须标注 |
|------|----------|
| fast | `执行模式: fast（骨架）` · `agent_reviewed: false` |
| full | `执行模式: full（含 agent_analysis + stage2）` · `agent_reviewed: true` |

**禁止**未读 JSON 编造分数。

---

## U4 — 可选沉淀

deep / 持仓决策 / 用户要求 → `distill-memory`（见 analysis-routing § nmem）

---

## 合并后验收（5 条，须全部通过）

1. 「分析 600362」→ 仅 U2-FAST · `agent_reviewed: false`
2. 「完整分析 600362」→ U2-FULL · stdout 含 Agent 已加载 · `agent_reviewed: true`
3. 先 1 再「补救升级」→ U2-FULL-REMEDIAL · 跳过 stage1
4. 「快速看看 600362」→ [quick-scan.md](quick-scan.md)，不进本文
5. 「深度研究 600362」若误跑 `run.py --depth deep` → 仍须 `agent_reviewed: false`（证明 deep≠full）；正确路径为 U0 判定 full 后走 U2-FULL

---

## 禁止（总）

- 未跑脚本就输出评分
- deep 关键词却只 `run.py --depth deep` 而不走 full
- fast 模式下声称含 Agent 增强层
- full 未写 agent_analysis 就声称完整增强报告

## 上游

`$UZI_ROOT/skills/deep-analysis/SKILL.md` — Stage 1/2 HARD-GATE 全文

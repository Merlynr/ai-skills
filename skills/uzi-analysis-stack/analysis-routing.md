# 分析路由

UZI Analysis Stack 的工具与意图路由。**平台表为 SSOT**（`SKILL.md` 不重复展开）。

> **深度 × 模式矩阵 SSOT** → 仅 [commands/analyze-stock.md § U0](commands/analyze-stock.md#u0--门控必须先输出再进-u2)。本节不重复该表，只保留 fast/full 概念与平台/专项/nmem。

## 按平台默认路径

| 平台 | 记忆 | UZI 执行 | 读产物 |
|------|------|----------|--------|
| **Codex** | nmem / `search-memory` | Shell：`python3 ${UZI_ROOT}/run.py …` | Read JSON/HTML under `scripts/` |
| **Cursor** | `read-working-memory` | Shell（同左） | Read |
| **OpenCode** | `read-working-memory` | Shell 或 explore 辅助查 ticker | Read |

```plaintext
所有平台 → 先读本 stack SKILL.md → 解析 UZI_ROOT → 选 fast|full → 执行
禁止 → 不检查路径直接凭记忆写分析报告
禁止 → full 模式跳过 agent_analysis.json 仍称「完整增强」
```

## 执行模式：fast vs full

| 模式 | 命令 | agent_analysis | synthesis | 适用 |
|------|------|----------------|-----------|------|
| **fast** | `run.py` 一键 | 无 | 骨架，`agent_reviewed: false` | lite/medium 速查、聊天摘要 |
| **full** | stage1 → Agent JSON → stage2 | **有** | 增强，`agent_reviewed: true` | 持仓/成本价、deep、首次覆盖、要高质量 HTML |

**路由规则（U0）** → 见 [analyze-stock.md § U0 矩阵](commands/analyze-stock.md#u0--门控必须先输出再进-u2)（**唯一 SSOT**，含 depth × mode 与 STOP 规则）。

执行入口：[commands/analyze-stock.md](commands/analyze-stock.md)（fast / full / 补救统一）

### Agent 超时规避（Windows / Cursor）

| 步骤 | 执行者 | 耗时 |
|------|--------|------|
| stage1 或 run.py collect | **用户 PowerShell**（Agent 仅给命令） | 8–15 min |
| 写 agent_analysis.json | **Cursor Agent** | 2–8 min |
| stage2 | Agent 或用户（短） | 1–3 min |

Agent **不要**单条 Shell 阻塞等待 medium 全量 `run.py`；应拆分或让用户本地跑 stage1。

### full 模式验收（单次 run 技术项）

- [ ] `.cache/<TICKER>/agent_analysis.json` 存在且 `agent_reviewed: true`
- [ ] stage2 stdout 含「Agent 分析已加载」
- [ ] 交付摘要标注 `执行模式: full`

### 栈级回归（5 条，改 skill / 合并路由后必跑）

完整用例与通过标准 → [commands/analyze-stock.md § 合并后验收](commands/analyze-stock.md#合并后验收5-条须全部通过)（**唯一清单**，本节不重复展开）。

| # | 触发语 | 预期 |
|---|--------|------|
| 1 | 分析 600362 | U2-FAST · `agent_reviewed: false` |
| 2 | 完整分析 600362 | U2-FULL · Agent 已加载 · `agent_reviewed: true` |
| 3 | 先 1 再补救升级 | U2-FULL-REMEDIAL · 跳过 stage1 |
| 4 | 快速看看 600362 | quick-scan.md · 不进 analyze |
| 5 | 深度研究 + 误跑 `run.py --depth deep` | 仍 `false`；正确须 U0→full→U2-FULL |

## UZI_ROOT 解析

```bash
# 推荐：setup-tracked-uzi.sh 安装后
export UZI_ROOT="${SKILLSHARE_SKILLS:-$HOME/.config/skillshare/skills}/uzi/_UZI-Skill"

# 或独立 clone
export UZI_ROOT="$HOME/UZI-Skill"
```

验证：

```bash
test -f "$UZI_ROOT/run.py" && echo "OK: $UZI_ROOT"
```

## 深度选择

| 级别 | `--depth` | 典型场景 | 说明 |
|------|-----------|----------|------|
| lite | `lite` | 速扫、初步风险 | 少维度 + Top 评委；见 quick-scan |
| medium | `medium` | 常规「能不能买」 | 默认；完整 HTML 报告 |
| deep | `deep` | 估值/IC/首次覆盖 | 机构建模 + 全评委；**U0 默认 mode=full**（见 [analyze-stock § U0](commands/analyze-stock.md#u0--门控必须先输出再进-u2)） |

环境变量：`export UZI_DEPTH=medium`（`--depth` 优先）。

## 专项路由

| 意图 | 做法 | 备注 |
|------|------|------|
| **DCF / 估值** | `run.py <ticker> --depth deep` + 读 Task 1.5 建模 JSON | 或 Read [commands/dcf.md](commands/dcf.md) |
| **杀猪盘** | `trap-detector` skill 流程或 lite 必跑 dim 18 | [commands/scan-trap.md](commands/scan-trap.md) |
| **龙虎榜** | Read `{UZI_ROOT}/skills/lhb-analyzer/SKILL.md` | 独立 skill，非 run.py 主路径 |
| **评委团 only** | Read `{UZI_ROOT}/skills/investor-panel/SKILL.md` | panel-only 场景 |
| **对比两只** | `run.py --versus 茅台 五粮液 --depth lite` | 见 UZI README |

## 与 stock-trade-journal 的分工

| 用户说 | 路由 |
|--------|------|
| 分析/估值/杀猪盘/龙虎榜 | **uzi-analysis-stack** |
| 今日实操反思/铁律/课程对齐 | **stock-trade-journal** |
| 先分析再写反思 | U2–U3 本 stack →  handoff 给 journal |

Handoff 块（交给 journal 时附带）：

```markdown
## UZI 分析 handoff
- ticker:
- 深度: lite|medium|deep
- 综合分 / 定调: （来自 synthesis.json 或 reports/*/one-liner.txt）
- 报告路径: `{UZI_ROOT}/skills/deep-analysis/scripts/reports/{TICKER}_{YYYYMMDD}/`
- one-liner: （Read one-liner.txt 原文）
- 用户关心的操作: （买/卖/观望）
```

`stock-trade-journal` 写复盘时**自行**读 UZI 证据（笔记库 `uzi-snapshots/` 优先，其次 `reports/`），读毕**归档到笔记库**（见 `stock-trade-journal/uzi-archive.md`）。handoff 可加速但不可替代 Read。

## nmem 写入格式

**何时写**：用户明确要求记住；或 deep 分析且有明确投资结论；lite 速扫默认不写。

**Skill**：`distill-memory` 或 `nmem m add`

**标题示例：**

```text
UZI 分析 | 贵州茅台 | 72分 | 观望优先
```

**正文结构：**

```markdown
- ticker: 600519.SH
- 深度: medium
- 评分: 72/100（fund=68, consensus=75）
- 定调: 观望优先
- Top3 看多: …
- Top3 看空: …
- DCF 内在价值: …（若有）
- 杀猪盘: 低风险 / …
- 报告: <path to html>
- 日期: YYYY-MM-DD
```

**读取历史分析**：`search-memory` 查 `UZI 分析` 或 ticker 名称。

## 依赖与故障

| 问题 | 处理 |
|------|------|
| `No module named akshare` | `pip install -r $UZI_ROOT/requirements.txt` |
| Playwright 报错 | `playwright install chromium` 或 `UZI_DEPTH=lite` |
| ticker 无法解析 | 改用 `600519.SH` 格式 |
| UZI_ROOT 不存在 | 运行 `./script/setup-tracked-uzi.sh` |
| skillshare audit 拦安装 | 上游 install 用 `--skip-audit`（见 setup 脚本） |
| `agent_reviewed: false` | [analyze-stock.md § U2-FULL-REMEDIAL](commands/analyze-stock.md#u2-full--stage1--agent-json--stage2仅-modefull) |
| `_agent_analysis_errors.json` | Read [agent-analysis-schema.md](agent-analysis-schema.md) 修正后重跑 stage2 |
| Agent Shell 超时 | stage1 用户本地跑；Agent 只做 JSON + stage2 |

## 升级

```bash
cd ~/.config/skillshare
skillshare update --group uzi    # 若 metadata 已注册 group
# 或
cd skills/uzi/_UZI-Skill && git pull
pip install -r requirements.txt -U
skillshare sync --all --force
```

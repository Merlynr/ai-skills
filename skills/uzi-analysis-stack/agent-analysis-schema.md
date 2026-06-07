# agent_analysis.json — Merlynr 精简契约

Agent 增强层写入路径：

```text
${UZI_ROOT}/skills/deep-analysis/scripts/.cache/<TICKER>/agent_analysis.json
```

校验逻辑见上游：`skills/deep-analysis/scripts/lib/agent_analysis_validator.py`  
错误清单：` .cache/<TICKER>/_agent_analysis_errors.json`（stage2 失败时）

## 必填字段

| 字段 | 要求 | 严重度 |
|------|------|--------|
| `agent_reviewed` | `true` | warning |
| `dim_commentary` | dict，≥5 个维度 key，每条 **≥20 字**，含具体数字 | warning |
| `panel_insights` | string，**≥30 字**，投票分布 + 多空分歧 | warning |
| `great_divide_override` | 见下表 | error 若缺 key |
| `narrative_override` | 见下表 | warning |

### great_divide_override

| 子字段 | 要求 |
|--------|------|
| `punchline` | ≥10 字，含冲突/数字 |
| `bull_say_rounds` | array，≥3 条 |
| `bear_say_rounds` | array，≥3 条 |

### narrative_override

| 子字段 | 要求 |
|--------|------|
| `core_conclusion` | ≥20 字 |
| `risks` | array，≥3 条 |
| `buy_zones` | 必须含 `value` / `growth` / `technical` / `youzi`，各含 `price`(number) + `rationale`(≥5 字) |

## medium/deep 推荐

| 字段 | 说明 |
|------|------|
| `qualitative_deep_dive` | 6 维：`3_macro` `7_industry` `8_materials` `9_futures` `13_policy` `15_events`；每维 `evidence`≥2、`conclusion` 1–2 句；6 维合计 `associations`≥3 |
| `data_gap_acknowledged` | dict，`{"dim_key": "已尝试但失败原因"}` |

详见 `$UZI_ROOT/skills/deep-analysis/references/task2.5-qualitative-deep-dive.md`

## 最小可过 schema 模板（复制后替换）

```json
{
  "agent_reviewed": true,
  "dim_commentary": {
    "0_basic": "…≥20字，含市值/主业/行业…",
    "1_financials": "…ROE/负债/现金流具体数…",
    "2_kline": "…趋势/Stage/量能…",
    "10_valuation": "…PE/PB/分位…",
    "18_trap": "…杀猪盘等级与依据…"
  },
  "panel_insights": "51评委中看多X人、看空Y人；价值派…技术派…共识Z%。",
  "great_divide_override": {
    "punchline": "…含数字的冲突金句…",
    "bull_say_rounds": ["…", "…", "…"],
    "bear_say_rounds": ["…", "…", "…"]
  },
  "narrative_override": {
    "core_conclusion": "…名称·分数·定调·一句话…",
    "risks": ["…", "…", "…"],
    "buy_zones": {
      "value": {"price": 0.0, "rationale": "…"},
      "growth": {"price": 0.0, "rationale": "…"},
      "technical": {"price": 0.0, "rationale": "…"},
      "youzi": {"price": 0.0, "rationale": "…"}
    }
  }
}
```

`price` 必须来自 `synthesis.json` / `raw_data.json` / `panel.json` 中的证据，禁止臆造。

## Agent 写文件 checklist

- [ ] 已 Read `panel.json`
- [ ] 已 Read `raw_data.json` 或其中关键 dim
- [ ] `dim_commentary` 是 **object** 不是 array
- [ ] `agent_reviewed: true`
- [ ] 已运行 stage2 且 stdout 含「Agent 分析已加载」
- [ ] 交付摘要注明 `执行模式: full`

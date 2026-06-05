# /uzi:dcf — DCF / 估值专项（deep）

**触发**: DCF、内在价值、估值多少、合理价位

**参数**: `$ARGUMENTS` = 股票名称或代码

## 步骤

### 1. 跑 deep 分析（含 Task 1.5 机构建模）

```bash
export UZI_ROOT="${UZI_ROOT:-${SKILLSHARE_SKILLS:-$HOME/.config/skillshare/skills}/uzi/_UZI-Skill}"
cd "$UZI_ROOT"
python3 run.py <TICKER> --no-browser --depth deep
```

### 2. 读建模产物

在 `${UZI_ROOT}/skills/deep-analysis/scripts/.cache/<ticker>/` 下查找：

- DCF / 估值相关 JSON（Task 1.5 输出，文件名以 UZI 版本为准）
- `synthesis.json` 中的估值摘要字段

Read `$UZI_ROOT/skills/deep-analysis/references/task1.5-institutional-modeling.md` 若字段含义不清。

### 3. 交付重点

```markdown
## DCF / 估值 · {名称}

- 内在价值: …
- 当前价: …
- 安全边际 / 高估低估: …
- 与 Comps/LBO 分歧（若有）: …
- 假设要点: …
```

### 4. 仅要 DCF 不要全报告时

仍建议 `--depth deep`；lite 不含完整 DCF 建模。

## 上游

UZI 插件：`stock-deep-analyzer:dcf`

Read：`$UZI_ROOT/commands/dcf.md`

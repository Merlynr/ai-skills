# /uzi:quick-scan — 快速扫描（lite）

**触发**: 快速看看、先扫一眼、30 秒、速判

**参数**: `$ARGUMENTS` = 股票名称或代码

## 步骤

### 1. 解析 UZI_ROOT

见 [../analysis-routing.md](../analysis-routing.md)

### 2. 执行 lite

```bash
export UZI_ROOT="${UZI_ROOT:-${SKILLSHARE_SKILLS:-$HOME/.config/skillshare/skills}/uzi/_UZI-Skill}"
cd "$UZI_ROOT"
python3 run.py <TICKER> --no-browser --depth lite
```

### 3. 交付

使用 [../report-template.md](../report-template.md) 的 **lite 精简版**。

维度预期（与 UZI quick-scan 一致）：财报、K 线、估值、杀猪盘（dim 18）；Top 10 评委。

### 4. 升级提示

若用户追问细节 → 建议 medium/full：`/uzi:analyze`（见 [analyze-stock.md](analyze-stock.md) U0）

## 上游

UZI 插件命令等价：`stock-deep-analyzer:quick-scan`

Read 参考：`$UZI_ROOT/commands/quick-scan.md`

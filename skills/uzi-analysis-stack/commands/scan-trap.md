# /uzi:scan-trap — 杀猪盘 / 陷阱排查

**触发**: 杀猪盘、是不是庄、陷阱、扫雷、安全吗

**参数**: `$ARGUMENTS` = 股票名称或代码

## 路由选择

| 场景 | 路径 |
|------|------|
| 只要杀猪盘结论 | `run.py <TICKER> --depth lite`（含 dim 18） |
| 完整八信号排查 | Read 并遵循 `$UZI_ROOT/skills/trap-detector/SKILL.md` |

## 快速路径（lite）

```bash
export UZI_ROOT="${UZI_ROOT:-${SKILLSHARE_SKILLS:-$HOME/.config/skillshare/skills}/uzi/_UZI-Skill}"
cd "$UZI_ROOT"
python3 run.py <TICKER> --no-browser --depth lite
```

从 synthesis / 报告提取 **杀猪盘等级** 与 1–2 条关键信号。

## 完整 trap-detector

```bash
# Agent: Read $UZI_ROOT/skills/trap-detector/SKILL.md
# 按其中步骤执行（含 references/eight-signals.md）
```

## 交付

```markdown
## 杀猪盘排查 · {名称} ({代码})

**等级**: {低/中/高/…}
**关键信号**: …
**建议**: …
```

## 上游

UZI 插件：`stock-deep-analyzer:scan-trap`

Read：`$UZI_ROOT/commands/scan-trap.md`

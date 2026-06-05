# 分析路由

UZI Analysis Stack 的工具与意图路由。**平台表为 SSOT**（`SKILL.md` 不重复展开）。

## 按平台默认路径

| 平台 | 记忆 | UZI 执行 | 读产物 |
|------|------|----------|--------|
| **Codex** | nmem / `search-memory` | Shell：`python3 ${UZI_ROOT}/run.py …` | Read JSON/HTML under `scripts/` |
| **Cursor** | `read-working-memory` | Shell（同左） | Read |
| **OpenCode** | `read-working-memory` | Shell 或 explore 辅助查 ticker | Read |

```plaintext
所有平台 → 先读本 stack SKILL.md → 解析 UZI_ROOT → 再跑 run.py
禁止 → 不检查路径直接凭记忆写分析报告
```

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
| deep | `deep` | 估值/IC/首次覆盖 | 机构建模 + 全评委 |

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
- 综合分 / 定调: （来自 synthesis.json）
- 报告路径:
- 用户关心的操作: （买/卖/观望）
```

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

## 升级

```bash
cd ~/.config/skillshare
skillshare update --group uzi    # 若 metadata 已注册 group
# 或
cd skills/uzi/_UZI-Skill && git pull
pip install -r requirements.txt -U
skillshare sync --all --force
```

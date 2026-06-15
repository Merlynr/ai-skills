# UZI-Skill 升级记录 v3.7.1 → v3.9.0

## 升级日期
2026-06-15

## 版本变化
- **升级前**: v3.7.1 (commit 8a87399)
- **升级后**: v3.9.0 (commit 50b87c2)
- **落后 commit 数**: 15 个

## 主要新增功能

### v3.9.0 (2026-06-11)
- **新评委「股海贼王」**: 首位从真实交割单蒸馏的评委 (65→66)
  - id: ghzw
  - group: F (游资)
  - tier: flagship
  - source: 淘股吧十年实盘帖 · 8951 笔交割单蒸馏

### v3.8.0 (2026-06-08)
- **5 个 Tier-1 命令**:
  - `ai-readiness.md` - AI 就绪度评估
  - `earnings-preview.md` - 财报前预览
  - `model-update.md` - 增量更新模型
  - `rebalance.md` - 逐持仓再平衡
  - `returns.md` - 组合收益归因

- **Serenity 严谨化**:
  - 8 罚分因子
  - 3 级证据阶梯 (强×1.0 > 中×0.85 > 弱×0.70)
  - 供应链 8 层分层

- **技术指标扩展**:
  - DuPont 杜邦分解
  - KDJ/OBV/Williams%R

### v3.8.1 (2026-06-10)
- **H/I 两组修复**: 配套层 6 处补齐
- **新增头像**: 15 个 SVG 头像资源

## 本地修改

### uzi-analysis-stack 更新
1. **agent-analysis-schema.md**: 评委数量 51→66
2. **analysis-routing.md**: 添加 5 个新 Tier-1 命令映射

### 数据源兼容性修复
1. **腾讯财经 URL**: HTTPS → HTTP (解决 SSL 兼容性)
2. **雪球 URL**: HTTPS → HTTP (解决 SSL 兼容性)
3. **Playwright 超时**: 15s → 30s (提高稳定性)
4. **行业映射**: 添加 300390 (天华新能)

## 已知问题

| 问题 | 原因 | 状态 |
|------|------|------|
| SSL 连接失败 | OpenSSL 版本兼容性 | 已通过 HTTP 绕过 |
| 巨潮 503 | 服务器端问题 | 外部因素，无法修复 |
| 游资全部 skip | 市值超出射程 | 设计如此 |

## 验证结果

- ✅ 版本确认: v3.9.0
- ✅ 评委数量: 66 人 (9 组)
- ✅ H/I 两组: 正常配置
- ✅ Tier-1 命令: 5 个都已就绪
- ✅ Pipeline metadata: 已修复
- ✅ 行业信息获取: 正常工作

## 使用建议

```bash
# 游资派分析小盘股
python run.py 002995 --school F --no-browser

# 价值派分析大盘股
python run.py 300390 --school A --no-browser

# 全量分析
python run.py 300390 --no-browser
```

## 相关链接
- UZI-Skill 仓库: https://github.com/wbh604/UZI-Skill
- 升级文档: https://github.com/wbh604/UZI-Skill/blob/main/RELEASE-NOTES.md

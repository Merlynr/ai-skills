# GSD Base 层改造记录

> 日期：2026-06-05  
> 仓库：`~/.config/skillshare`（Merlynr 个人 skills SSOT）  
> 关联 commit：`af7963a`（base 层迁移 + tracked）及后续 Merlynr 文档改进 commit

## 1. 改造动机

### 问题

- **~89 个 GSD skill** 全部暴露在 Cursor/agents 门面 target，上下文体积大（on-demand ~71K），且用户难以找到入口。
- GSD 升级路径分散：L1 runtime、L2 skill 适配器、L3 Merlynr 覆盖层没有统一脚本。
- `skillshare update --group base` 无法对上游 GSD 仓库做 **tracked pull**。

### 目标

1. **隐藏 base 层**：77 个 `gsd-*` 迁入 `skills/base/`，用户层只保留 facade（`merlynr-dev-stack`、`gsd-ns-*`、少量快捷 skill）。
2. **tracked 上游**：`gsd-build/get-shit-done` 注册为 skillshare tracked repo，支持 `skillshare update --group base`。
3. **多 target 分工**：门面型（cursor、agents、**opencode**）白名单 sync；**codex** 全量 sync。
4. **升级可重复**：一条脚本走完 L1→L2→L3→sync→verify。
5. **Merlynr 工作流细化**：grill-lite / tool-routing 边界与 handoff 模板。

---

## 2. 三层架构（L1 / L2 / L3）

| 层 | 路径 | 内容 | 更新方式 |
|----|------|------|----------|
| **L1 Runtime** | `~/.codex/get-shit-done/`（及各平台 GSD 安装目录） | workflows、bin、templates | `npx @opengsd/gsd-core@latest` / `gsd-update` |
| **L2 Skills** | `skills/base/gsd-*/SKILL.md` + tracked `skills/base/_get-shit-done/` | 薄适配器 skill + 上游 monorepo 引用 | `skillshare update --group base` + B2 rsync（见 §4） |
| **L3 Merlynr** | `skills/merlynr-dev-stack/`、`gsd-ns-*`、`gsd-team` 等 | 个人工作流、路由、覆盖 | 只改 skillshare SSOT，** never 改 upstream** |

**原则**：GSD 更新覆盖 L1/L2 安装文件；所有 Merlynr 定制写在 L3，GSD 升级后仍有效。

---

## 3. 目录与 sync 策略

### 3.1 迁移后布局

```plaintext
skills/
├── .gitignore              # skillshare 管理：忽略 base/_get-shit-done/
├── .metadata.json          # tracked 元数据（base/_get-shit-done）
├── base/
│   ├── _get-shit-done/     # tracked clone（不入 git）
│   └── gsd-*/              # 77 个 vendored SKILL.md（入 git）
├── merlynr-dev-stack/      # 用户工作流 SSOT
│   ├── SKILL.md
│   ├── grill-lite.md
│   └── tool-routing.md
├── gsd-ns-*/               # 6 个命名空间路由
├── gsd-do, gsd-fast, …     # 用户层快捷 skill（~12）
└── …                       # 非 GSD skill（nmem、学习等）
```

### 3.2 Target profile

`config.linux.yaml` / `config.windows.yaml`：

- `target_naming: standard` — `skills/base/gsd-plan-phase` sync 为 `gsd-plan-phase`（非 `base__gsd-plan-phase`）。
- **门面 profile**（`cursor`、`agents`、**`opencode`**）：`include` 白名单 ~18 skill。
- **执行 profile**（**`codex`**）：无 filter，全量 ~95 skill。

### 3.3 门面 target 读 base skill

cursor/agents 未 sync 某 base skill 时，Agent **Read SSOT**：

```plaintext
{SKILLSHARE_SKILLS}/base/{skill-name}/SKILL.md
```

详见 `merlynr-dev-stack/SKILL.md`「Base 层 skill 加载」。

### 3.4 同步后清理（cursor copy 模式）

cursor 为 **copy** 模式，历史本地 `gsd-*` 可能残留：

```bash
./script/prune-facade-locals.sh
```

---

## 4. Tracked base 子模块

### 4.1 注册命令

```bash
./script/setup-tracked-base.sh
# 等价于：
skillshare install gsd-build/get-shit-done --into base --track --force --kind skill --skip-audit
```

产物：

- 本地 clone：`skills/base/_get-shit-done/`（含 `.git`）
- `skills/.metadata.json` 条目：`group: base`, `tracked: true`
- `skills/.gitignore` 自动追加：`base/_get-shit-done/`

### 4.2 日常更新

```bash
skillshare update --group base          # git pull tracked repo
skillshare update --group base --dry-run
```

### 4.3 重要限制

上游 `get-shit-done` **不包含** `gsd-*/SKILL.md` agent skills（仅有 `commands/gsd/*.md` 等）。

因此：

| 路径 | 角色 |
|------|------|
| `base/_get-shit-done/` | L1 上游参考 + tracked pull |
| `base/gsd-*/SKILL.md` | L2 vendored 适配器，**仍在 git 中**，靠 upgrade 脚本 B2 从 `~/.codex/skills/gsd-*` rsync 刷新 |

---

## 5. 升级脚本

### 5.1 全栈升级

```bash
./script/upgrade-gsd-stack.sh           # L1 → reapply → L2 → L3 → sync → verify
./script/upgrade-gsd-stack.sh --dry-run
./script/upgrade-gsd-stack.sh --skip-l1 # 仅 L2/L3/sync
```

**L2 顺序**：

1. `skillshare update --group base`（tracked pull）
2. 从 `$CODEX_HOME/skills/gsd-*` rsync 到 `skills/base/`（跳过用户层 skill：gsd-ns-*、gsd-team、gsd-do 等）

### 5.2 一次性迁移（新机器或历史仓库）

```bash
./script/migrate-gsd-to-base.sh   # 幂等：顶层 gsd-* → skills/base/
```

### 5.3 公共路径解析

`script/_common.py`：`resolve_skills_dir()`、`resolve_gsd_base_dir()`、`resolve_skill_md()` — 供 `add-gsd-metadata.py`、`refine-gsd-tags.py`、`gsd-team-engine.py` 使用。

---

## 6. Merlynr 工作流改进（2026-06-05 续）

### 6.1 Phase 命名

Merlynr 流程使用 **M0–M4.5**（与 `gsd-team` 的 Phase 0 Cymbal Brief / Phase 1 探库区分）：

```plaintext
M0  grill-lite（需求澄清，可选）
M1  tool-routing（证据收集）
M2  GSD 规划
M3  执行
M4  验证与 nmem
M4.5 模块 AGENTS.md 写回
```

### 6.2 grill-lite

| 级别 | 是否启用 | 轮次 |
|------|----------|------|
| S | 否 | — |
| M | 验收略模糊、≤5 文件 | ≤3 轮 |
| L | 需求/验收未清 | ≤12 轮 |

出口必须输出 **Grill 共识** handoff 块，再进 `gsd-discuss-phase` / 执行，避免重复拷问。模板见 `skills/merlynr-dev-stack/grill-lite.md`。

### 6.3 tool-routing

- **平台 SSOT 唯一位置**：`tool-routing.md` § 按平台默认路径。
- **Cursor**：SemanticSearch → Grep → Read（不默认 Cymbal）。
- **Codex**：Cymbal → Grep → Read。
- **OpenCode**：explore agent → SemanticSearch → Grep。

`merlynr-dev-stack/SKILL.md` 不再重复平台表。

### 6.4 gsd-ns-workflow

进入 GSD phase 路由前：非 S 级且需求不清 → 先读 `merlynr-dev-stack` / grill-lite。

---

## 7. 验证清单

改造完成后建议执行：

```bash
skillshare update --group base --dry-run   # tracked 可 pull
skillshare sync --all --force
./script/prune-facade-locals.sh            # cursor 门面清理（OpenCode: 同脚本传 ~/.config/opencode/skills）
node script/apply-opencode-gsd-surface.js  # OpenCode /gsd-* 斜杠命令 → help+update
skillshare status                          # 门面 target ~18 on-demand；codex ~95
```

抽查：

- [ ] `skills/base/gsd-plan-phase/SKILL.md` 存在且可被 Read
- [ ] `skills/.metadata.json` 含 `base/_get-shit-done`
- [ ] cursor 下无多余顶层 `gsd-*`（除白名单）
- [ ] `upgrade-gsd-stack.sh --dry-run` 无报错

---

## 8. 后续可选方向

- Merlynr fork：仅含 `gsd-*/SKILL.md` 的 tracked L2 仓库（解决 upstream 结构不匹配）。
- `skillshare upgrade` 0.20.2 → 0.20.8（CLI 自身升级，与本次改造独立）。

---

## 9. 相关文件索引

| 文件 | 用途 |
|------|------|
| `docs/GSD-BASE-LAYER-REFACTOR.md` | 本文档 |
| `script/upgrade-gsd-stack.sh` | L1→L2→L3 全栈升级 |
| `script/setup-tracked-base.sh` | 注册 tracked base |
| `script/migrate-gsd-to-base.sh` | 历史迁移 |
| `script/prune-facade-locals.sh` | cursor Stale gsd 清理 |
| `script/_common.py` | SSOT 路径解析 |
| `skills/merlynr-dev-stack/` | Merlynr 工作流 SSOT |
| `config.linux.yaml` / `config.windows.yaml` | facade include 白名单 |

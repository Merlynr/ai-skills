# Skillshare - AI Skills 统一管理仓库

> 跨 AI CLI 工具同步 skills 和 agents 的中央仓库

## 快速开始

```bash
skillshare status              # 查看状态
skillshare sync --all          # 同步所有 skills
skillshare check --all         # 检查更新
```

## 前置要求

| 依赖 | 用途 | Linux/macOS 安装 | Windows 安装 |
|------|------|------------------|--------------|
| **Git** | 克隆仓库 | `apt install git` / `brew install git` | [git-scm.com](https://git-scm.com) |
| **Node.js** | 安装 skillshare CLI | [nodejs.org](https://nodejs.org) | [nodejs.org](https://nodejs.org) |
| **Python** | 运行脚本（可选） | `apt install python3` / `brew install python3` | [python.org](https://python.org) |

## 安装部署

### Linux / macOS

#### 方式一：一键部署（推荐）

拉取 SSOT、激活配置、`skillshare sync`，并自动执行 **Merlynr bootstrap**（GSD tracked base、UZI 引擎、OpenCode surface）：

```bash
curl -fsSL https://raw.githubusercontent.com/Merlynr/ai-skills/master/deploy.sh | bash
```

可选参数（传给内嵌 bootstrap）：

```bash
# 仅 SSOT + sync，不装 GSD/UZI 上游
bash deploy.sh --no-bootstrap

# 含 GSD L1 runtime（npx，较慢）
bash deploy.sh --with-l1

# 不要 UZI Python 引擎
bash deploy.sh --no-uzi
```

已 clone 仓库时：

```bash
cd ~/.config/skillshare
./deploy.sh
# 或只跑 bootstrap
./script/bootstrap-merlynr.sh
```

#### 方式二：手动部署

```bash
# 1. 克隆仓库
git clone https://github.com/Merlynr/ai-skills.git ~/.config/skillshare

# 2. 进入目录
cd ~/.config/skillshare

# 3. 添加执行权限
chmod +x deploy.sh

# 4. 运行部署脚本
./deploy.sh
```

#### 方式三：仅激活配置（已有仓库）

```bash
cd ~/.config/skillshare
chmod +x setup-config.sh
./setup-config.sh
```

---

### Windows

#### 方式一：一键部署（推荐）

打开 **PowerShell**，运行（含 Merlynr bootstrap，需 **Git Bash**）：

```powershell
irm https://raw.githubusercontent.com/Merlynr/ai-skills/master/deploy.ps1 -OutFile deploy.ps1
.\deploy.ps1 -Username "你的用户名"

# 可选
.\deploy.ps1 -Username "你的用户名" -NoBootstrap   # 仅 sync，不装 GSD/UZI
.\deploy.ps1 -Username "你的用户名" -WithL1      # 含 GSD L1 npx
.\deploy.ps1 -Username "你的用户名" -NoUzi         # 跳过 UZI 引擎
```

#### 方式二：手动部署

```powershell
# 1. 克隆仓库
git clone https://github.com/Merlynr/ai-skills.git "$env:APPDATA\skillshare"

# 2. 进入目录
cd "$env:APPDATA\skillshare"

# 3. 运行部署脚本
.\deploy.ps1 -Username "你的用户名"
```

#### 方式三：仅激活配置（已有仓库）

```powershell
cd "$env:APPDATA\skillshare"
.\setup-config.ps1
# 若需要修改用户名，编辑 config.yaml 将 C:/Users/xxx/ 替换为你的用户名
```

---

### 部署后配置

#### 1. 安装 skillshare CLI

```bash
npm install -g skillshare
```

#### 2. Windows 用户名配置

**使用 `-Username` 参数（推荐）**：

部署时自动替换配置文件中的用户名：

```powershell
.\deploy.ps1 -Username "你的用户名"
```

**手动修改**：

如果已部署但未指定用户名，可编辑 `config.yaml`：

```yaml
sources:
  skills: C:/Users/你的用户名/AppData/Roaming/skillshare/skills
  agents: C:/Users/你的用户名/AppData/Roaming/skillshare/agents

targets:
  agents:
    skills:
      path: C:/Users/你的用户名/.agents/skills
  codex:
    skills:
      path: C:/Users/你的用户名/.codex/skills
  cursor:
    skills:
      path: C:/Users/你的用户名/.cursor/skills
  opencode:
    skills:
      path: C:/Users/你的用户名/.config/opencode/skills
```

#### 3. 同步 skills

```bash
skillshare sync --all
```

> **注意**：使用 `deploy.ps1` 部署时会自动执行同步，无需手动运行。

#### 4. 验证部署

```bash
skillshare status              # 查看同步状态
skillshare doctor              # 运行诊断
skillshare list                # 列出所有 skills
```

期望结果（门面 target）：

- **cursor / agents / opencode**：约 18 个 skill（skillshare 门面）
- **codex**：全量 ~95
- **OpenCode `/gsd-*` 斜杠命令**：另需 `node script/apply-opencode-gsd-surface.js`（见 § GSD base 层）

#### 5. Windows 补充说明

| 项目 | 说明 |
|------|------|
| SSOT 路径 | `%APPDATA%\skillshare`（不是 `~/.config/skillshare`） |
| 配置模板 | `config.windows.yaml` → `setup-config.ps1` 或 `deploy.ps1 -Username` |
| Cursor 探库 | 走 SemanticSearch / Grep，**不必**装 Cymbal |
| Bash 脚本 | `script/*.sh` 需 **Git Bash** 或 **WSL**；或在 PowerShell 用下方等价命令 |

Windows 上注册 tracked base（新机器首次，可选）：

```powershell
cd $env:APPDATA\skillshare
skillshare install gsd-build/get-shit-done --into base --track --force --kind skill --skip-audit
```

Windows 上 GSD 栈升级（无 bash 时分步）：

```powershell
skillshare update --group base
npx @opengsd/gsd-core@latest
python script/add-gsd-metadata.py
skillshare sync --all --force
node script/apply-opencode-gsd-surface.js
```

Linux 一键等价：`./script/upgrade-gsd-stack.sh`（详见下文 § GSD base 层）。

---

```
~/.config/skillshare/          # Linux
%AppData%\skillshare\          # Windows
├── skills/
│   ├── base/                  # GSD base 层（77 gsd-* + tracked _get-shit-done）
│   ├── merlynr-dev-stack/     # Merlynr 工作流（grill-lite、tool-routing）
│   ├── gsd-ns-*/              # GSD 命名空间路由（6 个）
│   └── …                      # 用户层 skill、学习系列、nmem 等
├── agents/
├── script/                    # gsd-team-engine.py、upgrade-gsd-stack.sh 等
├── config.linux.yaml          # Linux 配置模板
├── config.windows.yaml        # Windows 配置模板
├── config.yaml                # 本机激活配置（gitignore）
├── deploy.sh / deploy.ps1
├── UPGRADE-GUIDE.md
├── docs/GSD-BASE-LAYER-REFACTOR.md
└── README.md
```

### 跨平台配置

仓库内**不直接提交** `config.yaml`，各平台使用模板：

| 平台 | 模板 | 激活方式 |
|------|------|----------|
| Linux | `config.linux.yaml` | `./setup-config.sh` |
| Windows | `config.windows.yaml` | `.\setup-config.ps1` |

也可设置环境变量指向模板，无需复制：

```bash
# Linux
export SKILLSHARE_CONFIG=~/.config/skillshare/config.linux.yaml

# Windows PowerShell
$env:SKILLSHARE_CONFIG = "$env:APPDATA\skillshare\config.windows.yaml"
```

## GSD base 层与同步策略

2026-06 改造后，GSD 分为三层（Merlynr 定制写在 L3，GSD 升级不覆盖）：

| 层 | 位置 | 更新方式 |
|----|------|----------|
| **L1 Runtime** | `~/.codex/get-shit-done/` 等 | `npx @opengsd/gsd-core@latest` / `gsd-update` |
| **L2 Skills** | `skills/base/gsd-*/` + tracked `base/_get-shit-done/` | `skillshare update --group base` + codex rsync（见升级脚本） |
| **L3 Merlynr** | `merlynr-dev-stack`、`gsd-ns-*` 等 | 只改本仓库 SSOT |

**同步策略**（`config.linux.yaml` / `config.windows.yaml` 已配置）：

| Target | 模式 | 内容 |
|--------|------|------|
| **cursor、agents、opencode** | merge / copy + **include 白名单** | ~18 门面 skill |
| **codex** | merge，无 filter | 全量 ~95 skill |

门面 target 未 sync 某 base skill 时，Agent Read SSOT：

```plaintext
{SSOT}/skills/base/{skill-name}/SKILL.md
```

**常用维护命令：**

```bash
skillshare update --group base          # tracked 上游 git pull
./script/upgrade-gsd-stack.sh         # Linux：L1→L2→L3→sync→verify
./script/setup-tracked-base.sh          # 新机器注册 tracked base
./script/prune-facade-locals.sh         # cursor copy 模式清理 stale gsd-*
node script/apply-opencode-gsd-surface.js   # OpenCode L1：/gsd-* 斜杠命令收紧（仅 help+update）
```

**OpenCode 两层说明**（skillshare sync 只收紧一层）：

| 层 | 路径 | 收紧方式 |
|----|------|----------|
| Skills（Agent 可选 skill） | `~/.config/opencode/skills/` | skillshare `include` 白名单 |
| Slash 命令（`/gsd-*` 菜单） | `~/.config/opencode/command/` | GSD `.gsd-profile` + `apply-opencode-gsd-surface.js` |

默认 GSD 安装会把 OpenCode 的 `.gsd-profile` 设为 `full`（~67 个 `/gsd-*`），与 skillshare 无关。

完整改造背景见 [docs/GSD-BASE-LAYER-REFACTOR.md](./docs/GSD-BASE-LAYER-REFACTOR.md)。

## Merlynr 一键 bootstrap

`deploy.sh` / `deploy.ps1` 在 sync 之后默认调用：

```bash
./script/bootstrap-merlynr.sh
```

| 步骤 | 内容 |
|------|------|
| sync | `skillshare sync --all --force` |
| GSD base | `setup-tracked-base.sh`（若缺失） |
| UZI 引擎 | `setup-tracked-uzi.sh` + `pip install -r …/requirements.txt` |
| GSD 升级 | `upgrade-gsd-stack.sh --skip-l1`（加 `--with-l1` 含 L1） |
| OpenCode | `apply-opencode-gsd-surface.js` |
| 清理 | `prune-facade-locals.sh ~/.claude/skills` |

**新机器远程一条命令（需 master 已 push 最新改动）：**

```bash
curl -fsSL https://raw.githubusercontent.com/Merlynr/ai-skills/master/deploy.sh | bash
```

仅更新已有仓库：

```bash
cd ~/.config/skillshare && git pull && ./script/bootstrap-merlynr.sh
```

## 工具链概览

| 工具 | 版本 | 用途 |
|------|------|------|
| Cymbal | Go binary | 代码索引与符号发现 |
| RTK | 0.34.3 | CLI 代理，优化输出 |
| GSD | 1.42.3 | 项目管理工作流 |
| nmem | CLI 0.7.0 / Server 0.8.6 | 记忆管理 |
| Skillshare | 0.20.x | Skills 跨工具同步 |

> Cymbal / RTK 主要为 **Codex/Linux** 探库；**Cursor on Windows** 按 `merlynr-dev-stack/tool-routing.md` 用 IDE 搜索即可。

## 同步目标

路径以 Linux 为例；Windows 将 `~` 换为 `C:/Users/<用户名>/`（或由 `config.windows.yaml` / `deploy.ps1 -Username` 生成）。

| 目标 | 路径 | 模式 | 说明 |
|------|------|------|------|
| agents | `~/.agents/skills` | merge | 门面白名单 |
| codex | `~/.codex/skills` | merge | 全量 |
| cursor | `~/.cursor/skills` | copy | 门面白名单 |
| opencode | `~/.config/opencode/skills` | merge | 门面白名单 |

## 包含的 Skills

### 工作流入口

- **merlynr-dev-stack** — 通用开发 S/M/L + GSD 路由
- **uzi-analysis-stack** — 股票分析 U0–U4（门面；引擎在 `skills/uzi/_UZI-Skill/`）
- **stock-trade-journal** — 实操反思（Obsidian 天才交易员）

### GSD 系列

- **base 层**（`skills/base/`）：77 个 `gsd-*` workflow skill
- **用户层**：`gsd-ns-*`（6）、`gsd-do/fast/quick`、`gsd-team`、`gsd-update`、`gsd-reapply-patches`
- **工作流入口**：`merlynr-dev-stack`（S/M/L 路由 + grill-lite + tool-routing）

### Nowledge Mem 系列 - 8 个
- `check-integration` - 检查 Nowledge Mem 集成
- `distill-memory` - 捕获关键洞察
- `find-skills` - 搜索可用 skills
- `read-working-memory` - 读取工作记忆
- `save-handoff` - 保存上下文交接
- `save-thread` - 保存会话线程
- `search-memory` - 搜索知识库
- `status` - 检查连接状态

### 自制学习系列 - 2 个
- `generate-daily-plan` - Obsidian 今日计划生成器（全局）
- `unified-learning-session` - 统一学习会话管理（支持任意学科，知识点分类整理，nmem 集成）

### 其他
- `commit-message` - 生成中文 commit 消息（待纳入）

## 升级指南

详见 [UPGRADE-GUIDE.md](./UPGRADE-GUIDE.md)（Cymbal / RTK / GSD L1 / skillshare CLI）。

### 日常升级

```bash
skillshare upgrade             # 升级 skillshare CLI
skillshare update --group base # 仅 tracked GSD 上游
skillshare sync --all          # 同步到所有 target
```

### GSD 全栈（Linux）

```bash
./script/upgrade-gsd-stack.sh
```

Windows 分步命令见上文 **§ 部署后配置 → Windows 补充说明**。完整改造记录：[docs/GSD-BASE-LAYER-REFACTOR.md](./docs/GSD-BASE-LAYER-REFACTOR.md)

## 常用命令

```bash
# 状态检查
skillshare status              # 查看同步状态
skillshare doctor              # 运行诊断

# 更新
skillshare upgrade             # 升级 CLI
skillshare update --all        # 更新所有 skills/agents
skillshare sync --all          # 同步到所有目标

# 管理
skillshare list                # 列出 skills
skillshare list agents         # 列出 agents
skillshare search <query>      # 搜索 skills
skillshare install <repo>      # 安装新 skill

# 维护
skillshare backup              # 备份目标
skillshare restore <target>    # 恢复目标
skillshare log                 # 查看操作日志
```

## 相关链接

| 工具 | GitHub |
|------|--------|
| Cymbal | https://github.com/1broseidon/cymbal |
| RTK | https://github.com/rtk-ai/rtk |
| GSD | https://github.com/gsd-build/get-shit-done/ |
| nmem | https://github.com/nowledge-co/community |
| Skillshare | https://github.com/runkids/skillshare |

---

*最后更新：2026-06-05*

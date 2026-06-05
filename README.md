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

```bash
curl -fsSL https://raw.githubusercontent.com/Merlynr/ai-skills/master/deploy.sh | bash
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

打开 **PowerShell**，运行：

```powershell
# 下载脚本
irm https://raw.githubusercontent.com/Merlynr/ai-skills/master/deploy.ps1 -OutFile deploy.ps1

# 运行（自动检测用户名）
.\deploy.ps1

# 或手动指定用户名
.\deploy.ps1 -Username "你的用户名"
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

#### 2. 安装 nmem（可选，用于记忆管理）

```bash
pip install nowledge-mem
```

#### 3. Windows 用户名配置

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

#### 4. 同步 skills

```bash
skillshare sync --all
```

> **注意**：使用 `deploy.ps1` 部署时会自动执行同步，无需手动运行。

#### 5. 验证部署

```bash
skillshare status              # 查看同步状态
skillshare doctor              # 运行诊断
skillshare list                # 列出所有 skills
```

## 仓库结构

```
~/.config/skillshare/          # Linux
%AppData%\skillshare\          # Windows
├── skills/              # 78+ skills（含 GSD、学习系列等）
├── agents/              # 自定义 agents（待扩展）
├── script/              # 团队引擎脚本
│   ├── gsd-team-engine.py
│   ├── gsd-team-gen.py
│   └── skill-registry.json
├── config.linux.yaml    # Linux 配置模板
├── config.windows.yaml  # Windows 配置模板
├── config.yaml          # 本机激活配置（gitignore）
├── setup-config.sh      # Linux 配置激活
├── setup-config.ps1     # Windows 配置激活
├── deploy.sh            # Linux 一键部署
├── deploy.ps1           # Windows 一键部署
├── UPGRADE-GUIDE.md     # 升级指南
├── docs/
│   └── GSD-BASE-LAYER-REFACTOR.md  # GSD base 层改造记录（2026-06）
└── README.md            # 本文件
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

## 工具链概览

| 工具 | 版本 | 用途 |
|------|------|------|
| Cymbal | Go binary | 代码索引与符号发现 |
| RTK | 0.34.3 | CLI 代理，优化输出 |
| GSD | 1.42.3 | 项目管理工作流 |
| nmem | CLI 0.7.0 / Server 0.8.6 | 记忆管理 |
| Skillshare | 0.19.24 | Skills 跨工具同步 |

## 同步目标

| 目标 | 路径 | 模式 |
|------|------|------|
| agents | `~/.agents/skills` | merge |
| codex | `~/.codex/skills` | merge |
| cursor | `~/.cursor/skills` | copy |
| opencode | `~/.config/opencode/skills` | merge |

## 包含的 Skills

### GSD (Get Shit Done) 系列 - 70 个
项目管理、代码审查、调试、文档生成等全套工具链。

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

详见 [UPGRADE-GUIDE.md](./UPGRADE-GUIDE.md)

**GSD base 层改造**（三层架构、tracked base、门面 sync）：见 [docs/GSD-BASE-LAYER-REFACTOR.md](./docs/GSD-BASE-LAYER-REFACTOR.md)

### 一键升级

```bash
skillshare upgrade             # 升级 skillshare CLI
skillshare update --all        # 更新所有 skills
skillshare sync --all          # 同步到所有目标
```

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

*最后更新：2026-06-01*

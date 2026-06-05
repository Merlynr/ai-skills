# Linux 工具链升级与更新指南

> 本文档供 AI Agent（如 OpenCode）阅读，用于执行工具链的升级和同步操作。

## 目录

1. [工具链概述](#1-工具链概述)
2. [Cymbal - 代码索引器](#2-cymbal---代码索引器)
3. [RTK - CLI 代理工具](#3-rtk---cli-代理工具)
4. [GSD - 项目管理工具](#4-gsd---项目管理工具)
5. [Skillshare - Skills 同步](#5-skillshare---skills-同步)
6. [一键升级流程](#6-一键升级流程)
7. [常见问题排查](#7-常见问题排查)

---

## 1. 工具链概述

### 当前版本

| 工具 | 版本 | 安装路径 | 说明 |
|------|------|---------|------|
| Cymbal | Go binary | `/root/.gvm/pkgsets/go1.22.3/global/bin/cymbal` | 代码索引与符号发现 |
| RTK | 0.34.3 | `/root/.cargo/bin/rtk` | CLI 代理，优化输出 |
| GSD | 1.2.0 | `~/.config/opencode/get-shit-done/` | 项目管理工作流 |
| Skillshare | 0.20.2 | `/usr/local/bin/skillshare` | Skills 跨工具同步 |

### 目录结构

```
~/.config/skillshare/          # Skills 主仓库（源）
├── skills/                    # skills 源文件
│   ├── base/                  # GSD base 层（77 gsd-* + tracked _get-shit-done）
│   └── merlynr-dev-stack/     # Merlynr 工作流 SSOT
├── docs/GSD-BASE-LAYER-REFACTOR.md
├── agents/                    # 所有 agents 源文件
├── config.yaml                # 同步配置
├── UPGRADE-GUIDE.md           # 本文档
└── README.md                  # 仓库说明

~/.config/opencode/            # OpenCode 配置目录
├── skills/                    # ← 由 skillshare 同步
├── agents/                    # ← 由 skillshare 同步
├── get-shit-done/             # GSD 工具目录
└── opencode.json              # OpenCode 配置

~/.agents/skills/              # Nowledge Mem skills
~/.codex/skills/               # Codex CLI skills
~/.cursor/skills/              # Cursor skills
```

### Skill 同步目标

| 目标名称 | 路径 | 同步模式 |
|---------|------|---------|
| agents | `/root/.agents/skills` | merge |
| codex | `/root/.codex/skills` | merge |
| cursor | `/root/.cursor/skills` | copy |
| opencode | `/root/.config/opencode/skills` | merge |

---

## 2. Cymbal - 代码索引器

> 高性能代码索引、解析和符号发现 CLI，使用 tree-sitter 进行多语言 AST 解析。

**GitHub**: https://github.com/1broseidon/cymbal

### 检查版本

```bash
cymbal ls --json | head -5
```

### 升级方法

```bash
# 方式 1：通过 Go 安装（推荐）
go install github.com/1broseidon/cymbal@latest

# 方式 2：从源码编译
git clone https://github.com/1broseidon/cymbal.git /tmp/cymbal
cd /tmp/cymbal && go build -o cymbal && mv cymbal /usr/local/bin/
```

### 常用命令

```bash
cymbal index <dir>             # 索引目录
cymbal search <query> -t       # 全文搜索
cymbal investigate <symbol>    # 调查符号
cymbal refs <symbol>           # 查找引用
cymbal impact <symbol>         # 影响分析
cymbal trace <symbol>          # 调用链追踪
cymbal structure               # 仓库结构概览
```

### 验证升级

```bash
cymbal index ~/.config/skillshare
cymbal structure
```

---

## 3. RTK - CLI 代理工具

> 高性能 CLI 代理，用于过滤和摘要系统输出，优化 LLM 上下文使用。

**GitHub**: https://github.com/rtk-ai/rtk

### 检查版本

```bash
rtk --version
```

### 升级方法

```bash
# 方式 1：通过 cargo 安装（推荐）
cargo install rtk --force

# 方式 2：从 GitHub Release 下载
# 访问 https://github.com/rtk-ai/rtk/releases 下载对应平台二进制

# 方式 3：从源码编译
git clone https://github.com/rtk-ai/rtk.git /tmp/rtk
cd /tmp/rtk && cargo build --release && mv target/release/rtk /usr/local/bin/
```

### 常用命令

```bash
rtk ls                         # 优化的目录列表
rtk tree                       # 优化的目录树
rtk read <file>                # 智能文件读取
rtk git <subcommand>           # Git 命令优化输出
rtk gh <subcommand>            # GitHub CLI 优化输出
rtk diff                       # 压缩 diff 输出
rtk grep <pattern>             # 压缩 grep 输出
rtk json <file>                # JSON 查看
rtk deps                       # 依赖摘要
rtk err <command>              # 仅显示错误/警告
rtk test <command>             # 仅显示失败测试
rtk cymbal <args>              # 调用 cymbal（如果有）
```

### 验证升级

```bash
rtk --version
rtk ls ~/.config/skillshare/
```

---

## 4. GSD - 项目管理工具

> Get Shit Done - AI 驱动的项目管理工作流工具，支持阶段规划、执行和验证。

**GitHub**: https://github.com/gsd-build/get-shit-done/

### 检查版本

```bash
rtk read ~/.config/opencode/get-shit-done/VERSION
```

### 升级方法

```bash
# 方式 1：通过 npx 升级（推荐）
npx @opengsd/gsd-core@latest

# 方式 2：通过 oh-my-openagent 插件更新
# OpenCode 会自动检测并提示更新

# 方式 3：手动更新
cd ~/.config/opencode/get-shit-done
git pull origin main
```

### Skills 同步

GSD 的 skills 位于 `~/.config/skillshare/skills/gsd-*/`，通过 skillshare 同步到各目标：

```bash
# 同步 GSD skills
skillshare sync --all
```

### 常用 Skills

| Skill | 说明 |
|-------|------|
| gsd-help | 显示可用命令 |
| gsd-progress | 检查进度 |
| gsd-plan-phase | 创建阶段计划 |
| gsd-execute-phase | 执行阶段计划 |
| gsd-code-review | 代码审查 |
| gsd-debug | 调试工作流 |
| gsd-ship | 创建 PR |

### 验证升级

```bash
rtk read ~/.config/opencode/get-shit-done/VERSION
skillshare list | grep gsd | wc -l
```

---

## 5. Skillshare - Skills 同步

> 跨 AI CLI 工具同步 skills 和 agents 的中央仓库管理工具。

**GitHub**: https://github.com/runkids/skillshare

### 检查版本

```bash
skillshare version
```

### 升级方法

```bash
# 升级 CLI
skillshare upgrade

# 升级 skillshare skill
skillshare upgrade --skill
```

### 同步操作

```bash
# 检查状态
skillshare status

# 预览变更
skillshare sync --dry-run

# 同步所有
skillshare sync --all

# 仅同步 skills
skillshare sync

# 仅同步 agents
skillshare sync agents
```

### 管理 Skills

```bash
# 列出所有 skills
skillshare list

# 列出 agents
skillshare list agents

# 搜索 skills
skillshare search <query>

# 安装新 skill
skillshare install <repo-path>

# 创建新 skill
skillshare new <name>
```

### GSD base 层（Merlynr 2026-06 改造）

77 个 GSD skill 位于 `skills/base/`；门面 target（cursor、agents）仅 sync 白名单。完整改造说明见 **[docs/GSD-BASE-LAYER-REFACTOR.md](./docs/GSD-BASE-LAYER-REFACTOR.md)**。

```bash
# tracked 上游 pull（L1 monorepo 引用）
skillshare update --group base

# 全栈升级：L1 runtime → L2 vendored → L3 overlay → sync
./script/upgrade-gsd-stack.sh

# 新机器注册 tracked base
./script/setup-tracked-base.sh

# cursor copy 模式清理 stale gsd-*
./script/prune-facade-locals.sh
```

### 验证升级

```bash
skillshare version
skillshare status
skillshare doctor
```

### ⚠️ 覆盖风险警告

**`skillshare update` 会覆盖本地修改！**

| 命令 | 影响 |
|------|------|
| `skillshare update <skill>` | ⚠️ 覆盖该 skill 的本地修改 |
| `skillshare update --all` | ⚠️ 覆盖所有 skill 的本地修改 |
| `skillshare sync` | ✅ 安全，不会覆盖源文件 |
| `skillshare upgrade` | ✅ 安全，只升级 CLI |

**受影响的内容**：
- 手动添加的 `triggers`、`tags`、`tool_chain` 等元数据
- 自定义的 skill 内容修改

**不受影响的内容**：
- `script/` 目录下的脚本（如 gsd-team-engine.py）
- GSD 升级（安装到 `.claude/skills/`，不影响 skillshare）

#### 保护方案

**方案 1：更新后恢复（推荐）**

```bash
# 已提交到 Git，更新后拉取即可恢复
skillshare update --all
cd ~/.config/skillshare && git pull origin master
```

**方案 2：备份后更新**

```bash
# 备份
cd ~/.config/skillshare && git stash

# 更新
skillshare update --all

# 恢复
git stash pop
```

**方案 3：排除特定 skill**

```bash
# 添加到 .skillignore，阻止更新
echo "gsd-*" >> ~/.config/skillshare/.skillignore
```

---

## 7. 一键升级流程

### 完整升级脚本

```bash
#!/bin/bash
# 升级所有工具链

echo "=== 1. 升级 Cymbal ==="
go install github.com/1broseidon/cymbal@latest

echo "=== 2. 升级 RTK ==="
cargo install rtk --force

echo "=== 3. 升级 GSD ==="
npx @opengsd/gsd-core@latest

echo "=== 4. 升级 Skillshare ==="
skillshare upgrade

echo "=== 5. 同步 Skills ==="
skillshare sync --all

echo "=== 6. 验证 ==="
rtk --version
skillshare status
```

### 快速升级（仅 skillshare）

```bash
# 1. 检查当前状态
skillshare status

# 2. 升级 CLI
skillshare upgrade

# 3. 更新所有 skills/agents
skillshare update --all

# 4. 同步到所有目标
skillshare sync --all

# 5. 验证
skillshare status
skillshare doctor
```

---

## 7. 常见问题排查

### 问题：skills 未同步到目标

```bash
skillshare sync --all
skillshare status
```

### 问题：目标目录有冲突文件

```bash
skillshare diff <target-name>
skillshare sync --force
```

### 问题：GSD 版本不匹配

```bash
# 查看当前版本
rtk read ~/.config/opencode/get-shit-done/VERSION

# 重新安装
cd ~/.config/opencode/get-shit-done && git pull
```

### 问题：Cymbal 索引损坏

```bash
# 删除索引数据库
rm -rf ~/.config/skillshare/.git/cymbal.db

# 重新索引
cymbal index ~/.config/skillshare
```

### 问题：RTK 命令找不到

```bash
# 检查 PATH
echo $PATH | tr ':' '\n' | grep -E "cargo|rtk"

# 重新安装
cargo install rtk --force
```

### 问题：opencode 未加载新 skills

1. 确认 skills 已同步：`ls ~/.config/opencode/skills/`
2. 重启 OpenCode 会话
3. 检查 `opencode.json` 中的 plugin 配置

---

## 相关链接

| 工具 | GitHub | 文档 |
|------|--------|------|
| Cymbal | https://github.com/1broseidon/cymbal | README |
| RTK | https://github.com/rtk-ai/rtk | README |
| GSD | https://github.com/gsd-build/get-shit-done/ | README |
| Skillshare | https://github.com/runkids/skillshare | README |

---

*最后更新：2026-06-02*
*文档路径：~/.config/skillshare/UPGRADE-GUIDE.md*

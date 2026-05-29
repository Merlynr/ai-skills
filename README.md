# Skillshare - AI Skills 统一管理仓库

> 跨 AI CLI 工具同步 skills 和 agents 的中央仓库

## 快速开始

```bash
skillshare status              # 查看状态
skillshare sync --all          # 同步所有 skills
skillshare check --all         # 检查更新
```

## 仓库结构

```
~/.config/skillshare/
├── skills/              # 63+ skills（含 GSD、自制学习系列等）
├── agents/              # 自定义 agents（待扩展）
├── config.yaml          # 同步配置
├── UPGRADE-GUIDE.md     # 升级指南（含 cymbal/gsd/rtk/nmem）
└── README.md            # 本文件
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

### 自制学习系列 - 3 个
- `generate-daily-plan` - Obsidian 今日计划生成器（全局）
- `gaoruan-study-session` - 高软/系统架构师每日学习会话（错题、截图、nmem 简报）
- `cpp-rust-study-session` - C++/Rust 学习会话（答疑笔记、计划同步）

> 后两个 skill 源自在 Obsidian 笔记库 `f:\note\.cursor\skills\` 的项目级 skill；纳入中央仓库后可通过 `skillshare sync` 分发到各工具的全局 skills 目录。在 `f:\note` 工作区内仍保留项目级副本，Cursor 打开该工作区时会自动加载。

### 其他
- `commit-message` - 生成中文 commit 消息（待纳入）

## 升级指南

详见 [UPGRADE-GUIDE.md](./UPGRADE-GUIDE.md)

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

*最后更新：2026-05-29*

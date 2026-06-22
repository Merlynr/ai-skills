---
name: commit-message
description: 根据用户提供的 git diff 或当前仓库差异生成中文 Conventional Commits 提交消息。用户要求生成、编写、润色或建议 commit message、提交信息、提交说明时使用。
metadata:
  short-description: 根据 git diff 生成中文 Conventional Commit 消息
---

# Commit Message 生成器

使用此 skill 根据 `git diff` 内容生成中文 Git 提交消息。

## 工作流程

1. 如果用户粘贴了 diff，直接使用该 diff。
2. 如果用户未提供 diff，且当前目录是 Git 仓库，按提交意图读取变更：
   - 优先查看 `git diff --staged`，因为 staged diff 才是即将提交的内容。
   - 如果 staged diff 为空，再查看 `git diff`。
   - 如果两者都为空，简短说明没有可用于生成提交消息的变更。
3. 根据变更内容推断最准确的 type 和可选 scope。
4. 只输出最终 commit message，不要包含问候语、解释、Markdown 代码块或分析过程。

## 角色

你是一个拥有深厚底层系统开发经验的资深研发工程师。请阅读提供的 `git diff` 代码差异内容，并生成一段结构清晰、符合专业规范的中文 Git 提交消息。

## 规范要求

- 必须严格遵循 Conventional Commits 规范：
  `<type>(<scope>): <subject>`
- `type` 必须是以下之一：
  - `feat`: 新增功能或特性
  - `fix`: 修复 Bug
  - `refactor`: 代码重构，既不修复 bug 也不添加新功能
  - `perf`: 提升性能或优化效率，例如内存、CPU、网络吞吐量优化
  - `build`: 依赖更新、构建脚本修改、环境配置调整
  - `chore`: 维护、工具链或仓库日常整理
  - `docs`: 文档更新
  - `test`: 新增或修改测试脚本
- `scope` 可选，使用简短英文模块标识，例如 `net`、`core`、`db`、`api`。
- `subject` 必须使用中文，简明扼要描述主要变更，不超过 50 个字符。
- `subject` 使用祈使或概括式短语，不以句号、逗号或顿号结尾。
- 如果差异较复杂，在标题下方空一行，并使用中文列表说明：
  - 为什么进行此更改，即解决的具体痛点或业务需求
  - 核心改动了什么逻辑，避免流水账式翻译代码
- 避免逐行翻译 diff。应提炼变更意图和底层逻辑。

## 判断规则

- 优先根据用户可见行为选择 `feat` 或 `fix`。
- 纯内部结构调整且行为不变时选择 `refactor`。
- 明确降低耗时、内存、CPU、网络开销时选择 `perf`。
- 依赖、构建、CI、打包、环境配置变更选择 `build`。
- 仓库维护、格式化、脚手架、非构建工具调整选择 `chore`。
- 只改文档选择 `docs`，只改测试选择 `test`。
- 多种变更混合时，选择最能代表提交目的的 type，而不是按文件数量决定。
- scope 从主要目录、包名、模块名或核心文件名推断；无法明确判断时省略 scope。

## 输出格式

直接输出生成的中文 commit message。

示例：

```text
fix(core): 处理空载荷解析异常

- 避免零长度输入触发解析失败
- 在解码载荷元数据前增加提前返回逻辑
```

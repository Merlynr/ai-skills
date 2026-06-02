#!/usr/bin/env python3
"""
批量为 GSD skill 添加元数据配置 (triggers, tags, tool_chain)
"""

import re
from pathlib import Path

SKILLS_DIR = Path("/root/.config/skillshare/skills")

# GSD skill 元数据配置
GSD_METADATA = {
    # === 计划类 ===
    "gsd-discuss-phase": {
        "tags": ["planning", "discussion", "requirements", "discuss"],
        "triggers": ["讨论阶段", "需求讨论", "收集需求", "discuss phase", "需求分析"],
        "tool_chain": ["gsd-discuss-phase", "gsd-spec-phase", "gsd-plan-phase"],
    },
    "gsd-plan-phase": {
        "tags": ["planning", "planning-phase", "architecture", "roadmap"],
        "triggers": ["创建计划", "规划阶段", "写计划", "plan phase", "阶段规划"],
        "tool_chain": ["gsd-plan-phase", "gsd-execute-phase"],
    },
    "gsd-research-phase": {
        "tags": ["research", "investigation", "technical-research"],
        "triggers": ["研究阶段", "调研", "research phase", "技术调研"],
        "tool_chain": ["gsd-research-phase", "gsd-plan-phase"],
    },
    "gsd-list-phase-assumptions": {
        "tags": ["planning", "assumptions", "risk-analysis"],
        "triggers": ["列出假设", "假设分析", "list assumptions"],
        "tool_chain": ["gsd-list-phase-assumptions", "gsd-plan-phase"],
    },
    "gsd-analyze-dependencies": {
        "tags": ["planning", "dependencies", "dependency-graph"],
        "triggers": ["分析依赖", "依赖关系", "analyze dependencies"],
        "tool_chain": ["gsd-analyze-dependencies", "gsd-plan-phase"],
    },
    "gsd-spec-phase": {
        "tags": ["specification", "requirements", "ambiguity"],
        "triggers": ["规格说明", "模糊度分析", "spec phase", "需求规格"],
        "tool_chain": ["gsd-spec-phase", "gsd-plan-phase"],
    },
    "gsd-mvp-phase": {
        "tags": ["mvp", "vertical-slice", "user-story"],
        "triggers": ["MVP 切片", "最小可行", "mvp phase"],
        "tool_chain": ["gsd-mvp-phase", "gsd-plan-phase"],
    },
    
    # === 执行类 ===
    "gsd-execute-phase": {
        "tags": ["implementation", "execute-phase", "development", "coding"],
        "triggers": ["执行阶段", "实现功能", "写代码", "execute phase", "开始开发"],
        "tool_chain": ["gsd-execute-phase", "gsd-verify-work"],
    },
    "gsd-fast": {
        "tags": ["fast-path", "trivial-task", "inline-execution"],
        "triggers": ["快速执行", "简单任务", "fast task", "立即执行"],
        "tool_chain": ["gsd-fast"],
    },
    "gsd-quick": {
        "tags": ["quick-task", "small-scope", "guaranteed-execution"],
        "triggers": ["快速任务", "简单实现", "quick task"],
        "tool_chain": ["gsd-quick"],
    },
    "gsd-autonomous": {
        "tags": ["autonomous", "batch-execution", "multi-phase"],
        "triggers": ["自动执行", "自主执行", "autonomous", "批量执行"],
        "tool_chain": ["gsd-autonomous"],
    },
    
    # === 审查类 ===
    "gsd-code-review": {
        "tags": ["code-review", "quality-gate", "security-review"],
        "triggers": ["代码审查", "code review", "安全审计", "审查代码"],
        "tool_chain": ["gsd-code-review", "gsd-validate-phase"],
    },
    "gsd-validate-phase": {
        "tags": ["validation-gap", "test-coverage", "nyquist"],
        "triggers": ["验证阶段", "验证缺口", "validate phase", "补充验证"],
        "tool_chain": ["gsd-validate-phase", "gsd-verify-work"],
    },
    "gsd-verify-work": {
        "tags": ["uat", "acceptance-testing", "conversational-verify"],
        "triggers": ["验证工作", "UAT 验证", "verify work", "功能验证"],
        "tool_chain": ["gsd-verify-work"],
    },
    "gsd-review": {
        "tags": ["peer-review", "cross-ai-review", "external-review"],
        "triggers": ["同行审查", "外部审查", "peer review", "交叉审查"],
        "tool_chain": ["gsd-review"],
    },
    "gsd-audit-uat": {
        "tags": ["uat-audit", "verification-audit"],
        "triggers": ["UAT 审计", "验证审计", "audit uat"],
        "tool_chain": ["gsd-audit-uat"],
    },
    "gsd-audit-milestone": {
        "tags": ["milestone-audit", "completion-audit"],
        "triggers": ["里程碑审计", "milestone audit"],
        "tool_chain": ["gsd-audit-milestone"],
    },
    "gsd-eval-review": {
        "tags": ["eval-audit", "ai-evaluation", "eval-coverage"],
        "triggers": ["评估审查", "eval review"],
        "tool_chain": ["gsd-eval-review"],
    },
    
    # === 调试类 ===
    "gsd-debug": {
        "tags": ["debugging", "troubleshooting", "root-cause"],
        "triggers": ["调试", "排错", "修复 bug", "debug", "问题排查"],
        "tool_chain": ["gsd-debug", "gsd-forensics"],
    },
    "gsd-forensics": {
        "tags": ["post-mortem", "workflow-forensics", "failure-analysis"],
        "triggers": ["事后分析", "故障分析", "forensics", "根因分析"],
        "tool_chain": ["gsd-forensics"],
    },
    
    # === 文档类 ===
    "gsd-docs-update": {
        "tags": ["documentation", "docs-update", "doc-maintenance"],
        "triggers": ["更新文档", "写文档", "生成文档", "docs update", "文档维护"],
        "tool_chain": ["gsd-docs-update"],
    },
    "gsd-ingest-docs": {
        "tags": ["doc-ingest", "planning-bootstrap", "adr-import"],
        "triggers": ["导入文档", "初始化文档", "ingest docs"],
        "tool_chain": ["gsd-ingest-docs"],
    },
    "gsd-milestone-summary": {
        "tags": ["milestone-report", "onboarding-summary"],
        "triggers": ["里程碑总结", "项目总结", "milestone summary"],
        "tool_chain": ["gsd-milestone-summary"],
    },
    "gsd-session-report": {
        "tags": ["session-report", "work-summary"],
        "triggers": ["会话报告", "session report", "工作报告"],
        "tool_chain": ["gsd-session-report"],
    },
    
    # === 项目管理类 ===
    "gsd-new-project": {
        "tags": ["project-init", "bootstrap", "roadmap-create"],
        "triggers": ["新建项目", "初始化项目", "new project", "项目初始化"],
        "tool_chain": ["gsd-new-project"],
    },
    "gsd-new-milestone": {
        "tags": ["milestone-start", "version-cycle"],
        "triggers": ["新建里程碑", "开始里程碑", "new milestone"],
        "tool_chain": ["gsd-new-milestone"],
    },
    "gsd-complete-milestone": {
        "tags": ["milestone-archive", "milestone-complete"],
        "triggers": ["完成里程碑", "归档里程碑", "complete milestone"],
        "tool_chain": ["gsd-complete-milestone"],
    },
    "gsd-progress": {
        "tags": ["progress-check", "status-report", "situational"],
        "triggers": ["检查进度", "项目进度", "progress", "当前状态"],
        "tool_chain": ["gsd-progress"],
    },
    "gsd-stats": {
        "tags": ["project-metrics", "statistics", "timeline"],
        "triggers": ["项目统计", "统计数据", "stats", "项目指标"],
        "tool_chain": ["gsd-stats"],
    },
    "gsd-manager": {
        "tags": ["command-center", "interactive-manager"],
        "triggers": ["项目管理", "管理器", "manager", "命令中心"],
        "tool_chain": ["gsd-manager"],
    },
    
    # === 任务管理类 ===
    "gsd-add-todo": {
        "tags": ["todo", "task-capture", "idea-capture"],
        "triggers": ["添加待办", "记录想法", "add todo", "待办事项"],
        "tool_chain": ["gsd-add-todo"],
    },
    "gsd-check-todos": {
        "tags": ["todo-list", "task-triage"],
        "triggers": ["查看待办", "待办列表", "check todos"],
        "tool_chain": ["gsd-check-todos"],
    },
    "gsd-note": {
        "tags": ["quick-note", "idea-capture", "note-taking"],
        "triggers": ["记笔记", "记录", "note", "快速记录"],
        "tool_chain": ["gsd-note"],
    },
    "gsd-add-backlog": {
        "tags": ["backlog", "parking-lot", "idea-staging"],
        "triggers": ["添加到待办", "backlog", "暂存想法"],
        "tool_chain": ["gsd-add-backlog"],
    },
    "gsd-plant-seed": {
        "tags": ["seed-idea", "future-trigger", "forward-looking"],
        "triggers": ["播种想法", "未来计划", "plant seed"],
        "tool_chain": ["gsd-plant-seed"],
    },
    
    # === 阶段管理类 ===
    "gsd-add-phase": {
        "tags": ["phase-add", "roadmap-edit"],
        "triggers": ["添加阶段", "新增阶段", "add phase"],
        "tool_chain": ["gsd-add-phase"],
    },
    "gsd-insert-phase": {
        "tags": ["phase-insert", "urgent-phase", "decimal-phase"],
        "triggers": ["插入阶段", "紧急任务", "insert phase"],
        "tool_chain": ["gsd-insert-phase"],
    },
    "gsd-remove-phase": {
        "tags": ["phase-remove", "roadmap-edit"],
        "triggers": ["删除阶段", "移除阶段", "remove phase"],
        "tool_chain": ["gsd-remove-phase"],
    },
    "gsd-plan-milestone-gaps": {
        "tags": ["milestone-gaps", "gap-closure"],
        "triggers": ["规划缺口", "关闭缺口", "plan gaps"],
        "tool_chain": ["gsd-plan-milestone-gaps"],
    },
    
    # === 工作区管理类 ===
    "gsd-new-workspace": {
        "tags": ["workspace-create", "isolated-workspace"],
        "triggers": ["新建工作区", "创建工作区", "new workspace"],
        "tool_chain": ["gsd-new-workspace"],
    },
    "gsd-list-workspaces": {
        "tags": ["workspace-list", "workspace-status"],
        "triggers": ["列出工作区", "工作区列表", "list workspaces"],
        "tool_chain": ["gsd-list-workspaces"],
    },
    "gsd-remove-workspace": {
        "tags": ["workspace-remove", "worktree-cleanup"],
        "triggers": ["删除工作区", "移除工作区", "remove workspace"],
        "tool_chain": ["gsd-remove-workspace"],
    },
    
    # === UI 类 ===
    "gsd-ui-phase": {
        "tags": ["ui-design", "frontend-spec", "ui-spec"],
        "triggers": ["UI 设计", "界面设计", "ui phase", "前端规格"],
        "tool_chain": ["gsd-ui-phase"],
    },
    "gsd-ui-review": {
        "tags": ["ui-audit", "visual-review", "design-review"],
        "triggers": ["UI 审查", "界面审查", "ui review", "视觉审计"],
        "tool_chain": ["gsd-ui-review"],
    },
    
    # === 安全类 ===
    "gsd-secure-phase": {
        "tags": ["security-audit", "threat-model", "mitigation"],
        "triggers": ["安全验证", "安全审计", "secure phase", "威胁分析"],
        "tool_chain": ["gsd-secure-phase"],
    },
    
    # === 工具类 ===
    "gsd-do": {
        "tags": ["intent-routing", "auto-dispatch", "command-router"],
        "triggers": ["自动路由", "智能分发", "do command"],
        "tool_chain": ["gsd-do"],
    },
    "gsd-help": {
        "tags": ["help", "command-reference", "usage-guide"],
        "triggers": ["帮助", "使用指南", "help", "命令列表"],
        "tool_chain": ["gsd-help"],
    },
    "gsd-health": {
        "tags": ["planning-health", "integrity-check", "repair"],
        "triggers": ["健康检查", "诊断问题", "health check"],
        "tool_chain": ["gsd-health"],
    },
    "gsd-map-codebase": {
        "tags": ["codebase-map", "architecture-map", "代码库"],
        "triggers": ["映射代码库", "分析代码", "map codebase", "代码结构"],
        "tool_chain": ["gsd-map-codebase"],
    },
    "gsd-update": {
        "tags": ["gsd-update", "upgrade", "maintenance", "changelog"],
        "triggers": ["gsd升级", "升级 GSD", "升级GSD", "gsd update", "gsd-update", "更新GSD"],
        "tool_chain": ["gsd-update", "gsd-reapply-patches"],
    },
    "gsd-reapply-patches": {
        "tags": ["patch-restore", "upgrade-recovery", "local-customization"],
        "triggers": ["重新应用补丁", "恢复补丁", "恢复修改", "reapply patches"],
        "tool_chain": ["gsd-reapply-patches"],
    },
    "gsd-settings": {
        "tags": ["workflow-settings", "model-profile", "toggle-config"],
        "triggers": ["GSD 设置", "settings", "模型配置", "工作流开关"],
        "tool_chain": ["gsd-settings"],
    },
    "gsd-set-profile": {
        "tags": ["model-profile", "quality-tier", "budget-profile"],
        "triggers": ["设置配置", "切换模型", "set profile"],
        "tool_chain": ["gsd-set-profile"],
    },
    "gsd-ship": {
        "tags": ["release", "pull-request", "merge-ready"],
        "triggers": ["发布", "创建 PR", "ship", "准备合并"],
        "tool_chain": ["gsd-ship"],
    },
    "gsd-pr-branch": {
        "tags": ["pr-branch", "clean-history", "planning-filter"],
        "triggers": ["PR 分支", "拆分 PR", "创建分支", "pr branch"],
        "tool_chain": ["gsd-pr-branch"],
    },
    "gsd-thread": {
        "tags": ["persistent-thread", "cross-session", "context-thread"],
        "triggers": ["管理线程", "上下文线程", "thread"],
        "tool_chain": ["gsd-thread"],
    },
    "gsd-pause-work": {
        "tags": ["handoff", "pause-session", "context-save"],
        "triggers": ["暂停工作", "上下文交接", "pause work"],
        "tool_chain": ["gsd-pause-work"],
    },
    "gsd-resume-work": {
        "tags": ["handoff-restore", "resume-session", "context-restore"],
        "triggers": ["恢复工作", "继续工作", "resume work"],
        "tool_chain": ["gsd-resume-work"],
    },
    "gsd-workstreams": {
        "tags": ["parallel-workstream", "multi-track", "workstream-manage"],
        "triggers": ["管理工作流", "并行工作", "workstream"],
        "tool_chain": ["gsd-workstreams"],
    },
    "gsd-profile-user": {
        "tags": ["developer-profile", "behavior-analysis"],
        "triggers": ["用户画像", "行为分析", "profile user"],
        "tool_chain": ["gsd-profile-user"],
    },
    "gsd-cleanup": {
        "tags": ["archive-phases", "milestone-cleanup", "housekeeping"],
        "triggers": ["清理", "归档", "cleanup", "维护"],
        "tool_chain": ["gsd-cleanup"],
    },
    "gsd-review-backlog": {
        "tags": ["backlog-grooming", "backlog-promotion"],
        "triggers": ["审查待办", "提升待办", "review backlog"],
        "tool_chain": ["gsd-review-backlog"],
    },
    "gsd-join-discord": {
        "tags": ["community", "discord"],
        "triggers": ["加入社区", "join discord"],
        "tool_chain": ["gsd-join-discord"],
    },
    "gsd-next": {
        "tags": ["workflow-advance", "next-step"],
        "triggers": ["下一步", "继续", "next step", "前进"],
        "tool_chain": ["gsd-next"],
    },
    "gsd-graphify": {
        "tags": ["knowledge-graph", "codebase-graph", "graph-query"],
        "triggers": ["知识图谱", "构建图谱", "graphify"],
        "tool_chain": ["gsd-graphify"],
    },
    "gsd-capture": {
        "tags": ["capture", "ideation", "task-intake"],
        "triggers": ["捕获想法", "记录任务", "capture"],
        "tool_chain": ["gsd-capture"],
    },
    "gsd-sketch": {
        "tags": ["ui-sketch", "mockup", "html-prototype"],
        "triggers": ["草图", "UI 草图", "sketch", "快速设计"],
        "tool_chain": ["gsd-sketch"],
    },
    "gsd-spike": {
        "tags": ["technical-spike", "feasibility", "exploratory"],
        "triggers": ["技术验证", "探索", "spike"],
        "tool_chain": ["gsd-spike"],
    },
    "gsd-explore": {
        "tags": ["socratic-ideation", "brainstorm", "idea-routing"],
        "triggers": ["探索", "创意", "explore", "头脑风暴"],
        "tool_chain": ["gsd-explore"],
    },
    "gsd-extract-learnings": {
        "tags": ["learnings", "retrospective", "decisions"],
        "triggers": ["提取经验", "学习总结", "extract learnings"],
        "tool_chain": ["gsd-extract-learnings"],
    },
    "gsd-import": {
        "tags": ["external-plan-import", "conflict-detection"],
        "triggers": ["导入", "外部导入", "import"],
        "tool_chain": ["gsd-import"],
    },
    "gsd-inbox": {
        "tags": ["github-inbox", "issue-triage", "pr-triage"],
        "triggers": ["收件箱", "分类", "inbox", "issue 处理"],
        "tool_chain": ["gsd-inbox"],
    },
    "gsd-audit-fix": {
        "tags": ["audit-fix", "auto-remediation", "fix-pipeline"],
        "triggers": ["审计修复", "自动修复", "audit fix"],
        "tool_chain": ["gsd-audit-fix"],
    },
    "gsd-add-tests": {
        "tags": ["testing", "unit-test", "integration-test", "test-generation"],
        "triggers": [
            "添加测试", "写测试", "创建测试", "生成测试",
            "单元测试", "集成测试", "测试用例", "add tests",
        ],
        "tool_chain": ["gsd-add-tests", "gsd-verify-work"],
    },
    "gsd-team": {
        "tags": ["team-orchestration", "multi-agent", "collaboration"],
        "triggers": ["组建团队", "生成 team", "多人协作", "团队", "team"],
        "tool_chain": ["gsd-execute-phase", "gsd-verify-work"],
    },
    "gsd-ai-integration-phase": {
        "tags": ["ai-integration", "llm-spec", "eval-planning"],
        "triggers": ["AI 集成", "AI 规格", "ai integration"],
        "tool_chain": ["gsd-ai-integration-phase"],
    },
    "gsd-config": {
        "tags": ["gsd-config", "workflow-config", "integration-config"],
        "triggers": ["gsd 配置", "工作流配置", "配置工作流", "gsd config"],
        "tool_chain": ["gsd-config"],
    },
    "gsd-ns-context": {
        "tags": ["codebase-intelligence", "context-map", "代码库"],
        "triggers": ["上下文", "代码库情报", "ns context"],
        "tool_chain": ["gsd-ns-context"],
    },
    "gsd-ns-ideate": {
        "tags": ["ideation", "explore-capture", "sketch-spike"],
        "triggers": ["创意", "探索捕获", "ns ideate"],
        "tool_chain": ["gsd-ns-ideate"],
    },
    "gsd-ns-manage": {
        "tags": ["workspace-admin", "skillshare-manage", "inbox-manage"],
        "triggers": ["管理", "工作区管理", "ns manage"],
        "tool_chain": ["gsd-ns-manage"],
    },
    "gsd-ns-project": {
        "tags": ["project-lifecycle", "milestone-cycle"],
        "triggers": ["项目生命周期", "ns project"],
        "tool_chain": ["gsd-ns-project"],
    },
    "gsd-ns-review": {
        "tags": ["quality-gate", "review-cluster"],
        "triggers": ["质量审查", "ns review"],
        "tool_chain": ["gsd-ns-review"],
    },
    "gsd-ns-workflow": {
        "tags": ["gsd-workflow", "phase-progress", "workflow-commands"],
        "triggers": ["ns workflow", "gsd ns workflow", "GSD 工作流命令"],
        "tool_chain": ["gsd-ns-workflow"],
    },
    "gsd-phase": {
        "tags": ["phase-crud", "roadmap-management"],
        "triggers": ["阶段管理", "CRUD 阶段", "phase"],
        "tool_chain": ["gsd-phase"],
    },
    "gsd-plan-review-convergence": {
        "tags": ["plan-review", "convergence", "cross-ai"],
        "triggers": ["计划审查收敛", "plan review"],
        "tool_chain": ["gsd-plan-review-convergence"],
    },
    "gsd-surface": {
        "tags": ["skill-surface", "profile-toggle"],
        "triggers": ["切换技能", "surface skills"],
        "tool_chain": ["gsd-surface"],
    },
    "gsd-ultraplan-phase": {
        "tags": ["ultraplan", "cloud-planning", "planning"],
        "triggers": ["云端计划", "ultraplan"],
        "tool_chain": ["gsd-ultraplan-phase"],
    },
    "gsd-undo": {
        "tags": ["git-revert", "phase-rollback"],
        "triggers": ["撤销", "回滚", "undo", "revert"],
        "tool_chain": ["gsd-undo"],
    },
    "gsd-workspace": {
        "tags": ["workspace-manage", "isolated-environment"],
        "triggers": ["管理工作区", "workspace"],
        "tool_chain": ["gsd-workspace"],
    },
    "merlynr-dev-stack": {
        "tags": ["merlynr", "workflow-stack", "evidence-routing", "development", "nmem"],
        "triggers": ["merlynr", "Merlynr", "开发工作流", "dev stack", "工作流栈", "开始开发"],
        "tool_chain": ["gsd-do", "gsd-discuss-phase", "gsd-plan-phase", "gsd-execute-phase"],
    },
    "skillshare": {
        "tags": ["skillshare", "skills-sync", "agent-sync", "skills-management"],
        "triggers": ["skillshare", "skillshare sync", "同步 skill", "skills 管理"],
        "tool_chain": ["skillshare"],
    },
}


def yaml_list(items: list, indent: int = 0) -> str:
    """生成 YAML 列表格式"""
    prefix = "  " * indent
    lines = []
    for item in items:
        lines.append(f"{prefix}- {item}")
    return "\n".join(lines)


def add_metadata_to_skill(skill_name: str, metadata: dict) -> bool:
    """为单个 skill 添加元数据"""
    skill_dir = SKILLS_DIR / skill_name
    skill_file = skill_dir / "SKILL.md"
    
    if not skill_file.exists():
        print(f"  ⚠️  {skill_name}: SKILL.md 不存在")
        return False
    
    content = skill_file.read_text(encoding="utf-8")
    
    # 检查是否已有 tags 或 triggers
    if "tags:" in content and "triggers:" in content:
        print(f"  ⏭️  {skill_name}: 已有元数据，跳过")
        return False
    
    # 构建元数据块
    tags_str = yaml_list(metadata["tags"], indent=0)
    triggers_str = yaml_list(metadata["triggers"], indent=0)
    tool_chain_str = ", ".join(metadata["tool_chain"])
    
    metadata_block = f"""tags: [{', '.join(metadata['tags'])}]
triggers:
{triggers_str}
tool_chain: [{tool_chain_str}]
"""
    
    # 在 description 后插入元数据
    # 查找 description 行结束位置
    lines = content.split("\n")
    new_lines = []
    inserted = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        # 在 metadata: 或 --- 之前插入
        if not inserted and (line.strip().startswith("metadata:") or 
                           (line.strip() == "---" and i > 0 and new_lines[-2].strip() != "---")):
            # 在这行之前插入
            new_lines.pop()
            new_lines.extend(metadata_block.split("\n"))
            new_lines.append(line)
            inserted = True
    
    if not inserted:
        # 如果没找到合适位置，在第一个 --- 后插入
        final_lines = []
        found_first_dash = False
        for line in new_lines:
            final_lines.append(line)
            if line.strip() == "---" and not found_first_dash:
                found_first_dash = True
            elif found_first_dash and not inserted:
                final_lines.extend(metadata_block.split("\n"))
                inserted = True
    
    skill_file.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"  ✅ {skill_name}: 已添加元数据")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("  批量为 GSD skill 添加元数据配置")
    print("=" * 60)
    print()
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for skill_name, metadata in GSD_METADATA.items():
        if skill_name.startswith("gsd-"):
            result = add_metadata_to_skill(skill_name, metadata)
            if result:
                success_count += 1
            else:
                skip_count += 1
    
    print()
    print("=" * 60)
    print(f"  完成！成功: {success_count}, 跳过: {skip_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()

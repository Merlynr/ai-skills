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
        "tags": ["planning", "discussion", "requirements", "context"],
        "triggers": ["讨论阶段", "需求讨论", "收集需求", "discuss phase", "需求分析"],
        "tool_chain": ["gsd-discuss-phase", "gsd-spec-phase", "gsd-plan-phase"],
    },
    "gsd-plan-phase": {
        "tags": ["planning", "plan", "phase", "architecture"],
        "triggers": ["创建计划", "规划阶段", "写计划", "plan phase", "阶段规划"],
        "tool_chain": ["gsd-plan-phase", "gsd-execute-phase"],
    },
    "gsd-research-phase": {
        "tags": ["research", "planning", "investigation"],
        "triggers": ["研究阶段", "调研", "research phase", "技术调研"],
        "tool_chain": ["gsd-research-phase", "gsd-plan-phase"],
    },
    "gsd-list-phase-assumptions": {
        "tags": ["planning", "assumptions", "analysis"],
        "triggers": ["列出假设", "假设分析", "list assumptions"],
        "tool_chain": ["gsd-list-phase-assumptions", "gsd-plan-phase"],
    },
    "gsd-analyze-dependencies": {
        "tags": ["planning", "dependencies", "analysis"],
        "triggers": ["分析依赖", "依赖关系", "analyze dependencies"],
        "tool_chain": ["gsd-analyze-dependencies", "gsd-plan-phase"],
    },
    "gsd-spec-phase": {
        "tags": ["planning", "specification", "requirements"],
        "triggers": ["规格说明", "模糊度分析", "spec phase", "需求规格"],
        "tool_chain": ["gsd-spec-phase", "gsd-plan-phase"],
    },
    "gsd-mvp-phase": {
        "tags": ["planning", "mvp", "vertical-slice"],
        "triggers": ["MVP 切片", "最小可行", "mvp phase"],
        "tool_chain": ["gsd-mvp-phase", "gsd-plan-phase"],
    },
    
    # === 执行类 ===
    "gsd-execute-phase": {
        "tags": ["execute", "implement", "code", "development"],
        "triggers": ["执行阶段", "实现功能", "写代码", "execute phase", "开始开发"],
        "tool_chain": ["gsd-execute-phase", "gsd-verify-work"],
    },
    "gsd-fast": {
        "tags": ["execute", "fast", "trivial", "quick"],
        "triggers": ["快速执行", "简单任务", "fast task", "立即执行"],
        "tool_chain": ["gsd-fast"],
    },
    "gsd-quick": {
        "tags": ["execute", "quick", "simple"],
        "triggers": ["快速任务", "简单实现", "quick task"],
        "tool_chain": ["gsd-quick"],
    },
    "gsd-autonomous": {
        "tags": ["execute", "autonomous", "batch", "automated"],
        "triggers": ["自动执行", "自主执行", "autonomous", "批量执行"],
        "tool_chain": ["gsd-autonomous"],
    },
    
    # === 审查类 ===
    "gsd-code-review": {
        "tags": ["review", "code-review", "quality", "security"],
        "triggers": ["代码审查", "code review", "安全审计", "审查代码"],
        "tool_chain": ["gsd-code-review", "gsd-validate-phase"],
    },
    "gsd-validate-phase": {
        "tags": ["review", "validate", "verification", "audit"],
        "triggers": ["验证阶段", "验证缺口", "validate phase", "补充验证"],
        "tool_chain": ["gsd-validate-phase", "gsd-verify-work"],
    },
    "gsd-verify-work": {
        "tags": ["review", "verify", "uat", "testing"],
        "triggers": ["验证工作", "UAT 验证", "verify work", "功能验证"],
        "tool_chain": ["gsd-verify-work"],
    },
    "gsd-review": {
        "tags": ["review", "peer-review", "cross-ai"],
        "triggers": ["同行审查", "外部审查", "peer review", "交叉审查"],
        "tool_chain": ["gsd-review"],
    },
    "gsd-audit-uat": {
        "tags": ["review", "audit", "uat", "verification"],
        "triggers": ["UAT 审计", "验证审计", "audit uat"],
        "tool_chain": ["gsd-audit-uat"],
    },
    "gsd-audit-milestone": {
        "tags": ["review", "audit", "milestone"],
        "triggers": ["里程碑审计", "milestone audit"],
        "tool_chain": ["gsd-audit-milestone"],
    },
    "gsd-eval-review": {
        "tags": ["review", "evaluation", "audit"],
        "triggers": ["评估审查", "eval review"],
        "tool_chain": ["gsd-eval-review"],
    },
    
    # === 调试类 ===
    "gsd-debug": {
        "tags": ["debug", "troubleshoot", "fix", "problem"],
        "triggers": ["调试", "排错", "修复 bug", "debug", "问题排查"],
        "tool_chain": ["gsd-debug", "gsd-forensics"],
    },
    "gsd-forensics": {
        "tags": ["debug", "forensics", "post-mortem", "analysis"],
        "triggers": ["事后分析", "故障分析", "forensics", "根因分析"],
        "tool_chain": ["gsd-forensics"],
    },
    
    # === 文档类 ===
    "gsd-docs-update": {
        "tags": ["docs", "documentation", "update"],
        "triggers": ["更新文档", "生成文档", "docs update", "文档维护"],
        "tool_chain": ["gsd-docs-update"],
    },
    "gsd-ingest-docs": {
        "tags": ["docs", "ingest", "import", "bootstrap"],
        "triggers": ["导入文档", "初始化文档", "ingest docs"],
        "tool_chain": ["gsd-ingest-docs"],
    },
    "gsd-milestone-summary": {
        "tags": ["docs", "summary", "milestone", "report"],
        "triggers": ["里程碑总结", "项目总结", "milestone summary"],
        "tool_chain": ["gsd-milestone-summary"],
    },
    "gsd-session-report": {
        "tags": ["docs", "report", "session", "summary"],
        "triggers": ["会话报告", "session report", "工作报告"],
        "tool_chain": ["gsd-session-report"],
    },
    
    # === 项目管理类 ===
    "gsd-new-project": {
        "tags": ["project", "initialize", "setup", "new"],
        "triggers": ["新建项目", "初始化项目", "new project", "项目初始化"],
        "tool_chain": ["gsd-new-project"],
    },
    "gsd-new-milestone": {
        "tags": ["project", "milestone", "new", "cycle"],
        "triggers": ["新建里程碑", "开始里程碑", "new milestone"],
        "tool_chain": ["gsd-new-milestone"],
    },
    "gsd-complete-milestone": {
        "tags": ["project", "milestone", "complete", "archive"],
        "triggers": ["完成里程碑", "归档里程碑", "complete milestone"],
        "tool_chain": ["gsd-complete-milestone"],
    },
    "gsd-progress": {
        "tags": ["project", "progress", "status", "check"],
        "triggers": ["检查进度", "项目进度", "progress", "当前状态"],
        "tool_chain": ["gsd-progress"],
    },
    "gsd-stats": {
        "tags": ["project", "stats", "statistics", "metrics"],
        "triggers": ["项目统计", "统计数据", "stats", "项目指标"],
        "tool_chain": ["gsd-stats"],
    },
    "gsd-manager": {
        "tags": ["project", "manager", "command-center", "interactive"],
        "triggers": ["项目管理", "管理器", "manager", "命令中心"],
        "tool_chain": ["gsd-manager"],
    },
    
    # === 任务管理类 ===
    "gsd-add-todo": {
        "tags": ["task", "todo", "capture", "idea"],
        "triggers": ["添加待办", "记录想法", "add todo", "待办事项"],
        "tool_chain": ["gsd-add-todo"],
    },
    "gsd-check-todos": {
        "tags": ["task", "todo", "list", "check"],
        "triggers": ["查看待办", "待办列表", "check todos"],
        "tool_chain": ["gsd-check-todos"],
    },
    "gsd-note": {
        "tags": ["task", "note", "capture", "idea"],
        "triggers": ["记笔记", "记录", "note", "快速记录"],
        "tool_chain": ["gsd-note"],
    },
    "gsd-add-backlog": {
        "tags": ["task", "backlog", "idea", "parking"],
        "triggers": ["添加到待办", "backlog", "暂存想法"],
        "tool_chain": ["gsd-add-backlog"],
    },
    "gsd-plant-seed": {
        "tags": ["task", "seed", "idea", "future"],
        "triggers": ["播种想法", "未来计划", "plant seed"],
        "tool_chain": ["gsd-plant-seed"],
    },
    
    # === 阶段管理类 ===
    "gsd-add-phase": {
        "tags": ["phase", "add", "roadmap"],
        "triggers": ["添加阶段", "新增阶段", "add phase"],
        "tool_chain": ["gsd-add-phase"],
    },
    "gsd-insert-phase": {
        "tags": ["phase", "insert", "urgent", "priority"],
        "triggers": ["插入阶段", "紧急任务", "insert phase"],
        "tool_chain": ["gsd-insert-phase"],
    },
    "gsd-remove-phase": {
        "tags": ["phase", "remove", "delete"],
        "triggers": ["删除阶段", "移除阶段", "remove phase"],
        "tool_chain": ["gsd-remove-phase"],
    },
    "gsd-plan-milestone-gaps": {
        "tags": ["phase", "gaps", "milestone", "closure"],
        "triggers": ["规划缺口", "关闭缺口", "plan gaps"],
        "tool_chain": ["gsd-plan-milestone-gaps"],
    },
    
    # === 工作区管理类 ===
    "gsd-new-workspace": {
        "tags": ["workspace", "new", "isolate", "create"],
        "triggers": ["新建工作区", "创建工作区", "new workspace"],
        "tool_chain": ["gsd-new-workspace"],
    },
    "gsd-list-workspaces": {
        "tags": ["workspace", "list", "status"],
        "triggers": ["列出工作区", "工作区列表", "list workspaces"],
        "tool_chain": ["gsd-list-workspaces"],
    },
    "gsd-remove-workspace": {
        "tags": ["workspace", "remove", "delete", "cleanup"],
        "triggers": ["删除工作区", "移除工作区", "remove workspace"],
        "tool_chain": ["gsd-remove-workspace"],
    },
    
    # === UI 类 ===
    "gsd-ui-phase": {
        "tags": ["ui", "design", "frontend", "spec"],
        "triggers": ["UI 设计", "界面设计", "ui phase", "前端规格"],
        "tool_chain": ["gsd-ui-phase"],
    },
    "gsd-ui-review": {
        "tags": ["ui", "review", "visual", "audit"],
        "triggers": ["UI 审查", "界面审查", "ui review", "视觉审计"],
        "tool_chain": ["gsd-ui-review"],
    },
    
    # === 安全类 ===
    "gsd-secure-phase": {
        "tags": ["security", "audit", "threat", "mitigation"],
        "triggers": ["安全验证", "安全审计", "secure phase", "威胁分析"],
        "tool_chain": ["gsd-secure-phase"],
    },
    
    # === 工具类 ===
    "gsd-do": {
        "tags": ["utility", "route", "dispatch", "auto"],
        "triggers": ["自动路由", "智能分发", "do command"],
        "tool_chain": ["gsd-do"],
    },
    "gsd-help": {
        "tags": ["utility", "help", "guide", "reference"],
        "triggers": ["帮助", "使用指南", "help", "命令列表"],
        "tool_chain": ["gsd-help"],
    },
    "gsd-health": {
        "tags": ["utility", "health", "diagnose", "repair"],
        "triggers": ["健康检查", "诊断问题", "health check"],
        "tool_chain": ["gsd-health"],
    },
    "gsd-map-codebase": {
        "tags": ["utility", "codebase", "map", "analyze"],
        "triggers": ["映射代码库", "分析代码", "map codebase", "代码结构"],
        "tool_chain": ["gsd-map-codebase"],
    },
    "gsd-update": {
        "tags": ["utility", "update", "upgrade", "maintenance"],
        "triggers": ["gsd升级", "升级 GSD", "升级GSD", "gsd update", "更新GSD"],
        "tool_chain": ["gsd-update", "gsd-reapply-patches"],
    },
    "gsd-reapply-patches": {
        "tags": ["utility", "patch", "reapply", "restore"],
        "triggers": ["重新应用补丁", "恢复修改", "reapply patches"],
        "tool_chain": ["gsd-reapply-patches"],
    },
    "gsd-settings": {
        "tags": ["utility", "settings", "config", "configure"],
        "triggers": ["设置", "配置", "settings", "工作流配置"],
        "tool_chain": ["gsd-settings"],
    },
    "gsd-set-profile": {
        "tags": ["utility", "profile", "model", "switch"],
        "triggers": ["设置配置", "切换模型", "set profile"],
        "tool_chain": ["gsd-set-profile"],
    },
    "gsd-ship": {
        "tags": ["utility", "ship", "pr", "merge", "release"],
        "triggers": ["发布", "创建 PR", "ship", "准备合并"],
        "tool_chain": ["gsd-ship"],
    },
    "gsd-pr-branch": {
        "tags": ["utility", "pr", "branch", "clean"],
        "triggers": ["PR 分支", "创建分支", "pr branch"],
        "tool_chain": ["gsd-pr-branch"],
    },
    "gsd-thread": {
        "tags": ["utility", "thread", "context", "persistent"],
        "triggers": ["管理线程", "上下文线程", "thread"],
        "tool_chain": ["gsd-thread"],
    },
    "gsd-pause-work": {
        "tags": ["utility", "pause", "handoff", "context"],
        "triggers": ["暂停工作", "上下文交接", "pause work"],
        "tool_chain": ["gsd-pause-work"],
    },
    "gsd-resume-work": {
        "tags": ["utility", "resume", "restore", "continue"],
        "triggers": ["恢复工作", "继续工作", "resume work"],
        "tool_chain": ["gsd-resume-work"],
    },
    "gsd-workstreams": {
        "tags": ["utility", "workstream", "parallel", "manage"],
        "triggers": ["管理工作流", "并行工作", "workstream"],
        "tool_chain": ["gsd-workstreams"],
    },
    "gsd-profile-user": {
        "tags": ["utility", "profile", "user", "behavior"],
        "triggers": ["用户画像", "行为分析", "profile user"],
        "tool_chain": ["gsd-profile-user"],
    },
    "gsd-cleanup": {
        "tags": ["utility", "cleanup", "archive", "maintenance"],
        "triggers": ["清理", "归档", "cleanup", "维护"],
        "tool_chain": ["gsd-cleanup"],
    },
    "gsd-review-backlog": {
        "tags": ["utility", "backlog", "review", "promote"],
        "triggers": ["审查待办", "提升待办", "review backlog"],
        "tool_chain": ["gsd-review-backlog"],
    },
    "gsd-join-discord": {
        "tags": ["utility", "community", "discord", "join"],
        "triggers": ["加入社区", "join discord"],
        "tool_chain": ["gsd-join-discord"],
    },
    "gsd-next": {
        "tags": ["utility", "next", "advance", "workflow"],
        "triggers": ["下一步", "继续", "next step", "前进"],
        "tool_chain": ["gsd-next"],
    },
    "gsd-graphify": {
        "tags": ["utility", "graph", "knowledge", "analyze"],
        "triggers": ["知识图谱", "构建图谱", "graphify"],
        "tool_chain": ["gsd-graphify"],
    },
    "gsd-capture": {
        "tags": ["utility", "capture", "idea", "task"],
        "triggers": ["捕获想法", "记录任务", "capture"],
        "tool_chain": ["gsd-capture"],
    },
    "gsd-sketch": {
        "tags": ["utility", "sketch", "ui", "design", "mockup"],
        "triggers": ["草图", "UI 草图", "sketch", "快速设计"],
        "tool_chain": ["gsd-sketch"],
    },
    "gsd-spike": {
        "tags": ["utility", "spike", "explore", "validate"],
        "triggers": ["技术验证", "探索", "spike"],
        "tool_chain": ["gsd-spike"],
    },
    "gsd-explore": {
        "tags": ["utility", "explore", "ideate", "socratic"],
        "triggers": ["探索", "创意", "explore", "头脑风暴"],
        "tool_chain": ["gsd-explore"],
    },
    "gsd-extract-learnings": {
        "tags": ["utility", "learnings", "extract", "knowledge"],
        "triggers": ["提取经验", "学习总结", "extract learnings"],
        "tool_chain": ["gsd-extract-learnings"],
    },
    "gsd-import": {
        "tags": ["utility", "import", "ingest", "external"],
        "triggers": ["导入", "外部导入", "import"],
        "tool_chain": ["gsd-import"],
    },
    "gsd-inbox": {
        "tags": ["utility", "inbox", "triage", "github"],
        "triggers": ["收件箱", "分类", "inbox", "issue 处理"],
        "tool_chain": ["gsd-inbox"],
    },
    "gsd-code-review": {
        "tags": ["review", "code-review", "quality", "security"],
        "triggers": ["代码审查", "code review", "安全审计", "审查代码"],
        "tool_chain": ["gsd-code-review", "gsd-validate-phase"],
    },
    "gsd-audit-fix": {
        "tags": ["review", "audit", "fix", "pipeline"],
        "triggers": ["审计修复", "自动修复", "audit fix"],
        "tool_chain": ["gsd-audit-fix"],
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

# 新增的 skill 元数据
NEW_GSD_METADATA = {
    "gsd-ai-integration-phase": {
        "tags": ["ai", "integration", "planning", "spec"],
        "triggers": ["AI 集成", "AI 规格", "ai integration"],
        "tool_chain": ["gsd-ai-integration-phase"],
    },
    "gsd-config": {
        "tags": ["config", "settings", "workflow"],
        "triggers": ["配置", "工作流配置", "config"],
        "tool_chain": ["gsd-config"],
    },
    "gsd-ns-context": {
        "tags": ["context", "codebase", "intelligence"],
        "triggers": ["上下文", "代码库情报", "ns context"],
        "tool_chain": ["gsd-ns-context"],
    },
    "gsd-ns-ideate": {
        "tags": ["ideate", "explore", "capture"],
        "triggers": ["创意", "探索捕获", "ns ideate"],
        "tool_chain": ["gsd-ns-ideate"],
    },
    "gsd-ns-manage": {
        "tags": ["manage", "config", "workspace"],
        "triggers": ["管理", "工作区管理", "ns manage"],
        "tool_chain": ["gsd-ns-manage"],
    },
    "gsd-ns-project": {
        "tags": ["project", "lifecycle", "milestone"],
        "triggers": ["项目生命周期", "ns project"],
        "tool_chain": ["gsd-ns-project"],
    },
    "gsd-ns-review": {
        "tags": ["review", "quality", "audit"],
        "triggers": ["质量审查", "ns review"],
        "tool_chain": ["gsd-ns-review"],
    },
    "gsd-ns-workflow": {
        "tags": ["workflow", "phase", "progress"],
        "triggers": ["工作流", "ns workflow"],
        "tool_chain": ["gsd-ns-workflow"],
    },
    "gsd-phase": {
        "tags": ["phase", "crud", "roadmap"],
        "triggers": ["阶段管理", "CRUD 阶段", "phase"],
        "tool_chain": ["gsd-phase"],
    },
    "gsd-plan-review-convergence": {
        "tags": ["plan", "review", "convergence"],
        "triggers": ["计划审查收敛", "plan review"],
        "tool_chain": ["gsd-plan-review-convergence"],
    },
    "gsd-surface": {
        "tags": ["surface", "skills", "toggle"],
        "triggers": ["切换技能", "surface skills"],
        "tool_chain": ["gsd-surface"],
    },
    "gsd-ultraplan-phase": {
        "tags": ["plan", "ultraplan", "cloud"],
        "triggers": ["云端计划", "ultraplan"],
        "tool_chain": ["gsd-ultraplan-phase"],
    },
    "gsd-undo": {
        "tags": ["undo", "revert", "rollback"],
        "triggers": ["撤销", "回滚", "undo", "revert"],
        "tool_chain": ["gsd-undo"],
    },
    "gsd-workspace": {
        "tags": ["workspace", "manage", "isolate"],
        "triggers": ["管理工作区", "workspace"],
        "tool_chain": ["gsd-workspace"],
    },
}

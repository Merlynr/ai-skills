#!/usr/bin/env python3
"""
GSD Team Generator for OpenCode (Skill-Aware)
生成可在 OpenCode 中直接使用的团队配置，支持 skill 感知

用法:
    python gsd-team-gen.py "任务描述"
    python gsd-team-gen.py "任务描述" --output team.json
    python gsd-team-gen.py --interactive
    python gsd-team-gen.py --list-skills
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
REGISTRY_PATH = SCRIPT_DIR / "skill-registry.json"
WORKSPACE = Path.home() / ".config" / "opencode" / "team_workspace"


def load_skill_registry() -> dict:
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"categories": {}, "task_patterns": {}}


def analyze_task(task_desc: str, registry: dict) -> dict:
    task_lower = task_desc.lower()
    matched_patterns = []
    recommended_skills = []

    for pattern_name, pattern in registry.get("task_patterns", {}).items():
        keywords = pattern.get("keywords", [])
        if any(k in task_lower for k in keywords):
            matched_patterns.append(pattern_name)
            recommended_skills.extend(pattern.get("recommended_skills", []))

    needs_frontend = any(k in task_lower for k in ["ui", "前端", "界面", "css", "react", "vue"])
    needs_backend = any(k in task_lower for k in ["api", "后端", "数据库", "server"])
    needs_arch = any(k in task_lower for k in ["架构", "设计", "重构"])
    needs_debug = any(k in task_lower for k in ["调试", "bug", "错误", "修复"])
    needs_docs = any(k in task_lower for k in ["文档", "doc", "readme"])

    return {
        "matched_patterns": matched_patterns,
        "recommended_skills": list(set(recommended_skills)),
        "needs_frontend": needs_frontend,
        "needs_backend": needs_backend,
        "needs_architecture": needs_arch,
        "needs_debugging": needs_debug,
        "needs_documentation": needs_docs
    }


def get_skills_for_phase(phase: str, registry: dict, analysis: dict) -> list:
    phase_skills = registry.get("categories", {}).get(phase, {}).get("skills", [])
    recommended = []

    for skill in phase_skills:
        skill_name = skill["name"]
        if skill_name in analysis.get("recommended_skills", []):
            recommended.insert(0, skill_name)
        else:
            recommended.append(skill_name)

    return recommended[:3]


def generate_team_config(task_desc: str, team_name: str = None) -> dict:
    registry = load_skill_registry()
    analysis = analyze_task(task_desc, registry)

    if not team_name:
        team_name = "task-team"

    plan_skills = get_skills_for_phase("plan", registry, analysis)
    implement_skills = get_skills_for_phase("implement", registry, analysis)
    verify_skills = get_skills_for_phase("verify", registry, analysis)
    debug_skills = get_skills_for_phase("debug", registry, analysis)

    members = []

    members.append({
        "name": "architect",
        "role": "架构师",
        "phase": "plan",
        "kind": "subagent_type",
        "subagent_type": "oracle",
        "prompt": f"分析任务需求，设计系统架构：{task_desc}",
        "skills": plan_skills,
        "skill_purpose": "使用规划类 skills 进行需求分析和架构设计"
    })

    members.append({
        "name": "researcher",
        "role": "研究员",
        "phase": "plan",
        "kind": "subagent_type",
        "subagent_type": "explore",
        "prompt": f"探索代码库，查找相关模式和实现：{task_desc}",
        "skills": plan_skills,
        "skill_purpose": "使用探索类 skills 理解现有代码"
    })

    impl_category = "visual-engineering" if analysis["needs_frontend"] else "unspecified-high"
    members.append({
        "name": "implementer",
        "role": "实现者",
        "phase": "implement",
        "kind": "category",
        "category": impl_category,
        "prompt": f"实现功能代码，遵循项目现有模式：{task_desc}",
        "skills": implement_skills,
        "skill_purpose": "使用实现类 skills 执行编码和测试"
    })

    members.append({
        "name": "reviewer",
        "role": "审查者",
        "phase": "verify",
        "kind": "subagent_type",
        "subagent_type": "oracle",
        "prompt": f"审查代码质量、安全性和最佳实践：{task_desc}",
        "skills": verify_skills,
        "skill_purpose": "使用验证类 skills 进行代码审查"
    })

    if analysis["needs_debugging"]:
        members.append({
            "name": "debugger",
            "role": "调试专家",
            "phase": "debug",
            "kind": "subagent_type",
            "subagent_type": "oracle",
            "prompt": f"诊断和修复问题：{task_desc}",
            "skills": debug_skills,
            "skill_purpose": "使用调试类 skills 诊断问题"
        })

    if analysis["needs_docs"]:
        members.append({
            "name": "documenter",
            "role": "文档编写者",
            "phase": "implement",
            "kind": "category",
            "category": "writing",
            "prompt": f"编写和更新项目文档：{task_desc}",
            "skills": ["gsd-docs-update", "gsd-ingest-docs"],
            "skill_purpose": "使用文档类 skills 更新文档"
        })

    config = {
        "name": team_name,
        "task": task_desc,
        "version": "2.0",
        "created_at": None,
        "members": members,
        "workflow": {
            "phases": ["plan", "implement", "verify"],
            "parallel_execution": True,
            "max_concurrent": 4
        },
        "analysis": analysis,
        "skill_registry_version": registry.get("version", "unknown")
    }

    return config


def save_config(config: dict, output_path: str = None) -> str:
    if not output_path:
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        output_path = WORKSPACE / f"{config['name']}.json"

    config["created_at"] = datetime.now().isoformat()

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return str(output_path)


def generate_opencode_commands(config: dict) -> str:
    commands = []
    commands.append(f"# 团队: {config['name']}")
    commands.append(f"# 任务: {config['task']}")
    commands.append(f"# Skills: {', '.join(config['analysis'].get('recommended_skills', []))}")
    commands.append("")
    commands.append("# 按阶段执行")
    commands.append("")

    phases = {}
    for member in config["members"]:
        phase = member["phase"]
        if phase not in phases:
            phases[phase] = []
        phases[phase].append(member)

    for phase, members in phases.items():
        commands.append(f"# === {phase.upper()} 阶段 ===")
        for member in members:
            skills_str = json.dumps(member["skills"])
            if member["kind"] == "subagent_type":
                commands.append(f'# {member["role"]} - {member.get("skill_purpose", "")}')
                commands.append(f'task(subagent_type="{member["subagent_type"]}", load_skills={skills_str}, run_in_background=true, prompt="""{member["prompt"]}""")')
            else:
                commands.append(f'# {member["role"]} - {member.get("skill_purpose", "")}')
                commands.append(f'task(category="{member["category"]}", load_skills={skills_str}, run_in_background=true, prompt="""{member["prompt"]}""")')
            commands.append("")
        commands.append("")

    return "\n".join(commands)


def print_team_summary(config: dict):
    print("\n" + "=" * 70)
    print(f"  团队: {config['name']}")
    print(f"  任务: {config['task'][:50]}...")
    print(f"  匹配模式: {', '.join(config['analysis'].get('matched_patterns', []))}")
    print("=" * 70)

    print("\n  成员配置:")
    print("-" * 70)

    for i, member in enumerate(config["members"], 1):
        kind = member.get("subagent_type") or member.get("category")
        skills = ", ".join(member.get("skills", [])[:3])
        print(f"  {i}. {member['name']} ({member['role']})")
        print(f"     类型: {member['kind']} = {kind}")
        print(f"     阶段: {member['phase']}")
        print(f"     Skills: {skills}")
        print(f"     用途: {member.get('skill_purpose', 'N/A')}")
        print()

    print("-" * 70)
    print(f"  总计: {len(config['members'])} 个成员")
    print(f"  推荐 Skills: {', '.join(config['analysis'].get('recommended_skills', [])[:5])}")
    print("=" * 70)


def list_skills():
    registry = load_skill_registry()

    print("\n=== Skills 注册表 ===\n")

    for category, info in registry.get("categories", {}).items():
        print(f"\n## {category.upper()} - {info['description']}")
        print("-" * 50)
        for skill in info.get("skills", []):
            print(f"  {skill['name']}: {skill['description']}")
            print(f"    使用场景: {skill['use_when']}")

    print("\n\n=== 任务模式 ===\n")
    for pattern, info in registry.get("task_patterns", {}).items():
        print(f"  {pattern}: {', '.join(info['keywords'])}")
        print(f"    推荐 Skills: {', '.join(info['recommended_skills'][:3])}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="GSD Team Generator for OpenCode (Skill-Aware)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python gsd-team-gen.py "实现用户认证系统"
  python gsd-team-gen.py "修复登录 bug" --name auth-fix
  python gsd-team-gen.py --list-skills
  python gsd-team-gen.py --interactive
        """
    )

    parser.add_argument("task", nargs="?", help="任务描述")
    parser.add_argument("--name", "-n", help="团队名称")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--commands", "-c", action="store_true", help="生成 OpenCode 命令")
    parser.add_argument("--list-skills", "-l", action="store_true", help="列出所有可用 skills")
    parser.add_argument("--list-types", "-t", action="store_true", help="列出支持的类型")

    args = parser.parse_args()

    if args.list_skills:
        list_skills()
        return

    if args.list_types:
        registry = load_skill_registry()
        print("\n支持的 Category 类型:")
        for k in ["visual-engineering", "artistry", "ultrabrain", "deep", "quick", "unspecified-low", "unspecified-high", "writing"]:
            print(f"  {k}")

        print("\n支持的 Subagent Type 类型:")
        for k in ["explore", "librarian", "oracle", "metis", "momus"]:
            print(f"  {k}")

        print("\nGSD 阶段:")
        for k, v in registry.get("categories", {}).items():
            print(f"  {k}: {v['description']}")
        return

    if args.interactive:
        print("\n=== GSD Team Generator (Skill-Aware) ===\n")
        task = input("请输入任务描述: ").strip()
        if not task:
            print("错误: 任务描述不能为空")
            sys.exit(1)
        name = input("团队名称 (可选，回车跳过): ").strip() or None
    else:
        task = args.task
        name = args.name

        if not task:
            parser.print_help()
            sys.exit(1)

    config = generate_team_config(task, name)

    print_team_summary(config)

    output_path = save_config(config, args.output)
    print(f"\n配置已保存到: {output_path}")

    if args.commands:
        print("\n" + "=" * 70)
        print("  OpenCode 命令:")
        print("=" * 70)
        print(generate_opencode_commands(config))

    print("\n使用方法:")
    print(f"  1. 在 OpenCode 中读取配置: read(\"{output_path}\")")
    print(f"  2. 或直接复制上面的命令执行")
    print(f"  3. 查看可用 skills: python gsd-team-gen.py --list-skills")
    print()


if __name__ == "__main__":
    main()

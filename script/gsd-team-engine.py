#!/usr/bin/env python3
"""
GSD Team Engine - Skill-Aware Task Execution System
实现意图识别、动态 Skill 加载和反馈循环

用法:
    python gsd-team-engine.py "任务描述"
    python gsd-team-engine.py --analyze "任务描述"
    python gsd-team-engine.py --learn "任务描述" --result success
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

SCRIPT_DIR = Path(__file__).parent
SKILLS_DIR = Path.home() / ".config" / "skillshare" / "skills"
WORKSPACE = Path.home() / ".config" / "opencode" / "team_workspace"
LEARNINGS_DIR = SCRIPT_DIR / "learnings"


class SkillMetadata:
    """Skill 元数据解析器"""
    
    @staticmethod
    def parse_skill(skill_path: Path) -> Dict:
        """解析 SKILL.md 文件，提取元数据"""
        if not skill_path.exists():
            return None
        
        content = skill_path.read_text(encoding='utf-8')
        
        metadata = {
            "name": skill_path.parent.name,
            "path": str(skill_path),
            "tags": [],
            "triggers": [],
            "tool_chain": [],
            "context_injection": True,
            "description": "",
            "steps": [],
            "learnings": []
        }
        
        # 解析 YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            
            # 提取 tags
            tags_match = re.search(r'tags:\s*\[(.*?)\]', yaml_content)
            if tags_match:
                metadata["tags"] = [t.strip() for t in tags_match.group(1).split(',')]
            
            # 提取 triggers
            triggers_match = re.search(r'triggers:\s*\[(.*?)\]', yaml_content)
            if triggers_match:
                metadata["triggers"] = [t.strip().strip('"\'') for t in triggers_match.group(1).split(',')]
            
            # 提取 tool_chain
            chain_match = re.search(r'tool_chain:\s*\[(.*?)\]', yaml_content)
            if chain_match:
                metadata["tool_chain"] = [t.strip().strip('"\'') for t in chain_match.group(1).split(',')]
            
            # 提取 description
            desc_match = re.search(r'description:\s*["\']?(.*?)["\']?\s*$', yaml_content, re.MULTILINE)
            if desc_match:
                metadata["description"] = desc_match.group(1)
        
        # 提取步骤（从正文）
        steps_section = re.search(r'(?:## 步骤|## Steps|## 执行流程)\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if steps_section:
            steps = re.findall(r'(?:步骤|Step)\s*\d+[：:]\s*(.*)', steps_section.group(1))
            metadata["steps"] = [s.strip() for s in steps if s.strip()]
        
        # 提取 learnings（如果存在）
        learnings_section = re.search(r'## 学习记录\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if learnings_section:
            metadata["learnings"] = learnings_section.group(1).strip().split('\n')
        
        return metadata


class IntentRecognizer:
    """意图识别器"""
    
    def __init__(self):
        self.skills_cache = {}
        self.load_all_skills()
    
    def load_all_skills(self):
        """加载所有 Skill 的元数据"""
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    metadata = SkillMetadata.parse_skill(skill_md)
                    if metadata:
                        self.skills_cache[skill_dir.name] = metadata
    
    def identify_intent(self, task_desc: str) -> Dict:
        """识别任务意图，返回匹配的 Skills"""
        task_lower = task_desc.lower()
        
        # 1. 关键词匹配（快速路径）
        keyword_matches = self._keyword_match(task_lower)
        
        # 2. 触发词匹配
        trigger_matches = self._trigger_match(task_lower)
        
        # 3. 标签匹配
        tag_matches = self._tag_match(task_lower)
        
        # 合并结果并评分
        scored_skills = self._score_matches(keyword_matches, trigger_matches, tag_matches)
        
        # 按分数排序
        sorted_skills = sorted(scored_skills.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "task": task_desc,
            "matched_skills": sorted_skills[:10],  # Top 10
            "primary_skill": sorted_skills[0][0] if sorted_skills else None,
            "confidence": sorted_skills[0][1] if sorted_skills else 0
        }
    
    def _keyword_match(self, task: str) -> List[str]:
        """关键词匹配"""
        matches = []
        
        keyword_map = {
            "debug": ["调试", "bug", "错误", "修复", "fix", "debug", "问题"],
            "plan": ["计划", "规划", "设计", "架构", "plan", "design"],
            "implement": ["实现", "编写", "开发", "代码", "implement", "code"],
            "verify": ["验证", "测试", "审查", "review", "test", "verify"],
            "ui": ["前端", "界面", "ui", "css", "react", "vue", "组件"],
            "api": ["接口", "api", "后端", "server", "数据库"],
            "docs": ["文档", "doc", "readme", "说明"],
            "performance": ["性能", "优化", "performance", "optimize"],
            "security": ["安全", "漏洞", "security", "vulnerability"],
            "refactor": ["重构", "refactor", "重写", "清理"]
        }
        
        for category, keywords in keyword_map.items():
            if any(k in task for k in keywords):
                matches.append(category)
        
        return matches
    
    def _trigger_match(self, task: str) -> List[str]:
        """触发词匹配"""
        matches = []
        
        for skill_name, metadata in self.skills_cache.items():
            for trigger in metadata.get("triggers", []):
                if trigger.lower() in task:
                    matches.append(skill_name)
                    break
        
        return matches
    
    def _tag_match(self, task: str) -> List[str]:
        """标签匹配"""
        matches = []
        
        for skill_name, metadata in self.skills_cache.items():
            for tag in metadata.get("tags", []):
                if tag.lower() in task:
                    matches.append(skill_name)
                    break
        
        return matches
    
    def _score_matches(self, keyword_matches, trigger_matches, tag_matches) -> Dict[str, float]:
        """计算匹配分数"""
        scores = {}
        
        # 触发词匹配权重最高（3分）
        for skill in trigger_matches:
            scores[skill] = scores.get(skill, 0) + 3.0
        
        # 标签匹配权重中等（2分）
        for skill in tag_matches:
            scores[skill] = scores.get(skill, 0) + 2.0
        
        # 关键词匹配权重较低（1分），但需要映射到具体 skill
        keyword_to_skills = {
            "debug": ["gsd-debug", "gsd-forensics"],
            "plan": ["gsd-plan-phase", "gsd-discuss-phase"],
            "implement": ["gsd-execute-phase", "gsd-fast"],
            "verify": ["gsd-code-review", "gsd-validate-phase"],
            "ui": ["gsd-ui-phase", "gsd-ui-review"],
            "api": ["gsd-code-review", "gsd-add-tests"],
            "docs": ["gsd-docs-update", "gsd-ingest-docs"],
            "performance": ["gsd-debug", "gsd-validate-phase"],
            "security": ["gsd-secure-phase", "gsd-code-review"],
            "refactor": ["gsd-map-codebase", "gsd-execute-phase"]
        }
        
        for keyword in keyword_matches:
            for skill in keyword_to_skills.get(keyword, []):
                scores[skill] = scores.get(skill, 0) + 1.0
        
        return scores


class DynamicSkillLoader:
    """动态 Skill 加载器"""
    
    def __init__(self, intent_recognizer: IntentRecognizer):
        self.recognizer = intent_recognizer
    
    def load_skills_for_task(self, task_desc: str, phase: str = None) -> List[str]:
        """为任务动态加载 Skills"""
        intent = self.recognizer.identify_intent(task_desc)
        
        skills = []
        for skill_name, score in intent["matched_skills"]:
            if score >= 2.0:  # 阈值过滤
                metadata = self.recognizer.skills_cache.get(skill_name)
                if metadata:
                    # 如果指定了阶段，过滤对应阶段的 skill
                    if phase:
                        if self._skill_matches_phase(skill_name, phase):
                            skills.append(skill_name)
                    else:
                        skills.append(skill_name)
        
        return skills[:5]  # 最多返回 5 个
    
    def _skill_matches_phase(self, skill_name: str, phase: str) -> bool:
        """检查 skill 是否匹配阶段"""
        phase_skills = {
            "plan": ["gsd-discuss-phase", "gsd-spec-phase", "gsd-plan-phase", 
                     "gsd-explore", "gsd-mvp-phase", "gsd-map-codebase"],
            "implement": ["gsd-execute-phase", "gsd-fast", "gsd-capture", 
                         "commit-message", "gsd-add-tests", "gsd-docs-update"],
            "verify": ["gsd-code-review", "gsd-audit-fix", "gsd-secure-phase",
                      "gsd-validate-phase", "gsd-verify-work", "gsd-ui-review"],
            "debug": ["gsd-debug", "gsd-forensics", "gsd-health"],
            "manage": ["gsd-progress", "gsd-manager", "gsd-milestone-summary",
                      "gsd-complete-milestone", "gsd-ship"]
        }
        
        return skill_name in phase_skills.get(phase, [])
    
    def get_skill_tool_chain(self, skill_name: str) -> List[str]:
        """获取 skill 的工具链"""
        metadata = self.recognizer.skills_cache.get(skill_name)
        if metadata:
            return metadata.get("tool_chain", [])
        return []


class FeedbackLoop:
    """反馈循环系统"""
    
    def __init__(self):
        self.learnings_dir = LEARNINGS_DIR
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
    
    def record_execution(self, task: str, skills_used: List[str], 
                        result: str, learnings: str = None):
        """记录执行结果"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "skills_used": skills_used,
            "result": result,
            "learnings": learnings
        }
        
        # 保存到学习记录文件
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.learnings_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        
        # 如果成功，追加到 skill 的学习记录
        if result == "success" and learnings:
            self._append_to_skill(skills_used, learnings)
        
        return str(filepath)
    
    def _append_to_skill(self, skills: List[str], learning: str):
        """追加学习记录到 skill 文件"""
        for skill_name in skills:
            skill_path = SKILLS_DIR / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text(encoding='utf-8')
                
                # 检查是否已有学习记录部分
                if "## 学习记录" not in content:
                    content += f"\n\n## 学习记录\n\n- [{datetime.now().strftime('%Y-%m-%d')}] {learning}\n"
                else:
                    # 追加到现有记录
                    content = content.replace(
                        "## 学习记录\n",
                        f"## 学习记录\n\n- [{datetime.now().strftime('%Y-%m-%d')}] {learning}\n"
                    )
                
                skill_path.write_text(content, encoding='utf-8')
    
    def get_learnings_summary(self, skill_name: str = None) -> List[Dict]:
        """获取学习记录摘要"""
        learnings = []
        
        for file in self.learnings_dir.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                record = json.load(f)
                if skill_name is None or skill_name in record.get("skills_used", []):
                    learnings.append(record)
        
        return learnings


class TeamEngine:
    """团队引擎 - 整合所有组件"""
    
    def __init__(self):
        self.intent_recognizer = IntentRecognizer()
        self.skill_loader = DynamicSkillLoader(self.intent_recognizer)
        self.feedback_loop = FeedbackLoop()
    
    def analyze_task(self, task_desc: str) -> Dict:
        """分析任务，返回详细意图"""
        intent = self.intent_recognizer.identify_intent(task_desc)
        
        # 为每个匹配的 skill 添加详细信息
        detailed_matches = []
        for skill_name, score in intent["matched_skills"]:
            metadata = self.intent_recognizer.skills_cache.get(skill_name)
            if metadata:
                detailed_matches.append({
                    "name": skill_name,
                    "score": score,
                    "description": metadata.get("description", ""),
                    "tags": metadata.get("tags", []),
                    "triggers": metadata.get("triggers", []),
                    "tool_chain": metadata.get("tool_chain", []),
                    "steps": metadata.get("steps", [])
                })
        
        return {
            "task": task_desc,
            "intent_analysis": detailed_matches,
            "primary_skill": intent["primary_skill"],
            "confidence": intent["confidence"]
        }
    
    def generate_team(self, task_desc: str, team_name: str = None) -> Dict:
        """生成团队配置"""
        if not team_name:
            team_name = "task-team"
        
        # 动态加载 skills
        plan_skills = self.skill_loader.load_skills_for_task(task_desc, "plan")
        implement_skills = self.skill_loader.load_skills_for_task(task_desc, "implement")
        verify_skills = self.skill_loader.load_skills_for_task(task_desc, "verify")
        debug_skills = self.skill_loader.load_skills_for_task(task_desc, "debug")
        
        # 获取意图分析
        intent = self.intent_recognizer.identify_intent(task_desc)
        
        members = []
        
        # 架构师
        members.append({
            "name": "architect",
            "role": "架构师",
            "phase": "plan",
            "kind": "subagent_type",
            "subagent_type": "oracle",
            "prompt": f"分析任务需求，设计系统架构：{task_desc}",
            "skills": plan_skills or ["gsd-discuss-phase", "gsd-spec-phase", "gsd-plan-phase"],
            "skill_purpose": "使用规划类 skills 进行需求分析和架构设计",
            "tool_chain": self._get_combined_tool_chain(plan_skills)
        })
        
        # 研究员
        members.append({
            "name": "researcher",
            "role": "研究员",
            "phase": "plan",
            "kind": "subagent_type",
            "subagent_type": "explore",
            "prompt": f"探索代码库，查找相关模式和实现：{task_desc}",
            "skills": plan_skills or ["gsd-map-codebase", "gsd-explore"],
            "skill_purpose": "使用探索类 skills 理解现有代码",
            "tool_chain": self._get_combined_tool_chain(plan_skills)
        })
        
        # 实现者
        impl_category = "visual-engineering" if any(k in task_desc.lower() for k in ["ui", "前端", "界面"]) else "unspecified-high"
        members.append({
            "name": "implementer",
            "role": "实现者",
            "phase": "implement",
            "kind": "category",
            "category": impl_category,
            "prompt": f"实现功能代码，遵循项目现有模式：{task_desc}",
            "skills": implement_skills or ["gsd-execute-phase", "gsd-fast"],
            "skill_purpose": "使用实现类 skills 执行编码和测试",
            "tool_chain": self._get_combined_tool_chain(implement_skills)
        })
        
        # 审查者
        members.append({
            "name": "reviewer",
            "role": "审查者",
            "phase": "verify",
            "kind": "subagent_type",
            "subagent_type": "oracle",
            "prompt": f"审查代码质量、安全性和最佳实践：{task_desc}",
            "skills": verify_skills or ["gsd-code-review", "gsd-validate-phase"],
            "skill_purpose": "使用验证类 skills 进行代码审查",
            "tool_chain": self._get_combined_tool_chain(verify_skills)
        })
        
        # 根据意图添加专家成员
        if debug_skills:
            members.append({
                "name": "debugger",
                "role": "调试专家",
                "phase": "debug",
                "kind": "subagent_type",
                "subagent_type": "oracle",
                "prompt": f"诊断和修复问题：{task_desc}",
                "skills": debug_skills,
                "skill_purpose": "使用调试类 skills 诊断问题",
                "tool_chain": self._get_combined_tool_chain(debug_skills)
            })
        
        config = {
            "name": team_name,
            "task": task_desc,
            "version": "3.0",
            "engine": "skill-aware",
            "created_at": None,
            "members": members,
            "workflow": {
                "phases": ["plan", "implement", "verify"],
                "parallel_execution": True,
                "max_concurrent": 4,
                "feedback_loop": True
            },
            "intent_analysis": {
                "primary_skill": intent["primary_skill"],
                "confidence": intent["confidence"],
                "matched_skills": [s[0] for s in intent["matched_skills"][:5]]
            }
        }
        
        return config
    
    def _get_combined_tool_chain(self, skills: List[str]) -> List[str]:
        """获取合并的工具链"""
        chain = []
        for skill in skills:
            chain.extend(self.skill_loader.get_skill_tool_chain(skill))
        return list(set(chain))
    
    def execute_with_learning(self, config: Dict, result: str, learnings: str = None):
        """执行后记录学习"""
        skills_used = []
        for member in config.get("members", []):
            skills_used.extend(member.get("skills", []))
        
        self.feedback_loop.record_execution(
            task=config["task"],
            skills_used=list(set(skills_used)),
            result=result,
            learnings=learnings
        )
    
    def print_analysis(self, analysis: Dict):
        """打印分析结果"""
        print("\n" + "=" * 70)
        print(f"  任务: {analysis['task']}")
        print(f"  主要意图: {analysis['primary_skill']}")
        print(f"  置信度: {analysis['confidence']:.1f}")
        print("=" * 70)
        
        print("\n  意图分析:")
        print("-" * 70)
        
        for i, skill in enumerate(analysis["intent_analysis"][:5], 1):
            print(f"  {i}. {skill['name']} (分数: {skill['score']:.1f})")
            print(f"     描述: {skill['description'][:50]}...")
            print(f"     标签: {', '.join(skill['tags'][:3])}")
            print(f"     工具链: {', '.join(skill['tool_chain'][:3])}")
            print()
        
        print("-" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="GSD Team Engine - Skill-Aware Task Execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python gsd-team-engine.py "实现用户认证系统"
  python gsd-team-engine.py --analyze "修复登录 bug"
  python gsd-team-engine.py --learn "任务描述" --result success --learnings "学到的经验"
        """
    )
    
    parser.add_argument("task", nargs="?", help="任务描述")
    parser.add_argument("--analyze", "-a", action="store_true", help="分析任务意图")
    parser.add_argument("--generate", "-g", action="store_true", help="生成团队配置")
    parser.add_argument("--learn", "-l", action="store_true", help="记录学习")
    parser.add_argument("--result", "-r", choices=["success", "failure"], help="执行结果")
    parser.add_argument("--learnings", help="学习内容")
    parser.add_argument("--name", "-n", help="团队名称")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--commands", "-c", action="store_true", help="生成 OpenCode 命令")
    
    args = parser.parse_args()
    
    if not args.task:
        parser.print_help()
        sys.exit(1)
    
    engine = TeamEngine()
    
    # 分析模式
    if args.analyze:
        analysis = engine.analyze_task(args.task)
        engine.print_analysis(analysis)
        return
    
    # 学习模式
    if args.learn:
        if not args.result:
            print("错误: --learn 模式需要 --result 参数")
            sys.exit(1)
        
        filepath = engine.feedback_loop.record_execution(
            task=args.task,
            skills_used=[],
            result=args.result,
            learnings=args.learnings
        )
        print(f"学习记录已保存: {filepath}")
        return
    
    # 生成团队配置
    config = engine.generate_team(args.task, args.name)
    
    # 打印摘要
    print_team_summary(config)
    
    # 保存配置
    output_path = save_config(config, args.output)
    print(f"\n配置已保存到: {output_path}")
    
    # 生成命令
    if args.commands:
        print("\n" + "=" * 70)
        print("  OpenCode 命令:")
        print("=" * 70)
        print(generate_opencode_commands(config))


def print_team_summary(config: Dict):
    """打印团队摘要"""
    print("\n" + "=" * 70)
    print(f"  团队: {config['name']}")
    print(f"  任务: {config['task'][:50]}...")
    print(f"  引擎: {config.get('engine', 'unknown')}")
    print(f"  主要意图: {config['intent_analysis']['primary_skill']}")
    print(f"  置信度: {config['intent_analysis']['confidence']:.1f}")
    print("=" * 70)
    
    print("\n  成员配置:")
    print("-" * 70)
    
    for i, member in enumerate(config["members"], 1):
        kind = member.get("subagent_type") or member.get("category")
        skills = ", ".join(member.get("skills", [])[:3])
        tool_chain = ", ".join(member.get("tool_chain", [])[:3])
        print(f"  {i}. {member['name']} ({member['role']})")
        print(f"     类型: {member['kind']} = {kind}")
        print(f"     阶段: {member['phase']}")
        print(f"     Skills: {skills}")
        print(f"     工具链: {tool_chain}")
        print(f"     用途: {member.get('skill_purpose', 'N/A')}")
        print()
    
    print("-" * 70)
    print(f"  总计: {len(config['members'])} 个成员")
    print(f"  匹配 Skills: {', '.join(config['intent_analysis']['matched_skills'][:5])}")
    print("=" * 70)


def save_config(config: Dict, output_path: str = None) -> str:
    """保存配置到文件"""
    if not output_path:
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        output_path = WORKSPACE / f"{config['name']}.json"
    
    config["created_at"] = datetime.now().isoformat()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return str(output_path)


def generate_opencode_commands(config: Dict) -> str:
    """生成 OpenCode 命令"""
    commands = []
    commands.append(f"# 团队: {config['name']}")
    commands.append(f"# 任务: {config['task']}")
    commands.append(f"# 引擎: {config.get('engine', 'unknown')}")
    commands.append(f"# 主要意图: {config['intent_analysis']['primary_skill']}")
    commands.append("")
    commands.append("# 按阶段执行（每个成员自动加载对应 Skills）")
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
            tool_chain = member.get("tool_chain", [])
            
            if member["kind"] == "subagent_type":
                commands.append(f'# {member["role"]} - {member.get("skill_purpose", "")}')
                if tool_chain:
                    commands.append(f'# 工具链: {", ".join(tool_chain[:3])}')
                commands.append(f'task(subagent_type="{member["subagent_type"]}", load_skills={skills_str}, run_in_background=true, prompt="""{member["prompt"]}""")')
            else:
                commands.append(f'# {member["role"]} - {member.get("skill_purpose", "")}')
                if tool_chain:
                    commands.append(f'# 工具链: {", ".join(tool_chain[:3])}')
                commands.append(f'task(category="{member["category"]}", load_skills={skills_str}, run_in_background=true, prompt="""{member["prompt"]}""")')
            commands.append("")
        commands.append("")
    
    return "\n".join(commands)


if __name__ == "__main__":
    main()

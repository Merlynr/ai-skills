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
_TRIAGE_MODULE = None


def _get_triage_module():
    global _TRIAGE_MODULE
    if _TRIAGE_MODULE is not None:
        return _TRIAGE_MODULE
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "gsd_team_triage", SCRIPT_DIR / "gsd-team-triage.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _TRIAGE_MODULE = module
    return module


SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from _common import (  # noqa: E402
    iter_skill_md_paths,
    resolve_skill_md,
    resolve_skills_dir,
)

SKILLS_DIR = resolve_skills_dir()


def resolve_opencode_config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "opencode"
    if sys.platform == "win32":
        return Path.home() / ".config" / "opencode"
    return Path.home() / ".config" / "opencode"


WORKSPACE = resolve_opencode_config_dir() / "team_workspace"
LEARNINGS_DIR = SCRIPT_DIR / "learnings"

# 仅触发词/标签匹配达到此分数才视为「强意图」；纯关键词映射为 1.0
MIN_INTENT_SCORE = 2.0
FALLBACK_SKILLS = ("gsd-do", "gsd-team", "gsd-progress")

# 占位/演示类表述，避免「测试」子串误命中 QA 类 skill
TASK_PLACEHOLDER_PATTERNS = (
    r"测试任务",
    r"试一下",
    r"试试",
    r"演示任务",
    r"示例任务",
)

# 过短/过泛 tag 不参与子串匹配，避免误命中
GENERIC_TAGS = frozenset({
    "gsd", "ui", "api", "doc", "stack", "tool", "test", "dev", "mcp",
    "fix", "new", "map", "pr", "ai", "uat", "mvp", "add",
    "utility", "review", "planning", "phase", "project", "workflow",
    "manage", "config", "settings", "execute", "context", "docs",
    "idea", "task", "milestone", "audit", "quality", "analysis",
    "explore", "capture", "plan", "code", "spec", "update", "help",
    "team", "research", "debug", "design", "security", "testing",
})

# 过泛 trigger 降权（仍可能命中，但分数低于更具体的 trigger）
GENERIC_TRIGGERS = frozenset({
    "配置", "设置", "管理", "帮助", "help", "team", "探索", "explore",
    "config", "settings", "phase", "review", "工作流", "config",
})

# 明确短语 → 本地 skill（达到 MIN_INTENT_SCORE）
STRONG_PHRASE_RULES = (
    (r"gsd\s*升级|升级\s*gsd|update\s*gsd|gsd-update|gsd\s*update", ("gsd-update",), 4.0),
    (r"merlynr|dev\s*stack|工作流栈|开发工作流", ("merlynr-dev-stack",), 4.0),
    (r"组建团队|生成\s*team|多人协作", ("gsd-team",), 4.0),
    (r"map\s*codebase|映射代码库|代码结构", ("gsd-map-codebase",), 3.5),
    (r"检查进度|项目进度|当前状态", ("gsd-progress",), 3.5),
    (r"ns\s*workflow|gsd\s*ns\s*workflow", ("gsd-ns-workflow",), 3.5),
    (r"重新应用补丁|reapply\s*patches?", ("gsd-reapply-patches",), 3.5),
    (r"单元测试|集成测试|测试用例|添加测试|写测试|跑测试|生成测试", ("gsd-add-tests",), 3.5),
    (r"代码审查|code\s*review|安全审计", ("gsd-code-review", "gsd-secure-phase"), 3.0),
    (r"性能问题|性能瓶颈|是否存在.*性能|合包|流量采集", ("gsd-debug", "gsd-map-codebase", "merlynr-dev-stack"), 3.5),
    (r"修复.*bug|排错|调试", ("gsd-debug", "gsd-forensics"), 3.0),
    (r"讨论阶段|需求讨论|discuss\s*phase", ("gsd-discuss-phase", "gsd-spec-phase"), 2.5),
    (r"规划阶段|创建计划|写计划|plan\s*phase", ("gsd-plan-phase",), 3.0),
    (r"执行阶段|实现功能|execute\s*phase", ("gsd-execute-phase",), 2.5),
    (r"工作流配置|配置工作流|gsd\s*配置|配置\s*gsd", ("gsd-config",), 3.0),
    (r"恢复补丁|重新应用补丁|reapply\s*patches?", ("gsd-reapply-patches",), 3.5),
    (r"写文档|更新文档|生成文档|文档维护", ("gsd-docs-update",), 3.0),
    (r"拆分\s*pr|拆成\s*pr|pr\s*分支", ("gsd-pr-branch",), 3.0),
    (r"导入文档|ingest\s*docs", ("gsd-ingest-docs",), 3.0),
    (r"发布|准备合并|创建\s*pr(?!\s*分支)", ("gsd-ship",), 2.5),
)


class SkillMetadata:
    """Skill 元数据解析器"""

    @staticmethod
    def _parse_yaml_string_list(yaml_content: str, key: str) -> List[str]:
        inline = re.search(rf"^{key}:\s*\[(.*?)\]\s*$", yaml_content, re.MULTILINE | re.DOTALL)
        if inline:
            return [
                item.strip().strip('"\'')
                for item in inline.group(1).split(",")
                if item.strip()
            ]

        block = re.search(rf"^{key}:\s*\n((?:[ \t]+-\s+.+\n?)+)", yaml_content, re.MULTILINE)
        if block:
            return [
                match.group(1).strip().strip('"\'')
                for match in re.finditer(r"-\s+(.+)", block.group(1))
            ]

        return []

    @staticmethod
    def _parse_yaml_description(yaml_content: str) -> str:
        block = re.search(
            r"^description:\s*(>|>-|\||\|-)\s*\n((?:[ \t]+.+\n?)*)",
            yaml_content,
            re.MULTILINE,
        )
        if block:
            lines = [
                re.sub(r"^[ \t]+", "", line)
                for line in block.group(2).splitlines()
                if line.strip()
            ]
            return " ".join(lines).strip()

        inline = re.search(
            r'^description:\s*["\']?(.+?)["\']?\s*$',
            yaml_content,
            re.MULTILINE,
        )
        if inline:
            value = inline.group(1).strip().strip('"\'')
            if value not in (">", ">-", "|", "|-"):
                return value
        return ""

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
            
            metadata["tags"] = SkillMetadata._parse_yaml_string_list(yaml_content, "tags")
            metadata["triggers"] = SkillMetadata._parse_yaml_string_list(yaml_content, "triggers")
            metadata["tool_chain"] = SkillMetadata._parse_yaml_string_list(yaml_content, "tool_chain")
            metadata["description"] = SkillMetadata._parse_yaml_description(yaml_content)
        
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
        if not SKILLS_DIR.is_dir():
            print(
                f"警告: Skills 目录不存在: {SKILLS_DIR}\n"
                f"  请确认 skillshare 已初始化，或设置 SKILLSHARE_SKILLS 环境变量。",
                file=sys.stderr,
            )
            return
        for skill_name, skill_md in iter_skill_md_paths(SKILLS_DIR):
            metadata = SkillMetadata.parse_skill(skill_md)
            if metadata:
                self.skills_cache[skill_name] = metadata
    
    def identify_intent(self, task_desc: str) -> Dict:
        """识别任务意图，返回匹配的 Skills"""
        task_lower = task_desc.lower()
        available = set(self.skills_cache.keys())
        scored_skills: Dict[str, float] = {}

        def merge_scores(src: Dict[str, float]) -> None:
            for skill, points in src.items():
                if skill in available:
                    scored_skills[skill] = scored_skills.get(skill, 0) + points

        merge_scores(self._skill_name_scores(task_lower, available))
        merge_scores(self._trigger_scores(task_lower, available))
        merge_scores(self._tag_scores(task_lower, available))
        merge_scores(self._phrase_match(task_lower, available))
        merge_scores(self._keyword_scores(task_lower, available))

        sorted_skills = sorted(
            scored_skills.items(),
            key=lambda x: (
                -x[1],
                -self._longest_trigger_len(x[0], task_lower),
                x[0],
            ),
        )
        top_score = sorted_skills[0][1] if sorted_skills else 0.0
        low_confidence = top_score < MIN_INTENT_SCORE
        fallback_skill = self._pick_fallback_skill() if low_confidence else None
        
        if low_confidence:
            primary_skill = fallback_skill
        else:
            primary_skill = sorted_skills[0][0]
        
        return {
            "task": task_desc,
            "matched_skills": sorted_skills[:10],
            "primary_skill": primary_skill,
            "confidence": top_score,
            "low_confidence": low_confidence,
            "fallback_skill": fallback_skill,
        }
    
    def _phrase_match(self, task: str, available: set) -> Dict[str, float]:
        if self._is_placeholder_task(task):
            return {}
        scores: Dict[str, float] = {}
        for pattern, skills, points in STRONG_PHRASE_RULES:
            if not re.search(pattern, task, re.IGNORECASE):
                continue
            for skill in skills:
                if skill in available:
                    scores[skill] = scores.get(skill, 0) + points
        return scores
    
    def _pick_fallback_skill(self) -> Optional[str]:
        for name in FALLBACK_SKILLS:
            if name in self.skills_cache:
                return name
        return next(iter(self.skills_cache), None)
    
    def _is_placeholder_task(self, task: str) -> bool:
        return any(re.search(p, task) for p in TASK_PLACEHOLDER_PATTERNS)
    
    def _matches_testing_intent(self, task: str) -> bool:
        """QA/测试类意图（排除「测试任务」等占位描述）"""
        if self._is_placeholder_task(task):
            return False
        testing_phrases = (
            "单元测试",
            "集成测试",
            "测试用例",
            "写测试",
            "添加测试",
            "跑测试",
            "e2e",
            "uat",
        )
        if any(p in task for p in testing_phrases):
            return True
        return bool(re.search(r"\btest\b", task))
    
    def _task_has_keyword(self, task: str, keyword: str) -> bool:
        if keyword == "测试":
            return self._matches_testing_intent(task)
        return keyword in task
    
    def _keyword_match(self, task: str) -> List[str]:
        """关键词匹配"""
        if self._is_placeholder_task(task):
            return []
        
        matches = []
        
        keyword_map = {
            "debug": ["调试", "bug", "错误", "修复", "fix", "debug", "问题"],
            "plan": ["计划", "规划", "设计", "架构", "plan", "design"],
            "implement": ["实现", "编写", "开发", "代码", "implement", "code"],
            "verify": [
                "验证",
                "审查",
                "review",
                "verify",
                "单元测试",
                "集成测试",
                "测试用例",
            ],
            "ui": ["前端", "界面", "ui", "css", "react", "vue", "组件"],
            "api": ["接口", "api", "后端", "server", "数据库"],
            "docs": ["文档", "doc", "readme", "说明"],
            "performance": ["性能", "优化", "performance", "optimize"],
            "security": ["安全", "漏洞", "security", "vulnerability"],
            "refactor": ["重构", "refactor", "重写", "清理"],
        }
        
        for category, keywords in keyword_map.items():
            if category == "verify" and self._matches_testing_intent(task):
                continue
            if any(self._task_has_keyword(task, k) for k in keywords):
                matches.append(category)
        
        return matches
    
    def _skill_name_variants(self, skill_name: str) -> List[str]:
        variants = {
            skill_name.lower(),
            skill_name.lower().replace("-", " "),
            skill_name.lower().replace("gsd-", "gsd "),
        }
        return [v for v in variants if len(v) >= 4]

    def _skill_name_scores(self, task: str, available: set) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for skill_name in available:
            for variant in self._skill_name_variants(skill_name):
                if variant in task:
                    scores[skill_name] = max(scores.get(skill_name, 0.0), 4.5)
                    break
        return scores

    def _trigger_in_task(self, trigger: str, task: str) -> bool:
        """Exact or flexible trigger match (word order / spacing variants)."""
        trigger_l = trigger.lower().strip()
        if not trigger_l:
            return False
        if trigger_l in task:
            return True

        parts = [p for p in re.split(r"\s+", trigger_l) if p]
        if len(parts) >= 2 and all(part in task for part in parts):
            return True

        if re.fullmatch(r"[\u4e00-\u9fff]+", trigger_l) and len(trigger_l) >= 4:
            for i in range(2, len(trigger_l)):
                left, right = trigger_l[:i], trigger_l[i:]
                if left in task and right in task:
                    return True

        return False

    def _trigger_match_len(self, trigger: str, task: str) -> int:
        trigger_l = trigger.lower().strip()
        if trigger_l in task:
            return len(trigger_l)
        if self._trigger_in_task(trigger_l, task):
            return len(trigger_l)
        return 0

    def _trigger_specificity_score(self, skill_name: str, trigger: str) -> float:
        trigger_l = trigger.lower().strip()
        if not trigger_l:
            return 0.0

        score = 3.0 + min(len(trigger_l) / 10.0, 2.0)
        if trigger_l in GENERIC_TRIGGERS:
            score -= 1.25

        skill_token = skill_name.replace("gsd-", "").replace("-", " ")
        trigger_token = trigger_l.replace("-", " ")
        if skill_token and skill_token in trigger_token:
            score += 1.5
        if trigger_l.replace(" ", "-") in skill_name:
            score += 1.0

        return score

    def _trigger_scores(self, task: str, available: set) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for skill_name, metadata in self.skills_cache.items():
            if skill_name not in available:
                continue
            best = 0.0
            for trigger in metadata.get("triggers", []):
                trigger_l = trigger.lower().strip()
                if not trigger_l or not self._trigger_in_task(trigger_l, task):
                    continue
                best = max(best, self._trigger_specificity_score(skill_name, trigger))
            if best > 0:
                scores[skill_name] = best
        return scores

    def _longest_trigger_len(self, skill_name: str, task: str) -> int:
        metadata = self.skills_cache.get(skill_name, {})
        longest = 0
        for trigger in metadata.get("triggers", []):
            match_len = self._trigger_match_len(trigger, task)
            if match_len:
                longest = max(longest, match_len)
        return longest

    def _tag_matches_task(self, tag: str, task: str) -> bool:
        tag_l = tag.lower().strip()
        if not tag_l:
            return False
        if tag_l in GENERIC_TAGS or len(tag_l) <= 3:
            return False
        return tag_l in task

    def _tag_specificity_score(self, skill_name: str, tag: str) -> float:
        tag_l = tag.lower().strip()
        score = 2.0 + min(len(tag_l) / 12.0, 1.5)
        skill_token = skill_name.replace("gsd-", "").replace("-", " ")
        tag_token = tag_l.replace("-", " ")
        if skill_token and skill_token in tag_token:
            score += 1.0
        if tag_l.replace(" ", "-") in skill_name or tag_l in skill_name:
            score += 0.75
        return score

    def _tag_scores(self, task: str, available: set) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for skill_name, metadata in self.skills_cache.items():
            if skill_name not in available:
                continue
            best = 0.0
            for tag in metadata.get("tags", []):
                if not self._tag_matches_task(tag, task):
                    continue
                best = max(best, self._tag_specificity_score(skill_name, tag))
            if best > 0:
                scores[skill_name] = best
        return scores

    def _keyword_scores(self, task: str, available: set) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        keyword_matches = self._keyword_match(task)
        keyword_to_skills = {
            "debug": ["gsd-debug", "gsd-forensics"],
            "plan": ["gsd-plan-phase", "gsd-discuss-phase", "gsd-spec-phase"],
            "implement": ["gsd-execute-phase", "gsd-fast", "gsd-quick"],
            "verify": ["gsd-code-review", "gsd-validate-phase", "gsd-verify-work"],
            "test": ["gsd-add-tests", "gsd-verify-work"],
            "ui": ["gsd-ui-phase", "gsd-ui-review", "gsd-sketch"],
            "api": ["gsd-ai-integration-phase"],
            "docs": ["gsd-docs-update", "gsd-ingest-docs"],
            "performance": ["gsd-debug", "gsd-validate-phase"],
            "security": ["gsd-secure-phase", "gsd-code-review"],
            "refactor": ["gsd-map-codebase", "gsd-execute-phase"],
            "team": ["gsd-team"],
            "upgrade": ["gsd-update", "gsd-reapply-patches"],
        }

        if self._matches_testing_intent(task):
            keyword_matches.append("test")

        for keyword in keyword_matches:
            for skill in keyword_to_skills.get(keyword, []):
                if skill in available:
                    scores[skill] = scores.get(skill, 0.0) + 1.0
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


class NmemIntegration:
    """nmem 集成 - 同步任务结果到 Nowledge Mem"""
    
    def __init__(self):
        self.enabled = self._check_nmem()
    
    def _check_nmem(self) -> bool:
        """检查 nmem 是否可用"""
        try:
            import subprocess
            result = subprocess.run(
                ["nmem", "--json", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                status = json.loads(result.stdout)
                return status.get("status") == "ok"
        except Exception:
            pass
        return False
    
    def create_task_thread(self, task: str, config: Dict, result: str, 
                          learnings: str = None) -> Optional[str]:
        """创建任务线程到 nmem"""
        if not self.enabled:
            return None
        
        try:
            import subprocess
            
            # 构建线程内容
            content = self._build_thread_content(task, config, result, learnings)
            
            # 创建线程
            title = f"Team Task: {task[:50]}"
            cmd = [
                "nmem", "t", "create",
                "-t", title,
                "-c", content,
                "-s", "gsd-team"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # 解析返回的 thread ID
                try:
                    output = json.loads(result.stdout)
                    return output.get("id")
                except json.JSONDecodeError:
                    return result.stdout.strip()
            
            return None
        except Exception as e:
            print(f"警告: nmem 线程创建失败: {e}")
            return None
    
    def save_memory(self, title: str, content: str, 
                   memory_type: str = "learning",
                   importance: float = 0.7,
                   labels: List[str] = None) -> Optional[str]:
        """保存记忆到 nmem"""
        if not self.enabled:
            return None
        
        try:
            import subprocess
            
            cmd = [
                "nmem", "m", "add",
                content,
                "-t", title,
                "--unit-type", memory_type,
                "-i", str(importance),
                "-s", "gsd-team"
            ]
            
            if labels:
                for label in labels:
                    cmd.extend(["-l", label])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                try:
                    output = json.loads(result.stdout)
                    return output.get("id")
                except json.JSONDecodeError:
                    return "saved"
            
            return None
        except Exception as e:
            print(f"警告: nmem 记忆保存失败: {e}")
            return None
    
    def distill_thread(self, thread_id: str) -> bool:
        """将线程提炼为记忆"""
        if not self.enabled or not thread_id:
            return False
        
        try:
            import subprocess
            
            cmd = ["nmem", "t", "distill", thread_id]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def _build_thread_content(self, task: str, config: Dict, 
                             result: str, learnings: str = None) -> str:
        """构建线程内容"""
        lines = [
            f"## 任务: {task}",
            f"",
            f"**结果**: {result}",
            f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            "## 团队配置",
            f"- 引擎: {config.get('engine', 'unknown')}",
            f"- 成员数: {len(config.get('members', []))}",
            f"- 主要意图: {config.get('intent_analysis', {}).get('primary_skill', 'N/A')}",
            f"",
            "## 使用的 Skills"
        ]
        
        for member in config.get("members", []):
            skills = ", ".join(member.get("skills", [])[:3])
            lines.append(f"- {member['role']}: {skills}")
        
        if learnings:
            lines.extend([
                "",
                "## 学习记录",
                learnings
            ])
        
        return "\n".join(lines)


class FeedbackLoop:
    """反馈循环系统"""
    
    def __init__(self):
        self.learnings_dir = LEARNINGS_DIR
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        self.nmem = NmemIntegration()
    
    def record_execution(self, task: str, skills_used: List[str], 
                        result: str, learnings: str = None,
                        config: Dict = None) -> Dict:
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
        
        # 同步到 nmem
        nmem_thread_id = None
        nmem_memory_id = None
        
        if self.nmem.enabled and config:
            # 创建线程
            nmem_thread_id = self.nmem.create_task_thread(
                task, config, result, learnings
            )
            
            # 如果成功且有学习内容，提炼为记忆
            if nmem_thread_id and result == "success" and learnings:
                self.nmem.distill_thread(nmem_thread_id)
            
            # 保存重要决策为记忆
            if learnings and result == "success":
                nmem_memory_id = self.nmem.save_memory(
                    title=f"Task: {task[:50]}",
                    content=learnings,
                    memory_type="learning",
                    importance=0.8,
                    labels=["team-task", "success"]
                )
        
        record["nmem_thread_id"] = nmem_thread_id
        record["nmem_memory_id"] = nmem_memory_id
        
        return record
    
    def _append_to_skill(self, skills: List[str], learning: str):
        """追加学习记录到 skill 文件"""
        for skill_name in skills:
            skill_path = resolve_skill_md(skill_name)
            if skill_path and skill_path.exists():
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


RESEARCHER_CYMBAL_PHASE1 = """Phase 1 探库（Merlynr / L 级，与 opencode_smart 一致）：
1. 若 Cymbal 索引未就绪：rtk cymbal index .
2. 已知符号优先：rtk cymbal investigate <symbol>；改前查引用：rtk cymbal refs <symbol>
3. 语义/调用链/影响面 → Cymbal；字面量、配置、Markdown、日志 → rg / 直接读文件
4. 项目边界与规范 → .planning/codebase/ 与 AGENTS.md
5. Cymbal 无结果时再扩大 Grep；勿为探库全库 @Codebase
"""


def build_researcher_prompt(task_desc: str) -> str:
    return (
        f"探索代码库，查找相关模式与实现：{task_desc}\n\n"
        f"{RESEARCHER_CYMBAL_PHASE1}"
    )


def format_brief_evidence(brief: Dict) -> str:
    evidence = brief.get("evidence") or {}
    lines = []
    modules = evidence.get("modules") or []
    if modules:
        lines.append("模块: " + ", ".join(modules[:8]))
    for item in (evidence.get("interfaces") or [])[:8]:
        line = item.get("line")
        loc = f"{item.get('file')}:{line}" if line else item.get("file")
        lines.append(f"- {item.get('kind')} {item.get('name')} @ {loc}")
    return "\n".join(lines) if lines else "(Brief 中暂无 Cymbal 证据)"


def build_researcher_prompt_from_brief(task_desc: str, brief: Dict) -> str:
    evidence = brief.get("evidence") or {}
    if evidence.get("modules") or evidence.get("interfaces"):
        return (
            f"基于 Phase 0 Cymbal Brief 做缺口验证（禁止全库重扫）：{task_desc}\n\n"
            f"已有证据:\n{format_brief_evidence(brief)}\n\n"
            "仅对 Brief 未覆盖的路径/符号执行精确 Cymbal 命令；"
            "发现缺口时补充到研判结论，不要重复罗列全库。\n\n"
            f"{RESEARCHER_CYMBAL_PHASE1}"
        )
    return build_researcher_prompt(task_desc)


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
        
        strong_matches = [
            m for m in detailed_matches if m["score"] >= MIN_INTENT_SCORE
        ]
        
        return {
            "task": task_desc,
            "intent_analysis": strong_matches or detailed_matches,
            "primary_skill": intent["primary_skill"],
            "confidence": intent["confidence"],
            "low_confidence": intent.get("low_confidence", False),
            "fallback_skill": intent.get("fallback_skill"),
        }
    
    def build_triage_brief(self, task_desc: str, repo_root: str = None) -> Dict:
        triage = _get_triage_module()
        builder = triage.TriageBuilder(self.analyze_task)
        return builder.build(task_desc, repo_root)

    def _skills_from_brief(self, brief: Dict, phase: str, default_skills: List[str]) -> List[str]:
        shortlist = [
            item["name"]
            for item in brief.get("skill_shortlist", [])
            if item.get("name")
        ]
        picked = [
            name
            for name in shortlist
            if self.skill_loader._skill_matches_phase(name, phase)
        ]
        return picked[:4] if picked else default_skills

    def _skip_roles_from_brief(self, brief: Optional[Dict]) -> set:
        if not brief:
            return set()
        hints = brief.get("dispatch_hints") or {}
        roles = hints.get("skip_roles") or brief.get("skip_roles") or []
        return {str(role).lower().strip() for role in roles if role}

    def _required_roles_from_brief(self, brief: Optional[Dict]) -> List[str]:
        if not brief:
            return []
        hints = brief.get("dispatch_hints") or {}
        roles = hints.get("required_roles") or brief.get("required_roles") or []
        return [str(role).lower().strip() for role in roles if role]

    def _manual_subagents_from_brief(self, brief: Optional[Dict]) -> List[Dict]:
        if not brief:
            return []
        hints = brief.get("dispatch_hints") or {}
        agents = hints.get("manual_subagents") or brief.get("manual_subagents") or []
        if not isinstance(agents, list):
            return []
        normalized = []
        for item in agents:
            if not isinstance(item, dict):
                continue
            name = (item.get("name") or "").strip()
            if not name:
                continue
            normalized.append(item)
        return normalized

    def _append_manual_subagents(self, members: List[Dict], manual_subagents: List[Dict], task_desc: str) -> None:
        for item in manual_subagents:
            name = (item.get("name") or "manual-agent").strip()
            role = item.get("role") or name
            phase = (item.get("phase") or "plan").strip().lower()
            if phase not in ("triage", "plan", "implement", "verify", "debug"):
                phase = "plan"
            prompt = item.get("prompt") or f"{role}：{task_desc}"
            skills = item.get("skills") or ["merlynr-dev"]
            if isinstance(skills, str):
                skills = [skills]
            members.append({
                "name": name,
                "role": role,
                "phase": phase,
                "kind": "subagent_type",
                "subagent_type": item.get("subagent_type") or "oracle",
                "prompt": prompt,
                "skills": skills,
                "skill_purpose": item.get("skill_purpose") or "merlynr-dev manual_subagent",
                "tool_chain": self._get_combined_tool_chain(skills),
                "manual": True,
            })

    def _role_skipped(self, role_name: str, skip_roles: set) -> bool:
        return role_name.lower() in skip_roles

    def _workflow_phases_from_members(self, members: List[Dict]) -> List[str]:
        phases = []
        for phase in ("triage", "plan", "implement", "verify", "debug"):
            if any(member.get("phase") == phase for member in members):
                phases.append(phase)
        return phases or ["plan", "implement", "verify"]

    def generate_team(
        self,
        task_desc: str,
        team_name: str = None,
        brief: Dict = None,
    ) -> Dict:
        """生成团队配置；传入 brief 时启用 Phase 0 Cymbal 研判驱动编组"""
        if not team_name:
            team_name = "task-team"

        default_plan = self.skill_loader.load_skills_for_task(task_desc, "plan")
        default_implement = self.skill_loader.load_skills_for_task(task_desc, "implement")
        default_verify = self.skill_loader.load_skills_for_task(task_desc, "verify")
        default_debug = self.skill_loader.load_skills_for_task(task_desc, "debug")

        if brief:
            plan_skills = self._skills_from_brief(
                brief, "plan", default_plan or ["gsd-discuss-phase", "gsd-spec-phase", "gsd-plan-phase"]
            )
            implement_skills = self._skills_from_brief(
                brief, "implement", default_implement or ["gsd-execute-phase", "gsd-fast"]
            )
            verify_skills = self._skills_from_brief(
                brief, "verify", default_verify or ["gsd-code-review", "gsd-validate-phase"]
            )
            debug_skills = self._skills_from_brief(brief, "debug", default_debug)
            hints = brief.get("dispatch_hints") or {}
        else:
            plan_skills = default_plan
            implement_skills = default_implement
            verify_skills = default_verify
            debug_skills = default_debug
            hints = {}

        skip_roles = self._skip_roles_from_brief(brief)
        intent = self.intent_recognizer.identify_intent(task_desc)
        members = []
        evidence_block = format_brief_evidence(brief) if brief else ""
        scope = hints.get("scope_summary") if brief else ""

        if brief:
            members.append({
                "name": "triage-lead",
                "role": "研判负责人",
                "phase": "triage",
                "kind": "subagent_type",
                "subagent_type": "oracle",
                "prompt": brief.get("triage_lead_prompt") or f"研判任务分工：{task_desc}",
                "skills": ["gsd-team", "merlynr-dev-stack"],
                "skill_purpose": "基于 Cymbal Brief + skill 短名单安排成员与 skills",
                "tool_chain": self._get_combined_tool_chain(["gsd-team", "merlynr-dev-stack"]),
            })

        architect_prompt = f"分析任务需求，设计系统架构：{task_desc}"
        if brief and evidence_block != "(Brief 中暂无 Cymbal 证据)":
            architect_prompt += (
                f"\n\nPhase 0 Cymbal 证据（已嗅探，勿全库重扫）：\n{evidence_block}\n"
                f"范围: {scope}"
            )

        if not self._role_skipped("architect", skip_roles):
            members.append({
                "name": "architect",
                "role": "架构师",
                "phase": "plan",
                "kind": "subagent_type",
                "subagent_type": "oracle",
                "prompt": architect_prompt,
                "skills": plan_skills or ["gsd-discuss-phase", "gsd-spec-phase", "gsd-plan-phase"],
                "skill_purpose": "使用规划类 skills 进行需求分析和架构设计",
                "tool_chain": self._get_combined_tool_chain(plan_skills),
            })

        if not self._role_skipped("researcher", skip_roles):
            researcher_skills = list(plan_skills or ["gsd-map-codebase", "gsd-explore"])
            if (
                "merlynr-dev-stack" not in researcher_skills
                and "merlynr-dev-stack" in self.intent_recognizer.skills_cache
            ):
                researcher_skills.append("merlynr-dev-stack")
            researcher_prompt = (
                build_researcher_prompt_from_brief(task_desc, brief)
                if brief
                else build_researcher_prompt(task_desc)
            )
            members.append({
                "name": "researcher",
                "role": "研究员",
                "phase": "plan",
                "kind": "subagent_type",
                "subagent_type": "explore",
                "prompt": researcher_prompt,
                "skills": researcher_skills,
                "skill_purpose": "Brief 缺口验证（Cymbal 精确补查，非全库罗列）"
                if brief
                else "Phase 1 证据：Cymbal 探库 + map-codebase",
                "tool_chain": self._get_combined_tool_chain(researcher_skills),
            })

        include_ui = hints.get("include_ui") or any(
            k in task_desc.lower() for k in ["ui", "前端", "界面"]
        )
        if not self._role_skipped("implementer", skip_roles):
            impl_category = "visual-engineering" if include_ui else "unspecified-high"
            implementer_prompt = f"实现功能代码，遵循项目现有模式：{task_desc}"
            if brief and scope:
                implementer_prompt += f"\n\n实现范围（Cymbal Brief）: {scope}"
            members.append({
                "name": "implementer",
                "role": "实现者",
                "phase": "implement",
                "kind": "category",
                "category": impl_category,
                "prompt": implementer_prompt,
                "skills": implement_skills or ["gsd-execute-phase", "gsd-fast"],
                "skill_purpose": "使用实现类 skills 执行编码和测试",
                "tool_chain": self._get_combined_tool_chain(implement_skills),
            })

        if not self._role_skipped("reviewer", skip_roles):
            members.append({
                "name": "reviewer",
                "role": "审查者",
                "phase": "verify",
                "kind": "subagent_type",
                "subagent_type": "oracle",
                "prompt": f"审查代码质量、安全性和最佳实践：{task_desc}",
                "skills": verify_skills or ["gsd-code-review", "gsd-validate-phase"],
                "skill_purpose": "使用验证类 skills 进行代码审查",
                "tool_chain": self._get_combined_tool_chain(verify_skills),
            })

        if include_ui and not self._role_skipped("ui-reviewer", skip_roles):
            ui_skills = ["gsd-ui-review", "gsd-ui-phase"]
            members.append({
                "name": "ui-reviewer",
                "role": "UI 审查",
                "phase": "verify",
                "kind": "subagent_type",
                "subagent_type": "oracle",
                "prompt": f"审查 UI/前端变更与 Brief 范围：{task_desc}\n范围: {scope or '见 Brief'}",
                "skills": ui_skills,
                "skill_purpose": "UI 专项审查",
                "tool_chain": self._get_combined_tool_chain(ui_skills),
            })

        add_debug = bool(debug_skills) and (
            hints.get("include_debug", False) if brief else True
        )
        if add_debug and debug_skills and not self._role_skipped("debugger", skip_roles):
            members.append({
                "name": "debugger",
                "role": "调试专家",
                "phase": "debug",
                "kind": "subagent_type",
                "subagent_type": "oracle",
                "prompt": f"诊断和修复问题：{task_desc}",
                "skills": debug_skills,
                "skill_purpose": "使用调试类 skills 诊断问题",
                "tool_chain": self._get_combined_tool_chain(debug_skills),
            })

        manual_subagents = self._manual_subagents_from_brief(brief)
        if manual_subagents:
            self._append_manual_subagents(members, manual_subagents, task_desc)

        required_roles = self._required_roles_from_brief(brief)
        present_roles = {m.get("name", "").lower() for m in members}
        missing_required = [r for r in required_roles if r not in present_roles and not self._role_skipped(r, skip_roles)]

        phases = self._workflow_phases_from_members(members) if brief else ["plan", "implement", "verify"]
        config = {
            "name": team_name,
            "task": task_desc,
            "version": "3.3" if brief else "3.0",
            "engine": "skill-aware+triage" if brief else "skill-aware",
            "created_at": None,
            "members": members,
            "workflow": {
                "phases": phases,
                "parallel_execution": True,
                "max_concurrent": 4,
                "feedback_loop": True,
                "skip_roles": sorted(skip_roles) if skip_roles else [],
                "required_roles": required_roles,
                "missing_required_roles": missing_required,
                "manual_subagents": [a.get("name") for a in manual_subagents],
            },
            "intent_analysis": {
                "primary_skill": intent["primary_skill"],
                "confidence": intent["confidence"],
                "matched_skills": [s[0] for s in intent["matched_skills"][:5]],
            },
        }
        if brief:
            config["team_brief"] = brief

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
        
        return self.feedback_loop.record_execution(
            task=config["task"],
            skills_used=list(set(skills_used)),
            result=result,
            learnings=learnings,
            config=config
        )
    
    def print_analysis(self, analysis: Dict):
        """打印分析结果"""
        print("\n" + "=" * 70)
        print(f"  任务: {analysis['task']}")
        if analysis.get("low_confidence"):
            print(
                f"  主要意图: {analysis['primary_skill']} "
                f"(通用回退，最高匹配分 {analysis['confidence']:.1f} < {MIN_INTENT_SCORE:.0f})"
            )
        else:
            print(f"  主要意图: {analysis['primary_skill']}")
            print(f"  置信度: {analysis['confidence']:.1f}")
        print("=" * 70)
        
        print("\n  意图分析:")
        print("-" * 70)
        
        matches = analysis["intent_analysis"][:5]
        if not matches:
            print("  (无强匹配 skill；请补充更具体的任务描述或 GSD 触发词)")
        else:
            for i, skill in enumerate(matches, 1):
                desc = skill["description"] or "(无描述)"
                snippet = desc[:50] + ("..." if len(desc) > 50 else "")
                print(f"  {i}. {skill['name']} (分数: {skill['score']:.1f})")
                print(f"     描述: {snippet}")
                tags = ", ".join(skill["tags"][:3])
                chain = ", ".join(skill["tool_chain"][:3])
                if tags:
                    print(f"     标签: {tags}")
                if chain:
                    print(f"     工具链: {chain}")
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
  python gsd-team-engine.py --triage --repo . "重构 team 引擎意图识别"
  python gsd-team-engine.py --triage "任务描述" --brief-out team-brief.json
  python gsd-team-engine.py --from-brief team-brief.json --commands
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
    parser.add_argument("--sync-nmem", action="store_true", help="同步到 nmem")
    parser.add_argument(
        "--triage",
        action="store_true",
        help="Phase 0: Cymbal 嗅探模块/接口，生成 Team Brief（非全量罗列）",
    )
    parser.add_argument(
        "--repo",
        help="Cymbal 嗅探目标仓库根目录（默认当前目录）",
    )
    parser.add_argument(
        "--from-brief",
        metavar="FILE",
        help="从 Team Brief JSON 生成团队配置",
    )
    parser.add_argument(
        "--brief-out",
        metavar="FILE",
        help="保存 Team Brief 到指定 JSON 文件",
    )
    
    args = parser.parse_args()

    if not args.task and not args.from_brief:
        parser.print_help()
        sys.exit(1)
    
    engine = TeamEngine()
    triage_mod = _get_triage_module()

    if args.from_brief:
        brief_path = Path(args.from_brief).expanduser()
        if not brief_path.is_file():
            print(f"错误: Brief 文件不存在: {brief_path}")
            sys.exit(1)
        with open(brief_path, "r", encoding="utf-8") as handle:
            brief = json.load(handle)
        task_desc = brief.get("task") or args.task
        if not task_desc:
            print("错误: Brief 中缺少 task 字段")
            sys.exit(1)
    else:
        brief = None
        task_desc = args.task

    if args.triage:
        brief = engine.build_triage_brief(task_desc, args.repo)
        triage_mod.print_triage_brief(brief)
        if args.brief_out:
            out_path = Path(args.brief_out).expanduser()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as handle:
                json.dump(brief, handle, indent=2, ensure_ascii=False)
            print(f"\nTeam Brief 已保存: {out_path}")
        elif not args.from_brief and not args.generate:
            default_brief = WORKSPACE / "team-brief.json"
            WORKSPACE.mkdir(parents=True, exist_ok=True)
            with open(default_brief, "w", encoding="utf-8") as handle:
                json.dump(brief, handle, indent=2, ensure_ascii=False)
            print(f"\nTeam Brief 已保存: {default_brief}")
        if not args.from_brief and not args.generate and not args.commands:
            if not args.brief_out:
                print("\n生成团队: python3 gsd-team-engine.py --from-brief team-brief.json --commands")
            return

    # 分析模式
    if args.analyze:
        analysis = engine.analyze_task(task_desc)
        engine.print_analysis(analysis)
        return
    
    # 学习模式
    if args.learn:
        if not args.result:
            print("错误: --learn 模式需要 --result 参数")
            sys.exit(1)
        
        # 生成配置（用于 nmem 同步）
        config = engine.generate_team(task_desc, args.name, brief=brief)
        
        result = engine.feedback_loop.record_execution(
            task=task_desc,
            skills_used=[],
            result=args.result,
            learnings=args.learnings,
            config=config
        )
        print(f"学习记录已保存: {result.get('timestamp')}")
        if result.get('nmem_thread_id'):
            print(f"nmem 线程 ID: {result['nmem_thread_id']}")
        if result.get('nmem_memory_id'):
            print(f"nmem 记忆 ID: {result['nmem_memory_id']}")
        return
    
    # nmem 同步模式
    if args.sync_nmem:
        nmem = NmemIntegration()
        if not nmem.enabled:
            print("错误: nmem 未启用或不可用")
            sys.exit(1)
        
        # 生成配置
        config = engine.generate_team(task_desc, args.name, brief=brief)
        
        # 同步到 nmem
        thread_id = nmem.create_task_thread(
            task_desc, config, "pending", "任务已创建，等待执行"
        )
        
        if thread_id:
            print(f"✓ 已同步到 nmem")
            print(f"  线程 ID: {thread_id}")
            print(f"  标题: Team Task: {args.task[:50]}")
        else:
            print("✗ 同步到 nmem 失败")
        return
    
    # 生成团队配置
    if not brief and args.triage is False and args.from_brief is None:
        brief = None
    config = engine.generate_team(task_desc, args.name, brief=brief)
    
    # 先展示意图分析，再展示团队摘要（与 --analyze 输出一致）
    analysis = engine.analyze_task(task_desc)
    engine.print_analysis(analysis)
    if brief:
        triage_mod.print_triage_brief(brief)
    print_team_summary(config, analysis=analysis)
    
    # 保存配置
    output_path = save_config(config, args.output)
    print(f"\n配置已保存到: {output_path}")
    
    # 生成命令
    if args.commands:
        print("\n" + "=" * 70)
        print("  OpenCode 命令:")
        print("=" * 70)
        print(generate_opencode_commands(config))


def print_team_summary(config: Dict, analysis: Dict = None):
    """打印团队摘要（analysis 由 analyze_task 传入时可避免重复解释意图）"""
    intent = config.get("intent_analysis", {})
    print("\n" + "=" * 70)
    print(f"  团队: {config['name']}")
    print(f"  任务: {config['task'][:50]}...")
    print(f"  引擎: {config.get('engine', 'unknown')}")
    if analysis and analysis.get("low_confidence"):
        print(
            f"  主要意图: {intent.get('primary_skill')} "
            f"(通用回退，见上方意图分析)"
        )
    else:
        print(f"  主要意图: {intent.get('primary_skill')}")
        print(f"  置信度: {intent.get('confidence', 0):.1f}")
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
    skip_roles = config.get("workflow", {}).get("skip_roles") or []
    if skip_roles:
        print(f"  跳过角色: {', '.join(skip_roles)}")
    missing = config.get("workflow", {}).get("missing_required_roles") or []
    if missing:
        print(f"  ⚠ 缺少 required_roles: {', '.join(missing)}")
    manual = config.get("workflow", {}).get("manual_subagents") or []
    if manual:
        print(f"  manual_subagents: {', '.join(manual)}")
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

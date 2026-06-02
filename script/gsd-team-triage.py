#!/usr/bin/env python3
"""Phase 0 triage: Cymbal evidence sniffing and Team Brief generation."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

MAX_MODULES = 8
MAX_INTERFACES = 12
MAX_PACKAGES = 5
MAX_SEARCH_TERMS = 8
MAX_SYMBOLS_PER_TERM = 6
MAX_CYMBAL_SEARCHES = 10
INTERFACE_KINDS = frozenset(
    {"function", "method", "class", "interface", "type", "struct", "enum"}
)

# 中文任务 → Cymbal 可检索的符号/路径别名（非全库，仅扩展检索词）
DOMAIN_PHRASE_ALIASES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (r"流量采集|flowcollect|flow collect", ("flowcollect", "FlowCollect", "flow", "collect")),
    (r"合包|合并.*包|pcap.*合并", ("merge", "FlowCollectDoTaskRun", "FlowcollectXdrrptInitMerge", "flowcollect_proc")),
    (r"性能|瓶颈|慢|卡顿|吞吐|延迟", ("performance", "perf", "optimize", "bottleneck")),
    (r"packet|报文|数据包", ("packet", "pcap", "Packet")),
    (r"离线|直送", ("offline", "FlowCollectDoTaskRunOffline", "flowcollect_proc2")),
    (r"上报|xdrrpt", ("xdrrpt", "Xdrrpt", "report")),
)

PERFORMANCE_SIGNALS = ("性能", "瓶颈", "慢", "卡顿", "吞吐", "延迟", "optimize", "performance", "perf")
INVESTIGATION_SIGNALS = ("是否存在", "有没有", "排查", "分析", "诊断", "investigate")
IMPLEMENT_SIGNALS = (
    "实现", "开发", "编写", "添加", "新增", "重构", "修改代码",
    "implement", "develop", "add feature", "code change",
)
DOCS_ONLY_SIGNALS = ("写文档", "更新文档", "文档维护", "docs update", "生成文档")

VALID_TEAM_ROLES = frozenset({
    "triage-lead", "architect", "researcher", "implementer",
    "reviewer", "debugger", "ui-reviewer",
})

NOISE_MODULE_PREFIXES = (
    "c_tmp/",
    "depends/",
    "emanager/aconf/",
    "scripts/tests/",
    "framework/modules/",
)

L_TASK_SIGNALS = (
    "组建团队",
    "重构",
    "新功能",
    "多模块",
    "refactor",
    "architecture",
    "migrate",
    "迁移",
    "系统",
    "完整",
)
S_TASK_SIGNALS = ("一行", "单文件", "typo", "拼写", "rename", "重命名")


def resolve_repo_root(explicit: Optional[str] = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    return Path.cwd().resolve()


def find_cymbal_command() -> Optional[List[str]]:
    if shutil.which("cymbal"):
        return ["cymbal"]
    if shutil.which("rtk"):
        return ["rtk", "cymbal"]
    return None


def run_cymbal(
    args: List[str],
    repo_root: Path,
    timeout: int = 45,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    prefix = find_cymbal_command()
    if not prefix:
        return None, "cymbal 不可用（请安装 cymbal 或 rtk cymbal）"

    cmd = prefix + args + ["--json"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, f"cymbal 超时: {' '.join(args)}"
    except OSError as exc:
        return None, f"cymbal 执行失败: {exc}"

    stdout = (proc.stdout or "").strip()
    if proc.returncode != 0:
        err = (proc.stderr or stdout or f"exit {proc.returncode}").strip()
        if "no results found" in err.lower():
            return {"results": []}, None
        return None, err.splitlines()[0][:200] if err else f"exit {proc.returncode}"

    if not stdout:
        return {}, None
    try:
        return json.loads(stdout), None
    except json.JSONDecodeError as exc:
        return None, f"cymbal JSON 解析失败: {exc}"


def extract_search_terms(task: str, max_terms: int = MAX_SEARCH_TERMS) -> List[str]:
    terms: List[str] = []
    seen = set()

    def add(term: str) -> None:
        term = term.strip()
        if not term or len(term) < 2:
            return
        key = term.lower()
        if key in seen:
            return
        seen.add(key)
        terms.append(term)

    for match in re.finditer(r"[A-Za-z_][A-Za-z0-9_]{2,}", task):
        add(match.group())

    for part in re.split(r"[\s,，、；;：:。.!！?？（）()\[\]【】]+", task):
        part = part.strip()
        if not part:
            continue
        if re.fullmatch(r"[\u4e00-\u9fff]{2,8}", part):
            add(part)
        elif re.search(r"[\u4e00-\u9fff]", part):
            for chunk in re.findall(r"[\u4e00-\u9fff]{2,6}", part):
                add(chunk)

    for pattern, aliases in DOMAIN_PHRASE_ALIASES:
        if re.search(pattern, task, re.IGNORECASE):
            for alias in aliases:
                add(alias)

    if not terms:
        add(task[:24])
    return terms[:max_terms]


def expand_search_terms(task: str, repo_root: Path) -> List[str]:
    """Prefer symbol-friendly terms; append AGENTS.md path hints."""
    terms = extract_search_terms(task)
    seen = {t.lower() for t in terms}
    extra: List[str] = []

    def add(term: str) -> None:
        key = term.lower()
        if key not in seen and len(term) >= 2:
            seen.add(key)
            extra.append(term)

    agents_terms, _agents_modules = scan_agents_md_hints(repo_root, task)
    for term in agents_terms:
        add(term)

    # English / symbol-like terms first (Cymbal indexes identifiers better than Chinese)
    english_first = [t for t in terms + extra if re.search(r"[A-Za-z_]", t)]
    chinese_rest = [t for t in terms + extra if t not in english_first]
    merged = english_first + chinese_rest
    return merged[:MAX_SEARCH_TERMS]


def scan_agents_md_hints(repo_root: Path, task: str) -> Tuple[List[str], List[str]]:
    """Scan AGENTS.md for domain keywords → Cymbal terms and module paths."""
    terms: List[str] = []
    modules: List[str] = []
    chinese_chunks = re.findall(r"[\u4e00-\u9fff]{2,8}", task)
    if not chinese_chunks:
        return terms, modules

    agents_files = [repo_root / "AGENTS.md"]
    agents_files.extend(sorted(repo_root.glob("modules/**/AGENTS.md"))[:12])

    for agents_path in agents_files:
        if not agents_path.is_file():
            continue
        try:
            content = agents_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not any(chunk in content for chunk in chinese_chunks):
            continue
        for match in re.finditer(r"`([a-zA-Z0-9_./-]+)`", content):
            path = match.group(1).strip("/")
            if "/" in path and len(path) > 3:
                modules.append(path.rstrip("/") + "/")
        rel = agents_path.relative_to(repo_root)
        parent = str(rel.parent).replace("\\", "/")
        if parent and parent != ".":
            modules.append(parent.rstrip("/") + "/")

    for pattern, aliases in DOMAIN_PHRASE_ALIASES:
        if re.search(pattern, task, re.IGNORECASE):
            terms.extend(aliases)

    if "流量" in task or "合包" in task or "flowcollect" in task.lower():
        terms.extend(["flowcollect", "FlowCollect", "merge", "pcap"])

    return list(dict.fromkeys(terms)), list(dict.fromkeys(modules))


def is_performance_task(task: str) -> bool:
    task_l = task.lower()
    return any(s in task or s in task_l for s in PERFORMANCE_SIGNALS)


def is_investigation_task(task: str) -> bool:
    return any(s in task for s in INVESTIGATION_SIGNALS)


def infer_task_grade(task: str) -> str:
    task_l = task.lower()
    if any(s in task for s in S_TASK_SIGNALS):
        return "S"
    if is_performance_task(task) and is_investigation_task(task):
        return "L"
    if is_performance_task(task) and any(k in task for k in ("合包", "流量", "模块", "系统")):
        return "L"
    if any(s.lower() in task_l or s in task for s in L_TASK_SIGNALS):
        return "L"
    if len(task) >= 36 or task.count("，") + task.count(",") >= 2:
        return "L"
    if is_investigation_task(task):
        return "M"
    if len(task) <= 24:
        return "M"
    return "M"


def module_relevance_score(module: str, task: str, terms: List[str]) -> float:
    score = 0.0
    module_l = module.lower()
    task_l = task.lower()
    for term in terms:
        if term.lower() in module_l:
            score += 3.0
    if any(module.startswith(prefix) for prefix in NOISE_MODULE_PREFIXES):
        score -= 2.5
    if module_l.startswith("modules/"):
        score += 1.5
    if "flowcollect" in module_l and ("流量" in task or "合包" in task or "flow" in task_l):
        score += 6.0
    return score


def rank_modules(modules: List[str], task: str, terms: List[str]) -> List[str]:
    ranked = sorted(
        dict.fromkeys(modules),
        key=lambda m: module_relevance_score(m, task, terms),
        reverse=True,
    )
    return [m for m in ranked if module_relevance_score(m, task, terms) > -1.0][:MAX_MODULES]


def split_requirements(task: str) -> List[str]:
    parts = re.split(r"[；;。.\n]+", task)
    cleaned = [p.strip() for p in parts if p.strip()]
    return cleaned or [task.strip()]


def module_from_rel_path(rel_path: str) -> str:
    path = Path(rel_path)
    parts = path.parts
    if not parts:
        return ""
    dir_parts = path.parent.parts if path.suffix else parts
    if len(dir_parts) >= 3 and dir_parts[0] == "modules":
        return str(Path(dir_parts[0]) / dir_parts[1] / dir_parts[2]) + "/"
    if path.suffix:
        parent = path.parent
        if str(parent) == ".":
            return f"{dir_parts[0]}/"
        if len(parent.parts) >= 2:
            return str(Path(parent.parts[0]) / parent.parts[1]) + "/"
        return str(parent) + "/"
    if len(parts) >= 2:
        return str(Path(parts[0]) / parts[1]) + "/"
    return f"{parts[0]}/"


class CymbalSniffer:
    """Use Cymbal to sniff task-related modules and interfaces (not full repo dump)."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.warnings: List[str] = []

    def sniff(self, task: str) -> Dict[str, Any]:
        self.warnings = []
        terms = expand_search_terms(task, self.repo_root)
        _, agents_modules = scan_agents_md_hints(self.repo_root, task)
        modules: List[str] = list(agents_modules)
        interfaces: List[Dict[str, Any]] = []
        packages: List[Dict[str, Any]] = []
        seen_modules = set(modules)
        seen_symbols = set()

        structure, err = run_cymbal(["structure"], self.repo_root)
        if err:
            self.warnings.append(f"structure: {err}")
        elif structure:
            results = structure.get("results") or structure
            if isinstance(results, dict):
                for pkg in (results.get("top_packages") or [])[:MAX_PACKAGES]:
                    packages.append(
                        {
                            "path": pkg.get("path", ""),
                            "symbols": pkg.get("symbols", 0),
                            "files": pkg.get("files", 0),
                        }
                    )
                if results.get("files", 0) == 0:
                    self.warnings.append(
                        "仓库尚未索引；请在项目根执行: rtk cymbal index ."
                    )

        search_count = 0
        for term in terms:
            if search_count >= MAX_CYMBAL_SEARCHES:
                break
            sym_payload, sym_err = run_cymbal(
                ["search", term, "-n", str(MAX_SYMBOLS_PER_TERM)],
                self.repo_root,
            )
            search_count += 1
            if sym_err and "no results" not in sym_err.lower():
                self.warnings.append(f"search({term}): {sym_err}")
            self._collect_symbol_hits(sym_payload, modules, interfaces, seen_modules, seen_symbols, task, terms)

            if search_count >= MAX_CYMBAL_SEARCHES:
                break
            text_payload, text_err = run_cymbal(
                ["search", term, "-t", "-n", "5"],
                self.repo_root,
            )
            search_count += 1
            if text_err and "no results" not in text_err.lower():
                self.warnings.append(f"search-text({term}): {text_err}")
            self._collect_text_hits(text_payload, modules, seen_modules)

        modules = rank_modules(modules, task, terms)

        if not interfaces and ("flowcollect" in task.lower() or "流量" in task or "合包" in task):
            for fallback in ("FlowCollect", "flowcollect", "merge"):
                if search_count >= MAX_CYMBAL_SEARCHES:
                    break
                sym_payload, _ = run_cymbal(["search", fallback, "-n", str(MAX_SYMBOLS_PER_TERM)], self.repo_root)
                search_count += 1
                self._collect_symbol_hits(
                    sym_payload, modules, interfaces, seen_modules, seen_symbols, task, terms
                )

        if not modules and packages:
            for pkg in packages[:3]:
                path = pkg.get("path", "")
                if path:
                    modules.append(path.rstrip("/") + "/")
            modules = rank_modules(modules, task, terms)

        interfaces = self._rank_interfaces(interfaces, task, terms)

        return {
            "repo_root": str(self.repo_root),
            "cymbal_available": find_cymbal_command() is not None,
            "search_terms": terms,
            "modules": modules[:MAX_MODULES],
            "interfaces": interfaces[:MAX_INTERFACES],
            "packages": packages[:MAX_PACKAGES],
            "warnings": list(self.warnings),
        }

    def _symbol_relevance(self, row: Dict[str, Any], task: str, terms: List[str]) -> float:
        name = (row.get("name") or "").lower()
        rel = (row.get("rel_path") or row.get("file") or "").lower()
        score = 0.0
        for term in terms:
            tl = term.lower()
            if tl in name or tl in rel:
                score += 2.0
        if "flowcollect" in rel or "flowcollect" in name:
            score += 4.0
        if any(rel.startswith(p) for p in NOISE_MODULE_PREFIXES):
            score -= 3.0
        if rel.startswith("depends/"):
            score -= 5.0
        if is_performance_task(task) and any(k in name for k in ("merge", "proc", "task", "run")):
            score += 2.0
        return score

    def _rank_interfaces(
        self,
        interfaces: List[Dict[str, Any]],
        task: str,
        terms: List[str],
    ) -> List[Dict[str, Any]]:
        ranked = sorted(
            interfaces,
            key=lambda item: self._symbol_relevance(item, task, terms),
            reverse=True,
        )
        return [
            item
            for item in ranked
            if self._symbol_relevance(item, task, terms) >= 1.0
            and not (item.get("file") or "").startswith("depends/")
        ]

    def _collect_symbol_hits(
        self,
        payload: Optional[Dict[str, Any]],
        modules: List[str],
        interfaces: List[Dict[str, Any]],
        seen_modules: set,
        seen_symbols: set,
        task: str,
        terms: List[str],
    ) -> None:
        if not payload:
            return
        rows = payload.get("results") or []
        if isinstance(rows, dict):
            rows = rows.get("results") or []
        for row in rows:
            if self._symbol_relevance(row, task, terms) < 0:
                continue
            rel_path = row.get("rel_path") or row.get("file") or ""
            if rel_path.startswith("/"):
                try:
                    rel_path = str(Path(rel_path).relative_to(self.repo_root))
                except ValueError:
                    rel_path = Path(rel_path).name

            module = module_from_rel_path(rel_path)
            if module and module not in seen_modules and len(modules) < MAX_MODULES * 2:
                seen_modules.add(module)
                modules.append(module)

            kind = (row.get("kind") or "symbol").lower()
            name = row.get("name") or Path(rel_path).stem
            symbol_key = (name, rel_path)
            if symbol_key in seen_symbols:
                continue
            if kind in INTERFACE_KINDS or row.get("signature"):
                seen_symbols.add(symbol_key)
                interfaces.append(
                    {
                        "name": name,
                        "kind": kind,
                        "file": rel_path,
                        "line": row.get("start_line") or row.get("line"),
                        "signature": (row.get("signature") or "")[:120],
                    }
                )

    def _collect_text_hits(
        self,
        payload: Optional[Dict[str, Any]],
        modules: List[str],
        seen_modules: set,
    ) -> None:
        if not payload:
            return
        rows = payload.get("results") or []
        for row in rows:
            rel_path = row.get("rel_path") or row.get("file") or ""
            module = module_from_rel_path(rel_path)
            if module and module not in seen_modules and len(modules) < MAX_MODULES:
                seen_modules.add(module)
                modules.append(module)


def build_skill_shortlist(
    analysis: Dict[str, Any],
    limit: int = 10,
) -> List[Dict[str, Any]]:
    shortlist: List[Dict[str, Any]] = []
    for item in analysis.get("intent_analysis") or []:
        shortlist.append(
            {
                "name": item.get("name"),
                "score": item.get("score"),
                "description": (item.get("description") or "")[:120],
                "tags": (item.get("tags") or [])[:4],
                "tool_chain": (item.get("tool_chain") or [])[:3],
            }
        )
        if len(shortlist) >= limit:
            break
    return shortlist


def task_implies_code_change(task: str) -> bool:
    task_l = task.lower()
    return any(s in task or s in task_l for s in IMPLEMENT_SIGNALS)


def infer_skip_roles(task: str, evidence: Dict[str, Any]) -> List[str]:
    """Rule-based default roles to omit from generated team config."""
    skip: List[str] = []
    task_l = task.lower()
    has_implement = task_implies_code_change(task)

    if is_performance_task(task) and not has_implement:
        skip.append("implementer")

    if is_investigation_task(task) and is_performance_task(task) and not has_implement:
        if "architect" not in skip and "设计" not in task and "架构" not in task:
            skip.append("architect")

    if any(s in task for s in DOCS_ONLY_SIGNALS) and not has_implement:
        skip.extend(["implementer", "debugger"])

    if any(s in task for s in ("代码审查", "code review", "peer review")) and not has_implement:
        skip.append("implementer")

    if not any(k in task_l for k in ("ui", "前端", "界面", "css", "react", "vue")):
        skip.append("ui-reviewer")

    return [role for role in dict.fromkeys(skip) if role in VALID_TEAM_ROLES]


def derive_persist_target(evidence: Dict[str, Any]) -> Optional[str]:
    modules = evidence.get("modules") or []
    if not modules:
        return None
    primary = modules[0].rstrip("/")
    if primary.endswith("AGENTS.md"):
        return primary
    return f"{primary}/AGENTS.md"


def derive_persist_sections(task: str, task_grade: str) -> List[str]:
    sections = ["Recent Changes"]
    if is_performance_task(task):
        sections.append("Performance Notes")
    if task_grade == "L":
        sections.extend(["Decisions", "Open Questions"])
    return list(dict.fromkeys(sections))


def build_dispatch_hints(task: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
    task_l = task.lower()
    modules = evidence.get("modules") or []
    module_text = " ".join(modules).lower()
    include_ui = any(k in task_l for k in ("ui", "前端", "界面", "css", "react", "vue")) or any(
        k in module_text for k in ("ui", "frontend", "component", "view")
    )
    include_debug = any(
        k in task_l for k in ("bug", "debug", "调试", "排错", "修复", "fix", "错误")
    ) or is_performance_task(task)
    include_performance = is_performance_task(task)
    scope = ", ".join(modules[:5]) if modules else "(待 Cymbal 补充证据)"
    skip_roles = infer_skip_roles(task, evidence)
    if include_ui and "ui-reviewer" in skip_roles:
        skip_roles = [r for r in skip_roles if r != "ui-reviewer"]
    if include_debug and "debugger" in skip_roles:
        skip_roles = [r for r in skip_roles if r != "debugger"]
    return {
        "include_ui": include_ui,
        "include_debug": include_debug,
        "include_performance": include_performance,
        "scope_summary": scope,
        "skip_roles": skip_roles,
    }


def enrich_skill_shortlist(task: str, shortlist: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add domain skills for performance / investigation tasks."""
    names = {item.get("name") for item in shortlist}
    extras: List[Dict[str, Any]] = []

    def add(name: str, score: float, description: str) -> None:
        if name not in names:
            extras.append({"name": name, "score": score, "description": description, "tags": [], "tool_chain": []})
            names.add(name)

    if is_performance_task(task):
        add("gsd-debug", 3.5, "Performance troubleshooting and root-cause analysis")
        add("gsd-validate-phase", 3.0, "Validation gaps and test coverage")
        add("merlynr-dev-stack", 3.0, "Evidence-first Cymbal investigation workflow")
        add("gsd-map-codebase", 2.8, "Codebase map for hotspot modules")

    if is_investigation_task(task):
        add("gsd-map-codebase", 2.5, "Map codebase before changing code")
        add("merlynr-dev-stack", 2.5, "Evidence-first routing")

    merged = sorted(shortlist + extras, key=lambda x: -(x.get("score") or 0))
    return merged[:10]


def build_triage_lead_prompt(brief: Dict[str, Any]) -> str:
    evidence = brief.get("evidence") or {}
    modules = evidence.get("modules") or []
    interfaces = evidence.get("interfaces") or []
    skills = brief.get("skill_shortlist") or []

    interface_lines = []
    for item in interfaces[:8]:
        line = item.get("line")
        suffix = f":{line}" if line else ""
        interface_lines.append(
            f"- {item.get('kind', 'symbol')} {item.get('name')} "
            f"({item.get('file')}{suffix})"
        )

    skill_lines = [
        f"- {s.get('name')} (score={s.get('score')}) — {(s.get('description') or '')[:80]}"
        for s in skills[:8]
    ]

    hints = brief.get("dispatch_hints") or {}
    skip_roles = hints.get("skip_roles") or []
    skip_line = ", ".join(skip_roles) if skip_roles else "(无，使用完整团队)"
    persist_target = brief.get("persist_target") or "(未推导)"
    persist_sections = ", ".join(brief.get("persist_sections") or [])

    return (
        "你是 Phase 0 研判负责人（triage-lead）。以下证据由 Cymbal 嗅探生成，"
        "不是全库罗列。请基于证据 + skill 短名单，输出最终团队分工与每人 skills。\n\n"
        f"任务: {brief.get('task')}\n"
        f"分级: {brief.get('task_grade')}\n"
        f"需求要点:\n"
        + "\n".join(f"- {r}" for r in brief.get("requirements") or [])
        + "\n\n"
        f"相关模块 ({len(modules)}):\n"
        + ("\n".join(f"- {m}" for m in modules) if modules else "- (无)")
        + "\n\n"
        f"相关接口/符号 ({len(interfaces)}):\n"
        + ("\n".join(interface_lines) if interface_lines else "- (无)")
        + "\n\n"
        f"Skill 短名单:\n"
        + ("\n".join(skill_lines) if skill_lines else "- (无)")
        + "\n\n"
        f"引擎建议 skip_roles: {skip_line}\n"
        f"（可在 Brief JSON 的 dispatch_hints.skip_roles 中覆写）\n\n"
        f"建议写回: {persist_target}\n"
        f"建议章节: {persist_sections}\n\n"
        "输出要求:\n"
        "1. 确认或修正 task_grade（S/M/L）\n"
        "2. 列出成员（architect / researcher / implementer / reviewer / 可选 debug、ui）\n"
        "3. 明确 skip_roles：纯排查/性能分析且无代码改动意图时，通常 skip implementer\n"
        "4. 每个成员: scope + load_skills（从短名单选，勿全库罗列 skill）\n"
        "5. 输出 Persist 块（target / grade / sections）供 Phase 4.5 写回模块 AGENTS\n"
        "6. 标注风险与待澄清项\n"
        "7. 禁止重新全库扫描；缺口用精确 Cymbal 命令补查\n"
    )


class TriageBuilder:
    """Build Team Brief: Cymbal evidence + intent skill shortlist."""

    def __init__(self, analyze_task: Callable[[str], Dict[str, Any]]):
        self.analyze_task = analyze_task

    def build(
        self,
        task_desc: str,
        repo_root: Optional[str] = None,
    ) -> Dict[str, Any]:
        root = resolve_repo_root(repo_root)
        analysis = self.analyze_task(task_desc)
        sniffer = CymbalSniffer(root)
        evidence = sniffer.sniff(task_desc)
        evidence["warnings"] = list(dict.fromkeys(evidence.get("warnings") or []))

        brief = {
            "version": "1.1",
            "task": task_desc,
            "task_grade": infer_task_grade(task_desc),
            "requirements": split_requirements(task_desc),
            "evidence": evidence,
            "intent": {
                "primary_skill": analysis.get("primary_skill"),
                "confidence": analysis.get("confidence"),
                "low_confidence": analysis.get("low_confidence", False),
            },
            "skill_shortlist": enrich_skill_shortlist(
                task_desc, build_skill_shortlist(analysis)
            ),
            "dispatch_hints": build_dispatch_hints(task_desc, evidence),
            "warnings": evidence.get("warnings") or [],
        }
        grade = brief["task_grade"]
        brief["persist_target"] = derive_persist_target(evidence)
        brief["persist_grade"] = grade if grade in ("M", "L") else "M"
        brief["persist_sections"] = derive_persist_sections(task_desc, grade)
        brief["triage_lead_prompt"] = build_triage_lead_prompt(brief)
        return brief


def print_triage_brief(brief: Dict[str, Any]) -> None:
    evidence = brief.get("evidence") or {}
    print("\n" + "=" * 70)
    print("  Phase 0 Team Brief（Cymbal 嗅探，非全量罗列）")
    print("=" * 70)
    print(f"  任务: {brief.get('task')}")
    print(f"  分级: {brief.get('task_grade')}")
    print(f"  仓库: {evidence.get('repo_root')}")
    print(f"  主要意图: {brief.get('intent', {}).get('primary_skill')}")
    print(f"  置信度: {brief.get('intent', {}).get('confidence', 0):.1f}")
    print("=" * 70)

    print("\n  需求要点:")
    for req in brief.get("requirements") or []:
        print(f"    - {req}")

    print(f"\n  Cymbal 检索词: {', '.join(evidence.get('search_terms') or [])}")
    print("\n  相关模块:")
    modules = evidence.get("modules") or []
    if modules:
        for module in modules:
            print(f"    - {module}")
    else:
        print("    - (未嗅探到；请补充任务关键词或先 cymbal index .)")

    print("\n  相关接口/符号:")
    interfaces = evidence.get("interfaces") or []
    if interfaces:
        for item in interfaces:
            line = item.get("line")
            loc = f"{item.get('file')}:{line}" if line else item.get("file")
            print(f"    - {item.get('kind')} {item.get('name')} @ {loc}")
    else:
        print("    - (无)")

    print("\n  Skill 短名单:")
    for skill in brief.get("skill_shortlist") or []:
        print(f"    - {skill.get('name')} ({skill.get('score')})")

    hints = brief.get("dispatch_hints") or {}
    print("\n  调度提示:")
    print(f"    - 范围: {hints.get('scope_summary')}")
    print(f"    - UI 专席: {'是' if hints.get('include_ui') else '否'}")
    print(f"    - Debug 专席: {'是' if hints.get('include_debug') else '否'}")
    if hints.get("include_performance"):
        print("    - 性能排查: 是")
    skip_roles = hints.get("skip_roles") or []
    if skip_roles:
        print(f"    - 跳过角色: {', '.join(skip_roles)}")

    if brief.get("persist_target"):
        print("\n  写回目标 (Phase 4.5):")
        print(f"    - target: {brief.get('persist_target')}")
        print(f"    - grade: {brief.get('persist_grade')}")
        sections = brief.get("persist_sections") or []
        if sections:
            print(f"    - sections: {', '.join(sections)}")

    warnings = brief.get("warnings") or []
    if warnings:
        print("\n  警告:")
        for warning in warnings:
            print(f"    ! {warning}")

    print("\n" + "-" * 70)
    print("  下一步: triage-lead 基于本 Brief 研判 → generate_team --from-brief")
    print("-" * 70)

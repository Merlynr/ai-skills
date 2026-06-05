#!/usr/bin/env python3
"""Shared path resolution for skillshare SSOT scripts."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Iterator, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent


def resolve_skillshare_root() -> Path:
    env_root = os.environ.get("SKILLSHARE_ROOT")
    if env_root:
        return Path(env_root).expanduser()

    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "skillshare"

    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "skillshare"
    return Path.home() / ".config" / "skillshare"


def _skills_dir_from_config(config_path: Path) -> Optional[Path]:
    if not config_path.is_file():
        return None
    content = config_path.read_text(encoding="utf-8")
    match = re.search(
        r"^sources:\s*\n(?:[ \t].*\n)*?[ \t]*skills:\s*(.+)\s*$",
        content,
        re.MULTILINE,
    )
    if not match:
        return None
    raw = match.group(1).strip().strip('"\'')
    return Path(raw.replace("/", os.sep)).expanduser()


def resolve_skills_dir() -> Path:
    """Skills SSOT root (config.yaml > SKILLSHARE_SKILLS > repo > default)."""
    env_skills = os.environ.get("SKILLSHARE_SKILLS")
    if env_skills:
        return Path(env_skills).expanduser()

    root = resolve_skillshare_root()
    from_config = _skills_dir_from_config(root / "config.yaml")
    if from_config and from_config.is_dir():
        return from_config

    repo_skills = SCRIPT_DIR.parent / "skills"
    if repo_skills.is_dir():
        return repo_skills

    return root / "skills"


def _has_gsd_skills(directory: Path) -> bool:
    return directory.is_dir() and any(directory.glob("gsd-*/SKILL.md"))


def resolve_gsd_base_dir() -> Path:
    """
    Directory holding upstream GSD skills (base layer).

    Prefers skills/base/ when it contains gsd-*/SKILL.md; falls back to a tracked
    repo directory under base/; otherwise legacy flat skills/ root.
    """
    skills = resolve_skills_dir()
    base = skills / "base"
    if _has_gsd_skills(base):
        return base

    if base.is_dir():
        for child in sorted(base.iterdir()):
            if child.is_dir() and child.name.startswith("_") and _has_gsd_skills(child):
                return child

    return skills


def resolve_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def resolve_runtime_dir() -> Path:
    """GSD L1 runtime (workflows, gsd-tools)."""
    return resolve_codex_home() / "get-shit-done"


def resolve_skill_md(skill_name: str) -> Optional[Path]:
    """Resolve SKILL.md for a skill name across user layer and base layer."""
    skills = resolve_skills_dir()
    candidates = [
        skills / skill_name / "SKILL.md",
        skills / "base" / skill_name / "SKILL.md",
    ]

    base = skills / "base"
    if base.is_dir():
        for child in base.iterdir():
            if child.is_dir() and child.name.startswith("_"):
                candidates.append(child / skill_name / "SKILL.md")

    for path in candidates:
        if path.is_file():
            return path
    return None


def iter_skill_md_paths(skills_root: Optional[Path] = None) -> Iterator[Tuple[str, Path]]:
    """
    Yield (cache_key, skill_md_path) for discoverable skills.

    cache_key prefers YAML `name:` when parseable; otherwise directory name.
    """
    root = skills_root or resolve_skills_dir()
    if not root.is_dir():
        return

    seen: set[str] = set()
    candidates: list[Path] = []

    for child in sorted(root.iterdir()):
        if child.is_dir() and not child.name.startswith((".", "_")):
            md = child / "SKILL.md"
            if md.is_file():
                candidates.append(md)

    base = root / "base"
    if base.is_dir():
        for child in sorted(base.iterdir()):
            if not child.is_dir():
                continue
            if child.name.startswith("_"):
                candidates.extend(sorted(child.glob("*/SKILL.md")))
            else:
                md = child / "SKILL.md"
                if md.is_file():
                    candidates.append(md)

    for skill_md in candidates:
        key = _skill_cache_key(skill_md)
        if key in seen:
            continue
        seen.add(key)
        yield key, skill_md


def _skill_cache_key(skill_md: Path) -> str:
    content = skill_md.read_text(encoding="utf-8")
    match = re.search(r"^name:\s*[\"']?([^\"'\n]+)[\"']?\s*$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return skill_md.parent.name


def count_gsd_skills(base_dir: Optional[Path] = None) -> int:
    base = base_dir or resolve_gsd_base_dir()
    return len(list(base.glob("gsd-*/SKILL.md")))


def read_l1_version() -> str:
    version_file = resolve_runtime_dir() / "VERSION"
    if version_file.is_file():
        return version_file.read_text(encoding="utf-8").strip()
    return "unknown"


if __name__ == "__main__":
    print(count_gsd_skills(resolve_gsd_base_dir()))

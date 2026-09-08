from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Skill:
    name: str
    description: str
    system_prompt_template: str
    allowed_tools: list[str] = field(default_factory=list)


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


# S7: 解析 Markdown skill：YAML frontmatter（name/description/allowed_tools，支持 > / | 块标量）+ 正文作为 system prompt。
def _parse_skill_file(path: Path) -> Skill:
    raise NotImplementedError


# 按三级优先级（项目本地 > 用户全局 > 内建）查找并解析 skill
class SkillLoader:
    _BUILTIN_DIR = Path(__file__).parent / "builtin"

    # S7: 按 _search_paths 顺序找第一个存在的文件并解析；找不到返回 None。
    def resolve(self, name: str) -> Skill | None:
        raise NotImplementedError

    # S7: 返回候选路径：.kama/skills、~/.kama/skills、内建；同时支持 name.md 与 name/SKILL.md。
    def _search_paths(self, name: str) -> list[Path]:
        raise NotImplementedError

    # S7: 列出所有可用 skill 名称（内建 + 用户 + 项目，后者覆盖同名）。
    def list_all(self) -> list[str]:
        raise NotImplementedError

    # S7: 列出全部 Skill 对象（含描述），项目本地覆盖同名内建。
    def list_all_skills(self) -> list[Skill]:
        raise NotImplementedError

    # S7: 把模板里的 $ARGUMENTS 替换成用户参数。
    def render_prompt(self, skill: Skill, arguments: str) -> str:
        raise NotImplementedError

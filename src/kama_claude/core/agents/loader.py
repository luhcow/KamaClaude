from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentProfile:
    name: str
    description: str
    system_prompt: str
    allowed_tools: list[str] = field(default_factory=list)
    model: str = ""


# 按两级优先级（项目本地 > 用户全局 > 内建）查找并解析角色配置
class AgentProfileLoader:
    _BUILTIN_DIR = Path(__file__).parent / "builtin"

    # S7: 按 _search_paths 找第一个存在的 TOML 并解析；找不到返回 None。
    def load(self, name: str) -> AgentProfile | None:
        raise NotImplementedError

    # S7: 返回 [项目本地, 用户全局, 内建] 路径，项目本地优先。
    def _search_paths(self, name: str) -> list[Path]:
        raise NotImplementedError

    # S7: 解析 TOML 的 [agent] 节为 AgentProfile。
    def _parse(self, path: Path, name: str) -> AgentProfile:
        raise NotImplementedError

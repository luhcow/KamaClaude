from __future__ import annotations

from kama_claude.core.tools.base import BaseTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    # S1: 按 tool.name 注册；同名覆盖。
    def register(self, tool: BaseTool) -> None:
        raise NotImplementedError

    # S1: 按名称查找工具，不存在返回 None。
    def get(self, name: str) -> BaseTool | None:
        raise NotImplementedError

    # S1: 返回 Anthropic 格式 schema 列表：name / description / input_schema。
    def tool_schemas(self) -> list[dict[str, object]]:
        raise NotImplementedError

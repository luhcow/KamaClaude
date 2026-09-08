from __future__ import annotations

from typing import Any

from kama_claude.core.mcp.client import (
    McpClient,
    McpServerUnavailableError,
    McpToolDef,
    McpToolError,
)
from kama_claude.core.tools.base import BaseTool, ToolResult


# 将 MCP 工具包装为 BaseTool，使 ToolRegistry 可透明调用
class McpTool(BaseTool):
    params_model = None  # input_schema 来自 MCP tool_def，不使用 pydantic model

    # 初始化 MCP 工具包装器，工具名以 server_name__ 为前缀防止命名冲突
    def __init__(self, client: McpClient, server_name: str, tool_def: McpToolDef) -> None:
        self._client = client
        self._server_name = server_name
        self._tool_def = tool_def
        self.name = f"{server_name}__{tool_def.name}"
        self.description = tool_def.description or f"MCP tool from {server_name}"
        self.input_schema: dict[str, Any] = (
            tool_def.input_schema or {"type": "object", "properties": {}}
        )

    # S7: 调 MCP call_tool；连接不可用 / 工具错误 / 其它异常都返回 is_error=True，不要往外抛。
    async def invoke(self, params: dict[str, object]) -> ToolResult:
        raise NotImplementedError

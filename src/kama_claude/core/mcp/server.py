from __future__ import annotations

import logging

from kama_claude.core.config import McpServerConfig
from kama_claude.core.mcp.client import McpClient
from kama_claude.core.mcp.tool import McpTool
from kama_claude.core.tools.registry import ToolRegistry

log = logging.getLogger(__name__)


# 管理所有 MCP server 连接的生命周期：启动、工具发现、注册、关闭
class McpServerManager:
    def __init__(self) -> None:
        self._clients: dict[str, McpClient] = {}
        self._tools: list[McpTool] = []

    # S7: 按配置连接每个 server、list_tools 后包装成 McpTool；单个失败记日志并跳过。
    async def start_all(self, servers: list[McpServerConfig]) -> None:
        raise NotImplementedError

    # S7: 把已发现的 MCP 工具 register 到给定 registry。
    def register_tools(self, registry: ToolRegistry) -> None:
        raise NotImplementedError

    # S7: 返回已发现工具的拷贝列表。
    def get_tools(self) -> list[McpTool]:
        raise NotImplementedError

    # S7: 关闭全部 client 并清空 _clients。
    async def stop_all(self) -> None:
        raise NotImplementedError

    # S7: 按 transport=stdio|tcp 建立 McpClient 连接。
    async def _connect(self, cfg: McpServerConfig) -> McpClient:
        raise NotImplementedError

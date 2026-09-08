from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger(__name__)


class McpServerUnavailableError(Exception):
    pass


class McpToolError(Exception):
    """MCP server 返回的应用层错误（连接正常，但工具调用失败）"""
    pass


@dataclass
class McpToolDef:
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)


# 通过 stdio 或 TCP 与 MCP server 通信的 JSON-RPC 2.0 客户端
class McpClient:
    def __init__(self) -> None:
        self._id = 0
        self._proc: asyncio.subprocess.Process | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._transport = ""
        self._lock = asyncio.Lock()
        self._stderr_task: asyncio.Task[None] | None = None

    _STREAM_LIMIT = 64 * 1024 * 1024  # 64 MB，防止大响应触发 LimitOverrunError

    # S7: 拉起 stdio 子进程，保存 stdout/stdin，drain stderr，然后 _initialize。
    async def connect_stdio(
        self,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
    ) -> None:
        raise NotImplementedError

    # S7: TCP 连接 MCP server 并 _initialize。
    async def connect_tcp(self, host: str, port: int) -> None:
        raise NotImplementedError

    # S7: 发送 initialize + notifications/initialized 完成握手。
    async def _initialize(self) -> None:
        raise NotImplementedError

    # S7: 调 tools/list，解析为 McpToolDef 列表。
    async def list_tools(self) -> list[McpToolDef]:
        raise NotImplementedError

    # S7: 调 tools/call，拼接 type=text 的 content；连接问题抛 McpServerUnavailableError，应用错误抛 McpToolError。
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        raise NotImplementedError

    # S7: 持续读 stderr 防止管道堵死。
    async def _drain_stderr(self) -> None:
        raise NotImplementedError

    # S7: 取消 stderr 任务，终止 stdio 子进程或关闭 TCP writer。
    async def close(self) -> None:
        raise NotImplementedError

    # S7: 写 JSON-RPC 请求并读到匹配 id 的响应；忽略 notification。
    async def _call(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    # S7: 发送无 id 的 JSON-RPC 通知。
    async def _notify(self, method: str, params: dict[str, Any]) -> None:
        raise NotImplementedError

    # S7: 按 transport 写一行 JSON。
    async def _write_line(self, line: str) -> None:
        raise NotImplementedError

    # S7: 读一行非空 JSON；EOF 视为连接断开。
    async def _read_line(self) -> str:
        raise NotImplementedError

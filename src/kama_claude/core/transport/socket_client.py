from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from kama_claude.core.bus.envelope import JsonRpcRequest

type EventHandler = Callable[[dict[str, Any]], Awaitable[None]]

_MAX_LINE_BYTES = 64 * 1024 * 1024  # 64 MB per frame，兼容 MCP 大文件工具结果


class IpcError(RuntimeError):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code


class SocketClient:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._pending: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._event_handlers: list[EventHandler] = []

    # S0: 建立到 core 的 TCP 连接，limit 用 _MAX_LINE_BYTES。
    async def connect(self) -> None:
        raise NotImplementedError

    # S0: 关闭写流并等待 socket 释放（建议加超时）。
    async def close(self) -> None:
        raise NotImplementedError

    # S2: 注册服务器推送事件回调，可多次调用追加多个 handler。
    def on_event(self, handler: EventHandler) -> None:
        raise NotImplementedError

    # S0: 发送 JSON-RPC 命令并等待对应 id 的响应；未 connect 则 RuntimeError；错误响应抛 IpcError。
    async def send_command(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    # S2: 持续 readline，把行交给 _dispatch；退出时 cancel 所有 pending future。
    async def run_event_loop(self) -> None:
        raise NotImplementedError

    # S2: 解析单行：jsonrpc 响应完成 pending；kind==event 则依次 await event handler。
    async def _dispatch(self, line: bytes) -> None:
        raise NotImplementedError

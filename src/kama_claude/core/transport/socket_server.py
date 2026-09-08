from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ValidationError

from kama_claude.core.bus.envelope import (
    INTERNAL_ERROR,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    HandlerError,
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcSuccess,
    make_error,
)
from kama_claude.core.trace.record import TraceRecord
from kama_claude.core.trace.writer import TraceWriter
from kama_claude.core.transport.ipc_broadcaster import IpcEventBroadcaster

logger = logging.getLogger(__name__)

type CommandHandler = Callable[[dict[str, Any]], Awaitable[Any]]

# 每个连接处理协程中，当前正在处理的 writer（供 handler 读取连接上下文）
_writer_var: ContextVar[asyncio.StreamWriter] = ContextVar("_writer_var")


def _now() -> str:
    return datetime.now(UTC).isoformat()


# 返回当前 handler 调用所属连接的 StreamWriter
def get_connection_writer() -> asyncio.StreamWriter:
    return _writer_var.get()

_MAX_LINE_BYTES = 64 * 1024 * 1024  # 64 MB per frame，兼容 MCP 大文件工具结果


class SocketServer:
    def __init__(
        self,
        host: str,
        port: int,
        broadcaster: IpcEventBroadcaster | None = None,
        trace: TraceWriter | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._handlers: dict[str, CommandHandler] = {}
        self._server: asyncio.AbstractServer | None = None
        self._broadcaster = broadcaster
        self._trace = trace
        self._active_writers: set[asyncio.StreamWriter] = set()

    # 注册一个方法名对应的命令处理函数
    def register(self, method: str, handler: CommandHandler) -> None:
        self._handlers[method] = handler

    # S0: 先探测 host:port，已被占用则 SystemExit；否则 asyncio.start_server 监听 NDJSON。
    # S2: 连接断开时走 _handle_connection 的 finally，调用 broadcaster.unsubscribe(writer)。
    async def start(self) -> str:
        raise NotImplementedError

    # S0: 关闭所有活跃连接，再 close 服务器并 wait_closed（建议加超时）。
    async def stop(self) -> None:
        raise NotImplementedError

    # S0: 把 writer 记入 _active_writers，进入读循环；结束时清理并关闭写流。
    # S2: finally 里若有 broadcaster，必须 unsubscribe(writer)。
    async def _handle_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        raise NotImplementedError

    # S0: 按行 readline；超限返回 invalid request。
    # S5: 每条命令 create_task(_handle_line)，避免长 handler 阻塞 permission.respond。
    async def _read_loop(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        raise NotImplementedError

    # S0: 解析 JSON-RPC 行：parse error / invalid request / method not found / handler 成功或错误码。
    # S3: 若配置了 trace，在分发前后写入 ipc 层 TraceRecord。
    async def _handle_line(self, line: bytes, writer: asyncio.StreamWriter) -> None:
        raise NotImplementedError

    # S0: 将 pydantic 消息序列化为 JSON 行写入流并 drain。
    async def _send(self, writer: asyncio.StreamWriter, msg: BaseModel) -> None:
        raise NotImplementedError

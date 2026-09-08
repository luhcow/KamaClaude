from __future__ import annotations

import asyncio
import datetime
import fnmatch
import json
import logging
import signal
import time
from datetime import UTC
from pathlib import Path
from typing import Any

from pydantic import BaseModel

import kama_claude
from kama_claude.core.bus.commands import (
    AgentRunCommand,
    AgentRunResult,
    EventSubscribeCommand,
    EventSubscribeResult,
    PermissionRespondCommand,
    PermissionRespondResult,
    PongResult,
    SessionCloseCommand,
    SessionCloseResult,
    SessionCompactCommand,
    SessionCompactResult,
    SessionCreateCommand,
    SessionCreateResult,
    SessionGetHistoryCommand,
    SessionGetHistoryResult,
    SessionSendMessageCommand,
    SessionSendMessageResult,
)
from kama_claude.core.bus.envelope import EventPushEnvelope
from kama_claude.core.config import KamaConfig, get_config
from kama_claude.core.events.bus import EventBus
from kama_claude.core.llm.provider import AnthropicProvider
from kama_claude.core.logging_setup import setup_logging
from kama_claude.core.mcp.server import McpServerManager
from kama_claude.core.permissions.manager import PermissionManager
from kama_claude.core.permissions.storage import load_policy_file
from kama_claude.core.runner import AgentRunner
from kama_claude.core.runs import events_file, new_run_id
from kama_claude.core.session import SessionManager, SessionStore
from kama_claude.core.trace.record import TraceRecord
from kama_claude.core.trace.writer import TraceWriter
from kama_claude.core.transport.ipc_broadcaster import IpcEventBroadcaster
from kama_claude.core.transport.socket_server import SocketServer, get_connection_writer

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.datetime.now(UTC).isoformat()


class CoreApp:
    def __init__(self) -> None:
        self._start_time = time.monotonic()
        self._bus = EventBus()
        self._broadcaster: IpcEventBroadcaster | None = None
        self._trace: TraceWriter | None = None
        self._config: KamaConfig | None = None
        self._running_runs: set[asyncio.Task[Any]] = set()
        self._sessions: SessionManager | None = None
        self._permission_manager: PermissionManager | None = None
        self._mcp_manager: McpServerManager | None = None

    # S0: 处理 core.ping，返回 server_version / uptime_ms / received_at。
    async def _ping_handler(self, params: dict[str, Any]) -> PongResult:
        raise NotImplementedError

    # S1: 作为 EventBus 订阅者，把内部事件写成 TraceRecord。
    async def _trace_event_handler(self, event: BaseModel) -> None:
        raise NotImplementedError

    # S1: 创建 one_shot session，异步 send_message，立即返回 run_id。
    async def _agent_run_handler(self, params: dict[str, Any]) -> AgentRunResult:
        raise NotImplementedError

    # S4: 创建 chat/one_shot session。
    async def _session_create_handler(self, params: dict[str, Any]) -> SessionCreateResult:
        raise NotImplementedError

    # S4: 向 session 发消息并等待该 run 完成。
    async def _session_send_handler(self, params: dict[str, Any]) -> SessionSendMessageResult:
        raise NotImplementedError

    # S4: 返回 session 的 messages 历史。
    async def _session_history_handler(self, params: dict[str, Any]) -> SessionGetHistoryResult:
        raise NotImplementedError

    # S5: 把客户端审批转给 PermissionManager.respond。
    async def _permission_respond_handler(self, params: dict[str, Any]) -> PermissionRespondResult:
        raise NotImplementedError

    # S6: 手动压缩 session thread。
    async def _session_compact_handler(self, params: dict[str, Any]) -> SessionCompactResult:
        raise NotImplementedError

    # S4: 关闭 session。
    async def _session_close_handler(self, params: dict[str, Any]) -> SessionCloseResult:
        raise NotImplementedError

    # S2: 可选回放 events.jsonl，再向 broadcaster 注册订阅。
    async def _subscribe_handler(self, params: dict[str, Any]) -> EventSubscribeResult:
        raise NotImplementedError

    # S2: 从 events.jsonl 按 topic glob 回放历史事件，返回条数。
    async def _replay_events(
        self,
        run_id: str,
        writer: asyncio.StreamWriter,
        topics: list[str],
    ) -> int:
        raise NotImplementedError

    # S0: 加载配置、setup_logging、启动 SocketServer、注册 core.ping、等待 SIGINT/SIGTERM、stop。
    # S1: 组装 EventBus / AgentRunner，注册 agent.run。
    # S2: 挂上 IpcEventBroadcaster，注册 event.subscribe。
    # S4: 组装 SessionManager，注册 session.*。
    # S5: 组装 PermissionManager，注册 permission.respond。
    # S6: 注册 session.compact。
    # S7: 启动 McpServerManager.start_all。
    async def run(self) -> None:
        raise NotImplementedError


# 同步入口：启动 CoreApp 事件循环
def run() -> None:
    asyncio.run(CoreApp().run())

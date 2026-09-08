from __future__ import annotations

import asyncio
import fnmatch
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import BaseModel

from kama_claude.core.bus.envelope import EventPushEnvelope
from kama_claude.core.trace.record import TraceRecord
from kama_claude.core.trace.writer import TraceWriter

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class _Subscription:
    sub_id: str
    writer: asyncio.StreamWriter
    topics: list[str]
    scope: str


class IpcEventBroadcaster:
    def __init__(self, trace: TraceWriter | None = None) -> None:
        self._subscriptions: list[_Subscription] = []
        self._trace = trace

    # S2: 注册客户端订阅，返回 subscription_id（建议 sub- + 短 uuid）。
    def subscribe(
        self,
        writer: asyncio.StreamWriter,
        topics: list[str],
        scope: str = "global",
    ) -> str:
        raise NotImplementedError

    # S2: 移除该 writer 的全部订阅。
    def unsubscribe(self, writer: asyncio.StreamWriter) -> None:
        raise NotImplementedError

    # S2: 按 topic glob 与 scope 过滤后，把 EventPushEnvelope 写成 NDJSON 推给订阅者；写失败则延迟 unsubscribe。
    async def handle(self, event: BaseModel) -> None:
        raise NotImplementedError

    # S2: 事件类型是否匹配 topics（fnmatch，支持 run.* 这类 glob）。
    @staticmethod
    def _matches_topic(event_type: str, topics: list[str]) -> bool:
        raise NotImplementedError

    # S2: scope==global 全通；scope 以 run: 开头则与 event run_id 精确匹配。
    @staticmethod
    def _matches_scope(run_id: str | None, scope: str) -> bool:
        raise NotImplementedError

from __future__ import annotations

import dataclasses
import time
from datetime import UTC, datetime
from typing import Any

from kama_claude.core.events.bus import EventBus
from kama_claude.core.llm.base import LLMProvider
from kama_claude.core.llm.types import LlmResponse
from kama_claude.core.trace.record import TraceRecord
from kama_claude.core.trace.writer import TraceWriter


def _now() -> str:
    return datetime.now(UTC).isoformat()


class TracingProvider:
    # 包裹真实 LLMProvider，在每次 chat() 调用前后向 TraceWriter 写入完整 API I/O 记录
    def __init__(
        self,
        inner: LLMProvider,
        trace: TraceWriter,
        *,
        include_payload: bool = True,
    ) -> None:
        self._inner = inner
        self._trace = trace
        self._include_payload = include_payload

    # S1: 调 inner.chat 前后各 emit 一条 llm 层 TraceRecord；include_payload=False 时只留摘要字段。
    async def chat(
        self,
        messages: list[dict[str, object]],
        tool_schemas: list[dict[str, object]],
        bus: EventBus,
        run_id: str,
        *,
        step: int = 0,
        system: str | None = None,
    ) -> LlmResponse:
        raise NotImplementedError

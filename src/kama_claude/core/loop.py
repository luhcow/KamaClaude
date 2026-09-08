from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from kama_claude.core.bus.events import StepFinishedEvent, StepStartedEvent
from kama_claude.core.context import ExecutionContext
from kama_claude.core.events.bus import EventBus
from kama_claude.core.llm.base import LLMProvider
from kama_claude.core.tools.invocation import invoke_tool
from kama_claude.core.tools.registry import ToolRegistry

if TYPE_CHECKING:
    from kama_claude.core.compact.compactor import Compactor
    from kama_claude.core.permissions.manager import PermissionManager


log = logging.getLogger(__name__)

def _now() -> str:
    return datetime.now(UTC).isoformat()


class AgentLoop:
    # 初始化循环所需依赖：LLM provider、工具注册表、事件总线，以及可选的权限管理器、压缩器和 session ID
    def __init__(
        self,
        provider: LLMProvider,
        registry: ToolRegistry,
        bus: EventBus,
        *,
        permission_manager: PermissionManager | None = None,
        compactor: Compactor | None = None,
        compact_threshold: float = 0.80,
        session_id: str = "",
    ) -> None:
        self._provider = provider
        self._registry = registry
        self._bus = bus
        self._permission_manager = permission_manager
        self._compactor = compactor
        self._compact_threshold = compact_threshold
        self._session_id = session_id

    # S1: 驱动 plan→act→observe：调 LLM、把 assistant blocks 写入 context、tool_use 时 invoke_tool、
    #     按 stop_reason 标记 success / exceeded_max_steps；LLM 异常标 llm_error；CancelledError 先 mark_failed("cancelled") 再上抛。
    #     工具失败不得终止循环，要把 is_error 结果回填给模型。
    # S2: 每步发布 StepStartedEvent / StepFinishedEvent。
    # S5: 把 permission_manager 与 session_id 传给 invoke_tool。
    # S6: 在 tool_use 且 run 未结束、usage.context_pct 达阈值时调用 compactor.compact。
    async def run(self, context: ExecutionContext) -> None:
        raise NotImplementedError

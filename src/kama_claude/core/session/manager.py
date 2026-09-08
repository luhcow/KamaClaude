from __future__ import annotations

import asyncio
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from kama_claude.core.bus.envelope import HandlerError
from kama_claude.core.bus.events import (
    SessionClosedEvent,
    SessionCreatedEvent,
    SessionMessageReceivedEvent,
    SessionResumedEvent,
    SessionWaitingForInputEvent,
    SkillInvokedEvent,
)
from kama_claude.core.events.bus import EventBus
from kama_claude.core.runs import new_run_id
from kama_claude.core.session.model import Session, SessionMode
from kama_claude.core.session.store import SessionStore
from kama_claude.core.skills.loader import SkillLoader

if TYPE_CHECKING:
    from kama_claude.core.llm.base import LLMProvider
    from kama_claude.core.runner import AgentRunner

SESSION_NOT_FOUND = -32010
SESSION_CLOSED = -32011
SESSION_BUSY = -32012


# 返回当前 UTC 时间的 ISO 8601 字符串
def _now() -> str:
    return datetime.now(UTC).isoformat()


class SessionManager:
    # 初始化会话管理器，接入文件存储、runner 工厂、事件总线和可选的 LLM provider（用于手动压缩）
    def __init__(
        self,
        store: SessionStore,
        runner_factory: Callable[[], AgentRunner],
        bus: EventBus,
        provider: LLMProvider | None = None,
    ) -> None:
        self._store = store
        self._runner_factory = runner_factory
        self._bus = bus
        self._provider = provider
        self._sessions: dict[str, Session] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._skill_loader = SkillLoader()

    # S4: 创建 session，写 meta，发布 SessionCreatedEvent。
    async def create(self, mode: SessionMode, title: str = "") -> Session:
        raise NotImplementedError

    # S4: 校验状态与 busy 锁，追加 user 消息，启动 runner.run_and_capture；
    #     one_shot 结束后 closed，chat 模式 waiting_for_input。
    # S7: 若 content 以 / 开头，解析 skill，展开 prompt / system_prompt_override / tool_whitelist。
    async def send_message(self, sid: str, content: str, *, run_id: str | None = None) -> str:
        raise NotImplementedError

    # S4: 关闭 session 并发布 SessionClosedEvent。
    async def close(self, sid: str) -> None:
        raise NotImplementedError

    # S6: 手动压缩 thread，write_compacted 成 summary 消息对，返回 SessionCompactResult。
    async def compact(self, sid: str, focus: str = "") -> Any:
        raise NotImplementedError

    # S4: 返回指定 session 的完整 thread。
    async def get_history(self, sid: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    # S4: 内存索引取 session，不存在抛 HandlerError(SESSION_NOT_FOUND)。
    def _get_session(self, sid: str) -> Session:
        raise NotImplementedError

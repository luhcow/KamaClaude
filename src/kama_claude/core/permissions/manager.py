from __future__ import annotations

import asyncio
import datetime
import logging
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC
from pathlib import Path
from typing import Any

from kama_claude.core.permissions.policy import (
    DEFAULT_POLICIES,
    PermissionDecision,
    ToolPolicy,
    matches_outside_cwd,
    param_preview,
)
from kama_claude.core.permissions.storage import load_policy_file, save_policy_file

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.datetime.now(UTC).isoformat()


@dataclass
class _PendingRequest:
    future: asyncio.Future[str]
    session_id: str
    tool_name: str


# 管理工具调用权限：策略评估、用户审批挂起、session 级和持久化 always 缓存、超时
class PermissionManager:
    def __init__(
        self,
        policies: dict[str, ToolPolicy] | None = None,
        *,
        policy_file: Path | None = None,
        timeout_s: float = 60.0,
    ) -> None:
        self._policies: dict[str, ToolPolicy] = policies or dict(DEFAULT_POLICIES)
        # tool_use_id → pending Future + metadata
        self._pending: dict[str, _PendingRequest] = {}
        # (session_id, tool_name) → "allow" | "deny"（session 内存，重启丢失）
        self._session_always: dict[tuple[str, str], str] = {}
        # tool_name → "allow" | "deny"（持久化，从 policy_file 加载）
        self._policy_file = policy_file
        self._persistent_always: dict[str, str] = (
            load_policy_file(policy_file) if policy_file is not None else {}
        )
        # 0 表示不超时
        self._timeout_s = timeout_s

    # S5: 对工具名 + 参数做静态 evaluate，不挂起。
    def evaluate(self, tool_name: str, params: dict[str, Any]) -> PermissionDecision:
        raise NotImplementedError

    # S5: 分层检查：deny_patterns → outside-cwd 强制 ASK → session 缓存 → persistent always
    #     → allow_patterns → default；需要 ASK 时发 event_emitter 并等待 Future（可超时）。
    #     返回 (allowed, decision_str)，decision 如 auto_allow / allow_once / timeout。
    async def check_and_wait(
        self,
        tool_use_id: str,
        tool_name: str,
        params: dict[str, Any],
        session_id: str,
        event_emitter: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> tuple[bool, str]:
        raise NotImplementedError

    # S5: 客户端审批到达时 resolve 对应 pending Future；未知 tool_use_id 忽略。
    def respond(self, tool_use_id: str, decision: str) -> None:
        raise NotImplementedError

    # S5: 把 always_allow / always_deny 写入 session 与 persistent 缓存（并 save_policy_file），返回是否放行。
    def _apply_response(self, decision: str, session_id: str, tool_name: str) -> bool:
        raise NotImplementedError

    # S5: 客户端断连时把该 session 所有 pending Future 以 deny_once 完成，避免永久挂起。
    def cancel_session(self, session_id: str, reason: str = "client_disconnected") -> None:
        raise NotImplementedError

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from kama_claude.core.bus.events import ContextCompactedEvent
from kama_claude.core.events.bus import EventBus

if TYPE_CHECKING:
    from kama_claude.core.context import ExecutionContext
    from kama_claude.core.llm.base import LLMProvider

logger = logging.getLogger(__name__)

_COMPACT_PROMPT = """\
You are compressing an agent conversation into a handoff summary.
Another LLM instance will continue this task from your summary alone — make it complete.

Structure your response with exactly these six sections:

## 1. Original Goal
One sentence describing what the user asked the agent to accomplish.

## 2. Completed Steps
Bullet list of what has been done. Be specific (file paths, commands run, decisions made).

## 3. Key Constraints & Discoveries
Facts learned during the run that affect future decisions \
(e.g., API limitations, file formats, user preferences stated mid-conversation).

## 4. Current File State
For each file that was created or modified: path, a one-line description of its current state.

## 5. Remaining TODOs
Ordered list of what still needs to be done to complete the original goal.

## 6. Critical Data
Any values the next LLM needs verbatim: IDs, tokens, exact error messages, config values \
discovered during the run.

Be concise. Omit reasoning steps and intermediate attempts. Keep conclusions.\
"""


# 返回当前 UTC 时间的简短时间戳字符串（用于文件名）
def _ts_compact() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


# 返回当前 UTC 时间的 ISO 8601 字符串
def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class CompactionResult:
    summary_text: str
    original_token_estimate: int
    summary_tokens: int


class Compactor:
    # 初始化压缩器，绑定事件总线、session 目录和 session ID
    def __init__(self, bus: EventBus, session_dir: Path, session_id: str) -> None:
        self._bus = bus
        self._session_dir = session_dir
        self._session_id = session_id

    # S6: 调用 compact_messages，成功则把 context.messages 换成 [user_summary, assistant_ack]，
    #     写 summary 文件并发布 ContextCompactedEvent。
    async def compact(
        self,
        context: ExecutionContext,
        provider: LLMProvider,
        focus: str = "",
    ) -> CompactionResult | None:
        raise NotImplementedError

    # S6: 把 messages 交给 LLM 生成摘要；失败或空摘要返回 None，不要抛给 loop。
    async def compact_messages(
        self,
        messages: list[dict[str, Any]],
        provider: LLMProvider,
        focus: str = "",
    ) -> CompactionResult | None:
        raise NotImplementedError

    # S6: 将摘要写入 session_dir/summary_<ts>.md，写失败只记日志。
    def _write_summary(self, text: str) -> None:
        raise NotImplementedError


# S6: 把 messages 编成可供压缩 prompt 阅读的纯文本（含 tool_use / tool_result 块）。
def _messages_to_text(messages: list[dict[str, Any]]) -> str:
    raise NotImplementedError

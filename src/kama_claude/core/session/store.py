from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from kama_claude.core.session.model import Session

logger = logging.getLogger(__name__)

MessageContent = str | list[dict[str, Any]]


# 返回当前 UTC 时间的 ISO 8601 字符串
def _now() -> str:
    return datetime.now(UTC).isoformat()


class SessionStore:
    # 初始化 session 文件存储根目录
    def __init__(self, root: Path) -> None:
        self._root = root.expanduser()
        self._root.mkdir(parents=True, exist_ok=True)

    # 返回指定 session 的目录路径
    def session_dir(self, sid: str) -> Path:
        return self._root / sid

    # 返回指定 session 下的 runs 目录路径
    def runs_dir(self, sid: str) -> Path:
        return self.session_dir(sid) / "runs"

    # S4: 把 session meta 写成 meta.json（ensure_ascii=False, indent=2）。
    def write_meta(self, session: Session) -> None:
        raise NotImplementedError

    # S4: 从 meta.json 读回 Session。
    def read_meta(self, sid: str) -> Session:
        raise NotImplementedError

    # S4: 追加一条 role/content 到 thread.jsonl，可选带 run_id。
    def append_message(
        self,
        sid: str,
        role: str,
        content: MessageContent,
        run_id: str | None = None,
    ) -> None:
        raise NotImplementedError

    # S4: 把一次 run 新产生的 messages 批量追加到 thread.jsonl。
    def append_messages(
        self,
        sid: str,
        messages: list[dict[str, Any]],
        run_id: str,
    ) -> None:
        raise NotImplementedError

    # S4: 读 thread.jsonl 为 Anthropic messages；跳过坏行与未知 role。
    # S6: 裁掉尾部未配对 tool_use，再 truncate_tool_results。
    def read_messages(self, sid: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    # S6: 从后往前找最后一个 tool_use/tool_result 已配对的位置，丢掉孤儿 tool_use。
    def _trim_orphan_tool_use(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        raise NotImplementedError

    # S6: 把压缩后的消息对覆盖写入 thread.jsonl，原文件备份为 thread_<ts>.jsonl.bak。
    def write_compacted(self, sid: str, messages: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    # S4: 读 notes.md，不存在返回空字符串。
    def read_notes(self, sid: str) -> str:
        raise NotImplementedError

    # S4: 将一条笔记追加到 notes.md。
    def append_note(self, sid: str, content: str, run_id: str) -> None:
        raise NotImplementedError

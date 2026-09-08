from __future__ import annotations

import asyncio
from pathlib import Path

from kama_claude.core.trace.record import TraceRecord


class TraceWriter:
    # 初始化 TraceWriter；写入目标文件路径在 start() 前不会创建
    def __init__(self, path: Path) -> None:
        self._path = path
        self._queue: asyncio.Queue[TraceRecord] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None

    # S1: 创建父目录并启动后台 _drain task。
    async def start(self) -> None:
        raise NotImplementedError

    # S1: join 队列后取消 drain task。
    async def stop(self) -> None:
        raise NotImplementedError

    # S1: 非阻塞把 record 放进队列。
    def emit(self, record: TraceRecord) -> None:
        raise NotImplementedError

    # S1: 循环从队列取 record，追加写成 JSONL 并 flush。
    async def _drain(self) -> None:
        raise NotImplementedError

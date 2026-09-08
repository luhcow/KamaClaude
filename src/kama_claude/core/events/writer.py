from __future__ import annotations

import logging
from pathlib import Path
from typing import IO

from pydantic import BaseModel

from kama_claude.core.events.bus import EventBus

logger = logging.getLogger(__name__)


class EventWriter:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._file: IO[str] | None = None

    # S1: 打开事件文件（追加模式），父目录不存在则创建。
    async def __aenter__(self) -> EventWriter:
        raise NotImplementedError

    # S1: 关闭事件文件。
    async def __aexit__(self, *args: object) -> None:
        raise NotImplementedError

    # S1: 将事件序列化为 JSON 行写入文件并 flush；写入失败记日志但不抛出。
    async def handle(self, event: BaseModel) -> None:
        raise NotImplementedError

    # S1: 把 handle 注册为 bus 的订阅者。
    def subscribe(self, bus: EventBus) -> None:
        raise NotImplementedError

from __future__ import annotations

from collections.abc import Awaitable, Callable

from pydantic import BaseModel

type EventHandler = Callable[[BaseModel], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: list[EventHandler] = []

    # S1: 注册一个异步事件处理函数，后注册的排在列表后面。
    def subscribe(self, handler: EventHandler) -> None:
        raise NotImplementedError

    # S1: 按注册顺序依次 await 所有订阅者；必须传原事件对象（不要先序列化再反序列化）。
    async def publish(self, event: BaseModel) -> None:
        raise NotImplementedError

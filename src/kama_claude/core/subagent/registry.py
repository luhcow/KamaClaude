from __future__ import annotations

import asyncio

from kama_claude.core.context import ExecutionContext


# 管理后台 subagent 任务的生命周期：注册、查询、批量取消
class BackgroundTaskRegistry:
    def __init__(self) -> None:
        self._tasks: dict[str, tuple[asyncio.Task[None], ExecutionContext]] = {}

    # S7: 注册后台任务及其 ExecutionContext。
    def register(
        self,
        run_id: str,
        task: asyncio.Task[None],
        context: ExecutionContext,
    ) -> None:
        raise NotImplementedError

    # S7: 查询 (task, context)；不存在返回 None。
    def get(self, run_id: str) -> tuple[asyncio.Task[None], ExecutionContext] | None:
        raise NotImplementedError

    # S7: 返回全部已注册任务，供 daemon 退出时清理。
    def all(self) -> list[tuple[asyncio.Task[None], ExecutionContext]]:
        raise NotImplementedError

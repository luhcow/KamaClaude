from __future__ import annotations

import json

from kama_claude.core.task.manager import TaskManager
from kama_claude.core.tools.base import BaseTool, ToolResult


class TaskGetTool(BaseTool):
    name = "task_get"
    description = "Get full details of a task by its integer ID. Returns the task as JSON."
    input_schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "ID of the task to retrieve.",
            },
        },
        "required": ["task_id"],
    }

    # 持有 TaskManager 实例，供 invoke 调用
    def __init__(self, task_manager: TaskManager) -> None:
        self._manager = task_manager

    # S6: 按 task_id 读取任务并返回 JSON；找不到变成 is_error。
    async def invoke(self, params: dict[str, object]) -> ToolResult:
        raise NotImplementedError

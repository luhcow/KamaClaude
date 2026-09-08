from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from kama_claude.core.task.model import Task, TaskStatus


def _now() -> str:
    return datetime.now(UTC).isoformat()


class TaskManager:
    # 初始化：确保目录存在，扫描现有文件确定下一个 ID
    def __init__(self, tasks_dir: Path) -> None:
        self._dir = tasks_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._next_id = self._max_id() + 1

    # S6: 扫描 task_*.json，返回最大 ID；没有文件返回 0。
    def _max_id(self) -> int:
        raise NotImplementedError

    # S6: 读取 task_{id}.json；不存在抛 ValueError。
    def _load(self, task_id: int) -> Task:
        raise NotImplementedError

    # S6: 把任务写成 task_{id}.json。
    def _save(self, task: Task) -> None:
        raise NotImplementedError

    # S6: 创建 pending 任务；blocked_by 引用的任务必须已存在。
    def create(
        self,
        subject: str,
        description: str = "",
        blocked_by: list[int] | None = None,
    ) -> Task:
        raise NotImplementedError

    # S6: 按 ID 读取任务。
    def get(self, task_id: int) -> Task:
        raise NotImplementedError

    # S6: 更新 status / blocked_by；status=completed 时调用 _clear_dependency。
    def update(
        self,
        task_id: int,
        *,
        status: TaskStatus | None = None,
        add_blocked_by: list[int] | None = None,
        remove_blocked_by: list[int] | None = None,
    ) -> Task:
        raise NotImplementedError

    # S6: 返回全部任务，按 ID 升序。
    def list_all(self) -> list[Task]:
        raise NotImplementedError

    # S6: 从所有其他任务的 blocked_by 里去掉 completed_id。
    def _clear_dependency(self, completed_id: int) -> None:
        raise NotImplementedError

    # S6: 格式化成 "[ ] #id: subject" 摘要；空列表返回 "No tasks."。
    def format_list(self) -> str:
        raise NotImplementedError

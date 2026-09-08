from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionContext:
    run_id: str
    goal: str
    max_steps: int
    prefill_messages: list[dict[str, Any]] = field(default_factory=list)
    session_notes: str = ""
    global_context: str = ""
    project_context: str = ""
    messages: list[dict[str, Any]] = field(default_factory=list)
    step: int = 0
    status: str = "running"  # "running" | "success" | "failed"
    reason: str | None = None
    result: str = ""
    # skill 或 subagent 角色可覆盖默认 system prompt
    system_prompt_override: str | None = None

    # S1: 有 prefill_messages 则拷贝为 messages；否则放入一条 user=goal 的消息。
    def __post_init__(self) -> None:
        raise NotImplementedError

    # S1: 以 base 为默认 system prompt。
    # S4: 非空时追加 Global / Project / Session Notes 分段，notes 段末尾提示用 note_save。
    # S7: system_prompt_override 非空时用它替换 base，记忆层仍然追加。
    def system_prompt(self, base: str) -> str:
        raise NotImplementedError

    # S1: 将 LLM content blocks 追加为 role=assistant 的消息。
    def add_assistant_message(self, content: list[Any]) -> None:
        raise NotImplementedError

    # S1: 把 tool_result block 追加为 user 消息；同一步多个结果要合并到同一条 user 消息。
    #     is_error=True 时 block 必须带 is_error。
    def add_tool_result(
        self, tool_use_id: str, content: str, is_error: bool = False
    ) -> None:
        raise NotImplementedError

    # S1: status 不再是 running 时返回 True。
    def is_done(self) -> bool:
        raise NotImplementedError

    # S1: 将 run 标记为成功。
    def mark_success(self) -> None:
        raise NotImplementedError

    # S1: 将 run 标记为失败并记录原因。
    def mark_failed(self, reason: str) -> None:
        raise NotImplementedError

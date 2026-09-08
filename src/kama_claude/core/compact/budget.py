from __future__ import annotations

from typing import Any

TOOL_RESULT_LIMIT = 8_000
TOOL_RESULT_KEEP = 4_000


# S6: 对 user 消息里超长 tool_result 做内存截断：len>limit 时只保留前 keep 字符并追加 omitted 说明。
#     返回新列表，不要原地改传入的 messages。
def truncate_tool_results(
    messages: list[dict[str, Any]],
    limit: int = TOOL_RESULT_LIMIT,
    keep: int = TOOL_RESULT_KEEP,
) -> list[dict[str, Any]]:
    raise NotImplementedError

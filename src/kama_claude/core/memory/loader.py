from __future__ import annotations

from pathlib import Path


# S3: 读取 context.md；路径不存在或内容为空时返回 ""（不要抛）。
def load_context_file(path: Path) -> str:
    raise NotImplementedError

from __future__ import annotations

from pathlib import Path

_DEFAULT_POLICY_PATH = Path("~/.kama/policy.toml")


# S5: 加载 policy.toml 的 [always] 节，返回 {tool_name: "allow"|"deny"}；文件不存在返回 {}。
def load_policy_file(path: Path | None = None) -> dict[str, str]:
    raise NotImplementedError


# S5: 把 always 字典覆盖写入 policy.toml 的 [always] 节；父目录不存在则创建。
def save_policy_file(always: dict[str, str], path: Path | None = None) -> None:
    raise NotImplementedError

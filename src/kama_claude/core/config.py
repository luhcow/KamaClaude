from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 7437
_DEFAULT_LOG_LEVEL = "INFO"
_DEFAULT_LOG_FILE = "~/.kama/logs/core.log"
_DEFAULT_LOG_FORMAT = "text"
_DEFAULT_CONFIG_PATH = "~/.kama/config.toml"
_DEFAULT_MAX_STEPS = 20
_DEFAULT_MODEL = "claude-sonnet-4-6"
_DEFAULT_TRACE_FILE = "~/.kama/traces/daemon.jsonl"


@dataclass
class LoggingConfig:
    level: str = _DEFAULT_LOG_LEVEL
    file: str = _DEFAULT_LOG_FILE
    format: str = _DEFAULT_LOG_FORMAT  # "text" | "json"


@dataclass
class AgentConfig:
    max_steps: int = _DEFAULT_MAX_STEPS


@dataclass
class LlmConfig:
    default_model: str = _DEFAULT_MODEL
    router: str = "static"  # "static" | "rule_based" (S4) | "cost_budget" (S6)


@dataclass
class TraceConfig:
    enabled: bool = True
    file: str = _DEFAULT_TRACE_FILE
    include_llm_payload: bool = True  # false 时 LLM 记录只保留摘要


@dataclass
class PermissionConfig:
    timeout_s: float = 60.0  # 审批超时秒数；0 表示不超时


@dataclass
class CompactionConfig:
    auto_threshold: float = 0.0    # context_pct 触发自动压缩的阈值（0 表示禁用，推荐用手动 /compact）
    tool_result_limit: int = 8_000  # tool_result 截断触发字符数
    tool_result_keep: int = 4_000   # 截断后保留的前缀字符数


@dataclass
class McpServerConfig:
    name: str
    transport: str = "stdio"       # "stdio" | "tcp"
    command: str = ""              # stdio 专用：可执行文件路径
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    host: str = "localhost"        # tcp 专用
    port: int = 3000               # tcp 专用


@dataclass
class McpConfig:
    servers: list[McpServerConfig] = field(default_factory=list)


@dataclass
class KamaConfig:
    host: str = _DEFAULT_HOST
    port: int = _DEFAULT_PORT
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    llm: LlmConfig = field(default_factory=LlmConfig)
    trace: TraceConfig = field(default_factory=TraceConfig)
    permission: PermissionConfig = field(default_factory=PermissionConfig)
    compaction: CompactionConfig = field(default_factory=CompactionConfig)
    mcp: McpConfig = field(default_factory=McpConfig)


# S0: 实现四级优先链：内建默认 → TOML（KAMA_CONFIG 显式路径，否则 ~/.kama/config.toml 再 .kama/config.toml）→ .env → KAMA_*。
#     .env 必须在读 KAMA_CONFIG 之前 load；缺文件静默跳过；未知 TOML 键交给 _apply_toml 硬退出。
# S1: 叠加 [agent]/[llm] 与 KAMA_MAX_STEPS、KAMA_LLM_DEFAULT_MODEL。
# S3: 叠加 [trace] 与 KAMA_TRACE_*。
# S5: 叠加 [permission] 与 KAMA_PERMISSION_TIMEOUT_S。
# S6: 叠加 [compaction] 与 KAMA_COMPACT_*。
# S7: 叠加 [mcp] servers 列表。不要改本函数签名。
def get_config() -> KamaConfig:
    raise NotImplementedError


# S0: 把已解析的 TOML 根表写入 config；未知小节/未知键/类型错误必须 SystemExit。
# 后续阶段：为 agent、llm、trace、permission、compaction、mcp 增加对应小节，保持未知键硬退出。
def _apply_toml(config: KamaConfig, data: dict[str, Any]) -> None:
    raise NotImplementedError


# S0: 用 KAMA_HOST / KAMA_PORT / KAMA_LOG_* 覆盖对应字段（已设置才覆盖）。
# 后续阶段：追加 KAMA_MAX_STEPS、KAMA_LLM_*、KAMA_TRACE_*、KAMA_PERMISSION_*、KAMA_COMPACT_*。
def _apply_env(config: KamaConfig) -> None:
    raise NotImplementedError

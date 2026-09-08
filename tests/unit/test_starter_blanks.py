from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from kama_claude.core.bus.envelope import PARSE_ERROR, make_error
from kama_claude.core.compact.budget import truncate_tool_results
from kama_claude.core.config import get_config
from kama_claude.core.context import ExecutionContext
from kama_claude.core.events.bus import EventBus
from kama_claude.core.loop import AgentLoop
from kama_claude.core.permissions.manager import PermissionManager
from kama_claude.core.permissions.policy import evaluate
from kama_claude.core.tools.invocation import invoke_tool
from kama_claude.core.tools.registry import ToolRegistry
from kama_claude.core.transport.socket_server import SocketServer

pytestmark = pytest.mark.starter_blanks


# 判断当前 import 到的 kama_claude 是否仍是挖空树（参考树应 skip）
def _is_starter_tree() -> bool:
    return "raise NotImplementedError" in inspect.getsource(get_config)


@pytest.fixture(scope="module", autouse=True)
def _skip_on_reference() -> None:
    if not _is_starter_tree():
        pytest.skip("running against reference implementation")


# 功能：验证 S0 配置与协议工厂入口存在且是显式填空哨兵，而不是缺失属性
# 设计：从真实发运路径 import get_config / make_error 再调用，断言 NotImplementedError，排除 ImportError/AttributeError
def test_s0_config_and_make_error_are_blank() -> None:
    assert callable(get_config)
    assert callable(make_error)
    with pytest.raises(NotImplementedError):
        get_config()
    with pytest.raises(NotImplementedError):
        make_error("1", PARSE_ERROR, "Parse error")


# 功能：验证 S0 传输层 SocketServer.start 可 import、可构造，调用时打到填空哨兵
# 设计：保留真实构造签名，await start()，确认失败在 NotImplementedError 而不是端口探测副作用
async def test_s0_socket_server_start_is_blank() -> None:
    assert hasattr(SocketServer, "start")
    server = SocketServer("127.0.0.1", 0)
    with pytest.raises(NotImplementedError):
        await server.start()


# 功能：验证 S1 Agent loop / EventBus / invoke_tool / ExecutionContext 入口是显式挖空
# 设计：只调用发运符号，不重写 loop 或工具逻辑；async 入口用 await 打到函数体里的哨兵
async def test_s1_loop_bus_invocation_are_blank() -> None:
    assert hasattr(AgentLoop, "run")
    assert hasattr(EventBus, "subscribe")
    assert callable(invoke_tool)

    bus = EventBus()
    with pytest.raises(NotImplementedError):
        bus.subscribe(lambda _e: None)  # type: ignore[arg-type, return-value]

    with pytest.raises(NotImplementedError):
        ExecutionContext(run_id="r1", goal="g", max_steps=1)

    registry = ToolRegistry()
    with pytest.raises(NotImplementedError):
        registry.register(None)  # type: ignore[arg-type]

    from kama_claude.core.llm.types import ToolCallBlock

    with pytest.raises(NotImplementedError):
        await invoke_tool(
            registry,
            ToolCallBlock(id="t1", name="echo", input={}),
            bus,
            "r1",
        )


# 功能：验证 S5 权限评估与 PermissionManager.check_and_wait 是显式挖空
# 设计：构造真实 PermissionManager（无 policy_file，避开 load 哨兵），调用 evaluate / check_and_wait
async def test_s5_permission_entries_are_blank() -> None:
    assert callable(evaluate)
    with pytest.raises(NotImplementedError):
        evaluate("bash", {"command": "ls"})

    manager = PermissionManager()
    assert hasattr(manager, "check_and_wait")
    with pytest.raises(NotImplementedError):
        await manager.check_and_wait(
            tool_use_id="u1",
            tool_name="bash",
            params={"command": "ls"},
            session_id="s1",
            event_emitter=lambda _d: None,  # type: ignore[arg-type, return-value]
        )


# 功能：验证 S6 truncate_tool_results 入口存在且打到填空哨兵
# 设计：直接调用真实函数，传入最小 messages，确认不是静默空实现
def test_s6_truncate_tool_results_is_blank() -> None:
    assert callable(truncate_tool_results)
    with pytest.raises(NotImplementedError):
        truncate_tool_results([{"role": "user", "content": "x"}])


# 功能：验证学生面对的包可 import，且挖空入口不是缺失属性
# 设计：hasattr 检查公开方法后再调用，把 AttributeError 与 NotImplementedError 分开
def test_teaching_symbols_exist_on_shipped_types() -> None:
    assert hasattr(SocketServer, "register")
    assert hasattr(SocketServer, "start")
    assert hasattr(SocketServer, "stop")
    assert hasattr(AgentLoop, "run")
    assert hasattr(PermissionManager, "respond")
    assert hasattr(PermissionManager, "check_and_wait")
    from kama_claude.core.memory.loader import load_context_file

    assert callable(load_context_file)
    with pytest.raises(NotImplementedError):
        load_context_file(Path("missing.md"))

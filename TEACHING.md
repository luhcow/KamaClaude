# 填空式学习指南

本仓库改成了类似 [mini-lsm](https://github.com/skyzh/mini-lsm) 的教学骨架：

| 路径 | 角色 |
| --- | --- |
| `src/kama_claude/` | 学生面对的填空树：类型、公开签名、脚手架保留，教学目标函数体是 `raise NotImplementedError` |
| `reference/kama_claude/` | 完整参考实现，可随时对照 |
| `tests/` | 判题器；import **真实发运符号** `kama_claude.*`，不要另写一份被测代码 |
| `docs/实现篇/` | 分阶段讲解（S0–S7），不是 mdbook |

每一处挖空旁边的注释写明阶段号（`S0`…`S7`）和要填什么。若同一函数后续阶段会加职责，注释按阶段写增量。

## 怎么做

1. 按 `docs/实现篇/S0-项目基础架构.md` 起，顺着 S0→S7 填 `src/` 里对应的 `NotImplementedError`。
2. 每填完一块，跑该模块的单测：`uv run pytest tests/unit/test_<模块>.py -v`。
3. 卡住时对照 `reference/kama_claude/` 里同名文件，但先自己写。
4. 填空完成后可忽略 `tests/unit/test_starter_blanks.py`（它只检查骨架仍是挖空）。

## 跑测试

```bash
# 骨架检查（挖空树应全绿）
uv run pytest tests/unit/test_starter_blanks.py -v

# 学生实现过程中：现有行为单测会红在 NotImplementedError 上，这是预期
uv run pytest tests/unit -v

# 对着完整参考跑（应全绿）
PYTHONPATH=reference uv run pytest tests/unit -v -m "not starter_blanks"
PYTHONPATH=reference uv run pytest tests/integration -v
```

## 阶段与主要填空

- **S0** 配置优先链 `get_config` / `_apply_toml` / `_apply_env`；协议工厂 `make_error`；TCP NDJSON `SocketServer` / `SocketClient`；`CoreApp._ping_handler` 与 `CoreApp.run` 的守护进程骨架。
- **S1** `EventBus`、`EventWriter`、`ExecutionContext`、`ToolRegistry`、`ReadFileTool.invoke`、`invoke_tool`（基础调用与事件）、`AgentLoop.run`（plan→act→observe）、`AgentRunner`、`AnthropicProvider.chat`、`TraceWriter`、`StdoutPrinter.handle`。
- **S2** `IpcEventBroadcaster`；Socket 读循环并发与断连 unsubscribe；TUI `_preview` / `_param_summary` / `LLMStreamBlock` / `ToolCallBlock` / `_handle_event`。
- **S3** `bash` / `write_file` / `list_dir`；`load_context_file`。
- **S4** `SessionStore` / `SessionManager`；`NoteSaveTool`；TUI 输入提交。
- **S5** `permissions.policy.evaluate`、`matches_outside_cwd`、`param_preview`、`load_policy_file` / `save_policy_file`、`PermissionManager`；`invoke_tool` 的参数校验、审批与重试。
- **S6** `truncate_tool_results`、`Compactor`、`TaskManager` 与 `task_*` 工具；session compact。
- **S7** `SkillLoader`、`AgentProfileLoader`、`SpawnAgentTool` / `AgentResultTool`、`BackgroundTaskRegistry`、`McpClient` / `McpServerManager` / `McpTool`。

类型、Pydantic 模型、数据类和平凡 getter 没有挖空，那是契约，请读它们再填函数体。

# 完整参考实现

本目录是 `src/kama_claude` 的完整可运行副本，对应填空前的产品代码。

学生应修改仓库根下的 `src/kama_claude/`。不要把参考实现拷回 `src/` 来“交作业”——现有 `tests/` 就是判题器，它们 import 的是 `kama_claude` 这个发运包。

对着参考实现跑测试（`PYTHONPATH` 优先于可编辑安装的 `src/`）：

```bash
PYTHONPATH=reference uv run pytest tests/unit -v -m "not starter_blanks"
PYTHONPATH=reference uv run pytest tests/integration -v
```

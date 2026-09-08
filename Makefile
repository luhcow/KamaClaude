.PHONY: lint test integration-test docs verify-s0 test-blanks test-ref

lint:
	uv run ruff check src tests scripts
	uv run mypy src

test:
	uv run pytest tests/unit -v

test-blanks:
	uv run pytest tests/unit/test_starter_blanks.py -v

test-ref:
	PYTHONPATH=reference uv run pytest tests/unit -v -m "not starter_blanks"
	PYTHONPATH=reference uv run pytest tests/integration -v

integration-test:
	uv run pytest tests/integration -v

docs:
	uv run python scripts/gen_protocol_doc.py

verify-s0:
	uv sync --frozen
	uv run ruff check src tests scripts
	uv run mypy src
	uv run pytest tests/unit/test_starter_blanks.py -v
	PYTHONPATH=reference uv run pytest tests/unit -v -m "not starter_blanks"
	PYTHONPATH=reference uv run pytest tests/integration -k ping -v
	uv run python scripts/gen_protocol_doc.py --check

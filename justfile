set unstable := true

deps:
    uv sync --no-dev --frozen

dev-deps:
    uv sync --only-dev --frozen

lock-deps:
    uv lock

upgrade-deps:
    uv lock --upgrade

configure: deps dev-deps

fix:
    just --fmt
    uv run ruff check --fix --unsafe-fixes

validate:
    uv lock --check
    uv run ruff check
    uv run ty check

test:
    uv run pytest tests

# AGENTS.md — semantic-ai-agent

Redis Semantic Caching sandbox project.
Build an intelligent semantic caching system using Redis with a domain of your choice.

## Setup

```bash
uv sync                       # install all deps (creates .venv)
uv run pre-commit install     # register git hooks (run once per clone)
```

## Running things

```bash
uv run jupyter lab            # start JupyterLab
uv run python src/script.py   # run a script inside the venv
```

## Quality checks

```bash
uv run poe check              # lint + typecheck + nbtest (full suite)
uv run poe lint               # ruff check + format --check
uv run poe fmt                # ruff format (auto-fix)
uv run poe typecheck          # mypy src/ + nbqa mypy notebooks/
uv run poe nbtest             # pytest --nbmake notebooks/ (slow, needs data/)
```

Always run `uv run poe check` after making any change and fix any errors.
Do not commit or push — the user handles all commits and pushes explicitly.

Don't read any .env file, use the .env.example file to understand the environment variables and create your own .env file.

## Project structure

```
data/raw/            # Original files — READ ONLY, never modify
data/interim/        # Intermediate outputs
data/processed/      # Final processed data, model-ready features
notebooks/           # Numbered notebooks — run in order
src/semantic_ai_agent/ # Reusable Python package (helpers, transforms, etc.)
models/              # Saved model checkpoints — not versioned
reports/             # Final reports and figures
```

## Gotchas

- `data/` is not versioned — only `.gitkeep` files are committed. You must provide your own dataset in `data/raw/` before running notebooks.
- `nbtest` (`pytest --nbmake`) will fail if `data/` is empty.
- `notebooks/*.ipynb` ignores `F401` (unused imports) — exploratory cells intentionally import without always using.
- `gitleaks` pre-commit hook will block commits containing secrets/API keys. Never hardcode credentials.
- When adding a new dependency: `uv add <package>` (updates both `pyproject.toml` and `uv.lock`).

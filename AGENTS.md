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
uv run poe serve              # start FastAPI server (uvicorn)
```

## Quality checks

```bash
uv run poe check              # lint + typecheck + unit tests (full suite)
uv run poe lint               # ruff check + format --check
uv run poe fmt                # ruff format (auto-fix)
uv run poe typecheck          # mypy src/ + nbqa mypy notebooks/
uv run poe test               # pytest tests/ (unit tests only, no Redis needed)
uv run poe nbtest             # pytest --nbmake notebooks/ (slow, needs Redis + data/)
```

Always run `uv run poe check` after making any change and fix any errors.
Do not commit or push — the user handles all commits and pushes explicitly.

Don't read any .env file, use the .env.example file to understand the environment variables and create your own .env file.

## Project structure

```
data/raw/                    # Original files — READ ONLY, never modify
data/interim/                # Intermediate outputs
data/processed/              # Final processed data, model-ready features
notebooks/                   # Numbered notebooks — run in order
reports/                     # Final reports and figures
models/                      # Saved model checkpoints — not versioned
tests/                       # Unit + integration tests (pytest)
  api/                       # FastAPI route tests (use TestContainer, no Redis)
src/semantic_ai_agent/       # Installable Python package
  settings.py                # Pydantic BaseSettings — all config via env vars
  utils/
    utils.py                 # Shared helpers: ping_redis, try_connect_to_redis
  domain/                    # Pure Pydantic models — no business logic
    base.py                  # DomainBase (shared model_config)
    faq_data.py              # FaqEntry
    cache_entry.py           # CacheEntry
    cache_result.py          # CacheResult, CacheResults
    cache_stats.py           # CacheStats
    hydrate_result.py        # HydrateResult
    chat_message.py          # ChatMessage
  services/                  # Business logic — raise @dataclass exceptions, no HTTP
    helper.py                # load_faq_json(path: Path) -> list[FaqEntry]
    cache/
      query_service.py       # CacheQueryService  — check(), store()
      hydration_service.py   # CacheHydrationService — hydrate(), hydrate_from_df()
      admin_service.py       # CacheAdminService  — clear(), stats()
      exceptions.py          # FaqFileNotFoundError, CacheConnectionError, …
    chat/
      service.py             # ChatService — ask()
      exceptions.py          # CacheConnectionError, LLMError
  injections/                # dependency-injector containers
    __init__.py              # configure_container() (cached singleton factory)
    production.py            # Container — Singletons for Redis infra, Factories for services
    test.py                  # TestContainer — mock services, in-memory settings
  api/                       # FastAPI application
    schema.py                # BaseSchema only (camelCase alias + populate_by_name)
    app.py                   # create_app() factory — includes routers + exception handlers
    dependencies.py          # Annotated type aliases: ChatServiceDependency, etc.
    error_handlers/
      __init__.py            # EXCEPTION_HANDLERS dict (exception type → handler fn)
      chat.py                # Handler functions for chat service exceptions
    routes/                  # One sub-package per endpoint group
      __init__.py            # ROUTERS list (imported by app.py)
      chat/
        schema.py            # ChatRequest, ChatResponse, ErrorResponse
        examples.py          # CHAT_EXAMPLES (OpenAPI request body examples)
        chat.py              # POST /chat router
      cache/
        schema.py            # HydrateRequest, HydrateResponse, CacheStatsResponse
        examples.py          # EXAMPLES (OpenAPI request body examples)
        cache.py             # POST /cache/hydrate, DELETE /cache, GET /cache/stats
      health/
        schema.py            # HealthResponse
        health.py            # GET / and GET /health routers
  cache/                     # Low-level cache utilities (used by notebooks)
    config.py                # Cache configuration constants
    evals.py                 # CacheEvaluator, PerfEval (notebook evaluation helpers)
```

## Architecture conventions

These are strict rules. Do not deviate without explicit user approval.

### Layering
```
API route → Service → Domain model
              ↓
           Helper / Utils
```
- Routes call services; services call helpers/utils. Routes never touch Redis directly.
- Services raise typed `@dataclass` exceptions (defined in `services/<domain>/exceptions.py`).
- API error handlers convert service exceptions to HTTP responses (defined in `api/error_handlers/`).
- New exception types go in `services/<domain>/exceptions.py`; their handlers go in `api/error_handlers/<domain>.py` and must be registered in `api/error_handlers/__init__.py`.

### Domain models
- All domain models live in `domain/` and inherit from `DomainBase`.
- API request/response models live in `api/routes/<route>/schema.py` and inherit from `BaseSchema`.
- `BaseSchema` lives in `api/schema.py` **only** — do not add other models there.

### Dependency injection
- Infrastructure (Redis client, SemanticCache, LLM) → `providers.Singleton` in `Container`.
- Services (`CacheQueryService`, `CacheHydrationService`, `CacheAdminService`, `ChatService`) → `providers.Factory` in `Container`.
- Add new injectable dependencies as `Annotated` aliases in `api/dependencies.py`.
- Never import libraries inside function bodies — all imports must be at module level.

### Schemas
- Each route package owns its schemas: `api/routes/<route>/schema.py`.
- All schemas inherit `BaseSchema` (camelCase JSON output, `populate_by_name=True` so Python keyword construction with snake_case also works).
- OpenAPI examples live in `api/routes/<route>/examples.py`, not in the route file itself.

### Adding a new endpoint group
1. Create `api/routes/<name>/` with `__init__.py`, `schema.py`, `examples.py`, `<name>.py`.
2. Add the router to `api/routes/__init__.py` → `ROUTERS`.
3. Add the wiring module path to `Container.wiring_config` and `TestContainer.wiring_config`.
4. Add mock services (if needed) to `injections/test.py`.

## Gotchas

- `data/` is not versioned — only `.gitkeep` files are committed. You must provide your own dataset in `data/raw/` before running notebooks.
- `nbtest` (`pytest --nbmake`) will fail if `data/` is empty or Redis is not running.
- `notebooks/*.ipynb` ignores `F401` (unused imports) — exploratory cells intentionally import without always using.
- `gitleaks` pre-commit hook will block commits containing secrets/API keys. Never hardcode credentials.
- When adding a new dependency: `uv add <package>` (updates both `pyproject.toml` and `uv.lock`).
- `00-semantic-cache-demo.ipynb` uses the legacy `SemanticCacheWrapper` import — it is a known issue and does not affect `poe test`.
- `poe check` runs `poe test` (unit tests), not `poe nbtest` (notebooks) — notebooks require a live Redis connection.

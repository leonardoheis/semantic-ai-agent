# HR Policy FAQ Semantic Cache

An intelligent semantic caching system built with Redis that caches responses to employee HR policy questions. Employees frequently ask the same policy questions using varied phrasing — e.g., "How many vacation days do I get?" vs "What's the PTO allowance?" — and semantic caching recognizes these as equivalent, delivering instant cached answers instead of calling the LLM every time.

This reduces LLM API costs by 70%+ and response latency by 80%+ for repeated HR queries across categories like vacation, benefits, payroll, leave, remote work, expenses, and onboarding.

## Prerequisites

- **Python 3.10+**
- **Docker** (for Redis Stack)
- **uv** — Python package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **OpenAI API key** — for LLM-generated responses on cache misses

## Quick start

```bash
git clone <repository-url>
cd semantic-ai-agent
uv sync
uv run pre-commit install
docker compose up -d
cp .env.example .env        # then edit .env and set your OPENAI_API_KEY
uv run jupyter lab
```

Open `notebooks/01-experiment.ipynb` and run all cells in order.  
The notebook uses `mock_llm` automatically when running under `poe check`; real OpenAI calls are only made in interactive JupyterLab sessions.

## Running the project

### 1. Clone and install dependencies

```bash
git clone <repository-url>
cd semantic-ai-agent
uv sync
```

This creates a `.venv` and installs all packages including Redis, sentence-transformers, LangChain, and PyTorch.

### 2. Install git hooks

```bash
uv run pre-commit install
```

One-time setup. Registers `ruff` formatting and `gitleaks` secret scanning hooks.

### 3. Start Redis

```bash
docker compose up -d
```

This launches Redis Stack with:
- **Port 6379** — Redis server (used by the cache)
- **Port 8001** — RedisInsight web UI for browsing cached data

Verify it is running:

```bash
docker compose ps
```

Or open http://localhost:8001 in your browser to access RedisInsight.

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI API key:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Your OpenAI API key (required for LLM calls) |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `CACHE_NAME` | `semantic-cache` | Name of the Redis vector index |
| `CACHE_DISTANCE_THRESHOLD` | `0.3` | Cosine distance threshold for cache hits |
| `CACHE_TTL_SECONDS` | `3600` | Time-to-live for cached entries (seconds) |

### 5. Launch the API server

```bash
uv run poe serve
```

The FastAPI server starts at http://localhost:8000. Interactive docs are available at http://localhost:8000/docs.

### 6. Launch JupyterLab

```bash
uv run jupyter lab
```

### 7. Run the notebook

Open `notebooks/01-experiment.ipynb` and run cells in order. The notebook walks through the full semantic caching pipeline:

1. **Imports and Redis connection** — verifies Redis is reachable
2. **Load FAQ data** — reads 26 curated HR FAQ pairs from `data/raw/faq_data.json`
3. **Initialize cache** — creates a `SemanticCache` (via `CacheQueryService`) with distance threshold and TTL
4. **Embedding model** — loads `all-MiniLM-L6-v2` (384 dimensions) for semantic encoding
5. **Hydrate cache** — bulk-loads all FAQ pairs into Redis via `CacheHydrationService`
6. **Cache logic** — `get_cached_or_generate()` checks cache first, calls GPT on miss, stores the result via `CacheStoreService`
7. **Test hits and misses** — validates cache behavior with semantically similar and different queries
8. **Threshold tuning** — sweeps distance thresholds and plots precision/recall/F1 curves
9. **Performance evaluation** — measures hit rate, latency, and cost savings against spec goals

### 8. GPU support (optional)

If you have an NVIDIA GPU with CUDA 12.8 support, PyTorch CUDA wheels are automatically resolved via the `[tool.uv.sources]` configuration in `pyproject.toml`. Verify GPU availability in the notebook:

```python
import torch
print(torch.cuda.is_available())  # True if GPU is detected
print(torch.cuda.get_device_name(0))
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat` | Send a question, get a cached or LLM-generated answer |
| `GET` | `/health` | Check Redis connectivity |
| `POST` | `/cache/hydrate` | Load FAQ data into the semantic cache |
| `DELETE` | `/cache` | Clear all cache entries |
| `GET` | `/cache/stats` | View cache index metadata |

The `/chat` endpoint supports multi-turn conversation via `session_id`. Omit it to start a new session, or pass a previous `session_id` to continue the conversation.

## Project structure

```
data/raw/faq_data.json              # 26 curated HR FAQ pairs (source data)
data/interim/                       # Intermediate processing outputs
data/processed/                     # Final processed data
notebooks/
  00-semantic-cache-demo.ipynb      # Introductory demo notebook
  01-experiment.ipynb               # Full semantic caching experiment
src/semantic_ai_agent/
  api/                              # FastAPI chatbot API
    error_handlers/                 # Central exception handler registry + per-service handlers
    routes/
      cache/                        # /cache endpoints — hydrate, clear, stats
        schema.py                   # HydrateRequest, CacheStatsResponse
        examples.py                 # OpenAPI request body examples
      chat/                         # /chat endpoint — multi-turn conversation
        schema.py                   # ChatRequest, ChatResponse
        examples.py                 # OpenAPI request body examples
      health/                       # /health endpoint
        schema.py                   # HealthResponse
    app.py                          # App factory (auto-discovers routers and exception handlers)
    dependencies.py                 # Annotated DI type aliases (Provide[...])
    schema.py                       # BaseSchema (camelCase aliasing, shared config)
  domain/                           # Pure Pydantic v2 domain models
    base.py                         # DomainBase
    faq_data.py                     # FaqEntry (raw FAQ record)
    cache_entry.py                  # CacheEntry
    cache_result.py                 # CacheResult / CacheResults
    cache_stats.py                  # CacheStats
    chat_message.py                 # ChatMessage (conversation history)
    chat_result.py                  # ChatResult (ask() return value)
    hydrate_result.py               # HydrateResult
    protocols.py                    # CacheReader / CacheWriter protocols
  services/
    cache/                          # Cache service layer (SRP-split)
      query.py                      # CacheQueryService — lookup / reranking
      store.py                      # CacheStoreService — write new entries
      hydration.py                  # CacheHydrationService — bulk FAQ load
      admin.py                      # CacheAdminService — clear
      stats.py                      # CacheStatsService — read index metadata
      exceptions.py                 # Cache-specific dataclass exceptions
    chat/
      chat.py                       # ChatService — session history, cache + LLM orchestration
      exceptions.py                 # Chat-specific dataclass exceptions
    helper.py                       # Shared helpers (load_faq_json)
  injections/
    production.py                   # DeclarativeContainer — Singletons (Redis) + Factories (services)
    test.py                         # TestContainer — in-memory mocks
  cache/
    config.py                       # API key loading helper
    evals.py                        # CacheEvaluator and PerfEval metrics (used by notebooks)
  utils/
    utils.py                        # ping_redis / try_connect_to_redis
  settings.py                       # Pydantic BaseSettings (env-driven configuration)
  frontend/                         # Placeholder for future UI
tests/
  api/                              # API route tests (test_chat, test_cache, test_health)
  services/                         # Service unit tests (test_chat_service)
  conftest.py                       # Shared pytest fixtures
```

## Cache design summary

| Parameter | Value |
|-----------|-------|
| Embedding model | `all-MiniLM-L6-v2` (384 dimensions) |
| Distance metric | Cosine similarity |
| Similarity threshold | 0.87 (distance threshold 0.13) |
| TTL | 30 days |
| Index type | HNSW |
| FAQ categories | 8 (vacation, benefits, payroll, remote work, sick/family leave, expenses, onboarding, general) |
| Total FAQ pairs | 26 |

Performance targets: 65%+ hit rate, <5ms cache lookup, 70% fewer LLM API calls, >95% precision.

## Quality checks

```bash
uv run poe check       # lint + typecheck + nbtest (full suite)
uv run poe lint        # ruff check + format verification
uv run poe fmt         # ruff auto-format
uv run poe typecheck   # mypy on src/ and notebooks/
uv run poe test        # pytest tests/ (API and service tests)
uv run poe nbtest      # pytest --nbmake (executes notebooks; USE_MOCK_LLM=true auto-set)
uv run poe serve       # start the FastAPI server on port 8000
```

Always run `uv run poe check` after making changes.

## Tech stack

| Component | Library |
|-----------|---------|
| API framework | FastAPI, Pydantic v2, uvicorn |
| Vector store and caching | Redis Stack, RedisVL |
| Semantic embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| LLM | OpenAI GPT-4o-mini via LangChain |
| Data processing | pandas, NumPy |
| Visualization | matplotlib |
| Quality tooling | ruff, mypy, pytest, pre-commit |
| Package management | uv, hatchling |

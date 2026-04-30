# Architecture

Hyper Claude Code is a Python 3.14 FastAPI proxy with an extensible middleware pipeline, 6 provider backends, and a 31-agent development team.

## System Overview

```
Claude Code CLI / VS Code / JetBrains
            |
            |  Anthropic Messages API
            v
   +---------------------------+
   |    Hyper Claude Code       |
   |                           |
   |  Middleware Pipeline       |
   |    Failover → Cache →     |
   |    Logger → Cost Tracker   |
   |                           |
   |  Model Router              |
   |    Opus/Sonnet/Haiku →    |
   |    provider/model          |
   |                           |
   |  Provider Registry         |
   |    OpenAI Chat Transport   |
   |    Anthropic Msg Transport |
   +---------------------------+
            |
            v
  NIM  OpenRouter  DeepSeek  LM Studio  llama.cpp  Ollama
```

## Package Structure

```
hyper-claude-code/
  server.py                  ASGI entry point — creates app, runs uvicorn
  api/
    app.py                   FastAPI factory, lifespan, CORS, exception handlers
    routes.py                /v1/messages, /v1/messages/count_tokens, /v1/models
    services.py              ClaudeProxyService — orchestrates routing → provider → streaming
    model_router.py          Claude model name → provider_id/model_name resolution
    dependencies.py          Auth (require_api_key), provider getter
    optimization_handlers.py 5 fast-path handlers for trivial requests
    runtime.py               AppRuntime — lifespan owner, initializes all subsystems
    cost_routes.py           GET /v1/cost
    cache_routes.py          GET /v1/cache/stats, POST /v1/cache/clear
    health_routes.py         GET /v1/health/providers
    models/                  Pydantic request/response models
    web_tools/               Web fetch with SSRF protection
  core/
    anthropic/
      conversion.py          AnthropicToOpenAIConverter (590 LOC, high cohesion)
      native_messages_request.py  Native Anthropic request builder
      sse.py                 SSEBuilder — Anthropic SSE event factory
      thinking.py            ThinkTagParser — streaming <think> block extraction
      tools.py               HeuristicToolParser — tool call detection in text
      tokens.py              tiktoken-based token estimation
      stream_contracts.py    SSE ordering invariants
    rate_limit.py            StrictSlidingWindowLimiter
  providers/
    base.py                  BaseProvider — abstract async generator interface
    openai_compat.py         OpenAIChatTransport (NIM) — 470 LOC streaming
    anthropic_messages.py    AnthropicMessagesTransport (5 providers)
    registry.py              Lazy provider cache by provider_id
    rate_limit.py            GlobalRateLimiter — 3-tier per-provider limiting
    error_mapping.py         Provider exceptions → Anthropic error shapes
    nvidia_nim/              NIM-specific client, request builder, voice
    open_router/             OpenRouter client and request builder
    deepseek/                DeepSeek client
    lmstudio/                LM Studio client
    llamacpp/                llama.cpp client
    ollama/                  Ollama client
  middleware/
    base.py                  Middleware ABC — before_request / after_response
    pipeline.py              Pipeline — ordered execution with short-circuit
    cost_tracker.py          Cost Intelligence plugin
    pricing.py               Per-provider token pricing tables
    response_cache.py        SHA-256 exact-match caching plugin
    cache_utils.py           Deterministic request hashing
    circuit_breaker.py       3-state circuit breaker (CLOSED/OPEN/HALF_OPEN)
    failover.py              Provider failover plugin
    request_logger.py        Request logging plugin
  storage/
    database.py              Async SQLite via aiosqlite (requests, cache, errors)
  messaging/
    handler.py               Claude message handler (620 LOC, CLI lifecycle)
    trees/                   Conversation tree queue management
    platforms/               Discord + Telegram adapters
    rendering/               Platform-specific markdown
    session.py               SessionStore with atomic file writes
    transcript.py            Streaming event → rendered text pipeline
    voice.py                 Whisper/NIM voice transcription
  cli/
    session.py               Claude CLI subprocess management
    manager.py               Session lifecycle coordinator
    process_registry.py      PID tracking + atexit cleanup
  config/
    settings.py              Pydantic Settings — all env vars
    provider_catalog.py      Provider metadata + transport types
    logging_config.py        Loguru configuration + redaction
  tests/                     20K+ lines — unit, contract, smoke
  .claude/                   31-agent team — agents, hooks, docs, Shadow Mind
```

## Request Lifecycle (10 Stages)

### 1. Ingress

`server.py` → `api/app.py:create_app()` → FastAPI with lifespan context manager.

`AppRuntime` (dataclass at `api/runtime.py`) owns the full lifecycle: provider registry, messaging platform, CLI session manager, storage, and middleware pipeline.

### 2. Authentication

`api/dependencies.py:require_api_key()` — checks `x-api-key`, `Authorization: Bearer`, or `anthropic-auth-token` headers. Uses `secrets.compare_digest` for constant-time comparison. Returns immediately (no auth) when `ANTHROPIC_AUTH_TOKEN` is empty.

### 3. Validation

FastAPI auto-validates the JSON body into `MessagesRequest` (Pydantic model at `api/models/anthropic.py`). `extra="allow"` preserves unknown fields for forward-compatibility. Discriminated union handles all 9+ Anthropic content block types.

### 4. Middleware Pipeline

`middleware/pipeline.py` executes middleware in order: Failover → Cache → Logger → Cost Tracker.

- `before_request()` runs in order — any middleware can short-circuit by returning a response object
- The handler (actual provider call) runs
- `after_response()` runs in reverse order

### 5. Optimization Fast-Path

`api/optimization_handlers.py` — 5 handlers intercept trivial Claude Code requests and return responses locally:

1. **Network probe mock** — quota/billing checks
2. **Prefix detection** — prefix matching probes
3. **Title generation skip** — conversation title requests
4. **Suggestion mode skip** — suggestion probes
5. **Filepath extraction mock** — filepath probes

These save latency and provider quota for requests that don't need a model.

### 6. Model Routing

`api/model_router.py:ModelRouter.resolve()` maps Claude model names to provider references:
- `claude-3-5-sonnet` → `MODEL_SONNET` setting → e.g., `open_router/deepseek/deepseek-r1-0528:free`
- Falls back to `MODEL` if no tier-specific override

Returns a frozen `ResolvedModel` dataclass with `provider_id` and `provider_model`.

### 7. Request Conversion

Two paths based on `transport_type` in `config/provider_catalog.py`:

**OpenAI Chat (NIM):** `core/anthropic/conversion.py:AnthropicToOpenAIConverter` performs heavy conversion — messages, tools, system prompts, reasoning replay modes, deferred post-tool content.

**Native Anthropic (5 providers):** `core/anthropic/native_messages_request.py` does minimal transformation — `model_dump(exclude_none=True)`, thinking history sanitization, OpenRouter-specific extra body.

### 8. Upstream Call

Providers call their backends via `openai.AsyncOpenAI` (NIM) or `httpx.AsyncClient` (native). All calls go through `GlobalRateLimiter.execute_with_retry()` with three-tier protection.

### 9. Streaming

**OpenAI Chat Transport** (~250 LOC streaming loop): iterates `async for chunk in stream`, pipes through `ThinkTagParser` + `HeuristicToolParser`, generates Anthropic SSE events via `SSEBuilder`.

**Native Anthropic Transport**: groups raw SSE lines into events, applies `NativeSseBlockPolicyState` filtering, tracks emitted blocks for error recovery.

### 10. Delivery

`StreamingResponse` with `text/event-stream` media type and `X-Accel-Buffering: no` header. The async generator yields SSE events directly to the client.

## Middleware Pipeline Architecture

```
before_request (in order):
  FailoverMiddleware    — reroute if provider circuit is open
  ResponseCacheMiddleware — return cached response (short-circuit)
  RequestLoggerMiddleware — no-op before
  CostTrackerMiddleware — check budget cap (429 if exceeded)

handler:
  ClaudeProxyService._create_message_inner()

after_response (reverse order):
  CostTrackerMiddleware — compute cost, log to storage
  RequestLoggerMiddleware — log request metadata
  ResponseCacheMiddleware — store response in cache
  FailoverMiddleware    — record success/failure on circuit breaker
```

Each middleware extends `middleware.Middleware` and overrides `before_request()` and/or `after_response()`. The pipeline uses identity comparison (`result is not request_data`) to detect short-circuits.

## Provider Architecture

```
BaseProvider (abstract)
  |
  +-- OpenAIChatTransport
  |     +-- NvidiaProvider
  |
  +-- AnthropicMessagesTransport
        +-- OpenRouterProvider
        +-- DeepSeekProvider
        +-- LMStudioProvider
        +-- LlamaCppProvider
        +-- OllamaProvider
```

`ProviderRegistry` (`providers/registry.py`) lazily creates provider instances per `provider_id`. Each provider implements `stream_response()` as an async generator yielding SSE event strings.

## Rate Limiting

Three independent mechanisms per provider:

| Tier | Implementation | Config |
|------|---------------|--------|
| Proactive | `StrictSlidingWindowLimiter` — sliding window with strict enforcement | `PROVIDER_RATE_LIMIT`, `PROVIDER_RATE_WINDOW` |
| Reactive | 429 detection in `execute_with_retry()` — exponential backoff + reactive blocking | Automatic |
| Concurrency | `asyncio.Semaphore` — caps in-flight requests | `PROVIDER_MAX_CONCURRENCY` |

## Storage

`storage/database.py` — async SQLite via `aiosqlite`. Three tables:

| Table | Purpose |
|-------|---------|
| `requests` | Request log (timestamp, model, provider, tokens, latency, cost, cache_hit) |
| `response_cache` | Cached responses (request_hash, response_data, created_at, expires_at) |
| `provider_errors` | Provider failure log (provider_id, error_type, timestamp) |

Database file at `~/.fcc/hcc.db` (configurable via `STORAGE_DB_PATH`).

## Import Boundaries

Enforced by AST-based contract tests at `tests/contracts/test_import_boundaries.py`:

- `core/` — zero imports from `api/`, `providers/`, `config/`, `messaging/`, `cli/`
- `providers/` — no imports from `messaging/`
- `config/` — leaf package
- `api/` — imports `providers/` only through `base`, `exceptions`, `registry`

## 31-Agent Team Architecture

See [`.claude/docs/team/TEAM_OVERVIEW.md`](../.claude/docs/team/TEAM_OVERVIEW.md) for the full layered OS architecture, agent roster, NEXUS protocol, trust infrastructure, and Shadow Mind specification.

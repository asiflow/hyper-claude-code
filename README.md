<div align="center">

<h1>Hyper Claude Code</h1>

<h3>The intelligent middleware platform for Claude Code</h3>

<p>Run Claude Code with any model. Track costs. Cache responses. Auto-failover between providers.<br>Ship with a 31-agent AI development team built in.</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/python-3.14-3776ab.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json&style=for-the-badge)](https://github.com/astral-sh/uv)
[![Tested with Pytest](https://img.shields.io/badge/testing-Pytest-00c0ff.svg?style=for-the-badge)](https://github.com/asiflow/hyper-claude-code/actions/workflows/tests.yml)
[![Type checking: Ty](https://img.shields.io/badge/type%20checking-ty-ffcc00.svg?style=for-the-badge)](https://pypi.org/project/ty/)
[![Code style: Ruff](https://img.shields.io/badge/code%20formatting-ruff-f5a623.svg?style=for-the-badge)](https://github.com/astral-sh/ruff)

[Quick Start](#-quick-start) · [Middleware](#-intelligent-middleware) · [Providers](#-providers) · [Agent Team](#-31-agent-development-team) · [API](#-api-endpoints) · [Docs](#-development)

</div>

---

## Why Hyper Claude Code?

Claude Code is the best agentic coding tool. But it only works with Anthropic's models at Anthropic's prices.

**Hyper Claude Code changes that.** It sits between Claude Code and any LLM provider — transparently proxying requests while adding intelligence at every layer.

| | |
|---|---|
| **6 Providers** | NVIDIA NIM, OpenRouter, DeepSeek, LM Studio, llama.cpp, Ollama |
| **4 Middleware Plugins** | Cost tracking, response caching, provider failover, request logging |
| **31-Agent Dev Team** | CTO-led engineering team with NEXUS protocol, Shadow Mind, trust infrastructure |
| **7 API Endpoints** | Cost, cache, health monitoring + standard Anthropic Messages API |
| **75K+ Lines** | Production-grade Python 3.14 with 20K+ lines of tests |
| **13 Feature Flags** | Everything toggleable, zero overhead when off |

```
Claude Code CLI / VS Code / JetBrains
            |
            |  Standard Anthropic API
            v
    +-----------------------+
    |  Hyper Claude Code    |
    |                       |
    |  Cost Tracking        |
    |  Response Caching     |
    |  Provider Failover    |
    |  Request Logging      |
    +-----------------------+
            |
            |  Provider-native format
            v
    NIM  OpenRouter  DeepSeek  LM Studio  llama.cpp  Ollama
```

**Use any model.** Free, paid, or local. NVIDIA NIM, OpenRouter, DeepSeek, LM Studio, llama.cpp, Ollama — all work out of the box.

**Pay nothing.** Route to free models on NVIDIA NIM or OpenRouter. Run fully local with Ollama or llama.cpp. Zero API costs.

**Stay private.** Run local models — your code never leaves your machine.

**Mix models per tier.** Send Opus requests to a powerful cloud model, Sonnet to a mid-tier, Haiku to a fast local model. All automatic.

---

## Quick Start

### 1. Install

```bash
# Install Claude Code (https://github.com/anthropics/claude-code)
# Then:
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.14
```

<details>
<summary>Windows PowerShell</summary>

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv self update
uv python install 3.14
```
</details>

### 2. Configure

```bash
git clone https://github.com/asiflow/hyper-claude-code.git
cd hyper-claude-code
cp .env.example .env
```

Edit `.env` — pick a provider and set your key:

```dotenv
NVIDIA_NIM_API_KEY="nvapi-your-key"
MODEL="nvidia_nim/z-ai/glm4.7"
ANTHROPIC_AUTH_TOKEN="your-secret-token"
```

> Generate a strong token: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

### 3. Start

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

> **Security:** When binding to `0.0.0.0`, always set `ANTHROPIC_AUTH_TOKEN`. For local-only use, omit `--host` to default to `127.0.0.1`.

### 4. Connect Claude Code

```bash
ANTHROPIC_AUTH_TOKEN="your-secret-token" ANTHROPIC_BASE_URL="http://localhost:8082" claude
```

That's it. Claude Code now runs through your proxy with your chosen model.

<details>
<summary>VS Code Extension</summary>

Add to `settings.json`:

```json
"claudeCode.environmentVariables": [
  { "name": "ANTHROPIC_BASE_URL", "value": "http://localhost:8082" },
  { "name": "ANTHROPIC_AUTH_TOKEN", "value": "your-secret-token" }
]
```
</details>

<details>
<summary>JetBrains ACP</summary>

Edit the installed Claude ACP config and add:

```json
"env": {
  "ANTHROPIC_BASE_URL": "http://localhost:8082",
  "ANTHROPIC_AUTH_TOKEN": "your-secret-token"
}
```
</details>

<details>
<summary>Model Picker (claude-pick)</summary>

```bash
brew install fzf
alias claude-pick="/path/to/hyper-claude-code/claude-pick"
claude-pick
```

Or create fixed aliases:

```bash
alias claude-kimi='ANTHROPIC_BASE_URL="http://localhost:8082" ANTHROPIC_AUTH_TOKEN="token:moonshotai/kimi-k2.5" claude'
```
</details>

---

## Intelligent Middleware

HCC is not just a proxy — it's an **intelligent middleware platform**. Four built-in plugins intercept every request, all behind feature flags with zero overhead when disabled.

### Cost Intelligence

Track what every coding session costs. Set budget caps. Never overspend.

```dotenv
ENABLE_COST_TRACKING=true
MAX_SESSION_COST_USD=5.00
```

- Real-time per-request cost computation from token counts + provider pricing
- Session, daily, and monthly aggregation via `GET /v1/cost`
- Hard budget cap — returns HTTP 429 before you exceed your limit
- Per-provider pricing tables (free models report $0.00)

### Response Caching

Identical requests return instantly. Save money and latency.

```dotenv
ENABLE_RESPONSE_CACHE=true
CACHE_TTL_SECONDS=3600
CACHE_MAX_ENTRIES=1000
```

- SHA-256 exact-match on normalized request content
- Configurable TTL and max entry count with LRU eviction
- Cache stats at `GET /v1/cache/stats` — measure your actual hit rate
- Clear cache anytime via `POST /v1/cache/clear`

### Provider Failover

If one provider goes down, HCC switches automatically. Your coding session never breaks.

```dotenv
ENABLE_PROVIDER_FAILOVER=true
FAILOVER_ERROR_THRESHOLD=0.5
FAILOVER_COOLDOWN_SECONDS=30
```

- Per-provider circuit breaker (CLOSED / OPEN / HALF_OPEN state machine)
- Configurable error thresholds and sliding window
- Ordered failover chains — define backup providers per primary
- Health dashboard at `GET /v1/health/providers`

### Request Logging

Full audit trail of every request for debugging and analysis.

```dotenv
ENABLE_REQUEST_LOGGING=true
STORAGE_DB_PATH="~/.fcc/hcc.db"
```

- Model, provider, token counts, latency, cost — all logged to local SQLite
- Zero external dependencies — everything stays on your machine

### Middleware Pipeline Architecture

Every feature is a plugin in an extensible pipeline:

```
Request --> [Failover] --> [Cache] --> [Logger] --> [Cost] --> Provider
               |              |
         reroute if       return cached
         provider down    (skip everything)
```

Build your own middleware by extending the `Middleware` base class. Add it to the pipeline. Done.

---

## Providers

Six backends. Two transport types. One API.

| Provider | Prefix | Key Required | Models |
|----------|--------|:---:|--------|
| **NVIDIA NIM** | `nvidia_nim/...` | Yes | [browse](https://build.nvidia.com/explore/discover) — `glm4.7`, `glm5`, `kimi-k2.5`, `minimax-m2.5` |
| **OpenRouter** | `open_router/...` | Yes | [browse](https://openrouter.ai/models) — 200+ models, [free tier](https://openrouter.ai/collections/free-models) |
| **DeepSeek** | `deepseek/...` | Yes | `deepseek-chat`, `deepseek-reasoner` |
| **LM Studio** | `lmstudio/...` | No | Any loaded model |
| **llama.cpp** | `llamacpp/...` | No | Any served model |
| **Ollama** | `ollama/...` | No | Any pulled model |

<details>
<summary><b>Provider setup details</b></summary>

**NVIDIA NIM** — Get a key at [build.nvidia.com/settings/api-keys](https://build.nvidia.com/settings/api-keys):
```dotenv
NVIDIA_NIM_API_KEY="nvapi-your-key"
MODEL="nvidia_nim/z-ai/glm4.7"
```

**OpenRouter** — Get a key at [openrouter.ai/keys](https://openrouter.ai/keys):
```dotenv
OPENROUTER_API_KEY="sk-or-your-key"
MODEL="open_router/stepfun/step-3.5-flash:free"
```

**DeepSeek** — Get a key at [platform.deepseek.com](https://platform.deepseek.com/api_keys):
```dotenv
DEEPSEEK_API_KEY="your-deepseek-key"
MODEL="deepseek/deepseek-chat"
```

**LM Studio** — Start the local server, load a model:
```dotenv
LM_STUDIO_BASE_URL="http://localhost:1234/v1"
MODEL="lmstudio/your-loaded-model"
```

**llama.cpp** — Start `llama-server` with enough context:
```dotenv
LLAMACPP_BASE_URL="http://localhost:8080/v1"
MODEL="llamacpp/local-model"
```

**Ollama** — Pull and serve:
```bash
ollama pull llama3.1 && ollama serve
```
```dotenv
OLLAMA_BASE_URL="http://localhost:11434"
MODEL="ollama/llama3.1"
```
</details>

### Mix Providers Per Tier

Route different Claude Code model tiers to different providers:

```dotenv
MODEL_OPUS="nvidia_nim/moonshotai/kimi-k2.5"
MODEL_SONNET="open_router/deepseek/deepseek-r1-0528:free"
MODEL_HAIKU="lmstudio/unsloth/GLM-4.7-Flash-GGUF"
MODEL="nvidia_nim/z-ai/glm4.7"
```

---

## 31-Agent Development Team

HCC ships with something no other open-source project has: **a 31-agent AI engineering team** that activates automatically when you open Claude Code in this repo.

```
Say "full team session" to activate all 31 agents.
```

The CTO agent takes command, assesses your request, delegates to specialist agents, validates findings through evidence verification, and synthesizes results with adversarial review.

### The Roster

| Tier | Agents | What They Do |
|------|--------|-------------|
| **CTO** | `cto` | Supreme authority — delegates, debates, evolves the team |
| **Builders** | `elite-engineer` `ai-platform-architect` `frontend-platform-engineer` `beam-architect` `elixir-engineer` `go-hybrid-engineer` | Write production code across any stack |
| **Guardians** | `go-expert` `python-expert` `typescript-expert` `deep-qa` `deep-reviewer` `infra-expert` `database-expert` `observability-expert` `test-engineer` `api-expert` `beam-sre` | Review, audit, catch what builders miss |
| **Strategists** | `deep-planner` `orchestrator` | Decompose tasks, coordinate multi-agent workflows |
| **Intelligence** | `memory-coordinator` `cluster-awareness` `benchmark-agent` `erlang-solutions-consultant` `talent-scout` `intuition-oracle` | Cross-agent knowledge, competitive intel, pattern recognition |
| **Meta** | `meta-agent` `recruiter` | Evolve agent prompts, hire new specialists on demand |
| **Governance** | `session-sentinel` | Protocol compliance, team health audits |
| **Verification** | `evidence-validator` `challenger` | Verify claims against source, adversarial review of recommendations |

### How It Works

**NEXUS Protocol** — Agents can't spawn other agents directly (Claude Code limitation). NEXUS bridges this: agents emit `[NEXUS:SPAWN]`, `[NEXUS:SCALE]`, `[NEXUS:ASK]` syscalls via `SendMessage`. The main thread processes them in real-time. Result: full multi-agent orchestration within Claude Code's permission model.

**Trust Infrastructure** — Every HIGH-severity finding is independently verified by `evidence-validator` before reaching you. Every strategic recommendation is stress-tested by `challenger` along 5 dimensions. A Bayesian trust ledger tracks per-agent accuracy across sessions.

**Shadow Mind** — An optional parallel cognitive layer. Six components (Observer, Pattern Computer, Speculator, Dreamer, Pattern Library, Intuition Oracle) run alongside the conscious team, providing probabilistic pattern-based guidance via `[NEXUS:INTUIT]`. Delete `.claude/agent-memory/shadow-mind/` to disable. [Full spec](.claude/agent-memory/shadow-mind/README.md).

**Contract Tests** — 341 assertions across 11 contracts validate every agent file. A pre-commit hook runs them automatically.

```bash
python3 .claude/tests/agents/run_contract_tests.py
```

### Team Documentation

| | |
|---|---|
| [Team Overview](.claude/docs/team/TEAM_OVERVIEW.md) | Architecture and capabilities |
| [Cheatsheet](.claude/docs/team/TEAM_CHEATSHEET.md) | Quick reference for dispatch patterns |
| [Runbook](.claude/docs/team/TEAM_RUNBOOK.md) | Operational procedures |
| [Scenarios](.claude/docs/team/TEAM_SCENARIOS.md) | Real-world walkthrough examples |
| [Agent Template](.claude/docs/team/AGENT_TEMPLATE.md) | Create new specialist agents |

---

## Architecture

### Request Lifecycle (10 Stages)

Every `/v1/messages` request flows through a precisely engineered pipeline:

```
 1. INGRESS          FastAPI + ASGI (api/app.py, api/routes.py)
        |
 2. AUTH             Constant-time token comparison, 3 header formats
        |                (api/dependencies.py)
 3. VALIDATION       Pydantic models with extra="allow" for forward-compat
        |                (api/models/anthropic.py)
 4. MIDDLEWARE        Failover -> Cache -> Logger -> Cost Tracker
        |                (middleware/*.py)
 5. OPTIMIZATION     5 fast-path handlers intercept trivial requests locally
        |                (api/optimization_handlers.py)
 6. MODEL ROUTING    Claude model name -> provider_id/model_name resolution
        |                (api/model_router.py, config/settings.py)
 7. CONVERSION       Anthropic -> OpenAI chat (NIM) or native passthrough (5 others)
        |                (core/anthropic/conversion.py, core/anthropic/native_messages_request.py)
 8. UPSTREAM         Rate-limited, retried provider call with 3-tier protection
        |                (providers/openai_compat.py, providers/anthropic_messages.py)
 9. STREAMING        SSE event generation with thinking/tool/text block handling
        |                (core/anthropic/sse.py, core/anthropic/thinking.py, core/anthropic/tools.py)
10. DELIVERY         StreamingResponse with anti-buffering headers
                         (api/services.py)
```

### Dual Transport Architecture

HCC handles two fundamentally different provider protocols through a shared base:

| Transport | Provider | How It Works |
|-----------|----------|-------------|
| **OpenAI Chat Translation** | NVIDIA NIM | Converts Anthropic messages to OpenAI chat format. `ThinkTagParser` extracts `<think>` blocks from text. `HeuristicToolParser` detects tool calls in plain text. Full SSE reconstruction. |
| **Native Anthropic Messages** | OpenRouter, DeepSeek, LM Studio, llama.cpp, Ollama | Near-transparent passthrough. Sanitizes thinking history, filters hidden blocks, tracks emitted SSE state for error recovery. |

Both transports share `BaseProvider` and produce identical Anthropic-compatible SSE output.

### Three-Tier Rate Limiting

Every provider is protected by three independent rate limiting mechanisms:

| Tier | Mechanism | Purpose |
|------|-----------|---------|
| **Proactive** | `StrictSlidingWindowLimiter` | Prevents exceeding known rate limits before they trigger |
| **Reactive** | 429 response detection + exponential backoff | Reacts to actual provider rate limit responses |
| **Concurrency** | `asyncio.Semaphore` | Caps simultaneous in-flight requests per provider |

### Security Architecture

| Layer | Protection |
|-------|-----------|
| **Auth** | Constant-time comparison via `secrets.compare_digest` (CWE-208). CORS restricted to localhost. |
| **SSRF** | Cloud metadata IP blocklist (AWS, Azure, GCP, Alibaba). DNS rebinding protection via pinned resolution. Private network blocking. |
| **Input** | Pydantic validation on all request bodies. Scheme allowlisting on web tools. |
| **Output** | Sensitive log redaction by default. 6 `LOG_RAW_*` flags all default OFF. |
| **Process** | CLI sessions use `create_subprocess_exec` (no shell injection). Atexit cleanup handler. |

### Key Engineering Decisions

- **Forward-compatible models** — `extra="allow"` on Pydantic models passes unknown Anthropic fields through untouched. New Claude API features work automatically.
- **Streaming-first** — All responses stream. The proxy never buffers complete responses. `X-Accel-Buffering: no` prevents reverse proxy interference.
- **Zero-overhead middleware** — Disabled plugins add exactly zero per-request cost. No conditional checks, no empty function calls.
- **AST-enforced import boundaries** — Contract tests use Python AST analysis to verify dependency direction. `core/` never imports `api/`. `providers/` never imports `messaging/`. Violations fail CI.
- **Mid-stream error recovery** — If a provider fails during streaming, the proxy closes open SSE blocks correctly before emitting the error, preventing Claude Code replay corruption.

---

## API Endpoints

All endpoints respect `ANTHROPIC_AUTH_TOKEN` when configured.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/messages` | Anthropic Messages API (proxied) |
| `POST` | `/v1/messages/count_tokens` | Token counting (proxied) |
| `GET` | `/v1/models` | Available model list |
| `GET` | `/v1/cost` | Cost summary — session / daily / monthly |
| `GET` | `/v1/cache/stats` | Cache hit rate and entry count |
| `POST` | `/v1/cache/clear` | Clear response cache |
| `GET` | `/v1/health/providers` | Circuit breaker status per provider |

---

## Discord & Telegram Bots

Run Claude Code sessions remotely. Stream progress. Branch conversations via replies.

> **Security:** The bot runs Claude Code with `--dangerously-skip-permissions` within `ALLOWED_DIR`. Restrict the directory scope and always configure allowlists.

<details>
<summary><b>Discord setup</b></summary>

```dotenv
MESSAGING_PLATFORM="discord"
DISCORD_BOT_TOKEN="your-discord-bot-token"
ALLOWED_DISCORD_CHANNELS="123456789"
CLAUDE_WORKSPACE="./agent_workspace"
ALLOWED_DIR="/path/to/your/projects"
```

Create the bot in the [Discord Developer Portal](https://discord.com/developers/applications). Enable Message Content Intent. Invite with read/send/history permissions.
</details>

<details>
<summary><b>Telegram setup</b></summary>

```dotenv
MESSAGING_PLATFORM="telegram"
TELEGRAM_BOT_TOKEN="123456789:ABC..."
ALLOWED_TELEGRAM_USER_ID="your-user-id"
CLAUDE_WORKSPACE="./agent_workspace"
ALLOWED_DIR="/path/to/your/projects"
```

Get a token from [@BotFather](https://t.me/BotFather). Get your user ID from [@userinfobot](https://t.me/userinfobot).
</details>

Bot commands: `/stop` (cancel task), `/clear` (reset sessions), `/stats` (session state).

### Voice Notes

Transcribe voice messages on Discord and Telegram via local Whisper or NVIDIA NIM:

```bash
uv sync --extra voice_local   # Local Whisper
uv sync --extra voice          # NVIDIA NIM
```

```dotenv
VOICE_NOTE_ENABLED=true
WHISPER_DEVICE="cpu"    # cpu | cuda | nvidia_nim
```

---

## Configuration

[`.env.example`](.env.example) is the canonical reference. Key groups:

<details>
<summary><b>Model Routing</b></summary>

```dotenv
MODEL="nvidia_nim/z-ai/glm4.7"     # Default model
MODEL_OPUS=                          # Override for Opus-tier requests
MODEL_SONNET=                        # Override for Sonnet-tier requests
MODEL_HAIKU=                         # Override for Haiku-tier requests
ENABLE_MODEL_THINKING=true           # Enable thinking/reasoning blocks
```
</details>

<details>
<summary><b>Middleware Feature Flags</b></summary>

```dotenv
ENABLE_MIDDLEWARE_PIPELINE=true      # Master switch
ENABLE_COST_TRACKING=false           # Cost intelligence
MAX_SESSION_COST_USD=                # Budget cap (empty = no limit)
ENABLE_RESPONSE_CACHE=false          # Response caching
CACHE_TTL_SECONDS=3600               # Cache lifetime
CACHE_MAX_ENTRIES=1000               # Max cached responses
ENABLE_PROVIDER_FAILOVER=false       # Circuit breaker + failover
FAILOVER_ERROR_THRESHOLD=0.5         # Error rate to trip breaker
FAILOVER_COOLDOWN_SECONDS=30         # Cooldown before retry
ENABLE_REQUEST_LOGGING=false         # SQLite request logging
STORAGE_DB_PATH="~/.fcc/hcc.db"     # Database path
```
</details>

<details>
<summary><b>Rate Limits & Timeouts</b></summary>

```dotenv
PROVIDER_RATE_LIMIT=1
PROVIDER_RATE_WINDOW=3
PROVIDER_MAX_CONCURRENCY=5
HTTP_READ_TIMEOUT=120
HTTP_CONNECT_TIMEOUT=10
```
</details>

<details>
<summary><b>Security & Diagnostics</b></summary>

```dotenv
ANTHROPIC_AUTH_TOKEN=                # API key for proxy access
LOG_RAW_API_PAYLOADS=false           # Exposes prompts — keep off
LOG_RAW_SSE_EVENTS=false
LOG_API_ERROR_TRACEBACKS=false
LOG_RAW_MESSAGING_CONTENT=false
LOG_RAW_CLI_DIAGNOSTICS=false
```
</details>

---

## Development

```text
hyper-claude-code/
  server.py              ASGI entry point
  api/                   FastAPI routes, services, routing, optimizations
  core/                  Anthropic protocol helpers, SSE, streaming
  providers/             6 provider transports, registry, rate limiting
  middleware/             Cost, cache, failover, logging plugins
  storage/               SQLite persistence
  messaging/             Discord/Telegram bots, voice, sessions
  cli/                   Entrypoints, Claude process management
  config/                Settings, provider catalog, logging
  tests/                 Unit, contract, and smoke tests
  .claude/               31-agent team, hooks, docs, Shadow Mind
```

```bash
uv run ruff format       # Format
uv run ruff check        # Lint
uv run ty check          # Type check
uv run pytest            # Test
```

### Extending

- **New provider:** Extend `OpenAIChatTransport` or `AnthropicMessagesTransport`, register in `config/provider_catalog.py` and `providers/registry.py`
- **New middleware:** Extend `middleware.Middleware`, add to pipeline in `api/runtime.py`
- **New bot platform:** Implement `MessagingPlatform` in `messaging/platforms/`
- **New agent:** Use the [agent template](.claude/docs/team/AGENT_TEMPLATE.md)

---

## Troubleshooting

<details>
<summary><b>Claude Code says "undefined input_tokens" or malformed response</b></summary>

- Set `ANTHROPIC_BASE_URL` to `http://localhost:8082` (not `/v1`)
- Check `server.log` for upstream errors
- Update to latest commit
</details>

<details>
<summary><b>llama.cpp or LM Studio returns HTTP 400</b></summary>

- Ensure the server supports `POST /v1/messages`
- Increase `--ctx-size` for Claude Code's large prompts
- Verify the base URL includes `/v1`
</details>

<details>
<summary><b>Provider disconnects during streaming</b></summary>

Reduce `PROVIDER_MAX_CONCURRENCY`, increase `HTTP_READ_TIMEOUT`, or enable failover to auto-switch providers.
</details>

<details>
<summary><b>Tool calls work on one model but not another</b></summary>

Tool support is model-dependent. Some models emit malformed tool JSON. Try another model or provider.
</details>

---

## Contributing

- Report bugs and feature requests in [Issues](https://github.com/asiflow/hyper-claude-code/issues)
- Keep changes small and covered by focused tests
- Run the full check sequence before opening a PR
- `except X, Y` syntax is valid Python 3.14 (PEP 758) — do not "fix" it

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built by [ASIFLOW.ai](https://asiflow.ai)**

</div>

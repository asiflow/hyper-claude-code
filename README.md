<div align="center">

# Hyper Claude Code

Use Claude Code CLI, VS Code, JetBrains ACP, or chat bots through your own Anthropic-compatible proxy — with intelligent middleware built in.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/python-3.14-3776ab.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json&style=for-the-badge)](https://github.com/astral-sh/uv)
[![Tested with Pytest](https://img.shields.io/badge/testing-Pytest-00c0ff.svg?style=for-the-badge)](https://github.com/asiflow/hyper-claude-code/actions/workflows/tests.yml)
[![Type checking: Ty](https://img.shields.io/badge/type%20checking-ty-ffcc00.svg?style=for-the-badge)](https://pypi.org/project/ty/)
[![Code style: Ruff](https://img.shields.io/badge/code%20formatting-ruff-f5a623.svg?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![Logging: Loguru](https://img.shields.io/badge/logging-loguru-4ecdc4.svg?style=for-the-badge)](https://github.com/Delgan/loguru)

Hyper Claude Code (HCC) routes Anthropic Messages API traffic from Claude Code to NVIDIA NIM, OpenRouter, DeepSeek, LM Studio, llama.cpp, or Ollama. It keeps Claude Code's client-side protocol stable while letting you choose free, paid, or local models.

[Quick Start](#quick-start) · [Intelligent Middleware](#intelligent-middleware-pipeline) · [Providers](#choose-a-provider) · [API Endpoints](#api-endpoints) · [Configuration](#configuration-reference) · [31-Agent Team](#31-agent-development-team) · [Development](#development)

</div>

<div align="center">
  <img src="pic.png" alt="Hyper Claude Code in action" width="700">
</div>

## What You Get

- **Drop-in proxy** for Claude Code's Anthropic API calls.
- **Six provider backends**: NVIDIA NIM, OpenRouter, DeepSeek, LM Studio, llama.cpp, and Ollama.
- **Per-model routing**: send Opus, Sonnet, Haiku, and fallback traffic to different providers.
- **Intelligent middleware pipeline**: cost tracking, response caching, provider failover, and request logging — all behind feature flags with zero overhead when off.
- **Streaming, tool use, reasoning/thinking block handling**, and local request optimizations.
- **Optional Discord or Telegram bot** wrapper for remote coding sessions.
- **Optional voice-note transcription** through local Whisper or NVIDIA NIM.

## Quick Start

### 1. Install Requirements

Install [Claude Code](https://github.com/anthropics/claude-code), then install `uv` and Python 3.14.

macOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv self update
uv python install 3.14
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv self update
uv python install 3.14
```

### 2. Clone And Configure

```bash
git clone https://github.com/asiflow/hyper-claude-code.git
cd hyper-claude-code
cp .env.example .env
```

PowerShell uses:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and choose one provider. For the default NVIDIA NIM path:

```dotenv
NVIDIA_NIM_API_KEY="nvapi-your-key"
MODEL="nvidia_nim/z-ai/glm4.7"
ANTHROPIC_AUTH_TOKEN="hcc"
```

Use any local secret for `ANTHROPIC_AUTH_TOKEN`; Claude Code will send the same value back to this proxy. Leave it empty only for local/private testing.

### 3. Start The Proxy

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

> **Security:** When binding to `0.0.0.0`, always set `ANTHROPIC_AUTH_TOKEN` to prevent unauthorized access from other machines on your network. For local-only use, omit `--host` to default to `127.0.0.1`.

Package install alternative:

```bash
uv tool install git+https://github.com/asiflow/hyper-claude-code.git
fcc-init
hyper-claude-code
```

`fcc-init` creates `~/.config/hyper-claude-code/.env` from the bundled template.

### 4. Run Claude Code

Point `ANTHROPIC_BASE_URL` at the proxy root. Do not append `/v1`.

PowerShell:

```powershell
$env:ANTHROPIC_AUTH_TOKEN="hcc"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; claude
```

Bash:

```bash
ANTHROPIC_AUTH_TOKEN="hcc" ANTHROPIC_BASE_URL="http://localhost:8082" claude
```

## Intelligent Middleware Pipeline

HCC is not just a proxy — it is an intelligent middleware platform. Four built-in plugins intercept every request and response, all behind feature flags with zero overhead when disabled.

### Cost Intelligence

Real-time per-request cost tracking with session, daily, and monthly aggregation. Set a hard budget cap with `MAX_SESSION_COST_USD` and the proxy returns HTTP 429 before you overspend.

```dotenv
ENABLE_COST_TRACKING=true
MAX_SESSION_COST_USD=5.00
```

### Response Caching

SHA-256 exact-match caching for non-streaming requests with configurable TTL and max entries. Identical prompts return instantly from the local SQLite cache.

```dotenv
ENABLE_RESPONSE_CACHE=true
CACHE_TTL_SECONDS=3600
CACHE_MAX_ENTRIES=1000
```

### Provider Failover

Circuit breaker pattern with configurable error thresholds and cooldown windows. Define failover chains so traffic automatically reroutes when a provider goes down.

```dotenv
ENABLE_PROVIDER_FAILOVER=true
FAILOVER_ERROR_THRESHOLD=0.5
FAILOVER_WINDOW_SIZE=10
FAILOVER_COOLDOWN_SECONDS=30
```

### Request Logging

Every request is logged to a local SQLite database with model, provider, token counts, latency, and cost metadata — useful for auditing and debugging.

```dotenv
ENABLE_REQUEST_LOGGING=true
STORAGE_DB_PATH="~/.fcc/hcc.db"
```

## Choose A Provider

Model values use this format:

```text
provider_id/model/name
```

`MODEL` is the fallback. `MODEL_OPUS`, `MODEL_SONNET`, and `MODEL_HAIKU` override routing for requests that Claude Code sends for those tiers.

| Provider | Prefix | Transport | Key | Default base URL |
| --- | --- | --- | --- | --- |
| NVIDIA NIM | `nvidia_nim/...` | OpenAI chat translation | `NVIDIA_NIM_API_KEY` | `https://integrate.api.nvidia.com/v1` |
| OpenRouter | `open_router/...` | Anthropic Messages | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1` |
| DeepSeek | `deepseek/...` | Anthropic Messages | `DEEPSEEK_API_KEY` | `https://api.deepseek.com/anthropic` |
| LM Studio | `lmstudio/...` | Anthropic Messages | none | `http://localhost:1234/v1` |
| llama.cpp | `llamacpp/...` | Anthropic Messages | none | `http://localhost:8080/v1` |
| Ollama | `ollama/...` | Anthropic Messages | none | `http://localhost:11434` |

<details>
<summary><b>NVIDIA NIM</b></summary>

Get a key at [build.nvidia.com/settings/api-keys](https://build.nvidia.com/settings/api-keys).

```dotenv
NVIDIA_NIM_API_KEY="nvapi-your-key"
MODEL="nvidia_nim/z-ai/glm4.7"
```

Popular examples:

- `nvidia_nim/z-ai/glm4.7`
- `nvidia_nim/z-ai/glm5`
- `nvidia_nim/moonshotai/kimi-k2.5`
- `nvidia_nim/minimaxai/minimax-m2.5`

Browse models at [build.nvidia.com](https://build.nvidia.com/explore/discover). A cached model list is also kept in [`nvidia_nim_models.json`](nvidia_nim_models.json).

</details>

<details>
<summary><b>OpenRouter</b></summary>

Get a key at [openrouter.ai/keys](https://openrouter.ai/keys).

```dotenv
OPENROUTER_API_KEY="sk-or-your-key"
MODEL="open_router/stepfun/step-3.5-flash:free"
```

Browse [all models](https://openrouter.ai/models) or [free models](https://openrouter.ai/collections/free-models).

</details>

<details>
<summary><b>DeepSeek</b></summary>

Get a key at [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys).

```dotenv
DEEPSEEK_API_KEY="your-deepseek-key"
MODEL="deepseek/deepseek-chat"
```

This provider uses DeepSeek's Anthropic-compatible endpoint, not the OpenAI chat-completions endpoint.

</details>

<details>
<summary><b>LM Studio</b></summary>

Start LM Studio's local server, load a model, then configure:

```dotenv
LM_STUDIO_BASE_URL="http://localhost:1234/v1"
MODEL="lmstudio/your-loaded-model"
```

Use the model identifier shown by LM Studio. Prefer models with tool-use support for Claude Code workflows.

</details>

<details>
<summary><b>llama.cpp</b></summary>

Start `llama-server` with an Anthropic-compatible `/v1/messages` endpoint and enough context for Claude Code requests.

```dotenv
LLAMACPP_BASE_URL="http://localhost:8080/v1"
MODEL="llamacpp/local-model"
```

For local coding models, context size matters. If llama.cpp returns HTTP 400 for normal Claude Code requests, increase `--ctx-size` and verify the model/server build supports the requested features.

</details>

<details>
<summary><b>Ollama</b></summary>

Run Ollama and pull a model:

```bash
ollama pull llama3.1
ollama serve
```

Then configure the proxy. `OLLAMA_BASE_URL` is the Ollama server root; do not append `/v1`.

```dotenv
OLLAMA_BASE_URL="http://localhost:11434"
MODEL="ollama/llama3.1"
```

Use the same tag shown by `ollama list`, for example `ollama/llama3.1:8b`.

</details>

<details>
<summary><b>Mix providers by model tier</b></summary>

Each tier can use a different provider:

```dotenv
NVIDIA_NIM_API_KEY="nvapi-your-key"
OPENROUTER_API_KEY="sk-or-your-key"

MODEL_OPUS="nvidia_nim/moonshotai/kimi-k2.5"
MODEL_SONNET="open_router/deepseek/deepseek-r1-0528:free"
MODEL_HAIKU="lmstudio/unsloth/GLM-4.7-Flash-GGUF"
MODEL="nvidia_nim/z-ai/glm4.7"
```

</details>

## API Endpoints

HCC exposes management endpoints alongside the standard Anthropic-compatible routes. All endpoints respect `ANTHROPIC_AUTH_TOKEN` when set.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/v1/cost` | Session, daily, and monthly cost summaries with budget remaining |
| `GET` | `/v1/cache/stats` | Cache hit/miss counts, hit rate, and entry count |
| `POST` | `/v1/cache/clear` | Clear all cached responses |
| `GET` | `/v1/health/providers` | Circuit breaker status for all tracked providers |
| `POST` | `/v1/messages` | Anthropic Messages API (proxied to provider) |
| `POST` | `/v1/messages/count_tokens` | Token counting (proxied to provider) |
| `GET` | `/v1/models` | Available model list |

## Connect Claude Code

### Claude Code CLI

```bash
ANTHROPIC_AUTH_TOKEN="hcc" ANTHROPIC_BASE_URL="http://localhost:8082" claude
```

### VS Code Extension

Open Settings, search for `claude-code.environmentVariables`, choose **Edit in settings.json**, and add:

```json
"claudeCode.environmentVariables": [
  { "name": "ANTHROPIC_BASE_URL", "value": "http://localhost:8082" },
  { "name": "ANTHROPIC_AUTH_TOKEN", "value": "hcc" }
]
```

Reload the extension. If the extension shows a login screen, choose the Anthropic Console path once; the local proxy still handles model traffic after the environment variables are active.

### JetBrains ACP

Edit the installed Claude ACP config:

- Windows: `C:\Users\%USERNAME%\AppData\Roaming\JetBrains\acp-agents\installed.json`
- Linux/macOS: `~/.jetbrains/acp.json`

Set the environment for `acp.registry.claude-acp`:

```json
"env": {
  "ANTHROPIC_BASE_URL": "http://localhost:8082",
  "ANTHROPIC_AUTH_TOKEN": "hcc"
}
```

Restart the IDE after changing the file.

### Model Picker

`claude-pick` lets you choose a model at launch time.

```bash
brew install fzf
alias claude-pick="/absolute/path/to/hyper-claude-code/claude-pick"
claude-pick
```

You can also create fixed aliases:

```bash
alias claude-kimi='ANTHROPIC_BASE_URL="http://localhost:8082" ANTHROPIC_AUTH_TOKEN="hcc:moonshotai/kimi-k2.5" claude'
```

## Optional Integrations

### Discord And Telegram Bots

The bot wrapper runs Claude Code sessions remotely, streams progress, supports reply-based conversation branches, and can stop or clear tasks.

> **Security:** The bot runs Claude Code with `--dangerously-skip-permissions` within `ALLOWED_DIR`, meaning all file and tool operations execute without interactive confirmation. Restrict `ALLOWED_DIR` to the minimum necessary directory and always configure channel/user allowlists.

Discord minimum config:

```dotenv
MESSAGING_PLATFORM="discord"
DISCORD_BOT_TOKEN="your-discord-bot-token"
ALLOWED_DISCORD_CHANNELS="123456789"
CLAUDE_WORKSPACE="./agent_workspace"
ALLOWED_DIR="C:/Users/yourname/projects"
```

Create the bot in the [Discord Developer Portal](https://discord.com/developers/applications), enable Message Content Intent, and invite it with read/send/history permissions.

Telegram minimum config:

```dotenv
MESSAGING_PLATFORM="telegram"
TELEGRAM_BOT_TOKEN="123456789:ABC..."
ALLOWED_TELEGRAM_USER_ID="your-user-id"
CLAUDE_WORKSPACE="./agent_workspace"
ALLOWED_DIR="C:/Users/yourname/projects"
```

Get a token from [@BotFather](https://t.me/BotFather) and your user ID from [@userinfobot](https://t.me/userinfobot).

Useful commands:

- `/stop` cancels a task; reply to a task message to stop only that branch.
- `/clear` resets sessions; reply to clear one branch.
- `/stats` shows session state.

### Voice Notes

Voice notes work on Discord and Telegram. Choose one backend:

```bash
uv sync --extra voice_local
uv sync --extra voice
uv sync --extra voice --extra voice_local
```

```dotenv
VOICE_NOTE_ENABLED=true
WHISPER_DEVICE="cpu"          # cpu | cuda | nvidia_nim
WHISPER_MODEL="base"
HF_TOKEN=""
```

Use `WHISPER_DEVICE="nvidia_nim"` with the `voice` extra and `NVIDIA_NIM_API_KEY` for NVIDIA-hosted transcription.

## Configuration Reference

[`.env.example`](.env.example) is the canonical list of variables. The sections below are the ones most users change.

### Model Routing

```dotenv
MODEL="nvidia_nim/z-ai/glm4.7"
MODEL_OPUS=
MODEL_SONNET=
MODEL_HAIKU=
ENABLE_MODEL_THINKING=true
ENABLE_OPUS_THINKING=
ENABLE_SONNET_THINKING=
ENABLE_HAIKU_THINKING=
```

Blank per-tier values inherit the fallback. Blank thinking overrides inherit `ENABLE_MODEL_THINKING`.

### Provider Keys And URLs

```dotenv
NVIDIA_NIM_API_KEY=""
OPENROUTER_API_KEY=""
DEEPSEEK_API_KEY=""
LM_STUDIO_BASE_URL="http://localhost:1234/v1"
LLAMACPP_BASE_URL="http://localhost:8080/v1"
OLLAMA_BASE_URL="http://localhost:11434"
```

Proxy settings are per provider:

```dotenv
NVIDIA_NIM_PROXY=""
OPENROUTER_PROXY=""
LMSTUDIO_PROXY=""
LLAMACPP_PROXY=""
```

### Feature Flags

All middleware plugins are disabled by default and add zero overhead when off. Enable what you need:

```dotenv
# Middleware pipeline (master switch — must be true for any plugin to run)
ENABLE_MIDDLEWARE_PIPELINE=true

# Cost Intelligence
ENABLE_COST_TRACKING=false
MAX_SESSION_COST_USD=

# Response Caching
ENABLE_RESPONSE_CACHE=false
CACHE_TTL_SECONDS=3600
CACHE_MAX_ENTRIES=1000

# Provider Failover
ENABLE_PROVIDER_FAILOVER=false
FAILOVER_ERROR_THRESHOLD=0.5
FAILOVER_WINDOW_SIZE=10
FAILOVER_COOLDOWN_SECONDS=30

# Request Logging
ENABLE_REQUEST_LOGGING=false
STORAGE_DB_PATH="~/.fcc/hcc.db"

# Request optimizations (all on by default)
ENABLE_NETWORK_PROBE_MOCK=true
ENABLE_TITLE_GENERATION_SKIP=true
ENABLE_SUGGESTION_MODE_SKIP=true
ENABLE_FILEPATH_EXTRACTION_MOCK=true
```

### Rate Limits And Timeouts

```dotenv
PROVIDER_RATE_LIMIT=1
PROVIDER_RATE_WINDOW=3
PROVIDER_MAX_CONCURRENCY=5
HTTP_READ_TIMEOUT=120
HTTP_WRITE_TIMEOUT=10
HTTP_CONNECT_TIMEOUT=10
```

Use lower limits for free hosted providers; local providers can usually tolerate higher concurrency if the machine can handle it.

### Security And Diagnostics

```dotenv
ANTHROPIC_AUTH_TOKEN=
LOG_RAW_API_PAYLOADS=false
LOG_RAW_SSE_EVENTS=false
LOG_API_ERROR_TRACEBACKS=false
LOG_RAW_MESSAGING_CONTENT=false
LOG_RAW_CLI_DIAGNOSTICS=false
LOG_MESSAGING_ERROR_DETAILS=false
```

Raw logging flags can expose prompts, tool arguments, paths, and model output. Keep them off unless you are debugging locally.

### Local Web Tools

```dotenv
ENABLE_WEB_SERVER_TOOLS=true
WEB_FETCH_ALLOWED_SCHEMES=http,https
WEB_FETCH_ALLOW_PRIVATE_NETWORKS=false
```

These tools perform outbound HTTP from the proxy. Keep private-network access disabled unless you are in a controlled lab environment.

## 31-Agent Development Team

HCC ships with a CTO-led 31-agent engineering team (29 specialists + 2 verifiers) in `.claude/`. The team is a layered operating system built on Claude Code, designed for complex multi-service, multi-language work.

**Activate the full team:**

```
Say "full team session" to Claude Code while in this repository.
```

The CTO agent assesses your request, delegates to specialist agents, gates findings through an evidence validator, and synthesizes results.

### Agent Roster

| Tier | Agents | Role |
| --- | --- | --- |
| **Builders** | `elite-engineer`, `ai-platform-architect`, `frontend-platform-engineer`, `beam-architect`, `elixir-engineer`, `go-hybrid-engineer` | Write production code |
| **Guardians** | `go-expert`, `python-expert`, `typescript-expert`, `deep-qa`, `deep-reviewer`, `infra-expert`, `database-expert`, `observability-expert`, `test-engineer`, `api-expert`, `beam-sre` | Review, audit, rarely write app code |
| **Strategists** | `deep-planner`, `orchestrator` | Task decomposition and workflow execution |
| **Intelligence** | `memory-coordinator`, `cluster-awareness`, `benchmark-agent`, `erlang-solutions-consultant`, `talent-scout`, `intuition-oracle` | Cross-agent knowledge, live state, competitive intel |
| **Meta-Cognitive** | `meta-agent`, `recruiter` | Prompt evolution and dynamic specialist hiring |
| **Governance** | `session-sentinel` | Protocol compliance and team health audits |
| **CTO** | `cto` | Supreme technical authority — dispatches, delegates, debates, self-evolves |
| **Verification** | `evidence-validator`, `challenger` | Claim verification and adversarial review |

### NEXUS Protocol

Subagents in Claude Code cannot spawn other agents or access privileged tools. NEXUS solves this with a syscall interface: agents send `[NEXUS:SPAWN]`, `[NEXUS:SCALE]`, `[NEXUS:ASK]`, etc. via `SendMessage` to the main thread, which executes the privileged operation and responds. This enables real-time multi-agent coordination without breaking the Claude Code privilege boundary.

### Trust Infrastructure

- **Evidence Validator** — every HIGH-severity finding is verified against source code before reaching the user. Findings are classified as CONFIRMED, PARTIALLY_CONFIRMED, REFUTED, or UNVERIFIABLE.
- **Challenger** — adversarial review of every CTO synthesis and strategic recommendation along 5 dimensions: steelman alternatives, hidden assumptions, evidence quality, missed cases, downstream impact.
- **Trust Ledger** — Bayesian-blended per-agent accuracy scorecard at `.claude/agent-memory/trust-ledger/`. The CTO uses trust weights to resolve conflicting findings.

### Shadow Mind

An optional parallel cognitive layer that runs alongside the conscious team. Six components — Observer daemon, Pattern Computer, Speculator, Dreamer, Pattern Library, and `intuition-oracle` — provide probabilistic pattern-based guidance via `[NEXUS:INTUIT]`. Delete `.claude/agent-memory/shadow-mind/` to disable without affecting the team. Full spec at [`.claude/agent-memory/shadow-mind/README.md`](.claude/agent-memory/shadow-mind/README.md).

### Contract Tests

341 assertions (11 contracts across 31 agents) validate every agent file. Run them with:

```bash
python3 .claude/tests/agents/run_contract_tests.py
```

A pre-commit hook runs these automatically on staged agent edits.

### Team Documentation

| Document | Path |
| --- | --- |
| Architecture and capabilities | [`.claude/docs/team/TEAM_OVERVIEW.md`](.claude/docs/team/TEAM_OVERVIEW.md) |
| Quick reference cheatsheet | [`.claude/docs/team/TEAM_CHEATSHEET.md`](.claude/docs/team/TEAM_CHEATSHEET.md) |
| Operational runbook | [`.claude/docs/team/TEAM_RUNBOOK.md`](.claude/docs/team/TEAM_RUNBOOK.md) |
| Real-world scenario walkthroughs | [`.claude/docs/team/TEAM_SCENARIOS.md`](.claude/docs/team/TEAM_SCENARIOS.md) |
| Agent template for new specialists | [`.claude/docs/team/AGENT_TEMPLATE.md`](.claude/docs/team/AGENT_TEMPLATE.md) |

## How It Works

```text
Claude Code CLI / IDE
        |
        | Anthropic Messages API
        v
Hyper Claude Code proxy (:8082)
        |
        | middleware pipeline (cost, cache, failover, logging)
        |
        | provider-specific request/stream adapter
        v
NIM / OpenRouter / DeepSeek / LM Studio / llama.cpp / Ollama
```

Important pieces:

- FastAPI exposes Anthropic-compatible routes such as `/v1/messages`, `/v1/messages/count_tokens`, and `/v1/models`.
- Model routing resolves the Claude model name to `MODEL_OPUS`, `MODEL_SONNET`, `MODEL_HAIKU`, or `MODEL`.
- NIM uses OpenAI chat streaming translated into Anthropic SSE.
- OpenRouter, DeepSeek, LM Studio, llama.cpp, and Ollama use Anthropic Messages style transports.
- The proxy normalizes thinking blocks, tool calls, token usage metadata, and provider errors into the shape Claude Code expects.
- Request optimizations answer trivial Claude Code probes locally to save latency and quota.
- The middleware pipeline intercepts requests for cost tracking, caching, failover, and logging before they reach the provider.

## Development

### Project Structure

```text
hyper-claude-code/
├── server.py              # ASGI entry point
├── api/                   # FastAPI routes, service layer, routing, optimizations
├── core/                  # Shared Anthropic protocol helpers and SSE utilities
├── providers/             # Provider transports, registry, rate limiting
├── middleware/             # Cost tracking, caching, failover, request logging
├── storage/               # SQLite-backed persistence for middleware state
├── messaging/             # Discord/Telegram adapters, sessions, voice
├── cli/                   # Package entry points and Claude process management
├── config/                # Settings, provider catalog, logging
├── tests/                 # Unit and contract tests
└── .claude/               # 31-agent team prompts, hooks, and contract tests
```

### Commands

```bash
uv run ruff format
uv run ruff check
uv run ty check
uv run pytest
```

Run them in that order before pushing. CI enforces the same checks.

### Package Scripts

`pyproject.toml` installs:

- `hyper-claude-code`: starts the proxy with configured host and port.
- `fcc-init`: creates the user config template at `~/.config/hyper-claude-code/.env`.

### Extending

- Add OpenAI-compatible providers by extending `OpenAIChatTransport`.
- Add Anthropic Messages providers by extending `AnthropicMessagesTransport`.
- Register provider metadata in `config.provider_catalog` and factory wiring in `providers.registry`.
- Add messaging platforms by implementing the `MessagingPlatform` interface in `messaging/`.

## Troubleshooting

### Claude Code says `undefined ... input_tokens`, `$.speed`, or malformed response

Update to the latest commit first. Older versions could emit invalid usage metadata in streaming responses. Then check:

- `ANTHROPIC_BASE_URL` is `http://localhost:8082`, not `http://localhost:8082/v1`.
- The proxy is returning Server-Sent Events for `/v1/messages`.
- `server.log` contains no upstream 400/500 response before the malformed-response error.

### llama.cpp or LM Studio returns HTTP 400

This usually means the local runtime rejected the Anthropic Messages request before the proxy could stream a model answer.

Check:

- The local server supports `POST /v1/messages`.
- The model and runtime support the requested context length and tools.
- llama.cpp was started with enough `--ctx-size` for Claude Code prompts.
- The configured base URL includes `/v1` for LM Studio and llama.cpp.

### Provider disconnects during streaming

Errors like `incomplete chunked read`, `server disconnected`, or a peer closing the body usually come from the upstream provider or gateway. Reduce concurrency, raise timeouts, or retry later.

### Tool calls work on one model but not another

Tool support is model and provider dependent. Some OpenAI-compatible models emit malformed tool-call deltas, omit tool names, or return tool calls as plain text. Try another model or provider before assuming the proxy is broken.

### The VS Code extension still shows a login screen

Confirm the extension environment variables are set, then reload the extension or restart VS Code. The browser login flow may still appear once; the local proxy is used when `ANTHROPIC_BASE_URL` is active in the extension process.

## Contributing

- Report bugs and feature requests in [Issues](https://github.com/asiflow/hyper-claude-code/issues).
- Keep changes small and covered by focused tests.
- Do not open Docker integration PRs.
- Do not open README change PRs just open an issue for it.
- Run the full check sequence before opening a pull request.
- The syntax Except X, Y is brought back in python 3.14 final version (not in 3.14 alpha). Keep in mind before opening PRs.

## License

MIT License. See [LICENSE](LICENSE) for details.

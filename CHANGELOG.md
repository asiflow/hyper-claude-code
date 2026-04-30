# Changelog

All notable changes to Hyper Claude Code are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.0.0] - 2026-04-30

### Added

- **Middleware Pipeline** — extensible `before_request` / `after_response` plugin architecture with zero overhead when disabled
- **Cost Intelligence** — per-request cost tracking with session/daily/monthly aggregation and budget caps (`ENABLE_COST_TRACKING`, `MAX_SESSION_COST_USD`)
- **Response Caching** — SHA-256 exact-match caching with configurable TTL and LRU eviction (`ENABLE_RESPONSE_CACHE`, `CACHE_TTL_SECONDS`)
- **Provider Failover** — per-provider circuit breaker (CLOSED/OPEN/HALF_OPEN) with configurable failover chains (`ENABLE_PROVIDER_FAILOVER`)
- **Request Logging** — full audit trail to local SQLite (`ENABLE_REQUEST_LOGGING`)
- **4 new API endpoints** — `GET /v1/cost`, `GET /v1/cache/stats`, `POST /v1/cache/clear`, `GET /v1/health/providers`
- **13 feature flags** — all middleware capabilities toggleable via environment variables
- **31-agent development team** — CTO-led engineering team with NEXUS protocol, Shadow Mind, trust ledger, adversarial review, and dynamic specialist hiring
- **CORS middleware** — restrictive localhost-only origin policy
- **CLI auth forwarding** — proxy auth token propagated to CLI subprocesses
- `storage/` package — async SQLite persistence via aiosqlite
- `middleware/` package — base class, pipeline, and 4 built-in plugins
- SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md
- `docs/` directory with quickstart, security, providers, and architecture guides
- `examples/` directory with sample configurations
- docker-compose.yml for containerized deployment

### Changed

- Default host binding changed from `0.0.0.0` to `127.0.0.1` (security hardening)
- `.env.example` default auth token changed from `"freecc"` to empty string with generation instructions
- Route handlers `create_message` and `count_tokens` changed from `async def` to `def` (FastAPI threadpool handles sync handlers correctly, prevents event loop blocking from tiktoken)
- PEP 758 except style normalized — all multi-exception except clauses use bare-comma syntax
- All loguru calls converted from f-strings and printf-style to lazy `{}` formatting
- Colon-stripping auth behavior documented in code comments
- Rebranded from "Free Claude Code" to "Hyper Claude Code"

### Security

- Default host `127.0.0.1` prevents accidental network exposure
- CORS middleware blocks cross-origin requests from non-localhost origins
- CLI subprocess auth token forwarded correctly (previously used hardcoded passthrough)
- Security warnings added to README for `--host 0.0.0.0` and bot `--dangerously-skip-permissions`

---

## [1.0.0] - 2026-04-29

### Added

- Initial release as Free Claude Code
- Anthropic Messages API proxy with 6 provider backends
- NVIDIA NIM, OpenRouter, DeepSeek, LM Studio, llama.cpp, Ollama support
- Per-model routing (MODEL_OPUS, MODEL_SONNET, MODEL_HAIKU)
- SSE streaming with thinking block, tool use, and reasoning content handling
- Discord and Telegram bot adapters
- Voice note transcription (Whisper + NVIDIA NIM)
- Request optimization fast-path handlers
- Three-tier rate limiting (proactive + reactive + concurrency)
- SSRF protection with DNS pinning and metadata IP blocklist
- Comprehensive test suite (20K+ lines)
- AST-enforced import boundary contract tests

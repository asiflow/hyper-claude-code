# Security Architecture

Hyper Claude Code is an API proxy that handles authentication tokens and forwards requests to upstream LLM providers. This document covers the full security model.

## Threat Model

HCC is designed for **local and trusted-network deployment**. The primary threat scenarios:

| Scenario | Likelihood | Mitigation |
|----------|-----------|-----------|
| Same-network attacker discovers open proxy | High (if misconfigured) | Default `127.0.0.1` binding, auth required for `0.0.0.0` |
| Malicious browser tab makes cross-origin requests | Medium | CORS restricted to localhost, JSON POST triggers preflight |
| Upstream provider compromise | Low | API keys only in outbound headers, never in responses |
| Supply chain attack via dependency | Low | Minimal deps, lockfile pinning |

## Authentication

### Token Validation

```python
# api/dependencies.py
secrets.compare_digest(submitted_token, configured_token)
```

- **Constant-time comparison** prevents timing-based token enumeration (CWE-208)
- Supports three header formats: `x-api-key`, `Authorization: Bearer`, `anthropic-auth-token`
- Token colon-stripping supports Claude Code's `key:model` convention — effectively a prefix-match when tokens contain colons

### Default Configuration

| Setting | Default | Security Impact |
|---------|---------|----------------|
| `host` | `127.0.0.1` | Loopback only — not network-accessible |
| `ANTHROPIC_AUTH_TOKEN` | Empty | No auth when empty — runtime warns if combined with `0.0.0.0` |
| CORS origins | `localhost` + `127.0.0.1` | Only local origins allowed |

### Auth Bypass

When `ANTHROPIC_AUTH_TOKEN` is empty, all endpoints are unauthenticated. This is intentional for local-only use. The runtime emits a warning at startup when this is combined with `0.0.0.0` binding.

## SSRF Protection

The web tools subsystem (`api/web_tools/egress.py`) implements comprehensive SSRF defenses:

### IP Blocklist

```python
CLOUD_METADATA_ADDRS = {
    "169.254.169.254",      # AWS, GCP
    "fd00:ec2::254",        # AWS IPv6
    "168.63.129.16",        # Azure
    "100.100.100.200",      # Alibaba
}
```

### DNS Rebinding Protection

1. Resolve hostname to IP addresses
2. Validate ALL resolved IPs against blocklist (private, loopback, link-local, metadata)
3. Pin the resolved address for the actual connection (TOCTOU prevention)
4. Re-validate on each redirect hop

### Network Controls

| Control | Default | Config |
|---------|---------|--------|
| Private network access | Blocked | `WEB_FETCH_ALLOW_PRIVATE_NETWORKS=false` |
| Allowed schemes | `http`, `https` | `WEB_FETCH_ALLOWED_SCHEMES` |
| Response size cap | 2MB | Hardcoded |
| Output char cap | 24K | Hardcoded |
| Max redirects | 10 | Hardcoded |

## Input Validation

- All request bodies validated via Pydantic models with typed fields
- `extra="allow"` on request models for forward-compatibility (unknown fields pass through, not rejected)
- Settings validated at startup with migration guidance for removed environment variables
- Model name format validated before provider resolution

## Output Sanitization

### Log Redaction

All sensitive logging is disabled by default:

| Flag | Default | What It Logs |
|------|---------|-------------|
| `LOG_RAW_API_PAYLOADS` | `false` | Full request/response bodies |
| `LOG_RAW_SSE_EVENTS` | `false` | Raw SSE event content |
| `LOG_API_ERROR_TRACEBACKS` | `false` | Full stack traces |
| `LOG_RAW_MESSAGING_CONTENT` | `false` | Bot message content |
| `LOG_RAW_CLI_DIAGNOSTICS` | `false` | Claude CLI stderr |
| `LOG_MESSAGING_ERROR_DETAILS` | `false` | Messaging error context |

Telegram bot tokens and Authorization headers are redacted before log emission regardless of flag settings.

### Error Responses

Error handlers sanitize responses to prevent information leakage:
- Pydantic validation errors show field paths but not content values
- Provider errors are mapped to Anthropic-compatible error shapes
- Stack traces are not included unless `LOG_API_ERROR_TRACEBACKS=true`

## Process Security

### CLI Subprocess Isolation

- Subprocesses spawned via `asyncio.create_subprocess_exec` (argv-style, no shell injection)
- Each subprocess gets an isolated environment copy (`os.environ.copy()`)
- `atexit` handler ensures orphaned subprocesses are killed on proxy shutdown
- Process registry tracks all spawned PIDs for cleanup

### Bot Security

- Discord/Telegram bots run Claude Code with `--dangerously-skip-permissions` (required for non-interactive operation)
- `ALLOWED_DISCORD_CHANNELS` / `ALLOWED_TELEGRAM_USER_ID` enforced at startup AND per-message (defense-in-depth)
- Bot refuses to start without allowlist configuration
- `ALLOWED_DIR` constrains filesystem access scope

## Middleware Security

| Plugin | Security Consideration |
|--------|----------------------|
| Cost Tracker | Reads only token counts from response metadata — no PII exposure |
| Response Cache | Local SQLite, single-tenant — no cross-user leakage. SHA-256 keys are collision-resistant |
| Failover | Circuit breaker is in-memory, not externally manipulable. Error thresholds configured via env vars only |
| Request Logger | Logs metadata (model, tokens, latency) — not request/response content |

## Dependency Policy

- Minimal dependency footprint — `aiosqlite` is the only non-standard dependency added for middleware
- All dependencies pinned in `uv.lock`
- `pyproject.toml` specifies minimum versions, not exact pins
- Optional extras (`voice`, `voice_local`, `discord`, `telegram`) are isolated

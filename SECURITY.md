# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest `main` | Yes |
| Older commits | Best-effort |

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

Email **support@asiflow.ai** with:

- Description of the vulnerability
- Steps to reproduce
- Impact assessment
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide an initial assessment within 7 days.

## Security Architecture

Hyper Claude Code is an API proxy that handles authentication tokens and forwards requests to upstream LLM providers. The security model is designed for local/trusted-network deployment.

### Authentication

- API key comparison uses `secrets.compare_digest` for constant-time comparison (CWE-208 mitigation)
- Default binding is `127.0.0.1` (loopback only) — network exposure requires explicit `--host 0.0.0.0`
- Runtime warns at startup when auth is disabled + host is `0.0.0.0`
- CORS restricted to localhost origins via anchored regex

### SSRF Protection

- Cloud metadata IP blocklist (AWS 169.254.169.254, Azure, GCP, Alibaba)
- DNS rebinding protection via pinned address resolution
- Private network and loopback blocking by default
- URL scheme allowlisting (http/https only)
- Per-hop DNS re-validation on redirects

### Data Handling

- Upstream API keys flow only in outbound request headers — never in responses to clients
- All `LOG_RAW_*` flags default to OFF — sensitive data is not logged unless explicitly enabled
- Response cache is local SQLite — single-tenant, no cross-user leakage
- No telemetry, no analytics, no data sent to third parties

### Process Isolation

- CLI subprocesses use `asyncio.create_subprocess_exec` (no shell injection)
- `atexit` handler ensures subprocess cleanup
- Subprocess environments are isolated copies (`os.environ.copy()`)

### Bot Security

- Discord/Telegram bots run Claude Code with `--dangerously-skip-permissions` within `ALLOWED_DIR`
- Channel/user allowlists are enforced at both startup and per-message
- Restrict `ALLOWED_DIR` to the minimum necessary directory

For the full security architecture, see [docs/security.md](docs/security.md).

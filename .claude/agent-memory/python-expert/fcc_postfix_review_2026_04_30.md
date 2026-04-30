---
name: FCC Post-Fix Review 2026-04-30
description: Review of 3 fix tracks (async handlers, PEP 758 except, logger cleanup) — 6 missed logger conversions found
type: project
---

Post-fix review of elite-engineer remediation (FIX 1, FIX 3, FIX 4).

**FIX 1 (async handlers) — PASS.** `create_message` and `count_tokens` in `api/routes.py` correctly converted to sync `def`. No `await` calls in handler bodies or in `ClaudeProxyService` methods. FastAPI threadpool dispatch is correct.

**FIX 3 (PEP 758 except) — PASS.** All 8 sites verified semantically equivalent. Project targets Python 3.14.

**FIX 4 (logger cleanup) — PARTIAL PASS.** 6 sites missed:
- `messaging/limiter.py:73,106,227` — f-string loggers (eager evaluation)
- `core/anthropic/tokens.py:93-96` — `%r` printf-style (Loguru ignores `%r`, arg silently dropped)
- `cli/process_registry.py:66,74` — `%s` printf-style (same issue)

**Why:** The `%r` and `%s` issues are silent bugs — Loguru does not process printf-style placeholders, so the arguments are passed but never interpolated into the log message. The f-string calls are a performance anti-pattern (eager evaluation even when log level disabled).

**How to apply:** When reviewing future logger cleanups, verify with `rg 'logger\.\w+\(f' *.py` and `rg 'logger\.\w+\(.*%[srdf]' *.py` after the batch.

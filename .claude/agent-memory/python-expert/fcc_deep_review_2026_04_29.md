---
name: FCC Deep Python Review 2026-04-30
description: Comprehensive Python review -- except-comma syntax bug (8 sites), blocking DNS in egress.py, threading.Lock in async SessionStore, lru_cache non-invalidable, f-string in logger calls
type: project
---

## Key Findings (2026-04-30 refresh)

1. **CRITICAL: `except Type, Type` syntax** -- 8 occurrences across 5 files use Python 2 bare-comma except syntax instead of `except (Type, Type)`. In Python 3, `except A, B:` assigns the exception to variable `B` -- it does NOT catch both types. Files: openai_compat.py:271,373, tokens.py:99, discord_markdown.py:171,178, telegram_markdown.py:179,186, discord.py:408,481.

2. **HIGH: Blocking `socket.getaddrinfo` in async context** -- `egress.py:41` calls synchronous `socket.getaddrinfo` (DNS resolution can block for seconds). `outbound.py:239` wraps egress in `asyncio.to_thread` but `enforce_web_fetch_egress` at egress.py:127 calls the blocking function directly.

3. **HIGH: `SessionStore` uses `threading.Lock` in async application** -- session.py:35 uses `threading.Lock` which can block the event loop when contended. Should use `asyncio.Lock` or `asyncio.to_thread` wrapper.

4. **MEDIUM: f-string in loguru logger calls** -- Multiple files use f-strings instead of loguru's `{}` placeholders (e.g., rate_limit.py:64,139,165, telegram.py:179,185,244,261,520, session.py:139,245,249,272,311). This defeats loguru's lazy formatting and structured logging.

5. **LOW: `lru_cache` on `get_settings()` is not invalidable** -- settings.py:483 process-wide singleton cannot be reset for testing without clearing the cache.

6. **FIXED since last review:** `asyncio.get_event_loop()` calls removed. `BaseProvider.stream_response` now uses `TYPE_CHECKING` guard for proper typing.

## How to apply
- Finding 1 is a runtime correctness bug -- fix immediately
- Finding 2-3 are async hygiene issues that matter under load
- Finding 4 is a logging best practice issue
- Finding 5 is tech debt for testability

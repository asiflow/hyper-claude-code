---
name: FCC Sync-in-Async Hotspot Map 2026-04-30
description: Complete mapping of all sync-in-async hotspots in FCC codebase — token counting, SessionStore file I/O, tempfile creation, except-comma syntax bugs, f-string logger pattern
type: project
---

Complete sync-in-async hotspot mapping performed 2026-04-30.

**HIGH findings:**
1. `api/services.py:113` — `create_message` is a sync method calling CPU-bound tiktoken (`get_token_count`) on event loop. Called from async route handler at `api/routes.py:86`.
2. `core/anthropic/tokens.py:99` — `except TypeError, ValueError` Python 2 syntax bug (also at 5 other sites in telegram_markdown.py, discord_markdown.py).
3. `messaging/session.py` — `save_tree`, `record_message_id`, `register_node` are sync methods with `threading.Lock` called from async handlers; I/O-bound `_write_data` (json.dump + fsync) happens inside timer thread — correctly offloaded, but lock contention is a latent risk.

**MEDIUM findings:**
4. `messaging/platforms/discord.py:210` and `telegram.py:640` — `tempfile.NamedTemporaryFile` is a sync syscall in async voice handlers.
5. f-string logger anti-pattern at 30+ sites across messaging, cli, providers — forces eager string formatting.

**DOWNGRADED (correctly handled):**
- `socket.getaddrinfo` in `egress.py:41` — production caller wraps in `asyncio.to_thread` at `outbound.py:239`.
- `threading.Lock` in `SessionStore` — intentionally correct for cross-thread timer safety.
- Voice transcription — correctly uses `asyncio.to_thread` at `voice.py:68`.

**How to apply:** When reviewing Python changes in this codebase, check for sync calls inside `async def` functions, especially in the hot request path (services.py → routes.py → tokens.py).

# Contributing to Hyper Claude Code

Thank you for your interest in contributing! This guide covers the process for submitting changes.

## Getting Started

```bash
git clone https://github.com/asiflow/hyper-claude-code.git
cd hyper-claude-code
cp .env.example .env
uv sync --all-extras
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow the existing code patterns:
- Python 3.14 — `except A, B:` is valid PEP 758 syntax, do not "fix" it
- Loguru for logging — use lazy formatting: `logger.info("msg {}", var)`, not f-strings
- Pydantic for models and settings
- FastAPI for routes
- `async def` only when the function body uses `await`

### 3. Run Checks

```bash
uv run ruff format        # Format code
uv run ruff check         # Lint
uv run ty check           # Type check
uv run pytest             # Run tests
```

All four must pass before submitting a PR. CI enforces the same checks.

### 4. Agent Contract Tests

If you modified any file in `.claude/agents/`:

```bash
python3 .claude/tests/agents/run_contract_tests.py
```

All 341 assertions must pass. The pre-commit hook runs this automatically.

### 5. Submit a PR

- Keep PRs focused — one feature or fix per PR
- Write a clear description of what and why
- Reference any related issues

## What to Contribute

### Welcome

- Bug fixes with tests
- New provider integrations (extend `OpenAIChatTransport` or `AnthropicMessagesTransport`)
- New middleware plugins
- Test coverage improvements
- Documentation improvements (open an issue first)
- Performance optimizations with benchmarks

### Please Open an Issue First

- New features or major changes — discuss before building
- README changes — open an issue, do not submit README PRs directly
- Architecture changes

### Not Accepted

- Docker integration PRs
- Changes that add heavy dependencies without discussion
- "Fix" PRs for PEP 758 `except X, Y:` syntax — this is intentional

## Code Style

- **No comments** unless the WHY is non-obvious
- **No f-strings in logger calls** — use `logger.info("msg {}", var)`
- **Type annotations** on all public functions
- **`async def`** only when the body contains `await` — FastAPI runs sync handlers in threadpool automatically
- **Import boundaries** — `core/` never imports `api/`. `providers/` never imports `messaging/`. These are enforced by AST-based contract tests.

## Project Structure

```
api/           Routes, services, model routing, middleware integration
core/          Anthropic protocol helpers (SSE, conversion, streaming)
providers/     Provider transports and registry
middleware/    Extensible plugin pipeline
storage/       SQLite persistence
messaging/     Discord/Telegram bots
cli/           Entrypoints and process management
config/        Settings and provider catalog
tests/         Unit, contract, and smoke tests
.claude/       31-agent team (agents, hooks, docs, Shadow Mind)
```

## Adding a Provider

1. Create `providers/your_provider/` with `__init__.py` and `client.py`
2. Extend `OpenAIChatTransport` (for OpenAI-compatible APIs) or `AnthropicMessagesTransport` (for Anthropic-compatible APIs)
3. Add provider metadata to `config/provider_catalog.py`
4. Add factory wiring in `providers/registry.py`
5. Add settings fields in `config/settings.py`
6. Add tests in `tests/providers/`

## Adding a Middleware Plugin

1. Create `middleware/your_plugin.py`
2. Extend `middleware.Middleware` with `before_request()` and/or `after_response()`
3. Add feature flag to `config/settings.py` (follow `enable_*` pattern)
4. Register in `api/runtime.py` pipeline initialization
5. Add tests

## Using the Agent Team

The 31-agent team in `.claude/` is available when you run Claude Code in this repo. Say "full team session" to activate the CTO, or dispatch individual agents:

- "review this code" — dispatches language-specific expert
- "plan this feature" — dispatches deep-planner
- "audit security" — dispatches deep-reviewer
- "run tests" — dispatches test-engineer

See [`.claude/docs/team/TEAM_CHEATSHEET.md`](.claude/docs/team/TEAM_CHEATSHEET.md) for the full dispatch reference.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

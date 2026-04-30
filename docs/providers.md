# Provider Guide

Hyper Claude Code supports 6 LLM provider backends through two transport types.

## Transport Types

### OpenAI Chat Translation

Used by **NVIDIA NIM**. Converts Anthropic Messages API requests to OpenAI chat completions format, then translates the streaming response back to Anthropic SSE.

Key components:
- `core/anthropic/conversion.py` — `AnthropicToOpenAIConverter` handles message format translation
- `core/anthropic/thinking.py` — `ThinkTagParser` extracts `<think>` blocks from text streams
- `core/anthropic/tools.py` — `HeuristicToolParser` detects tool calls in plain text (for models without native function calling)

### Native Anthropic Messages

Used by **OpenRouter, DeepSeek, LM Studio, llama.cpp, Ollama**. These providers speak the Anthropic Messages API natively (or a compatible subset). The proxy passes requests through with minimal transformation:

- Thinking history sanitization (unsigned blocks removed when thinking enabled, all blocks removed when disabled)
- SSE block policy filtering (hidden blocks suppressed)
- Error recovery via `EmittedNativeSseTracker`

---

## NVIDIA NIM

**Transport:** OpenAI Chat Translation
**Key:** `NVIDIA_NIM_API_KEY` ([get one](https://build.nvidia.com/settings/api-keys))
**Default URL:** `https://integrate.api.nvidia.com/v1`

```dotenv
NVIDIA_NIM_API_KEY="nvapi-your-key"
MODEL="nvidia_nim/z-ai/glm4.7"
```

### Popular Models

| Model | Notes |
|-------|-------|
| `nvidia_nim/z-ai/glm4.7` | Strong general-purpose |
| `nvidia_nim/z-ai/glm5` | Latest generation |
| `nvidia_nim/moonshotai/kimi-k2.5` | Long context, strong reasoning |
| `nvidia_nim/minimaxai/minimax-m2.5` | Fast, cost-effective |

Browse all models at [build.nvidia.com](https://build.nvidia.com/explore/discover). A cached model list is in [`nvidia_nim_models.json`](../nvidia_nim_models.json).

### NIM-Specific Features

- Adaptive retry: on HTTP 400, strips `reasoning_budget`, `chat_template`, `reasoning_content` and retries
- `extra_body` support for `chat_template_kwargs` and tuning parameters
- Proxy support via `NVIDIA_NIM_PROXY`

---

## OpenRouter

**Transport:** Native Anthropic Messages
**Key:** `OPENROUTER_API_KEY` ([get one](https://openrouter.ai/keys))
**Default URL:** `https://openrouter.ai/api/v1`

```dotenv
OPENROUTER_API_KEY="sk-or-your-key"
MODEL="open_router/stepfun/step-3.5-flash:free"
```

### Free Models

Browse [free models](https://openrouter.ai/collections/free-models) — many capable models at zero cost.

### OpenRouter-Specific Features

- `extra_body` for OpenRouter-specific parameters (transforms, provider routing)
- Proxy support via `OPENROUTER_PROXY`

---

## DeepSeek

**Transport:** Native Anthropic Messages
**Key:** `DEEPSEEK_API_KEY` ([get one](https://platform.deepseek.com/api_keys))
**Default URL:** `https://api.deepseek.com/anthropic`

```dotenv
DEEPSEEK_API_KEY="your-deepseek-key"
MODEL="deepseek/deepseek-chat"
```

Uses DeepSeek's Anthropic-compatible endpoint, not the OpenAI chat endpoint.

---

## LM Studio

**Transport:** Native Anthropic Messages
**Key:** None (local)
**Default URL:** `http://localhost:1234/v1`

```dotenv
LM_STUDIO_BASE_URL="http://localhost:1234/v1"
MODEL="lmstudio/your-loaded-model"
```

Start LM Studio's local server and load a model. Use the identifier shown in LM Studio. Prefer models with tool-use support for Claude Code workflows.

---

## llama.cpp

**Transport:** Native Anthropic Messages
**Key:** None (local)
**Default URL:** `http://localhost:8080/v1`

```dotenv
LLAMACPP_BASE_URL="http://localhost:8080/v1"
MODEL="llamacpp/local-model"
```

Start `llama-server` with sufficient context for Claude Code:

```bash
llama-server -m your-model.gguf --ctx-size 32768 --port 8080
```

If you get HTTP 400 errors, increase `--ctx-size`.

---

## Ollama

**Transport:** Native Anthropic Messages
**Key:** None (local)
**Default URL:** `http://localhost:11434`

```dotenv
OLLAMA_BASE_URL="http://localhost:11434"
MODEL="ollama/llama3.1"
```

```bash
ollama pull llama3.1
ollama serve
```

Use the tag shown by `ollama list` (e.g., `ollama/llama3.1:8b`). Note: `OLLAMA_BASE_URL` is the server root — do not append `/v1`.

---

## Per-Tier Model Routing

Route different Claude Code model tiers to different providers:

```dotenv
MODEL_OPUS="nvidia_nim/moonshotai/kimi-k2.5"              # Complex tasks
MODEL_SONNET="open_router/deepseek/deepseek-r1-0528:free"  # Mid-tier (free)
MODEL_HAIKU="ollama/llama3.1"                               # Fast local
MODEL="nvidia_nim/z-ai/glm4.7"                              # Default
```

Blank per-tier values inherit `MODEL`.

## Thinking/Reasoning Configuration

```dotenv
ENABLE_MODEL_THINKING=true       # Global default
ENABLE_OPUS_THINKING=            # Per-tier override (blank = inherit)
ENABLE_SONNET_THINKING=
ENABLE_HAIKU_THINKING=
```

## Rate Limiting

```dotenv
PROVIDER_RATE_LIMIT=1            # Requests per window
PROVIDER_RATE_WINDOW=3           # Window in seconds
PROVIDER_MAX_CONCURRENCY=5      # Max simultaneous requests
```

Use lower values for free hosted providers. Local providers can handle higher concurrency.

## Timeouts

```dotenv
HTTP_READ_TIMEOUT=120            # Streaming read timeout
HTTP_WRITE_TIMEOUT=10            # Request write timeout
HTTP_CONNECT_TIMEOUT=10          # Connection timeout
```

## Adding a New Provider

1. Create `providers/your_provider/__init__.py` and `client.py`
2. Extend `OpenAIChatTransport` or `AnthropicMessagesTransport`
3. Register in `config/provider_catalog.py` (metadata) and `providers/registry.py` (factory)
4. Add settings in `config/settings.py`
5. Add tests in `tests/providers/`

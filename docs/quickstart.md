# Quickstart Guide

Get Hyper Claude Code running in under 5 minutes.

## Prerequisites

- [Claude Code](https://github.com/anthropics/claude-code) installed
- [uv](https://github.com/astral-sh/uv) package manager
- Python 3.14+
- An API key from at least one provider (or a local model server)

## Step 1: Install

```bash
brew install uv               # or: pip install uv
uv python install 3.14
git clone https://github.com/asiflow/hyper-claude-code.git
cd hyper-claude-code
```

## Step 2: Configure

```bash
cp .env.example .env
```

Edit `.env` with your provider. Simplest path — NVIDIA NIM (free tier):

```dotenv
NVIDIA_NIM_API_KEY="nvapi-your-key"
MODEL="nvidia_nim/z-ai/glm4.7"
ANTHROPIC_AUTH_TOKEN="your-secret-token"
```

Generate a strong token:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Start the Proxy

```bash
uv run uvicorn server:app --port 8082
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8082
```

## Step 4: Connect Claude Code

In a new terminal:

```bash
ANTHROPIC_AUTH_TOKEN="your-secret-token" ANTHROPIC_BASE_URL="http://localhost:8082" claude
```

Claude Code now runs through your proxy using your chosen model.

## Step 5 (Optional): Enable Middleware

Add to your `.env`:

```dotenv
ENABLE_COST_TRACKING=true          # See what each session costs
ENABLE_RESPONSE_CACHE=true         # Cache identical requests
ENABLE_PROVIDER_FAILOVER=true      # Auto-switch on provider failure
ENABLE_REQUEST_LOGGING=true        # Full audit trail
```

Restart the proxy to pick up changes.

## Step 6 (Optional): Activate the Agent Team

Open Claude Code in the hyper-claude-code directory:

```bash
cd hyper-claude-code
claude
```

Say **"full team session"** to activate the 31-agent engineering team. The CTO takes command and dispatches specialists based on your request.

## Verify It Works

```bash
# Check the proxy is running
curl http://localhost:8082/health

# Check available models
curl -H "x-api-key: your-secret-token" http://localhost:8082/v1/models

# Check cost tracking (if enabled)
curl -H "x-api-key: your-secret-token" http://localhost:8082/v1/cost

# Check cache stats (if enabled)
curl -H "x-api-key: your-secret-token" http://localhost:8082/v1/cache/stats
```

## Next Steps

- [Provider setup details](providers.md)
- [Architecture deep-dive](architecture.md)
- [Security model](security.md)
- [Full configuration reference](../.env.example)

# Example Configurations

Copy any of these to your project root as `.env` and customize the API keys.

| File | Use Case |
|------|----------|
| [`basic.env`](basic.env) | Simplest setup — one provider, local access |
| [`multi-provider.env`](multi-provider.env) | Mix providers per model tier (Opus/Sonnet/Haiku) |
| [`full-middleware.env`](full-middleware.env) | All middleware enabled — cost tracking, caching, failover, logging |
| [`local-only.env`](local-only.env) | Fully local with Ollama — no cloud, no API keys, complete privacy |
| [`discord-bot.env`](discord-bot.env) | Discord bot for remote coding sessions |

## Usage

```bash
cp examples/basic.env .env
# Edit .env with your API key
uv run uvicorn server:app --port 8082
```

---
name: HCC Project Profile
description: Hyper Claude Code is a pure-Python 3.14 FastAPI proxy — no Go, TS, Elixir, K8s, or database. 6 packages, 225 source files. Agent team needs tailoring from original multi-service origin.
type: project
---

HCC (Hyper Claude Code) is a pure-Python 3.14 FastAPI/Pydantic/httpx proxy that routes Anthropic Messages API traffic to alternative LLM providers (NVIDIA NIM, OpenRouter, DeepSeek, LM Studio, llama.cpp, Ollama).

**Why:** The 31-agent team was originally built for a Go+Python+Elixir+Next.js multi-service project on GKE. HCC has ZERO Go, TypeScript, or Elixir code, no K8s, no database, no frontend. 11 of 31 agents are completely irrelevant.

**How to apply:** When planning for HCC, scope to Python/FastAPI only. Cross-service impact matrices are unnecessary (single-service). Remove references to `<go-service>`, `<python-service>`, `<frontend>`, GKE, Istio, GraphQL from all agent prompts. Ship a 20-agent team (11 removed: go-expert, go-hybrid-engineer, typescript-expert, frontend-platform-engineer, beam-architect, elixir-engineer, beam-sre, erlang-solutions-consultant, infra-expert, cluster-awareness, database-expert).

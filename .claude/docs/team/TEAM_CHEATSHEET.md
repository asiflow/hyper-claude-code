# Team — Quick Reference Cheatsheet

> Print this. Tape it to your monitor. Use it until the patterns are reflex.

---

## Agent → Domain Map (Memorize)

```
IMPLEMENTATION                    REVIEW
─────────────────────              ─────────────────────
elite-engineer       → anything   go-expert        → Go
ai-platform-architect → AI/ML    python-expert    → Python
frontend-platform-    → frontend typescript-expert → TS/React
   engineer                       deep-qa          → quality
beam-architect       → BEAM topo  deep-reviewer    → security
elixir-engineer      → Elixir     infra-expert     → K8s/GCP
go-hybrid-engineer   → gRPC/edge  database-expert  → SQL/Redis
                                  observability-   → logs/traces
PLANNING                             expert
─────────────────────              api-expert       → GraphQL
deep-planner     → plans          test-engineer    → tests (writes too)
orchestrator     → execute        beam-sre         → BEAM cluster ops

INTELLIGENCE                      META
─────────────────────              ─────────────────────
memory-coordinator  → team knowledge   meta-agent   → prompt evolution
cluster-awareness   → live cluster     recruiter    → 8-phase hiring
benchmark-agent     → competitive intel session-sentinel → protocol audit
erlang-solutions-   → BEAM advisory    cto          → supreme authority
   consultant          (external retainer)
talent-scout        → team-gap audit
intuition-oracle    → Shadow Mind query (optional)

VERIFICATION (Tier 8)
─────────────────────
evidence-validator → verify finding against source (CONFIRMED/REFUTED/...)
challenger        → adversarial review of CTO synthesis + new-agent drafts
```

---

## NEXUS Syscalls (Subagent → Kernel)

All sent via `SendMessage({to: "lead", message: "[NEXUS:...]", summary: "..."})`.

| Syscall | Format | Auto |
|---------|--------|------|
| **SPAWN** | `[NEXUS:SPAWN] agent_type \| name=X \| prompt=...` | ✅ |
| **SCALE** | `[NEXUS:SCALE] agent_type \| count=N \| prompt=...` | ⚠️ |
| **RELOAD** | `[NEXUS:RELOAD] agent_name` | ✅ |
| **MCP** | `[NEXUS:MCP] server_name \| config={...}` | ⚠️ |
| **ASK** | `[NEXUS:ASK] question text` | ⚠️ |
| **CRON** | `[NEXUS:CRON] schedule=5m \| command=...` | ⚠️ |
| **WORKTREE** | `[NEXUS:WORKTREE] branch=X` | ⚠️ |
| **CAPABILITIES?** | `[NEXUS:CAPABILITIES?]` | ✅ |
| **PERSIST** | `[NEXUS:PERSIST] key=X \| value=Y` | ✅ |
| **BRIDGE** | `[NEXUS:BRIDGE] from_team=X \| to_agent=Y \| message=...` | ⚠️ |
| **INTUIT** | `[NEXUS:INTUIT] <question>` (Shadow Mind query, optional) | ✅ |

**AUTO ✅** = runs immediately. **CONFIRM ⚠️** = user confirmation for high-risk.

---

## Closing Protocol Signal Template

Every agent ends with these 4 sections:

```markdown
### MEMORY HANDOFF
[durable finding, or NONE]

### EVOLUTION SIGNAL
[prompt improvement opportunity, or NONE]

### CROSS-AGENT FLAG
[out-of-domain finding, or NONE]

### DISPATCH RECOMMENDATION
[next agent to dispatch, or NONE]
```

---

## Signal Bus Files

Location: `.claude/agent-memory/signal-bus/`

| File | Written By | Read By | Cleared By |
|------|-----------|---------|------------|
| `memory-handoffs.md` | all agents | memory-coordinator | Pattern F |
| `evolution-signals.md` | all agents | meta-agent | Pattern F |
| `cross-agent-flags.md` | all agents | CTO/orchestrator | on routing |
| `dispatch-queue.md` | all agents | orchestrator | on dispatch |
| `nexus-log.md` | main thread | auditors | Pattern F (optional) |

### Canonical Entry Format

```
- (YYYY-MM-DD, agent=<name>, session=<topic>) <signal content>
```

---

## Common Dispatch Patterns

### Single-Shot Review
```
Agent({
  subagent_type: "go-expert",
  prompt: "Review [file:lines] for [specific concern]. Report findings with severity."
})
```

### Multi-Language Review (Parallel)
```
[go-expert, python-expert, typescript-expert] — dispatched in parallel, one message
```

### Full Workflow
```
deep-planner (plan) → cto (approve + coordinate) → orchestrator (execute)
```

### Pattern F (End of Session)
```
memory-coordinator + meta-agent — dispatched in parallel
```

### Emergency Incident
```
cluster-awareness + deep-reviewer (parallel) →
  decision →
  elite-engineer (fix) →
  language-expert (rapid review) →
  cluster-awareness (verify deploy)
```

---

## Activation Phrases (User → Main Thread)

| User says... | Main thread dispatches |
|--------------|------------------------|
| "review Go code" | `go-expert` |
| "plan remediation" | `deep-planner` |
| "orchestrate" / "execute plan" | `orchestrator` |
| "full team session" | `session-sentinel` → `cto` |
| "quality audit" | `deep-qa` |
| "security review" | `deep-reviewer` |
| "test strategy" | `test-engineer` |
| "what's deployed" | `cluster-awareness` |
| "how does [competitor] do this" | `benchmark-agent` |
| "Pattern F" / "end session learning" | `memory-coordinator` + `meta-agent` |
| "remember this" / "team memory" | `memory-coordinator` |
| "evolve prompts" / "meta sweep" | `meta-agent` |
| "incident" / "outage" / "urgent" | `cto` (emergency mode) |
| "implement" / "fix bug" | `elite-engineer` |
| "build frontend component" | `frontend-platform-engineer` |
| "design agent system" / "RAG" | `ai-platform-architect` |
| "verify finding" / "is this claim true" / "check evidence" | `evidence-validator` |
| "challenge this" / "counter-argument" / "devil's advocate" | `challenger` |
| "design BEAM / OTP topology" / "Plane 1 kernel" | `beam-architect` |
| "implement Elixir" / "build product-agent" / "gen_statem code" | `elixir-engineer` (often scaled x2 for pair work) |
| "gRPC boundary" / "Plane 2 Go edge" / "Dapr sidecar" | `go-hybrid-engineer` |
| "BEAM cluster ops" / "libcluster" / "hot-code-load" | `beam-sre` |
| "consult Erlang Solutions" / "Gate 2 validation" / "BEAM gut-check" | `erlang-solutions-consultant` |
| "team coverage gap" / "detect missing specialist" / "audit team gaps" | `talent-scout` |
| "hire new agent" / "run hiring pipeline" | `recruiter` (after talent-scout requisition) |
| "consult the team's intuition" / "has pattern been seen" / "INTUIT" | `intuition-oracle` (via `[NEXUS:INTUIT]`) |
| "run contract tests" / "check agent health" | `python3 .claude/tests/agents/run_contract_tests.py` |
| "show trust standings" | `./.claude/agent-memory/trust-ledger/ledger.py standings` |

---

## The Absolute Must-Nots

- ❌ NEVER dispatch generic built-in subagents (`Plan`, `general-purpose`, `Explore`) — always use custom team
- ❌ NEVER commit with bundled unrelated changes — split into logical commits
- ❌ NEVER skip language expert review after code changes
- ❌ NEVER skip deep-reviewer for security-touching code
- ❌ NEVER let CTO do work itself — it's a coordinator, not a worker
- ❌ NEVER bulk-delete files based on "looks unused" without user confirmation (feedback_no_delete_frontend_hooks.md)
- ❌ NEVER use `--no-verify` on git commits without explicit user permission
- ❌ NEVER force-push to main
- ❌ NEVER assume cluster state without `cluster-awareness` verification

---

## Quick Health Checks

```bash
# Agent files present?
ls .claude/agents/*.md | wc -l   # should be 31

# Signal bus exists?
ls .claude/agent-memory/signal-bus/   # should show 5 files

# Agent teams enabled?
grep CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS .claude/settings.json

# Session-sentinel model correct?
grep "^model:" .claude/agents/session-sentinel.md   # should be "sonnet"

# Pending signals?
wc -l .claude/agent-memory/signal-bus/*.md

# Shadow Mind heartbeat fresh? (only if Shadow Mind is enabled)
ls -la .claude/agent-memory/shadow-mind/heartbeats/ 2>/dev/null   # check mtimes < 24h

# Contract tests passing?
python3 .claude/tests/agents/run_contract_tests.py   # expected: 341 passed
```

---

## Key Files Quick Reference

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Main thread protocol (kernel rules) |
| `.claude/agents/*.md` | 31 agent prompts (29 specialists + 2 verifiers) |
| `.claude/hooks/*.sh` | Protocol enforcement hooks (auto-run) + Shadow Mind scripts (shadow-*) + post-hire-verify.sh |
| `.claude/tests/agents/` | 341-assertion contract test suite |
| `.claude/agent-memory/trust-ledger/` | Per-agent accuracy scorecard |
| `.claude/agent-memory/<agent>/MEMORY.md` | Per-agent memory index |
| `.claude/agent-memory/signal-bus/*.md` | Async message bus |
| `.claude/agent-memory/shadow-mind/` | Shadow Mind data (optional, delete-to-disable) |
| `.claude/docs/team/*` | This documentation suite |
| `~/.claude/projects/<proj>/memory/MEMORY.md` | User-level project memory |
| `~/.claude/teams/<team>/config.json` | Runtime team configuration |
| `~/.claude/teams/<team>/inboxes/` | Teammate message inboxes |

---

## One-Line Invocations

```
# Start a full team session
"Use the team. [your goal]. CTO has full authority."

# Quick review
"Review [file] with [agent-name]"

# Emergency response
"Incident in [service]: [symptom]. Use the team."

# End of session
"Run Pattern F"

# Strategic decision
"Strategic decision needed: [X vs Y]. Use the team to analyze."
```

---

*Last updated: 2026-04-18 — v3.0 with 31 agents, hiring pipeline, Shadow Mind.*

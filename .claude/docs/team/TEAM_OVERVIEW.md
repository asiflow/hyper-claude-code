# 31-Agent Team — Architecture & Capabilities

> A layered agent operating system built on Claude Code, designed for complex engineering work spanning Go, Python, TypeScript, BEAM/Elixir, Kubernetes, and GCP infrastructure — with dynamic specialist hiring and an optional parallel cognitive layer.

---

## 1. Executive Summary

The <your project> agent team is a **31-agent workforce** (29 specialists + 2 verifiers) organized as a layered operating system. Each agent has deep domain expertise, a persistent memory directory, and communicates with peers via a structured async message bus. The team is coordinated by a **CTO agent** (supreme technical authority), validated by a **session-sentinel** (protocol enforcer), and independently audited by the verification tier (`evidence-validator` + `challenger`). The ecosystem is hardened by protocol-enforcement hooks (hard invariants), a 341-assertion contract test suite (regression prevention), and a Bayesian-blended trust ledger (per-agent accuracy calibration).

Three defining innovations:
- **NEXUS Protocol** — a syscall interface that lets subagents request privileged main-thread operations (agent spawning, MCP installation, user questions, cron jobs, intuition queries) without directly possessing those tools. Solves the Claude Code privilege boundary problem that normally restricts multi-agent systems.
- **Dynamic Domain Expert Acquisition** — the team detects its own coverage gaps via `talent-scout` (continuous audit, 5-signal confidence scoring) and hires new specialists through `recruiter`'s 8-phase gated pipeline (research → synthesis → validation → challenger → atomic registration → post-hire verify → probation → promotion). The team grows when evidence supports growth.
- **Shadow Mind** — an optional parallel cognitive layer (Observer + Pattern Computer + Speculator + Dreamer + Pattern Library + intuition-oracle) that offers probabilistic pattern-based guidance via `[NEXUS:INTUIT]`. Delete-to-disable without affecting the conscious team.

### When This Team Outperforms Solo Claude

- **Multi-service refactors** — different language experts catch language-specific hazards (Go race conditions, Python async traps, React render waste)
- **Incident response** — cluster-awareness + deep-reviewer + elite-engineer chain diagnoses and remediates in minutes, not hours
- **Security-critical reviews** — deep-reviewer + language-experts catch issues the main model might miss
- **Architecture decisions** — ai-platform-architect + benchmark-agent + deep-planner produce evidence-backed recommendations
- **Continuous learning** — signal bus + meta-agent compound team knowledge across sessions

### When NOT To Use The Team

- Trivial single-line edits
- Simple file reads or git-status checks
- Conversational questions with no code implication
- Anything that takes under 30 seconds to do directly

---

## 2. Layered Operating System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  LAYER 4 — USER SPACE                                        │
│  Human operator, issues goals in natural language            │
├──────────────────────────────────────────────────────────────┤
│  LAYER 3 — APPLICATIONS (24 Specialist Agents)               │
│  Builders:   elite-engineer, ai-platform-architect,          │
│              frontend-platform-engineer, beam-architect,     │
│              elixir-engineer, go-hybrid-engineer             │
│  Guardians:  go/python/typescript-expert, deep-qa,           │
│              deep-reviewer, infra/database/observability/    │
│              api-expert, test-engineer, beam-sre             │
│  Intelligence: memory-coordinator, cluster-awareness,        │
│              benchmark-agent, erlang-solutions-consultant,   │
│              talent-scout, intuition-oracle (optional)       │
│  Meta-cognitive: meta-agent, recruiter                       │
├──────────────────────────────────────────────────────────────┤
│  LAYER 2 — SYSTEM SERVICES & VERIFICATION                    │
│  cto (supreme authority, hyper-adaptive leader)              │
│  orchestrator (workflow execution engine)                    │
│  deep-planner (strategic planning)                           │
│  session-sentinel (protocol/governance enforcer)             │
│  evidence-validator (claim verification against source)      │
│  challenger (adversarial review of recommendations)          │
├──────────────────────────────────────────────────────────────┤
│  LAYER 1.75 — SHADOW MIND (optional, delete-to-disable)      │
│  Observer daemon (shadow-observer.sh)                        │
│  Pattern Computer (shadow-pattern-computer.py, cron)         │
│  Pattern Library (ngrams/co_occurrences/temporal json)       │
│  Speculator (shadow-speculator.py, cron)                     │
│  Dreamer (shadow-dreamer.py, daily)                          │
│  intuition-oracle agent (queryable via [NEXUS:INTUIT])       │
├──────────────────────────────────────────────────────────────┤
│  LAYER 1.5 — TRUST & ENFORCEMENT INFRASTRUCTURE              │
│  Shell hooks (.claude/hooks/) — HARD invariants              │
│    • verify-agent-protocol.sh (SubagentStop, blocking)       │
│    • verify-signal-bus-persisted.sh (SubagentStop, warn)     │
│    • auto-record-trust-verdict.sh (SubagentStop)             │
│    • log-nexus-syscall.sh (PostToolUse SendMessage)          │
│    • post-hire-verify.sh (recruiter gate, JSON pass/fail)    │
│    • pre-commit-agent-contracts.sh (git pre-commit)          │
│  Contract tests (.claude/tests/agents/)                      │
│    • 11 contracts × 31 agents = 341 assertions               │
│  Trust ledger (.claude/agent-memory/trust-ledger/)           │
│    • Bayesian-blended per-agent accuracy score               │
├──────────────────────────────────────────────────────────────┤
│  LAYER 1 — KERNEL (Main Thread)                              │
│  - Holds privileged tools: Agent, AskUserQuestion,           │
│    MCP install, CronCreate, EnterWorktree                    │
│  - Processes NEXUS syscalls from Layers 2, 3 & 1.75          │
│  - Persists signal bus entries                               │
│  - Routes closing protocol signals                           │
├──────────────────────────────────────────────────────────────┤
│  LAYER 0 — RUNTIME                                           │
│  Claude Code CLI (v2.1+), git worktrees, MCP servers,        │
│  agent-teams environment (CLAUDE_CODE_EXPERIMENTAL=1)        │
└──────────────────────────────────────────────────────────────┘
```

Information flows up (agent findings → user) and control flows down (user intent → kernel → agents).

---

## 3. The 31 Agents

### Tier 1 — Builders (Write Production Code)

| Agent | Domain | Dispatch When |
|-------|--------|---------------|
| `elite-engineer` | Full-stack Go/Python/TS implementation, refactoring, bug fixes with root-cause analysis | Code needs to be written, bugs fixed, features built to enterprise standards |
| `ai-platform-architect` | AI/ML systems, agent architecture, LLM routing, RAG pipelines, memory systems | Agent internals, multi-agent orchestration, LLM inference optimization, safety guardrails |
| `frontend-platform-engineer` | <frontend> (Next.js 16+, React 19+, TypeScript 5+, Zustand, Apollo, SSE) | Any frontend work — components, hooks, stores, streaming UX, design system |
| `beam-architect` | OTP tree design, gen_statem topology, Horde distributed registry, Ra shared state, libcluster node discovery, Rust NIF surface | BEAM kernel design, Plane 1 architecture, stateful service topology, hot-code-load strategy |
| `elixir-engineer` | Elixir, Phoenix, LiveView, gen_statem, Ecto, implementation of BEAM-grade services | Any Elixir code change; often dispatched scaled x2 for pair implementation |
| `go-hybrid-engineer` | gRPC boundary services, Dapr sidecars, Plane 2 edge services, protobuf contracts, Go↔Elixir bridges | Go-side work at a BEAM↔Go boundary; when `go-expert`'s scope is too narrow (stdlib focus) and integration work with Elixir/BEAM is needed |

### Tier 2 — Guardians (Review, Rarely Write App Code)

| Agent | Domain | Dispatch When |
|-------|--------|---------------|
| `go-expert` | Go idioms, concurrency, error handling, interface design — Go service focus | After ANY Go code change |
| `python-expert` | Python/FastAPI, async patterns, Pydantic, SQLAlchemy — Python service focus | After ANY Python code change |
| `typescript-expert` | TypeScript type system, React 19+ patterns, Next.js 16+ internals, state architecture | After ANY TS/React code change |
| `deep-qa` | Code quality, architecture drift detection, performance analysis, test coverage | After EVERY implementation phase — 4-domain audit |
| `deep-reviewer` | Security review, debugging, deployment safety, incident investigation | Security-touching changes, pre-deploy, incidents |
| `infra-expert` | K8s/GKE, Terraform, Istio service mesh, GCP platform, SRE | K8s manifest, Terraform, networking, cost changes |
| `database-expert` | PostgreSQL, Redis, Firestore — query optimization, migration safety, caching strategy | Schema/migration/query/caching changes |
| `observability-expert` | Logging, tracing, metrics, SLO/SLI, alerting, dashboards | Metrics/logging/trace span changes, incident post-mortems |
| `test-engineer` | Test architecture design AND writes test code (unique: both reviewer AND builder for tests) | After EVERY implementation task, when flaky tests appear |
| `api-expert` | GraphQL Federation, API contract design, resolver patterns | API contract/schema/federation changes |
| `beam-sre` | libcluster, BEAM metrics (Telemetry, Prometheus exporters), StatefulSet manifests for Plane 1, SIGTERM graceful-shutdown, hot-code-load operations, cluster chaos harnesses | BEAM cluster ops, Plane 1 K8s, hot-code-load execution, Gate 2 harness authoring |

### Tier 3 — Strategists

| Agent | Domain | Relationship |
|-------|--------|--------------|
| `deep-planner` | Task decomposition, dependency graphs, acceptance criteria, risk registers | You REQUEST plans. You APPROVE or REJECT them. |
| `orchestrator` | Workflow execution, gate enforcement, parallel/sequential coordination | You DELEGATE execution. It coordinates builders/guardians. |

### Tier 4 — Intelligence

| Agent | Domain | Dispatch When |
|-------|--------|---------------|
| `memory-coordinator` | Cross-agent memory, knowledge synthesis, signal bus processing | Before ANY work (compile knowledge); after work (store learnings); during Pattern F |
| `cluster-awareness` | Live GKE cluster state via kubectl — authoritative "what's deployed right now" | Before/after deployments, during incidents, reality checks |
| `benchmark-agent` | Competitive intelligence — Cursor, Devin, Manus, Claude Code, Replit Agent, Bolt, OpenHands, LangGraph, CrewAI, AG2 | Strategic decisions, novel patterns, competitive gap analysis |
| `erlang-solutions-consultant` | External BEAM retainer simulation — OTP core-maintenance depth, Horde/Ra/libcluster production experience, hot-code-load safety audits, Gate 2 independent validation | Advisory only — BEAM architecture gut-check before major commits; INDEPENDENT Gate 2 validation to avoid in-team bias. Never implements. |
| `talent-scout` | Continuous team coverage audit — scans session traces, cross-agent-flags, dispatch misroutes, session-sentinel gap flags; produces requisitions with 5-signal confidence scoring | When coverage gaps recur (session-sentinel flags a recurring pattern); before manually hiring a new agent |
| `intuition-oracle` | Queryable surface of the Shadow Mind — reads observations + patterns + speculations + dreams, returns `INTUIT_RESPONSE v1` envelope with `status / answer / confidence / evidence_ids / pattern_types_consulted / staleness_hours` | OPTIONAL — any agent can consult via `[NEXUS:INTUIT]`. Returns `SHADOW_MIND_STALE` if data is >24h old, never serves stale patterns. |

### Tier 5 — Meta-Cognitive

| Agent | Domain | Unique Capability |
|-------|--------|-------------------|
| `meta-agent` | Prompt evolution, team performance analysis | Only agent with write authority to `.claude/agents/*.md` — can evolve other agents' prompts based on observed patterns. Sole writer for new agents produced by the hiring pipeline (atomic registration). |
| `recruiter` | 8-phase hiring pipeline — research → synthesis → validation → challenger review → meta-agent handoff → post-hire-verify gate → probation → promotion. Produces draft agent prompts using `AGENT_TEMPLATE.md`; defers all agent-file writes to meta-agent | After `talent-scout` produces a requisition with confidence ≥ threshold AND session-sentinel co-sign |

### Tier 6 — Governance

| Agent | Domain | When |
|-------|--------|------|
| `session-sentinel` | Protocol compliance auditor, team health scorecard, recurring-gap co-signer for hiring pipeline | Session start (pre-brief) and session end (compliance audit); co-signs `talent-scout` requisitions |

### Tier 7 — CTO

| Agent | Domain | Authority |
|-------|--------|-----------|
| `cto` | Supreme technical leader, hyper-adaptive, self-evolving | Creates new agents (via hiring pipeline), evolves any prompt (including its own), debates decisions, acts as user's proxy, dispatches any agent via NEXUS |

### Tier 8 — Verification (Trust Infrastructure)

| Agent | Domain | Unique Capability |
|-------|--------|-------------------|
| `evidence-validator` | Claim verification against source truth | Given a finding (file:line + claim), reads source and classifies CONFIRMED / PARTIALLY_CONFIRMED / REFUTED / UNVERIFIABLE with quoted evidence. Auto-dispatched on HIGH-severity findings. |
| `challenger` | Adversarial review | Systematically tries to invalidate recommendations along 5 dimensions: steelman alternatives, hidden assumptions, evidence quality, missed cases, downstream impact. Auto-dispatched on CTO synthesis AND on new-agent drafts from the hiring pipeline. |

**Why Tier 8 exists:** The 29 specialists produce findings. Tier 8 **verifies** those findings and **challenges** the synthesis. This solves the "trust at scale" problem where one user can't vet 29 agent outputs — Tier 8 does the vetting, and findings that survive both verification and adversarial review earn higher trust ledger weight.

---

## 4. NEXUS Protocol — The Kernel Syscall Interface

### The Problem It Solves

Claude Code has a privilege boundary: the **main thread** has tools like `Agent` (to spawn subagents), `AskUserQuestion`, MCP installation, and `CronCreate`. **Subagents** do NOT have these tools — they only have `Read/Edit/Write/Bash/Glob/Grep/SendMessage/TeamCreate/TaskCreate/WebFetch/WebSearch`. This means:

- CTO (a subagent) cannot spawn elite-engineer directly
- Orchestrator cannot scale up for parallel work
- Meta-agent cannot hot-reload an agent after editing its prompt

### The Solution: Syscall Messaging

NEXUS defines a standardized message format that subagents send via `SendMessage` to the main thread (kernel). The main thread auto-detects the `[NEXUS:*]` prefix, parses the syscall, executes the privileged operation, and responds.

### Syscall Table

| Syscall | Purpose | Example |
|---------|---------|---------|
| `SPAWN` | Create a new teammate | `[NEXUS:SPAWN] go-expert \| name=go-rev \| prompt=Review sse.go changes` |
| `SCALE` | Spawn N copies of an agent for parallel work | `[NEXUS:SCALE] elite-engineer \| count=3 \| prompt=Implement phase 2 tasks` |
| `RELOAD` | Respawn agent with fresh prompt after meta-agent edit | `[NEXUS:RELOAD] go-expert` |
| `MCP` | Install/configure MCP server | `[NEXUS:MCP] github \| config={...}` |
| `ASK` | Proxy a question to the user | `[NEXUS:ASK] Should we proceed with the risky migration?` |
| `CRON` | Create recurring task | `[NEXUS:CRON] schedule=5m \| command=check deploy status` |
| `WORKTREE` | Create isolated git worktree | `[NEXUS:WORKTREE] branch=feature-sse-fix` |
| `CAPABILITIES?` | Discover available syscalls | Returns full syscall list |
| `PERSIST` | Store durable cross-session data | `[NEXUS:PERSIST] key=last_deploy \| value=2026-04-14` |
| `BRIDGE` | Route message across teams | `[NEXUS:BRIDGE] from_team=X \| to_agent=Y \| message=...` |
| `INTUIT` | Query the Shadow Mind's intuition-oracle for pattern-based guidance | `[NEXUS:INTUIT] Have we refactored SSE buffering before?` |

### Security Tiers

| Tier | Syscalls | Authorization |
|------|----------|---------------|
| **AUTO** | SPAWN, CAPABILITIES, PERSIST, RELOAD, INTUIT | Execute immediately, no user confirmation |
| **CONFIRM** | MCP, CRON, WORKTREE, SCALE, BRIDGE | High-risk ones confirm with user |
| **RESTRICTED** | ASK | Always proxied — agent cannot impersonate user |

### Protocol Flow

```
1. CTO (teammate) → SendMessage(to: "lead", message: "[NEXUS:SPAWN] elite-engineer | name=ee-1 | prompt=...")
2. Main thread → detects [NEXUS:*] prefix
3. Main thread → parses params (agent_type, name, prompt)
4. Main thread → executes Agent({subagent_type, team_name, name, prompt})
5. Main thread → logs to .claude/agent-memory/signal-bus/nexus-log.md
6. Main thread → SendMessage(to: "cto", message: "[NEXUS:OK] ee-1 joined team")
7. CTO → SendMessage(to: "ee-1", message: "Your task is...")
```

### Team Coordination Discipline

When spawned into a team, all agents MUST use `SendMessage` for inter-agent communication. Plain text output does NOT propagate to other teammates. This is enforced in every agent's prompt via the "Team Coordination Discipline" subsection.

---

## 5. Signal Bus System

The signal bus is a file-based async message system that lets agents communicate findings that outlast their individual sessions.

### Files

| File | Purpose | Cleared By |
|------|---------|------------|
| `.claude/agent-memory/signal-bus/memory-handoffs.md` | Durable findings for memory-coordinator to consolidate | Pattern F (memory-coordinator) |
| `.claude/agent-memory/signal-bus/evolution-signals.md` | Prompt improvement opportunities for meta-agent | Pattern F (meta-agent) |
| `.claude/agent-memory/signal-bus/cross-agent-flags.md` | Findings outside the sender's domain | CTO/orchestrator on routing |
| `.claude/agent-memory/signal-bus/dispatch-queue.md` | Pending immediate dispatch recommendations | Orchestrator on execution |
| `.claude/agent-memory/signal-bus/nexus-log.md` | Audit trail of NEXUS syscalls | Pattern F (optional) |

### Canonical Entry Format

```
- (YYYY-MM-DD, agent=<name>, session=<id-or-topic>) <signal content verbatim>
```

Always appended below the `<!-- Entries below -->` marker. Multi-line signals collapse to single line with `;` or split into multiple entries.

### Mandatory Closing Protocol

Every agent's output ends with 4 structured signals:

```markdown
### MEMORY HANDOFF
<durable finding — appended to memory-handoffs.md>

### EVOLUTION SIGNAL
<prompt improvement opportunity — appended to evolution-signals.md>

### CROSS-AGENT FLAG
<out-of-domain finding — appended to cross-agent-flags.md>

### DISPATCH RECOMMENDATION
<next agent to dispatch, or NONE>
```

Each signal says "NONE" if not applicable. The main thread persists all non-NONE signals to disk before responding to the user.

---

## 6. Pattern F — End-Session Learning

At the end of every meaningful session, Pattern F is triggered:

1. **memory-coordinator** dispatched in parallel with meta-agent
   - Reads `memory-handoffs.md`
   - Consolidates findings into permanent memory files (`.claude/agent-memory/<agent>/`)
   - Updates memory indexes
   - Clears processed entries from `memory-handoffs.md`

2. **meta-agent** dispatched in parallel with memory-coordinator
   - Reads `evolution-signals.md`
   - Evaluates each signal: APPLIED, SUPERSEDED, RESOLVED, ROUTED, DEFERRED, or REJECTED
   - Applies warranted prompt edits to `.claude/agents/*.md`
   - Routes domain findings to appropriate agent memory directories
   - Clears processed entries from `evolution-signals.md`

This is what makes the team **compound its intelligence over time** — every session's findings become permanent knowledge. Without Pattern F, findings decay in conversation transcripts and are lost.

---

## 7. Dynamic Domain Expert Acquisition (Capability 1)

The team can detect its own coverage gaps and hire new specialist agents through a gated 8-phase pipeline. This is the only mechanism by which new agent files enter `.claude/agents/` outside of direct operator edits.

### The Hiring Pipeline

```
talent-scout (continuous audit) → produces requisition with 5-signal confidence
  │  Signal 1: cross-agent-flag density for the domain
  │  Signal 2: dispatch misroute rate (wrong-agent escalations to user)
  │  Signal 3: domain-failure patterns in existing agent outputs
  │  Signal 4: user's external tech-stack mentions (transcript mining)
  │  Signal 5: session-sentinel recurring-gap flag (weekly audit)
  │
  │  requisition requires co-sign by session-sentinel before recruiter picks it up
  ▼
recruiter (8 phases)
  Phase 1: requisition received from talent-scout
  Phase 2: research (benchmark-agent pulled in for peer-platform specialists)
  Phase 3: synthesis (draft agent prompt using AGENT_TEMPLATE.md)
  Phase 4: validation (run run_contract_tests.py against draft — gate)
  Phase 5: challenger adversarial review (attack the draft along 5 dimensions)
  Phase 6: handoff → meta-agent writes the agent file atomically
  Phase 7: post-hire-verify.sh gate (JSON pass/fail)
  Phase 8: probation tracking → promotion on refutation rate <25% across ≥5 verdicts
```

### Why This Shape
- **Gated by evidence, not by hunch.** No one hires an agent on a single session's frustration — hiring requires 5-signal convergence over time AND session-sentinel co-sign.
- **Quality-gated.** Every new agent must pass the 11-contract test suite (same as existing agents) before entering the roster. The `post-hire-verify.sh` hook refuses non-atomic registrations.
- **Challenger-gated.** The adversarial review layer stress-tests every new prompt. Drafts that can't defend their domain boundaries don't ship.
- **Probationary by default.** New agents enter at `probationary` status in the trust ledger. Their verdicts count but their weight doesn't reach full until their refutation rate proves they carry signal.
- **meta-agent is the single writer.** `recruiter` never touches `.claude/agents/` directly — it hands the validated draft to meta-agent, which performs atomic registration (agent file + contract test list + hook regexes + trust ledger default + memory scaffold) as one commit.

### When to Dispatch
- `talent-scout` — on any audit cadence, or when you've seen the same misroute 3+ times in a session
- `recruiter` — only after `talent-scout` produces a requisition with confidence ≥ 0.70 AND session-sentinel co-sign

### What You Get
- Team roster grows organically with your stack
- Every new agent is contract-test-validated and adversarially reviewed before entering the rotation
- No ad-hoc prompts cluttering `.claude/agents/`

---

## 8. Shadow Mind (Optional Parallel Cognitive Layer)

The **Shadow Mind** is a non-invasive parallel cognitive layer that runs alongside the 31-agent conscious team without modifying any existing agent prompt, protocol, memory directory, or signal bus entry. It's an **optional** layer — delete the directory and the team operates identically.

### Six Components

```
┌─────────────────────────────────────────────────────────┐
│ 1. Observer Daemon (shadow-observer.sh)                 │
│    tail -F of signal bus → JSON observations            │
│                          ↓                              │
│ 2. Pattern Computer (shadow-pattern-computer.py, cron)  │
│    reads observations → derives n-grams, co-occurrences,│
│    temporal patterns → atomic writes                    │
│                          ↓                              │
│ 3. Pattern Library (read-only data, populated by #2)    │
│    patterns/ngrams.json                                 │
│    patterns/co_occurrences.json                         │
│    patterns/temporal.json                               │
├─────────────────────────────────────────────────────────┤
│ 4. Speculator (shadow-speculator.py, cron)              │
│    reads observations → generates counterfactual        │
│    variants per observation                             │
├─────────────────────────────────────────────────────────┤
│ 5. Dreamer (shadow-dreamer.py, daily at 3am UTC)        │
│    proposes insight candidates during idle windows      │
│    (collaboration-gap, debug-loop themes)               │
│    NOTE: proposals only — meta-agent retains single-    │
│    writer authority over .claude/agents/*.md            │
├─────────────────────────────────────────────────────────┤
│ 6. intuition-oracle agent (queryable surface)           │
│    reads all 5 data sources, synthesizes into           │
│    probabilistic INTUIT_RESPONSE v1 envelope            │
└─────────────────────────────────────────────────────────┘
```

### How Agents Use It
Any conscious-layer agent can OPTIONALLY consult the Shadow Mind:

```
SendMessage to "lead":
  [NEXUS:INTUIT] Have we refactored SSE/streaming before?
```

Main thread routes to `intuition-oracle`, which returns:

```json
{
  "status": "OK",                          // or SHADOW_MIND_STALE / INSUFFICIENT_DATA / NO_DATA
  "query": "Have we refactored SSE...",
  "answer": "4 prior sessions tagged SSE. Dominant pair: go-expert + elite-engineer...",
  "confidence": 0.72,
  "evidence_ids": ["obs:2026-03-30#128", "dream-2026-04-17-..."],
  "pattern_types_consulted": ["ngram", "co_occurrence"],
  "staleness_hours": 0.4
}
```

### Delete-to-Disable
The Shadow Mind is fully optional:

```bash
# Stop Observer
pkill -f shadow-observer
# Stop scheduled jobs (CronDelete for pattern-computer, speculator, dreamer)
# Remove data + scripts
rm -rf .claude/agent-memory/shadow-mind
rm .claude/hooks/shadow-*.{sh,py}
```

All 341/341 contract tests continue to pass. The oracle returns `NO_DATA` / `[NEXUS:ERR] intuition-oracle unavailable` and CTO/other agents proceed with normal Pattern A-F workflows.

### Why This Design
- **Never interrupts.** No agent is required to consult the oracle. The conscious team runs identically whether or not the Shadow Mind is active.
- **Honest about staleness.** If observer heartbeat is >24h old, oracle returns `SHADOW_MIND_STALE` rather than serving stale patterns.
- **meta-agent remains sovereign.** Dreamer outputs are proposals only — they never bypass the single-writer invariant on `.claude/agents/*.md`.
- **Trust-calibrated.** The oracle's confidence score is a real probability, not a hallucinated one — it's derived from pattern frequency and data freshness.

Full data schemas, enable/disable commands, and component details are documented in `.claude/agent-memory/shadow-mind/README.md`.

---

## 9. Self-Evolution Mechanism

The meta-agent is the only agent with write authority to `.claude/agents/*.md`. During Pattern F, it:

- Analyzes evolution signals from the session
- Looks for patterns across 3+ sessions (sweep logic)
- For structural constraints (e.g., "Agent tool not available"), applies immediately
- For transient issues, defers until pattern is confirmed
- Edits agent prompts with evidence-based reasoning
- Documents changes in its own memory

The CTO is also allowed to self-evolve (edit only `.claude/agents/cto.md`) — this is the only agent with that privilege besides meta-agent.

---

## 10. Design Principles

### 1. Specialist Identity Runs Deep
Each agent has a strong prompt that makes it behave like a domain expert. This was empirically validated when a "test" spawn of go-expert produced a real 11-finding Go code review during shutdown — its identity was so strong it couldn't help itself.

### 2. Evidence-Based Debate
CTO is expected to challenge agents with file:line evidence when it disagrees. Silent compliance is not leadership.

### 3. Signal Bus Is Source of Truth
Transcripts decay. The signal bus is durable. Findings live in files, not in conversation memory.

### 4. Closed-Loop Workflows
Once the team starts, don't break out. Every step should be an agent dispatch until the user interrupts or the workflow completes.

### 5. Gate Enforcement
No skipping quality gates. Language expert review after code changes. Deep-qa audit after phases. Deep-reviewer for security-touching changes.

### 6. Self-Improvement
Every session makes the next session smarter via Pattern F. The team learns from its own mistakes.

---

## 11. Performance & Cost Notes

- **Most agents use `opus`** (deepest reasoning) — this is expensive but appropriate for complex work
- **session-sentinel uses `sonnet`** — sufficient for protocol audits
- **Candidates for sonnet** (to optimize cost): cluster-awareness, benchmark-agent, memory-coordinator, observability-expert, database-expert
- **Typical session cost:** 2-8 agent dispatches × opus = significantly more than a single opus conversation, but with 5-10x output quality for complex multi-domain work

### ROI Sweet Spot

The team pays for itself when:
- Work spans 2+ services or languages
- Security is non-trivial
- Code quality matters (shipping to production)
- Architecture decisions are being made
- Incident response has real time pressure

The team is OVER-ENGINEERED for:
- Single-file edits
- Quick questions
- Prototyping/exploration
- Personal projects with no quality bar

---

## 12. Related Documentation

- **TEAM_RUNBOOK.md** — How to operate the team day-to-day
- **TEAM_CHEATSHEET.md** — Quick reference card
- **TEAM_SCENARIOS.md** — Real-world workflow examples with prompts
- **CLAUDE.md** (project root) — The operational protocol the main thread follows

---

*Last updated: 2026-04-18. Team v3.0 — 31 agents, NEXUS protocol, dynamic hiring pipeline, Shadow Mind cognitive layer.*

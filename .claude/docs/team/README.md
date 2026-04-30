# Agent Team — Documentation Index

> Start here. This is the entry point to the team documentation.

---

## What Is This?

The 31-agent team is a layered agent operating system built on Claude Code, designed for complex engineering work across Go (<go-service>), Python (<python-service>), TypeScript (<frontend>), BEAM/Elixir (<beam-service>), and GCP infrastructure. The team is led by a CTO agent with full authority, supported by 28 specialist agents + 2 verification agents (evidence-validator, challenger) + 1 optional intuition-oracle (Shadow Mind surface) organized into 8 tiers, and hardened by protocol-enforcement hooks, a 341-assertion contract test suite, and a data-driven trust ledger.

The team's defining innovations are:
- The **NEXUS Protocol** — a syscall interface that bridges the Claude Code privilege boundary, letting subagents request privileged main-thread operations without directly possessing those tools
- The **Dynamic Domain Expert Acquisition** pipeline (`talent-scout` + `recruiter`) — the team can detect its own coverage gaps and hire new specialist agents through an 8-phase gated pipeline
- The **Shadow Mind** — an optional parallel cognitive layer (Observer + Pattern Computer + Speculator + Dreamer + Pattern Library + intuition-oracle) that offers probabilistic pattern-based guidance via the `[NEXUS:INTUIT]` syscall, delete-to-disable without affecting the conscious team

---

## Documentation Map

### 📘 [TEAM_OVERVIEW.md](TEAM_OVERVIEW.md)
**Start here if you're new.** Comprehensive architecture reference covering:
- Layered OS architecture
- All 31 agents (29 specialists + 2 verifiers) with roles
- NEXUS Protocol deep dive
- Signal bus system
- Pattern F (end-session learning)
- Self-evolution mechanism
- Dynamic hiring pipeline (talent-scout + recruiter)
- Shadow Mind cognitive layer
- Design principles
- Cost/ROI considerations

### 🛠️ [TEAM_RUNBOOK.md](TEAM_RUNBOOK.md)
**Read before every session until internalized.** Day-to-day operational playbook:
- Pre-session checklist
- When to use the team (decision tree)
- Dispatching modes (direct vs team-based)
- Common failure modes & fixes
- Cost management
- Session end (Pattern F)
- Emergency procedures
- Quality gates
- FAQ

### 🃏 [TEAM_CHEATSHEET.md](TEAM_CHEATSHEET.md)
**Print and keep nearby.** Quick reference:
- Agent → domain map
- NEXUS syscall table
- Closing protocol template
- Signal bus files
- Common dispatch patterns
- Activation phrases
- Must-nots
- Health checks

### 🎭 [TEAM_SCENARIOS.md](TEAM_SCENARIOS.md)
**Copy-paste-ready workflows.** 19 real-world scenarios:
1. Production incident response
2. New feature build (full-stack)
3. Security review (pre-merge)
4. Architecture decision
5. Performance optimization
6. Infrastructure change
7. Code quality audit (proactive)
8. Test strategy design
9. Cross-service dependency change
10. Team evolution (meta-work)
11. Simple tasks (anti-pattern)
12. Session start best practice
13. **Verification — Trust But Verify** (evidence-validator workflow)
14. **Adversarial Review of CTO Synthesis** (challenger workflow)
15. **Team Health Monitoring** (contract tests + trust ledger + signal bus drain)
16. **BEAM kernel build / Phase 0 ramp** (beam-architect + elixir-engineer×2 + beam-sre)
17. **Independent Gate 2 validation** (erlang-solutions-consultant retainer)
18. **Systemic capability gap → hiring pipeline** (talent-scout → recruiter → meta-agent)
19. **Shadow Mind intuition for fast-path decisions** (`[NEXUS:INTUIT]` usage)

Each includes: situation, agent chain, exact prompts, expected output, variations.

---

## Reading Order Recommendation

### First-time user
1. TEAM_OVERVIEW.md (understand what the team IS)
2. TEAM_SCENARIOS.md (see how it WORKS in real cases)
3. TEAM_RUNBOOK.md (learn how to OPERATE it)
4. TEAM_CHEATSHEET.md (internalize quick reference)

### Returning user
1. TEAM_CHEATSHEET.md (refresh memory)
2. TEAM_SCENARIOS.md (find the scenario matching today's work)

### During a session
- TEAM_RUNBOOK.md → "Common Failure Modes" if something's off
- TEAM_CHEATSHEET.md → "Activation Phrases" to engage the right agent

---

## Related Project-Root Files

- `../../CLAUDE.md` — The operational protocol the main thread follows. Read this too.
- `../../.claude/agents/*.md` — The 31 agent prompts. Read individual agents when deep-diving.
- `../../.claude/hooks/*.sh` — Protocol enforcement hooks (auto-run by Claude Code).
- `../../.claude/tests/agents/` — Contract test suite (341 assertions across 31 agents).
- `../../.claude/agent-memory/trust-ledger/` — Per-agent trust scorecard.
- `../../.claude/agent-memory/signal-bus/*.md` — Live signal bus (check before/after sessions).
- `../../.claude/agent-memory/shadow-mind/` — Shadow Mind data (observations, patterns, speculations, dreams) — optional, delete-to-disable.

---

## Quick Start (Copy-Paste)

### Start a full team session
```
Use the team. [your specific goal]. CTO has full authority.
```

### Quick single-agent dispatch
```
Review [file] with [agent-name]
```

### End a session
```
Run Pattern F
```

### Emergency
```
INCIDENT: [symptom]. Use the team. Emergency mode.
```

---

## Contributing

This documentation is maintained by the team itself. When you discover new patterns, failure modes, or use cases:

1. Update the relevant doc file directly
2. Add a MEMORY HANDOFF signal if it's a finding worth persisting
3. Add an EVOLUTION SIGNAL if an agent prompt needs improvement
4. meta-agent will process signals during Pattern F

---

*Last updated: 2026-04-18. Team v3.0 with NEXUS protocol, dynamic hiring pipeline, and Shadow Mind cognitive layer.*

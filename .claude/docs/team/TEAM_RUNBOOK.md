# Agent Team — Operational Runbook

> Day-to-day playbook for operating the 31-agent team (29 specialists + 2 verifiers). Read this before every session until you've internalized the patterns.

---

## Pre-Session Checklist

Before starting any significant work session:

- [ ] Check `git status` — is the working tree clean? If not, understand what's uncommitted.
- [ ] Check recent commits: `git log --oneline -5` — know what shipped recently.
- [ ] Check signal bus for pending items: `ls .claude/agent-memory/signal-bus/`
- [ ] Verify `.claude/settings.json` has `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- [ ] If this is a fresh session, consider dispatching `session-sentinel` first for a pre-brief

---

## When to Use the Team (Decision Tree)

```
Is this a code change or multi-step task?
├── NO → Just answer directly. Don't dispatch.
└── YES → Does it touch 2+ services or languages?
    ├── NO, single file/domain → Can you do it in < 5 minutes yourself?
    │   ├── YES → Do it yourself. Use language expert for review ONLY.
    │   └── NO → Dispatch the relevant builder (elite-engineer or frontend-platform-engineer)
    └── YES, multi-service → Is it complex enough to need a plan?
        ├── NO → CTO with parallel builders + guardians
        └── YES → deep-planner first → CTO to execute plan
```

### Red Flags That You're Over-Engineering

- Dispatching for tasks under 50 lines
- Using orchestrator for 1-step work
- Asking benchmark-agent for trivial decisions
- Running Pattern F after a 2-message session

### Red Flags That You're Under-Engineering

- Writing production Go code without `go-expert` review
- Touching auth/security without `deep-reviewer`
- Deploying without `deep-reviewer` + `infra-expert`
- Making architecture decisions without `ai-platform-architect` or `benchmark-agent`

---

## Dispatching Agents — The Two Modes

### Mode 1: Direct Subagent Dispatch (Synchronous)

For single-shot work where you want a complete answer back.

```
Main thread → Agent({subagent_type: "go-expert", prompt: "Review sse.go:142..."})
            ← Returns full response when done
```

**Use when:**
- Single agent can complete the work
- You want the result inline
- No back-and-forth coordination needed

**Examples:**
- Code review: `go-expert`, `python-expert`, `typescript-expert`
- Quick audit: `deep-qa`
- Security review: `deep-reviewer`
- Live state check: `cluster-awareness`

### Mode 2: Team-Based Coordination (Async)

For multi-agent work where agents need to talk to each other.

```
Main thread → TeamCreate({team_name: "feature-x"})
            → Agent({subagent_type: "cto", team_name: "feature-x", name: "cto", run_in_background: true})
CTO (teammate) → SendMessage({to: "lead", message: "[NEXUS:SPAWN] elite-engineer..."})
Main thread → detects NEXUS, spawns elite-engineer as teammate
CTO → SendMessage({to: "elite-engineer", message: "Implement X..."})
... workflow continues via message passing ...
```

**Use when:**
- Multi-step workflow (3+ agents chain work)
- Agents need to iterate (builder → reviewer → builder)
- Long-running background work
- User needs to inject messages mid-workflow

---

## Common Failure Modes & Fixes

### Failure 1: "CTO Trap" — CTO doing work itself

**Symptom:** CTO returns with findings, code changes, or long investigations instead of delegating.

**Cause:** Simple prompts that don't push CTO into delegation mode.

**Fix:** In your prompt, explicitly say "DELEGATE this work — do not do it yourself."

### Failure 2: Signal Bus Not Persisted

**Symptom:** Agent outputs closing protocol signals but signal bus files remain empty.

**Cause:** Main thread summarizes to user without calling Edit to persist.

**Fix:** Check `.claude/agent-memory/signal-bus/*.md` after every agent dispatch. If empty after signals were emitted, the protocol was violated — manually persist or re-dispatch with an explicit "persist your signals to the bus" instruction.

### Failure 3: Teammate Uses Plain Text Instead of SendMessage

**Symptom:** Teammate goes idle but no message arrives in lead's inbox.

**Cause:** Agent prompt lacks Team Coordination Discipline section OR the agent is confused about which mode it's in.

**Fix:** All 31 agent prompts should have this section (validated by the contract test suite). If missing, run `python3 .claude/tests/agents/run_contract_tests.py --agent <name>` to identify the gap. To recover mid-session, SendMessage to the agent reminding them to use SendMessage.

### Failure 4: Agent Returns "Agent tool not available"

**Symptom:** Agent tries to dispatch another agent and fails.

**Cause:** Agent prompt references the old "Agent tool" dispatch pattern.

**Fix:** Agent should use NEXUS syscalls instead. Verify the agent file has the NEXUS PROTOCOL section. If not, add it.

### Failure 5: Pattern F Never Runs

**Symptom:** Signal bus files grow large (20+ entries), `.claude/agent-memory/<agent>/` memories stale.

**Cause:** Sessions end without running Pattern F.

**Fix:** Make Pattern F the last thing every session. Either user-initiated ("run Pattern F") or automatic in the session-end protocol.

### Failure 6: Session-Sentinel Won't Spawn

**Symptom:** Dispatching session-sentinel fails with "Agent type 'session-sentinel' not found" while other agents work fine.

**Cause (confirmed 2026-04-14, commit f5b6e8b):** frontmatter `description:` field containing LITERAL newlines instead of `\n` escape sequences. Multi-line YAML scalar → harness rejects silently. Other agents have single-line descriptions with `\n\n` escapes.

(Earlier diagnoses attributing this to `model:` value were WRONG. The model field was never the issue.)

**Fix:**
1. Run contract test: `python3 .claude/tests/agents/run_contract_tests.py --agent session-sentinel`
2. If `frontmatter.description_single_line` fails → description has literal newlines, collapse to single-line with `\n\n` escapes matching any working agent (e.g., challenger.md)
3. If all contracts pass but agent still not found → session agent catalog is stale, **restart Claude Code** to refresh the agent roster

**Prevention:** contract test `test_frontmatter_description_single_line` runs at pre-commit and catches any agent file with a multi-line description before it reaches the working tree.

---

## Cost Management

### Current Baseline (all-opus)
- Typical session: 4-8 agent dispatches × opus = $$$ per session
- Full remediation campaign: 15-20 dispatches = $$$$

### Optimization Opportunities

| Agent | Current | Suggested | Rationale |
|-------|---------|-----------|-----------|
| session-sentinel | sonnet | sonnet ✅ | Already optimized |
| cluster-awareness | opus | sonnet | kubectl interpretation is low-reasoning |
| benchmark-agent | opus | sonnet | Web research + comparison |
| memory-coordinator | opus | sonnet | File I/O + synthesis |
| observability-expert | opus | sonnet | Review patterns |
| database-expert | opus | sonnet | Review patterns |

**Caveat:** Test each downgrade before committing. Some review agents genuinely need opus depth for edge cases.

### When To Use Haiku

Probably never — we have no positive evidence haiku works for agents in this harness. The "session-sentinel incident" was previously attributed to haiku rejection, but the real cause (commit f5b6e8b) was a YAML description bug. Haiku has not been re-tested.

If you want to experiment, test on a low-risk agent first (e.g., a new dummy agent), verify it registers and produces usable output, THEN consider applying to existing agents. The contract test `test_model_not_haiku` currently BANS haiku as a precaution until we have positive evidence.

---

## Session End Protocol (Pattern F)

At the end of every meaningful session:

```
Main thread dispatches memory-coordinator + meta-agent in PARALLEL
(they operate on different signal bus files, so parallel is safe)
```

**memory-coordinator task:**
- Read memory-handoffs.md
- Consolidate findings into permanent memory files
- Update memory indexes
- Clear processed entries

**meta-agent task:**
- Read evolution-signals.md
- Apply prompt edits where evidence warrants
- Route domain findings to appropriate agent memories
- Clear processed entries

**After Pattern F completes:**
- Signal bus should be empty (just headers + markers)
- New memory files exist in `.claude/agent-memory/<agent>/`
- Possibly updated agent prompts in `.claude/agents/`

---

## Emergency Procedures

### "Production is on fire"

1. Do NOT dispatch full team — time is critical
2. Dispatch `cluster-awareness` FIRST (live state) in parallel with `deep-reviewer` (diagnose)
3. Based on findings, dispatch `elite-engineer` (implement fix) + rapid language-expert review
4. After fix deployed, `observability-expert` for monitoring improvements
5. After incident resolved, `meta-agent` for prompt evolution to prevent recurrence
6. Document in postmortem memory file

### "Agent is stuck in infinite loop"

1. If teammate: SendMessage with `{type: "shutdown_request"}`
2. If subagent: It will time out eventually; if critical, don't wait
3. Dispatch `cto` to diagnose why the agent got stuck
4. meta-agent during Pattern F should evolve the agent to prevent recurrence

### "Signal bus is corrupted"

1. Don't panic — signal bus is secondary. Source of truth is in permanent memory files.
2. Read the last few entries manually to understand what was being tracked
3. Clear the file (keep header + marker)
4. Re-dispatch agents whose work was in-flight

### "User session crashed mid-workflow"

1. Check `~/.claude/teams/` for any orphaned teams
2. Check signal bus for in-flight work
3. On next session, run Pattern F first to drain any accumulated signals
4. Then resume where you left off

---

## Quality Gates (Non-Negotiable)

After implementation:
- **Language expert review** — go-expert, python-expert, typescript-expert (based on language)
- **test-engineer** — verifies test coverage, adds missing tests
- **deep-qa** — code quality, architecture drift, performance

For security-touching work:
- **deep-reviewer** — security assessment mandatory

For deployment:
- **deep-reviewer** — deployment safety validation
- **infra-expert** — manifest review
- **cluster-awareness** — post-deploy verification

Skipping gates = skipping the value of having the team.

---

## Frequently Asked Questions

### Q: Can I dispatch multiple agents in parallel?
**A:** Yes, for independent work. Make multiple Agent tool calls in a single message. Example: go-expert + python-expert + typescript-expert reviewing a multi-service PR.

### Q: How do I stop a background agent?
**A:** SendMessage to it with `{type: "shutdown_request", reason: "..."}`. It will approve and terminate.

### Q: What if CTO and elite-engineer disagree?
**A:** CTO is the arbiter. It should debate with evidence (file:line), gather a second opinion if stakes are high, and decide. Escalate to user if risk is high and consequences severe.

### Q: Can I edit an agent's prompt mid-session?
**A:** Yes, but the running instance has the old prompt in context. Use `[NEXUS:RELOAD agent-name]` to respawn with the new prompt.

### Q: Do agents see each other's closing protocol signals?
**A:** No — signals go to the signal bus (file-based), NOT to other agents' inboxes. Only the main thread or CTO routes them.

### Q: What's the difference between memory and signal bus?
**A:** Signal bus is short-term, cleared by Pattern F. Memory (`.claude/agent-memory/<agent>/`) is permanent. Signals distill into memory.

### Q: Do I need to enable the Shadow Mind?
**A:** No. The Shadow Mind is optional. The 31-agent team operates fully without it. Enable it if you want probabilistic pattern-based guidance via `[NEXUS:INTUIT]`; skip it if you don't.

### Q: How do I hire a new specialist agent?
**A:** You don't hire directly — let the pipeline do it. Dispatch `talent-scout` for an audit; if it produces a requisition with confidence ≥0.70 AND session-sentinel co-signs, dispatch `recruiter` to run the 8-phase pipeline. `meta-agent` performs the atomic registration and `post-hire-verify.sh` is the final gate.

---

## Shadow Mind — Operational Procedures

The Shadow Mind is a parallel non-invasive cognitive layer. Six components, all optional, delete-to-disable. This section covers activation, health checks, querying, disabling, and common failure modes.

### Activation (one-time setup per environment)

```bash
# Observer — continuous tail -F of signal bus
Monitor command="bash .claude/hooks/shadow-observer.sh" persistent=true

# Pattern Computer — every 4 hours at :15 (offset from speculator to avoid write races)
CronCreate schedule="15 */4 * * *" command="python3 .claude/hooks/shadow-pattern-computer.py"

# Speculator — every 4 hours on the hour
CronCreate schedule="0 */4 * * *" command="python3 .claude/hooks/shadow-speculator.py"

# Dreamer — daily at 3am UTC (long-idle window)
CronCreate schedule="0 3 * * *" command="python3 .claude/hooks/shadow-dreamer.py"
```

### Health Check

```bash
# Are components running? Check heartbeat freshness (should be < 24h)
ls -la .claude/agent-memory/shadow-mind/heartbeats/

# Is the Pattern Library populated?
python3 -c "
import json
with open('.claude/agent-memory/shadow-mind/patterns/ngrams.json') as f:
    d = json.load(f)
print(f'transitions: {sum(len(v) for v in d[\"transitions\"].values())}')
print(f'sessions observed: {d[\"sessions_observed\"]}')
"

# Probe the oracle (no-op query; should return OK or INSUFFICIENT_DATA, not ERR)
# From a teammate session:
#   SendMessage to "lead": [NEXUS:INTUIT] health probe
```

### Querying from an Agent

```
SendMessage to "lead":
  [NEXUS:INTUIT] Has <pattern> been observed before? If yes, what typically follows?
```

Main thread routes to `intuition-oracle`, which reads observations + patterns + speculations + dreams and returns an `INTUIT_RESPONSE v1` envelope within ~2s. Returns `INSUFFICIENT_DATA` honestly if pattern data is too thin.

### Disable (per-component or full)

```bash
# Stop Observer (it's a long-running Monitor process)
pkill -f shadow-observer

# Stop scheduled jobs (use CronList to find the IDs)
CronDelete <pattern-computer-cron-id>
CronDelete <speculator-cron-id>
CronDelete <dreamer-cron-id>

# Full Shadow Mind removal (data + scripts)
rm -rf .claude/agent-memory/shadow-mind
rm .claude/hooks/shadow-*.{sh,py}
# Team continues operating — 341/341 contract tests still pass
```

### Failure Modes

- **Observer heartbeat stale > 24h** → oracle returns `SHADOW_MIND_STALE`; restart Observer via Monitor, verify the signal bus path is correct
- **Pattern Computer never ran** → `patterns/*.json` empty or missing; oracle can still answer from observations directly but with LOW confidence. Run the computer manually (`python3 .claude/hooks/shadow-pattern-computer.py`) or schedule via CronCreate
- **Speculator/Dreamer filling disk** → they're additive by design. Add retention cleanup cron if needed:
  ```bash
  find .claude/agent-memory/shadow-mind/speculations -mtime +30 -delete
  find .claude/agent-memory/shadow-mind/dreams -mtime +90 -delete
  ```
- **Oracle returns `NO_DATA`** → Shadow Mind is enabled but no data has been collected yet. Expected on fresh install; populates after a few hours of Observer tailing the signal bus
- **meta-agent rejects a Dreamer proposal** → this is correct behavior. Dreamer proposes, meta-agent is the single writer to `.claude/agents/*.md`. Proposals that don't meet the bar get rejected with a logged reason.

### Non-Invasiveness Invariants

The Shadow Mind's design guarantees:
- No conscious-layer agent prompt is modified by the Shadow Mind
- No signal bus entry is modified by the Shadow Mind (Observer only reads)
- meta-agent retains single-writer authority over `.claude/agents/*.md`
- If the Shadow Mind is disabled mid-session, agents continue operating (NEXUS:INTUIT returns ERR; agents proceed without)
- All 341/341 contract tests pass whether Shadow Mind is enabled or disabled

---

## Hiring Pipeline — Operational Notes

When a new specialist is needed (e.g., AWS/CDK work keeps getting misrouted to `infra-expert`):

1. Dispatch `talent-scout` for a team coverage audit
2. If talent-scout returns a requisition with confidence ≥0.70, ask `session-sentinel` to co-sign (it will only co-sign if it has its own recurring-gap flag for the domain)
3. Dispatch `recruiter` with the signed requisition — it runs the 8-phase pipeline
4. Phase 6: `recruiter` hands the validated draft to `meta-agent` for atomic registration
5. Phase 7: `post-hire-verify.sh` runs automatically; must return `{"status":"verified"}` or registration fails
6. Phase 8: new agent enters `probationary` status in the trust ledger; promotion happens after ≥5 verdicts with refutation rate <25%

**Never edit `.claude/agents/` directly to add a new agent.** The pipeline gates exist for a reason — bypassing them skips contract-test validation, challenger review, and atomic registration. If a new agent is urgently needed, run the pipeline in rapid mode (deep-planner can compress the phases) but don't skip them.

---

## Related Documentation

- **TEAM_OVERVIEW.md** — Architecture and capabilities reference
- **TEAM_CHEATSHEET.md** — Quick reference card
- **TEAM_SCENARIOS.md** — Real-world workflow examples (including Scenario 19: Shadow Mind usage)
- **CLAUDE.md** (project root) — Main thread operational protocol
- **`.claude/agent-memory/shadow-mind/README.md`** — Full Shadow Mind architecture spec

---

*Last updated: 2026-04-18 — v3.0 with 31 agents, hiring pipeline operational notes, and Shadow Mind operational procedures.*

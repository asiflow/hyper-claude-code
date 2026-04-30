# Shadow Mind — Parallel Non-Invasive Cognitive Layer

> A background cognitive substrate that coexists with the 30-agent conscious team without modifying any existing agent prompt, protocol, or memory. **Fully optional, fully disable-able, zero coupling to the conscious layer.**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CONSCIOUS LAYER (30 agents)              │
│   CTO / specialists / verifiers / orchestrator / sentinel   │
│                                                             │
│   signal-bus/   memory/   hooks/   trust-ledger/            │
│                                                             │
└────────────────────────┬────────────────────────────────────┘
                         │  READ-ONLY OBSERVATION
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       SHADOW MIND                           │
│                                                             │
│  (1) Observer Daemon ──► observations/*.jsonl               │
│        tail -F signal-bus, canonical-format parser          │
│                                                             │
│  (2) Pattern Library ──► patterns/{ngrams,                  │
│        grown async       co_occurrences, temporal}.json     │
│                                                             │
│  (3) Speculator ───────► speculations/YYYY-MM-DD-HH.json    │
│        counterfactuals   every 4h via CronCreate            │
│                                                             │
│  (4) Dreamer ──────────► dreams/YYYY-MM-DD-*.yaml           │
│        long-idle analysis, pattern insights                 │
│                                                             │
│  (5) Intuition Oracle ◄─ QUERIED via [NEXUS:INTUIT]         │
│        synthesizes the four inputs above into probabilistic │
│        guidance. Created as a peer agent (parallel rollout) │
│                                                             │
│  heartbeats/{observer,speculator,dreamer}.json              │
│        staleness detection — Oracle reads, responds         │
│        SHADOW_MIND_STALE when last_run > 24h                │
└─────────────────────────────────────────────────────────────┘
```

**Invariant:** Deleting `.claude/agent-memory/shadow-mind/` deletes the entire Shadow Mind. The 30-agent team continues to operate identically — 330/330 contract tests still pass, all hooks still fire, all signal bus writes still land.

---

## Components

### 1. Observer Daemon — `.claude/hooks/shadow-observer.sh`

Continuous process that:
- `tail -F`s the three signal-bus files (`memory-handoffs.md`, `evolution-signals.md`, `cross-agent-flags.md`)
- Parses each new canonical entry `- (YYYY-MM-DD, agent=<name>, session=<id>) <content>`
- Appends a JSON record to `observations/<YYYY-MM-DD>.jsonl`
- Updates `heartbeats/observer.json` every new write and every 60s

**Enable:**
```
Monitor({
  command: "$CLAUDE_PROJECT_DIR/.claude/hooks/shadow-observer.sh",
  persistent: true
})
```

**Disable (any one works):**
- `TaskStop` the Monitor task
- `kill <observer-pid>` (pid stored in `heartbeats/observer.json`)
- `rm .claude/hooks/shadow-observer.sh`
- `rm -rf .claude/agent-memory/shadow-mind/`

### 2. Pattern Library — `patterns/{ngrams,co_occurrences,temporal}.json`

Three JSON files populated by the **Pattern Computer** (component 2b below):
- `ngrams.json` — `P(next_agent | current_agent)` transition probabilities per session
- `co_occurrences.json` — symmetric agent↔agent and signal_type↔signal_type pairs within same session
- `temporal.json` — hour-of-day + day-of-week + per-agent-hour density

Pattern files are atomically rewritten (not append); running the Pattern Computer again is idempotent and always reflects the current observation set.

### 2b. Pattern Computer — `.claude/hooks/shadow-pattern-computer.py`

Python 3 script that reads all `observations/*.jsonl`, derives n-grams + co-occurrences + temporal patterns, and writes atomically to `patterns/*.json`. **Read-only on observations; atomic write on patterns.**

Invocation:
- On-demand: `python3 .claude/hooks/shadow-pattern-computer.py`
- Scheduled: `CronCreate` with `schedule='15 */4 * * *'` (every 4 hours, offset 15 min from Speculator to avoid race)
- Verbose dry-run: `... --dry-run --verbose` (prints top transitions + pairs to stdout without writing)

Thresholds (baked into script, tunable if needed):
- `MIN_NGRAM_COUNT = 2` — at least 2 observed transitions before a pattern is surfaced
- `MIN_COOCC_COUNT = 2` — at least 2 co-occurrences before a pair is counted
- `MIN_TEMPORAL_COUNT = 3` — at least 3 observations in same hour/day bucket

Runtime: <1s for typical observation volumes (<10k records). Updates `heartbeats/pattern-computer.json` on each run. Disable by deleting the script or the CronCreate.

### 3. Speculator — `.claude/hooks/shadow-speculator.py`

Python 3 script that reads last N observations and generates 1-3 counterfactual variants each. Writes to `speculations/<YYYY-MM-DD-HH>.json`. **Never executes any action.**

**Enable (scheduled):**
```
CronCreate({
  cron: "7 */4 * * *",
  prompt: "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/shadow-speculator.py"
})
```

**Enable (on-demand):**
```bash
python3 .claude/hooks/shadow-speculator.py --limit 10
python3 .claude/hooks/shadow-speculator.py --dry-run   # preview, no disk writes
python3 .claude/hooks/shadow-speculator.py --seed 42   # deterministic variant selection
```

**Disable:** `CronDelete <id>` or delete the script file.

Runtime budget: < 30s per invocation.

### 4. Dreamer — `.claude/hooks/shadow-dreamer.py`

Python 3 script that activates during long-idle windows (default: most-recent observation > 1 hour ago). Performs pattern analysis across ~5 sessions of observations and proposes insight candidates in YAML for meta-agent review.

Insight types:
- `collaboration-gap` — active agent pairs that never co-occur
- `debug-loop` — sessions with N+ unresolved findings from the same agent
- `evolution-backlog` — evolution signals repeated ≥3× without being baked in
- `trust-drift` — agents receiving repeated cross-agent flags

**Enable:**
```
CronCreate({
  cron: "3 3 * * *",
  prompt: "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/shadow-dreamer.py"
})
```

**On-demand:**
```bash
python3 .claude/hooks/shadow-dreamer.py --force     # bypass idle check
python3 .claude/hooks/shadow-dreamer.py --dry-run   # inspect insights only
```

**Disable:** `CronDelete <id>` or delete the script. meta-agent retains single-writer authority over `.claude/agents/*.md`; dreams are proposals, never applied automatically.

### 5. Intuition Oracle (created in parallel by meta-oracle)

The single queryable surface for the Shadow Mind. Accessed via the OPTIONAL `[NEXUS:INTUIT]` syscall. This daemon is not created by this infrastructure PR — it is registered here (hooks, contract tests, ledger, docs) so the parallel meta-oracle rollout plugs in without further edits.

---

## Data Schemas

### `observations/<YYYY-MM-DD>.jsonl`
One JSON object per line:
```json
{
  "ts": "2026-04-18T17:45:12Z",
  "signal_date": "2026-04-18",
  "agent": "go-expert",
  "session": "smart-agents-audit",
  "signal_type": "memory_handoff" | "evolution_signal" | "cross_agent_flag",
  "content": "LoopManager.Start() derives from context.Background() — shutdown race.",
  "raw_line": "- (2026-04-18, agent=go-expert, session=smart-agents-audit) ..."
}
```

### `patterns/ngrams.json`
```json
{
  "version": 1,
  "ngrams": {
    "deep-planner -> elite-engineer": {
      "count": 14,
      "last_seen": "2026-04-17T09:12:02Z",
      "sessions": ["living-platform", "smart-agents-audit"]
    }
  }
}
```

### `speculations/<YYYY-MM-DD-HH>.json`
```json
{
  "version": 1,
  "generated_at": "2026-04-18T20:00:07Z",
  "speculations": [
    {
      "id": "spec-abc123def456-0",
      "original_observation_id": "abc123def456",
      "variant_type": "agent_not_dispatched" | "severity_escalation" | "alternative_choice" | "cto_route_alternate",
      "question": "What if agent go-expert had NOT been dispatched during session X?",
      "hypothetical_outcome": "...",
      "confidence_score": 0.55,
      "source_signal_type": "memory_handoff",
      "source_agent": "go-expert",
      "source_session": "smart-agents-audit"
    }
  ]
}
```

### `dreams/<YYYY-MM-DD>-<slug>-<digest>.yaml`
```yaml
id: dream-2026-04-18-debug-loop-abc123
type: collaboration-gap | debug-loop | trust-drift | evolution-backlog
confidence: 0.65
review_status: pending
proposed_to: meta-agent
proposal: "Session X shows N findings from agent Y without resolution. Consider ..."
evidence:
  - {"session": "X", "agent": "Y", "signal_type": "memory_handoff", "count": 3}
generated_at: 2026-04-18T03:04:12Z
```

### `heartbeats/<component>.json`
```json
{
  "last_run": "2026-04-18T17:45:12Z",
  "observations_count": 1247,
  "pid": 12345,
  "component": "observer"
}
```

---

## `[NEXUS:INTUIT]` Syscall (OPTIONAL)

A NEW syscall added to the NEXUS table. No agent is required to use it.

**Request format (teammate sends via SendMessage to `"lead"`):**
```
[NEXUS:INTUIT] <natural-language question>
```

**Response envelope (INTUIT_RESPONSE v1) from the kernel or oracle:**
```
[NEXUS:OK] INTUIT_RESPONSE v1
{
  "status": "OK" | "SHADOW_MIND_STALE" | "NO_DATA",
  "query": "<original question>",
  "answer": "<human-readable answer or best-effort probabilistic guidance>",
  "confidence": 0.0-1.0,
  "evidence_ids": ["spec-...", "dream-...", "obs:2026-04-18#42"],
  "pattern_types_consulted": ["ngram", "co_occurrence", "temporal"],
  "staleness_hours": 0.0
}
```

**Staleness rule:** If `heartbeats/observer.json.last_run` is older than 24h, the oracle MUST respond with `status: SHADOW_MIND_STALE` rather than serving stale patterns. This preserves trust calibration.

**Optional-to-consult:** Conscious-layer agents work identically whether they call `[NEXUS:INTUIT]` or not. Shadow Mind never interrupts a dispatch chain; it is advisory only.

---

## Disable-ability Guarantees

| Target | Command | Effect |
|---|---|---|
| Observer only | `kill <observer-pid>` (from `heartbeats/observer.json`) | Signal-bus tail stops; no new observations. Existing data preserved. |
| Speculator only | `CronDelete <speculator-id>` | No new counterfactuals generated. |
| Dreamer only | `CronDelete <dreamer-id>` | No new dreams generated. |
| All background components | Kill observer + CronDelete both schedules | All generators idle; observations/patterns frozen. |
| Entire Shadow Mind | `rm -rf .claude/agent-memory/shadow-mind/` + remove hook scripts | Layer fully removed. **30-agent team still passes 330/330 contract tests.** |

**Zero-coupling verification:** Run the contract test suite with and without `shadow-mind/` present. Counts and outcomes are identical.

---

## Operational Notes

- All reads of signal-bus files are read-only (`tail -F`, `grep`, `cat`). Shadow Mind never writes to `signal-bus/`, `memory-*`, or `trust-ledger/`.
- All Shadow Mind outputs live under `shadow-mind/`. Nothing escapes this namespace.
- Observer, Speculator, and Dreamer each have independent failure modes. If one crashes, the others continue.
- The oracle (`intuition-oracle`) is the ONLY component that reads across subsystems — it is pure-read, advisory, and non-interrupting.
- meta-agent retains single-writer authority over `.claude/agents/*.md`. Dreams are proposals, not applied changes.

## Related

- NEXUS protocol: `CLAUDE.md` → "NEXUS PROTOCOL — Team Operating System Layer"
- Signal bus protocol: `.claude/agent-memory/signal-bus/`
- Trust ledger: `.claude/agent-memory/trust-ledger/ledger.py`
- Agent contracts: `.claude/tests/agents/run_contract_tests.py`

# Agent Trust Ledger

Per-agent accuracy scorecard. Records verdicts from `evidence-validator` and challenge outcomes from `challenger`, producing a trust weight (0-1) that CTO can use to weight future findings.

## Why It Exists

The 21-agent team produces more findings than one human can verify. Without calibration, the team treats all findings equally. Reality: some agents are more reliable than others for specific domains. The trust ledger turns this tacit knowledge into explicit data.

Over time:
- High-accuracy agents get faster pass-through (less verification overhead)
- Low-accuracy agents get aggressive validation (more evidence-validator dispatches)
- Domain-specific trust emerges (e.g., go-expert might be 0.95 on concurrency, 0.7 on design)

## Schema

One JSON file per agent: `<agent-name>.json`

```json
{
  "agent": "go-expert",
  "domain": "Go language + Go services",
  "model": "opus",
  "findings": {
    "total": 12,
    "confirmed": 9,
    "partially_confirmed": 2,
    "refuted": 1,
    "unverifiable": 0
  },
  "challenges": {
    "received": 3,
    "survived": 2,
    "lost": 1
  },
  "accuracy_score": 0.833,
  "trust_weight": 0.893,
  "history": [
    {"ts": "2026-04-14T...", "kind": "verdict", "id": "F-42", "outcome": "CONFIRMED"}
  ],
  "notes": ""
}
```

**accuracy_score** = (confirmed + 0.5 × partially_confirmed) / (confirmed + partially + refuted)
Does not count unverifiable (they're noise, not wrong).

**trust_weight** = Bayesian-blended accuracy with a prior of 5 observations at 0.9 (slight optimism). New or low-sample agents land near 0.9 until they earn or lose trust from data.

## Usage

```bash
# Record a CONFIRMED verdict for a go-expert finding
./ledger.py verdict --agent go-expert --verdict CONFIRMED --finding-id F-42

# Record a challenger outcome (target survived the challenge)
./ledger.py challenge --agent cto --outcome SURVIVED --challenge-id C-13

# See the full record for an agent
./ledger.py show --agent go-expert

# Get current trust weight (machine-readable)
./ledger.py weight --agent go-expert

# See team-wide standings
./ledger.py standings
```

## Integration Points

### evidence-validator → ledger
Every time evidence-validator produces a verdict on a finding, the source agent's record should be updated:

```bash
./ledger.py verdict --agent <source-agent> --verdict <CONFIRMED|...> --finding-id <finding-ref>
```

### challenger → ledger
Every time a challenge completes:

```bash
# If target successfully rebutted the challenge:
./ledger.py challenge --agent <target> --outcome SURVIVED

# If the challenge forced target to revise:
./ledger.py challenge --agent <target> --outcome LOST
```

### CTO synthesis
When CTO aggregates findings from multiple agents, it should weight each by `trust_weight`:

```bash
# In CTO's logic:
WEIGHT_GO=$(./ledger.py weight --agent go-expert)
WEIGHT_PY=$(./ledger.py weight --agent python-expert)
# Use these to weight conflicting findings during synthesis.
```

## Interpreting Trust Weights

| Weight Range | Meaning | CTO Behavior |
|--------------|---------|--------------|
| 0.95-1.00 | Excellent track record | Accept findings with light review |
| 0.85-0.95 | Good (default for new agents) | Standard review gate |
| 0.70-0.85 | Notable refute history | Always dispatch evidence-validator on HIGH findings |
| <0.70 | Low reliability | Evidence-validator on ALL findings; consider prompt evolution |

## Decay

The ledger has no time decay. A refute from 6 months ago still counts. This is intentional — prompt quality issues that caused refutes in the past are usually still present unless meta-agent evolved the prompt. If an agent's prompt is significantly updated (major version bump), manually reset its ledger to allow re-calibration:

```bash
./ledger.py reset --agent go-expert  # TODO: not implemented yet
```

For now, delete the JSON file manually.

## History Bounds

Each agent's `history` array is capped at 200 entries. Old entries roll off. The aggregate counts are never reset (they reflect all-time accuracy).

## Adversarial Consideration

If meta-agent or CTO tries to game the ledger by avoiding dispatching evidence-validator on weak claims, the trust weights become stale. This is mitigated by:
- `session-sentinel` auditing the ratio of HIGH findings to evidence-validator dispatches
- `challenger` catching reasoning gaps that evidence-validator can't (static verification vs. adversarial reasoning)

## Current State

Run `./ledger.py standings` to see current standings. Empty ledger → no data yet. As evidence-validator and challenger are used, data accumulates.

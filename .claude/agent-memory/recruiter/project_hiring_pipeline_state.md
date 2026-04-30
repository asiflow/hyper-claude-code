---
name: hiring_pipeline_state
description: Current state of the hiring pipeline — in-flight requisitions, completed hires, retirements.
type: project
---

# Hiring Pipeline State

**Last updated:** 2026-04-19
**Total hires executed by recruiter:** 1
**Total retirements executed by recruiter:** 0
**Current in-flight requisitions:** 0

## In-Flight Requisitions

_(none)_

## Completed Hires

### 1. `elixir-kernel-engineer` — 2026-04-19 (first real hire, pipeline validation)

```yaml
requisition_id: req-2026-04-19-elixir-kernel-engineer
slug: elixir-kernel-engineer
registered_on: 2026-04-19
status: probationary
domain: elixir-kernel-engineering (Plane 1 BEAM solo-build + surge throughput)
scope: single-slot, permanent (not a surge-only hire)

talent_scout_scan:
  composite_confidence: 0.365
  standard_threshold: 0.40 (would normally SUPPRESS)
  overridden_by: user_authoritative_directive
  override_documented: true (cosign_waiver_reason field populated, not silent bypass)

recruiter_pipeline_execution:
  phase_1_requisition_parse: PASS
  phase_2_domain_research: PASS (WebSearch + WebFetch + adjacent-agent scar-tissue mining)
  phase_3_inherit_context: PASS
  phase_4_draft_synthesis: PASS (AGENT_TEMPLATE.md scaffold)
  phase_5_contract_tests: PASS (first iteration)
  phase_6_challenger_review: APPROVED_WITH_NOTES (verdict-id: ch-ekr-1)
  phase_7_handoff_to_meta_agent: PASS (atomic registration)
  phase_8_probation_initialization: PASS

cto_adjudication:
  decision: path_B (separate agent file)
  alternative_rejected: path_A (SCALE=3 on elixir-engineer)
  rejection_rationale: >
    elixir-engineer.md has 10+ hardcoded dyadic-pair assumptions (count=2 baked in,
    two-party disagreement matrix, hardcoded ee-1/ee-2 addressing). SCALE=3 would
    break the pair-protocol's hardcoded assumptions without a prompt rewrite.
  citations: 10 line-level citations from elixir-engineer.md

probation_config:
  dispatch_cap: 5
  max_refutation_rate: 0.4
  min_trust_weight_after_10: 0.5
  first_3_dispatches_gate:
    agent: beam-architect
    mode: pre-merge
    rationale: trust-calibration compensation for absence of pre-merge dyadic review

probation_state:
  dispatches_completed: 0
  current_refutation_rate: null
  current_trust_weight: 0.90 (bootstrap)
  after_5_dispatches_evaluation: in_progress
  after_10_dispatches_evaluation: in_progress
  notes: >
    Foundation window not yet open in the adopter platform; probation dispatch
    cycle begins when the hired agent is first routed a real task.

pipeline_validation: COMPLETE
operational_trust_calibration: IN_PROGRESS

distribution_specificity_note: |
  This hire was executed in the parent production platform this generalized
  distribution is derived from. The hired agent's implementation is tightly
  coupled to that platform's BEAM Plane 1 topology and is NOT shipped in the
  generic 31-agent distribution. The requisition, probation YAML, trust-ledger
  entry, and challenger verdict are preserved as proof-of-pipeline-execution
  artifacts. Future hires executed by adopters of this distribution are
  recorded in-place in the adopter's own repo.
```

## Retirements

_(none)_

## Aborted Requisitions

_(none)_

## Pattern Observations

### 2026-04-19 — First hire reflections

- **The user-override path is load-bearing.** Composite confidence 0.365 was below the standard 0.40 auto-initiate threshold. The right behavior was NOT to suppress the requisition; it was to recognize the explicit user directive as authoritative and auto-initiate with a documented waiver (`cosign_waiver_reason` field). Silent bypasses would have been a protocol violation. This pattern should be emphasized in `talent-scout` and `recruiter` prompts — the algorithmic threshold is advisory to the user, not a gate over the user.

- **Path A vs Path B adjudication is a generalizable pattern.** When a requisition could be satisfied by extending an existing agent's scale vs. creating a new agent file, `recruiter` should evaluate BOTH paths and surface the trade-off to CTO before drafting. Citations from the existing agent file (e.g., hardcoded count values, protocol assumptions) are required evidence — not prose.

- **Probation config should be stricter when pre-hire confidence was below the standard threshold.** The `elixir-kernel-engineer` probation adds a first-3-dispatches `beam-architect` pre-merge gate specifically to compensate for the lower confidence floor. This "trust-calibration compensation" pattern should be added to the probation-config template for future below-threshold hires.

### Schema notes for future entries

See the `elixir-kernel-engineer` entry above as the canonical shape. Fields that MUST appear in every completed-hire record: `requisition_id`, `slug`, `registered_on`, `status`, `recruiter_pipeline_execution.phase_1` through `phase_8`, `probation_config`, `probation_state`, and any `cto_adjudication` record if Path A vs Path B (or similar) arose.

# Team — Real-World Scenarios

> Copy-paste-ready workflows. Each scenario includes the situation, agent chain, exact prompts, expected output, and common variations.

---

## Scenario 1: Production Incident Response

### Situation
Users report that <go-service> sessions drop after 5 minutes. SSE connections close unexpectedly. You have 30 minutes before the CEO asks for a status update.

### Agent Chain
```
cluster-awareness + deep-reviewer (parallel)
  → decision: hotfix or rollback?
  → elite-engineer (implement fix)
  → go-expert (rapid review)
  → infra-expert (deploy)
  → cluster-awareness (verify)
  → observability-expert (prevent recurrence)
  → meta-agent (evolve prompts)
```

### Starting Prompt to Main Thread
```
INCIDENT: <go-service> sessions drop after 5 minutes in production.
Users reporting SSE connection closures. Started ~15 min ago.

Use the team. CTO has full authority. Emergency mode — skip pre-brief,
immediate triage.
```

### CTO's First Move (Expected)
CTO will NEXUS-spawn cluster-awareness + deep-reviewer in parallel:

```
[NEXUS:SPAWN] cluster-awareness | name=ca-incident | prompt=Get live <go-service> pod status, recent restart count, OOMKill events, HPA state, Redis connectivity. Report in < 2 min.

[NEXUS:SPAWN] deep-reviewer | name=dr-incident | prompt=Debug SSE session drop at 5-minute mark in the Go service. Check sse.go lifecycle, Redis TTL, session state machine, recent commits for regressions. File:line evidence required.
```

### After Findings Arrive
CTO synthesizes: "Is this infra (Redis died) or code (SSE bug)?" Based on evidence:
- If infra: `infra-expert` to remediate
- If code: `elite-engineer` to fix + `go-expert` review + infra-expert for deploy

### Common Variations
- **Urgent + uncertain cause:** Use 3-agent parallel — cluster-awareness + deep-reviewer + observability-expert
- **Known cause, just fix:** Skip diagnosis, jump to elite-engineer + review + deploy
- **Systemic issue:** Add deep-planner after fix to plan longer-term remediation

### After-Action
```
Dispatch meta-agent to analyze this incident and update relevant agent
prompts to prevent recurrence. Store the incident in cto memory.
```

---

## Scenario 2: New Feature Build (Full-Stack)

### Situation
Product asks: "Add file upload with progress tracking, virus scanning, and 100MB limit to <go-service> and expose in <frontend>."

### Agent Chain
```
deep-planner (produces plan with agent assignments)
  → cto (review + approve)
  → orchestrator (execute)
    → ai-platform-architect (design upload architecture)
    → elite-engineer (Go backend + Python scanner)
    → frontend-platform-engineer (React component + streaming hook)
    → go-expert + python-expert + typescript-expert (reviews in parallel)
    → test-engineer (tests)
    → deep-qa (quality audit)
    → deep-reviewer (security — uploads are dangerous)
    → infra-expert (K8s manifest changes, GCS bucket)
    → database-expert (file metadata schema)
    → api-expert (GraphQL mutations + subscriptions)
  → cto (final status)
```

### Starting Prompt to Main Thread
```
Feature request: Add file upload to <go-service> + <frontend>.
Requirements: progress tracking, virus scanning, 100MB limit,
integrates with existing session model.

Use the team. Full workflow: deep-planner → CTO review → orchestrator
executes → all gates.
```

### deep-planner Produces (Expected)
A plan document with:
- Phase breakdown (design → backend → frontend → tests → deploy)
- Dependency graph (what blocks what)
- Risk register (security, performance, UX)
- Agent assignments per task
- Acceptance criteria per phase

### CTO Review (Expected)
Either approves the plan verbatim, requests changes ("add rate limiting tests"), or replans if scope is wrong.

### Orchestrator Execution
Orchestrator NEXUS-spawns agents phase-by-phase, enforces gates, reports consolidated status.

### Common Variations
- **Smaller feature (< 3 services):** Skip orchestrator, CTO coordinates directly
- **Novel architecture:** Add benchmark-agent between plan and execute
- **Time-critical MVP:** Cut guardian agents, add them in follow-up pass

---

## Scenario 3: Security Review (Pre-Merge)

### Situation
A PR changes authentication middleware and session handling. 400 lines across 6 files. Needs sign-off before merge.

### Agent Chain
```
deep-reviewer (security audit)
  + go-expert OR python-expert OR typescript-expert (language review, in parallel)
  + test-engineer (test coverage verification, in parallel)
→ cto (synthesize findings)
→ decision: approve / conditional approve / reject
```

### Starting Prompt
```
PR review required — changes to auth middleware + session handling.
Files: backend/<go-service>/internal/adapters/http/middleware.go,
backend/<go-service>/internal/application/session_service.go,
<frontend>/src/hooks/useAuth.ts (6 files total, ~400 lines).

Use the team in parallel: deep-reviewer for security, go-expert for
backend idiom, typescript-expert for frontend, test-engineer for
coverage. Then CTO synthesizes final recommendation.
```

### Expected Output Shape
```
DEEP-REVIEWER:
  HIGH: Potential auth bypass at middleware.go:142 if header is missing
  MEDIUM: Session fixation window during token refresh
  LOW: Logging includes token prefix (consider removing)

GO-EXPERT:
  LOW: Error wrapping inconsistent (errors.Wrap vs fmt.Errorf %w)

TYPESCRIPT-EXPERT:
  MEDIUM: useAuth has unstable reference causing downstream re-renders
  LOW: Missing React 19 'use' hook opportunity

TEST-ENGINEER:
  MEDIUM: No test for auth bypass edge case (deep-reviewer HIGH #1)
  LOW: Session fixation test missing

CTO VERDICT:
  REJECT — 1 HIGH from deep-reviewer must be fixed before merge.
  Re-dispatch elite-engineer with findings, then re-review.
```

### Common Variations
- **Simple PR (1 file, < 50 lines):** Single language expert, no parallel fan-out
- **Config-only change (K8s manifests):** infra-expert + deep-reviewer, no language experts needed
- **Database migration:** database-expert + deep-reviewer for migration safety

---

## Scenario 4: Architecture Decision

### Situation
Team is split on whether to refactor the session state machine or add a recovery layer on top. High impact, difficult to reverse.

### Agent Chain
```
memory-coordinator (what's the team know?)
  + benchmark-agent (how do competitors solve this?)
  + ai-platform-architect (first-principles analysis)
  + go-expert (Go-specific concerns for refactor)
→ cto (debate + recommendation)
→ User decides
→ deep-planner (plan the chosen approach)
```

### Starting Prompt
```
Strategic decision needed: refactor session state machine OR add
recovery layer on top?

Context: current state machine is brittle, recovery is difficult,
but refactor is 2-3 week effort with high regression risk.

Use the team for analysis. Parallel: memory-coordinator (team history),
benchmark-agent (how do Cursor/Devin/Manus handle session recovery?),
ai-platform-architect (first-principles design), go-expert
(Go-specific refactor risks). CTO synthesizes with debate protocol.
```

### Expected CTO Output
```
OPTION A: REFACTOR
  Pros: [evidence-backed]
  Cons: [evidence-backed]
  Cost: 2-3 weeks, 3 services affected
  Reversibility: LOW

OPTION B: RECOVERY LAYER
  Pros: [evidence-backed]
  Cons: [evidence-backed]
  Cost: 1 week, 1 service affected
  Reversibility: HIGH

BENCHMARK INTEL: Cursor uses B (wrapper-based recovery), Devin uses A
(rebuilt state machine in v2), Manus uses hybrid.

CTO RECOMMENDATION: Start with B (low-reversibility dominated by
high-reversibility tactic per safe-evolution principle), monitor for
3 weeks, escalate to A only if B proves insufficient.

SECOND OPINION: ai-platform-architect agrees. go-expert flags that
any refactor (A) needs dedicated race-condition test harness.

USER DECISION REQUIRED.
```

---

## Scenario 5: Performance Optimization

### Situation
The Go service dashboard feels sluggish. Render cycles, bundle size, state management all suspects. Need systematic analysis.

### Agent Chain
```
deep-qa (performance diagnosis across all domains)
  → typescript-expert (deep dive on React render cycles if frontend)
  OR go-expert (backend perf if Go)
  OR database-expert (query perf if DB)
→ elite-engineer (implement fixes)
→ test-engineer (perf regression tests)
→ deep-qa (verify improvement)
```

### Starting Prompt
```
Performance issue: <go-service> dashboard feels slow.
Symptoms: ~2s time-to-interactive, visible jank during typing,
500ms+ on message send.

Use the team. deep-qa for systematic diagnosis first, then
domain-specific expert for deep dive based on findings. Then
elite-engineer to fix, test-engineer for perf regression test.
```

### deep-qa Finds (Example)
```
PERFORMANCE FINDINGS:
  FRONTEND (HIGH): ChatPanel re-renders 12x per message due to
                   unstable selector in useSmartAgentsStream hook
  BACKEND (LOW): SSE event serialization allocating in hot path
  DB (LOW): Session lookup missing index on (user_id, created_at)
```

### Follow-Up Dispatch
```
Dispatch typescript-expert to deep-dive ChatPanel rendering
(deep-qa HIGH finding). Then elite-engineer for fix.
```

---

## Scenario 6: Infrastructure Change

### Situation
Migrating from GKE Standard to GKE Autopilot. Need to update 20 K8s manifests, review networkpolicies, cert-manager setup, HPA configs.

### Agent Chain
```
cluster-awareness (baseline current state)
  → infra-expert (design migration + review all manifests)
  → deep-reviewer (security implications)
  → elite-engineer (apply manifest changes)
  → infra-expert (second review of changes)
  → cluster-awareness (dry-run verify in staging)
  → cto (approval for production)
  → cluster-awareness (production verify)
```

### Starting Prompt
```
Migrating <go-service> from GKE Standard to Autopilot.
Scope: 20 K8s manifests across backend/<go-service>/k8s/.

Use the team. cluster-awareness baseline first, infra-expert designs
migration, deep-reviewer for security, elite-engineer applies changes,
infra-expert reviews, cluster-awareness verifies in staging.
DO NOT touch production until I approve.
```

### Critical Gate
CTO should NOT autonomously deploy to prod. "any action with HIGH
blast radius + LOW reversibility" is SUPERVISED authority — requires
user approval.

---

## Scenario 7: Code Quality Audit (Proactive)

### Situation
Quarterly code health check. Want a comprehensive assessment across
all services before next major release.

### Agent Chain
```
deep-qa (quality + architecture + perf + tests)
  + deep-reviewer (security sweep)
  (parallel) →
  memory-coordinator (synthesize with prior audits)
  → cto (prioritize findings by impact)
  → deep-planner (if remediation plan needed)
```

### Starting Prompt
```
Quarterly code health audit.
Scope: all of <go-service> + <python-service> + <frontend>.

Use the team. Parallel: deep-qa for comprehensive quality/arch/perf/test
audit, deep-reviewer for security sweep. Then memory-coordinator
compiles findings with prior audits. Then CTO prioritizes.

Report with severity ranking and a recommended remediation plan.
```

---

## Scenario 8: Test Strategy Design

### Situation
New service being built. Need test strategy before implementation
starts. Must cover unit, integration, E2E, contract between services.

### Agent Chain
```
test-engineer (designs strategy + test pyramid)
  → api-expert (contract test design if services cross boundaries)
  → deep-planner (schedule test development)
  → elite-engineer / test-engineer (implement test framework)
```

### Starting Prompt
```
New service: orchestrator-v2 in Go. Touches PostgreSQL, Redis,
<go-service> via GraphQL, exposed via SSE.

Use the team. test-engineer designs the full test strategy (unit +
integration + contract + E2E + chaos). api-expert contributes
contract test design for GraphQL boundary. deep-planner schedules
test development parallel to feature work.
```

---

## Scenario 9: Cross-Service Dependency Change

### Situation
Changing a GraphQL schema in the Go service that <frontend> consumes.
Need to coordinate the change without breaking the frontend.

### Agent Chain
```
api-expert (analyze schema change impact)
  + frontend-platform-engineer (assess frontend impact, in parallel)
  → deep-planner (coordination plan: backend-compatible phase → frontend update → breaking removal)
  → orchestrator (execute phases)
```

### Starting Prompt
```
Schema change needed: <go-service> GraphQL `Session` type needs new
required field `lastActivityAt`. <frontend> uses this type in 8 places.

Use the team. api-expert analyzes federation + backward compatibility.
frontend-platform-engineer assesses frontend impact. deep-planner
designs zero-downtime migration. orchestrator executes.
```

---

## Scenario 10: Team Evolution (Meta-Work)

### Situation
You've noticed the team keeps missing cross-service impact. Want to
make the team smarter about it.

### Agent Chain
```
meta-agent (analyze team failure patterns)
  → benchmark-agent (how do other multi-agent systems handle this?)
  → meta-agent (apply prompt evolutions)
  → validate in next session
```

### Starting Prompt
```
Team improvement request: the team keeps missing cross-service impact
(e.g., backend changes that break the frontend). Analyze why and
evolve the relevant prompts to close the gap.

Use meta-agent for pattern analysis, benchmark-agent for how
other systems solve this. Then meta-agent applies prompt evolutions.
Document what changed and why.
```

### Expected meta-agent Output
```
PATTERN ANALYSIS (last 5 sessions):
  - 3 of 5 sessions had backend changes without frontend impact check
  - Root cause: no mandatory "cross-service impact" signal in closing
    protocol
  - elite-engineer prompt doesn't explicitly require impact analysis

EVOLUTION APPLIED:
  - Added new CROSS-SERVICE IMPACT section to closing protocol template
  - Updated elite-engineer prompt: mandatory impact analysis for any
    API contract change
  - Updated orchestrator prompt: auto-dispatch frontend-platform-engineer
    if api-expert flags contract change

BENCHMARK INTEL: LangGraph uses "change propagation" explicit graph;
CrewAI uses per-agent change-listener pattern. Our signal-bus approach
is closer to LangGraph — single mandatory signal per phase.

VERIFICATION: Run a test session in next 24h to confirm improvement.
```

---

## Scenario 11: Using the Team for Simple Tasks (Anti-Pattern)

### Situation
"Just fix this typo in the README."

### Don't Do This
```
Don't: dispatch CTO for a typo fix
Don't: create a team for a 1-line change
Don't: run Pattern F after a 2-message session
```

### Do This
```
Main thread → Edit({file_path: "README.md", ...})
```

No dispatch. No team. The team is for hard problems, not easy ones.

---

## Scenario 12: Session Start Best Practice

### When Starting Fresh
```
"Starting a work session on [specific goal]. Use session-sentinel
for a pre-brief, then I'll engage CTO or dispatch directly based
on the brief."
```

### session-sentinel Returns
```
PRE-SESSION BRIEF:
  Working tree: [N modified files, summary]
  Recent commits: [last 5]
  Signal bus: [pending entries count]
  Team memory highlights relevant to [your goal]: [summary]
  Known open issues: [from cross-agent-flags]
  Recommended first action: [evidence-based]
```

Then you have context to make a good dispatch.

---

## Scenario 13: Verification — Trust But Verify

### Situation
go-expert just reported a HIGH-severity finding claiming `orchestrator.go:268-277 force-resets stuck-streaming sessions without IsActive guard`. Before dispatching elite-engineer to fix it (which takes 30+ min), you want to verify the claim is real, not a hallucination or stale finding.

### Agent Chain
```
evidence-validator (verify the specific claim)
→ trust ledger update (record verdict)
→ if CONFIRMED → elite-engineer (remediate)
→ if REFUTED → meta-agent (evolve go-expert prompt to reduce false positives)
→ if PARTIALLY_CONFIRMED → dispatch with caveats
```

### Starting Prompt
```
Verify go-expert's finding before we act on it:

CLAIM SOURCE: go-expert
CLAIM SEVERITY: HIGH
CLAIM LOCATION: backend/<go-service>/internal/application/orchestrator.go:268-277
CLAIM TEXT: Force-resets stuck-streaming sessions without LoopManager.IsActive() guard — can spawn concurrent goroutines for the same session
IMPACT: State machine invariant violation, duplicate messages, corrupted history

Dispatch evidence-validator.
```

### evidence-validator Returns (Example)
```
VERDICT: CONFIRMED

EVIDENCE:
  Location (current): backend/<go-service>/internal/application/orchestrator.go:268-277
  Source quoted:
    ```
    268  if session.Status == agent.SessionStatusStreaming {
    269      o.logger.Warn().Str("session_id", session.ID).Msg("session stuck in streaming state, resetting to active")
    270      session.Status = agent.SessionStatusActive
    ...
    ```
  No LoopManager.IsActive() call exists between the guard and the reset.

ANALYSIS:
  The claim accurately describes current code. The reset runs unconditionally
  when status is Streaming, without checking whether a loop goroutine is
  actively writing to the same session. This matches the claim.

CAVEATS:
  Static inspection confirms the missing guard. Runtime verification
  (reproducing the race) would require an actual concurrent workload.

SEVERITY ASSESSMENT:
  Claimed: HIGH
  Assessed: HIGH (concurrent writes to same session is a known state
  machine invariant violation)
```

### Follow-Up
Record in trust ledger:
```bash
./.claude/agent-memory/trust-ledger/ledger.py verdict --agent go-expert --verdict CONFIRMED --finding-id orchestrator-stuck-reset
```

Then dispatch elite-engineer with the finding as context.

---

## Scenario 14: Adversarial Review of CTO Synthesis

### Situation
CTO just synthesized a recommendation: "Migrate to gRPC for service-to-service communication. Cost: 4 weeks of engineering. Benefit: 30% latency reduction, type safety." You want to stress-test this before committing 4 weeks of effort.

### Agent Chain
```
challenger (adversarial review along 5 dimensions)
→ CTO must respond to the challenge
→ user reviews both + decides
```

### Starting Prompt
```
Challenge the CTO's recommendation:

CTO'S RECOMMENDATION:
"Migrate service-to-service from GraphQL Federation to gRPC. Projected
cost: 4 eng-weeks. Projected benefit: 30% latency reduction, compile-time
type safety between services. Risk: moderate (well-understood migration).
Alternative considered: HTTP/3 with JSON — rejected as smaller win."

Dispatch challenger to attack this along the 5 dimensions (steelman the
alternative, expose assumptions, attack evidence, find missed cases,
surface downstream impact).
```

### challenger Returns (Example Structure)
```markdown
## Challenge Summary
Target: CTO — gRPC migration recommendation
Severity of challenge: STRONG (target should revise)

## Counter-Argument (Steelman HTTP/3 + JSON)
The CTO understated HTTP/3's wins. At our service count (14), the
operational cost of managing .proto contracts + codegen pipelines
likely exceeds gRPC's transport gains. HTTP/3 + JSON Schema has 80%
of the benefit at 20% of the migration cost.

## Hidden Assumptions
1. CTO assumes 30% latency win carries to our workload...
2. CTO assumes team will maintain .proto schemas discipline...
3. CTO assumes 4-week estimate is stable...

## Evidence Weaknesses
- The "30% latency reduction" number — from which benchmark? Grpc.io
  synthetic, or production data from a similar service?
- "Well-understood migration" — by whom on our team? Neither
  <go-service> nor <python-service> currently uses gRPC.

## Missed Cases
- Streaming: how does gRPC handle long-lived SSE patterns we use?
- Debugging: chrome devtools don't inspect gRPC — how do frontend
  engineers debug contract issues?
- Multi-language: our 3 languages × 14 services = 42 codegen
  configurations to maintain...

## Downstream Impact
- Frontend: can't call backend services directly via gRPC (grpc-web
  is lossy) — forces a gateway layer
- Observability: distributed tracing needs gRPC-aware instrumentation...

## Required Revisions
- Benchmark latency against HTTP/3 + JSON under OUR workload
- Scope: which services first? Sequencing matters
- Fallback plan: can we revert if engineering velocity drops?
```

### Outcome
CTO now must respond to the challenge. Possible outcomes:
- **Revise:** CTO agrees with challenger, updates recommendation
- **Defend:** CTO rebuts with new evidence, recommendation stands (trust ledger: CTO challenge SURVIVED)
- **Escalate:** CTO presents both to user for decision

### Why This Matters
Without challenger, the user would see only CTO's clean recommendation and likely accept it. With challenger, the user sees both the recommendation AND the strongest critique — much better-informed decision, and catches CTO drift before 4 weeks are spent.

---

## Scenario 15: Team Health Monitoring

### Situation
Weekly team health check. Want to see which agents are performing well, which have low trust, which need prompt evolution.

### Commands (No Agent Dispatch Needed)

```bash
# Check current trust standings
./.claude/agent-memory/trust-ledger/ledger.py standings

# Run contract tests against all agents
python3 .claude/tests/agents/run_contract_tests.py

# See recent NEXUS syscall activity
tail -30 .claude/agent-memory/signal-bus/nexus-log.md

# Signal bus drain status (should be empty post-Pattern F)
wc -l .claude/agent-memory/signal-bus/*.md
```

### Weekly Ritual
1. Run `standings` — identify agents with trust_weight < 0.85
2. Dispatch meta-agent with: "Evolve [low-trust agents] based on their trust ledger history"
3. Run contract tests — any regressions from recent edits
4. Signal bus check — if entries exist, run Pattern F

---

## Scenario 16: BEAM Kernel Build / Phase 0 Ramp

### Situation
You're standing up a BEAM-based stateful kernel (or "Plane 1") for a living-platform-style service: gen_statem session topology, Horde for distributed process registry, Ra for shared-state checkpoints, libcluster for node discovery on a GKE StatefulSet, and Rust NIFs for crypto hot paths. The existing `elite-engineer` + `ai-platform-architect` stack has no Elixir/OTP/Horde/Ra depth — dispatching them produces generic-quality code. The BEAM tier exists precisely for this.

### Agent Chain
```
beam-architect (topology design — OTP tree, Horde/Ra/pg choices, Rust NIF surface)
  ↓ (design approved)
[NEXUS:SCALE] elixir-engineer count=2 → ee-1, ee-2 (pair-dispatched implementation)
  ↓ (in parallel)
beam-sre (libcluster config, StatefulSet manifest, SIGTERM graceful-shutdown wiring)
  ↓ (integration phase)
beam-architect (Rust NIF review — never-blocking-scheduler invariant)
  ↓ (pre-commit check)
erlang-solutions-consultant (topology gut-check — bounded advisory)
  ↓
cto (synthesis)
  ↓
deep-reviewer (Plane 1 security posture — capability leakage, boundary enforcement)
```

### Starting Prompt
```
Phase 0 ramp: W1-W4 BEAM kernel skeleton. Scope: gen_statem session
topology, Horde registry, Ra shared state, libcluster on GKE
StatefulSet, Rust NIF for crypto hot paths.

Dispatch beam-architect first (topology design), then scale
elixir-engineer x2 for pair implementation in parallel with beam-sre
for K8s wiring. erlang-solutions-consultant does a topology gut-check
before we commit. CTO synthesizes, deep-reviewer does security posture.

Invariant: no gRPC inside the BEAM kernel (Plane 1 purity).
```

### Why Five BEAM Agents, Not One
- `beam-architect` — topology and OTP tree design (no Elixir line-level code)
- `elixir-engineer` — implements the Elixir code (scaled x2 for pair work)
- `go-hybrid-engineer` — owns the Plane 2 gRPC edge (only if crossing to Go)
- `beam-sre` — cluster operations, libcluster, K8s manifests, hot-code-load
- `erlang-solutions-consultant` — external advisory, never implements, BEAM gut-checks only

---

## Scenario 17: Independent Gate 2 Validation (External Retainer)

### Situation
You're entering a production-gate checkpoint for a BEAM-heavy service: full load + chaos + SLO posture validation before rollout. Per retainer plan, `erlang-solutions-consultant` performs independent validation to avoid in-team bias. (`beam-sre` built the chaos harness; `beam-sre` validating it has obvious self-review bias.)

### Agent Chain
```
beam-sre (prepares load + chaos test harness; runs internally)
  ↓
erlang-solutions-consultant (INDEPENDENT Gate 2 validation — reviews harness,
                              runs parallel validation, issues PASS / CONDITIONAL / FAIL verdict)
  ↓ (if CONDITIONAL or FAIL)
beam-architect + elixir-engineer (ee-1, ee-2) (remediation based on consultant findings)
  ↓ (re-validate)
erlang-solutions-consultant (second-pass validation)
  ↓ (if PASS)
cto (rollout authorization)
```

### Starting Prompt
```
Gate 2 for <service>. beam-sre has the internal load+chaos harness
ready. Dispatch erlang-solutions-consultant for INDEPENDENT Gate 2
validation per retainer scope.

The consultant is advisory only — does NOT implement. Issues
PASS / CONDITIONAL / FAIL. If CONDITIONAL or FAIL, route findings
to beam-architect + elixir-engineer (pair) for remediation, then
re-validate with the consultant.
```

### Why Independence Matters
External validation is the whole point of the retainer. Erlang Solutions has OTP core-maintenance credibility and 100+ BEAM production systems. In-team agents carry style bias; the external retainer catches what the team can't see about itself.

---

## Scenario 18: Systemic Capability Gap → Hiring Pipeline

### Situation
Across the last 6 sessions, the team has repeatedly misrouted AWS/CDK work to `infra-expert` (who is GCP-focused). The signal bus shows 4 `cross-agent-flags.md` entries like "infra-expert: this is actually AWS, I don't know CDK well" in the last 2 weeks. `session-sentinel`'s weekly audit flags a "recurring misroute pattern: AWS infrastructure work." The team clearly lacks an AWS specialist.

### Agent Chain
```
talent-scout (continuous scan → produces requisition with 5-signal confidence score)
  ↓ (confidence ≥ threshold AND session-sentinel co-signs)
recruiter (8-phase pipeline begins)
  Phase 1: requisition received from talent-scout
  Phase 2: research (benchmark-agent pulled in for peer platforms)
  Phase 3: synthesis (uses AGENT_TEMPLATE.md to draft prompt)
  Phase 4: validation (run run_contract_tests.py against draft — gate)
  Phase 5: challenger (adversarial review of draft)
  Phase 6: handoff → meta-agent writes .claude/agents/aws-specialist.md atomically
           + updates contract-test list + hook regexes + trust ledger defaults + memory scaffold
  Phase 7: post-hire-verify.sh runs (gate; JSON pass/fail)
  Phase 8: probation tracking begins (status: probationary in ledger)
           → promotion to active after refutation rate <25% across ≥5 verdicts
```

### Starting Prompt
```
Dispatch talent-scout for a team coverage audit. We've seen 4
misrouted AWS/CDK tickets in the last 2 weeks and session-sentinel
is flagging it as a recurring pattern. If confidence clears the
threshold, initiate the hiring pipeline via recruiter.
```

### talent-scout Returns (Example Requisition)
```
REQUISITION: aws-specialist (Tier 2 Guardian, color: bronze, model: opus)

5-SIGNAL CONFIDENCE: 0.84 (threshold: 0.70)
  Signal 1 — cross-agent-flag density: 4 flags / 2 weeks = HIGH
  Signal 2 — dispatch misroute rate: 6 AWS tickets routed to infra-expert,
             5 escalated to user
  Signal 3 — domain-failure pattern: infra-expert self-identifies as GCP-first
             in 3 recent outputs
  Signal 4 — external tech-stack mentions: user referenced "our AWS account"
             7 times in 2 weeks
  Signal 5 — session-sentinel recurring-gap flag: PRESENT (weekly audit
             2026-04-12, 2026-04-19)

CO-SIGN REQUIRED: session-sentinel
```

### Recruiter Output (Phase 6 — Handoff)
```
DRAFT PROMPT ATTACHED: /tmp/draft-aws-specialist.md (42 KB)
CONTRACT TESTS: passed 11/11 (simulated)
CHALLENGER VERDICT: survived with 1 caveat — add explicit "defer to
  infra-expert for GCP-bridge work" to CAPABILITY DOMAINS section. APPLIED.

HANDOFF → meta-agent
Action: atomically register aws-specialist via:
  1. Write .claude/agents/aws-specialist.md
  2. Append to CUSTOM_AGENTS regex in verify-agent-protocol.sh
     + verify-signal-bus-persisted.sh
  3. Append to CUSTOM_AGENTS set in run_contract_tests.py
  4. Append to DEFAULT_DOMAINS dict in ledger.py
  5. Create .claude/agent-memory/aws-specialist/MEMORY.md with seed entries
  6. Commit atomically (single commit, all 5 files + new agent file)
  7. Run post-hire-verify.sh aws-specialist
```

### Post-Hire Verification
```bash
bash .claude/hooks/post-hire-verify.sh aws-specialist
→ {"status":"verified","agent":"aws-specialist","next_gate":"probation_tracking"}

python3 .claude/agent-memory/trust-ledger/ledger.py standings | grep aws
→ aws-specialist  probationary  0.9  1.0  0C/0P/0R  0S/0L
```

### 3 Months Later (Probation Gate)
After 7 verifiable verdicts (6 CONFIRMED, 1 REFUTED), refutation rate = 14% < 25%:
```
python3 .claude/agent-memory/trust-ledger/ledger.py promote --agent aws-specialist
→ ✓ aws-specialist: promoted to active.
```

### Why This Matters
Without `talent-scout` + `recruiter`, hiring is ad-hoc and politically-driven. With them, hiring is data-driven (5-signal confidence + session-sentinel co-sign), process-driven (8 phases enforced), and quality-gated (contract tests + challenger + post-hire-verify). **The team grows when evidence supports growth, not when someone has a hunch.**

---

## Scenario 19: Shadow Mind Intuition for Fast-Path Decisions

### Situation
CTO is about to dispatch a full Pattern A (plan → build → review → test → QA) for a "refactor the SSE event buffering logic" request. Before committing to the full chain, CTO wants to know: has the team seen this kind of refactor before? What's the usual outcome? Which agent-pairs tend to get dispatched together on SSE work? This is exactly the sort of probabilistic pattern-lookup the Shadow Mind exists to answer. Crucially, **it's optional** — if the oracle is stale or has no data, CTO proceeds with the normal Pattern A.

### Agent Chain
```
cto (teammate, already in session)
  → [NEXUS:INTUIT] "Have we refactored SSE buffering before?
                    Which agents co-dispatched? What was the average finding count?"
    main thread (kernel) routes the query:
       • intuition-oracle reads shadow-mind/observations/*.jsonl
       • consults patterns/ngrams.json (dispatch sequences for SSE-tagged sessions)
       • consults patterns/co_occurrences.json (finding types)
       • pulls relevant dreams/*.yaml (collaboration-gap or debug-loop themes)
       • checks heartbeats/observer.json (is data fresh? last_run < 24h?)
       • also checks heartbeats/pattern-computer.json (are patterns fresh?)
    → returns INTUIT_RESPONSE v1
  → cto receives probabilistic guidance, adjusts Pattern A (e.g., skip a redundant step,
    or pre-dispatch evidence-validator because past SSE refactors had 3+ HIGH findings)
```

### Starting Prompt (Inside a Teammate Session)
```
SendMessage to "lead":
  [NEXUS:INTUIT] Have we refactored SSE/streaming logic before?
  Which agent pairs co-dispatched on those sessions, and what was
  the typical finding density?
```

### INTUIT_RESPONSE (Example — Fresh Data)
```json
[NEXUS:OK] INTUIT_RESPONSE v1
{
  "status": "OK",
  "query": "Have we refactored SSE/streaming logic...",
  "answer": "4 prior sessions tagged SSE/streaming. Dominant pair: go-expert + elite-engineer (4/4). Secondary pair: deep-reviewer + test-engineer (3/4). Average HIGH-severity finding count: 3.25. Recurring theme: session state/lifecycle bugs. Recommendation: pre-dispatch evidence-validator; expect 3+ HIGH findings.",
  "confidence": 0.72,
  "evidence_ids": [
    "obs:2026-03-30#128", "obs:2026-04-10#44",
    "obs:2026-04-14#61", "dream-2026-04-17-debug-loop-sse-abc123"
  ],
  "pattern_types_consulted": ["ngram", "co_occurrence"],
  "staleness_hours": 0.4
}
```

### CTO's Decision Path
```
cto (teammate) → TaskUpdate: Pattern A adjusted
  → pre-dispatch evidence-validator alongside deep-reviewer (save one round-trip)
  → add test-engineer earlier in the chain (pattern says they pair with deep-reviewer here)
  → proceed with Pattern A, now informed by Shadow Mind's probabilistic read
```

### Alternative — Stale Shadow Mind
If `heartbeats/observer.json.last_run` is older than 24h:
```json
[NEXUS:OK] INTUIT_RESPONSE v1
{
  "status": "SHADOW_MIND_STALE",
  "query": "...",
  "answer": "Observer heartbeat last updated 31.2h ago. Not serving stale patterns.",
  "confidence": 0.0,
  "evidence_ids": [],
  "pattern_types_consulted": [],
  "staleness_hours": 31.2
}
```

CTO sees `SHADOW_MIND_STALE`, proceeds with the normal Pattern A without the fast-path optimization — behavior is **identical to a world without the Shadow Mind**. No interruption, no failure cascade.

### Why This Matters
The Shadow Mind lets the conscious layer make better-calibrated decisions WITHOUT forcing it to consult anything. Pattern A works fine without `[NEXUS:INTUIT]`. But when the oracle has fresh data, it compresses "read through 6 prior sessions + meta-agent's notes + trust ledger" into a single query with a confidence score. The whole thing is delete-to-disable — remove `shadow-mind/` and the oracle's `status` flips to `NO_DATA` (or the syscall returns `[NEXUS:ERR] intuition-oracle unavailable`), and CTO proceeds as before. No conscious-layer agent is ever required to consult the Shadow Mind.

---

## Meta-Pattern: The "Chain Dispatch"

When an agent returns with `DISPATCH RECOMMENDATION: Agent X`, you dispatch X with A's recommendation as context. X might recommend Y. You dispatch Y. This creates emergent workflows from individual agent intelligence.

```
A returns → recommends B →
  main thread dispatches B with A's context →
    B returns → recommends C →
      main thread dispatches C with B's context →
        C returns → NONE → chain complete
```

Continue until `DISPATCH RECOMMENDATION: NONE`.

---

## Related Documentation

- **TEAM_OVERVIEW.md** — Architecture and capabilities reference
- **TEAM_RUNBOOK.md** — Day-to-day operational playbook
- **TEAM_CHEATSHEET.md** — Quick reference card
- **CLAUDE.md** (project root) — Main thread operational protocol

---

*Last updated: 2026-04-18 — v3.0 with 4 new scenarios (16–19): BEAM kernel build, Gate 2 validation, hiring pipeline, Shadow Mind intuition.*

#!/usr/bin/env python3
"""
Trust Ledger
============

Per-agent accuracy scorecard. Records verdicts from evidence-validator
and challenge outcomes from challenger, computing an accuracy score
that CTO can use to weight future findings.

Storage: one JSON file per agent at `.claude/agent-memory/trust-ledger/<agent>.json`.

Usage:
    # Record an evidence-validator verdict for a finding by another agent
    ./ledger.py verdict --agent go-expert --verdict CONFIRMED --finding-id F-42

    # Record a challenger outcome
    ./ledger.py challenge --agent cto --outcome SURVIVED --challenge-id C-13

    # Show current standings
    ./ledger.py standings

    # Show one agent's record in detail
    ./ledger.py show --agent go-expert

    # Compute trust weight for an agent (0.0-1.0, used for weighting)
    ./ledger.py weight --agent go-expert

Schema per agent file:
{
  "agent": "go-expert",
  "domain": "Go language + smart-agents",
  "model": "opus",
  "findings": {
    "total": 0,
    "confirmed": 0,
    "partially_confirmed": 0,
    "refuted": 0,
    "unverifiable": 0
  },
  "challenges": {
    "received": 0,
    "survived": 0,
    "lost": 0
  },
  "accuracy_score": 1.0,
  "trust_weight": 1.0,
  "history": [
    {"ts": "2026-04-14T...", "kind": "verdict", "id": "F-42", "outcome": "CONFIRMED"}
  ],
  "notes": ""
}
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

LEDGER_DIR = Path(__file__).resolve().parent
AGENTS_DIR = LEDGER_DIR.parents[1] / "agents"

# Default domain per agent (populated on first write).
DEFAULT_DOMAINS = {
    "cto": "Supreme technical authority, team leader",
    "orchestrator": "Workflow execution, gate enforcement",
    "deep-planner": "Task decomposition, dependency graphs, plans",
    "deep-qa": "Code quality, architecture, performance, tests",
    "deep-reviewer": "Security, debugging, deployment safety",
    "meta-agent": "Prompt evolution, team learning",
    "memory-coordinator": "Cross-agent memory, knowledge synthesis",
    "session-sentinel": "Protocol enforcement, session audits",
    "elite-engineer": "Full-stack Go/Python/TS implementation",
    "ai-platform-architect": "AI/ML systems, agent architecture",
    "frontend-platform-engineer": "Frontend-v3 React/Next.js",
    "go-expert": "Go language + smart-agents service",
    "python-expert": "Python/FastAPI + code-agent service",
    "typescript-expert": "TypeScript/React + frontend-v3",
    "infra-expert": "K8s/GKE/Terraform/SRE",
    "database-expert": "PostgreSQL/Redis/Firestore",
    "observability-expert": "Logging/tracing/metrics/alerting",
    "api-expert": "GraphQL Federation, API contracts",
    "test-engineer": "Test architecture + test code",
    "cluster-awareness": "Live GKE cluster state",
    "benchmark-agent": "Competitive intelligence",
    "beam-architect": "BEAM Plane 1 kernel architecture — OTP supervision, Horde/Ra/pg cluster topology, Rust NIFs, BLOCKING-1 enforcement",
    "elixir-engineer": "Elixir/Phoenix/LiveView implementation on BEAM — gen_statem agents, Ecto+Memgraph persistence, MOD-2 v1.2 compliance; pair-dispatched",
    "go-hybrid-engineer": "Plane 2 Go edge + Plane 1↔2 gRPC boundary — protobuf contracts, Dapr sidecar, SDK integrations; CONDITIONAL on D3-hybrid",
    "beam-sre": "BEAM cluster operations on GKE — libcluster, BEAM metrics, hot-code-load, chaos engineering, SLO/SLI for agent sessions",
    "erlang-solutions-consultant": "External Erlang/Elixir advisory retainer — architecture review, hot-code-load safety, Gate 2 validation; advisory only",
    "talent-scout": "Continuous team coverage-gap detection via 5-signal confidence scoring; drafts hiring requisitions; advisory + gated auto-initiate with session-sentinel co-sign",
    "recruiter": "8-phase hiring pipeline (requisition → research → synthesis → validation → challenger → handoff → probation → retirement); draft-and-handoff pattern — meta-agent retains single-writer authority over .claude/agents/*.md",
    "evidence-validator": "Claim verification",
    "challenger": "Adversarial review",
    "intuition-oracle": "Shadow Mind query surface — probabilistic pattern-lookup/counterfactual/team-perception responses via INTUIT_RESPONSE v1 envelope; read-only, non-interrupting, optional-to-consult",
}

# Agent lifecycle status — probationary during trial window, active once promotion
# criteria met (refutation rate < 25% across ≥5 dispatches), retired when sunset.
VALID_STATUSES = {"probationary", "active", "retired"}
NEW_HIRE_STATUS = "probationary"
LEGACY_STATUS = "active"  # Default for pre-existing agents migrated forward.

# Agents that pre-date the status field and should be migrated to "active"
# on first load. New agents added AFTER 2026-04-18 default to "probationary".
LEGACY_ACTIVE_AGENTS = {
    "cto", "orchestrator", "deep-planner", "deep-qa", "deep-reviewer",
    "meta-agent", "memory-coordinator", "session-sentinel",
    "elite-engineer", "ai-platform-architect", "frontend-platform-engineer",
    "go-expert", "python-expert", "typescript-expert",
    "infra-expert", "database-expert", "observability-expert",
    "api-expert", "test-engineer", "cluster-awareness", "benchmark-agent",
    "beam-architect", "elixir-engineer", "go-hybrid-engineer",
    "beam-sre", "erlang-solutions-consultant",
    "evidence-validator", "challenger",
}


def ledger_path(agent: str) -> Path:
    return LEDGER_DIR / f"{agent}.json"


def _default_status_for(agent: str) -> str:
    # Pre-existing agents migrate to "active"; unknown (new) agents enter
    # the hiring pipeline as "probationary" until explicitly promoted.
    return LEGACY_STATUS if agent in LEGACY_ACTIVE_AGENTS else NEW_HIRE_STATUS


def load(agent: str) -> dict:
    path = ledger_path(agent)
    if path.exists():
        record = json.loads(path.read_text())
        # Backward-compat migration: legacy JSONs written before the status
        # field existed. Stamp them as "active" on first read — subsequent
        # save() persists the migration.
        if "status" not in record:
            record["status"] = _default_status_for(agent)
        return record
    return {
        "agent": agent,
        "domain": DEFAULT_DOMAINS.get(agent, "unspecified"),
        "model": "unknown",
        "status": _default_status_for(agent),
        "findings": {
            "total": 0, "confirmed": 0, "partially_confirmed": 0,
            "refuted": 0, "unverifiable": 0,
        },
        "challenges": {"received": 0, "survived": 0, "lost": 0},
        "accuracy_score": 1.0,
        "trust_weight": 1.0,
        "history": [],
        "notes": "",
    }


def save(agent: str, record: dict) -> None:
    path = ledger_path(agent)
    path.write_text(json.dumps(record, indent=2) + "\n")


def compute_accuracy(findings: dict) -> float:
    confirmed = findings["confirmed"]
    partial = findings["partially_confirmed"]
    refuted = findings["refuted"]
    unverifiable = findings["unverifiable"]

    verifiable = confirmed + partial + refuted
    if verifiable == 0:
        return 1.0  # No data yet — start with full trust.

    return (confirmed + 0.5 * partial) / verifiable


def compute_trust_weight(record: dict) -> float:
    """
    Blend accuracy with sample size. An agent with 50 confirmations has
    more signal than one with 2. We apply a Bayesian-style prior of 5
    neutral-trust observations so new/low-sample agents don't swing wildly.
    """
    findings = record["findings"]
    accuracy = compute_accuracy(findings)
    verifiable = findings["confirmed"] + findings["partially_confirmed"] + findings["refuted"]

    prior_n = 5
    prior_mean = 0.9  # Slight optimism — most agents ARE accurate.

    return (accuracy * verifiable + prior_mean * prior_n) / (verifiable + prior_n)


def update_scores(record: dict) -> None:
    record["accuracy_score"] = round(compute_accuracy(record["findings"]), 3)
    record["trust_weight"] = round(compute_trust_weight(record), 3)


def cmd_verdict(args: argparse.Namespace) -> int:
    agent = args.agent
    verdict = args.verdict.upper()

    valid = {"CONFIRMED", "PARTIALLY_CONFIRMED", "REFUTED", "UNVERIFIABLE"}
    if verdict not in valid:
        print(f"ERROR: verdict must be one of {valid}", file=sys.stderr)
        return 2

    record = load(agent)
    record["findings"]["total"] += 1

    key = {
        "CONFIRMED": "confirmed",
        "PARTIALLY_CONFIRMED": "partially_confirmed",
        "REFUTED": "refuted",
        "UNVERIFIABLE": "unverifiable",
    }[verdict]
    record["findings"][key] += 1

    record["history"].append({
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kind": "verdict",
        "id": args.finding_id or "unspecified",
        "outcome": verdict,
    })
    # Cap history at 200 entries to prevent unbounded growth.
    record["history"] = record["history"][-200:]

    update_scores(record)
    save(agent, record)
    print(f"✓ {agent}: {verdict} recorded. accuracy={record['accuracy_score']} trust={record['trust_weight']}")
    return 0


def cmd_challenge(args: argparse.Namespace) -> int:
    agent = args.agent
    outcome = args.outcome.upper()

    valid = {"SURVIVED", "LOST"}
    if outcome not in valid:
        print(f"ERROR: outcome must be one of {valid}", file=sys.stderr)
        return 2

    record = load(agent)
    record["challenges"]["received"] += 1

    if outcome == "SURVIVED":
        record["challenges"]["survived"] += 1
    else:
        record["challenges"]["lost"] += 1

    record["history"].append({
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kind": "challenge",
        "id": args.challenge_id or "unspecified",
        "outcome": outcome,
    })
    record["history"] = record["history"][-200:]

    save(agent, record)
    print(f"✓ {agent}: challenge {outcome} recorded.")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    record = load(args.agent)
    print(json.dumps(record, indent=2))
    return 0


def cmd_weight(args: argparse.Namespace) -> int:
    record = load(args.agent)
    # If file didn't exist, compute from default.
    weight = compute_trust_weight(record)
    print(f"{weight:.3f}")
    return 0


def _promotion_eligibility(record: dict) -> tuple[bool, str]:
    """
    Probation → active requires refutation rate < 25% across ≥5 verifiable
    dispatches. Unverifiable verdicts don't count toward the sample.
    """
    findings = record["findings"]
    verifiable = findings["confirmed"] + findings["partially_confirmed"] + findings["refuted"]
    if verifiable < 5:
        return False, f"insufficient sample: {verifiable} verifiable verdict(s), need ≥5"
    refutation_rate = findings["refuted"] / verifiable
    if refutation_rate >= 0.25:
        return False, f"refutation rate {refutation_rate:.1%} ≥ 25% (need <25%)"
    return True, f"eligible: {verifiable} verdicts, refutation rate {refutation_rate:.1%}"


def cmd_promote(args: argparse.Namespace) -> int:
    agent = args.agent
    record = load(agent)
    current = record.get("status", _default_status_for(agent))

    if current == "active":
        print(f"ℹ {agent}: already active, no change.")
        return 0
    if current == "retired":
        print(f"ERROR: {agent} is retired — cannot promote. Re-hire via recruiter first.",
              file=sys.stderr)
        return 2

    if not args.force:
        eligible, reason = _promotion_eligibility(record)
        if not eligible:
            print(f"ERROR: {agent} not eligible for promotion — {reason}. "
                  f"Use --force to override.", file=sys.stderr)
            return 2

    record["status"] = "active"
    record["history"].append({
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kind": "status_change",
        "id": "promotion",
        "outcome": "probationary→active",
    })
    record["history"] = record["history"][-200:]
    save(agent, record)
    print(f"✓ {agent}: promoted to active.")
    return 0


def cmd_retire(args: argparse.Namespace) -> int:
    agent = args.agent
    record = load(agent)
    current = record.get("status", _default_status_for(agent))

    if current == "retired":
        print(f"ℹ {agent}: already retired, no change.")
        return 0

    record["status"] = "retired"
    record["history"].append({
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kind": "status_change",
        "id": "retirement",
        "outcome": f"{current}→retired",
    })
    record["history"] = record["history"][-200:]
    if args.reason:
        note_line = f"[{datetime.datetime.now(datetime.timezone.utc).date().isoformat()}] retired: {args.reason}"
        record["notes"] = (record.get("notes") or "") + ("\n" if record.get("notes") else "") + note_line
    save(agent, record)
    print(f"✓ {agent}: retired.")
    return 0


def cmd_standings(args: argparse.Namespace) -> int:
    # Load all ledger files.
    records = []
    if LEDGER_DIR.exists():
        for path in sorted(LEDGER_DIR.glob("*.json")):
            records.append(json.loads(path.read_text()))

    # Also include agents without ledger files at default weight.
    known = {r["agent"] for r in records}
    for agent in AGENTS_DIR.glob("*.md"):
        name = agent.stem
        if name not in known:
            records.append(load(name))

    # Recompute scores for every record (ensures display is consistent
    # even for agents with no ledger file yet).
    for r in records:
        update_scores(r)

    # Backfill the status field for any record missing it (legacy JSONs).
    for r in records:
        if "status" not in r:
            r["status"] = _default_status_for(r["agent"])

    # Sort by trust weight descending, retired agents last.
    def _sort_key(r: dict) -> tuple:
        retired_penalty = 1 if r.get("status") == "retired" else 0
        return (retired_penalty, -r["trust_weight"], r["agent"])
    records.sort(key=_sort_key)

    print(f"{'Agent':<30} {'Status':<14} {'Trust':<8} {'Accuracy':<10} {'Findings':<12} {'Challenges':<12}")
    print("-" * 86)
    for r in records:
        findings_str = f"{r['findings']['confirmed']}C/{r['findings']['partially_confirmed']}P/{r['findings']['refuted']}R"
        challenges_str = f"{r['challenges']['survived']}S/{r['challenges']['lost']}L"
        status = r.get("status", "active")
        print(f"{r['agent']:<30} {status:<14} {r['trust_weight']:<8} {r['accuracy_score']:<10} {findings_str:<12} {challenges_str:<12}")

    print()
    print("Legend: C=Confirmed, P=Partially confirmed, R=Refuted, S=Survived challenge, L=Lost challenge")
    print("Status: probationary (new hire, on trial) | active (validated) | retired (sunset)")
    print("Trust weight: Bayesian-blended accuracy (0-1). New agents start at 0.9.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("verdict", help="Record an evidence-validator verdict")
    p.add_argument("--agent", required=True)
    p.add_argument("--verdict", required=True,
                   choices=["CONFIRMED", "PARTIALLY_CONFIRMED", "REFUTED", "UNVERIFIABLE"])
    p.add_argument("--finding-id", help="Optional finding identifier for audit trail")
    p.set_defaults(func=cmd_verdict)

    p = sub.add_parser("challenge", help="Record a challenger outcome")
    p.add_argument("--agent", required=True)
    p.add_argument("--outcome", required=True, choices=["SURVIVED", "LOST"])
    p.add_argument("--challenge-id", help="Optional challenge identifier")
    p.set_defaults(func=cmd_challenge)

    p = sub.add_parser("show", help="Show full record for an agent")
    p.add_argument("--agent", required=True)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("weight", help="Compute current trust weight for an agent")
    p.add_argument("--agent", required=True)
    p.set_defaults(func=cmd_weight)

    p = sub.add_parser("standings", help="Show all agents ranked by trust")
    p.set_defaults(func=cmd_standings)

    p = sub.add_parser("promote", help="Promote a probationary agent to active (requires refutation rate <25% across ≥5 verdicts, or --force)")
    p.add_argument("--agent", required=True)
    p.add_argument("--force", action="store_true", help="Skip eligibility gate")
    p.set_defaults(func=cmd_promote)

    p = sub.add_parser("retire", help="Retire an agent (sunset — no further dispatch expected)")
    p.add_argument("--agent", required=True)
    p.add_argument("--reason", help="Optional reason, appended to agent notes")
    p.set_defaults(func=cmd_retire)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

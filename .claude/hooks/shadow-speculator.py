#!/usr/bin/env python3
"""
Shadow Speculator — Counterfactual generator for the Shadow Mind layer.

Invoke via: CronCreate with schedule "0 */4 * * *". Disable via: CronDelete.
Runs during idle; does NOT execute any actions. Write-only to
``shadow-mind/speculations/<YYYY-MM-DD-HH>.json``.

Reads the last N observations (default 10) from
``shadow-mind/observations/`` and generates 1-3 counterfactual variants per
observation. Each variant is a structured JSON record that meta-agent and
intuition-oracle can consult, but no action is ever taken. The whole
component is delete-to-disable — remove this file or stop scheduling it and
the 30-agent conscious layer continues unaffected.

Runtime budget: < 30s per invocation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
SHADOW_DIR = REPO_ROOT / ".claude" / "agent-memory" / "shadow-mind"
OBS_DIR = SHADOW_DIR / "observations"
SPEC_DIR = SHADOW_DIR / "speculations"
HB_FILE = SHADOW_DIR / "heartbeats" / "speculator.json"

VARIANT_TEMPLATES = [
    {
        "variant_type": "agent_not_dispatched",
        "template": "What if agent {agent} had NOT been dispatched during session {session}?",
        "outcome_template": (
            "Removing {agent} likely degrades {signal_type} coverage for this "
            "session's domain; peer agents would need to absorb the gap."
        ),
        "confidence": 0.55,
    },
    {
        "variant_type": "severity_escalation",
        "template": "What if the finding had been reported at HIGH severity instead of its original level?",
        "outcome_template": (
            "Higher severity would auto-dispatch evidence-validator before user "
            "surfacing, adding ~1 extra round-trip but increasing trust weight."
        ),
        "confidence": 0.6,
    },
    {
        "variant_type": "alternative_choice",
        "template": "What if a peer agent had been chosen instead of {agent} for this handoff?",
        "outcome_template": (
            "Different agent selection changes finding framing and may surface "
            "distinct blind spots — useful for adversarial diversity."
        ),
        "confidence": 0.5,
    },
    {
        "variant_type": "cto_route_alternate",
        "template": "What if the CTO had routed to option B instead of option A for this decision?",
        "outcome_template": (
            "Alternate routing typically trades latency for depth or vice versa; "
            "downstream evidence-validator verdicts would need re-computation."
        ),
        "confidence": 0.45,
    },
]


def iter_recent_observations(limit: int) -> list[dict]:
    """Return the last ``limit`` observation records, newest first."""
    if not OBS_DIR.exists():
        return []
    files = sorted(
        (p for p in OBS_DIR.glob("*.jsonl") if p.is_file()),
        key=lambda p: p.name,
        reverse=True,
    )
    records: list[dict] = []
    for fp in files:
        try:
            with fp.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError as exc:
            print(f"[speculator] skipping {fp}: {exc}", file=sys.stderr)
            continue
        if len(records) >= limit * 4:
            break
    records.sort(key=lambda r: r.get("ts", ""), reverse=True)
    return records[:limit]


def observation_id(obs: dict) -> str:
    """Derive a stable observation ID from its raw line + timestamp."""
    key = (obs.get("ts", "") + "|" + obs.get("raw_line", "")).encode("utf-8")
    return hashlib.sha1(key).hexdigest()[:12]


def build_variants(obs: dict, rng: random.Random) -> list[dict]:
    """Return 1-3 variant dicts for a single observation."""
    n = rng.randint(1, 3)
    picks = rng.sample(VARIANT_TEMPLATES, k=min(n, len(VARIANT_TEMPLATES)))
    obs_id = observation_id(obs)
    variants: list[dict] = []
    agent = obs.get("agent", "unknown")
    session = obs.get("session", "unknown")
    signal_type = obs.get("signal_type", "unknown")
    for idx, tmpl in enumerate(picks):
        variants.append(
            {
                "id": f"spec-{obs_id}-{idx}",
                "original_observation_id": obs_id,
                "variant_type": tmpl["variant_type"],
                "question": tmpl["template"].format(
                    agent=agent, session=session, signal_type=signal_type
                ),
                "hypothetical_outcome": tmpl["outcome_template"].format(
                    agent=agent, session=session, signal_type=signal_type
                ),
                "confidence_score": tmpl["confidence"],
                "source_signal_type": signal_type,
                "source_agent": agent,
                "source_session": session,
            }
        )
    return variants


def write_heartbeat(count: int) -> None:
    HB_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "last_run": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "speculations_generated": count,
        "component": "speculator",
    }
    HB_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_speculations(variants: Iterable[dict], dry_run: bool) -> Path | None:
    """Persist variants to a single per-hour JSON file. Returns path or None on dry-run."""
    variants_list = list(variants)
    if not variants_list:
        return None
    if dry_run:
        json.dump({"count": len(variants_list), "sample": variants_list[:2]}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return None
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H")
    out = SPEC_DIR / f"{stamp}.json"
    existing: list[dict] = []
    if out.exists():
        try:
            existing = json.loads(out.read_text(encoding="utf-8")).get("speculations", [])
        except json.JSONDecodeError:
            existing = []
    payload = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "speculations": existing + variants_list,
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate counterfactual variants for recent Shadow Mind "
            "observations. Does NOT execute any action; write-only."
        )
    )
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=10,
        help="Number of most-recent observations to process (default: 10).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for deterministic variant selection (default: entropy).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print a sample of variants to stdout; do not write to disk.",
    )
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    observations = iter_recent_observations(args.limit)
    if not observations:
        print("[speculator] no observations yet — nothing to speculate on")
        if not args.dry_run:
            write_heartbeat(0)
        return 0

    all_variants: list[dict] = []
    for obs in observations:
        all_variants.extend(build_variants(obs, rng))

    out_path = write_speculations(all_variants, dry_run=args.dry_run)
    if not args.dry_run:
        write_heartbeat(len(all_variants))
        where = str(out_path) if out_path else "(none)"
        print(f"[speculator] wrote {len(all_variants)} variants -> {where}")
    else:
        print(f"[speculator] dry-run: would have written {len(all_variants)} variants")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

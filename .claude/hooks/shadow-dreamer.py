#!/usr/bin/env python3
"""
Shadow Dreamer — Long-idle pattern analysis for the Shadow Mind layer.

Invoke via: CronCreate with schedule "3 3 * * *" (daily ~3 AM local).
Disable via: CronDelete. Runs ONLY during long-idle windows
(default: most-recent observation > 1 hour ago) to avoid contention with
active sessions. Write-only to ``shadow-mind/dreams/<YYYY-MM-DD>-<slug>.yaml``
— never applies an evolution; only proposes candidates for meta-agent review.

Delete-to-disable: removing this file does not affect the 30-agent
conscious layer. All dream outputs are advisory. meta-agent retains
single-writer authority over ``.claude/agents/*.md``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SHADOW_DIR = REPO_ROOT / ".claude" / "agent-memory" / "shadow-mind"
OBS_DIR = SHADOW_DIR / "observations"
DREAMS_DIR = SHADOW_DIR / "dreams"
HB_FILE = SHADOW_DIR / "heartbeats" / "dreamer.json"

SESSION_WINDOW = 5   # Approx number of recent sessions worth of observations to read.
OBS_PER_SESSION = 80 # Upper-bound heuristic; total cap is SESSION_WINDOW * this.
MIN_PAIR_EVIDENCE = 3
MIN_STUCK_LOOP_COUNT = 3
MIN_EVOLUTION_REPEAT = 3


def slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len] or "dream"


def load_recent_observations(cap: int) -> list[dict]:
    """Load the last ``cap`` observations across all jsonl files."""
    if not OBS_DIR.exists():
        return []
    files = sorted(OBS_DIR.glob("*.jsonl"), key=lambda p: p.name, reverse=True)
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
            print(f"[dreamer] skipping {fp}: {exc}", file=sys.stderr)
            continue
        if len(records) >= cap:
            break
    records.sort(key=lambda r: r.get("ts", ""), reverse=True)
    return records[:cap]


def most_recent_obs_age_hours(observations: list[dict]) -> float:
    if not observations:
        return float("inf")
    ts = observations[0].get("ts")
    if not ts:
        return float("inf")
    try:
        parsed = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return float("inf")
    delta = datetime.now(timezone.utc) - parsed
    return delta.total_seconds() / 3600.0


# --- Insight detectors ------------------------------------------------------

def detect_collaboration_gaps(observations: list[dict]) -> list[dict]:
    """Find agent pairs that rarely or never co-appear in the same session."""
    sessions: dict[str, set[str]] = defaultdict(set)
    for obs in observations:
        sess = obs.get("session")
        agent = obs.get("agent")
        if sess and agent:
            sessions[sess].add(agent)

    pair_counts: Counter[tuple[str, str]] = Counter()
    all_agents: set[str] = set()
    for agents in sessions.values():
        all_agents.update(agents)
        sorted_agents = sorted(agents)
        for i, a in enumerate(sorted_agents):
            for b in sorted_agents[i + 1 :]:
                pair_counts[(a, b)] += 1

    insights: list[dict] = []
    agents_list = sorted(all_agents)
    # Only flag pairs among agents that DO appear multiple times individually
    # but never co-occur — otherwise every rarely-seen agent pair explodes.
    solo_counts = Counter(obs.get("agent") for obs in observations if obs.get("agent"))
    for i, a in enumerate(agents_list):
        if solo_counts[a] < MIN_PAIR_EVIDENCE:
            continue
        for b in agents_list[i + 1 :]:
            if solo_counts[b] < MIN_PAIR_EVIDENCE:
                continue
            if pair_counts[(a, b)] == 0:
                insights.append(
                    {
                        "type": "collaboration-gap",
                        "proposal": (
                            f"Agents `{a}` and `{b}` are both active (≥{MIN_PAIR_EVIDENCE} "
                            "appearances) but never co-dispatched. Evaluate whether a "
                            "cross-domain collaboration pattern is missing."
                        ),
                        "evidence": [
                            {"agent": a, "solo_count": solo_counts[a]},
                            {"agent": b, "solo_count": solo_counts[b]},
                        ],
                        "confidence": 0.55,
                    }
                )
    return insights


def detect_stuck_debug_loops(observations: list[dict]) -> list[dict]:
    """Find sessions where the same agent emits repeated findings without resolution markers."""
    by_session: dict[str, list[dict]] = defaultdict(list)
    for obs in observations:
        sess = obs.get("session")
        if sess:
            by_session[sess].append(obs)

    insights: list[dict] = []
    resolution_markers = ("resolved", "fixed", "shipped", "merged", "deployed", "closed")
    for sess, entries in by_session.items():
        agent_signal_counts: Counter[tuple[str, str]] = Counter()
        has_resolution = False
        for e in entries:
            content = (e.get("content") or "").lower()
            if any(marker in content for marker in resolution_markers):
                has_resolution = True
            agent_signal_counts[(e.get("agent", ""), e.get("signal_type", ""))] += 1
        if has_resolution:
            continue
        for (agent, signal_type), count in agent_signal_counts.items():
            if count >= MIN_STUCK_LOOP_COUNT:
                insights.append(
                    {
                        "type": "debug-loop",
                        "proposal": (
                            f"Session `{sess}` shows {count} `{signal_type}` signals "
                            f"from `{agent}` with no resolution markers. Consider "
                            "dispatching a verifier or reviewer to break the loop."
                        ),
                        "evidence": [
                            {"session": sess, "agent": agent, "signal_type": signal_type, "count": count},
                        ],
                        "confidence": 0.65,
                    }
                )
    return insights


def detect_evolution_backlog(observations: list[dict]) -> list[dict]:
    """Detect evolution signals proposing the same agent change repeatedly."""
    evo_only = [o for o in observations if o.get("signal_type") == "evolution_signal"]
    bucket: Counter[str] = Counter()
    exemplars: dict[str, str] = {}
    for obs in evo_only:
        content = (obs.get("content") or "").strip()
        if not content:
            continue
        # Normalize: first 80 chars, lowercase — cheap bucketing for recurring proposals.
        key = re.sub(r"\s+", " ", content.lower())[:80]
        bucket[key] += 1
        exemplars.setdefault(key, content)

    insights: list[dict] = []
    for key, count in bucket.items():
        if count >= MIN_EVOLUTION_REPEAT:
            insights.append(
                {
                    "type": "evolution-backlog",
                    "proposal": (
                        f"Evolution proposal repeated {count}× without being baked "
                        f"into a prompt: \"{exemplars[key][:120]}\". meta-agent "
                        "should evaluate during next sweep."
                    ),
                    "evidence": [{"exemplar": exemplars[key], "repeat_count": count}],
                    "confidence": 0.7,
                }
            )
    return insights


def detect_trust_drift(observations: list[dict]) -> list[dict]:
    """Flag agents whose output volume is spiking in cross-agent-flags (proxy for trust drift)."""
    flag_obs = [o for o in observations if o.get("signal_type") == "cross_agent_flag"]
    target_counts: Counter[str] = Counter()
    for obs in flag_obs:
        content = (obs.get("content") or "").lower()
        # "<agent> should know: ..." or "flag <agent> ..." — heuristic extraction
        m = re.match(r"^\s*([a-z0-9-]+)\s+should\s+know", content) or re.match(
            r"^\s*flag\s+([a-z0-9-]+)", content
        )
        if m:
            target_counts[m.group(1)] += 1
    insights: list[dict] = []
    for agent, count in target_counts.items():
        if count >= MIN_EVOLUTION_REPEAT:
            insights.append(
                {
                    "type": "trust-drift",
                    "proposal": (
                        f"Agent `{agent}` has received {count} cross-agent flags "
                        "within the dream window. Review trust-ledger weight and "
                        "recent verdicts."
                    ),
                    "evidence": [{"agent": agent, "flag_count": count}],
                    "confidence": 0.5,
                }
            )
    return insights


# --- Persistence ------------------------------------------------------------

def write_dream(insight: dict) -> Path:
    DREAMS_DIR.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = slugify(insight.get("type", "dream") + "-" + insight.get("proposal", "")[:30])
    digest = hashlib.sha1(json.dumps(insight, sort_keys=True).encode("utf-8")).hexdigest()[:6]
    out = DREAMS_DIR / f"{date}-{slug}-{digest}.yaml"
    lines: list[str] = []
    lines.append(f"id: dream-{date}-{slug}-{digest}")
    lines.append(f"type: {insight['type']}")
    lines.append(f"confidence: {insight['confidence']}")
    lines.append("review_status: pending")
    lines.append("proposed_to: meta-agent")
    proposal_escaped = insight["proposal"].replace("\\", "\\\\").replace('"', '\\"')
    lines.append(f"proposal: \"{proposal_escaped}\"")
    lines.append("evidence:")
    for ev in insight.get("evidence", []):
        lines.append("  - " + json.dumps(ev, sort_keys=True))
    lines.append(f"generated_at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_heartbeat(count: int, activated: bool) -> None:
    HB_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "last_run": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dreams_generated": count,
        "activated": activated,
        "component": "dreamer",
    }
    HB_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate pattern-analysis insight candidates (dreams) for meta-agent "
            "review. Activates only during long-idle windows. Advisory only."
        )
    )
    parser.add_argument(
        "--min-idle-hours",
        type=float,
        default=1.0,
        help="Minimum hours since last observation before dreaming activates (default: 1.0).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass the idle-window check (useful for testing).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print insights to stdout; do not write YAML files.",
    )
    args = parser.parse_args(argv)

    cap = SESSION_WINDOW * OBS_PER_SESSION
    observations = load_recent_observations(cap)

    if not observations:
        print("[dreamer] no observations — nothing to dream about")
        write_heartbeat(0, activated=False)
        return 0

    age = most_recent_obs_age_hours(observations)
    if not args.force and age < args.min_idle_hours:
        print(
            f"[dreamer] last observation {age:.2f}h ago < {args.min_idle_hours}h — "
            "not yet in idle window; skipping"
        )
        write_heartbeat(0, activated=False)
        return 0

    insights: list[dict] = []
    insights.extend(detect_collaboration_gaps(observations))
    insights.extend(detect_stuck_debug_loops(observations))
    insights.extend(detect_evolution_backlog(observations))
    insights.extend(detect_trust_drift(observations))

    if args.dry_run:
        print(json.dumps(insights, indent=2))
        return 0

    written: list[Path] = []
    for insight in insights:
        written.append(write_dream(insight))

    write_heartbeat(len(written), activated=True)
    print(f"[dreamer] wrote {len(written)} dream candidates (idle {age:.2f}h)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

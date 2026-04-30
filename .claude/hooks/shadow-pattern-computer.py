#!/usr/bin/env python3
"""
Shadow Pattern Computer — derives Pattern Library from observations.

Reads `.claude/agent-memory/shadow-mind/observations/*.jsonl` (populated by
the Observer Daemon) and computes three pattern artifacts consumed by the
intuition-oracle agent:

  1. patterns/ngrams.json         — P(next_agent | current_agent) transition
                                    probabilities per session
  2. patterns/co_occurrences.json — agent↔agent and signal_type↔signal_type
                                    co-occurrence matrices within same session
  3. patterns/temporal.json       — hour-of-day and day-of-week signal density

INVOCATION:
  Run on-demand:      python3 shadow-pattern-computer.py
  Scheduled:          CronCreate with schedule='15 */4 * * *' (every 4 hours)
  Dry-run (no write): python3 shadow-pattern-computer.py --dry-run

DISABLE:
  Any of these turn the computer off without affecting the 30-agent team:
    * Delete this file
    * Delete .claude/agent-memory/shadow-mind/ (full layer removal)
    * CronDelete the scheduled invocation

GUARANTEES:
  - Read-only on observations/*.jsonl
  - Atomic write (via temp-file swap) to patterns/*.json
  - Malformed observations skipped with stderr warning (never blocks)
  - Idempotent — re-running with same observations yields same patterns
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(
    os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
)
SHADOW_ROOT = REPO_ROOT / ".claude/agent-memory/shadow-mind"
OBSERVATIONS_DIR = SHADOW_ROOT / "observations"
PATTERNS_DIR = SHADOW_ROOT / "patterns"
HEARTBEATS_DIR = SHADOW_ROOT / "heartbeats"

# Minimum evidence thresholds — pattern below these is too noisy to surface
MIN_NGRAM_COUNT = 2       # require at least 2 observed transitions
MIN_COOCC_COUNT = 2       # require at least 2 co-occurrences
MIN_TEMPORAL_COUNT = 3    # require at least 3 observations in same bucket


def log_err(msg: str) -> None:
    print(f"[pattern-computer] {msg}", file=sys.stderr)


def log_info(msg: str) -> None:
    print(f"[pattern-computer] {msg}")


# ---------------------------------------------------------------------------
# Observation loading
# ---------------------------------------------------------------------------
def load_observations() -> list[dict]:
    """Read all observations/*.jsonl files into a time-ordered list."""
    if not OBSERVATIONS_DIR.exists():
        log_err(f"observations dir missing: {OBSERVATIONS_DIR}")
        return []

    records: list[dict] = []
    skipped = 0
    for jsonl in sorted(OBSERVATIONS_DIR.glob("*.jsonl")):
        with jsonl.open() as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    # Required fields
                    if not all(
                        k in rec for k in ("ts", "agent", "session", "signal_type")
                    ):
                        skipped += 1
                        continue
                    records.append(rec)
                except json.JSONDecodeError:
                    log_err(f"malformed JSON at {jsonl.name}:{lineno}, skipping")
                    skipped += 1
    # Sort by timestamp so n-gram transitions are in temporal order
    records.sort(key=lambda r: r.get("ts", ""))
    if skipped:
        log_err(f"skipped {skipped} malformed/incomplete records")
    return records


# ---------------------------------------------------------------------------
# N-gram computation (agent transitions within same session)
# ---------------------------------------------------------------------------
def compute_ngrams(records: list[dict]) -> dict:
    """
    P(next_agent | current_agent) transition probabilities per session.

    Returns:
        {
          "version": 1,
          "computed_at": "<iso>",
          "sample_size": <N>,
          "sessions_observed": <M>,
          "transitions": {
             "from_agent": {
                "to_agent": {"count": N, "probability": 0.0-1.0}
             }
          }
        }
    """
    # Group observations by session, preserving temporal order
    by_session: dict[str, list[str]] = defaultdict(list)
    for rec in records:
        by_session[rec["session"]].append(rec["agent"])

    # Count transitions within each session
    transitions: Counter[tuple[str, str]] = Counter()
    for session, agents in by_session.items():
        for i in range(len(agents) - 1):
            from_a, to_a = agents[i], agents[i + 1]
            if from_a == to_a:
                continue  # skip self-transitions (same agent same session)
            transitions[(from_a, to_a)] += 1

    # Convert to nested dict with probabilities
    from_totals: Counter[str] = Counter()
    for (from_a, _), count in transitions.items():
        from_totals[from_a] += count

    nested: dict = defaultdict(dict)
    for (from_a, to_a), count in transitions.items():
        if count < MIN_NGRAM_COUNT:
            continue
        prob = round(count / from_totals[from_a], 4)
        nested[from_a][to_a] = {"count": count, "probability": prob}

    return {
        "version": 1,
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sample_size": len(records),
        "sessions_observed": len(by_session),
        "min_count_threshold": MIN_NGRAM_COUNT,
        "transitions": dict(nested),
    }


# ---------------------------------------------------------------------------
# Co-occurrence computation
# ---------------------------------------------------------------------------
def compute_co_occurrences(records: list[dict]) -> dict:
    """
    Agent↔agent and signal_type↔signal_type co-occurrence within same session.

    Two items co-occur if they both appear in observations of the same session.
    """
    by_session: dict[str, dict] = defaultdict(lambda: {"agents": set(), "signal_types": set()})
    for rec in records:
        by_session[rec["session"]]["agents"].add(rec["agent"])
        by_session[rec["session"]]["signal_types"].add(rec["signal_type"])

    # Pair counting (unordered pairs)
    agent_pairs: Counter[tuple[str, str]] = Counter()
    signal_pairs: Counter[tuple[str, str]] = Counter()
    for session, data in by_session.items():
        agents = sorted(data["agents"])
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                agent_pairs[(agents[i], agents[j])] += 1
        signals = sorted(data["signal_types"])
        for i in range(len(signals)):
            for j in range(i + 1, len(signals)):
                signal_pairs[(signals[i], signals[j])] += 1

    def to_nested(pairs: Counter) -> dict:
        nested: dict = defaultdict(dict)
        for (a, b), count in pairs.items():
            if count < MIN_COOCC_COUNT:
                continue
            nested[a][b] = count
            nested[b][a] = count  # symmetric
        return dict(nested)

    return {
        "version": 1,
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sessions_observed": len(by_session),
        "min_count_threshold": MIN_COOCC_COUNT,
        "agent_pairs": to_nested(agent_pairs),
        "signal_type_pairs": to_nested(signal_pairs),
    }


# ---------------------------------------------------------------------------
# Temporal pattern computation
# ---------------------------------------------------------------------------
def compute_temporal(records: list[dict]) -> dict:
    """Hour-of-day and day-of-week signal density."""
    by_hour: Counter[int] = Counter()
    by_dow: Counter[int] = Counter()  # 0=Monday
    by_agent_hour: dict[str, Counter[int]] = defaultdict(Counter)

    for rec in records:
        ts = rec.get("ts", "")
        try:
            # Observer emits ISO 8601 with Z suffix
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            by_hour[dt.hour] += 1
            by_dow[dt.weekday()] += 1
            by_agent_hour[rec["agent"]][dt.hour] += 1
        except (ValueError, TypeError):
            continue

    # Filter low-count buckets
    filtered_by_hour = {str(h): c for h, c in by_hour.items() if c >= MIN_TEMPORAL_COUNT}
    filtered_by_dow = {str(d): c for d, c in by_dow.items() if c >= MIN_TEMPORAL_COUNT}
    filtered_agent_hour = {
        agent: {str(h): c for h, c in hours.items() if c >= MIN_TEMPORAL_COUNT}
        for agent, hours in by_agent_hour.items()
    }
    filtered_agent_hour = {a: h for a, h in filtered_agent_hour.items() if h}

    return {
        "version": 1,
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sample_size": sum(by_hour.values()),
        "min_count_threshold": MIN_TEMPORAL_COUNT,
        "by_hour_utc": filtered_by_hour,
        "by_day_of_week": filtered_by_dow,  # 0=Mon..6=Sun
        "by_agent_hour": filtered_agent_hour,
    }


# ---------------------------------------------------------------------------
# Atomic writes
# ---------------------------------------------------------------------------
def write_atomic(path: Path, data: dict) -> None:
    """Write JSON atomically via temp-file + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
    ) as tmp:
        json.dump(data, tmp, indent=2, sort_keys=True)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def update_heartbeat(stats: dict) -> None:
    HEARTBEATS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "last_run": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stats": stats,
    }
    write_atomic(HEARTBEATS_DIR / "pattern-computer.json", payload)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Derive Pattern Library (n-grams + co-occurrences + temporal) from "
            "Shadow Mind observations. Read-only on observations; atomic write "
            "to patterns/*.json. Runs in <10s for typical observation volumes."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute + print summary to stdout; do not write files.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print top n-gram transitions + co-occurrence pairs.",
    )
    args = parser.parse_args()

    start = time.time()
    records = load_observations()
    if not records:
        log_err("no observations found — nothing to compute")
        return 1

    ngrams = compute_ngrams(records)
    cooccs = compute_co_occurrences(records)
    temporal = compute_temporal(records)

    stats = {
        "records_processed": len(records),
        "transitions_found": sum(
            len(v) for v in ngrams["transitions"].values()
        ),
        "agent_pairs_found": sum(
            len(v) for v in cooccs["agent_pairs"].values()
        )
        // 2,  # symmetric — divide by 2
        "signal_pairs_found": sum(
            len(v) for v in cooccs["signal_type_pairs"].values()
        )
        // 2,
        "temporal_hours_covered": len(temporal["by_hour_utc"]),
        "duration_sec": round(time.time() - start, 3),
    }

    if args.verbose or args.dry_run:
        log_info("=" * 60)
        log_info(f"records processed: {stats['records_processed']}")
        log_info(f"transitions found (threshold {MIN_NGRAM_COUNT}+): {stats['transitions_found']}")
        log_info(f"agent pairs found (threshold {MIN_COOCC_COUNT}+): {stats['agent_pairs_found']}")
        log_info(f"signal-type pairs found: {stats['signal_pairs_found']}")
        log_info(f"temporal hour-buckets: {stats['temporal_hours_covered']}")

        if args.verbose:
            log_info("")
            log_info("Top 5 transitions (by count):")
            flat_trans: list[tuple[str, str, int, float]] = []
            for from_a, tos in ngrams["transitions"].items():
                for to_a, data in tos.items():
                    flat_trans.append((from_a, to_a, data["count"], data["probability"]))
            flat_trans.sort(key=lambda t: t[2], reverse=True)
            for from_a, to_a, count, prob in flat_trans[:5]:
                log_info(f"  {from_a} → {to_a}: count={count} P={prob}")

            log_info("")
            log_info("Top 5 agent co-occurrence pairs (by count):")
            flat_pairs: list[tuple[str, str, int]] = []
            seen: set[tuple[str, str]] = set()
            for a, partners in cooccs["agent_pairs"].items():
                for b, count in partners.items():
                    key = tuple(sorted([a, b]))
                    if key in seen:
                        continue
                    seen.add(key)
                    flat_pairs.append((a, b, count))
            flat_pairs.sort(key=lambda t: t[2], reverse=True)
            for a, b, count in flat_pairs[:5]:
                log_info(f"  {a} ↔ {b}: {count} session(s)")

    if args.dry_run:
        log_info("")
        log_info("DRY-RUN — no files written")
        return 0

    # Atomic writes
    write_atomic(PATTERNS_DIR / "ngrams.json", ngrams)
    write_atomic(PATTERNS_DIR / "co_occurrences.json", cooccs)
    write_atomic(PATTERNS_DIR / "temporal.json", temporal)
    update_heartbeat(stats)

    log_info(
        f"wrote 3 pattern files ({stats['transitions_found']} transitions, "
        f"{stats['agent_pairs_found']} agent pairs, "
        f"{stats['temporal_hours_covered']} hour buckets) in {stats['duration_sec']}s"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

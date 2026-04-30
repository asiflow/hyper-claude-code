#!/usr/bin/env bash
#
# Shadow Observer Daemon — Non-invasive signal-bus watcher.
#
# Tails the 3 signal-bus files, parses each new canonical entry, writes a
# JSON record to shadow-mind/observations/<date>.jsonl, and updates a
# heartbeat file so the intuition-oracle can detect staleness.
#
# INVOCATION:
#   Run via the Monitor tool with this script as the command, persistent=true.
#   Example (pseudocode): Monitor({ command: ".claude/hooks/shadow-observer.sh",
#                                    persistent: true })
#
# DISABLE:
#   Any one of these turns the observer off without affecting the 30-agent team:
#     * Kill the Monitor process (TaskStop or kill <pid>)
#     * Delete this file
#     * Delete .claude/agent-memory/shadow-mind/ (full layer removal)
#   The conscious layer (30 agents + signal bus) is unaffected.
#
# GUARANTEES:
#   - Read-only against signal-bus files (tail -F, no writes)
#   - Non-blocking: malformed lines are logged to stderr and skipped
#   - Backfills last 200 entries on cold start (empty observations/)
#   - Idempotent writes (JSON-lines append, one record per signal line)
#
set -uo pipefail

REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
SIGNAL_BUS_DIR="$REPO_ROOT/.claude/agent-memory/signal-bus"
SHADOW_DIR="$REPO_ROOT/.claude/agent-memory/shadow-mind"
OBS_DIR="$SHADOW_DIR/observations"
HB_FILE="$SHADOW_DIR/heartbeats/observer.json"

SIGNAL_FILES=(
  "memory-handoffs.md:memory_handoff"
  "evolution-signals.md:evolution_signal"
  "cross-agent-flags.md:cross_agent_flag"
)

# --- Utilities ---------------------------------------------------------------

log_err() { echo "[shadow-observer] $*" >&2; }

# Escape a string for JSON embedding (handles backslash, quote, control chars).
json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().rstrip()))'
}

# Parse canonical signal-bus entry:
#   - (YYYY-MM-DD, agent=<name>, session=<id>) <content>
# Emits: ts_date<TAB>agent<TAB>session<TAB>content
# Returns non-zero on malformed line.
parse_canonical() {
  local line="$1"
  python3 - "$line" <<'PY'
import re, sys
line = sys.argv[1]
m = re.match(r'^- \((\d{4}-\d{2}-\d{2}),\s*agent=([^,]+),\s*session=([^)]+)\)\s*(.*)$', line)
if not m:
    sys.exit(1)
date, agent, session, content = m.groups()
print(f"{date}\t{agent.strip()}\t{session.strip()}\t{content.strip()}")
PY
}

# Append one observation record to the per-day .jsonl file.
# Arguments: signal_type raw_line
write_observation() {
  local signal_type="$1"
  local raw_line="$2"
  local parsed
  parsed=$(parse_canonical "$raw_line" 2>/dev/null) || {
    log_err "malformed line skipped (${signal_type}): ${raw_line:0:120}"
    return 0
  }
  local date agent session content
  IFS=$'\t' read -r date agent session content <<<"$parsed"
  local out_file="$OBS_DIR/${date}.jsonl"
  local ts_now
  ts_now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  local agent_json session_json content_json raw_json
  agent_json=$(printf '%s' "$agent" | json_escape)
  session_json=$(printf '%s' "$session" | json_escape)
  content_json=$(printf '%s' "$content" | json_escape)
  raw_json=$(printf '%s' "$raw_line" | json_escape)
  {
    printf '{"ts":"%s","signal_date":"%s","agent":%s,"session":%s,"signal_type":"%s","content":%s,"raw_line":%s}\n' \
      "$ts_now" "$date" "$agent_json" "$session_json" "$signal_type" "$content_json" "$raw_json"
  } >>"$out_file"
}

# Update heartbeat with last-run and observations count.
update_heartbeat() {
  local count
  count=$(find "$OBS_DIR" -name "*.jsonl" -exec cat {} + 2>/dev/null | wc -l | tr -d ' ')
  local ts_now
  ts_now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  printf '{"last_run":"%s","observations_count":%s,"pid":%d}\n' \
    "$ts_now" "${count:-0}" "$$" >"$HB_FILE"
}

# Count existing observation records (across all jsonl files).
current_obs_count() {
  find "$OBS_DIR" -name "*.jsonl" 2>/dev/null | xargs -I{} cat {} 2>/dev/null | wc -l | tr -d ' '
}

# Backfill last N canonical entries from a signal-bus file.
backfill_file() {
  local file_base="$1"
  local signal_type="$2"
  local limit="$3"
  local path="$SIGNAL_BUS_DIR/$file_base"
  [ -f "$path" ] || return 0
  grep -E '^- \([0-9]{4}-[0-9]{2}-[0-9]{2}, agent=' "$path" 2>/dev/null \
    | tail -n "$limit" \
    | while IFS= read -r line; do
        write_observation "$signal_type" "$line"
      done
}

# --- Main -------------------------------------------------------------------

# Sanity check: signal bus exists.
if [ ! -d "$SIGNAL_BUS_DIR" ]; then
  log_err "signal-bus directory missing: $SIGNAL_BUS_DIR"
  exit 1
fi

mkdir -p "$OBS_DIR" "$SHADOW_DIR/heartbeats"

# Backfill on cold start (empty observations).
existing=$(current_obs_count)
if [ "${existing:-0}" -eq 0 ]; then
  log_err "cold start — backfilling last 200 entries per signal file"
  for entry in "${SIGNAL_FILES[@]}"; do
    IFS=':' read -r f t <<<"$entry"
    backfill_file "$f" "$t" 200
  done
  update_heartbeat
fi

# Build the tail -F command list.
TAIL_ARGS=()
for entry in "${SIGNAL_FILES[@]}"; do
  IFS=':' read -r f _ <<<"$entry"
  TAIL_ARGS+=("$SIGNAL_BUS_DIR/$f")
done

log_err "observer starting — tailing ${#TAIL_ARGS[@]} files (pid=$$)"

# Periodic heartbeat refresh in the background (every 60s).
(
  while true; do
    sleep 60
    update_heartbeat
  done
) &
HB_BG_PID=$!
trap 'kill $HB_BG_PID 2>/dev/null || true' EXIT INT TERM

# tail -F with --line-buffered grep tagged by filename.
# When multiple files are tailed, `tail -F` prefixes with "==> file <==" headers;
# we track the current source file and route each line accordingly.
current_file=""
tail -n 0 -F "${TAIL_ARGS[@]}" 2>/dev/null | while IFS= read -r line; do
  if [[ "$line" =~ ^==\>\ (.+)\ \<==$ ]]; then
    current_file="${BASH_REMATCH[1]}"
    continue
  fi
  # Only care about canonical signal-bus entries.
  if [[ ! "$line" =~ ^-\ \([0-9]{4}-[0-9]{2}-[0-9]{2},\ agent= ]]; then
    continue
  fi
  # Resolve signal_type from the current file.
  base=$(basename "$current_file")
  signal_type=""
  for entry in "${SIGNAL_FILES[@]}"; do
    IFS=':' read -r f t <<<"$entry"
    if [ "$f" = "$base" ]; then
      signal_type="$t"
      break
    fi
  done
  [ -z "$signal_type" ] && continue
  write_observation "$signal_type" "$line"
  update_heartbeat
done

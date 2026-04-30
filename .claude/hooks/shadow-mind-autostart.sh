#!/usr/bin/env bash
#
# SessionStart hook — Shadow Mind Autostart
#
# Eliminates the 6-tool-call manual activation ceremony by:
#   1. Detecting if Observer daemon is running (via PID file heartbeat)
#   2. If not, launching shadow-observer.sh as a background process
#   3. Refreshing Pattern Library (one-shot pattern-computer run)
#   4. Reporting status to STDERR (visible to main thread context)
#
# No-ops safely if:
#   - Shadow Mind directory doesn't exist (feature not installed)
#   - Observer is already running (detected via PID file)
#   - Required scripts are missing
#
# Exit 0 always — SessionStart failures must not prevent Claude Code
# from starting. This is a convenience layer, not a gate.
#
set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
SHADOW_DIR="$PROJECT_DIR/.claude/agent-memory/shadow-mind"
HOOKS_DIR="$PROJECT_DIR/.claude/hooks"
OBSERVER="$HOOKS_DIR/shadow-observer.sh"
PATTERN_COMPUTER="$HOOKS_DIR/shadow-pattern-computer.py"
HEARTBEAT_FILE="$SHADOW_DIR/heartbeats/observer.json"

# No-op guard: Shadow Mind not installed
[ ! -d "$SHADOW_DIR" ] && exit 0
[ ! -x "$OBSERVER" ] && exit 0

# Check if observer is already running
OBSERVER_RUNNING=0
RUNNING_PID=""
if [ -f "$HEARTBEAT_FILE" ]; then
  CANDIDATE_PID=$(jq -r '.pid // empty' "$HEARTBEAT_FILE" 2>/dev/null)
  if [ -n "$CANDIDATE_PID" ] && kill -0 "$CANDIDATE_PID" 2>/dev/null; then
    OBSERVER_RUNNING=1
    RUNNING_PID="$CANDIDATE_PID"
  fi
fi

if [ "$OBSERVER_RUNNING" = "1" ]; then
  echo "Shadow Mind: observer already running (PID=$RUNNING_PID)" >&2
else
  # Launch observer as detached background process
  # Redirect to a log file so nohup output doesn't pollute anything
  OBSERVER_LOG="/tmp/shadow-observer-$(date -u +%s).log"
  nohup "$OBSERVER" >"$OBSERVER_LOG" 2>&1 &
  NEW_PID=$!
  # Give observer a brief moment to write its initial heartbeat
  sleep 0.5
  if kill -0 "$NEW_PID" 2>/dev/null; then
    echo "Shadow Mind: observer launched (PID=$NEW_PID, log=$OBSERVER_LOG)" >&2
  else
    echo "Shadow Mind: observer failed to launch (check $OBSERVER_LOG)" >&2
    exit 0
  fi
fi

# Refresh Pattern Library (idempotent — one-shot)
if [ -x "$PATTERN_COMPUTER" ] || [ -f "$PATTERN_COMPUTER" ]; then
  if python3 "$PATTERN_COMPUTER" >/dev/null 2>&1; then
    # Report current pattern counts
    NGRAMS_FILE="$SHADOW_DIR/patterns/ngrams.json"
    if [ -f "$NGRAMS_FILE" ]; then
      NGRAM_COUNT=$(jq 'length // 0' "$NGRAMS_FILE" 2>/dev/null || echo "?")
      echo "Shadow Mind: pattern library refreshed ($NGRAM_COUNT ngram entries)" >&2
    else
      echo "Shadow Mind: pattern library refreshed" >&2
    fi
  fi
fi

# Report heartbeat freshness for intuition oracle staleness check
if [ -f "$HEARTBEAT_FILE" ]; then
  LAST_HEARTBEAT=$(jq -r '.last_seen // empty' "$HEARTBEAT_FILE" 2>/dev/null)
  [ -n "$LAST_HEARTBEAT" ] && echo "Shadow Mind: ACTIVE (last heartbeat=$LAST_HEARTBEAT)" >&2
fi

exit 0

#!/usr/bin/env bash
#
# SubagentStop hook — Trust Ledger Auto-Recorder
#
# When evidence-validator returns, parses its output for CLAIM SOURCE
# and VERDICT, then calls ledger.py to record the verdict against the
# source agent. When challenger returns, looks for a CHALLENGE OUTCOME
# section (target + outcome) and records that.
#
# Without this hook the trust ledger stays empty regardless of how
# many verdicts/challenges are produced — the source-of-truth gap that
# session-sentinel flagged in the 2026-04-14 mid-deployment audit.
#
# Non-blocking (exit 0 always) — diagnostic, not enforcing. If parsing
# fails, appends a row to ledger-parse-failures.log for later review.
#
set -uo pipefail

INPUT=$(cat)

STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // "false"')
if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

LAST_MSG=$(echo "$INPUT" | jq -r '.last_assistant_message // empty')
AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // "unknown"')

if [ -z "$LAST_MSG" ]; then
  exit 0
fi

LEDGER="${CLAUDE_PROJECT_DIR:-.}/.claude/agent-memory/trust-ledger/ledger.py"
FAILURE_LOG="${CLAUDE_PROJECT_DIR:-.}/.claude/agent-memory/trust-ledger/parse-failures.log"

if [ ! -x "$LEDGER" ]; then
  exit 0  # No ledger — nothing to record.
fi

# Helper: extract first match group from message.
extract() {
  local pattern="$1"
  echo "$LAST_MSG" | grep -m1 -oE "$pattern" | head -1
}

case "$AGENT_TYPE" in
  evidence-validator)
    # Expect output containing both CLAIM SOURCE and VERDICT.
    SOURCE=$(echo "$LAST_MSG" | grep -m1 -oE 'CLAIM SOURCE:[[:space:]]*[a-z0-9-]+' | sed -E 's/CLAIM SOURCE:[[:space:]]*//')
    VERDICT=$(echo "$LAST_MSG" | grep -m1 -oE 'VERDICT:[[:space:]]*(CONFIRMED|PARTIALLY_CONFIRMED|REFUTED|UNVERIFIABLE)' | sed -E 's/VERDICT:[[:space:]]*//')

    if [ -n "$SOURCE" ] && [ -n "$VERDICT" ]; then
      python3 "$LEDGER" verdict --agent "$SOURCE" --verdict "$VERDICT" >/dev/null 2>&1 || {
        echo "$(date -u +%FT%TZ) verdict-write-failed agent=$SOURCE verdict=$VERDICT" >> "$FAILURE_LOG"
      }
    else
      echo "$(date -u +%FT%TZ) parse-failed source='$SOURCE' verdict='$VERDICT'" >> "$FAILURE_LOG"
    fi
    ;;

  challenger)
    # Expect output containing CHALLENGE TARGET and CHALLENGE OUTCOME.
    TARGET=$(echo "$LAST_MSG" | grep -m1 -oE 'CHALLENGE TARGET:[[:space:]]*[a-z0-9-]+' | sed -E 's/CHALLENGE TARGET:[[:space:]]*//')
    OUTCOME=$(echo "$LAST_MSG" | grep -m1 -oE 'CHALLENGE OUTCOME:[[:space:]]*(SURVIVED|LOST)' | sed -E 's/CHALLENGE OUTCOME:[[:space:]]*//')

    if [ -n "$TARGET" ] && [ -n "$OUTCOME" ]; then
      python3 "$LEDGER" challenge --agent "$TARGET" --outcome "$OUTCOME" >/dev/null 2>&1 || {
        echo "$(date -u +%FT%TZ) challenge-write-failed agent=$TARGET outcome=$OUTCOME" >> "$FAILURE_LOG"
      }
    fi
    ;;
esac

exit 0

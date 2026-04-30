#!/usr/bin/env bash
#
# SubagentStop wrapper for post-hire-verify.sh
#
# Adapts the SubagentStop stdin JSON to the positional-arg interface
# that post-hire-verify.sh expects. Only fires for meta-agent/recruiter.
# Non-blocking (exit 0 always).
#
set -uo pipefail

INPUT=$(cat)

STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // "false"')
if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // "unknown"')

case "$AGENT_TYPE" in
  meta-agent|recruiter) ;;
  *) exit 0 ;;
esac

MSG=$(echo "$INPUT" | jq -r '.last_assistant_message // ""')

AGENT_NAME=""
AGENT_NAME=$(echo "$MSG" | grep -oE '"agent":"[a-z][a-z0-9-]+"' | head -1 | cut -d'"' -f4)
[ -z "$AGENT_NAME" ] && AGENT_NAME=$(echo "$MSG" | grep -oE 'registered[[:space:]]+[a-z][a-z0-9-]+' | head -1 | awk '{print $2}')
[ -z "$AGENT_NAME" ] && AGENT_NAME=$(echo "$MSG" | grep -oE 'hired[[:space:]]+[a-z][a-z0-9-]+' | head -1 | awk '{print $2}')
[ -z "$AGENT_NAME" ] && AGENT_NAME=$(echo "$MSG" | grep -oE 'new agent[[:space:]]+[a-z][a-z0-9-]+' | head -1 | awk '{print $3}')

if [ -z "$AGENT_NAME" ]; then
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/post-hire-verify.sh" "$AGENT_NAME" >/dev/null 2>&1 || true

exit 0

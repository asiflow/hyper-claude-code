#!/usr/bin/env bash
#
# PostToolUse:SendMessage hook — Parallel Inbox Depth Watchdog
#
# Prevents the documented "kernel fault" pattern where the main thread
# misses parallel SendMessage-to-"lead" calls because Claude Code UI
# surfaces only ONE idle notification at a time while sibling messages
# land silently in the team inbox JSON.
#
# Evidence of the pattern (session-v2.md Apr-18):
#   - Line 963: "I missed the original ba-5-optin SPAWN — CTO sent it in
#     parallel with the db-expert SPAWN"
#   - Line 985: "campaign delay (21:49 missed spawn → 22:03 resend)" — 14min
#   - Line 1170: "Second kernel fault — CTO sent challenger-mod2-v1.2 27s
#     BEFORE infra-expert. I processed infra-expert and missed challenger."
#
# Mechanism:
#   After any teammate→lead SendMessage, scan the team inbox for messages
#   received in the last 120s. If >1 messages, emit a STDERR warning that
#   becomes visible to the main thread's context.
#
# Non-blocking (exit 0 always). Diagnostic, not enforcing.
#
set -uo pipefail

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
[ "$TOOL_NAME" != "SendMessage" ] && exit 0

TO=$(echo "$INPUT" | jq -r '.tool_input.to // empty' 2>/dev/null)
# Only fire on teammate-to-lead messages (the miss pattern)
[ "$TO" != "lead" ] && exit 0

# Find the active team's lead inbox. Claude Code stores at
# ~/.claude/teams/<team>/inboxes/lead.json
INBOX=""
for candidate in "$HOME/.claude/teams"/*/inboxes/lead.json; do
  [ -f "$candidate" ] || continue
  # Pick the most recently modified one (current active team)
  if [ -z "$INBOX" ] || [ "$candidate" -nt "$INBOX" ]; then
    INBOX="$candidate"
  fi
done

[ -z "$INBOX" ] && exit 0
[ ! -f "$INBOX" ] && exit 0

# Compute 120s cutoff in ISO-8601 UTC format (macOS BSD date -v, Linux date -d)
if date -u -v-120S +"%Y-%m-%dT%H:%M:%S" >/dev/null 2>&1; then
  CUTOFF=$(date -u -v-120S +"%Y-%m-%dT%H:%M:%S")
else
  CUTOFF=$(date -u -d '120 seconds ago' +"%Y-%m-%dT%H:%M:%S" 2>/dev/null)
fi
[ -z "$CUTOFF" ] && exit 0

# Count messages within the window and list distinct senders
RECENT_COUNT=$(jq --arg cutoff "$CUTOFF" '
  [.[] | select(.timestamp // "" | tostring > $cutoff)] | length
' "$INBOX" 2>/dev/null)

# jq might return null/empty if the inbox schema is different; be defensive
[ -z "$RECENT_COUNT" ] && exit 0
[ "$RECENT_COUNT" = "null" ] && exit 0

if [ "$RECENT_COUNT" -gt 1 ] 2>/dev/null; then
  SENDERS=$(jq --arg cutoff "$CUTOFF" -r '
    [.[] | select(.timestamp // "" | tostring > $cutoff) | .from // "unknown"] | unique | join(", ")
  ' "$INBOX" 2>/dev/null)
  echo "INBOX WATCHDOG: $RECENT_COUNT messages in lead inbox within 120s from: $SENDERS. Scan full inbox before acting — parallel syscalls may be pending." >&2
fi

exit 0

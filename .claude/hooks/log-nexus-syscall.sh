#!/usr/bin/env bash
#
# PostToolUse hook on SendMessage — NEXUS Syscall Auto-Logger
#
# When a teammate sends a [NEXUS:*] syscall via SendMessage, this hook
# automatically appends an entry to signal-bus/nexus-log.md.
#
# Removes the burden of manual logging from the main thread kernel.
# The log becomes the authoritative audit trail regardless of whether
# the kernel remembered to log it.
#
set -uo pipefail

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
if [ "$TOOL_NAME" != "SendMessage" ]; then
  exit 0
fi

MESSAGE=$(echo "$INPUT" | jq -r '.tool_input.message // empty')
TO=$(echo "$INPUT" | jq -r '.tool_input.to // "unknown"')
SENDER=$(echo "$INPUT" | jq -r '.agent_type // "main-thread"')

# Only log NEXUS syscalls.
if ! echo "$MESSAGE" | grep -qE '^\[NEXUS:'; then
  exit 0
fi

# Extract the syscall name (first bracketed token after NEXUS:).
# Collapse newlines FIRST so multi-line bodies (e.g. [NEXUS:OK]\n\n<list>) don't
# leak into the syscall field — discovered by live E2E test 2026-04-15.
SYSCALL=$(echo "$MESSAGE" | tr '\n' ' ' | sed -E 's/^\[NEXUS:([A-Z?!_]+)\].*/\1/' | head -c 20)

# Build the log entry.
LOG_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/agent-memory/signal-bus/nexus-log.md"
if [ ! -f "$LOG_FILE" ]; then
  exit 0  # Log file doesn't exist — skip silently.
fi

TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M")
# Strip newlines from message for single-line log entry, cap at 180 chars.
PREVIEW=$(echo "$MESSAGE" | tr '\n' ' ' | head -c 180)

ENTRY="- ($TIMESTAMP, agent=$SENDER, syscall=$SYSCALL, to=$TO) $PREVIEW"

# Append atomically (append is O_APPEND on POSIX, safe under concurrency).
echo "$ENTRY" >> "$LOG_FILE"

exit 0

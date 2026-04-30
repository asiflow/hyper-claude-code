#!/usr/bin/env bash
#
# SubagentStop hook — Signal Bus Persistence Verifier
#
# When an agent emits non-NONE signals in its closing protocol, this hook
# verifies the signal bus files were actually updated. If an agent said
# "MEMORY HANDOFF: <finding>" but memory-handoffs.md wasn't touched,
# someone (probably the main thread kernel) violated the persistence
# protocol. Emits a warning to Claude's context so the main thread is
# prompted to catch up.
#
# Non-blocking (exit 0). This is about drift detection, not enforcement.
# The PROTOCOL hook enforces emission; this hook ensures emissions land
# on disk.
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

CUSTOM_AGENTS="^(cto|orchestrator|deep-planner|deep-qa|deep-reviewer|meta-agent|memory-coordinator|session-sentinel|elite-engineer|ai-platform-architect|frontend-platform-engineer|go-expert|python-expert|typescript-expert|infra-expert|database-expert|observability-expert|api-expert|test-engineer|cluster-awareness|benchmark-agent|beam-architect|elixir-engineer|go-hybrid-engineer|beam-sre|erlang-solutions-consultant|talent-scout|recruiter|evidence-validator|challenger|intuition-oracle)$"
if ! echo "$AGENT_TYPE" | grep -qE "$CUSTOM_AGENTS"; then
  exit 0
fi

BUS_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/agent-memory/signal-bus"

# For each signal section, check: was the body non-NONE AND was the
# target file modified in the last 120 seconds?
check_signal() {
  local section="$1"
  local target_file="$2"

  # Extract the body of the section (lines between this section header
  # and the next section header or end of message).
  local body
  body=$(echo "$LAST_MSG" | awk -v s="$section" '
    $0 == s { flag=1; next }
    flag && /^### / { exit }
    flag { print }
  ' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

  # Strip leading/trailing blank lines.
  body=$(echo "$body" | awk 'NF { print; p=1 } !NF && p { print }' | sed '/^$/d')

  # If body is empty or NONE (case-insensitive), no persistence expected.
  if [ -z "$body" ] || echo "$body" | head -1 | grep -qiE '^NONE\.?$'; then
    return 0
  fi

  # Non-NONE signal emitted. Check target file mtime.
  if [ ! -f "$target_file" ]; then
    echo "WARN: $section emitted but $target_file does not exist" >&2
    return 1
  fi

  local mtime now age
  mtime=$(stat -f %m "$target_file" 2>/dev/null || stat -c %Y "$target_file" 2>/dev/null || echo 0)
  now=$(date +%s)
  age=$((now - mtime))

  if [ "$age" -gt 120 ]; then
    echo "WARN: agent '$AGENT_TYPE' emitted $section but $(basename "$target_file") not updated in ${age}s" >&2
    return 1
  fi

  return 0
}

WARNINGS=0
check_signal "### MEMORY HANDOFF" "$BUS_DIR/memory-handoffs.md" || WARNINGS=$((WARNINGS + 1))
check_signal "### EVOLUTION SIGNAL" "$BUS_DIR/evolution-signals.md" || WARNINGS=$((WARNINGS + 1))
check_signal "### CROSS-AGENT FLAG" "$BUS_DIR/cross-agent-flags.md" || WARNINGS=$((WARNINGS + 1))

# Exit 0 regardless — this hook is diagnostic, not enforcing.
# Warnings on stderr go to debug log and show as "<hook name> hook error" inline.
exit 0

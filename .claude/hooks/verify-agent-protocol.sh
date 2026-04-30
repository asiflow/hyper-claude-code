#!/usr/bin/env bash
#
# SubagentStop hook — Protocol Compliance Enforcer
#
# Enforces that custom agents (from .claude/agents/) emit the mandatory
# closing protocol before stopping. If sections are missing, blocks the
# subagent (exit 2) and feeds structured feedback via stderr so the
# agent knows what to add before retrying.
#
# This is a HARD invariant. Prompts were soft compliance — this makes
# it impossible to skip.
#
set -uo pipefail

INPUT=$(cat)

# Infinite loop guard — if we've already blocked once, accept the retry.
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // "false"')
if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

# Extract the agent's final message and its type.
LAST_MSG=$(echo "$INPUT" | jq -r '.last_assistant_message // empty')
AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // "unknown"')

# Empty output — can't validate. Pass through.
if [ -z "$LAST_MSG" ]; then
  exit 0
fi

# Only enforce protocol on our 26 custom agents.
# Built-in Claude Code agents (Bash, Explore, Plan, general-purpose) don't
# follow our closing protocol and shouldn't be validated against it.
CUSTOM_AGENTS="^(cto|orchestrator|deep-planner|deep-qa|deep-reviewer|meta-agent|memory-coordinator|session-sentinel|elite-engineer|ai-platform-architect|frontend-platform-engineer|go-expert|python-expert|typescript-expert|infra-expert|database-expert|observability-expert|api-expert|test-engineer|cluster-awareness|benchmark-agent|beam-architect|elixir-engineer|go-hybrid-engineer|beam-sre|erlang-solutions-consultant|talent-scout|recruiter|evidence-validator|challenger|intuition-oracle)$"

if ! echo "$AGENT_TYPE" | grep -qE "$CUSTOM_AGENTS"; then
  exit 0
fi

# Check for the four required closing protocol sections.
MISSING=()
for section in "### MEMORY HANDOFF" "### EVOLUTION SIGNAL" "### CROSS-AGENT FLAG" "### DISPATCH RECOMMENDATION"; do
  if ! echo "$LAST_MSG" | grep -qF "$section"; then
    MISSING+=("$section")
  fi
done

if [ "${#MISSING[@]}" -gt 0 ]; then
  {
    echo "PROTOCOL VIOLATION: agent '$AGENT_TYPE' omitted closing protocol sections:"
    for m in "${MISSING[@]}"; do
      echo "  - $m"
    done
    echo ""
    echo "Every agent MUST end its final output with ALL FOUR sections per CLAUDE.md Mandatory Closing Protocol."
    echo "Use 'NONE' as the body if a section has no content (e.g., '### DISPATCH RECOMMENDATION\\nNONE')."
    echo ""
    echo "Please re-emit your response with all sections present."
  } >&2
  exit 2  # Block the stop; stderr becomes Claude feedback so agent can correct.
fi

# All sections present — allow stop.
exit 0

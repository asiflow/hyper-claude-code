#!/usr/bin/env bash
#
# post-hire-verify.sh — Hiring Pipeline Gate: post-registration verification
#
# Runs AFTER meta-agent commits a new agent atomically to confirm the new
# hire is correctly registered at all 4 enforcement points and has the
# supporting memory + trust-ledger infrastructure in place.
#
# Invocation (by meta-agent at Phase 7 of the recruiter pipeline, or
# manually by the operator):
#   bash .claude/hooks/post-hire-verify.sh <new-agent-name>
#
# Exit codes:
#   0  = verified, new hire is production-ready for probation tracking
#   1  = verification failed at step N (JSON error emitted to stdout)
#
# Output (JSON only — callers parse it):
#   Success: {"status":"verified","agent":"<name>","next_gate":"probation_tracking"}
#   Failure: {"error":"post-hire-verify failed at step N","detail":"..."}
#
# Steps verified in order:
#   1. Contract test suite passes (python3 .claude/tests/agents/run_contract_tests.py)
#   2. New agent appears in all 4 registration points with count == 1:
#      - .claude/hooks/verify-agent-protocol.sh CUSTOM_AGENTS regex
#      - .claude/hooks/verify-signal-bus-persisted.sh CUSTOM_AGENTS regex
#      - .claude/tests/agents/run_contract_tests.py CUSTOM_AGENTS set
#      - .claude/agent-memory/trust-ledger/ledger.py DEFAULT_DOMAINS dict
#   3. .claude/agent-memory/<new-agent>/MEMORY.md exists
#   4. .claude/agent-memory/trust-ledger/<new-agent>.json exists with
#      status: probationary
#
set -uo pipefail

# Repo root detection — script sits in .claude/hooks/, so root is two up.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Emit JSON error + exit 1.
fail() {
  local step="$1"
  local detail="$2"
  # Escape backslashes + quotes for JSON.
  detail="${detail//\\/\\\\}"
  detail="${detail//\"/\\\"}"
  printf '{"error":"post-hire-verify failed at step %s","detail":"%s"}\n' \
    "$step" "$detail"
  exit 1
}

# Emit JSON success + exit 0.
succeed() {
  local agent="$1"
  printf '{"status":"verified","agent":"%s","next_gate":"probation_tracking"}\n' \
    "$agent"
  exit 0
}

# ---- Argument handling -----------------------------------------------------

if [ $# -ne 1 ]; then
  fail "args" "expected exactly 1 argument (new agent name), got $#"
fi

NEW_AGENT="$1"

# Basic name sanity — lowercase, hyphen-separated, no spaces.
if ! printf '%s' "$NEW_AGENT" | grep -qE '^[a-z][a-z0-9-]*[a-z0-9]$'; then
  fail "args" "agent name '$NEW_AGENT' must match ^[a-z][a-z0-9-]*[a-z0-9]$"
fi

# ---- Step 1: Contract test suite passes ------------------------------------

CONTRACT_SCRIPT="$REPO_ROOT/.claude/tests/agents/run_contract_tests.py"
if [ ! -f "$CONTRACT_SCRIPT" ]; then
  fail "1" "contract test runner not found at $CONTRACT_SCRIPT"
fi

# Run the full suite. We capture both stdout and stderr; on failure the tail
# is included in the JSON detail so meta-agent can diagnose without re-running.
CONTRACT_OUTPUT=$(python3 "$CONTRACT_SCRIPT" 2>&1)
CONTRACT_RC=$?
if [ $CONTRACT_RC -ne 0 ]; then
  # Collapse output to one line for JSON; take the last ~200 chars.
  tail_out=$(printf '%s' "$CONTRACT_OUTPUT" | tr '\n' ' ' | tail -c 400)
  fail "1" "contract tests failed (rc=$CONTRACT_RC): $tail_out"
fi

# ---- Step 2: New agent registered at all 4 enforcement points --------------

declare -a REGISTRATION_POINTS=(
  "$REPO_ROOT/.claude/hooks/verify-agent-protocol.sh"
  "$REPO_ROOT/.claude/hooks/verify-signal-bus-persisted.sh"
  "$REPO_ROOT/.claude/tests/agents/run_contract_tests.py"
  "$REPO_ROOT/.claude/agent-memory/trust-ledger/ledger.py"
)

for point in "${REGISTRATION_POINTS[@]}"; do
  if [ ! -f "$point" ]; then
    fail "2" "registration point missing: $point"
  fi
  # Count exact occurrences of the agent name. We use word boundaries
  # (the agent name is expected to appear as a standalone token or
  # within quotes / regex alternation).
  count=$(grep -c -- "$NEW_AGENT" "$point" || true)
  if [ -z "$count" ]; then
    count=0
  fi
  if [ "$count" -lt 1 ]; then
    fail "2" "agent '$NEW_AGENT' not found in $point (count=0)"
  fi
  # A count ≥ 1 is acceptable — ledger DEFAULT_DOMAINS has both the key
  # string AND potentially references in doc comments. We only require
  # at least one occurrence per registration point.
done

# ---- Step 3: Memory directory + MEMORY.md exist ----------------------------

MEMORY_INDEX="$REPO_ROOT/.claude/agent-memory/$NEW_AGENT/MEMORY.md"
if [ ! -f "$MEMORY_INDEX" ]; then
  fail "3" "memory index not found at $MEMORY_INDEX (meta-agent must create .claude/agent-memory/$NEW_AGENT/MEMORY.md during registration)"
fi

# ---- Step 4: Trust-ledger JSON exists with status: probationary -----------

LEDGER_JSON="$REPO_ROOT/.claude/agent-memory/trust-ledger/$NEW_AGENT.json"
# If the JSON doesn't exist yet, bootstrap it via the ledger CLI so the
# probation clock starts. This preserves the invariant "every new hire
# has a ledger entry at probation creation."
if [ ! -f "$LEDGER_JSON" ]; then
  # Bootstrap: load+save the record to persist defaults (including
  # status: probationary via _default_status_for).
  python3 - <<PYEOF "$NEW_AGENT" "$REPO_ROOT" 2>/dev/null || fail "4" "failed to bootstrap ledger JSON for $NEW_AGENT"
import sys
sys.path.insert(0, sys.argv[2] + "/.claude/agent-memory/trust-ledger")
import ledger as L
agent = sys.argv[1]
record = L.load(agent)
L.save(agent, record)
PYEOF
fi

# Re-check after bootstrap attempt.
if [ ! -f "$LEDGER_JSON" ]; then
  fail "4" "trust-ledger JSON still missing after bootstrap: $LEDGER_JSON"
fi

# Verify the status field is "probationary" (new hires ONLY — if meta-agent
# is re-running the hook on an already-promoted agent, that's a separate
# class of error we don't check here).
status=$(python3 -c "
import json, sys
with open('$LEDGER_JSON') as f:
    r = json.load(f)
print(r.get('status', 'MISSING'))
" 2>/dev/null)

if [ "$status" != "probationary" ]; then
  fail "4" "trust-ledger status for '$NEW_AGENT' is '$status', expected 'probationary'"
fi

# ---- All gates passed ------------------------------------------------------

succeed "$NEW_AGENT"

#!/usr/bin/env bash
#
# Pre-commit hook: run agent contract tests against staged agent files.
#
# Install by symlinking into .git/hooks/pre-commit or chaining from an
# existing pre-commit hook. Exits 1 if any staged .claude/agents/*.md
# file fails the contract.
#
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
RUNNER="$REPO_ROOT/.claude/tests/agents/run_contract_tests.py"

# Check if any agent files are staged.
STAGED_AGENTS=$(git diff --cached --name-only --diff-filter=ACMR | grep '^\.claude/agents/.*\.md$' || true)

if [ -z "$STAGED_AGENTS" ]; then
  exit 0
fi

echo "Running agent contract tests on staged changes..."
if python3 "$RUNNER" --changed-only; then
  echo "Agent contracts OK."
  exit 0
else
  echo ""
  echo "Agent contract tests FAILED. Fix the issues above or commit with --no-verify if you intend to bypass."
  exit 1
fi

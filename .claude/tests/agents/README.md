# Agent Contract Tests

Validates every agent file in `.claude/agents/` against a shared contract. Catches regressions BEFORE they reach production.

## What Gets Tested

| Test | What It Validates |
|------|-------------------|
| `frontmatter.required_fields` | name, description, model present |
| `frontmatter.name_matches_filename` | `name:` field matches `.md` filename |
| `frontmatter.model_valid` | model is `opus`, `sonnet`, or `haiku` |
| `frontmatter.model_not_haiku` | model is NOT haiku (known harness incompatibility) |
| `frontmatter.description_single_line` | description is a single-line YAML scalar (prevents 2026-04-14 session-sentinel registration bug) |
| `frontmatter.description_non_trivial` | description ≥ 100 chars |
| `body.non_trivial` | body ≥ 500 chars |
| `body.closing_protocol_sections` | All 4 closing protocol headers present |
| `body.nexus_protocol_present` | NEXUS documentation present (section or ≥3 mentions) |
| `body.team_coordination_discipline` | SendMessage discipline documented |
| `body.no_deprecated_agent_tool_reference` | No legacy "use the Agent tool" phrases |

## Usage

```bash
# Run all tests
python3 .claude/tests/agents/run_contract_tests.py

# Test one agent
python3 .claude/tests/agents/run_contract_tests.py --agent go-expert

# Test only agents changed in git working tree
python3 .claude/tests/agents/run_contract_tests.py --changed-only

# Produce JUnit XML for CI
python3 .claude/tests/agents/run_contract_tests.py --junit /tmp/agents.xml

# JSON output for scripting
python3 .claude/tests/agents/run_contract_tests.py --json
```

## Pre-Commit Integration

Install the pre-commit hook that only runs tests on staged agent files:

```bash
ln -s ../../.claude/hooks/pre-commit-agent-contracts.sh .git/hooks/pre-commit
chmod +x .claude/hooks/pre-commit-agent-contracts.sh
```

If you already have a pre-commit hook, chain this one in:

```bash
# Add to existing .git/hooks/pre-commit
.claude/hooks/pre-commit-agent-contracts.sh || exit 1
```

## CI Integration

Add to GitHub Actions / GitLab CI:

```yaml
- name: Run agent contract tests
  run: python3 .claude/tests/agents/run_contract_tests.py --junit agent-tests.xml
```

## Adding New Contracts

To add a new test, add a function in `run_contract_tests.py` that takes an `AgentFile` and returns a `TestResult`, then append it to the `CONTRACT_TESTS` list at the bottom of that file.

Example:

```python
def test_my_new_contract(agent: AgentFile) -> TestResult:
    if "some_required_pattern" not in agent.body:
        return TestResult(
            agent=agent.basename,
            test="body.my_new_contract",
            passed=False,
            message="Missing required pattern",
        )
    return TestResult(agent.basename, "body.my_new_contract", True)

# Then add to CONTRACT_TESTS list.
```

## Expected Pass Rate

All 31 custom agents should pass all 11 contracts. Current state: 341/341 passing.

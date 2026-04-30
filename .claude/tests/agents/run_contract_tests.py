#!/usr/bin/env python3
"""
Agent Contract Test Runner
==========================

Validates every agent file in .claude/agents/ against a shared contract:
- Frontmatter is parseable YAML and contains required fields
- Model value is in the valid set
- Filename matches the `name` field in frontmatter
- Body contains the mandatory sections (closing protocol, NEXUS, team discipline)
- No references to deprecated patterns (e.g., "Agent tool" as a capability)
- Optional per-agent contracts can be added in per-agent/<agent>.yaml

Usage:
    python3 run_contract_tests.py                     # run all tests
    python3 run_contract_tests.py --agent go-expert   # test one agent
    python3 run_contract_tests.py --changed-only      # test only agents changed in git working tree
    python3 run_contract_tests.py --junit out.xml     # produce JUnit XML for CI

Exit codes:
    0 = all tests passed
    1 = one or more tests failed
    2 = harness error (missing files, unparseable YAML in fixture, etc.)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Layout detection: works in both distribution and installed contexts.
#   Distribution layout (this repo at rest):  <hyper-root>/tests/agents/run_contract_tests.py
#       -> AGENTS_DIR = <hyper-root>/agents/
#   Installed layout (after `cp -R ... YOUR_PROJECT/.claude/`):
#       <project>/.claude/tests/agents/run_contract_tests.py
#       -> AGENTS_DIR = <project>/.claude/agents/
_test_file = Path(__file__).resolve()
_dist_candidate = _test_file.parents[2] / "agents"           # distribution layout
_installed_candidate = _test_file.parents[3] / ".claude" / "agents"  # installed layout

# Prefer distribution layout (more specific) — otherwise the test would walk
# up into an enclosing project's `.claude/agents/` when the repo is checked
# out as a subdirectory of another project.
if _dist_candidate.is_dir():
    REPO_ROOT = _test_file.parents[2]
    AGENTS_DIR = _dist_candidate
elif _installed_candidate.is_dir():
    REPO_ROOT = _test_file.parents[3]
    AGENTS_DIR = _installed_candidate
else:
    print(
        f"ERROR: could not find agents/ directory.\n"
        f"  Checked distribution layout: {_dist_candidate}\n"
        f"  Checked installed layout:    {_installed_candidate}",
        file=sys.stderr,
    )
    sys.exit(2)
TESTS_DIR = _test_file.parent

VALID_MODELS = {"opus", "sonnet", "haiku"}
CUSTOM_AGENTS = {
    "cto", "orchestrator", "deep-planner", "deep-qa", "deep-reviewer",
    "meta-agent", "memory-coordinator", "session-sentinel",
    "elite-engineer", "ai-platform-architect", "frontend-platform-engineer",
    "go-expert", "python-expert", "typescript-expert",
    "infra-expert", "database-expert", "observability-expert",
    "api-expert", "test-engineer", "cluster-awareness", "benchmark-agent",
    "beam-architect", "elixir-engineer", "go-hybrid-engineer",
    "beam-sre", "erlang-solutions-consultant",
    "talent-scout", "recruiter",
    "evidence-validator", "challenger",
    "intuition-oracle",
}


@dataclass
class TestResult:
    agent: str
    test: str
    passed: bool
    message: str = ""

    def as_dict(self) -> dict:
        return {
            "agent": self.agent,
            "test": self.test,
            "passed": self.passed,
            "message": self.message,
        }


@dataclass
class AgentFile:
    path: Path
    raw: str
    frontmatter_raw: str
    frontmatter: dict
    body: str

    @property
    def basename(self) -> str:
        return self.path.stem


def parse_frontmatter_yaml(text: str) -> dict:
    """
    Minimal YAML parser for agent frontmatter. We deliberately avoid a
    yaml dependency — frontmatter in agent files is simple key:value
    format, optionally with multiline strings. This handles that subset.
    """
    result: dict = {}
    current_key: Optional[str] = None
    current_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.rstrip()
        if not stripped:
            if current_key and current_lines:
                current_lines.append("")
            continue

        # Top-level key: match "key:" or "key: value"
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$', line)
        if match and not line.startswith(" "):
            # Commit previous key
            if current_key is not None:
                value = "\n".join(current_lines).strip()
                result[current_key] = _coerce(value)
                current_lines = []

            key = match.group(1)
            rest = match.group(2).strip()
            current_key = key

            # Quoted string on same line
            if rest.startswith('"') and rest.endswith('"') and len(rest) > 1:
                current_lines = [rest[1:-1]]
            elif rest:
                current_lines = [rest]
            else:
                current_lines = []
        else:
            if current_key is not None:
                current_lines.append(line)

    if current_key is not None:
        value = "\n".join(current_lines).strip()
        result[current_key] = _coerce(value)

    return result


def _coerce(value: str) -> str:
    # Strip surrounding quotes and unescape common sequences.
    if value.startswith('"') and value.endswith('"') and len(value) > 1:
        value = value[1:-1]
    return value


def load_agent(path: Path) -> AgentFile:
    raw = path.read_text()
    if not raw.startswith("---"):
        raise ValueError(f"{path.name}: missing frontmatter delimiter")

    # Split the document at the SECOND --- marker on its own line.
    parts = re.split(r'^---\s*$', raw, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        raise ValueError(f"{path.name}: frontmatter not closed with ---")

    frontmatter_raw = parts[1]
    body = parts[2].lstrip("\n")
    frontmatter = parse_frontmatter_yaml(frontmatter_raw)

    return AgentFile(
        path=path,
        raw=raw,
        frontmatter_raw=frontmatter_raw,
        frontmatter=frontmatter,
        body=body,
    )


# ----------------------------------------------------------------------
# Contract tests
# ----------------------------------------------------------------------

def test_frontmatter_required_fields(agent: AgentFile) -> TestResult:
    required = {"name", "description", "model"}
    missing = required - set(agent.frontmatter)
    if missing:
        return TestResult(
            agent=agent.basename,
            test="frontmatter.required_fields",
            passed=False,
            message=f"Missing fields: {sorted(missing)}",
        )
    return TestResult(agent.basename, "frontmatter.required_fields", True)


def test_frontmatter_name_matches_filename(agent: AgentFile) -> TestResult:
    name = agent.frontmatter.get("name", "")
    if name != agent.basename:
        return TestResult(
            agent=agent.basename,
            test="frontmatter.name_matches_filename",
            passed=False,
            message=f"name='{name}' but filename is '{agent.basename}'",
        )
    return TestResult(agent.basename, "frontmatter.name_matches_filename", True)


def test_model_valid(agent: AgentFile) -> TestResult:
    model = agent.frontmatter.get("model", "")
    if model not in VALID_MODELS:
        return TestResult(
            agent=agent.basename,
            test="frontmatter.model_valid",
            passed=False,
            message=f"model='{model}' not in {sorted(VALID_MODELS)}",
        )
    return TestResult(agent.basename, "frontmatter.model_valid", True)


def test_model_not_haiku(agent: AgentFile) -> TestResult:
    """
    Known harness issue: haiku agents fail to register in experimental
    agent-teams mode. Prevent recurrence of the session-sentinel incident.
    """
    model = agent.frontmatter.get("model", "")
    if model == "haiku":
        return TestResult(
            agent=agent.basename,
            test="frontmatter.model_not_haiku",
            passed=False,
            message="haiku is rejected by the agent-teams harness (see 2026-04-14 session-sentinel incident)",
        )
    return TestResult(agent.basename, "frontmatter.model_not_haiku", True)


def test_closing_protocol_sections(agent: AgentFile) -> TestResult:
    required_sections = [
        "### MEMORY HANDOFF",
        "### EVOLUTION SIGNAL",
        "### CROSS-AGENT FLAG",
        "### DISPATCH RECOMMENDATION",
    ]
    missing = [s for s in required_sections if s not in agent.body]
    if missing:
        return TestResult(
            agent=agent.basename,
            test="body.closing_protocol_sections",
            passed=False,
            message=f"Missing closing protocol sections: {missing}",
        )
    return TestResult(agent.basename, "body.closing_protocol_sections", True)


def test_nexus_protocol_present(agent: AgentFile) -> TestResult:
    """
    Every non-sentinel agent must document NEXUS access.
    - session-sentinel is exempt (read-only auditor, minimal tooling).
    - CTO and orchestrator have expanded 'HOW YOU DISPATCH...' sections
      that reference NEXUS throughout; they don't need the literal
      'NEXUS PROTOCOL' subheader.
    - All other agents use the shared 'NEXUS PROTOCOL' subsection.
    """
    if agent.basename == "session-sentinel":
        return TestResult(agent.basename, "body.nexus_protocol_present", True, message="(exempt)")

    # Accept either the shared subsection header or any substantive
    # mention of NEXUS (minimum 3 references in body).
    has_subsection = "NEXUS PROTOCOL" in agent.body
    nexus_mentions = agent.body.count("NEXUS")
    if has_subsection or nexus_mentions >= 3:
        return TestResult(agent.basename, "body.nexus_protocol_present", True)

    return TestResult(
        agent=agent.basename,
        test="body.nexus_protocol_present",
        passed=False,
        message=f"Missing NEXUS documentation (no 'NEXUS PROTOCOL' header and only {nexus_mentions} NEXUS references)",
    )


def test_team_coordination_discipline(agent: AgentFile) -> TestResult:
    """
    Agents that can be spawned into teams must document SendMessage
    discipline. CTO and orchestrator already have full NEXUS docs that
    cover this; evidence-validator too. The other 19 need the short
    discipline subsection.
    """
    # Agents with their own expanded NEXUS/team docs are exempt.
    if agent.basename in {"cto", "orchestrator"}:
        return TestResult(agent.basename, "body.team_coordination_discipline", True, message="(expanded docs cover this)")

    if "Team Coordination Discipline" not in agent.body:
        return TestResult(
            agent=agent.basename,
            test="body.team_coordination_discipline",
            passed=False,
            message="Missing 'Team Coordination Discipline' subsection",
        )
    return TestResult(agent.basename, "body.team_coordination_discipline", True)


def test_no_deprecated_agent_tool_reference(agent: AgentFile) -> TestResult:
    """
    The 'Agent tool' capability reference was removed in favor of NEXUS.
    The phrase should not appear as a capability claim anywhere.
    """
    forbidden_patterns = [
        r"use the Agent tool",
        r"dispatch.*via Agent tool",
        r"Agent tool to launch",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, agent.body, re.IGNORECASE):
            return TestResult(
                agent=agent.basename,
                test="body.no_deprecated_agent_tool_reference",
                passed=False,
                message=f"Found deprecated pattern: '{pattern}'",
            )
    return TestResult(agent.basename, "body.no_deprecated_agent_tool_reference", True)


def test_description_non_trivial(agent: AgentFile) -> TestResult:
    desc = agent.frontmatter.get("description", "")
    if len(desc) < 100:
        return TestResult(
            agent=agent.basename,
            test="frontmatter.description_non_trivial",
            passed=False,
            message=f"description is only {len(desc)} chars (min 100)",
        )
    return TestResult(agent.basename, "frontmatter.description_non_trivial", True)


def test_body_non_trivial(agent: AgentFile) -> TestResult:
    if len(agent.body) < 500:
        return TestResult(
            agent=agent.basename,
            test="body.non_trivial",
            passed=False,
            message=f"body is only {len(agent.body)} chars (min 500)",
        )
    return TestResult(agent.basename, "body.non_trivial", True)


def test_frontmatter_description_single_line(agent: AgentFile) -> TestResult:
    """
    CRITICAL harness compatibility check — prevents the session-sentinel
    registration bug we hit on 2026-04-14.

    The Claude Code agent-teams harness expects the `description:` field
    to be a single-line YAML scalar. If the description contains LITERAL
    newlines (i.e., the YAML string spans multiple lines), parsing fails
    silently and the agent does NOT register. Other agents register fine;
    the broken one just becomes unavailable at dispatch time.

    Fix: use `\\n` escape sequences within a single-line "..." scalar, as
    every working agent file does.

    Detection: scan the raw frontmatter for `description: "..."` and check
    that the CLOSING quote appears before any newline.
    """
    fm = agent.frontmatter_raw

    # Find the line starting with "description:"
    lines = fm.split("\n")
    desc_start_idx = None
    for i, line in enumerate(lines):
        if re.match(r'^description:\s*"', line):
            desc_start_idx = i
            break

    if desc_start_idx is None:
        # No description at all — separate test catches this.
        return TestResult(agent.basename, "frontmatter.description_single_line", True, message="(no description to check)")

    start_line = lines[desc_start_idx]
    # Strip `description: "` prefix.
    content_after_quote = re.sub(r'^description:\s*"', '', start_line)

    # Count unescaped closing quotes on this line.
    # We look for `"` not preceded by `\`.
    closed = re.search(r'(?<!\\)"', content_after_quote)

    if closed:
        # Closing quote on same line — GOOD.
        return TestResult(agent.basename, "frontmatter.description_single_line", True)

    # Closing quote is on a subsequent line → multi-line description → harness incompatibility.
    # Find where it closes for the error message.
    for i in range(desc_start_idx + 1, len(lines)):
        if re.search(r'(?<!\\)"', lines[i]):
            span = i - desc_start_idx + 1
            return TestResult(
                agent=agent.basename,
                test="frontmatter.description_single_line",
                passed=False,
                message=f"description spans {span} lines with literal newlines. "
                        f"Agent-teams harness will fail to register this agent. "
                        f"Fix: collapse to a single line with \\n escapes, "
                        f"same as working agents (e.g. challenger.md).",
            )

    return TestResult(
        agent=agent.basename,
        test="frontmatter.description_single_line",
        passed=False,
        message="description has an unclosed quote — malformed YAML",
    )


CONTRACT_TESTS = [
    test_frontmatter_required_fields,
    test_frontmatter_name_matches_filename,
    test_model_valid,
    test_model_not_haiku,
    test_frontmatter_description_single_line,
    test_description_non_trivial,
    test_body_non_trivial,
    test_closing_protocol_sections,
    test_nexus_protocol_present,
    test_team_coordination_discipline,
    test_no_deprecated_agent_tool_reference,
]


# ----------------------------------------------------------------------
# Harness
# ----------------------------------------------------------------------

def run_tests_for_agent(path: Path) -> list[TestResult]:
    try:
        agent = load_agent(path)
    except Exception as e:
        return [TestResult(path.stem, "load", False, str(e))]

    results = []
    for test_fn in CONTRACT_TESTS:
        try:
            results.append(test_fn(agent))
        except Exception as e:
            results.append(TestResult(agent.basename, test_fn.__name__, False, f"harness error: {e}"))

    return results


def find_agents(filter_name: Optional[str] = None, changed_only: bool = False) -> list[Path]:
    if filter_name:
        path = AGENTS_DIR / f"{filter_name}.md"
        if not path.exists():
            print(f"ERROR: agent file not found: {path}", file=sys.stderr)
            sys.exit(2)
        return [path]

    all_agents = sorted(AGENTS_DIR.glob("*.md"))

    if changed_only:
        try:
            diff = subprocess.run(
                ["git", "diff", "--name-only", "--", ".claude/agents/"],
                capture_output=True, text=True, cwd=REPO_ROOT, check=True,
            )
            staged = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--", ".claude/agents/"],
                capture_output=True, text=True, cwd=REPO_ROOT, check=True,
            )
            changed = set((diff.stdout + staged.stdout).strip().splitlines())
            return [a for a in all_agents if f".claude/agents/{a.name}" in changed]
        except subprocess.CalledProcessError:
            print("WARN: --changed-only requested but git failed; running all", file=sys.stderr)
            return all_agents

    return all_agents


def print_summary(results: list[TestResult]) -> int:
    by_agent: dict[str, list[TestResult]] = {}
    for r in results:
        by_agent.setdefault(r.agent, []).append(r)

    total_pass = sum(1 for r in results if r.passed)
    total_fail = sum(1 for r in results if not r.passed)

    for agent in sorted(by_agent):
        agent_results = by_agent[agent]
        agent_fails = [r for r in agent_results if not r.passed]
        if agent_fails:
            print(f"\n✗ {agent} — {len(agent_fails)} failure(s)")
            for r in agent_fails:
                print(f"    ✗ {r.test}: {r.message}")
        else:
            print(f"✓ {agent} — all {len(agent_results)} tests passed")

    print(f"\n{'=' * 60}")
    print(f"Total: {total_pass} passed, {total_fail} failed "
          f"({len(by_agent)} agent(s) tested)")

    return 1 if total_fail > 0 else 0


def write_junit(results: list[TestResult], output: Path) -> None:
    # Minimal JUnit XML for CI integration.
    from xml.sax.saxutils import escape
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append(f'<testsuite name="agent-contracts" tests="{len(results)}">')
    for r in results:
        lines.append(f'  <testcase classname="{r.agent}" name="{r.test}">')
        if not r.passed:
            lines.append(f'    <failure message="{escape(r.message)}"/>')
        lines.append('  </testcase>')
    lines.append('</testsuite>')
    output.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", help="Test only this agent by name (no .md suffix)")
    parser.add_argument("--changed-only", action="store_true",
                        help="Test only agents modified in git working tree")
    parser.add_argument("--junit", type=Path, help="Write JUnit XML to this path")
    parser.add_argument("--json", action="store_true", help="Emit JSON output instead of text")
    args = parser.parse_args()

    agents = find_agents(args.agent, args.changed_only)
    if not agents:
        print("No agents matched the filter.", file=sys.stderr)
        return 0

    all_results: list[TestResult] = []
    for path in agents:
        all_results.extend(run_tests_for_agent(path))

    if args.json:
        print(json.dumps([r.as_dict() for r in all_results], indent=2))
    else:
        exit_code = print_summary(all_results)

    if args.junit:
        write_junit(all_results, args.junit)

    if args.json:
        return 1 if any(not r.passed for r in all_results) else 0
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

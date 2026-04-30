# Cross-Agent Flags — Findings for Other Agents' Domains

Agents write CROSS-AGENT FLAG signals here when they discover something outside their domain.
CTO/Orchestrator routes to the target agent.

**Format:** `- (YYYY-MM-DD, agent=<source>, session=<id>, target=<agent>) <finding>`
**Processing:** IMMEDIATE — route to the target agent.
**Cleared:** After the target agent is dispatched with the finding.

---

<!-- Entries below this line — append new entries -->

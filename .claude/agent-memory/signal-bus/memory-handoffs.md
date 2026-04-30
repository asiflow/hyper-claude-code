# Memory Handoffs — Learnings for Memory-Coordinator

Agents write MEMORY HANDOFF signals here. Memory-coordinator processes them during Pattern F.

**Format:** `- (YYYY-MM-DD, agent=<name>, session=<id>) <learning content>`
**Processing:** BATCH — accumulated until Pattern F, then memory-coordinator consolidates.
**Cleared:** After memory-coordinator processes.

---

<!-- Entries below this line — append new entries -->

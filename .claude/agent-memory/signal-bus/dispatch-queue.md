# Dispatch Queue — Pending Agent Dispatches

Agents write DISPATCH RECOMMENDATION signals here when chained dispatches are needed.

**Format:** `- (YYYY-MM-DD, agent=<source>) dispatch <target> for <reason>`
**Processing:** Main thread reads this when processing signal bus after agent returns.
**Cleared:** After dispatch occurs.

---

<!-- Entries below this line — append new entries -->

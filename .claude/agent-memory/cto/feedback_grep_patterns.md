---
name: CTO Grep Pattern Lesson
description: When verifying agent findings via grep, test regex against the exact claimed string — dotted names like asyncio.CancelledError won't match \w+
type: feedback
---

When grepping to verify agent findings, test the regex against the exact claimed pattern before asserting "no matches found."

**Why:** CTO searched for `except \w+, \w+:` to verify bare-comma except syntax. This regex doesn't match module-qualified names like `asyncio.CancelledError` (the dot breaks `\w+`). CTO incorrectly declared the code didn't exist and blamed evidence-validator — but the validator was correct.

**How to apply:** When verifying patterns containing Python dotted names (module.Class), use `except .*,` or a pattern that accounts for dots. Better yet, use a broader initial grep and narrow down, rather than a narrow grep that may miss valid matches.

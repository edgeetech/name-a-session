---
description: Set a human-readable name for the current Claude session
argument-hint: [name]
allowed-tools: Bash(python:*)
---

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/store.py" rename "$ARGUMENTS"`

If the command output above is exactly `ASK_USER_FOR_NAME`:
1. Ask the user a single short question: "What should this session be named?" — wait for their reply.
2. Once they answer, run this Bash command, substituting their answer for `<NAME>`:
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/store.py" rename "<NAME>"`
3. Report the resulting `OK: ...` line verbatim. Do not add extra commentary.

Otherwise, report the command output verbatim. Do not add extra commentary.

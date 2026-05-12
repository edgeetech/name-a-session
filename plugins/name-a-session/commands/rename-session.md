---
description: Set a human-readable name for the current Claude session
argument-hint: <name>
allowed-tools: Bash(python:*)
---

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/store.py" rename "$ARGUMENTS"`

Report the result of the command above to the user verbatim. Do not add extra commentary.

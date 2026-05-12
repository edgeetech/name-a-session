---
description: Search saved Claude sessions by name (substring match, case-insensitive)
argument-hint: <query>
allowed-tools: Bash(python:*)
---

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/store.py" find "$ARGUMENTS"`

Show the table above to the user verbatim. Do not add commentary or reformat.

---
description: Search saved Claude sessions by name or folder (substring, case-insensitive). Omit query to list all.
argument-hint: [query]
allowed-tools: Bash(python:*)
---

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/store.py" find "$ARGUMENTS"`

Show the table above to the user verbatim. Do not add commentary or reformat.

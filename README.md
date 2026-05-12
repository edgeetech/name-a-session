# name-a-session

Claude Code plugin to label the active session with a human-readable name and search past sessions by that name — all from the CLI, no Claude Desktop required.

Author: Ahmet Selcuk OZYURT | EdgeeTech

## Install

```bash
/plugin marketplace add edgeetech/name-a-session
/plugin install name-a-session@name-a-session
```

Restart Claude Code after install so the `SessionStart` hook and slash commands register.

## Usage

- `/rename-session <name>` — set a name on the current session.
- `/find-session <query>` — case-insensitive substring search. Prints `NAME | SESSION_ID | CWD`.

New sessions are automatically recorded (unnamed) on launch via a `SessionStart` hook.

Resume a session from search output:

```bash
claude --resume <session_id>
```

## Storage

All names and metadata are stored in:

```
C:/Workspace/.claude/session-names.json
```

The file is global across projects, auto-created on first use, and contains one entry per session id:

```json
{
  "<session-id>": {
    "name": "my feature work",
    "cwd": "C:/Workspace/...",
    "transcript": "...",
    "created": 1715520000.0,
    "updated": 1715520000.0,
    "last_seen": 1715520000.0
  }
}
```

> Note: the storage path is currently hardcoded for the author's setup. Adjust `STORE` in `plugins/name-a-session/scripts/store.py` if you use a different `CLAUDE_CONFIG_DIR`.

## Layout

```
.claude-plugin/marketplace.json         # marketplace manifest
plugins/name-a-session/
├── .claude-plugin/plugin.json          # plugin manifest
├── commands/rename-session.md          # /rename-session
├── commands/find-session.md            # /find-session
├── hooks/hooks.json                    # SessionStart capture
└── scripts/store.py                    # storage backend (Python 3)
```

## Requirements

- Python 3 on `PATH`
- Claude Code with plugin support

## License

MIT

<div align="center">

# 🏷️ name-a-session

### *Give your Claude Code sessions real names — and find them later.*

[![Version](https://img.shields.io/badge/version-0.3.4-blue?style=for-the-badge)](./plugins/name-a-session/.claude-plugin/plugin.json)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white)](https://docs.claude.com/en/docs/claude-code)
[![Python](https://img.shields.io/badge/python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#-license)
[![Built by EdgeeTech](https://img.shields.io/badge/built%20by-EdgeeTech-FF6B6B?style=for-the-badge)](https://github.com/edgeetech)

</div>

---

## ✨ Why this plugin?

Claude Code's built-in `/rename` renames the **current** session in the **current** project picker.
That's it. No global history. No search across projects. No auto-tracking.

This plugin **levels that up**:

| Feature | Built-in `/rename` | 🏷️ `name-a-session` |
|---|:---:|:---:|
| 📛 Rename current session | ✅ | ✅ |
| 🌍 Global registry across **all** projects | ❌ | ✅ |
| 🔎 Substring search by name **or** folder | ❌ | ✅ |
| 📡 Auto-records every session on launch | ❌ | ✅ |
| 🪝 Mirrors built-in `/rename` into the registry | ❌ | ✅ |
| 🔄 `/rename-session` writes back to built-in title too | ❌ | ✅ |
| 💬 Prompts for a name if you forget the argument | ❌ | ✅ |
| 🚀 One-line resume command (`cd` + `--resume`) | ❌ | ✅ |
| 🎨 Markdown-rendered result table | ❌ | ✅ |

---

## 🚀 Install

```bash
/plugin marketplace add edgeetech/name-a-session
/plugin install name-a-session@name-a-session
/reload-plugins
```

> 💡 Restart Claude Code if hooks don't fire immediately.

---

## 🧰 Usage

### 📝 Name the current session

```text
/rename-session my feature work
```

```
OK: session 9398a66f-… renamed to: my feature work (also mirrored to built-in /rename)
```

Forget the argument? The plugin asks for it:

```text
/rename-session
```
> *What should this session be named?*

Type your answer — the rename runs with it.

### 🔍 Find a session

Search by **name or folder** (case-insensitive substring). Omit the query to list everything.

```text
/find-session sevdiye
```

| 🏷️ Name | 📁🔗 Resume command |
|---|---|
| **Sevdiyem Session** | `cd "C:\Workspace\EDGEETECH\ai\name-a-session" && claude --resume 9398a66f-b1dc-452b-b324-9e54d9350b80` |

_1 session(s) matching `sevdiye`_

The 📁🔗 column embeds the folder inside the resume command, so you copy-paste a single line and you're back in the right cwd with the right session.

### ▶️ Resume

```bash
cd "C:\Workspace\EDGEETECH\ai\foo" && claude --resume 9398a66f-b1dc-…
```

---

## 🧠 How it works

```
┌──────────────────┐  SessionStart  ┌─────────────────────────────┐
│  claude launches │ ──────────────▶│  store.py capture           │
└──────────────────┘                │  scans transcript for title │
                                    └──────────────┬──────────────┘
                                                   │
                       Stop (after every turn)     │
        ┌─────────────────────────────────────────▶│
        │                                          ▼
┌──────────────────┐                  ┌─────────────────────────────┐
│ built-in /rename │ ── writes ─────▶│ <session>.jsonl transcript  │
└──────────────────┘   custom-title   │   {"type":"custom-title"}   │
                                      └──────────────┬──────────────┘
                                                     │ tail-scan
                                                     ▼
┌──────────────────┐                  ┌─────────────────────────────┐
│ /rename-session  │ ── writes ─────▶│  C:/Workspace/.claude/      │
└──────────────────┘ name + mirrors   │  session-names.json         │
        ▲                              └──────────────┬──────────────┘
        │                                             │
        └──────────── /find-session ──────────────────┘
```

- 🪝 **`SessionStart` hook** registers every session (id, cwd, transcript path) and immediately scans the transcript for any pre-existing built-in title.
- 🪝 **`Stop` hook** runs after each Claude turn, tails the last 256 KB of the transcript JSONL, and absorbs the latest `{"type":"custom-title","customTitle":"…"}` — the artefact the built-in `/rename` writes.
- 📝 **`/rename-session`** writes the name into the global registry **and** appends a `custom-title` event to the transcript, so Claude Code's own session title stays in sync.
- 🔎 **`/find-session`** filters the registry (substring on name *or* folder) and prints a 2-column markdown table that Claude Code renders natively.

> 💡 Why not a `UserPromptSubmit` hook for the built-in command?
> Slash commands like `/rename` are intercepted client-side and never reach `UserPromptSubmit`. The transcript is the only artefact common to both paths, so the plugin reads from / writes to it directly.

### 🔁 Loop-safe

Both sides write `custom-title` events, both sides read them. To avoid an endless ping-pong:

- The registry tracks `last_builtin_title` per session.
- A `Stop`-hook scan only adopts a transcript title when it **differs** from `last_builtin_title`.
- `/rename-session` updates `last_builtin_title` to the value it just wrote.

Net effect: each title change propagates once, in either direction, then stops.

---

## 💾 Storage

All data lives in a single JSON file:

```
C:/Workspace/.claude/session-names.json
```

```json
{
  "9398a66f-b1dc-452b-b324-9e54d9350b80": {
    "name": "Sevdiyem Session",
    "cwd": "C:\\Workspace\\EDGEETECH\\ai\\name-a-session",
    "transcript": "C:\\Workspace\\.claude\\projects\\…\\….jsonl",
    "created": 1715520000.0,
    "updated": 1715520400.0,
    "last_seen": 1715520400.0,
    "last_builtin_title": "Sevdiyem Session",
    "source": "rename-session"
  }
}
```

> ⚠️ Path is **hard-coded** to the author's `CLAUDE_CONFIG_DIR`. Edit `STORE` in
> [`plugins/name-a-session/scripts/store.py`](./plugins/name-a-session/scripts/store.py)
> if yours differs.

---

## 🗂️ Repo layout

```
name-a-session/
├── .claude-plugin/
│   └── marketplace.json              📦 marketplace manifest
└── plugins/name-a-session/
    ├── .claude-plugin/plugin.json    🏷️  plugin manifest
    ├── commands/
    │   ├── rename-session.md         📝 /rename-session (prompts if empty)
    │   └── find-session.md           🔍 /find-session
    ├── hooks/hooks.json              🪝 SessionStart + Stop hooks
    └── scripts/store.py              🐍 storage backend
```

---

## 📋 Requirements

- 🐍 Python 3.7+ on `PATH` (uses `sys.stdout.reconfigure` for UTF-8 stdout on Windows consoles)
- 💬 Claude Code with plugin support

---

## 🛣️ Roadmap

- [ ] Make storage path configurable via env var
- [ ] `--json` output mode for scripting
- [ ] `/forget-session <id>` to prune the registry
- [ ] Cross-platform `cd` (POSIX vs PowerShell vs cmd) in the resume column

---

## 👤 Author

**Ahmet Selcuk OZYURT** — [EdgeeTech](https://github.com/edgeetech)

## 📄 License

MIT — see [`LICENSE`](./LICENSE).

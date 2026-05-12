#!/usr/bin/env python3
import json, os, sys, time
from pathlib import Path

# Force UTF-8 stdout so emoji in the markdown table don't blow up on the
# default cp1252 Windows console.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TRANSCRIPT_TAIL_BYTES = 262144  # 256 KB tail is plenty to find the latest title


def _scan_transcript_for_title(path):
    """Return the most recent customTitle recorded in a Claude Code transcript, or None."""
    if not path:
        return None
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            if size > TRANSCRIPT_TAIL_BYTES:
                f.seek(size - TRANSCRIPT_TAIL_BYTES)
                f.readline()  # discard partial line
            data = f.read().decode("utf-8", errors="ignore")
    except OSError:
        return None
    title = None
    for line in data.splitlines():
        if "custom-title" not in line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("type") == "custom-title" and rec.get("customTitle"):
            title = rec["customTitle"]
    return title

STORE = Path("C:/Workspace/.claude/session-names.json")

def load():
    if STORE.exists():
        try:
            return json.loads(STORE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}

def save(d):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(d, indent=2), encoding="utf-8")

def _upsert(sid, payload, source_hint=None):
    """Insert/update entry, then absorb any built-in title found in the transcript."""
    d = load()
    entry = d.get(sid, {})
    entry.setdefault("name", "")
    entry["cwd"] = payload.get("cwd") or entry.get("cwd", "")
    entry["transcript"] = (
        payload.get("transcript_path") or entry.get("transcript", "")
    )
    entry.setdefault("created", time.time())
    entry["last_seen"] = time.time()

    title = _scan_transcript_for_title(entry.get("transcript"))
    # Only adopt a built-in title when it has actually changed since last sync,
    # so an explicit `/rename-session` is not clobbered on the next Stop event.
    if title and title != entry.get("last_builtin_title"):
        entry["name"] = title
        entry["last_builtin_title"] = title
        entry["updated"] = time.time()
        entry["source"] = "builtin-rename"
    elif source_hint and not entry.get("source"):
        entry["source"] = source_hint

    d[sid] = entry
    save(d)


def cmd_capture():
    """SessionStart hook: register the session and pull any existing built-in title."""
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    sid = payload.get("session_id")
    if not sid:
        return
    _upsert(sid, payload, source_hint="session-start")


def cmd_sync():
    """Stop hook: after each Claude turn, mirror built-in /rename from the transcript."""
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    sid = payload.get("session_id")
    if not sid:
        return
    _upsert(sid, payload)


def _write_builtin_title(transcript_path, sid, name):
    """Append a `custom-title` event to the session transcript so the built-in
    `/rename` title in Claude Code stays in sync with our plugin rename."""
    if not transcript_path:
        return False
    p = Path(transcript_path)
    if not p.exists():
        return False
    try:
        with open(p, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({
                "type": "custom-title",
                "customTitle": name,
                "sessionId": sid,
            }) + "\n")
        return True
    except OSError:
        return False


def _resolve_current_session_id(d):
    """Pick the current session id.

    Preference order:
      1. $CLAUDE_SESSION_ID env (set in hook contexts).
      2. Newest transcript JSONL under the current cwd's project dir.
      3. Most recently seen entry in the registry.
    """
    sid = os.environ.get("CLAUDE_SESSION_ID", "").strip()
    if sid:
        return sid

    cwd = os.getcwd()
    encoded = cwd.replace(":", "-").replace("\\", "-").replace("/", "-")
    proj_dir = Path("C:/Workspace/.claude/projects") / encoded
    if proj_dir.is_dir():
        files = sorted(proj_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            return files[0].stem

    if d:
        return max(d.items(), key=lambda kv: kv[1].get("last_seen", 0))[0]

    return ""


def cmd_rename(name):
    name = name.strip()
    if not name:
        print("ASK_USER_FOR_NAME")
        return
    d = load()
    sid = _resolve_current_session_id(d)
    if not sid:
        print("ERR: cannot resolve current session id")
        return
    entry = d.setdefault(sid, {
        "cwd": os.getcwd(),
        "transcript": "",
        "created": time.time(),
    })
    entry["name"] = name
    entry["updated"] = time.time()
    entry["source"] = "rename-session"
    # Mirror to built-in so Claude Code's own session title matches.
    mirrored = _write_builtin_title(entry.get("transcript"), sid, name)
    if mirrored:
        # Avoid Stop hook re-importing the same title as a "new" built-in change.
        entry["last_builtin_title"] = name
    save(d)
    suffix = " (also mirrored to built-in /rename)" if mirrored else ""
    print(f"OK: session {sid} renamed to: {name}{suffix}")

def _md_escape(s):
    return s.replace("|", "\\|").replace("\n", " ")


def cmd_find(q):
    q = q.strip().lower()
    d = load()
    items = list(d.items())
    if q:
        items = [
            (s, e)
            for s, e in items
            if q in e.get("name", "").lower() or q in e.get("cwd", "").lower()
        ]
    if not items:
        print(f"_no matches_" + (f" for `{q}`" if q else ""))
        return
    items.sort(
        key=lambda x: x[1].get("updated", x[1].get("last_seen", 0)),
        reverse=True,
    )

    print("| 🏷️ Name | 📁🔗 Resume command |")
    print("|---|---|")
    for sid, e in items:
        name = e.get("name") or "_(unnamed)_"
        cwd = e.get("cwd", "") or ""
        cli = f'cd "{cwd}" && claude --resume {sid}'
        print(f"| **{_md_escape(name)}** | `{_md_escape(cli)}` |")

    suffix = f" matching `{q}`" if q else ""
    print(f"\n_{len(items)} session(s){suffix}_")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: store.py {capture|rename|find} [args...]")
    op = sys.argv[1]
    arg = " ".join(sys.argv[2:])
    if op == "capture":
        cmd_capture()
    elif op == "rename":
        cmd_rename(arg)
    elif op == "find":
        cmd_find(arg)
    elif op == "sync":
        cmd_sync()
    else:
        sys.exit(f"unknown op: {op}")

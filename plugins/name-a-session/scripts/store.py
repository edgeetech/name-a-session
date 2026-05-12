#!/usr/bin/env python3
import json, os, sys, time
from pathlib import Path

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

def cmd_capture():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    sid = payload.get("session_id")
    if not sid:
        return
    d = load()
    entry = d.get(sid, {})
    entry.setdefault("name", "")
    entry["cwd"] = payload.get("cwd", entry.get("cwd", ""))
    entry["transcript"] = payload.get("transcript_path", entry.get("transcript", ""))
    entry.setdefault("created", time.time())
    entry["last_seen"] = time.time()
    d[sid] = entry
    save(d)

def cmd_rename(name):
    name = name.strip()
    if not name:
        print("ERR: empty name")
        return
    sid = os.environ.get("CLAUDE_SESSION_ID", "").strip()
    if not sid:
        print("ERR: CLAUDE_SESSION_ID not set")
        return
    d = load()
    entry = d.setdefault(sid, {
        "cwd": os.getcwd(),
        "transcript": "",
        "created": time.time(),
    })
    entry["name"] = name
    entry["updated"] = time.time()
    save(d)
    print(f"OK: session {sid} renamed to: {name}")

def cmd_find(q):
    q = q.strip().lower()
    d = load()
    if not q:
        hits = list(d.items())
    else:
        hits = [(s, e) for s, e in d.items() if q in e.get("name", "").lower()]
    if not hits:
        print("no matches")
        return
    hits.sort(key=lambda x: x[1].get("updated", x[1].get("last_seen", 0)), reverse=True)
    print(f"{'NAME':<32}  {'SESSION_ID':<38}  CWD")
    print("-" * 100)
    for sid, e in hits:
        name = e.get("name") or "(unnamed)"
        cwd = e.get("cwd", "")
        print(f"{name[:32]:<32}  {sid:<38}  {cwd}")

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
    else:
        sys.exit(f"unknown op: {op}")

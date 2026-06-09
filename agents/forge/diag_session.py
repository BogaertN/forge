"""
Forge diag_session.py
Level 0.8 — Diagnostic Session Continuity.

A diagnostic session is a named troubleshooting chain that links:
  - Proposals (commands Forge suggested)
  - Diagnostic outputs (terminal output Nic pasted)
  - Interpretations (what Forge concluded)
  - Next steps (what Forge recommended)

Each session is stored as a JSON file in:
  ~/forge/diagnostics/sessions/<session_id>/session.json

CRITICAL: No subprocess, no os.system, no shell access. Storage only.
"""

import os
import re
import json
import datetime
from pathlib import Path
from typing import Optional

FORGE_ROOT    = Path(__file__).resolve().parents[2]
SESSIONS_DIR  = FORGE_ROOT / "diagnostics" / "sessions"

VALID_STATUSES = {"open", "in_progress", "resolved", "abandoned"}


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _slug(topic: str) -> str:
    """Make a filename-safe slug from a topic string."""
    slug = re.sub(r"[^\w\s-]", "", topic.lower())
    slug = re.sub(r"[\s_]+", "_", slug.strip())
    return slug[:50].rstrip("_") or "session"


def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _session_dir(session_id: str) -> Path:
    return SESSIONS_DIR / session_id


def _session_file(session_id: str) -> Path:
    return _session_dir(session_id) / "session.json"


def _load(session_id: str) -> dict:
    path = _session_file(session_id)
    if not path.exists():
        raise FileNotFoundError(f"Session not found: {session_id}")
    with open(path, "r") as f:
        return json.load(f)


def _save(session_id: str, data: dict):
    path = _session_file(session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = _now()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ─── SESSION LIFECYCLE ───────────────────────────────────────────────────────

def create_session(topic: str, forge_session_id: str) -> str:
    """
    Create a new diagnostic session.
    Returns the session_id.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = _slug(topic)
    session_id = f"{timestamp}_{slug}"

    data = {
        "session_id":       session_id,
        "topic":            topic,
        "started_at":       _now(),
        "forge_session_id": forge_session_id,
        "status":           "open",
        "issue_description": "",
        "events":           [],
        "next_step":        "",
        "resolved":         False,
        "last_updated":     _now(),
    }

    _session_dir(session_id).mkdir(parents=True, exist_ok=True)
    _save(session_id, data)
    return session_id


def get_session(session_id: str) -> dict:
    """Return the full session dict."""
    return _load(session_id)


def update_status(session_id: str, status: str, resolution_note: str = "") -> dict:
    """Update session status. Returns updated session."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Choose from: {VALID_STATUSES}")
    data = _load(session_id)
    data["status"] = status
    data["resolved"] = status == "resolved"
    if resolution_note:
        data["issue_description"] = resolution_note
    _save(session_id, data)
    return data


# ─── EVENT LINKING ────────────────────────────────────────────────────────────

def link_proposal(
    session_id: str,
    proposal_path: str,
    command: str,
    allowed: bool,
    risk_level: str = "",
) -> None:
    """Link a proposal file to this session."""
    data = _load(session_id)
    event = {
        "type":      "PROPOSAL",
        "timestamp": _now(),
        "file":      proposal_path,
        "command":   command,
        "allowed":   allowed,
        "risk":      risk_level,
    }
    data["events"].append(event)
    if data["status"] == "open":
        data["status"] = "in_progress"
    _save(session_id, data)


def link_diagnostic(
    session_id: str,
    diag_path: str,
    command: str,
    sha256: str,
    line_count: int,
) -> None:
    """Link a diagnostic output file to this session."""
    data = _load(session_id)
    event = {
        "type":       "DIAGNOSTIC_OUTPUT",
        "timestamp":  _now(),
        "file":       diag_path,
        "command":    command,
        "sha256":     sha256,
        "line_count": line_count,
    }
    data["events"].append(event)
    if data["status"] == "open":
        data["status"] = "in_progress"
    _save(session_id, data)


def add_interpretation(
    session_id: str,
    summary: str,
    next_step: str = "",
) -> None:
    """
    Record an interpretation event — what Forge concluded from the diagnostic output.
    Optionally record the recommended next step.
    """
    data = _load(session_id)
    event = {
        "type":      "INTERPRETATION",
        "timestamp": _now(),
        "summary":   summary,
        "next_step": next_step,
    }
    data["events"].append(event)
    if next_step:
        data["next_step"] = next_step
    _save(session_id, data)


# ─── DISPLAY ─────────────────────────────────────────────────────────────────

def format_status(session_id: str) -> str:
    """Return a human-readable status string for the session."""
    try:
        data = _load(session_id)
    except FileNotFoundError:
        return f"[forge] Session not found: {session_id}"

    events = data.get("events", [])
    lines = [
        "",
        "── Diagnostic Session ────────────────────────────────",
        f"  ID        : {data['session_id']}",
        f"  Topic     : {data['topic']}",
        f"  Status    : {data['status'].upper()}",
        f"  Started   : {data['started_at']}",
        f"  Updated   : {data['last_updated']}",
        f"  Events    : {len(events)}",
    ]

    if data.get("next_step"):
        lines.append(f"  Next step : {data['next_step']}")

    if events:
        lines.append("")
        lines.append("  Event history:")
        for i, event in enumerate(events, start=1):
            etype = event.get("type", "?")
            ts    = event.get("timestamp", "?")[:19]
            if etype == "PROPOSAL":
                status = "APPROVED" if event.get("allowed") else "REFUSED"
                lines.append(f"    {i}. [{ts}] PROPOSAL ({status}): {event.get('command', '')}")
                lines.append(f"         File: {event.get('file', '')}")
            elif etype == "DIAGNOSTIC_OUTPUT":
                lines.append(f"    {i}. [{ts}] DIAGNOSTIC_OUTPUT: {event.get('command', '')} ({event.get('line_count', '?')} lines, sha256={event.get('sha256', '?')})")
                lines.append(f"         File: {event.get('file', '')}")
            elif etype == "INTERPRETATION":
                summary = event.get("summary", "")[:80]
                lines.append(f"    {i}. [{ts}] INTERPRETATION: {summary}")
                if event.get("next_step"):
                    lines.append(f"         Next step: {event['next_step']}")

    lines.append("──────────────────────────────────────────────────────")
    return "\n".join(lines)


def format_summary_line(session_id: str) -> str:
    """One-line summary for session list display."""
    try:
        data = _load(session_id)
        n = len(data.get("events", []))
        return (
            f"  {data['session_id']:<50} "
            f"[{data['status'].upper():<11}] "
            f"{n} events"
        )
    except FileNotFoundError:
        return f"  {session_id} [NOT FOUND]"


# ─── SESSION LIST ─────────────────────────────────────────────────────────────

def list_sessions(limit: int = 10) -> list[str]:
    """
    Return session_ids sorted newest-first.
    Only returns sessions that have a valid session.json.
    """
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sessions = []
    for item in sorted(SESSIONS_DIR.iterdir(), reverse=True):
        if item.is_dir() and (item / "session.json").exists():
            sessions.append(item.name)
            if len(sessions) >= limit:
                break
    return sessions


def get_active_session_context(session_id: str) -> str:
    """
    Return a compact string describing the active session for inclusion
    in the system prompt. Tells the model what is being investigated
    and what has happened so far.
    """
    try:
        data = _load(session_id)
    except FileNotFoundError:
        return ""

    events = data.get("events", [])
    n_proposals   = sum(1 for e in events if e["type"] == "PROPOSAL")
    n_outputs     = sum(1 for e in events if e["type"] == "DIAGNOSTIC_OUTPUT")
    n_interp      = sum(1 for e in events if e["type"] == "INTERPRETATION")

    context_lines = [
        f"ACTIVE DIAGNOSTIC SESSION: {data['session_id']}",
        f"  Topic   : {data['topic']}",
        f"  Status  : {data['status']}",
        f"  Events  : {n_proposals} proposal(s), {n_outputs} output(s), {n_interp} interpretation(s)",
    ]

    if data.get("next_step"):
        context_lines.append(f"  Next step on record: {data['next_step']}")

    # Most recent interpretation
    last_interp = None
    for e in reversed(events):
        if e["type"] == "INTERPRETATION":
            last_interp = e
            break
    if last_interp:
        context_lines.append(f"  Last finding: {last_interp.get('summary', '')[:120]}")

    return "\n".join(context_lines)

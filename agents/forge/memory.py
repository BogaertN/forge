"""
Forge memory.py
Append-only hash-chained audit log and session memory management.

Audit entry format:
[timestamp] SESSION: {id} | TOOL: {tool} | PATH: {path} | LINES: {lines} | REASON: {reason} | PREV_HASH: {prev} | ENTRY_HASH: {hash}
"""

import os
import json
import hashlib
import datetime
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR   = FORGE_ROOT / "logs"
MEMORY_DIR = FORGE_ROOT / "memory"

# _AUDIT_LOG_OVERRIDE: set this in tests to redirect audit writes to a temp file.
# Never set this in production code. Default is None (uses the real log).
_AUDIT_LOG_OVERRIDE: Path | None = None

AUDIT_LOG        = LOGS_DIR / "forge_audit.log"
ERROR_LOG        = LOGS_DIR / "forge_error.log"
USER_PROFILE     = MEMORY_DIR / "user_profile.json"
PROJECT_PROFILE  = MEMORY_DIR / "project_profile.json"
KNOWN_ERRORS     = MEMORY_DIR / "known_errors.json"


def _active_audit_log() -> Path:
    """Return the active audit log path. Tests can override via _AUDIT_LOG_OVERRIDE."""
    return _AUDIT_LOG_OVERRIDE if _AUDIT_LOG_OVERRIDE is not None else AUDIT_LOG


# ─── AUDIT LOG ────────────────────────────────────────────────────────────────

def _get_last_entry_hash() -> str:
    """Read the ENTRY_HASH from the last line of the audit log."""
    log = _active_audit_log()
    if not log.exists() or log.stat().st_size == 0:
        return "GENESIS"
    with open(log, "rb") as f:
        # Efficiently read last non-empty line
        f.seek(0, 2)
        size = f.tell()
        pos = size - 1
        last_line = b""
        while pos >= 0:
            f.seek(pos)
            char = f.read(1)
            if char == b"\n" and last_line.strip():
                break
            last_line = char + last_line
            pos -= 1
    line = last_line.decode("utf-8", errors="replace").strip()
    if "ENTRY_HASH:" in line:
        return line.split("ENTRY_HASH:")[-1].strip()
    return "UNKNOWN"


def _compute_entry_hash(content: str, prev_hash: str) -> str:
    """Compute SHA-256 of content + prev_hash."""
    raw = f"{content}|{prev_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def write_audit_entry(
    session_id: str,
    tool: str,
    path: str = "-",
    lines: str = "-",
    reason: str = "-",
    extra: str = "",
    _log_path: Path = None        # override for tests only — never pass this in production code
) -> str:
    """
    Write one hash-chained entry to forge_audit.log.
    Returns the entry hash.
    Raises RuntimeError if the log cannot be written (audit log is mandatory).
    _log_path is used only by unit tests to write to a temp file instead of the live log.
    """
    log_file = _log_path if _log_path is not None else AUDIT_LOG
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    prev_hash = _get_last_entry_hash()

    content = (
        f"[{timestamp}] "
        f"SESSION: {session_id} | "
        f"TOOL: {tool} | "
        f"PATH: {path} | "
        f"LINES: {lines} | "
        f"REASON: {reason}"
    )
    if extra:
        content += f" | {extra}"

    entry_hash = _compute_entry_hash(content, prev_hash)
    full_line = f"{content} | PREV_HASH: {prev_hash} | ENTRY_HASH: {entry_hash}\n"

    try:
        with open(_active_audit_log(), "a") as f:
            f.write(full_line)
    except OSError as e:
        raise RuntimeError(f"CRITICAL: Cannot write to audit log at {_active_audit_log()}: {e}")

    return entry_hash


def write_session_start(session_id: str, scope_paths: list[str]) -> str:
    """Write the session-open audit entry."""
    return write_audit_entry(
        session_id=session_id,
        tool="SESSION_START",
        path=str(scope_paths),
        lines="-",
        reason="New Forge session opened"
    )


def write_session_end(session_id: str, reason: str | bool) -> str:
    """
    Write the session-close audit entry.

    reason: a descriptive string such as:
      'FILES_UNCHANGED'          — no project writes occurred
      'APPROVED_PATCH_APPLIED'   — one or more patches were applied
      'APPROVED_ROLLBACK_RESTORED' — one or more rollbacks were restored
    Also accepts a bool for backward compatibility (True → APPROVED_PATCH_APPLIED).
    """
    if isinstance(reason, bool):
        status = "APPROVED_PATCH_APPLIED" if reason else "FILES_UNCHANGED"
    else:
        status = str(reason) if reason else "FILES_UNCHANGED"

    return write_audit_entry(
        session_id=session_id,
        tool="SESSION_END",
        path="-",
        lines="-",
        reason=status
    )


def write_error_log(session_id: str, message: str):
    """Write to the error log. Never raises — errors in error logging are printed only."""
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"[{timestamp}] SESSION: {session_id} | ERROR: {message}\n"
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(line)
    except OSError:
        print(f"[forge] WARNING: Could not write to error log: {message}")


def verify_audit_chain() -> tuple[bool, str]:
    """
    Verify the hash chain of the audit log is intact.
    Returns (valid: bool, message: str).
    """
    log = _active_audit_log()
    if not log.exists() or log.stat().st_size == 0:
        return True, "Audit log is empty. Chain is valid (no entries)."

    with open(log, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    if not lines:
        return True, "Audit log has no entries."

    prev_hash = "GENESIS"
    for i, line in enumerate(lines):
        if "PREV_HASH:" not in line or "ENTRY_HASH:" not in line:
            return False, f"Line {i+1} is missing hash fields."

        stored_prev = line.split("PREV_HASH:")[-1].split("|")[0].strip()
        stored_entry = line.split("ENTRY_HASH:")[-1].strip()

        if stored_prev != prev_hash:
            return False, (
                f"Chain broken at line {i+1}. "
                f"Expected PREV_HASH={prev_hash}, found {stored_prev}."
            )

        # Reconstruct content (everything before PREV_HASH)
        content = line.split(" | PREV_HASH:")[0]
        expected_hash = _compute_entry_hash(content, prev_hash)
        if expected_hash != stored_entry:
            return False, (
                f"Hash mismatch at line {i+1}. "
                f"Expected {expected_hash}, found {stored_entry}."
            )

        prev_hash = stored_entry

    return True, f"Chain verified. {len(lines)} entries, all intact."


# ─── SESSION MEMORY ────────────────────────────────────────────────────────────

class SessionMemory:
    """
    In-memory store for a single Forge session.
    Tracks tool calls, findings, and context for the current conversation.
    Can compress itself when approaching context limits.
    """

    MAX_TOOL_RESULTS = 20  # keep last N tool results in active memory

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.tool_calls: list[dict] = []       # all tool calls this session
        self.findings: list[str] = []          # plain-language findings accumulated
        self.files_changed: list[str] = []     # populated at higher trust levels
        self.context_compressed = False

    def record_tool_call(self, tool: str, args: dict, result: str, audit_hash: str):
        """Record a tool call and its result."""
        self.tool_calls.append({
            "tool": tool,
            "args": args,
            "result": result,
            "audit_hash": audit_hash
        })
        # Trim if over limit to keep context manageable
        if len(self.tool_calls) > self.MAX_TOOL_RESULTS:
            self._compress()

    def _compress(self):
        """
        Keep the last 10 tool calls in full detail.
        Summarize older ones as a single compressed entry.
        Write compression event to project profile.
        """
        old = self.tool_calls[:-10]
        self.tool_calls = self.tool_calls[-10:]
        summary = f"[COMPRESSED: {len(old)} earlier tool calls summarized]"
        self.tool_calls.insert(0, {
            "tool": "CONTEXT_COMPRESSION",
            "args": {},
            "result": summary,
            "audit_hash": "compressed"
        })
        self.context_compressed = True
        # Persist summary to project profile
        _update_project_profile_summary(
            f"Session {self.session_id}: context compressed after {len(old)+10} tool calls."
        )

    def get_tool_results_for_context(self) -> list[dict]:
        """Return tool calls formatted for the LLM context window."""
        return [
            {
                "role": "tool",
                "name": tc["tool"],
                "content": tc["result"][:2000]  # truncate very long results
            }
            for tc in self.tool_calls
        ]

    def add_finding(self, finding: str):
        self.findings.append(finding)

    def get_findings_summary(self) -> str:
        if not self.findings:
            return "No findings recorded yet this session."
        return "\n".join(f"- {f}" for f in self.findings)

    def nothing_changed(self) -> bool:
        return len(self.files_changed) == 0


# ─── PERSISTENT MEMORY ─────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_json(path: Path, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_user_profile() -> dict:
    return _load_json(USER_PROFILE)


def load_project_profile() -> dict:
    return _load_json(PROJECT_PROFILE)


def _update_project_profile_summary(summary: str):
    """Append a summary note to the project profile."""
    profile = _load_json(PROJECT_PROFILE)
    profile["session_summary"] = summary
    profile["last_updated"] = datetime.datetime.now().isoformat(timespec="seconds")
    _save_json(PROJECT_PROFILE, profile)


def update_project_profile(root: str, language: str = "", entry_points: list = None):
    """Update project profile when Nic scopes to a new project."""
    profile = _load_json(PROJECT_PROFILE)
    profile["project_root"] = root
    profile["current_project"] = os.path.basename(root.rstrip("/"))
    if language:
        profile["language"] = language
    if entry_points:
        profile["entry_points"] = entry_points
    profile["last_updated"] = datetime.datetime.now().isoformat(timespec="seconds")
    _save_json(PROJECT_PROFILE, profile)


def record_known_error(error_signature: str, resolution: str):
    """Add a new known error to the persistent store."""
    data = _load_json(KNOWN_ERRORS)
    errors = data.get("errors", [])
    errors.append({
        "signature": error_signature,
        "resolution": resolution,
        "recorded_at": datetime.datetime.now().isoformat(timespec="seconds")
    })
    data["errors"] = errors
    _save_json(KNOWN_ERRORS, data)


def lookup_known_error(error_text: str) -> str | None:
    """
    Check if an error matches something Forge has seen before.
    Returns the resolution string if found, None otherwise.
    Simple substring match — good enough for Level 0.5.
    """
    data = _load_json(KNOWN_ERRORS)
    for entry in data.get("errors", []):
        if entry.get("signature", "") in error_text:
            return entry.get("resolution", "")
    return None

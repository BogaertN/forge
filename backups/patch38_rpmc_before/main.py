#!/usr/bin/env python3
"""
Forge — main.py
The CLI entry point.

Usage:
  python main.py                  Start a session (prompts for scope)
  python main.py approve <path>   Add a path to approved_paths.json
  python main.py audit            Verify the integrity of forge_audit.log
  python main.py status           Show current config and trust level
"""

import os
import sys
import re
import json
import datetime
from typing import Optional
import argparse
from pathlib import Path

FORGE_ROOT   = Path(__file__).resolve().parent
sys.path.insert(0, str(FORGE_ROOT))

from agents.forge.permissions import (
    get_approved_paths,
    get_session_paths,
)
from agents.forge.memory import (
    SessionMemory,
    write_session_start,
    write_session_end,
    write_error_log,
    verify_audit_chain,
)
from agents.forge.agent import ForgeAgent

CONFIG_DIR   = FORGE_ROOT / "config"
LOGS_DIR     = FORGE_ROOT / "logs"
MEMORY_DIR   = FORGE_ROOT / "memory"

APPROVED_PATHS_FILE = CONFIG_DIR / "approved_paths.json"
SESSION_SCOPE_FILE  = CONFIG_DIR / "session_scope.json"
AUDIT_LOG           = LOGS_DIR / "forge_audit.log"


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _save_json(path: Path, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _make_session_id() -> str:
    now = datetime.datetime.now()
    return f"forge_{now.strftime('%Y_%m_%d_%H%M%S')}"


def _print_banner(session_id: str, scope: list[str]):
    print()
    print("┌─────────────────────────────────────────────────────┐")
    print("│  FORGE  —  Local Coding Assistant  —  Level 4.9    │")
    print("│  Corpus Extraction Quality Report.                  │")
    print("│  corpus-extract-check/report/show.                  │")
    print("└─────────────────────────────────────────────────────┘")
    print(f"  Session : {session_id}")
    print(f"  Scope   : {', '.join(scope) if scope else '(none)'}")
    print(f"  Model   : qwen3:8b via Ollama")
    print(f"  Audit   : {AUDIT_LOG}")
    print()
    print("  Type your question or a command. 'help' for full command list.")
    print()


def _sanitize_response(response: str) -> str:
    """
    Strip raw tool call artifacts from the model response before displaying to Nic.
    The model occasionally outputs leftover function call syntax in its text response.
    These are never useful to the user — they are internal tool routing artifacts.
    """
    lines = response.splitlines()
    clean = []
    skip_next = False
    for line in lines:
        stripped = line.strip()
        # Skip lines that look like raw tool call syntax
        if any(stripped.startswith(pat) for pat in (
            "propose_command(", ".propose_command(",
            "analyze_command_output(", ".analyze_command_output(",
            "search_knowledge_base(", ".search_knowledge_base(",
            "read_file(", ".read_file(",
            "list_files(", ".list_files(",
            "search_text(", ".search_text(",
            "list_allowed_folders(", ".list_allowed_folders(",
        )):
            skip_next = False
            continue
        # Skip lines that are just raw JSON fragments from tool calls
        if stripped.startswith('{"') and stripped.endswith("}"):
            continue
        clean.append(line)

    result = "\n".join(clean)
    # Collapse more than two consecutive blank lines into two
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def _print_response(response: str):
    print()
    print(_sanitize_response(response))
    print()


# ─── COMMANDS ─────────────────────────────────────────────────────────────────

def cmd_approve(path_arg: str):
    """Add a path to approved_paths.json."""
    path = os.path.realpath(os.path.abspath(os.path.expanduser(path_arg)))

    if not os.path.exists(path):
        print(f"[forge] ERROR: Path does not exist: {path}")
        sys.exit(1)

    data = _load_json(APPROVED_PATHS_FILE)
    paths = data.get("paths", [])

    if path in paths:
        print(f"[forge] Already approved: {path}")
        return

    # Safety check — never approve sensitive locations
    sensitive = [".ssh", ".gnupg", ".config", ".cache", "identity-vault"]
    for s in sensitive:
        if s in path:
            print(f"[forge] ERROR: Cannot approve sensitive path containing '{s}': {path}")
            sys.exit(1)

    paths.append(path)
    data["paths"] = paths
    _save_json(APPROVED_PATHS_FILE, data)
    print(f"[forge] Approved: {path}")
    print(f"[forge] Approved paths: {paths}")


def cmd_audit():
    """Verify the integrity of the forge_audit.log hash chain."""
    print("[forge] Verifying audit log chain integrity...")
    valid, message = verify_audit_chain()
    if valid:
        print(f"[forge] ✓ {message}")
    else:
        print(f"[forge] ✗ CHAIN BROKEN: {message}")
        sys.exit(1)


def cmd_status():
    """Show current configuration and trust level."""
    from agents.forge.permissions import get_current_trust_level
    from agents.forge.memory import load_user_profile, load_project_profile

    approved = get_approved_paths()
    session  = get_session_paths()
    level    = get_current_trust_level()
    user     = load_user_profile()
    project  = load_project_profile()

    print()
    print("── Forge Status ──────────────────────────────────────")
    print(f"  Trust level   : {level}")
    print(f"  User          : {user.get('name', 'not set')}")
    print(f"  Project       : {project.get('current_project', 'not set')}")
    print(f"  Project root  : {project.get('project_root', 'not set')}")
    print(f"  Approved paths: {approved if approved else ['(none)']}")
    print(f"  Session scope : {session if session else ['(none — not in session)']}")
    print(f"  Audit log     : {AUDIT_LOG} ({_log_size()})")
    print("──────────────────────────────────────────────────────")
    print()


def _log_size() -> str:
    if not AUDIT_LOG.exists():
        return "not created"
    size = AUDIT_LOG.stat().st_size
    if size < 1024:
        return f"{size}B"
    return f"{size/1024:.1f}KB"


# ─── SESSION ──────────────────────────────────────────────────────────────────

def _first_run_setup():
    """
    If no approved paths are configured, walk Nic through adding the first one.
    """
    print()
    print("[forge] No approved paths configured.")
    print("[forge] Forge needs at least one project path to work with.")
    print("[forge] This path will be permanently stored in config/approved_paths.json")
    print()

    while True:
        path_input = input("  Enter the full path to your project directory: ").strip()
        if not path_input:
            print("  Please enter a path.")
            continue

        path = os.path.realpath(os.path.abspath(os.path.expanduser(path_input)))

        if not os.path.exists(path):
            print(f"  Path does not exist: {path}")
            print("  Please enter a path that exists on this machine.")
            continue

        if not os.path.isdir(path):
            print(f"  '{path}' is a file, not a directory. Enter a directory path.")
            continue

        confirm = input(f"  Approve this path? {path} [y/n]: ").strip().lower()
        if confirm == "y":
            cmd_approve(path)
            break
        else:
            print("  Skipped. Please enter a different path.")


def _setup_session_scope(approved: list[str]) -> list[str]:
    """
    Ask Nic which approved path(s) to work with this session.
    Returns the session scope list.
    """
    if len(approved) == 1:
        scope = approved
        print(f"[forge] Session scope set to: {scope[0]}")
    else:
        print("[forge] Multiple approved paths. Which would you like to work with this session?")
        for i, p in enumerate(approved, start=1):
            print(f"  {i}. {p}")
        print(f"  {len(approved)+1}. All of them")
        while True:
            choice = input("  Choice [1-{}]: ".format(len(approved)+1)).strip()
            if choice.isdigit():
                c = int(choice)
                if 1 <= c <= len(approved):
                    scope = [approved[c-1]]
                    break
                elif c == len(approved)+1:
                    scope = approved
                    break
            print("  Invalid choice. Try again.")

    # Write session_scope.json
    session_data = {
        "_comment": "Per-session path restriction. Written at session start.",
        "session_id": "",  # filled in after session ID is created
        "started_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "paths": scope
    }
    _save_json(SESSION_SCOPE_FILE, session_data)
    return scope


# Module-level active diagnostic session (set when user runs diag-session start)
_active_diag_session_id: str | None = None


def cmd_run(
    command_name: str,
    session_id: str,
    agent,
) -> None:
    """
    Deterministic execution mode — bypasses LLM for the run step.
    Calls runner.run_safe_command() directly in Python.
    Then passes the output to the agent for analysis.

    Usage inside a Forge session: run <command_name>
    Examples:
      forge> run nvidia-smi
      forge> run free -h
      forge> run ollama version
    """
    from agents.forge.runner import run_safe_command, COMMAND_NAMES

    command_name = command_name.strip()
    if not command_name:
        print()
        print("[forge] Usage: run <command_name>")
        print("[forge] Level 1.0 allowlist:")
        for name in COMMAND_NAMES:
            print(f"  run {name}")
        print()
        return

    print()
    print(f"[forge] Executing: {command_name}")

    result = run_safe_command(session_id=session_id, command_name=command_name)

    if "error" in result and not result.get("ok"):
        print(f"[forge] ERROR: {result['error']}")
        return

    print(f"[forge] Done. Exit: {result['exit_code']} | Lines: {result['line_count']} | SHA-256: {result['output_sha256']}")
    print(f"[forge] Saved: {result['diag_path']}")
    print()
    print("─── OUTPUT ─────────────────────────────────────────────")
    print(result["output"])
    print("────────────────────────────────────────────────────────")
    print()

    # Link to active diagnostic session if one is open
    if _active_diag_session_id:
        try:
            from agents.forge.diag_session import link_diagnostic
            link_diagnostic(
                session_id=_active_diag_session_id,
                diag_path=result["diag_path"],
                command=command_name,
                sha256=result["output_sha256"],
                line_count=result["line_count"],
            )
            print(f"[forge] Linked to session: {_active_diag_session_id}")
            print()
        except Exception:
            pass

    # Pass to agent for analysis
    question = (
        f"The command '{command_name}' was executed by the CLI (not by you). "
        f"Exit code: {result['exit_code']}. "
        f"SHA-256: {result['output_sha256']}. "
        f"Saved to: {result['diag_path']}.\n\n"
        f"Here is the verbatim output:\n\n"
        f"{result['output']}\n\n"
        f"Do NOT call run_safe_command or analyze_command_output — the execution is already complete and audited. "
        f"Analyze the output above and explain:\n"
        f"1. What it shows (key values and what they mean)\n"
        f"2. Whether anything looks abnormal or worth noting\n"
        f"3. Whether a next diagnostic step is needed"
    )

    print("[forge] Analyzing...")
    response = agent.ask(question)
    _print_response(response)


def cmd_exact_list(directory: str, files_only: bool = False, session_id: str = "") -> None:
    """
    Deterministic filesystem listing from Python. Bypasses the LLM entirely.
    Shows exact names, sizes, permission bits, and entry types.
    Refuses blocked/out-of-scope paths before reading.

    Usage: exact-list <directory>
           exact-list <directory> --files-only
    """
    import os, stat
    from agents.forge.permissions import is_path_blocked, is_path_allowed
    from agents.forge.memory import write_audit_entry

    directory = directory.strip()
    if not directory:
        print()
        print("  Usage: exact-list <directory>")
        print("  Example: exact-list /home/nic/aiweb/runtime_wrappers/symbolic_cognition_stack")
        print("  Flags:   --files-only")
        print()
        return

    path = Path(os.path.realpath(os.path.expanduser(directory)))

    # ── Security checks BEFORE any read ──────────────────────────────────────
    blocked, reason = is_path_blocked(str(path))
    if blocked:
        write_audit_entry(session_id, "EXACT_LIST_REFUSED", str(path), "-",
                          f"blocked: {reason[:120]}")
        print(f"[forge] EXACT_LIST REFUSED: path is blocked: {reason}")
        print(f"[forge] EXACT_LIST_REFUSED logged. No path was read.")
        return

    allowed, reason = is_path_allowed(str(path))
    if not allowed:
        write_audit_entry(session_id, "EXACT_LIST_REFUSED", str(path), "-",
                          f"out of scope: {reason[:120]}")
        print(f"[forge] EXACT_LIST REFUSED: path is outside approved/session scope: {reason}")
        print(f"[forge] EXACT_LIST_REFUSED logged. No path was read.")
        return

    if not path.exists():
        print(f"[forge] ERROR: Directory does not exist: {path}")
        return

    if not path.is_dir():
        print(f"[forge] ERROR: Not a directory: {path}")
        print(f"  Use 'exact-read' to read a file.")
        return

    # ── Scan entries ──────────────────────────────────────────────────────────
    try:
        entries = sorted(os.scandir(str(path)), key=lambda e: (not e.is_dir(), e.name))
    except PermissionError as e:
        print(f"[forge] ERROR: Permission denied reading directory: {e}")
        return

    dirs    = []
    files   = []
    symlinks = []
    others  = []

    for entry in entries:
        try:
            st = entry.stat(follow_symlinks=False)
            perm = oct(st.st_mode)[-3:]
            size = st.st_size
        except OSError:
            perm = "???"
            size = 0

        if entry.is_symlink():
            try:
                link_target = os.readlink(entry.path)
            except OSError:
                link_target = "?"
            symlinks.append((entry.name, size, perm, link_target))
        elif entry.is_dir(follow_symlinks=False):
            dirs.append((entry.name, size, perm))
        elif entry.is_file(follow_symlinks=False):
            files.append((entry.name, size, perm))
        else:
            others.append((entry.name, size, perm))

    total_entries = len(dirs) + len(files) + len(symlinks) + len(others)
    shown_entries = len(files) if files_only else total_entries

    write_audit_entry(
        session_id=session_id,
        tool="EXACT_LIST",
        path=str(path),
        lines=f"{total_entries} entries",
        reason=f"dirs={len(dirs)} files={len(files)} symlinks={len(symlinks)} files_only={files_only}"
    )

    print()
    print(f"── Exact Directory Listing ───────────────────────────")
    print(f"  Path      : {path}")
    print(f"  Entries   : {total_entries} total ({len(dirs)} dirs, {len(files)} files, {len(symlinks)} symlinks)")
    if files_only:
        print(f"  Mode      : --files-only")
    print()

    if not files_only and dirs:
        print(f"  Directories ({len(dirs)}):")
        for name, size, perm in dirs:
            print(f"    d{perm}  {name}/")
        print()

    if files:
        print(f"  Files ({len(files)}):")
        for name, size, perm in files:
            size_str = f"{size:>10,} B" if size < 1024 else f"{size/1024:>9.1f} KB"
            print(f"    -{perm}  {size_str}  {name}")
        print()

    if not files_only and symlinks:
        print(f"  Symlinks ({len(symlinks)}):")
        for name, size, perm, target in symlinks:
            print(f"    l{perm}  {name} → {target}")
        print()

    if not files_only and others:
        print(f"  Other ({len(others)}):")
        for name, size, perm in others:
            print(f"    ?{perm}  {name}")
        print()

    print(f"  [No files were modified. This is a read-only listing.]")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_exact_read(filepath: str, session_id: str = "") -> None:
    """
    Deterministic file read from Python. Bypasses the LLM entirely.
    Shows exact path, size, line count, and full content.
    Refuses blocked/out-of-scope paths before reading.

    Usage: exact-read <file>
    Example: exact-read /home/nic/aiweb/agents/agent.py
    """
    import os
    from agents.forge.permissions import is_path_blocked, is_path_allowed
    from agents.forge.memory import write_audit_entry

    MAX_READ_BYTES = 102_400  # 100 KB cap

    filepath = filepath.strip()
    if not filepath:
        print()
        print("  Usage: exact-read <file>")
        print("  Example: exact-read /home/nic/aiweb/README.md")
        print()
        return

    path = Path(os.path.realpath(os.path.expanduser(filepath)))

    # ── Security checks BEFORE any read ──────────────────────────────────────
    blocked, reason = is_path_blocked(str(path))
    if blocked:
        write_audit_entry(session_id, "EXACT_READ_REFUSED", str(path), "-",
                          f"blocked: {reason[:120]}")
        print(f"[forge] EXACT_READ REFUSED: path is blocked: {reason}")
        print(f"[forge] EXACT_READ_REFUSED logged. No file was read.")
        return

    allowed, reason = is_path_allowed(str(path))
    if not allowed:
        write_audit_entry(session_id, "EXACT_READ_REFUSED", str(path), "-",
                          f"out of scope: {reason[:120]}")
        print(f"[forge] EXACT_READ REFUSED: path is outside approved/session scope: {reason}")
        print(f"[forge] EXACT_READ_REFUSED logged. No file was read.")
        return

    if not path.exists():
        print(f"[forge] ERROR: File does not exist: {path}")
        return

    if path.is_dir():
        print(f"[forge] ERROR: That is a directory. Use 'exact-list' to list directories.")
        return

    if path.is_symlink():
        print(f"[forge] WARNING: '{path.name}' is a symlink → {os.readlink(str(path))}")

    # ── Read file ─────────────────────────────────────────────────────────────
    try:
        file_size = path.stat().st_size
    except OSError as e:
        print(f"[forge] ERROR: Cannot stat file: {e}")
        return

    truncated = False
    try:
        with open(str(path), "rb") as f:
            raw = f.read(MAX_READ_BYTES + 1)
        if len(raw) > MAX_READ_BYTES:
            raw = raw[:MAX_READ_BYTES]
            truncated = True
        # Binary detection
        if b"\x00" in raw:
            write_audit_entry(session_id, "EXACT_READ_REFUSED", str(path), "-",
                              "binary file detected")
            print(f"[forge] EXACT_READ REFUSED: file appears to be binary.")
            return
        content = raw.decode("utf-8", errors="replace")
    except OSError as e:
        print(f"[forge] ERROR: Cannot read file: {e}")
        return

    lines = content.splitlines()
    line_count = len(lines)

    write_audit_entry(
        session_id=session_id,
        tool="EXACT_READ",
        path=str(path),
        lines=f"{line_count} lines",
        reason=f"size={file_size} truncated={truncated}"
    )

    print()
    print(f"── Exact File Read ───────────────────────────────────")
    print(f"  Path       : {path}")
    print(f"  Size       : {file_size:,} bytes")
    print(f"  Lines      : {line_count}")
    if truncated:
        print(f"  ⚠ TRUNCATED: showing first {MAX_READ_BYTES:,} bytes of {file_size:,}")
    print()
    print(f"── Content ───────────────────────────────────────────")
    for i, line in enumerate(lines, start=1):
        print(f"  {i:4d}  {line}")
    if truncated:
        print(f"  ... [truncated at {MAX_READ_BYTES:,} bytes — full file has {file_size:,} bytes]")
    print(f"──────────────────────────────────────────────────────")
    print()


# ─── CORPUS ROOT AND ALLOWED FILES ───────────────────────────────────────────
# The corpus commands only read files within CORPUS_ROOT.
# Document content is never read — only metadata manifest files.
_CORPUS_ROOT    = Path.home() / "forge_corpus"
_CORPUS_CSV     = _CORPUS_ROOT / "corpus_metadata_manifest.csv"
_CORPUS_JSON    = _CORPUS_ROOT / "corpus_metadata_manifest.json"
_CORPUS_MD      = _CORPUS_ROOT / "CORPUS_METADATA_MANIFEST.md"
_CORPUS_READINESS = _CORPUS_ROOT / "CORPUS_INGESTION_READINESS_REPORT.md"

_CORPUS_POLICY_RULES = [
    "1. Exact filesystem truth (exact-list, exact-read) — always first",
    "2. Current codebase (~/aiweb agents, engines, runtime, config) — code questions",
    "3. Tests and manifests (engine_manifest.json, test_*.py) — validation",
    "4. Engineering standards (05_ENGINEERING_STANDARDS) — build conventions",
    "5. AI.Web architecture (02_AIWEB_ARCHITECTURE) — system design",
    "6. Gilligan (03_GILLIGAN_AGENT_CORE) — only for Gilligan-specific questions",
    "7. FBSC doctrine (04_FBSC_DOCTRINE) — only for symbolic/phase/drift questions",
    "8. Public/business docs (06_PUBLIC_LANGUAGE / 07_BUSINESS_LEGAL) — only for public/business writing when present",
    "9. Research/future speculation — only when explicitly requested",
]


def _corpus_load_json() -> list[dict]:
    """Load corpus metadata from JSON manifest. Returns empty list on failure."""
    if not _CORPUS_JSON.exists():
        return []
    try:
        import json as _json
        with open(_CORPUS_JSON, "r", encoding="utf-8") as f:
            data = _json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return list(data.values()) if data else []
        return []
    except Exception:
        return []


def _corpus_load_csv() -> list[dict]:
    """Load corpus metadata from CSV manifest. Returns empty list on failure."""
    if not _CORPUS_CSV.exists():
        return []
    try:
        import csv as _csv
        rows = []
        with open(_CORPUS_CSV, "r", encoding="utf-8") as f:
            reader = _csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
        return rows
    except Exception:
        return []


def _corpus_security_check(path: Path, session_id: str) -> bool:
    """
    Verify a path is inside CORPUS_ROOT. Refuses and audits if not.
    Returns True if safe, False if refused.
    """
    from agents.forge.memory import write_audit_entry
    try:
        path.relative_to(_CORPUS_ROOT)
        return True
    except ValueError:
        write_audit_entry(
            session_id=session_id,
            tool="CORPUS_REFUSED",
            path=str(path),
            lines="-",
            reason="path outside ~/forge_corpus"
        )
        print(f"[forge] CORPUS REFUSED: path is outside ~/forge_corpus")
        print(f"  Got: {path}")
        print(f"[forge] CORPUS_REFUSED logged. No path was read.")
        return False


def cmd_corpus_list(session_id: str) -> None:
    """
    List corpus contents from metadata manifest only.
    Groups by corpus_folder. Shows eligible and held counts.
    Never reads document content.
    Usage: corpus-list
    """
    from agents.forge.memory import write_audit_entry

    if not _corpus_security_check(_CORPUS_CSV, session_id):
        return

    rows = _corpus_load_json() or _corpus_load_csv()
    if not rows:
        print(f"[forge] ERROR: Could not load corpus manifest from {_CORPUS_JSON} or {_CORPUS_CSV}")
        return

    total  = len(rows)
    eligible = sum(1 for r in rows if str(r.get("index_eligible", "")).strip().lower() in ("true", "1", "yes"))
    held   = total - eligible

    # Group by corpus_folder
    from collections import defaultdict
    folders: dict[str, list] = defaultdict(list)
    held_items = []
    for r in rows:
        folder = r.get("corpus_folder", r.get("folder", "(unknown)"))
        folders[folder].append(r)
        if str(r.get("index_eligible", "")).strip().lower() not in ("true", "1", "yes"):
            held_items.append(r)

    write_audit_entry(
        session_id=session_id,
        tool="CORPUS_LISTED",
        path=str(_CORPUS_JSON),
        lines=f"{total} items",
        reason=f"total={total} eligible={eligible} held={held}"
    )

    print()
    print(f"── Corpus Manifest ───────────────────────────────────")
    print(f"  Root     : {_CORPUS_ROOT}")
    print(f"  Total    : {total}")
    print(f"  Eligible : {eligible}")
    print(f"  Held     : {held}")
    print()
    print(f"  Folders:")
    for folder in sorted(folders):
        items = folders[folder]
        n_elig = sum(1 for r in items if str(r.get("index_eligible", "")).strip().lower() in ("true", "1", "yes"))
        print(f"    {folder:<40} {len(items)} items  ({n_elig} eligible)")
    if held_items:
        print()
        print(f"  Held from indexing ({held}):")
        for r in held_items:
            fname = r.get("filename", r.get("id", "?"))
            reason = r.get("do_not_use_for", r.get("status", ""))
            print(f"    {r.get('id','?'):<15} {fname}  [{reason[:50]}]")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_status(session_id: str) -> None:
    """
    Show corpus readiness status from manifest and readiness report.
    Never reads document content.
    Usage: corpus-status
    """
    from agents.forge.memory import write_audit_entry

    if not _corpus_security_check(_CORPUS_CSV, session_id):
        return

    rows = _corpus_load_json() or _corpus_load_csv()
    total    = len(rows) if rows else 0
    eligible = sum(1 for r in rows if str(r.get("index_eligible", "")).strip().lower() in ("true", "1", "yes"))
    held     = total - eligible

    # Read readiness report if available
    readiness_summary = ""
    if _CORPUS_READINESS.exists() and _corpus_security_check(_CORPUS_READINESS, session_id):
        try:
            content = _CORPUS_READINESS.read_text(encoding="utf-8")
            # Extract key lines: verdict, errors, warnings
            for line in content.splitlines():
                l = line.strip()
                if any(kw in l.upper() for kw in ("READY", "VERDICT", "ERROR", "WARNING", "STATUS")):
                    if l and not l.startswith("#"):
                        readiness_summary += f"\n  {l}"
        except OSError:
            pass

    write_audit_entry(
        session_id=session_id,
        tool="CORPUS_STATUS",
        path=str(_CORPUS_JSON),
        lines=f"{total} items",
        reason=f"total={total} eligible={eligible} held={held}"
    )

    print()
    print(f"── Corpus Status ─────────────────────────────────────")
    print(f"  Root      : {_CORPUS_ROOT}")
    print(f"  Total     : {total} files")
    print(f"  Eligible  : {eligible}")
    print(f"  Held      : {held}")
    if readiness_summary:
        print(f"\n  Readiness report:{readiness_summary}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_show(corpus_id: str, session_id: str) -> None:
    """
    Show metadata for one corpus item by ID.
    Never reads document content.
    Usage: corpus-show <corpus_id>
    Example: corpus-show corpus_0011
    """
    from agents.forge.memory import write_audit_entry

    corpus_id = corpus_id.strip()
    if not corpus_id:
        print()
        print("  Usage: corpus-show <corpus_id>")
        print("  Example: corpus-show corpus_0011")
        print()
        return

    if not _corpus_security_check(_CORPUS_JSON, session_id):
        return

    rows = _corpus_load_json() or _corpus_load_csv()
    if not rows:
        print(f"[forge] ERROR: Could not load corpus manifest.")
        return

    # Find by id (exact or case-insensitive)
    item = None
    for r in rows:
        if r.get("id", "").strip().lower() == corpus_id.lower():
            item = r
            break

    if item is None:
        print(f"[forge] ERROR: Corpus item '{corpus_id}' not found.")
        all_ids = [r.get("id", "?") for r in rows]
        print(f"  Known IDs: {', '.join(all_ids[:10])}" + (" ..." if len(all_ids) > 10 else ""))
        return

    write_audit_entry(
        session_id=session_id,
        tool="CORPUS_ITEM_SHOWN",
        path=str(_CORPUS_JSON),
        lines="-",
        reason=f"id={corpus_id}"
    )

    # Display all fields
    print()
    print(f"── Corpus Item: {corpus_id} ──────────────────────────")
    for key, val in item.items():
        if val is not None and str(val).strip():
            print(f"  {key:<25}: {str(val)[:100]}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_check(session_id: str) -> None:
    """
    Validate the corpus metadata manifest.
    Checks CSV/JSON row count consistency, file existence, and eligibility logic.
    Never reads document content.
    Usage: corpus-check
    """
    from agents.forge.memory import write_audit_entry

    if not _corpus_security_check(_CORPUS_CSV, session_id):
        return

    errors   = []
    warnings = []

    # Load both formats
    json_rows = _corpus_load_json()
    csv_rows  = _corpus_load_csv()

    # Check 1: both manifests exist
    if not _CORPUS_JSON.exists():
        errors.append(f"JSON manifest not found: {_CORPUS_JSON}")
    if not _CORPUS_CSV.exists():
        errors.append(f"CSV manifest not found: {_CORPUS_CSV}")

    if not json_rows and not csv_rows:
        errors.append("Could not load any rows from CSV or JSON manifest")
        audit_tool = "CORPUS_CHECK_FAILED"
    else:
        rows = json_rows or csv_rows

        # Check 2: CSV/JSON row counts match (if both available)
        if json_rows and csv_rows and len(json_rows) != len(csv_rows):
            errors.append(f"Row count mismatch: JSON={len(json_rows)}, CSV={len(csv_rows)}")

        # Check 3: every absolute_path exists on disk
        missing_files = []
        for r in rows:
            abs_path = r.get("absolute_path", "").strip()
            if abs_path and not os.path.exists(abs_path):
                missing_files.append(abs_path)
        if missing_files:
            for p in missing_files[:5]:
                errors.append(f"File missing on disk: {p}")
            if len(missing_files) > 5:
                errors.append(f"... and {len(missing_files)-5} more missing files")

        # Check 4: archive items should not be index_eligible
        for r in rows:
            folder = r.get("corpus_folder", "").upper()
            eligible = str(r.get("index_eligible", "")).strip().lower() in ("true", "1", "yes")
            if "ARCHIVE" in folder and eligible:
                warnings.append(f"Archive item marked eligible: {r.get('id','?')} ({r.get('filename','')})")

        # Check 5: non-archive current items should be eligible
        for r in rows:
            folder = r.get("corpus_folder", "").upper()
            status = r.get("status", "").lower()
            eligible = str(r.get("index_eligible", "")).strip().lower() in ("true", "1", "yes")
            if "ARCHIVE" not in folder and status in ("current", "seed", "canonical") and not eligible:
                warnings.append(f"Current item not eligible: {r.get('id','?')} ({r.get('filename','')})")

        audit_tool = "CORPUS_CHECK_OK" if not errors else "CORPUS_CHECK_FAILED"

    write_audit_entry(
        session_id=session_id,
        tool=audit_tool,
        path=str(_CORPUS_JSON),
        lines=f"{len(json_rows or csv_rows or [])} rows",
        reason=f"errors={len(errors)} warnings={len(warnings)}"
    )

    print()
    print(f"── Corpus Check ──────────────────────────────────────")
    print(f"  JSON manifest : {'EXISTS' if _CORPUS_JSON.exists() else 'MISSING'}")
    print(f"  CSV manifest  : {'EXISTS' if _CORPUS_CSV.exists() else 'MISSING'}")
    if json_rows:
        print(f"  JSON rows     : {len(json_rows)}")
    if csv_rows:
        print(f"  CSV rows      : {len(csv_rows)}")
    print()
    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    ✗ {e}")
    else:
        print(f"  Errors   : 0  ✓")
    if warnings:
        print(f"  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠ {w}")
    else:
        print(f"  Warnings : 0  ✓")
    print()
    print(f"  Result : {audit_tool}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_extract_check(session_id: str) -> None:
    """
    Run extraction quality check on all index-eligible corpus files.
    Skips archive-held items. Records per-item summaries.
    Saves JSON and Markdown reports to ~/forge/corpus_reports/.
    Never ingests. Never writes to Chroma or vector DB.
    Usage: corpus-extract-check
    """
    from agents.forge.corpus_reporter import run_extraction_check, save_report, REPORTS_DIR
    from agents.forge.memory import write_audit_entry

    if not _corpus_security_check(_CORPUS_JSON, session_id):
        return

    rows = _corpus_load_json() or _corpus_load_csv()
    if not rows:
        print("[forge] ERROR: Could not load corpus manifest.")
        return

    eligible_count = sum(
        1 for r in rows
        if str(r.get("index_eligible", "")).strip().lower() in ("true", "1", "yes")
        and "09_ARCHIVE_REVIEW" not in str(r.get("corpus_folder", "")).upper()
    )
    held_count = len(rows) - eligible_count

    write_audit_entry(
        session_id=session_id,
        tool="CORPUS_EXTRACT_CHECK_STARTED",
        path=str(_CORPUS_JSON),
        lines=f"{eligible_count} eligible",
        reason=f"total={len(rows)} eligible={eligible_count} held={held_count}"
    )

    print()
    print(f"── Corpus Extraction Check ───────────────────────────")
    print(f"  Total corpus items : {len(rows)}")
    print(f"  Eligible to check  : {eligible_count}")
    print(f"  Held (skipping)    : {held_count}")
    print()

    results = {"ok": 0, "unsupported": 0, "failed": 0, "empty": 0, "hash_miss": 0}

    def on_progress(current: int, total: int, cid: str) -> None:
        print(f"  [{current:2d}/{total}] {cid}...", end="\r", flush=True)

    try:
        report = run_extraction_check(
            corpus_root=_CORPUS_ROOT,
            manifest_rows=rows,
            session_id=session_id,
            on_progress=on_progress,
        )
    except Exception as e:
        write_audit_entry(session_id, "CORPUS_EXTRACT_CHECK_FAILED", "-", "-",
                          f"exception: {e}")
        print(f"\n[forge] EXTRACTION CHECK FAILED: {e}")
        return

    print()  # clear progress line

    # Save reports
    try:
        json_path, md_path = save_report(report)
    except OSError as e:
        write_audit_entry(session_id, "CORPUS_EXTRACT_CHECK_FAILED", "-", "-",
                          f"report save failed: {e}")
        print(f"[forge] ERROR: Could not save report: {e}")
        return

    summary = report["summary"]

    write_audit_entry(
        session_id=session_id,
        tool="CORPUS_EXTRACT_CHECK_COMPLETED",
        path=str(json_path),
        lines=f"{eligible_count} items checked",
        reason=(
            f"ok={summary['successful']} "
            f"unsupported={summary['unsupported']} "
            f"failed={summary['failed']} "
            f"hash_miss={summary['hash_mismatches']} "
            f"empty={summary['empty_text']}"
        )
    )

    # Print per-item results
    for item in report["items"]:
        icon = "✓" if item["extraction_status"] == "ok" else "⚠" if item["extraction_status"] == "unsupported" else "✗"
        print(f"  {icon} {item['corpus_id']:<15} {item['filename']:<40} "
              f"{item['format']:<6} {item['extraction_status']:<20} "
              f"{item['chars_extracted']:>7,} chars")
        for w in item.get("warnings", [])[:2]:
            print(f"      ⚠ {w[:90]}")
        for e in item.get("errors", [])[:2]:
            print(f"      ✗ {e[:90]}")

    print()
    print(f"── Summary ───────────────────────────────────────────")
    print(f"  Eligible checked  : {summary['total_eligible']}")
    print(f"  Successful        : {summary['successful']}")
    print(f"  Unsupported fmt   : {summary['unsupported']}")
    print(f"  Failed            : {summary['failed']}")
    print(f"  File missing      : {summary['file_missing']}")
    print(f"  Hash mismatches   : {summary['hash_mismatches']}")
    print(f"  Empty text        : {summary['empty_text']}")
    print(f"  Warnings          : {summary['total_warnings']}")
    print()
    print(f"  JSON report : {json_path}")
    print(f"  MD report   : {md_path}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_extract_report(session_id: str) -> None:
    """
    Print the latest corpus extraction report summary.
    Usage: corpus-extract-report
    """
    from agents.forge.corpus_reporter import load_latest_report, list_reports, REPORTS_DIR
    from agents.forge.memory import write_audit_entry

    reports = list_reports()
    if not reports:
        print()
        print("[forge] No extraction reports found.")
        print(f"  Run 'corpus-extract-check' first.")
        print(f"  Reports directory: {REPORTS_DIR}")
        print()
        return

    report = load_latest_report()
    if not report:
        print("[forge] ERROR: Could not load latest report.")
        return

    summary = report["summary"]
    write_audit_entry(
        session_id=session_id,
        tool="CORPUS_EXTRACT_REPORT_SHOWN",
        path=str(reports[0]),
        lines="-",
        reason=f"report_id={report['report_id']}"
    )

    print()
    print(f"── Corpus Extraction Report ──────────────────────────")
    print(f"  Report ID  : {report['report_id']}")
    print(f"  Timestamp  : {report['timestamp']}")
    print(f"  Session    : {report['session_id']}")
    print()
    print(f"  ┌─ Summary ──────────────────────────────────────┐")
    print(f"  │ Eligible checked  : {summary['total_eligible']:<4}                    │")
    print(f"  │ Successful        : {summary['successful']:<4}                    │")
    print(f"  │ Unsupported fmt   : {summary['unsupported']:<4}                    │")
    print(f"  │ Failed            : {summary['failed']:<4}                    │")
    print(f"  │ File missing      : {summary['file_missing']:<4}                    │")
    print(f"  │ Hash mismatches   : {summary['hash_mismatches']:<4}                    │")
    print(f"  │ Empty text        : {summary['empty_text']:<4}                    │")
    print(f"  │ Warnings          : {summary['total_warnings']:<4}                    │")
    print(f"  └────────────────────────────────────────────────┘")
    print()
    print(f"  By folder:")
    for folder, counts in sorted(report.get("by_folder", {}).items()):
        icon = "✓" if counts["ok"] == counts["total"] else "⚠"
        print(f"    {icon} {folder:<40} {counts['ok']}/{counts['total']} OK")
    print()
    print(f"  All reports ({len(reports)}):")
    for rp in reports[:5]:
        print(f"    {rp.name}")
    if len(reports) > 5:
        print(f"    ... ({len(reports)-5} more)")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_extract_show(arg: str, session_id: str) -> None:
    """
    Show detailed extraction report.
    Usage: corpus-extract-show latest
           corpus-extract-show <report_filename>
    """
    from agents.forge.corpus_reporter import load_latest_report, list_reports, REPORTS_DIR
    from agents.forge.memory import write_audit_entry

    arg = arg.strip().lower()

    if arg in ("", "latest", "last"):
        report = load_latest_report()
        source = "latest"
    else:
        # Try to find by partial filename
        candidates = [p for p in list_reports() if arg in p.name.lower()]
        if not candidates:
            print(f"[forge] ERROR: No report matching '{arg}'.")
            reports = list_reports()
            if reports:
                print(f"  Available: {', '.join(p.name for p in reports[:5])}")
            return
        try:
            import json as _json
            with open(candidates[0], "r", encoding="utf-8") as f:
                report = _json.load(f)
            source = candidates[0].name
        except (OSError, Exception) as e:
            print(f"[forge] ERROR: Could not read report: {e}")
            return

    if not report:
        print("[forge] No reports found. Run 'corpus-extract-check' first.")
        return

    write_audit_entry(
        session_id=session_id,
        tool="CORPUS_EXTRACT_REPORT_SHOWN",
        path=source,
        lines=f"{len(report.get('items', []))} items",
        reason=f"report_id={report.get('report_id', '?')}"
    )

    summary = report["summary"]
    print()
    print(f"── Extraction Report Detail ──────────────────────────")
    print(f"  Report ID : {report['report_id']}")
    print(f"  Timestamp : {report['timestamp']}")
    print()
    print(f"  Per-item results:")
    print()
    for item in report.get("items", []):
        icon = "✓" if item["extraction_status"] == "ok" else "⚠" if item["extraction_status"] == "unsupported" else "✗"
        print(f"  {icon} {item['corpus_id']:<15} {item['filename']}")
        print(f"      Format: {item['format']}  |  "
              f"Status: {item['extraction_status']}  |  "
              f"Chars: {item['chars_extracted']:,}  |  "
              f"Lines: {item['lines_estimated']:,}  |  "
              f"Hash OK: {item['hash_ok']}")
        if item.get("preview_first_200"):
            preview = item["preview_first_200"][:120].replace("\n", " ")
            print(f"      Preview: {preview}…")
        for w in item.get("warnings", []):
            print(f"      ⚠ {w[:100]}")
        for e in item.get("errors", []):
            print(f"      ✗ {e[:100]}")
        print()

    if report.get("skipped"):
        print(f"  Held / skipped ({len(report['skipped'])}):")
        for s in report["skipped"]:
            print(f"    - {s['corpus_id']} {s['filename']} — {s['reason']}")
        print()
    print(f"──────────────────────────────────────────────────────")
    print()


CORPUS_REPORTS_DIR = FORGE_ROOT / "corpus_reports"


def _corpus_reports_dir() -> Path:
    d = CORPUS_REPORTS_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def cmd_corpus_extract_check(session_id: str) -> None:
    """
    Run extraction quality check across all index-eligible corpus files.
    Records per-file summary (no full text stored). Saves JSON + Markdown report.
    Never ingests. Never writes to Chroma or vector DB.
    Usage: corpus-extract-check
    """
    import json as _json
    import hashlib
    from agents.forge.document_adapters import extract_text
    from agents.forge.memory import write_audit_entry

    if not _corpus_security_check(_CORPUS_JSON, session_id):
        return

    rows = _corpus_load_json() or _corpus_load_csv()
    if not rows:
        print("[forge] ERROR: Could not load corpus manifest.")
        return

    write_audit_entry(session_id, "CORPUS_EXTRACT_CHECK_STARTED", str(_CORPUS_JSON),
                      f"{len(rows)} manifest rows", f"session={session_id}")

    ARCHIVE_MARKER    = "ARCHIVE"
    PREVIEW_CHARS     = 200
    results           = []
    skipped_archive   = 0
    errors_total      = 0

    print()
    print(f"── Corpus Extraction Quality Check ───────────────────")
    print(f"  Manifest : {_CORPUS_JSON}")
    print(f"  Total rows: {len(rows)}")
    print()

    for r in rows:
        cid     = r.get("id", "?")
        fname   = r.get("filename", "?")
        folder  = r.get("corpus_folder", "")
        eligible = str(r.get("index_eligible", "")).strip().lower() in ("true", "1", "yes")
        authority = r.get("authority", "")

        # Skip archive items
        if not eligible or ARCHIVE_MARKER in folder.upper():
            skipped_archive += 1
            continue

        abs_path_str = r.get("absolute_path", "").strip() or \
                       str(_CORPUS_ROOT / r.get("relative_path", ""))
        abs_path = Path(abs_path_str)
        suffix   = abs_path.suffix.lower()

        entry = {
            "corpus_id":           cid,
            "filename":            fname,
            "format":              suffix,
            "corpus_folder":       folder,
            "authority":           authority,
            "eligible":            True,
            "hash_ok":             False,
            "extraction_status":   "NOT_RUN",
            "chars_extracted":     0,
            "lines_estimated":     0,
            "preview_first_200":   "",
            "warnings":            [],
            "errors":              [],
        }

        # Path safety check
        try:
            abs_path.relative_to(_CORPUS_ROOT)
        except ValueError:
            entry["extraction_status"] = "PATH_VIOLATION"
            entry["errors"].append(f"Path escapes corpus root: {abs_path}")
            results.append(entry)
            errors_total += 1
            print(f"  {cid:<15} ✗ PATH_VIOLATION")
            continue

        # File existence check
        if not abs_path.exists():
            entry["extraction_status"] = "FILE_MISSING"
            entry["errors"].append(f"File not found: {abs_path}")
            results.append(entry)
            errors_total += 1
            print(f"  {cid:<15} ✗ MISSING  {fname}")
            continue

        # SHA-256 check
        expected_sha = str(r.get("sha256_16", "")).strip()
        if expected_sha:
            try:
                actual_sha = hashlib.sha256(abs_path.read_bytes()).hexdigest()[:16]
                if actual_sha != expected_sha:
                    entry["extraction_status"] = "HASH_MISMATCH"
                    entry["errors"].append(
                        f"SHA mismatch: expected={expected_sha} actual={actual_sha}"
                    )
                    results.append(entry)
                    errors_total += 1
                    print(f"  {cid:<15} ✗ HASH_MISMATCH  {fname}")
                    continue
                entry["hash_ok"] = True
            except OSError as e:
                entry["extraction_status"] = "READ_ERROR"
                entry["errors"].append(f"Cannot read file: {e}")
                results.append(entry)
                errors_total += 1
                print(f"  {cid:<15} ✗ READ_ERROR  {fname}")
                continue
        else:
            entry["hash_ok"] = None  # no hash in manifest to check

        # Extract text
        result = extract_text(abs_path, max_chars=10_000)  # generous for stats
        if result.unsupported:
            entry["extraction_status"] = "UNSUPPORTED"
            entry["errors"].append(result.error[:200])
            print(f"  {cid:<15} ⚠ UNSUPPORTED  {fname}  ({suffix})")
        elif result.error:
            entry["extraction_status"] = "FAILED"
            entry["errors"].append(result.error[:200])
            errors_total += 1
            print(f"  {cid:<15} ✗ FAILED  {fname}")
        else:
            text = result.text
            if not text.strip():
                entry["extraction_status"] = "EMPTY"
                entry["warnings"].append("Extracted text is empty")
                print(f"  {cid:<15} ⚠ EMPTY  {fname}")
            else:
                entry["extraction_status"] = "OK"
                entry["chars_extracted"]  = len(text)
                entry["lines_estimated"]  = text.count("\n") + 1
                entry["preview_first_200"] = text[:PREVIEW_CHARS].replace("\n", " ")
                print(f"  {cid:<15} ✓ OK  {fname}  ({len(text):,} chars)")

        results.append(entry)

    # ── Compute summary ────────────────────────────────────────────────────────
    ok_count          = sum(1 for r in results if r["extraction_status"] == "OK")
    unsupported_count = sum(1 for r in results if r["extraction_status"] == "UNSUPPORTED")
    failed_count      = sum(1 for r in results if r["extraction_status"] in ("FAILED", "READ_ERROR", "PATH_VIOLATION"))
    mismatch_count    = sum(1 for r in results if r["extraction_status"] == "HASH_MISMATCH")
    missing_count     = sum(1 for r in results if r["extraction_status"] == "FILE_MISSING")
    empty_count       = sum(1 for r in results if r["extraction_status"] == "EMPTY")

    # Group by folder
    from collections import defaultdict
    folder_stats: dict[str, dict] = defaultdict(lambda: {"ok": 0, "issues": 0})
    for r in results:
        f = r["corpus_folder"]
        if r["extraction_status"] == "OK":
            folder_stats[f]["ok"] += 1
        else:
            folder_stats[f]["issues"] += 1

    # ── Save JSON report ───────────────────────────────────────────────────────
    reports_dir = _corpus_reports_dir()
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_id = f"{ts}_extraction_check"

    report_data = {
        "report_id":        report_id,
        "timestamp":        datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id":       session_id,
        "manifest":         str(_CORPUS_JSON),
        "total_manifest":   len(rows),
        "skipped_archive":  skipped_archive,
        "total_checked":    len(results),
        "ok":               ok_count,
        "unsupported":      unsupported_count,
        "failed":           failed_count,
        "hash_mismatch":    mismatch_count,
        "missing":          missing_count,
        "empty":            empty_count,
        "folder_stats":     dict(folder_stats),
        "results":          results,
    }

    json_path = reports_dir / f"{report_id}.json"
    try:
        json_path.write_text(_json.dumps(report_data, indent=2), encoding="utf-8")
    except OSError as e:
        print(f"[forge] WARNING: Could not save JSON report: {e}")

    # ── Save Markdown report ───────────────────────────────────────────────────
    md_lines = [
        f"# Corpus Extraction Quality Report",
        f"",
        f"**Report ID**: `{report_id}`  ",
        f"**Timestamp**: {report_data['timestamp']}  ",
        f"**Session**: `{session_id}`",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total manifest rows | {len(rows)} |",
        f"| Skipped (archive/held) | {skipped_archive} |",
        f"| Checked (eligible) | {len(results)} |",
        f"| ✓ OK | {ok_count} |",
        f"| ⚠ Unsupported format | {unsupported_count} |",
        f"| ⚠ Empty extraction | {empty_count} |",
        f"| ✗ Hash mismatch | {mismatch_count} |",
        f"| ✗ File missing | {missing_count} |",
        f"| ✗ Extraction failed | {failed_count} |",
        f"",
        f"## By Folder",
        f"",
    ]
    for folder, stats in sorted(folder_stats.items()):
        status = "✓" if stats["issues"] == 0 else "⚠"
        md_lines.append(f"- {status} **{folder}**: {stats['ok']} ok, {stats['issues']} issues")

    md_lines += [
        f"",
        f"## Per-File Results",
        f"",
        f"| ID | Filename | Format | Status | Chars |",
        f"|----|----------|--------|--------|-------|",
    ]
    for r in results:
        status_icon = {"OK": "✓", "UNSUPPORTED": "⚠", "EMPTY": "⚠"}.get(r["extraction_status"], "✗")
        md_lines.append(
            f"| {r['corpus_id']} | {r['filename']} | {r['format']} "
            f"| {status_icon} {r['extraction_status']} | {r['chars_extracted']:,} |"
        )

    md_lines.append(f"\n---\n*This report contains extraction metadata only — no full document text.*")

    md_path = reports_dir / f"{report_id}.md"
    try:
        md_path.write_text("\n".join(md_lines), encoding="utf-8")
    except OSError as e:
        print(f"[forge] WARNING: Could not save Markdown report: {e}")

    # ── Print summary ──────────────────────────────────────────────────────────
    audit_tool = "CORPUS_EXTRACT_CHECK_COMPLETED" if errors_total == 0 else "CORPUS_EXTRACT_CHECK_FAILED"
    write_audit_entry(
        session_id=session_id,
        tool=audit_tool,
        path=str(json_path),
        lines=f"{len(results)} checked",
        reason=(
            f"ok={ok_count} unsupported={unsupported_count} "
            f"failed={failed_count} mismatch={mismatch_count} "
            f"missing={missing_count} empty={empty_count}"
        )
    )

    print()
    print(f"── Extraction Summary ────────────────────────────────")
    print(f"  Checked    : {len(results)}  (skipped archive: {skipped_archive})")
    print(f"  ✓ OK       : {ok_count}")
    print(f"  ⚠ Unsupported: {unsupported_count}")
    print(f"  ⚠ Empty    : {empty_count}")
    print(f"  ✗ Failed   : {failed_count}")
    print(f"  ✗ Missing  : {missing_count}")
    print(f"  ✗ Hash ✗   : {mismatch_count}")
    print()
    print(f"  JSON report : {json_path}")
    print(f"  MD report   : {md_path}")
    print(f"  Audit       : {audit_tool}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_extract_report(session_id: str) -> None:
    """
    Show the latest corpus extraction report summary.
    Usage: corpus-extract-report
    """
    import json as _json
    from agents.forge.memory import write_audit_entry

    reports_dir = _corpus_reports_dir()
    json_files  = sorted(reports_dir.glob("*_extraction_check.json"), reverse=True)

    if not json_files:
        print("[forge] No extraction reports found. Run 'corpus-extract-check' first.")
        return

    latest = json_files[0]
    try:
        data = _json.loads(latest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"[forge] ERROR: Cannot read report {latest.name}: {e}")
        return

    write_audit_entry(
        session_id=session_id,
        tool="CORPUS_EXTRACT_REPORT_SHOWN",
        path=str(latest),
        lines="-",
        reason=f"report_id={data.get('report_id','?')}"
    )

    print()
    print(f"── Latest Extraction Report ──────────────────────────")
    print(f"  Report ID  : {data.get('report_id', '?')}")
    print(f"  Timestamp  : {data.get('timestamp', '?')}")
    print(f"  Manifest   : {data.get('manifest', '?')}")
    print()
    print(f"  Total manifest rows : {data.get('total_manifest', '?')}")
    print(f"  Skipped (archive)   : {data.get('skipped_archive', '?')}")
    print(f"  Checked (eligible)  : {data.get('total_checked', '?')}")
    print()
    print(f"  ✓ OK              : {data.get('ok', '?')}")
    print(f"  ⚠ Unsupported     : {data.get('unsupported', '?')}")
    print(f"  ⚠ Empty           : {data.get('empty', '?')}")
    print(f"  ✗ Failed          : {data.get('failed', '?')}")
    print(f"  ✗ Missing         : {data.get('missing', '?')}")
    print(f"  ✗ Hash mismatch   : {data.get('hash_mismatch', '?')}")
    print()

    folder_stats = data.get("folder_stats", {})
    if folder_stats:
        print(f"  By folder:")
        for folder, stats in sorted(folder_stats.items()):
            icon = "✓" if stats.get("issues", 0) == 0 else "⚠"
            print(f"    {icon} {folder:<40} ok={stats.get('ok',0)} issues={stats.get('issues',0)}")

    other_reports = len(json_files) - 1
    if other_reports:
        print()
        print(f"  ({other_reports} older report(s) in {reports_dir})")

    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_extract_show(arg: str, session_id: str) -> None:
    """
    Show detailed extraction report. Accepts 'latest' or a report filename.
    Usage: corpus-extract-show latest
           corpus-extract-show 2026-05-09_234500_extraction_check
    """
    import json as _json
    from agents.forge.memory import write_audit_entry

    arg = arg.strip().lower()
    reports_dir = _corpus_reports_dir()

    if not arg or arg == "latest":
        json_files = sorted(reports_dir.glob("*_extraction_check.json"), reverse=True)
        if not json_files:
            print("[forge] No extraction reports found. Run 'corpus-extract-check' first.")
            return
        report_path = json_files[0]
    else:
        # Accept bare report_id or filename
        candidate = reports_dir / arg
        if not candidate.suffix:
            candidate = candidate.with_suffix(".json")
        if not candidate.exists():
            # Try as prefix search
            matches = sorted(reports_dir.glob(f"{arg}*.json"), reverse=True)
            if not matches:
                print(f"[forge] ERROR: Report not found: {arg}")
                print(f"  Use 'corpus-extract-show latest' or check ~/forge/corpus_reports/")
                return
            report_path = matches[0]
        else:
            report_path = candidate

    try:
        data = _json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"[forge] ERROR: Cannot read report: {e}")
        return

    write_audit_entry(
        session_id=session_id,
        tool="CORPUS_EXTRACT_REPORT_SHOWN",
        path=str(report_path),
        lines="-",
        reason=f"report_id={data.get('report_id','?')} detail=full"
    )

    results = data.get("results", [])

    print()
    print(f"── Extraction Report Detail ──────────────────────────")
    print(f"  Report    : {data.get('report_id', '?')}")
    print(f"  Timestamp : {data.get('timestamp', '?')}")
    print()

    for r in results:
        status = r.get("extraction_status", "?")
        icon = {"OK": "✓", "UNSUPPORTED": "⚠", "EMPTY": "⚠"}.get(status, "✗")
        print(f"  {icon} {r['corpus_id']:<15} {r['filename']:<45} {status}")
        if r.get("chars_extracted"):
            print(f"      chars={r['chars_extracted']:,}  lines≈{r['lines_estimated']}")
        if r.get("preview_first_200"):
            preview = r["preview_first_200"][:120].replace("\n", " ")
            print(f"      preview: {preview}...")
        for w in r.get("warnings", []):
            print(f"      ⚠ {w}")
        for e in r.get("errors", []):
            print(f"      ✗ {e[:100]}")

    print()
    print(f"  Report file: {report_path}")
    print(f"  (No full document text is stored in extraction reports.)")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_doc_capabilities(session_id: str) -> None:
    """
    Show the status of all document adapters in the active Python environment.
    Usage: doc-capabilities
    """
    from agents.forge.document_adapters import get_adapter_status
    from agents.forge.memory import write_audit_entry

    status = get_adapter_status()
    available = [e for e, s in status.items() if s["status"] == "available"]
    missing   = [e for e, s in status.items() if s["status"] == "missing"]
    future    = [e for e, s in status.items() if s["status"] == "future"]

    write_audit_entry(
        session_id=session_id,
        tool="DOC_CAPABILITIES_SHOWN",
        path="-",
        lines=f"{len(available)} available",
        reason=f"available={len(available)} missing={len(missing)} future={len(future)}"
    )

    print()
    print(f"── Document Adapter Capabilities ─────────────────────")
    print(f"  Python : {sys.executable}")
    print()
    print(f"  Available ({len(available)}):")
    for ext in sorted(available):
        s = status[ext]
        print(f"    {ext:<8}  read=YES  write=NO  lib={s['library']}")
    if missing:
        print()
        print(f"  Missing libraries ({len(missing)}):")
        for ext in sorted(missing):
            s = status[ext]
            print(f"    {ext:<8}  read=NO   write=NO  lib={s['library']}  → {s['notes']}")
    if future:
        print()
        print(f"  Future / unsupported ({len(future)}):")
        for ext in sorted(future):
            s = status[ext]
            print(f"    {ext:<8}  read=NO   write=NO  {s['notes']}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_doc_formats(session_id: str) -> None:
    """
    List supported, missing-library, and future document formats.
    Usage: doc-formats
    """
    from agents.forge.document_adapters import (
        PLAIN_TEXT_EXTENSIONS, LIBRARY_FORMATS, FUTURE_FORMATS, _check_library
    )
    from agents.forge.memory import write_audit_entry

    write_audit_entry(session_id, "DOC_FORMATS_SHOWN", "-", "-", "format listing")

    print()
    print(f"── Document Format Support ───────────────────────────")
    print(f"  Supported (plain text — no library needed):")
    for ext in sorted(PLAIN_TEXT_EXTENSIONS):
        print(f"    {ext}")
    print()
    print(f"  Library-backed formats:")
    for ext, info in sorted(LIBRARY_FORMATS.items()):
        available = _check_library(info["import_check"])
        status = "AVAILABLE" if available else "MISSING"
        print(f"    {ext:<8}  [{status}]  requires: {info['library']}")
        if not available:
            print(f"             install: {info['install_hint']}")
    print()
    print(f"  Future / not yet supported:")
    for ext, desc in sorted(FUTURE_FORMATS.items()):
        print(f"    {ext:<8}  {desc}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_doc_preview(corpus_id: str, session_id: str) -> None:
    """
    Preview a corpus document by corpus ID using the document adapter registry.
    User supplies only the ID — path is resolved from metadata.
    Archive-held items are refused. Hash must match manifest.
    Usage: doc-preview <corpus_id>
    """
    from agents.forge.document_adapters import corpus_preview as _corpus_preview_backend
    from agents.forge.memory import write_audit_entry

    PREVIEW_MAX_CHARS = 4_000
    ARCHIVE_MARKER = "ARCHIVE"

    corpus_id = corpus_id.strip()
    if not corpus_id:
        print()
        print("  Usage: doc-preview <corpus_id>")
        print("  Example: doc-preview corpus_0011")
        print()
        return

    if not _corpus_security_check(_CORPUS_JSON, session_id):
        return

    rows = _corpus_load_json() or _corpus_load_csv()
    if not rows:
        print("[forge] ERROR: Could not load corpus manifest.")
        return

    item = None
    for r in rows:
        if r.get("id", "").strip().lower() == corpus_id.lower():
            item = r
            break

    if item is None:
        write_audit_entry(session_id, "DOC_PREVIEW_REFUSED", "-", "-",
                          f"id_not_found={corpus_id}")
        print(f"[forge] DOC PREVIEW REFUSED: ID '{corpus_id}' not found in manifest.")
        all_ids = [r.get("id", "?") for r in rows]
        print(f"  Known IDs: {', '.join(all_ids[:12])}" + (" ..." if len(all_ids) > 12 else ""))
        return

    eligible = str(item.get("index_eligible", "")).strip().lower() in ("true", "1", "yes")
    folder   = str(item.get("corpus_folder", "")).upper()

    if not eligible or ARCHIVE_MARKER in folder:
        write_audit_entry(session_id, "DOC_PREVIEW_REFUSED", "-", "-",
                          f"id={corpus_id} | held/archive")
        print(f"[forge] DOC PREVIEW REFUSED: '{corpus_id}' is held from indexing (archive or ineligible).")
        print(f"  Folder    : {item.get('corpus_folder', '?')}")
        print(f"  Eligible  : {item.get('index_eligible', '?')}")
        return

    # Delegate to shared adapter backend
    text, error_msg, audit_tool = _corpus_preview_backend(
        item=item,
        corpus_root=_CORPUS_ROOT,
        session_id=session_id,
    )

    abs_path_str = item.get("absolute_path", str(_CORPUS_ROOT / item.get("relative_path", "")))
    suffix = Path(abs_path_str).suffix.lower()

    write_audit_entry(
        session_id=session_id,
        tool=audit_tool,
        path=abs_path_str,
        lines=f"{len(text)} chars" if text else "-",
        reason=f"id={corpus_id} | format={suffix}"
    )

    print()
    print(f"── Doc Preview: {corpus_id} ──────────────────────────")
    print(f"  Filename  : {item.get('filename', '?')}")
    print(f"  Folder    : {item.get('corpus_folder', '?')}")
    print(f"  Authority : {item.get('authority', '?')}")
    print(f"  Eligible  : {item.get('index_eligible', '?')}")
    print(f"  Format    : {suffix}")
    print(f"  Path      : {abs_path_str}")
    print()

    if error_msg:
        print(f"  ⚠ {error_msg}")
    else:
        truncated = len(text) > PREVIEW_MAX_CHARS
        preview = text[:PREVIEW_MAX_CHARS]
        print(f"── Content ({len(preview)} chars) ────────────────────────")
        for line in preview.splitlines()[:80]:
            print(f"  {line}")
        if truncated:
            print(f"\n  ... [truncated at {PREVIEW_MAX_CHARS} characters]")

    print()
    print(f"  ⚠ PREVIEW ONLY — not indexed, not ingested.")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_preview(corpus_id: str, session_id: str) -> None:
    """
    Controlled preview of a corpus document by corpus ID.
    Delegates to the document adapter registry backend (same as doc-preview).
    Usage: corpus-preview <corpus_id>
    """
    # corpus-preview now uses the same backend as doc-preview
    # Kept for backward compatibility; doc-preview is the canonical command
    cmd_doc_preview(corpus_id, session_id)


def cmd_corpus_policy(session_id: str) -> None:
    """
    Print corpus search priority rules.
    No file read required.
    Usage: corpus-policy
    """
    from agents.forge.memory import write_audit_entry

    write_audit_entry(
        session_id=session_id,
        tool="CORPUS_POLICY_SHOWN",
        path="-",
        lines="-",
        reason=f"{len(_CORPUS_POLICY_RULES)} rules"
    )

    print()
    print(f"── Corpus Search Priority Policy ─────────────────────")
    print(f"  When answering a question, Forge uses sources in this order:")
    print()
    for rule in _CORPUS_POLICY_RULES:
        print(f"  {rule}")
    print()
    print(f"  These rules prevent mixing architectural doctrine into code")
    print(f"  questions, or contaminating exact filesystem truth with theory.")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_field_report(arg: str, session_id: str) -> None:
    """
    Read-only lifecycle summary for a patch artifact or target file.
    Shows the full chain, current state, and all related artifacts.
    Usage: field-report <plan_or_rollback_or_target_file>
    """
    import os, hashlib
    from agents.forge.memory import write_audit_entry
    from agents.forge.ledger import (
        is_in_ledger_dirs, find_artifact_path, scan_all_artifacts,
        parse_artifact, find_chain, get_current_state,
        TYPE_ORDER, ALLOWED_LEDGER_DIRS,
    )
    from agents.forge.permissions import is_path_allowed, is_path_blocked

    arg = arg.strip()
    if not arg:
        print()
        print("  Usage: field-report <plan_or_rollback_or_target_file>")
        print("  Example: field-report 2026-05-09_PLAN_README_md.txt")
        print("  Example: field-report /home/nic/aiweb/README.md")
        print()
        return

    candidate = Path(os.path.expanduser(arg))

    # ── Determine what was passed: artifact or target file ───────────────────
    is_artifact = False
    is_target   = False

    if candidate.is_absolute():
        if is_in_ledger_dirs(candidate):
            is_artifact = True
        else:
            # Check if it's an approved target file
            blocked, reason = is_path_blocked(str(candidate))
            allowed, reason = is_path_allowed(str(candidate))
            if blocked or not allowed:
                write_audit_entry(
                    session_id=session_id,
                    tool="FIELD_REPORT_REFUSED",
                    path=str(candidate),
                    lines="-",
                    reason="path outside Forge artifact dirs and approved scope"
                )
                print(f"[forge] FIELD REPORT REFUSED")
                print(f"  Path must be a Forge artifact or an approved target file.")
                print(f"  Got: {candidate}")
                print(f"[forge] FIELD_REPORT_REFUSED logged. No path was read.")
                return
            is_target = True
    else:
        # Bare filename — search ledger dirs
        found = find_artifact_path(arg)
        if found:
            candidate = found
            is_artifact = True
        else:
            print(f"[forge] ERROR: Cannot find '{arg}' in any Forge patch directory.")
            return

    # ── Load artifact(s) and chain ───────────────────────────────────────────
    all_artifacts = scan_all_artifacts()

    if is_target:
        # Group by target and show all artifacts for this target
        target_str   = str(candidate)
        chain = [a for a in all_artifacts if a.get("target_file") == target_str]
        chain.sort(key=lambda a: (a["timestamp"] or "0000", a["filename"]))
        # Get SHA values from best available apply plan
        orig_sha, fut_sha = "", ""
        for a in chain:
            if a["type"] == "APPLY_PLAN" and a.get("future_sha"):
                orig_sha = a.get("original_sha", "")
                fut_sha  = a.get("future_sha", "")
                break
    else:
        artifact = parse_artifact(candidate)
        chain    = find_chain(artifact, all_artifacts)
        target_str = artifact.get("target_file", "")
        orig_sha, fut_sha = "", ""
        for a in chain:
            if a["type"] == "APPLY_PLAN" and a.get("future_sha"):
                orig_sha = orig_sha or a.get("original_sha", "")
                fut_sha  = fut_sha  or a.get("future_sha", "")

    # ── Current state ─────────────────────────────────────────────────────────
    state, current_sha = get_current_state(target_str, orig_sha, fut_sha)

    # ── Find best rollback ────────────────────────────────────────────────────
    rollbacks = [a for a in chain if a["type"] == "ROLLBACK_SNAPSHOT"]
    best_rollback = rollbacks[-1] if rollbacks else None

    # ── Audit ─────────────────────────────────────────────────────────────────
    write_audit_entry(
        session_id=session_id,
        tool="FIELD_REPORT_CREATED",
        path=target_str or str(candidate),
        lines=f"{len(chain)} artifacts",
        reason=f"target={target_str} | chain={len(chain)} | state={state}"
    )

    # ── Display ───────────────────────────────────────────────────────────────
    step_labels = {
        "PROPOSAL":          "① PROPOSE  ",
        "REFUSED_PROPOSAL":  "① REFUSED  ",
        "DIFF":              "② PREVIEW  ",
        "APPLY_PLAN":        "③ PREFLIGHT",
        "ROLLBACK_SNAPSHOT": "④ ROLLBACK ",
        "SAFETY_SNAPSHOT":   "⑤ SAFETY   ",
        "UNKNOWN":           "?  UNKNOWN  ",
    }

    print()
    print(f"── Field Report ──────────────────────────────────────")
    print(f"  Target file  : {target_str or '(unknown)'}")
    target_exists = target_str and os.path.exists(target_str)
    print(f"  Target exists: {'YES' if target_exists else 'NO'}")
    if current_sha:
        print(f"  Current SHA  : {current_sha}")
    print(f"  State        : {state}")
    print()

    if chain:
        chain_sorted = sorted(chain, key=lambda a: (
            a["timestamp"] or "0000",
            TYPE_ORDER.get(a["type"], 9),
        ))
        print(f"  Lifecycle chain ({len(chain)} artifacts):")
        for a in chain_sorted:
            label = step_labels.get(a["type"], "?  ")
            sha_note = ""
            if a["type"] == "APPLY_PLAN":
                o = a.get("original_sha", "")
                f = a.get("future_sha", "")
                if o and f:
                    sha_note = f"  [{o}→{f}]"
                    if current_sha == f:
                        sha_note += " ← APPLIED ✓"
                    elif current_sha == o:
                        sha_note += " ← original"
            elif a["type"] in ("ROLLBACK_SNAPSHOT", "SAFETY_SNAPSHOT"):
                r = a.get("rollback_sha", "")
                if r:
                    sha_note = f"  [sha:{r}]"
            print(f"    {label}  {a['timestamp']}  {a['filename']}{sha_note}")
    else:
        print(f"  (no chain found)")

    if best_rollback:
        print()
        print(f"  Rollback available:")
        print(f"    {best_rollback['path']}")
        rollback_exists = best_rollback["path"].exists()
        print(f"    Exists: {'YES' if rollback_exists else 'NO — MISSING'}")

    print()
    if state == "APPLIED":
        print(f"  Summary: Patch has been successfully applied. ✓")
    elif state == "ORIGINAL":
        print(f"  Summary: Target is in original state — patch not yet applied.")
    elif state == "DRIFT":
        print(f"  Summary: Target SHA matches neither original nor future — drift detected.")
    elif state == "MISSING":
        print(f"  Summary: Target file does not exist.")

    print(f"──────────────────────────────────────────────────────")
    print()


def _ledger_path_check(arg: str, session_id: str) -> Optional[Path]:
    """
    Validate that a ledger argument is inside one of the Forge-owned patch
    directories. Returns the resolved Path on success, None on refusal.
    """
    from agents.forge.ledger import is_in_ledger_dirs, find_artifact_path, ALLOWED_LEDGER_DIRS
    from agents.forge.memory import write_audit_entry

    candidate = Path(os.path.expanduser(arg)) if os.path.sep in arg or arg.startswith("~") else None

    # Full path provided — check boundary
    if candidate and candidate.is_absolute():
        if not is_in_ledger_dirs(candidate):
            write_audit_entry(
                session_id=session_id,
                tool="PATCH_LEDGER_REFUSED",
                path=str(candidate),
                lines="-",
                reason="path outside Forge-owned patch directories"
            )
            print(f"[forge] PATCH LEDGER REFUSED")
            print(f"  Path must be inside one of:")
            for d in ALLOWED_LEDGER_DIRS:
                print(f"    {d}")
            print(f"  Got: {candidate}")
            print(f"[forge] PATCH_LEDGER_REFUSED logged. No path was read.")
            return None
        if not candidate.exists():
            print(f"[forge] ERROR: File not found: {candidate}")
            return None
        return candidate

    # Bare filename — search all ledger directories
    found = find_artifact_path(arg)
    if not found:
        print(f"[forge] ERROR: Cannot find '{arg}' in any Forge patch directory.")
        return None
    return found


def cmd_patch_list(session_id: str) -> None:
    """
    List all patch artifacts grouped by target file.
    Usage: patch-list
    """
    from agents.forge.ledger import scan_all_artifacts, group_by_target, get_current_state, format_patch_list
    from agents.forge.memory import write_audit_entry

    artifacts = scan_all_artifacts()
    groups    = group_by_target(artifacts)

    # Get current SHA for each target that exists
    current_shas: dict[str, str] = {}
    for target in groups:
        if target != "(target unknown)" and os.path.exists(target):
            state, sha = get_current_state(target, "", "")
            if sha:
                current_shas[target] = sha

    total = sum(len(v) for v in groups.values())

    write_audit_entry(
        session_id=session_id,
        tool="PATCH_LEDGER_LISTED",
        path="-",
        lines=f"{total} artifacts",
        reason=f"targets={len(groups)} | total_artifacts={total}"
    )

    print()
    print(f"── Forge Patch Ledger ({total} artifacts, {len(groups)} target(s)) ───────────")
    print(format_patch_list(groups, current_shas))
    print()
    print(f"  Forge patch directories:")
    from agents.forge.ledger import ALLOWED_LEDGER_DIRS
    for d in ALLOWED_LEDGER_DIRS:
        count = sum(1 for a in artifacts if a["path"].is_relative_to(d)
                    and a["path"].parent == d)
        print(f"    {d}  ({count} files)")
    print("──────────────────────────────────────────────────────")
    print()


def cmd_patch_status(arg: str, session_id: str) -> None:
    """
    Show detailed status for a single patch artifact.
    Usage: patch-status <filename_or_path>
    """
    from agents.forge.ledger import (
        parse_artifact, scan_all_artifacts, find_chain,
        get_current_state, TYPE_LABELS, format_artifact_line
    )
    from agents.forge.memory import write_audit_entry

    path = _ledger_path_check(arg, session_id)
    if path is None:
        return

    artifact = parse_artifact(path)
    target   = artifact.get("target_file", "")

    # Current state
    orig_sha = artifact.get("original_sha", "")
    fut_sha  = artifact.get("future_sha", "")
    state, current_sha = get_current_state(target, orig_sha, fut_sha)

    # Related artifacts
    all_artifacts = scan_all_artifacts()
    chain = find_chain(artifact, all_artifacts)

    write_audit_entry(
        session_id=session_id,
        tool="PATCH_LEDGER_STATUS",
        path=str(path),
        lines="-",
        reason=f"type={artifact['type']} | target={target} | state={state}"
    )

    print()
    print(f"── Patch Status ──────────────────────────────────────")
    print(f"  File        : {path.name}")
    print(f"  Type        : {artifact['type']}")
    print(f"  Full path   : {path}")
    print(f"  Timestamp   : {artifact['timestamp'] or '(unknown)'}")
    print()
    print(f"  Target file : {target or '(could not parse)'}")
    if target:
        exists = os.path.exists(target)
        print(f"  Target exists: {'YES' if exists else 'NO'}")
        if current_sha:
            print(f"  Current SHA : {current_sha}")
    if orig_sha:
        print(f"  Original SHA: {orig_sha}")
    if fut_sha:
        print(f"  Future SHA  : {fut_sha}")
    if artifact.get("rollback_sha"):
        print(f"  Rollback SHA: {artifact['rollback_sha']}")
    print()
    print(f"  State       : {state}")

    if chain:
        print()
        print(f"  Related artifacts ({len(chain)}):")
        for a in chain:
            marker = "  ← THIS" if a["path"] == path else ""
            print(f"    {format_artifact_line(a, current_sha)}{marker}")

    print("──────────────────────────────────────────────────────")
    print()


def cmd_patch_chain(arg: str, session_id: str) -> None:
    """
    Show the full lifecycle chain for a patch artifact.
    Usage: patch-chain <filename_or_path>
    """
    from agents.forge.ledger import (
        parse_artifact, scan_all_artifacts, find_chain,
        get_current_state, TYPE_ORDER
    )
    from agents.forge.memory import write_audit_entry

    path = _ledger_path_check(arg, session_id)
    if path is None:
        return

    artifact = parse_artifact(path)
    target   = artifact.get("target_file", "")

    all_artifacts = scan_all_artifacts()
    chain = find_chain(artifact, all_artifacts)

    orig_sha = artifact.get("original_sha", "")
    fut_sha  = artifact.get("future_sha", "")
    # Try to find richer SHA data from a PLAN in the chain
    for a in chain:
        if a["type"] == "APPLY_PLAN":
            orig_sha = orig_sha or a.get("original_sha", "")
            fut_sha  = fut_sha  or a.get("future_sha", "")
            break

    state, current_sha = get_current_state(target, orig_sha, fut_sha)

    write_audit_entry(
        session_id=session_id,
        tool="PATCH_LEDGER_CHAIN",
        path=str(path),
        lines=f"{len(chain)} artifacts in chain",
        reason=f"type={artifact['type']} | target={target} | chain_len={len(chain)}"
    )

    print()
    print(f"── Patch Lifecycle Chain ─────────────────────────────")
    print(f"  Starting artifact : {path.name}")
    print(f"  Target file       : {target or '(unknown)'}")
    if current_sha:
        print(f"  Current SHA       : {current_sha}  (state: {state})")
    print()

    if not chain:
        print("  (no chain found — artifact may be standalone)")
    else:
        print("  Lifecycle (chronological):")
        print()
        # Sort chain by type order then timestamp for logical lifecycle display
        chain_sorted = sorted(chain, key=lambda a: (
            a["timestamp"] or "0000",
            TYPE_ORDER.get(a["type"], 9)
        ))
        step_labels = {
            "PROPOSAL":          "①  PROPOSE  ",
            "REFUSED_PROPOSAL":  "①  REFUSED  ",
            "DIFF":              "②  PREVIEW  ",
            "APPLY_PLAN":        "③  PREFLIGHT",
            "ROLLBACK_SNAPSHOT": "④  ROLLBACK ",
            "SAFETY_SNAPSHOT":   "⑤  SAFETY   ",
        }
        for a in chain_sorted:
            label  = step_labels.get(a["type"], "?  UNKNOWN  ")
            marker = "  ← this" if a["path"] == path else ""
            sha_note = ""
            if a["type"] == "APPLY_PLAN":
                o = a.get("original_sha", "")
                f = a.get("future_sha", "")
                if o and f:
                    sha_note = f"  [{o}→{f}]"
            elif a["type"] in ("ROLLBACK_SNAPSHOT", "SAFETY_SNAPSHOT"):
                r = a.get("rollback_sha", "")
                if r:
                    sha_note = f"  [sha:{r}]"
            print(f"    {label}  {a['timestamp']}  {a['filename']}{sha_note}{marker}")

        print()
        print(f"  Current state: {state}")
        if state == "APPLIED":
            print(f"  → Future SHA ({fut_sha}) matches current file ✓")
        elif state == "ORIGINAL":
            print(f"  → Original SHA ({orig_sha}) matches current file")
        elif state == "DRIFT":
            print(f"  → Current SHA ({current_sha}) matches neither original nor future")

    print("──────────────────────────────────────────────────────")
    print()


def _parse_rollback_snapshot(content: str) -> dict:
    """
    Parse a FORGE ROLLBACK SNAPSHOT document.
    Returns dict with: target_file, file_sha256, rollback_content.
    """
    result = {"target_file": "", "file_sha256": "", "rollback_content": ""}

    m = re.search(r"Target file\s+:\s+(.+)", content)
    if m:
        result["target_file"] = m.group(1).strip()

    m = re.search(r"File SHA-256\s+:\s+([0-9a-f]{16})", content)
    if m:
        result["file_sha256"] = m.group(1).strip()

    # Content between the first ═ separator block and the second
    # Format: ═══\n\n{content}\n\n═══
    m = re.search(
        r"═{10,}\n\n(.*?)\n\n═{10,}",
        content,
        re.DOTALL,
    )
    if m:
        result["rollback_content"] = m.group(1)

    return result


def cmd_rollback_restore(
    rollback_file_arg: str,
    session_id: str,
) -> bool:
    """
    Restore a file from a rollback snapshot.
    All checks before write. Requires typing RESTORE to confirm.
    Returns True if restore succeeded (for session write tracking).

    Usage: rollback-restore <rollback_file>
    Example: rollback-restore 2026-05-09_ROLLBACK_test_txt.txt
    """
    import os
    import hashlib
    from agents.forge.memory import write_audit_entry
    from agents.forge.permissions import is_path_allowed, is_path_blocked

    rollback_file_arg = rollback_file_arg.strip()
    if not rollback_file_arg:
        print()
        print("  Usage: rollback-restore <rollback_file>")
        print("  Example: rollback-restore 2026-05-09_ROLLBACK_test_txt.txt")
        print("  Tip: rollback files are in ~/forge/rollback_registry/")
        print()
        return False

    candidate = Path(os.path.expanduser(rollback_file_arg))
    rollback_dir = FORGE_ROOT / "rollback_registry"

    # ── Path boundary check BEFORE any read ──────────────────────────────────
    if candidate.is_absolute():
        try:
            candidate.relative_to(rollback_dir)
        except ValueError:
            write_audit_entry(
                session_id=session_id,
                tool="ROLLBACK_RESTORE_REFUSED",
                path=str(candidate),
                lines="-",
                reason="rollback file outside ~/forge/rollback_registry/"
            )
            print(f"[forge] ROLLBACK RESTORE REFUSED")
            print(f"  Rollback file must be inside ~/forge/rollback_registry/")
            print(f"  Got    : {candidate}")
            print(f"  Allowed: {rollback_dir}")
            print(f"[forge] ROLLBACK_RESTORE_REFUSED logged. No path was read.")
            return False

    # ── Existence check ───────────────────────────────────────────────────────
    if not candidate.is_absolute():
        candidate = rollback_dir / rollback_file_arg
    if not candidate.exists():
        print(f"[forge] ERROR: Rollback file not found: {candidate}")
        return False

    # ── Parse rollback snapshot ───────────────────────────────────────────────
    try:
        snapshot_content = candidate.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[forge] ERROR: Cannot read rollback snapshot: {e}")
        return False

    fields = _parse_rollback_snapshot(snapshot_content)
    target_file      = fields.get("target_file", "")
    rollback_sha     = fields.get("file_sha256", "")
    rollback_content = fields.get("rollback_content", "")

    if not target_file:
        print("[forge] ERROR: Cannot parse 'Target file' from rollback snapshot.")
        return False
    if not rollback_content:
        print("[forge] ERROR: Cannot parse rollback content from snapshot.")
        print("  The snapshot may be malformed. Check the file manually.")
        return False

    # ── Validate target file ──────────────────────────────────────────────────
    blocked, reason = is_path_blocked(target_file)
    if blocked:
        write_audit_entry(session_id, "ROLLBACK_RESTORE_REFUSED", target_file, "-",
                          f"target blocked: {reason[:120]}")
        print(f"[forge] ROLLBACK RESTORE REFUSED: target file is blocked: {reason}")
        return False

    allowed, reason = is_path_allowed(target_file)
    if not allowed:
        write_audit_entry(session_id, "ROLLBACK_RESTORE_REFUSED", target_file, "-",
                          f"target out of scope: {reason[:120]}")
        print(f"[forge] ROLLBACK RESTORE REFUSED: target is outside approved scope: {reason}")
        return False

    if not os.path.exists(target_file):
        print(f"[forge] ERROR: Target file does not exist: {target_file}")
        return False

    if os.path.islink(target_file):
        write_audit_entry(session_id, "ROLLBACK_RESTORE_REFUSED", target_file, "-", "target is a symlink")
        print(f"[forge] ROLLBACK RESTORE REFUSED: target is a symlink.")
        return False

    if os.path.isdir(target_file):
        print(f"[forge] ERROR: Target is a directory, not a file.")
        return False

    # ── Read current file ─────────────────────────────────────────────────────
    try:
        with open(target_file, "rb") as f:
            raw_bytes = f.read()
    except OSError as e:
        print(f"[forge] ERROR: Cannot read target file: {e}")
        return False

    if b"\x00" in raw_bytes:
        print(f"[forge] ROLLBACK RESTORE REFUSED: target appears to be a binary file.")
        return False

    try:
        current_content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        print(f"[forge] ROLLBACK RESTORE REFUSED: target file is not valid UTF-8.")
        return False

    current_sha = hashlib.sha256(current_content.encode("utf-8")).hexdigest()[:16]
    rollback_computed_sha = hashlib.sha256(rollback_content.encode("utf-8")).hexdigest()[:16]

    # ── Show state and get confirmation ──────────────────────────────────────
    print()
    print("── Rollback Restore ──────────────────────────────────")
    print(f"  Rollback file  : {candidate.name}")
    print(f"  Target file    : {target_file}")
    print(f"  Current SHA    : {current_sha}")
    print(f"  Rollback SHA   : {rollback_sha or rollback_computed_sha}")
    print()
    if current_sha == rollback_computed_sha:
        print("  ⚠ Target already matches rollback content. No change needed.")
        print()
    print("  THIS WILL OVERWRITE THE TARGET FILE.")
    print("  A pre-restore safety snapshot will be saved first.")
    print()
    print("  To abort, press Ctrl-C or type anything other than RESTORE.")
    print("  To proceed, type RESTORE (exact, case-sensitive):")
    print()

    try:
        confirmation = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        print("[forge] Rollback restore cancelled. No files were modified.")
        return False

    if confirmation != "RESTORE":
        print(f"[forge] Rollback restore cancelled (got {confirmation!r}, expected 'RESTORE').")
        return False

    # ── Save pre-restore safety snapshot ─────────────────────────────────────
    safety_dir = FORGE_ROOT / "rollback_registry" / "restore_safety_snapshots"
    safety_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = re.sub(r"[^\w]", "_", os.path.basename(target_file))[:30]
    safety_name = f"{ts}_SAFETY_{slug}.txt"
    safety_path = safety_dir / safety_name

    safety_doc = (
        f"FORGE PRE-RESTORE SAFETY SNAPSHOT\n"
        f"{'═' * 66}\n"
        f"Target file   : {target_file}\n"
        f"Snapshot time : {datetime.datetime.now().isoformat(timespec='seconds')}\n"
        f"Current SHA   : {current_sha}\n"
        f"Session ID    : {session_id}\n"
        f"{'═' * 66}\n\n"
        f"{current_content}\n\n"
        f"{'═' * 66}\n"
        f"This snapshot was saved automatically before a rollback restore.\n"
        f"{'═' * 66}\n"
    )
    try:
        safety_path.write_text(safety_doc, encoding="utf-8")
        print(f"\n[forge] Safety snapshot saved: {safety_path}")
    except OSError as e:
        print(f"[forge] WARNING: Could not save safety snapshot: {e}")
        print(f"[forge] Proceeding with restore anyway.")

    # ── Write rollback content ────────────────────────────────────────────────
    print(f"[forge] Writing rollback content to target file...")
    try:
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(rollback_content)
    except OSError as e:
        write_audit_entry(session_id, "ROLLBACK_RESTORE_FAILED", target_file, "-",
                          f"write error: {e}")
        print(f"[forge] ROLLBACK RESTORE FAILED: write error: {e}")
        print(f"[forge] Safety snapshot at: {safety_path}")
        return False

    # ── Post-write verification ───────────────────────────────────────────────
    try:
        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            post_content = f.read()
    except OSError as e:
        write_audit_entry(session_id, "ROLLBACK_RESTORE_FAILED", target_file, "-",
                          f"post-read error: {e}")
        print(f"[forge] ROLLBACK RESTORE FAILED: post-write read error: {e}")
        return False

    post_sha = hashlib.sha256(post_content.encode("utf-8")).hexdigest()[:16]

    if post_sha != rollback_computed_sha:
        write_audit_entry(session_id, "ROLLBACK_RESTORE_FAILED", target_file, "-",
                          f"post-write sha mismatch: got={post_sha} expected={rollback_computed_sha}")
        print(f"[forge] ROLLBACK RESTORE FAILED: SHA mismatch after write.")
        print(f"  Got     : {post_sha}")
        print(f"  Expected: {rollback_computed_sha}")
        print(f"  Safety snapshot: {safety_path}")
        print(f"  Manual recovery: copy from safety snapshot if needed.")
        return False

    # ── Audit ROLLBACK_RESTORED ───────────────────────────────────────────────
    audit_hash = write_audit_entry(
        session_id=session_id,
        tool="ROLLBACK_RESTORED",
        path=target_file,
        lines=f"{len(post_content.splitlines())} lines",
        reason=(
            f"rollback={candidate.name} | "
            f"post_sha={post_sha} | "
            f"safety_snapshot={safety_name}"
        )
    )

    print()
    print(f"[forge] ROLLBACK RESTORED")
    print(f"  Target file    : {target_file}")
    print(f"  Post SHA-256   : {post_sha}  ✓ matches rollback content")
    print(f"  Safety snapshot: {safety_path}")
    print(f"  Audit hash     : {audit_hash}  (ROLLBACK_RESTORED)")
    print()

    # ── Fresh readback from disk after rollback ──────────────────────────────
    import hashlib as _hl2
    from agents.forge.memory import write_audit_entry as _wae2
    try:
        with open(target_file, "r", encoding="utf-8", errors="replace") as _f2:
            _fresh2 = _f2.read()
        _fresh2_lines = _fresh2.splitlines()
        _fresh2_sha   = _hl2.sha256(_fresh2.encode("utf-8")).hexdigest()[:16]
        _count2       = len(_fresh2_lines)

        _preview2 = _fresh2_lines[:5]
        if _count2 > 10:
            _preview2.append(f"  ... [{_count2 - 8} lines omitted] ...")
            _preview2.extend(_fresh2_lines[-3:])
        elif _count2 > 5:
            _preview2.extend(_fresh2_lines[5:])

        _wae2(
            session_id=session_id,
            tool="ROLLBACK_POST_RESTORE_READBACK",
            path=target_file,
            lines=f"{_count2} lines",
            reason=f"restored_sha={_fresh2_sha}"
        )

        print(f"── Fresh readback from disk after rollback ───────────")
        print(f"  Target   : {target_file}")
        print(f"  SHA-256  : {_fresh2_sha}")
        print(f"  Lines    : {_count2}")
        print()
        for _line2 in _preview2[:25]:
            print(f"  {_line2}")
        print(f"──────────────────────────────────────────────────────")
        print()

    except OSError as _e2:
        _wae2(
            session_id=session_id,
            tool="ROLLBACK_POST_RESTORE_READBACK_FAILED",
            path=target_file,
            lines="-",
            reason=f"read error: {_e2}"
        )
        print(f"  ⚠ Fresh readback failed: {_e2}")
        print()

    return True


def cmd_patch_verify(
    apply_plan_arg: str,
    session_id: str,
) -> None:
    """
    Read-only post-apply integrity verification.
    Compares the current target file SHA-256 against the apply plan's
    original_sha256 and future_sha256 to determine apply state.
    Never modifies any file. Never restores anything.

    Usage: patch-verify <apply_plan_file>
    Example: patch-verify 2026-05-09_PLAN_test_txt.txt
    """
    from agents.forge.applier import _parse_apply_plan
    from agents.forge.memory import write_audit_entry
    import hashlib

    apply_plan_arg = apply_plan_arg.strip()
    if not apply_plan_arg:
        print()
        print("  Usage: patch-verify <apply_plan_file>")
        print("  Example: patch-verify 2026-05-09_PLAN_test_txt.txt")
        print()
        return

    import os
    candidate = Path(os.path.expanduser(apply_plan_arg))
    apply_plans_dir = FORGE_ROOT / "apply_plans"

    # ── Path boundary check before any read ──────────────────────────────────
    if candidate.is_absolute():
        try:
            candidate.relative_to(apply_plans_dir)
        except ValueError:
            write_audit_entry(
                session_id=session_id,
                tool="PATCH_VERIFY_REFUSED",
                path=str(candidate),
                lines="-",
                reason="apply plan outside ~/forge/apply_plans/"
            )
            print(f"[forge] PATCH VERIFY REFUSED")
            print(f"  Apply plan must be inside ~/forge/apply_plans/")
            print(f"  Got    : {candidate}")
            print(f"  Allowed: {apply_plans_dir}")
            print(f"[forge] PATCH_VERIFY_REFUSED logged. No path was read.")
            return

    # ── Existence check ───────────────────────────────────────────────────────
    if not candidate.is_absolute():
        candidate = apply_plans_dir / apply_plan_arg
    if not candidate.exists():
        print(f"[forge] ERROR: Apply plan not found: {candidate}")
        return

    # ── Parse apply plan ──────────────────────────────────────────────────────
    try:
        plan_content = candidate.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[forge] ERROR: Cannot read apply plan: {e}")
        return

    fields        = _parse_apply_plan(plan_content)
    target_file   = fields.get("target_file", "")
    original_sha  = fields.get("original_sha256", "")
    future_sha    = fields.get("future_sha256", "")
    rollback_path = fields.get("rollback_path", "")

    if not target_file:
        print("[forge] ERROR: Cannot parse 'Target file' from apply plan.")
        return

    print()
    print(f"[forge] Verifying apply state for plan: {candidate.name}")
    print(f"  Target file   : {target_file}")
    print(f"  Original SHA  : {original_sha}  ← SHA before applying")
    print(f"  Future SHA    : {future_sha}   ← SHA after applying")
    print()

    # ── Check rollback snapshot ───────────────────────────────────────────────
    rollback_exists = rollback_path and os.path.exists(rollback_path)
    if not rollback_exists:
        write_audit_entry(
            session_id=session_id,
            tool="PATCH_VERIFY_ROLLBACK_MISSING",
            path=target_file,
            lines="-",
            reason=f"plan={candidate.name} | rollback={rollback_path}"
        )
        print(f"  ⚠ ROLLBACK SNAPSHOT MISSING")
        print(f"    Expected : {rollback_path}")
        print(f"    Status   : NOT FOUND — recovery may not be possible")
        print()
    else:
        print(f"  Rollback     : {rollback_path}  ✓ exists")

    # ── Read current target file ──────────────────────────────────────────────
    if not os.path.exists(target_file):
        print(f"[forge] ERROR: Target file does not exist: {target_file}")
        return

    try:
        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            current_content = f.read()
    except OSError as e:
        print(f"[forge] ERROR: Cannot read target file: {e}")
        return

    current_sha = hashlib.sha256(current_content.encode("utf-8")).hexdigest()[:16]
    print(f"  Current SHA   : {current_sha}  ← actual current file")
    print()

    # ── Determine and report state ────────────────────────────────────────────
    if current_sha == future_sha:
        audit_tool = "PATCH_VERIFY_OK"
        state_msg  = "APPLIED STATE VERIFIED"
        detail_msg = "Current file matches the planned future state."
    elif current_sha == original_sha:
        audit_tool = "PATCH_VERIFY_NOT_APPLIED"
        state_msg  = "TARGET IS IN ORIGINAL STATE"
        detail_msg = "Patch does not appear to have been applied yet."
    else:
        audit_tool = "PATCH_VERIFY_DRIFT"
        state_msg  = "TARGET DRIFT DETECTED"
        detail_msg = (
            "Current SHA matches neither original nor future. "
            "The file has been modified by something other than this patch."
        )

    write_audit_entry(
        session_id=session_id,
        tool=audit_tool,
        path=target_file,
        lines="-",
        reason=(
            f"plan={candidate.name} | "
            f"current_sha={current_sha} | "
            f"original_sha={original_sha} | "
            f"future_sha={future_sha} | "
            f"rollback_exists={rollback_exists}"
        )
    )

    print(f"── Verification Result ───────────────────────────────")
    print(f"  State  : {state_msg}")
    print(f"  Detail : {detail_msg}")
    print(f"  Audit  : {audit_tool} logged")
    print(f"──────────────────────────────────────────────────────")
    print()
    print(f"[forge] No project files were modified by this verification.")
    print()


def cmd_patch_apply(
    apply_plan_arg: str,
    session_id: str,
) -> None:
    """
    Approval-gated patch application.
    Reads an apply plan, runs all safety checks, then asks Nic to type
    'APPLY' before writing anything. Never applies without explicit approval.

    Usage: patch-apply <apply_plan_file>
    Example: patch-apply 2026-05-09_PLAN_test_txt.txt
    """
    from agents.forge.applier import apply_patch, _parse_apply_plan
    from agents.forge.memory import write_audit_entry

    apply_plan_arg = apply_plan_arg.strip()
    if not apply_plan_arg:
        print()
        print("  Usage: patch-apply <apply_plan_file>")
        print("  Example: patch-apply 2026-05-09_PLAN_test_txt.txt")
        print("  Tip: run 'patch-preflight <proposal>' first to generate an apply plan.")
        print()
        return

    # ── Path boundary check BEFORE existence check ────────────────────────────
    import os
    candidate = Path(os.path.expanduser(apply_plan_arg))
    apply_plans_dir = FORGE_ROOT / "apply_plans"

    if candidate.is_absolute():
        try:
            candidate.relative_to(apply_plans_dir)
        except ValueError:
            write_audit_entry(
                session_id=session_id,
                tool="PATCH_APPLY_REFUSED",
                path=str(candidate),
                lines="-",
                reason="apply plan outside ~/forge/apply_plans/"
            )
            print(f"[forge] PATCH APPLY REFUSED")
            print(f"  Apply plan must be inside ~/forge/apply_plans/")
            print(f"  Got    : {candidate}")
            print(f"  Allowed: {apply_plans_dir}")
            print(f"[forge] PATCH_APPLY_REFUSED logged. No files were read.")
            return

    # ── Existence check ───────────────────────────────────────────────────────
    if not candidate.is_absolute():
        candidate = apply_plans_dir / apply_plan_arg
    if not candidate.exists():
        print(f"[forge] ERROR: Apply plan not found: {candidate}")
        print(f"  Try: patch-apply (no argument) to list recent plans.")
        return

    # ── Parse plan header to show target before asking for confirmation ───────
    try:
        plan_content = candidate.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[forge] ERROR: Cannot read apply plan: {e}")
        return

    fields = _parse_apply_plan(plan_content)
    target_file    = fields.get("target_file", "(could not parse)")
    original_sha   = fields.get("original_sha256", "?")
    future_sha     = fields.get("future_sha256", "?")
    rollback_path  = fields.get("rollback_path", "(could not parse)")

    # ── Display all checks that will run ─────────────────────────────────────
    print()
    print("── Patch Apply ───────────────────────────────────────")
    print(f"  Apply plan  : {candidate.name}")
    print(f"  Target file : {target_file}")
    print(f"  Original SHA: {original_sha}  ← must match current file")
    print(f"  Future SHA  : {future_sha}     ← must match after write")
    print(f"  Rollback    : {rollback_path}")
    print()
    print("  Checks that will run before writing:")
    print("    1. Target file exists, is a regular text file, not a symlink")
    print("    2. Target is within approved/session scope, not blocked")
    print("    3. Current SHA-256 matches apply plan original_sha256")
    print("       (confirms file unchanged since preflight — implies snippet still present)")
    print("    4. Rollback snapshot exists at the path above")
    print("    5. COMPUTED FUTURE CONTENT parsed from apply plan")
    print()
    print("  After a successful write:")
    print("    6. File will be re-read and SHA-256 verified against future_sha256")
    print("    7. PATCH_APPLIED will be written to audit log")
    print()
    print("──────────────────────────────────────────────────────")
    print()
    print("  THIS WILL MODIFY A PROJECT FILE.")
    print("  The rollback snapshot must exist before you proceed.")
    print()

    # ── Last chance confirmation ──────────────────────────────────────────────
    print("  To abort, press Ctrl-C or type anything other than APPLY.")
    print("  To proceed, type APPLY (exact, case-sensitive):")
    print()
    try:
        confirmation = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        print("[forge] Apply cancelled. No files were modified.")
        return

    if confirmation != "APPLY":
        print(f"[forge] Apply cancelled (got {confirmation!r}, expected 'APPLY'). No files were modified.")
        return

    # ── Execute apply ─────────────────────────────────────────────────────────
    print()
    print("[forge] Running all checks and applying...")

    result = apply_patch(session_id=session_id, apply_plan_path_arg=str(candidate))

    print()
    if result["ok"]:
        import hashlib as _hl
        from agents.forge.memory import write_audit_entry

        print(f"[forge] PATCH APPLIED")
        print(f"  Target file  : {result['target_file']}")
        print(f"  Post SHA-256 : {result['post_sha256']}  ✓ matches plan future_sha256")
        print(f"  Rollback at  : {result['backup_path']}")
        print(f"  Audit hash   : {result['audit_hash']}  (PATCH_APPLIED)")
        print()

        # ── Fresh readback from disk (deterministic Python read, not model memory) ──
        try:
            with open(result["target_file"], "r", encoding="utf-8", errors="replace") as _f:
                _fresh = _f.read()
            _fresh_lines = _fresh.splitlines()
            _fresh_sha   = _hl.sha256(_fresh.encode("utf-8")).hexdigest()[:16]
            _line_count  = len(_fresh_lines)

            # Preview: first 5 lines + last 3 lines if file is long
            _preview = _fresh_lines[:5]
            if _line_count > 10:
                _preview.append(f"  ... [{_line_count - 8} lines omitted] ...")
                _preview.extend(_fresh_lines[-3:])
            elif _line_count > 5:
                _preview.extend(_fresh_lines[5:])

            write_audit_entry(
                session_id=session_id,
                tool="PATCH_POST_WRITE_READBACK",
                path=result["target_file"],
                lines=f"{_line_count} lines",
                reason=f"post_sha256={_fresh_sha}"
            )

            print(f"── Fresh readback from disk ──────────────────────────")
            print(f"  Target   : {result['target_file']}")
            print(f"  SHA-256  : {_fresh_sha}")
            print(f"  Lines    : {_line_count}")
            print()
            for _line in _preview[:25]:
                print(f"  {_line}")
            print(f"──────────────────────────────────────────────────────")

        except OSError as _e:
            write_audit_entry(
                session_id=session_id,
                tool="PATCH_POST_WRITE_READBACK_FAILED",
                path=result["target_file"],
                lines="-",
                reason=f"read error: {_e}"
            )
            print(f"  ⚠ Fresh readback failed: {_e}")

        print()
        print(f"  If anything is wrong, restore from rollback:")
        print(f"    Open: {result['backup_path']}")
        print(f"    Copy content between the separator lines back into: {result['target_file']}")
        print()
        return True
    else:
        print(f"[forge] PATCH FAILED")
        print(f"  Reason: {result.get('error', 'Unknown error')}")
        if result.get("rollback_instructions"):
            print()
            print(f"  {result['rollback_instructions']}")
        print()
        print(f"  No automatic repair will be attempted.")
        print(f"  The audit log records what happened.")
    print()
    return False


def cmd_patch_preflight(
    proposal_file_arg: str,
    session_id: str,
) -> None:
    """
    Run the full apply preflight for a patch proposal.
    Saves rollback snapshot and apply plan. Never modifies project files.

    Usage: patch-preflight <proposal_file>
    Example: patch-preflight 2026-05-09_PATCH_test_txt.txt
    """
    from agents.forge.preflight import run_preflight

    proposal_file_arg = proposal_file_arg.strip()
    if not proposal_file_arg:
        print()
        print("  Usage: patch-preflight <proposal_file>")
        print("  Example: patch-preflight 2026-05-09_PATCH_test_txt.txt")
        print("  Tip: run 'patch-review <file>' first to see the diff.")
        print()
        return

    # ── Path boundary check BEFORE anything else ──────────────────────────────
    # If an absolute path is given, verify it is inside proposed_patches/
    # before reading or accessing anything.
    import os as _os
    candidate_path = Path(_os.path.expanduser(proposal_file_arg))
    patches_dir = FORGE_ROOT / "proposed_patches"

    if candidate_path.is_absolute():
        try:
            candidate_path.relative_to(patches_dir)
        except ValueError:
            from agents.forge.memory import write_audit_entry
            write_audit_entry(
                session_id=session_id,
                tool="PATCH_APPLY_PLAN_REFUSED",
                path=str(candidate_path),
                lines="-",
                reason="proposal path outside ~/forge/proposed_patches/"
            )
            print(f"[forge] PREFLIGHT REFUSED")
            print(f"  Reason : Proposal must be inside ~/forge/proposed_patches/")
            print(f"  Got    : {candidate_path}")
            print(f"  Allowed: {patches_dir}")
            print(f"[forge] PATCH_APPLY_PLAN_REFUSED logged. No path was read.")
            return

    print()
    print(f"[forge] Running apply preflight for: {proposal_file_arg}")
    print(f"[forge] Steps:")
    print(f"  1. Validate proposal and target file")
    print(f"  2. Confirm original snippet exists")
    print(f"  3. Save rollback snapshot → ~/forge/rollback_registry/")
    print(f"  4. Save apply plan       → ~/forge/apply_plans/")
    print(f"  5. Audit (PATCH_APPLY_PLAN_CREATED on success, PATCH_APPLY_PLAN_REFUSED on failure)")
    print(f"  [No project files will be modified]")
    print()

    result = run_preflight(session_id=session_id, proposal_file_arg=proposal_file_arg)

    if not result["ok"]:
        print(f"[forge] PREFLIGHT FAILED")
        print(f"  Reason : {result.get('error', 'Unknown error')}")
        print()
        return

    print(f"[forge] PREFLIGHT COMPLETE")
    print(f"  Target file      : {result['target_file']}")
    print(f"  Snippet found    : line {result['snippet_line']}")
    print(f"  Occurrences      : {result['occurrence_count']}")
    print(f"  Original SHA-256 : {result['original_sha256']}")
    print(f"  Future SHA-256   : {result['future_sha256']}")
    print()
    print(f"  Rollback saved   : {result['rollback_path']}")
    print(f"  Apply plan saved : {result['apply_plan_path']}")
    print(f"  Audit hash       : {result['audit_hash']}  (PATCH_APPLY_PLAN_CREATED)")
    print()

    if result["occurrence_count"] > 1:
        print(f"  ⚠ WARNING: Snippet appears {result['occurrence_count']} times.")
        print(f"    Only the first occurrence will be replaced. Review the apply plan.")
        print()

    print(f"[forge] No project files were modified.")
    print(f"[forge] When ready to apply, follow the instructions in the apply plan.")
    print(f"  Open: {result['apply_plan_path']}")
    print()


def _parse_proposal_file(content: str) -> dict:
    """
    Parse a FORGE PATCH PROPOSAL document and extract key fields.
    Returns a dict with: target_file, original_snippet, proposed_snippet.
    Returns empty strings for fields that cannot be parsed.
    """
    result = {"target_file": "", "original_snippet": "", "proposed_snippet": ""}

    # Target file
    m = re.search(r"Target file\s+:\s+(.+)", content)
    if m:
        result["target_file"] = m.group(1).strip()

    # Original snippet — between ORIGINAL header + separator and PROPOSED CHANGE
    m = re.search(
        r"ORIGINAL \(current content[^\n]*\)\n─+\n(.*?)\n\n\nPROPOSED CHANGE",
        content,
        re.DOTALL,
    )
    if m:
        result["original_snippet"] = m.group(1).strip("\n")

    # Proposed snippet — between PROPOSED CHANGE header + separator and REASONING
    m = re.search(
        r"PROPOSED CHANGE\n─+\n(.*?)\n\n\nREASONING",
        content,
        re.DOTALL,
    )
    if m:
        result["proposed_snippet"] = m.group(1).strip("\n")

    return result


def cmd_patch_review(
    proposal_file_arg: str,
    session_id: str,
) -> None:
    """
    Show a unified diff preview for a patch proposal file.
    Saves the diff to ~/forge/proposed_patches/diffs/.
    Never modifies any project file.

    Usage: patch-review <proposal_file>
    Example: patch-review ~/forge/proposed_patches/2026-05-09_PATCH_test_txt.txt
    """
    import difflib
    import os
    from agents.forge.permissions import is_path_allowed, is_path_blocked
    from agents.forge.memory import write_audit_entry

    # ── Locate proposal file ──────────────────────────────────────────────────
    proposal_path = Path(os.path.expanduser(proposal_file_arg.strip()))

    # Accept bare filename if inside proposed_patches
    if not proposal_path.is_absolute():
        candidate = FORGE_ROOT / "proposed_patches" / proposal_file_arg.strip()
        if candidate.exists():
            proposal_path = candidate

    # ── Path boundary check BEFORE existence check ────────────────────────────
    # If an absolute path was given, verify it is inside proposed_patches
    # before reading anything. Do not expose or touch paths outside this dir.
    patches_dir = FORGE_ROOT / "proposed_patches"
    if proposal_path.is_absolute():
        try:
            proposal_path.relative_to(patches_dir)
        except ValueError:
            from agents.forge.memory import write_audit_entry
            audit_hash = write_audit_entry(
                session_id=session_id,
                tool="PATCH_DIFF_REFUSED",
                path=str(proposal_path),
                lines="-",
                reason="proposal path outside ~/forge/proposed_patches/"
            )
            print(f"[forge] REFUSED: Proposal file must be inside ~/forge/proposed_patches/")
            print(f"  Got     : {proposal_path}")
            print(f"  Expected: {patches_dir}")
            print(f"[forge] PATCH_DIFF_REFUSED logged. No path was read.")
            return

    # ── Now check existence ───────────────────────────────────────────────────
    if not proposal_path.exists():
        print(f"[forge] ERROR: Proposal file not found: {proposal_path}")
        print(f"  Try: patch-review (no argument) to list recent proposals.")
        return

    if not proposal_path.name.endswith(".txt"):
        print(f"[forge] ERROR: Expected a .txt proposal file.")
        return

    print()
    print(f"[forge] Reviewing proposal: {proposal_path.name}")

    # ── Parse proposal ────────────────────────────────────────────────────────
    try:
        proposal_content = proposal_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[forge] ERROR: Cannot read proposal file: {e}")
        return

    fields = _parse_proposal_file(proposal_content)
    target_file    = fields["target_file"]
    original_snippet = fields["original_snippet"]
    proposed_snippet = fields["proposed_snippet"]

    if not target_file:
        print("[forge] ERROR: Cannot parse 'Target file' from proposal.")
        return
    if not original_snippet:
        print("[forge] ERROR: Cannot parse 'ORIGINAL' section from proposal.")
        return
    if not proposed_snippet:
        print("[forge] ERROR: Cannot parse 'PROPOSED CHANGE' section from proposal.")
        return

    print(f"  Target   : {target_file}")
    print(f"  Original : {len(original_snippet)} chars")
    print(f"  Proposed : {len(proposed_snippet)} chars")

    # ── Validate target path ──────────────────────────────────────────────────
    blocked, reason = is_path_blocked(target_file)
    if blocked:
        print(f"[forge] ERROR: Target file is blocked: {reason}")
        return

    allowed, reason = is_path_allowed(target_file)
    if not allowed:
        print(f"[forge] WARNING: Target file may be outside current session scope: {reason}")
        print(f"[forge] Continuing with diff preview only.")

    # ── Read current file content ─────────────────────────────────────────────
    if not os.path.exists(target_file):
        print(f"[forge] WARNING: Target file does not exist: {target_file}")
        print(f"[forge] Showing proposal as-is without diff.")
        current_content = None
    else:
        try:
            with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                current_content = f.read()
        except OSError as e:
            print(f"[forge] ERROR: Cannot read target file: {e}")
            return

    # ── Check original snippet is still present ───────────────────────────────
    snippet_found = current_content is not None and original_snippet in current_content

    if current_content is not None and not snippet_found:
        print()
        print("  ⚠ WARNING: The original snippet is NOT found in the current target file.")
        print("  The file may have changed since this proposal was written.")
        print("  Diff preview will show proposal vs empty context only.")

    # ── Generate unified diff ─────────────────────────────────────────────────
    if snippet_found:
        proposed_content = current_content.replace(original_snippet, proposed_snippet, 1)
        from_lines = current_content.splitlines(keepends=True)
        to_lines   = proposed_content.splitlines(keepends=True)
        fname      = os.path.basename(target_file)
        diff_lines = list(difflib.unified_diff(
            from_lines,
            to_lines,
            fromfile=f"a/{fname}  (current)",
            tofile=f"b/{fname}  (proposed)",
            lineterm="",
        ))
        diff_text = "\n".join(diff_lines)
        has_diff  = bool(diff_lines)
    else:
        # Show snippet diff without file context
        from_lines = original_snippet.splitlines(keepends=True)
        to_lines   = proposed_snippet.splitlines(keepends=True)
        diff_lines = list(difflib.unified_diff(
            from_lines,
            to_lines,
            fromfile="original",
            tofile="proposed",
            lineterm="",
        ))
        diff_text = "\n".join(diff_lines)
        has_diff  = bool(diff_lines)

    # ── Print diff ────────────────────────────────────────────────────────────
    print()
    print("── Unified Diff Preview ──────────────────────────────")
    if not has_diff:
        print("  (no differences — original and proposed are identical)")
    else:
        for line in diff_lines[:200]:   # cap display at 200 lines
            if line.startswith("+"):
                print(f"  \033[92m{line}\033[0m")   # green
            elif line.startswith("-"):
                print(f"  \033[91m{line}\033[0m")   # red
            elif line.startswith("@"):
                print(f"  \033[36m{line}\033[0m")   # cyan
            else:
                print(f"  {line}")
        if len(diff_lines) > 200:
            print(f"  ... [{len(diff_lines) - 200} more diff lines in saved file]")
    print("──────────────────────────────────────────────────────")

    # ── Save diff file ────────────────────────────────────────────────────────
    diffs_dir = FORGE_ROOT / "proposed_patches" / "diffs"
    diffs_dir.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = re.sub(r"[^\w]", "_", proposal_path.stem)[:40]
    diff_filename = f"{timestamp_str}_DIFF_{slug}.txt"
    diff_path = diffs_dir / diff_filename

    diff_doc = f"""FORGE PATCH DIFF PREVIEW
{'═' * 66}
Proposal file   : {proposal_path}
Target file     : {target_file}
Timestamp       : {datetime.datetime.now().isoformat(timespec='seconds')}
Session ID      : {session_id}
Snippet found   : {'YES' if snippet_found else 'NO — file may have changed'}
{'═' * 66}

{diff_text if diff_text else '(no differences)'}

{'═' * 66}
No project files were modified by this diff preview.
Apply the change manually by editing the target file.
{'═' * 66}
"""
    diff_path.write_text(diff_doc, encoding="utf-8")

    # ── Audit ─────────────────────────────────────────────────────────────────
    audit_hash = write_audit_entry(
        session_id=session_id,
        tool="PATCH_DIFF_PREVIEWED",
        path=str(diff_path),
        lines=f"{len(diff_lines)} diff lines",
        reason=(
            f"proposal={proposal_path.name} | "
            f"target={target_file} | "
            f"snippet_found={snippet_found}"
        )
    )

    print()
    print(f"[forge] Diff saved : {diff_path}")
    print(f"[forge] Audit hash : {audit_hash}  (PATCH_DIFF_PREVIEWED)")
    print()
    print("[forge] No project files were modified.")
    print("[forge] To apply: edit the target file manually using the proposal as your guide.")
    print()


def cmd_patch_propose(
    target_file: str,
    session_id: str,
) -> None:
    """
    Deterministic patch proposal mode — bypasses the LLM entirely.
    Collects fields interactively, calls write_proposed_patch() directly in Python.

    Usage: patch-propose <target_file>
    Example: patch-propose ~/forge_test_project/test.txt

    For original_snippet and proposed_snippet: paste multiple lines, then type END.
    For all other fields: single-line input.
    """
    from agents.forge.patcher import write_proposed_patch
    from agents.forge.permissions import is_path_blocked, is_path_allowed

    # ── Resolve and pre-validate target path ──────────────────────────────────
    import os
    target_file = os.path.realpath(os.path.abspath(os.path.expanduser(target_file.strip())))

    print()
    print(f"[forge] Patch proposal for: {target_file}")

    # Fast-fail on blocked paths before asking all fields
    blocked, reason = is_path_blocked(target_file)
    if blocked:
        print(f"[forge] REFUSED (blocked): {reason}")
        from agents.forge.memory import write_audit_entry
        write_audit_entry(
            session_id=session_id,
            tool="PATCH_PROPOSAL_REFUSED",
            path=target_file,
            lines="-",
            reason=f"pre-validation blocked: {reason[:120]}"
        )
        print("[forge] PATCH_PROPOSAL_REFUSED logged. No files were written.")
        return

    allowed, reason = is_path_allowed(target_file)
    if not allowed:
        print(f"[forge] REFUSED (out of scope): {reason}")
        from agents.forge.memory import write_audit_entry
        write_audit_entry(
            session_id=session_id,
            tool="PATCH_PROPOSAL_REFUSED",
            path=target_file,
            lines="-",
            reason=f"pre-validation scope: {reason[:120]}"
        )
        print("[forge] PATCH_PROPOSAL_REFUSED logged. No files were written.")
        return

    print("[forge] Target path: approved ✓")
    print()

    # ── Collect single-line fields ─────────────────────────────────────────────
    def _ask(prompt: str, required: bool = True) -> str:
        while True:
            val = input(f"  {prompt}: ").strip()
            if val or not required:
                return val
            print("  (required — please enter a value)")

    def _ask_multiline(prompt: str) -> str:
        print(f"  {prompt}")
        print("  Paste content below. Type END on its own line when done.")
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.rstrip("\r\n") == "END":
                break
            lines.append(line)
        return "\n".join(lines)

    print("[forge] Fill in the patch proposal fields.")
    print("[forge] For multi-line fields (snippets), paste content and type END on its own line.")
    print()

    problem_summary = _ask("Problem summary (one or two sentences)")
    print()
    original_snippet = _ask_multiline("Original snippet (verbatim from the file)")
    print()
    proposed_snippet = _ask_multiline("Proposed snippet (exact replacement)")
    print()
    reasoning = _ask("Reasoning (why this change is correct and safe)")
    print()

    while True:
        risk = _ask("Risk level [LOW / MEDIUM / HIGH]").upper()
        if risk in ("LOW", "MEDIUM", "HIGH"):
            risk_level = risk
            break
        print("  Please enter LOW, MEDIUM, or HIGH.")

    print()
    test_plan = _ask("Test plan (how to verify the change works)")
    print()
    rollback_notes = _ask("Rollback notes (how to undo if needed)")
    print()

    # ── Confirm before writing ─────────────────────────────────────────────────
    print("── Proposal Summary ──────────────────────────────────")
    print(f"  Target      : {target_file}")
    print(f"  Problem     : {problem_summary[:80]}")
    print(f"  Risk        : {risk_level}")
    print(f"  Original    : {original_snippet[:60].replace(chr(10), ' ')}...")
    print(f"  Proposed    : {proposed_snippet[:60].replace(chr(10), ' ')}...")
    print("──────────────────────────────────────────────────────")
    print()

    confirm = input("  Write this proposal to ~/forge/proposed_patches/? [y/n]: ").strip().lower()
    if confirm != "y":
        print("[forge] Proposal cancelled. No files were written.")
        return

    # ── Call write_proposed_patch directly ────────────────────────────────────
    result = write_proposed_patch(
        session_id=session_id,
        target_file=target_file,
        problem_summary=problem_summary,
        original_snippet=original_snippet,
        proposed_snippet=proposed_snippet,
        reasoning=reasoning,
        risk_level=risk_level,
        test_plan=test_plan,
        rollback_notes=rollback_notes,
    )

    print()
    if result["ok"]:
        print(f"[forge] PATCH PROPOSAL CREATED")
        print(f"  Proposal : {result['proposal_path']}")
        print(f"  Audit    : PATCH_PROPOSAL_CREATED logged")
        print(f"  Target   : {target_file}  ← NOT modified")
        print()
        print("  To apply: open the proposal file, review it, then edit the target file manually.")
    else:
        print(f"[forge] REFUSED")
        print(f"  Reason   : {result.get('reason', 'Validation failed.')}")
        print(f"  Audit    : PATCH_PROPOSAL_REFUSED logged")
        print(f"  Target   : {target_file}  ← NOT modified")

    print()

    # Link to active diagnostic session if one is open
    if _active_diag_session_id and result.get("proposal_path"):
        try:
            from agents.forge.diag_session import link_proposal
            link_proposal(
                session_id=_active_diag_session_id,
                proposal_path=result["proposal_path"],
                command=f"patch:{target_file}",
                allowed=result["ok"],
                risk_level=risk_level,
            )
        except Exception:
            pass


def cmd_propose(
    command: str,
    session_id: str,
    forge_session_id: str,
) -> None:
    """
    Deterministic proposal mode — bypasses the LLM entirely.
    Calls propose_command validation directly in Python.

    Usage inside a Forge session: propose <command>
    Examples:
      forge> propose ollama version
      forge> propose nvidia-smi
      forge> propose journalctl -u ollama.service -n 50 --no-pager
    """
    from agents.forge.proposals import propose_command, validate_command

    command = command.strip()
    if not command:
        print("[forge] Usage: propose <command>")
        print("  Examples:")
        print("    propose ollama version")
        print("    propose nvidia-smi")
        print("    propose journalctl -u ollama.service -n 50 --no-pager")
        return

    print()
    print(f"[forge] Validating proposal for: {command}")

    # Pre-validate so we can show a fast answer before building the full document
    validation = validate_command(command)
    if not validation.allowed:
        print(f"[forge] REFUSED: {validation.reason}")
        print(f"[forge] Logging refusal to audit and proposals directory...")

    # Call propose_command directly — fills in CLI-appropriate field values
    # The model normally fills these fields; here we use honest CLI defaults
    result = propose_command(
        session_id=forge_session_id,
        user_question=f"[Direct CLI proposal by Nic via 'propose {command}']",
        command=command,
        purpose=f"Direct diagnostic proposal submitted via Forge CLI.",
        safety_rationale=(
            f"Command proposed directly by Nic via the 'propose' CLI command. "
            f"Validated against Forge Level 0.9 allowlist."
        ),
        risk_level=validation.risk if validation.allowed else "HIGH",
        expected_output="(Run the command and use 'diag' to paste output for analysis.)",
        what_could_go_wrong=(
            "Standard caveats apply for this command type. "
            "Review the proposal file for details before running."
        ),
    )

    if result.get("duplicate"):
        print(f"[forge] DUPLICATE: This command was already proposed this session.")
        print(f"  Existing proposal: {result['proposal_path']}")
        print()
        print(f"  Command: {command}")
        print()
        print("  Copy and paste the command yourself if you approve:")
        print(f"    {command}")
        print()
        return

    if result["ok"]:
        print(f"[forge] PROPOSAL CREATED")
        print(f"  Command  : {command}")
        print(f"  Risk     : {result['risk_level']}")
        print(f"  File     : {result['proposal_path']}")
        print(f"  Audit    : PROPOSE_COMMAND logged")
        print()
        print(f"  {'─' * 48}")
        print(f"  Copy and paste the command yourself if you approve:")
        print(f"    {command}")
        print(f"  {'─' * 48}")
        print()
        print(f"  Then paste the output with:  diag {command}")
        print()
    else:
        print(f"[forge] REFUSED")
        print(f"  Command  : {command}")
        print(f"  Reason   : {result.get('reason', 'Validation failed.')}")
        print(f"  File     : {result.get('proposal_path', '(no file)')}")
        print(f"  Audit    : PROPOSE_COMMAND_REFUSED logged")
        print()

    # Link to active diagnostic session if one is open
    if _active_diag_session_id and result.get("proposal_path"):
        try:
            from agents.forge.diag_session import link_proposal
            link_proposal(
                session_id=_active_diag_session_id,
                proposal_path=result["proposal_path"],
                command=command,
                allowed=result["ok"],
                risk_level=result.get("risk_level", ""),
            )
            print(f"[forge] Linked to session: {_active_diag_session_id}")
        except Exception as e:
            print(f"[forge] WARNING: Could not link to diag session: {e}")


def cmd_diag_session(
    subcommand: str,
    topic_or_status: str,
    session_id_str: str,
    agent,
) -> None:
    """
    diag-session start <topic>         — start a new diagnostic session
    diag-session status                — show current session status
    diag-session close resolved|abandoned [note] — close current session
    diag-session list                  — list recent sessions
    """
    from agents.forge.diag_session import (
        create_session, format_status, format_summary_line,
        list_sessions, update_status, get_active_session_context,
    )
    from agents.forge.memory import write_audit_entry

    global _active_diag_session_id

    if subcommand == "start":
        topic = topic_or_status.strip()
        if not topic:
            print("[forge] Usage: diag-session start <topic>")
            print("  Example: diag-session start ollama_gpu_check")
            return

        new_id = create_session(topic, session_id_str)
        _active_diag_session_id = new_id
        agent.set_diag_session(new_id)

        write_audit_entry(
            session_id=session_id_str,
            tool="DIAG_SESSION_START",
            path=str(FORGE_ROOT / "diagnostics" / "sessions" / new_id / "session.json"),
            lines="-",
            reason=f"topic={topic} | diag_session={new_id}"
        )

        print()
        print(f"[forge] Diagnostic session started.")
        print(f"  Session : {new_id}")
        print(f"  Topic   : {topic}")
        print(f"  Use 'diag <command>' to capture output linked to this session.")
        print(f"  Use 'diag-session status' to see the full chain.")
        print()

    elif subcommand == "status":
        if not _active_diag_session_id:
            print("[forge] No active diagnostic session. Use 'diag-session start <topic>'.")
            # Show recent sessions
            recent = list_sessions(5)
            if recent:
                print("[forge] Recent sessions:")
                for s in recent:
                    print(format_summary_line(s))
            return
        print(format_status(_active_diag_session_id))

    elif subcommand == "close":
        if not _active_diag_session_id:
            print("[forge] No active diagnostic session to close.")
            return

        raw_status = topic_or_status.strip().lower()
        if raw_status not in ("resolved", "abandoned"):
            print("[forge] Usage: diag-session close resolved|abandoned [note]")
            return

        update_status(_active_diag_session_id, raw_status)
        write_audit_entry(
            session_id=session_id_str,
            tool="DIAG_SESSION_CLOSE",
            path=str(FORGE_ROOT / "diagnostics" / "sessions" / _active_diag_session_id / "session.json"),
            lines="-",
            reason=f"status={raw_status} | diag_session={_active_diag_session_id}"
        )

        closed_id = _active_diag_session_id
        _active_diag_session_id = None
        agent.set_diag_session(None)

        print()
        print(f"[forge] Diagnostic session closed as {raw_status.upper()}.")
        print(f"  Session : {closed_id}")
        print()

    elif subcommand == "list":
        sessions = list_sessions(10)
        if not sessions:
            print("[forge] No diagnostic sessions found.")
            return
        print()
        print("  Recent diagnostic sessions:")
        for s in sessions:
            marker = " ← active" if s == _active_diag_session_id else ""
            print(format_summary_line(s) + marker)
        print()

    else:
        print("[forge] Usage:")
        print("  diag-session start <topic>")
        print("  diag-session status")
        print("  diag-session close resolved|abandoned")
        print("  diag-session list")


def cmd_diag_paste(
    command: str,
    session_id: str,
    agent,
) -> None:
    """
    Deterministic paste capture mode.
    Reads lines from stdin until the sentinel 'END' appears alone on a line.
    Calls analyze_command_output directly in Python — no LLM extraction involved.
    Then passes the stored result to the agent for analysis only.

    Usage inside a Forge session: diag free -h
    """
    from agents.forge.diagnostics import analyze_command_output
    from agents.forge.memory import write_audit_entry

    print()
    print(f"[forge] Capturing output for: {command}")
    print(f"[forge] Paste the terminal output below.")
    print(f"[forge] When done, type END on its own line and press Enter.")
    print()

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.rstrip("\r\n") == "END":
            break
        lines.append(line)

    if not lines:
        print("[forge] No output captured. Diagnostic cancelled.")
        write_audit_entry(
            session_id=session_id,
            tool="DIAGNOSTIC_CAPTURE_CANCELLED",
            path=command,
            lines="-",
            reason="diag command: no output lines received before END"
        )
        return

    # Join lines exactly as pasted — preserve all leading whitespace
    captured_output = "\n".join(lines)

    print(f"[forge] Captured {len(lines)} lines. Storing...")

    # Call analyze_command_output directly — bypasses LLM entirely
    result = analyze_command_output(
        session_id=session_id,
        command=command,
        output=captured_output,
        context="",
    )

    if not result["ok"]:
        print(f"[forge] ERROR: {result['error']}")
        return

    print(f"[forge] Stored. Lines: {result['output_line_count']} | SHA-256: {result['output_sha256']}")
    print(f"[forge] Diagnostic file: {result['diagnostic_path']}")

    # Link to active diagnostic session if one is running
    if _active_diag_session_id:
        try:
            from agents.forge.diag_session import link_diagnostic
            link_diagnostic(
                session_id=_active_diag_session_id,
                diag_path=result['diagnostic_path'],
                command=command,
                sha256=result['output_sha256'],
                line_count=result['output_line_count'],
            )
            print(f"[forge] Linked to session: {_active_diag_session_id}")
        except Exception as e:
            print(f"[forge] WARNING: Could not link to diag session: {e}")
    print()

    # Build the analysis question — tell the agent the capture already happened
    # so it does not try to call analyze_command_output again
    question = (
        f"The terminal output from running `{command}` has already been captured "
        f"and stored by the CLI (not by you). "
        f"SHA-256 of stored output: {result['output_sha256']}. "
        f"Diagnostic file: {result['diagnostic_path']}.\n\n"
        f"Here is the verbatim output that was stored:\n\n"
        f"{result['output_preview']}\n\n"
        f"Do NOT call analyze_command_output — the capture is already complete and audited. "
        f"Your job is analysis only:\n"
        f"1. What does this output say? (literal values and what they represent)\n"
        f"2. What does it mean? (interpretation in plain language)\n"
        f"3. Are there any warnings, errors, or concerning values?\n"
        f"4. Is a next diagnostic step needed? If so, call propose_command."
    )

    print("[forge] Analyzing...")
    response = agent.ask(question)
    _print_response(response)


def run_session():
    """Main interactive session loop."""
    approved = get_approved_paths()

    # First-run setup if needed
    if not approved:
        _first_run_setup()
        approved = get_approved_paths()
        if not approved:
            print("[forge] ERROR: No approved paths. Cannot start session.")
            sys.exit(1)

    # Set session scope
    scope = _setup_session_scope(approved)

    # Create session ID and update session_scope.json with it
    session_id = _make_session_id()
    session_data = _load_json(SESSION_SCOPE_FILE)
    session_data["session_id"] = session_id
    _save_json(SESSION_SCOPE_FILE, session_data)

    # Write session start to audit log
    write_session_start(session_id, scope)

    # Initialize session memory and agent
    memory = SessionMemory(session_id)
    agent  = ForgeAgent(session_id, memory)

    # Ensure proposals directory exists
    (FORGE_ROOT / "proposals").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "diagnostics").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "proposed_patches").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "rollback_registry").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "rollback_registry" / "restore_safety_snapshots").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "apply_plans").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "corpus_reports").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "corpus_reports").mkdir(parents=True, exist_ok=True)

    _print_banner(session_id, scope)

    # files_changed tracks whether approved project writes occurred this session.
    # False = no writes. String = reason code for audit.
    files_changed: bool | str = False

    try:
        while True:
            try:
                user_input = input("forge> ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                break

            if user_input.lower() == "status":
                cmd_status()
                continue

            if user_input.lower() == "audit":
                cmd_audit()
                continue

            if user_input.lower().startswith("run "):
                run_cmd = user_input[4:].strip()
                cmd_run(run_cmd, session_id, agent)
                continue

            if user_input.lower() == "run":
                from agents.forge.runner import COMMAND_NAMES
                print()
                print("  Usage: run <command_name>")
                print("  Level 1.0 allowlist:")
                for name in COMMAND_NAMES:
                    print(f"    run {name}")
                print()
                continue

            if user_input.lower() == "corpus-extract-check":
                cmd_corpus_extract_check(session_id)
                continue

            if user_input.lower() == "corpus-extract-report":
                cmd_corpus_extract_report(session_id)
                continue

            if user_input.lower().startswith("corpus-extract-show "):
                ces_arg = user_input[20:].strip()
                cmd_corpus_extract_show(ces_arg, session_id)
                continue

            if user_input.lower() == "corpus-extract-show":
                cmd_corpus_extract_show("latest", session_id)
                continue

            if user_input.lower() == "corpus-extract-check":
                cmd_corpus_extract_check(session_id)
                continue

            if user_input.lower() == "corpus-extract-report":
                cmd_corpus_extract_report(session_id)
                continue

            if user_input.lower().startswith("corpus-extract-show "):
                ces_arg = user_input[20:].strip()
                cmd_corpus_extract_show(ces_arg, session_id)
                continue

            if user_input.lower() == "corpus-extract-show":
                cmd_corpus_extract_show("latest", session_id)
                continue

            if user_input.lower() == "doc-capabilities":
                cmd_doc_capabilities(session_id)
                continue

            if user_input.lower() == "doc-formats":
                cmd_doc_formats(session_id)
                continue

            if user_input.lower().startswith("doc-preview "):
                dp_id = user_input[12:].strip()
                cmd_doc_preview(dp_id, session_id)
                continue

            if user_input.lower() == "doc-preview":
                print()
                print("  Usage: doc-preview <corpus_id>")
                print("  Example: doc-preview corpus_0011")
                print()
                continue

            if user_input.lower().startswith("corpus-preview "):
                cp_id = user_input[15:].strip()
                cmd_corpus_preview(cp_id, session_id)
                continue

            if user_input.lower() == "corpus-preview":
                print()
                print("  Usage: corpus-preview <corpus_id>")
                print("  Example: corpus-preview corpus_0011")
                print()
                continue

            if user_input.lower() == "corpus-list":
                cmd_corpus_list(session_id)
                continue

            if user_input.lower() == "corpus-status":
                cmd_corpus_status(session_id)
                continue

            if user_input.lower().startswith("corpus-show "):
                cs_arg = user_input[12:].strip()
                cmd_corpus_show(cs_arg, session_id)
                continue

            if user_input.lower() == "corpus-show":
                print()
                print("  Usage: corpus-show <corpus_id>")
                print("  Example: corpus-show corpus_0011")
                print()
                continue

            if user_input.lower() == "corpus-check":
                cmd_corpus_check(session_id)
                continue

            if user_input.lower() == "corpus-policy":
                cmd_corpus_policy(session_id)
                continue

            if user_input.lower().startswith("exact-list "):
                el_rest = user_input[11:].strip()
                files_only_flag = "--files-only" in el_rest
                el_dir = el_rest.replace("--files-only", "").strip()
                cmd_exact_list(el_dir, files_only=files_only_flag, session_id=session_id)
                continue

            if user_input.lower() == "exact-list":
                cmd_exact_list("", session_id=session_id)
                continue

            if user_input.lower().startswith("exact-read "):
                er_arg = user_input[11:].strip()
                cmd_exact_read(er_arg, session_id=session_id)
                continue

            if user_input.lower() == "exact-read":
                cmd_exact_read("", session_id=session_id)
                continue

            if user_input.lower().startswith("field-report "):
                fr_arg = user_input[13:].strip()
                cmd_field_report(fr_arg, session_id)
                continue

            if user_input.lower() == "field-report":
                print()
                print("  Usage: field-report <plan_or_rollback_or_target_file>")
                print("  Example: field-report 2026-05-09_PLAN_README_md.txt")
                print("  Example: field-report /home/nic/aiweb/README.md")
                print()
                continue

            if user_input.lower() == "patch-list":
                cmd_patch_list(session_id)
                continue

            if user_input.lower().startswith("patch-status "):
                ps_arg = user_input[13:].strip()
                cmd_patch_status(ps_arg, session_id)
                continue

            if user_input.lower() == "patch-status":
                print()
                print("  Usage: patch-status <filename_or_path>")
                print("  Example: patch-status 2026-05-09_PLAN_test_txt.txt")
                print()
                continue

            if user_input.lower().startswith("patch-chain "):
                pc_arg = user_input[12:].strip()
                cmd_patch_chain(pc_arg, session_id)
                continue

            if user_input.lower() == "patch-chain":
                print()
                print("  Usage: patch-chain <filename_or_path>")
                print("  Example: patch-chain 2026-05-09_ROLLBACK_test_txt.txt")
                print()
                continue

            if user_input.lower().startswith("rollback-restore "):
                rr_arg = user_input[17:].strip()
                restored = cmd_rollback_restore(rr_arg, session_id)
                if restored:
                    files_changed = "APPROVED_ROLLBACK_RESTORED"
                continue

            if user_input.lower() == "rollback-restore":
                cmd_rollback_restore("", session_id)
                continue

            if user_input.lower().startswith("patch-verify "):
                pv_arg = user_input[13:].strip()
                cmd_patch_verify(pv_arg, session_id)
                continue

            if user_input.lower() == "patch-verify":
                cmd_patch_verify("", session_id)
                continue

            if user_input.lower().startswith("patch-apply "):
                pa_arg = user_input[12:].strip()
                applied = cmd_patch_apply(pa_arg, session_id)
                if applied:
                    files_changed = "APPROVED_PATCH_APPLIED"
                continue

            if user_input.lower() == "patch-apply":
                cmd_patch_apply("", session_id)
                continue

            if user_input.lower().startswith("patch-preflight "):
                pf_arg = user_input[16:].strip()
                cmd_patch_preflight(pf_arg, session_id)
                continue

            if user_input.lower() == "patch-preflight":
                cmd_patch_preflight("", session_id)
                continue

            if user_input.lower().startswith("patch-review ") or user_input.lower().startswith("show-patch-diff "):
                # Accept both aliases
                if user_input.lower().startswith("patch-review "):
                    review_arg = user_input[13:].strip()
                else:
                    review_arg = user_input[16:].strip()
                if not review_arg:
                    print()
                    print("  Usage: patch-review <proposal_file>")
                    print("  Example: patch-review 2026-05-09_PATCH_test_txt.txt")
                    print("  Example: patch-review ~/forge/proposed_patches/2026-05-09_PATCH_test_txt.txt")
                    print()
                else:
                    cmd_patch_review(review_arg, session_id)
                continue

            if user_input.lower() in ("patch-review", "show-patch-diff"):
                # List available proposals
                patches_dir = FORGE_ROOT / "proposed_patches"
                proposals = sorted(patches_dir.glob("PROPOSAL_*.txt"), reverse=True) if patches_dir.exists() else []
                if proposals:
                    print()
                    print("  Usage: patch-review <proposal_file>")
                    print("  Recent proposals:")
                    for p in proposals[:8]:
                        print(f"    patch-review {p.name}")
                    print()
                else:
                    print()
                    print("  Usage: patch-review <proposal_file>")
                    print("  No proposals found yet. Create one with: patch-propose <file>")
                    print()
                continue

            if user_input.lower().startswith("patch-propose "):
                patch_target = user_input[14:].strip()
                if not patch_target:
                    print()
                    print("  Usage: patch-propose <target_file>")
                    print("  Example: patch-propose ~/forge_test_project/test.txt")
                    print()
                else:
                    cmd_patch_propose(patch_target, session_id)
                continue

            if user_input.lower() == "patch-propose":
                print()
                print("  Usage: patch-propose <target_file>")
                print("  Example: patch-propose ~/forge_test_project/test.txt")
                print()
                continue

            if user_input.lower().startswith("propose "):
                raw = user_input[8:].strip()
                # Routing guard: "propose a patch/change/fix..." = natural language, not shell command
                # Route those to patch-propose suggestion instead of shell command validator
                first_word = raw.split()[0].lower() if raw.split() else ""
                if first_word in ("a", "an", "the", "patch", "change", "fix", "update", "edit"):
                    print()
                    print("[forge] That looks like a natural language patch request.")
                    print("[forge] Use 'patch-propose <file>' for deterministic patch proposals.")
                    print("  Example: patch-propose ~/forge_test_project/test.txt")
                    print()
                    continue
                cmd_propose(raw, session_id, session_id)
                continue

            if user_input.lower() == "propose":
                propose_cmd = user_input[8:].strip()
                cmd_propose(propose_cmd, session_id, session_id)
                continue

            if user_input.lower() == "propose":
                print()
                print("  Usage: propose <command>")
                print("  Examples:")
                print("    propose ollama version")
                print("    propose nvidia-smi")
                print("    propose journalctl -u ollama.service -n 50 --no-pager")
                print("    propose df -h")
                print()
                continue

            if user_input.lower().startswith("diag-session "):
                parts = user_input[13:].strip().split(None, 1)
                sub  = parts[0].lower() if parts else ""
                rest = parts[1].strip() if len(parts) > 1 else ""
                cmd_diag_session(sub, rest, session_id, agent)
                continue

            if user_input.lower() == "diag-session":
                cmd_diag_session("status", "", session_id, agent)
                continue

            if user_input.lower().startswith("diag "):
                diag_command = user_input[5:].strip()
                if not diag_command:
                    print()
                    print("  Usage: diag <command>")
                    print("  Example: diag free -h")
                    print()
                else:
                    cmd_diag_paste(diag_command, session_id, agent)
                continue

            if user_input.lower() == "help":
                print()
                print("  Commands:")
                print("    status                          — show current config")
                print("    audit                           — check audit log integrity")
                print("    run <command>                   — execute from Level 1.0 allowlist")
                print("    propose <command>               — validate and save a shell command proposal")
                print("    patch-propose <target_file>     — create a patch proposal")
                print("    patch-review <proposal_file>    — show unified diff preview")
                print("    patch-preflight <proposal_file> — validate + save rollback + apply plan")
                print("    exact-list <dir> [--files-only]  — exact directory listing (bypasses LLM)")
                print("    exact-read <file>                — exact file read (bypasses LLM)")
                print("    patch-status <file>              — show artifact type and state")
                print("    patch-chain <file>               — show full lifecycle chain")
                print("    patch-verify <plan_file>          — verify post-apply state (read-only)")
                print("    diag <command>                  — paste multi-line terminal output")
                print("    diag-session start <topic>      — start a diagnostic session")
                print("    diag-session status             — show active session chain")
                print("    diag-session close resolved     — close session as resolved")
                print("    diag-session list               — list recent sessions")
                print("    quit                            — end session")
                print()
                print("  Level 4.0 full patch workflow:")
                print("    patch-propose <file>       ← create proposal")
                print("    patch-review <proposal>    ← preview diff")
                print("    patch-preflight <proposal> ← save rollback + apply plan")
                print("    patch-apply <plan>         ← apply (requires typing APPLY)")
                print()
                print("  Or just type your question.")
                print()
                continue

            # Process the question
            print()
            print("[forge] Thinking...")
            response = agent.ask(user_input)
            _print_response(response)

    except KeyboardInterrupt:
        print("\n[forge] Session interrupted.")

    finally:
        # Determine session end reason and message
        if not files_changed:
            end_reason = "FILES_UNCHANGED"
            end_msg = "Session ended. No files were changed this session."
        elif files_changed == "APPROVED_ROLLBACK_RESTORED":
            end_reason = "APPROVED_ROLLBACK_RESTORED"
            end_msg = "Session ended. Approved rollback restore occurred this session."
        else:
            end_reason = "APPROVED_PATCH_APPLIED"
            end_msg = "Session ended. Approved project file writes occurred this session."

        write_session_end(session_id, end_reason)

        print()
        print(f"[forge] {end_msg}")
        print(f"[forge] Audit log: {AUDIT_LOG}")
        print()


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

def cmd_add(path_arg: str, mode: str = "core", preview_only: bool = False):
    """
    forge add <path> [--mode core|docs|logs|all] [--preview]

    Scan a path, show inclusion preview, ask for approval, then index into ChromaDB.
    Uses approved_paths.json + blocked_paths.json only. Session scope is not consulted.

    --mode core    Source and high-signal files only. DEFAULT.
    --mode docs    Documentation files only.
    --mode logs    Core files plus .log, .jsonl, .trace files.
    --mode all     Broad scan. Requires extra confirmation if over 1000 files.

    --preview / --dry-run
                   Scan and show detailed report without indexing anything.
    """
    from agents.forge.knowledge_base import (
        scan_for_indexing,
        index_path,
        check_embed_model_available,
        get_kb_stats,
        EMBED_MODEL,
        KB_DIR,
        INDEXING_MODES,
        LARGE_INDEX_THRESHOLD,
    )
    from agents.forge.permissions import (
        get_approved_paths,
        is_path_blocked,
        _is_under_any,
    )
    from agents.forge.memory import write_audit_entry

    if mode not in INDEXING_MODES:
        print(f"[forge] ERROR: Unknown mode '{mode}'. Choose from: {list(INDEXING_MODES)}")
        sys.exit(1)

    path = os.path.realpath(os.path.abspath(os.path.expanduser(path_arg)))

    # Generate KB session ID
    kb_session_id = f"kb_{datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')}"

    # Check 1: approved
    approved = get_approved_paths()
    if not approved:
        print(f"[forge] ERROR: No approved paths configured.")
        print(f"[forge] Run 'python main.py approve {path}' first.")
        sys.exit(1)
    if not _is_under_any(path, approved):
        print(f"[forge] ERROR: '{path}' is not in approved_paths.json.")
        print(f"[forge] Approved: {approved}")
        print(f"[forge] Run 'python main.py approve {path}' to add it.")
        sys.exit(1)

    # Check 2: not blocked
    blocked, reason = is_path_blocked(path)
    if blocked:
        print(f"[forge] ERROR: Path is blocked. {reason}")
        sys.exit(1)

    # Check 3: exists
    if not os.path.exists(path):
        print(f"[forge] ERROR: Path does not exist: {path}")
        sys.exit(1)

    # Check embedding model (skip in preview-only mode)
    if not preview_only:
        model_ok, model_msg = check_embed_model_available()
        if not model_ok:
            print(f"[forge] ERROR: {model_msg}")
            sys.exit(1)
        print(f"[forge] Embedding model: {EMBED_MODEL} ✓")

    # AUDIT: KB_SCAN_START
    write_audit_entry(
        session_id=kb_session_id,
        tool="KB_SCAN_START",
        path=path,
        lines="-",
        reason=f"forge add | mode={mode} | preview={preview_only} | model={EMBED_MODEL}"
    )

    # Scan with session scope override
    import agents.forge.permissions as perms
    orig_session = perms.get_session_paths
    perms.get_session_paths = lambda: [path]
    print(f"[forge] Scanning {path}  [mode: {mode}] ...")
    try:
        scan = scan_for_indexing(path, mode=mode)
    finally:
        perms.get_session_paths = orig_session

    # AUDIT: KB_SCAN_PREVIEW
    write_audit_entry(
        session_id=kb_session_id,
        tool="KB_SCAN_PREVIEW",
        path=path,
        lines="-",
        reason=(
            f"mode={mode} | "
            f"to_index={len(scan.will_index)} | "
            f"already_current={len(scan.already_current)} | "
            f"excluded={len(scan.will_skip)}"
        )
    )

    # ── PREVIEW / DRY RUN MODE ──
    if preview_only:
        print(scan.detailed_preview())
        write_audit_entry(
            session_id=kb_session_id,
            tool="KB_INDEX_COMPLETE",
            path=path,
            lines="-",
            reason=f"DRY RUN — no files indexed | mode={mode}"
        )
        return

    # ── NORMAL MODE: show short summary then ask ──
    print("\n── Indexing Preview ──────────────────────────────────")
    print(scan.summary())
    print("──────────────────────────────────────────────────────")

    if scan.is_empty():
        print("\n[forge] Nothing new to index.")
        if scan.already_current:
            print(f"[forge] {len(scan.already_current)} files are already current.")
        write_audit_entry(
            session_id=kb_session_id,
            tool="KB_INDEX_COMPLETE",
            path=path,
            lines="-",
            reason="nothing_to_index | all files already current"
        )
        return

    # ── 1000-FILE GATE ──
    if len(scan.will_index) > LARGE_INDEX_THRESHOLD:
        print()
        print(f"  ⚠️  WARNING: This index contains {len(scan.will_index):,} files.")
        print(f"     That is more than {LARGE_INDEX_THRESHOLD} files.")
        print(f"     Indexing will take significant time and disk space.")
        print()
        confirm_large = input(
            f"  Type INDEX (all caps) to continue, or anything else to cancel: "
        ).strip()
        if confirm_large != "INDEX":
            write_audit_entry(
                session_id=kb_session_id,
                tool="KB_INDEX_CANCELLED",
                path=path,
                lines="-",
                reason=f"large index cancelled by user ({len(scan.will_index)} files)"
            )
            print("[forge] Indexing cancelled.")
            return
    else:
        # Normal approval
        print()
        confirm = input(
            f"  Index {len(scan.will_index)} files into the local knowledge base? [y/n]: "
        ).strip().lower()
        if confirm != "y":
            write_audit_entry(
                session_id=kb_session_id,
                tool="KB_INDEX_CANCELLED",
                path=path,
                lines="-",
                reason="user declined indexing"
            )
            print("[forge] Indexing cancelled. No files were changed.")
            return

    # AUDIT: KB_INDEX_APPROVED
    write_audit_entry(
        session_id=kb_session_id,
        tool="KB_INDEX_APPROVED",
        path=path,
        lines="-",
        reason=f"user approved | mode={mode} | files_to_index={len(scan.will_index)}"
    )

    project_name = os.path.basename(path.rstrip("/")) or "unknown"
    print(f"\n[forge] Indexing into project '{project_name}'  [mode: {mode}] ...")
    print(f"[forge] This may take a few minutes for large codebases.\n")

    files_indexed, chunks_created, empty_skipped, true_errors = index_path(
        path=path,
        project_name=project_name,
        files_to_index=scan.will_index,
        session_id=kb_session_id,
        already_current_count=len(scan.already_current),
    )

    write_audit_entry(
        session_id=kb_session_id,
        tool="KB_INDEX_COMPLETE",
        path=path,
        lines=f"{chunks_created} chunks",
        reason=(
            f"files_indexed={files_indexed} | "
            f"chunks={chunks_created} | "
            f"empty_skipped={empty_skipped} | "
            f"true_errors={true_errors} | "
            f"mode={mode} | "
            f"project={project_name}"
        )
    )

    print()
    print("── Indexing Complete ─────────────────────────────────")
    print(f"  Mode          : {mode}")
    print(f"  Files indexed : {files_indexed}")
    print(f"  Chunks created: {chunks_created}")
    if empty_skipped:
        print(f"  Empty skipped : {empty_skipped}")
    if true_errors:
        print(f"  True errors   : {true_errors}")
    print(f"  Manifest      : {MEMORY_DIR / 'forge_kb_manifest.json'}")
    print(f"  Vector DB     : {KB_DIR}")
    print()
    print(get_kb_stats())
    print("──────────────────────────────────────────────────────")
    print()
    print("[forge] No project files were modified. Only the local knowledge base was updated.")


def cmd_kb(subcommand: str = "status", query: str = "", n_results: int = 5):
    """
    forge kb             — show knowledge base stats
    forge kb search <q>  — search the knowledge base directly (no LLM)
    """
    from agents.forge.knowledge_base import get_kb_stats, search_knowledge_base

    if subcommand == "search":
        if not query:
            print("[forge] ERROR: Provide a search query. Example: python main.py kb search 'agent loop'")
            sys.exit(1)

        print(f"\n[forge] Searching knowledge base for: '{query}'  (top {n_results} results)\n")
        result = search_knowledge_base(query, n_results=n_results)

        if not result["ok"]:
            print(f"[forge] {result['error']}")
            sys.exit(1)

        print(result["data"])
        print("[forge] Direct KB search complete. No files were read. No LLM was used.")

    else:
        # Default: status
        print()
        print(get_kb_stats())
        print()


def main():
    parser = argparse.ArgumentParser(
        prog="forge",
        description="Forge — AI.Web local coding assistant"
    )
    subparsers = parser.add_subparsers(dest="command")

    # forge approve <path>
    approve_parser = subparsers.add_parser("approve", help="Approve a path for Forge access")
    approve_parser.add_argument("path", help="Absolute or relative path to approve")

    # forge add <path> [--mode core|docs|logs|all] [--preview]
    add_parser = subparsers.add_parser("add", help="Index a path into the local knowledge base")
    add_parser.add_argument("path", help="Path to scan and index")
    add_parser.add_argument(
        "--mode",
        choices=["core", "docs", "logs", "all", "project"],
        default="core",
        help="Indexing mode (default: core)"
    )
    add_parser.add_argument(
        "--preview", "--dry-run",
        dest="preview",
        action="store_true",
        default=False,
        help="Scan and show detailed preview without indexing"
    )

    # forge audit
    subparsers.add_parser("audit", help="Verify integrity of forge_audit.log")

    # forge status
    subparsers.add_parser("status", help="Show current Forge configuration")

    # forge kb [search <query>] [--results N]
    kb_parser = subparsers.add_parser("kb", help="Knowledge base: status or direct search")
    kb_sub = kb_parser.add_subparsers(dest="kb_subcommand")
    kb_search_parser = kb_sub.add_parser("search", help="Search the KB directly without the LLM")
    kb_search_parser.add_argument("query", help="Search query")
    kb_search_parser.add_argument(
        "--results", "-n",
        type=int,
        default=5,
        dest="n_results",
        help="Number of results to return (default: 5)"
    )

    args = parser.parse_args()

    if args.command == "approve":
        cmd_approve(args.path)
    elif args.command == "add":
        cmd_add(args.path, mode=args.mode, preview_only=args.preview)
    elif args.command == "audit":
        cmd_audit()
    elif args.command == "status":
        cmd_status()
    elif args.command == "kb":
        if hasattr(args, "kb_subcommand") and args.kb_subcommand == "search":
            cmd_kb("search", args.query, args.n_results)
        else:
            cmd_kb("status")
    else:
        # No subcommand — start a session
        run_session()


if __name__ == "__main__":
    main()

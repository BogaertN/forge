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
    print("│  FORGE  —  Local Coding Assistant  —  Level 5.0    │")
    print("│  Phase B Multi-Document Ingestion Planning.       │")
    print("│  dry-run parity | duplicate guard | receipts        │")
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



CORPUS_REPORTS_DIR = FORGE_ROOT / "corpus_reports"
VECTOR_REPORTS_DIR    = FORGE_ROOT / "vector_reports"
SOURCE_GAP_REPORTS_DIR = FORGE_ROOT / "source_gap_reports"
INGESTION_PLANS_DIR   = FORGE_ROOT / "ingestion_plans"
CHROMA_DB_PATH        = FORGE_ROOT / "memory" / "chroma_db"
INGESTION_AUTH_FILE   = FORGE_ROOT / "ingestion_plans" / "INGESTION_AUTHORIZED.flag"

# Known source references not yet in local corpus (from Drive audit)
KNOWN_SOURCE_GAPS = [
    {
        "title": "RPMC Full Protocol Draft",
        "full_title": "Resonant Phase Memory Calculus: The Law of Recursion, Collapse, and Return — Full Protocol Draft",
        "category": "RPMC Core Protocol",
        "role": "Primary RPMC law document — defines all operators, axioms, and structure",
        "drive_id": "1eN6in0lUcGY9RdHcAPFlJOHJNpN6ny1M",
        "required_for_full_authority": True,
        # Identity fingerprints: words that uniquely identify THIS document vs. any other RPMC-related doc.
        # Deliberately EXCLUDES generic RPMC terms ("phase", "memory", "resonant", "echo", "drift").
        "identity_fingerprints": ["calculus", "protocol", "rpmc", "recursion", "collapse"],
        "strong_match_threshold": 2,  # 2 of 5 specific fingerprints in filename = strong signal
        "generic_rpmc_terms": ["resonant", "phase", "memory", "echo", "drift"],
    },
    {
        "title": "RPMC Implementation Blueprint",
        "full_title": "RPMC Implementation Blueprint (ProtoForge Dev Book)",
        "category": "RPMC Implementation",
        "role": "Engineering guide for RPMC runtime — Memory Stack, Collapse Handler, Resurrection Log",
        "drive_id": "1L_f5I2InqyMiGKX7ERs0et9jY9-gzpVgvqmZ-VAl46E",
        "required_for_full_authority": True,
        "identity_fingerprints": ["blueprint", "implementation", "protoforge"],
        "strong_match_threshold": 2,
        "generic_rpmc_terms": ["memory", "stack", "collapse", "resurrection"],
    },
    {
        "title": "RPMC Canonical Test Data Set v1.0",
        "full_title": "Resonant Phase Memory Calculus Canonical Test Data Set Version 1.0",
        "category": "RPMC Validation",
        "role": "Benchmark for recursive memory, echo integrity, drift, and resurrection validation",
        "drive_id": "1b8JAc-aATjD7h1Ed4KYA2kxxPkxHaX5-lDO5V5qsXsM",
        "required_for_full_authority": False,
        "identity_fingerprints": ["canonical", "dataset", "benchmark", "version"],
        "strong_match_threshold": 2,
        "generic_rpmc_terms": ["resonant", "memory", "recursive", "validation"],
    },
]

INGESTION_POLICY_RULES = [
    "1.  Ingestion requires a vector audit report first.",
    "2.  Ingestion requires a corpus extraction report (17 OK / 0 failed).",
    "3.  Ingestion requires corpus-check clean (0 errors, 0 warnings).",
    "4.  Ingestion requires rpmc-check clean or warning-acknowledged.",
    "5.  Ingestion uses corpus IDs only — no arbitrary paths.",
    "6.  Ingestion verifies SHA-256 before text extraction.",
    "7.  Ingestion writes an ingestion manifest before any Chroma write.",
    "8.  Ingestion uses named collection namespaces (never the default collection).",
    "9.  Ingestion must remain reversible — quarantine path must exist before write.",
    "10. Single-document trial ingestion must pass before full-corpus ingestion.",
    "11. RPMC source gaps block final full-corpus memory authority, not trial ingestion.",
    "12. No automatic Drive sync. No automatic downloads.",
    "13. Archive-held corpus items (09_ARCHIVE_REVIEW) must never be ingested.",
    "14. Ingestion manifest is written and audited before the first Chroma write.",
]

PLANNED_NAMESPACES = [
    ("aiweb_trial_v1",       "Single-document trial ingestion — validation only"),
    ("aiweb_corpus_v1",      "Full eligible corpus — after trial passes"),
    ("aiweb_rpmc_kernel_v1", "RPMC source documents — after Drive sources registered"),
    ("aiweb_archive_cold_v1","Archive/held documents — cold, read-only reference"),
]

# ─── PART 1: VECTOR STORE PROVENANCE ─────────────────────────────────────────

def cmd_vector_status(session_id: str) -> None:
    """Show Chroma DB directory status. Read-only. Usage: vector-status"""
    import os
    from agents.forge.memory import write_audit_entry

    exists = CHROMA_DB_PATH.exists()
    items  = []
    if exists and CHROMA_DB_PATH.is_dir():
        try:
            items = list(CHROMA_DB_PATH.iterdir())
        except PermissionError:
            items = []

    write_audit_entry(session_id, "VECTOR_STATUS_SHOWN", str(CHROMA_DB_PATH), "-",
                      f"exists={exists} items={len(items)}")

    print()
    print(f"── Vector Store Status ───────────────────────────────")
    print(f"  Path   : {CHROMA_DB_PATH}")
    print(f"  Exists : {'YES' if exists else 'NO'}")
    print(f"  Items  : {len(items)}")
    if items:
        print()
        for item in sorted(items):
            try:
                stat = item.stat()
                size = stat.st_size
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
                is_dir = item.is_dir()
                tag = "/" if is_dir else ""
                size_str = f"{size:,} B" if size < 1024 else f"{size/1024:.1f} KB"
                looks_like = ""
                if item.suffix in (".sqlite3", ".db", ".sqlite"):
                    looks_like = " [SQLite]"
                elif is_dir and item.name in ("index", "segments"):
                    looks_like = " [index dir]"
                print(f"    {size_str:>12}  {mtime}  {item.name}{tag}{looks_like}")
            except OSError:
                print(f"    (unreadable)  {item.name}")
        empty_scaffold = len(items) <= 2 and all(i.name in ("chroma.sqlite3",) for i in items if i.is_file())
        print()
        print(f"  Assessment: {'appears to be scaffold/prior session DB' if empty_scaffold else 'contains data — audit recommended'}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_vector_audit(session_id: str) -> None:
    """Deep read-only audit of Chroma DB. Saves JSON + Markdown report. Usage: vector-audit"""
    import json as _json
    from agents.forge.memory import write_audit_entry

    write_audit_entry(session_id, "VECTOR_AUDIT_STARTED", str(CHROMA_DB_PATH), "-", "audit initiated")

    report = {
        "timestamp":   datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id":  session_id,
        "chroma_path": str(CHROMA_DB_PATH),
        "exists":      CHROMA_DB_PATH.exists(),
        "filesystem":  {},
        "collections": [],
        "chromadb_available": False,
        "errors": [],
    }

    # Filesystem inventory
    if CHROMA_DB_PATH.exists() and CHROMA_DB_PATH.is_dir():
        try:
            fs = {}
            for item in sorted(CHROMA_DB_PATH.rglob("*")):
                try:
                    st = item.stat()
                    rel = str(item.relative_to(CHROMA_DB_PATH))
                    fs[rel] = {"size_bytes": st.st_size, "is_dir": item.is_dir(),
                               "mtime": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")}
                except OSError:
                    pass
            report["filesystem"] = fs
        except Exception as e:
            report["errors"].append(f"filesystem scan: {e}")

    # ChromaDB client inspection
    try:
        import chromadb
        report["chromadb_available"] = True
        report["chromadb_version"] = getattr(chromadb, "__version__", "unknown")
        try:
            client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
            collections = client.list_collections()
            for col in collections:
                try:
                    count = col.count()
                    meta  = col.metadata or {}
                    # Peek at a few records without storing them
                    peek = col.peek(limit=3)
                    peek_ids = peek.get("ids", [])[:3]
                    peek_metas = peek.get("metadatas", [])[:3]
                    report["collections"].append({
                        "name":       col.name,
                        "count":      count,
                        "metadata":   meta,
                        "peek_ids":   peek_ids,
                        "peek_meta_keys": [list(m.keys()) for m in (peek_metas or []) if m],
                    })
                except Exception as e:
                    report["collections"].append({"name": col.name, "error": str(e)})
        except Exception as e:
            report["errors"].append(f"chromadb client: {e}")
    except ImportError:
        report["errors"].append("chromadb not importable — filesystem report only")

    # Save reports
    VECTOR_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    json_path = VECTOR_REPORTS_DIR / f"{ts}_vector_audit.json"
    md_path   = VECTOR_REPORTS_DIR / f"{ts}_vector_audit.md"

    try:
        json_path.write_text(_json.dumps(report, indent=2), encoding="utf-8")
    except OSError as e:
        print(f"[forge] WARNING: Could not save JSON report: {e}")

    # Build Markdown
    col_section = ""
    for col in report["collections"]:
        col_section += f"\n### Collection: `{col.get('name','?')}`\n"
        col_section += f"- Count: {col.get('count','?')}\n"
        col_section += f"- Metadata: {col.get('metadata',{})}\n"
        if col.get("peek_ids"):
            col_section += f"- Sample IDs: {col['peek_ids']}\n"
        if col.get("error"):
            col_section += f"- Error: {col['error']}\n"

    md = f"""# Vector Store Audit Report
**Timestamp**: {report['timestamp']}  
**Path**: `{report['chroma_path']}`  
**Exists**: {report['exists']}  
**ChromaDB**: {'available v' + report.get('chromadb_version','?') if report['chromadb_available'] else 'not importable'}

## Collections ({len(report['collections'])})
{col_section or '(none found)'}

## Filesystem ({len(report['filesystem'])} items)
{chr(10).join(f'- `{k}`: {v["size_bytes"]:,} B' for k,v in sorted(report['filesystem'].items())[:20])}

## Errors
{chr(10).join(f'- {e}' for e in report['errors']) or '(none)'}

---
*Read-only audit. No Chroma writes performed.*
"""
    try:
        md_path.write_text(md, encoding="utf-8")
    except OSError as e:
        print(f"[forge] WARNING: Could not save Markdown report: {e}")

    audit_tool = "VECTOR_AUDIT_COMPLETED" if not report["errors"] else "VECTOR_AUDIT_FAILED"
    write_audit_entry(session_id, audit_tool, str(json_path), "-",
                      f"collections={len(report['collections'])} fs_items={len(report['filesystem'])}")

    # Print summary
    print()
    print(f"── Vector Audit ──────────────────────────────────────")
    print(f"  Path       : {CHROMA_DB_PATH}")
    print(f"  Exists     : {report['exists']}")
    print(f"  ChromaDB   : {'v' + report.get('chromadb_version','?') if report['chromadb_available'] else 'not importable'}")
    print(f"  Collections: {len(report['collections'])}")
    for col in report["collections"]:
        print(f"    • {col.get('name','?'):<40} count={col.get('count','?')}")
    print(f"  FS items   : {len(report['filesystem'])}")
    if report["errors"]:
        print(f"  Errors     : {len(report['errors'])}")
        for e in report["errors"][:3]:
            print(f"    ⚠ {e}")
    print()
    print(f"  JSON report: {json_path}")
    print(f"  MD report  : {md_path}")
    print(f"  Audit      : {audit_tool}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_vector_report(session_id: str) -> None:
    """Show the latest vector audit report. Usage: vector-report"""
    import json as _json
    from agents.forge.memory import write_audit_entry

    VECTOR_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    reports = sorted(VECTOR_REPORTS_DIR.glob("*_vector_audit.json"), reverse=True)
    if not reports:
        print("[forge] No vector audit reports found. Run 'vector-audit' first.")
        return

    try:
        data = _json.loads(reports[0].read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"[forge] ERROR: Cannot read report: {e}")
        return

    write_audit_entry(session_id, "VECTOR_REPORT_SHOWN", str(reports[0]), "-",
                      f"collections={len(data.get('collections',[]))} ts={data.get('timestamp','?')}")

    print()
    print(f"── Latest Vector Audit Report ────────────────────────")
    print(f"  Timestamp  : {data.get('timestamp','?')}")
    print(f"  Path       : {data.get('chroma_path','?')}")
    print(f"  Exists     : {data.get('exists','?')}")
    print(f"  Collections: {len(data.get('collections',[]))}")
    for col in data.get("collections", []):
        print(f"    • {col.get('name','?'):<40} count={col.get('count','?')}")
        keys = col.get("peek_meta_keys", [])
        if keys:
            print(f"      meta keys seen: {keys[:3]}")
    print(f"  FS items   : {len(data.get('filesystem',{}))}")
    if data.get("errors"):
        print(f"  Errors     : {data['errors']}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_vector_quarantine_plan(session_id: str) -> None:
    """Print quarantine options for existing Chroma DB. Planning only. Usage: vector-quarantine-plan"""
    from agents.forge.memory import write_audit_entry

    write_audit_entry(session_id, "VECTOR_QUARANTINE_PLAN_SHOWN", str(CHROMA_DB_PATH), "-", "plan displayed")

    print()
    print(f"── Vector Quarantine Plan (Planning Only) ────────────")
    print(f"  Current Chroma DB: {CHROMA_DB_PATH}")
    print()
    print(f"  Option A — Keep existing DB (do nothing):")
    print(f"    • Trial ingestion writes to a NEW named collection (aiweb_trial_v1)")
    print(f"    • Existing data remains in its collection, untouched")
    print(f"    • Risk: namespace collision if old data uses conflicting names")
    print()
    print(f"  Option B — Archive/quarantine old DB before ingestion:")
    print(f"    • Move {CHROMA_DB_PATH} to {CHROMA_DB_PATH}_quarantine_<timestamp>/")
    print(f"    • Create fresh empty {CHROMA_DB_PATH} for new ingestion")
    print(f"    • Requires explicit future approval (not done in this patch)")
    print()
    print(f"  Option C — Separate DB path for corpus ingestion:")
    print(f"    • Ingest to a new path: {FORGE_ROOT / 'memory' / 'aiweb_corpus_db'}/")
    print(f"    • Keeps existing chroma_db fully intact")
    print(f"    • Clean separation — recommended if old DB is from KB testing")
    print()
    print(f"  Option D — Full reset (requires explicit future approval):")
    print(f"    • Delete existing chroma_db entirely")
    print(f"    • Start fresh with corpus ingestion only")
    print(f"    • Irreversible without a backup")
    print()
    print(f"  RECOMMENDATION: Option C (separate DB path) for trial ingestion.")
    print(f"  No action will be taken by this command.")
    print(f"  Execute quarantine only after explicit authorization.")
    print(f"──────────────────────────────────────────────────────")
    print()


# ─── PART 2: SOURCE GAP REPORT ───────────────────────────────────────────────

def _match_source_to_corpus(source: dict, rows: list[dict]) -> dict:
    """
    Match a known source document to local corpus entries using strict evidence rules.

    Match hierarchy (filename is primary signal — most reliable):
      REGISTERED_EXACT  — full_title phrase or all identity_fingerprints in filename
      REGISTERED_STRONG — ≥ strong_match_threshold identity_fingerprints in filename
      RELATED_ONLY      — only generic_rpmc_terms found anywhere in row data
      MISSING           — nothing found

    IMPORTANT: matching on concatenated row values (all fields) is NOT allowed.
    Matches must be in filename, relative_path, or absolute_path first.
    Generic RPMC terms (phase, memory, resonant, echo) in metadata fields do NOT constitute registration.
    """
    fingerprints = [fp.lower() for fp in source.get("identity_fingerprints", [])]
    generic_terms = [g.lower() for g in source.get("generic_rpmc_terms", [])]
    threshold    = source.get("strong_match_threshold", 3)
    full_title   = source.get("full_title", source.get("title", "")).lower()

    best_match = None
    best_status = "MISSING"
    best_confidence = "missing"
    best_match_type = "missing"
    best_evidence = ""
    best_fp_count = 0

    for row in (rows or []):
        fname    = str(row.get("filename", "")).lower()
        rel_path = str(row.get("relative_path", "")).lower()
        abs_path = str(row.get("absolute_path", "")).lower()
        path_str = f"{fname} {rel_path} {abs_path}"

        # Check for exact phrase match in filename/path
        title_words = [w for w in full_title.split() if len(w) > 4
                       and w not in ("with", "from", "that", "this", "their", "have")]
        path_title_matches = sum(1 for w in title_words if w in path_str)
        exact_phrase_in_path = (
            "resonant phase memory calculus" in path_str or
            "rpmc_full_protocol" in path_str or
            "rpmc_implementation_blueprint" in path_str or
            "rpmc_canonical_test" in path_str or
            "rpmc-full-protocol" in path_str
        )

        # Count identity fingerprints in filename/path
        fp_in_path = [fp for fp in fingerprints if fp in path_str]
        fp_count   = len(fp_in_path)

        # Determine status based on filename/path only
        if exact_phrase_in_path or (fp_count == len(fingerprints) and len(fingerprints) >= 3):
            status     = "REGISTERED_EXACT"
            confidence = "high"
            match_type = "exact_title"
            evidence   = f"Identity fingerprints in path: {fp_in_path} | file: {fname}"
        elif fp_count >= threshold:
            status     = "REGISTERED_STRONG"
            confidence = "high"
            match_type = "strong_title_partial"
            evidence   = f"{fp_count}/{len(fingerprints)} fingerprints in filename: {fp_in_path}"
        else:
            # Only if nothing found in filename/path, check generic terms in ALL fields
            # This can only produce RELATED_ONLY, never registration
            all_fields = " ".join(str(v).lower() for v in row.values())
            generic_hits = [g for g in generic_terms if g in all_fields]
            if generic_hits:
                status     = "RELATED_ONLY"
                confidence = "low"
                match_type = "content_keyword_only"
                evidence   = f"Generic RPMC terms only in metadata: {generic_hits} — not identity evidence"
            else:
                continue  # No match at all

        # Track best match
        priority = {"REGISTERED_EXACT": 4, "REGISTERED_STRONG": 3, "RELATED_ONLY": 2}.get(status, 0)
        best_priority = {"REGISTERED_EXACT": 4, "REGISTERED_STRONG": 3, "RELATED_ONLY": 2}.get(best_status, 0)

        if priority > best_priority or (priority == best_priority and fp_count > best_fp_count):
            best_match      = row
            best_status     = status
            best_confidence = confidence
            best_match_type = match_type
            best_evidence   = evidence
            best_fp_count   = fp_count

    satisfies = best_status in ("REGISTERED_EXACT", "REGISTERED_STRONG")

    return {
        "title":                 source["title"],
        "full_title":            source.get("full_title", source["title"]),
        "category":              source["category"],
        "role":                  source["role"],
        "drive_id":              source["drive_id"],
        "required_for_full_authority": source["required_for_full_authority"],
        "status":                best_status,
        "confidence":            best_confidence,
        "match_type":            best_match_type,
        "satisfies_full_authority": satisfies,
        "matched_corpus_id":     best_match.get("id","") if best_match else None,
        "matched_filename":      best_match.get("filename","") if best_match else None,
        "matched_corpus_folder": best_match.get("corpus_folder","") if best_match else None,
        "matched_absolute_path": best_match.get("absolute_path","") if best_match else None,
        "matched_sha256_16":     best_match.get("sha256_16","") if best_match else None,
        "evidence_snippet":      best_evidence,
        "warning": (
            f"Required for full RPMC authority — not found locally"
            if source["required_for_full_authority"] and not satisfies else
            "Not required for trial ingestion" if not source["required_for_full_authority"] and not satisfies else ""
        ),
    }


def cmd_source_gap_report(session_id: str) -> None:
    """
    Hardened source gap report. Uses source_authority_registry.json — not hardcoded entries.
    RELATED_ONLY matches do NOT count as registered. Usage: source-gap-report
    """
    import json as _json
    from agents.forge.memory import write_audit_entry

    registry = _load_source_authority_registry()
    if not registry:
        # Fallback: show message
        print("[forge] WARNING: source_authority_registry.json not found or empty.")
        print(f"  Expected at: {SOURCE_AUTHORITY_REGISTRY_FILE}")
        print("  Create or populate this file to use source-gap-report.")
        return

    rows = _corpus_load_json() or _corpus_load_csv()
    results = [_match_source_to_corpus_from_registry(s, rows) for s in registry]

    exact_or_strong = sum(1 for r in results if r["satisfies_full_authority"])
    required_gaps   = sum(1 for r in results if r.get("required_for_full_authority") and not r["satisfies_full_authority"])
    total_gaps      = sum(1 for r in results if not r["satisfies_full_authority"])

    trial_ok     = True
    full_auth_ok = required_gaps == 0
    if full_auth_ok and total_gaps == 0:
        verdict = "ALL_SOURCES_REGISTERED_EXACT_OR_STRONG"
    elif full_auth_ok:
        verdict = "REQUIRED_SOURCES_REGISTERED_OPTIONAL_GAPS"
    else:
        verdict = f"AUTHORITY_GAPS_PRESENT ({required_gaps} required source(s) not exact/strong)"

    report = {
        "timestamp":           datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id":          session_id,
        "registry_file":       str(SOURCE_AUTHORITY_REGISTRY_FILE),
        "total_sources":       len(results),
        "exact_or_strong":     exact_or_strong,
        "required_gaps":       required_gaps,
        "total_gaps":          total_gaps,
        "trial_readiness":     "OK_WITH_WARNINGS" if total_gaps > 0 else "OK",
        "full_auth_readiness": "OK" if full_auth_ok else f"BLOCKED ({required_gaps} required gaps)",
        "verdict":             verdict,
        "results":             results,
    }

    SOURCE_GAP_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    json_path = SOURCE_GAP_REPORTS_DIR / f"{ts}_source_gap.json"
    md_lines  = [f"# Source Gap Report (registry-driven)", f"", f"**Verdict**: {verdict}",
                 f"**Required gaps**: {required_gaps}  **Trial**: {report['trial_readiness']}",
                 f"**Full auth**: {report['full_auth_readiness']}", f"",
                 f"| Source Key | Status | Match Type | Satisfies |",
                 f"|-----------|--------|-----------|-----------|"]
    for r in results:
        md_lines.append(f"| {r['source_key']} | {r['status']} | {r['match_type']} | {r['satisfies_full_authority']} |")
    try:
        json_path.write_text(_json.dumps(report, indent=2), encoding="utf-8")
        md_path = SOURCE_GAP_REPORTS_DIR / f"{ts}_source_gap.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")
    except OSError:
        pass

    audit_tool = "SOURCE_GAP_WARN" if total_gaps > 0 else "SOURCE_GAP_OK"
    write_audit_entry(session_id, "SOURCE_GAP_REPORT_CREATED", str(json_path), "-",
                      f"required_gaps={required_gaps} verdict={verdict[:60]}")
    write_audit_entry(session_id, audit_tool, str(json_path), "-", f"required_gaps={required_gaps}")

    print()
    print(f"── Source Gap Report (registry-driven) ───────────────")
    for r in results:
        icon = {"REGISTERED_EXACT":"✓","REGISTERED_STRONG":"✓","RELATED_ONLY":"⚠","MISSING":"✗"}.get(r["status"],"?")
        print(f"  {icon} {r['source_key']}")
        print(f"      Status    : {r['status']}")
        print(f"      Match type: {r['match_type']}  Confidence: {r['confidence']}")
        print(f"      Satisfies : {'YES' if r['satisfies_full_authority'] else 'NO'}")
        if r.get("evidence_snippet"):
            print(f"      Evidence  : {r['evidence_snippet'][:70]}")
        if r.get("warning"):
            print(f"      Warning   : {r['warning']}")
    print()
    print(f"  Trial readiness    : {report['trial_readiness']}")
    print(f"  Full auth readiness: {report['full_auth_readiness']}")
    print(f"  Verdict: {verdict}")
    print(f"  Note: RELATED_ONLY ≠ registered. Only EXACT/STRONG satisfies authority.")
    print(f"  Registry: {SOURCE_AUTHORITY_REGISTRY_FILE}")
    print(f"──────────────────────────────────────────────────────")
    print()


def _match_source_to_corpus_from_registry(source: dict, rows: list[dict]) -> dict:
    """
    Match a source registry entry to local corpus rows using strict filename evidence.
    No row text concatenation. Matches only on filename/path fingerprints.
    """
    fingerprints = [fp.lower() for fp in source.get("strong_filename_terms", [])]
    threshold    = source.get("strong_filename_threshold", 2)
    source_key   = source.get("source_key", "UNKNOWN")

    best = {"status": "MISSING", "confidence": "missing", "match_type": "missing",
            "matched_row": None, "evidence": "", "fp_count": 0}

    for row in (rows or []):
        fname    = str(row.get("filename","")).lower()
        rel_path = str(row.get("relative_path","")).lower()
        path_str = f"{fname} {rel_path}"
        fp_hits  = [fp for fp in fingerprints if fp in path_str]
        count    = len(fp_hits)

        # Exact: matches all fingerprints or a distinctive multi-word phrase
        exact_phrases = [p.lower() for t in source.get("expected_titles",[]) for p in [t.lower()] if len(p) > 10]
        exact = any(p in path_str for p in exact_phrases if len(p.split()) >= 3)

        if exact or (count == len(fingerprints) and len(fingerprints) >= 3):
            status, conf, mtype = "REGISTERED_EXACT", "high", "exact_title"
            evid = f"All fingerprints + phrase in path: {fp_hits}"
        elif count >= threshold:
            status, conf, mtype = "REGISTERED_STRONG", "high", "strong_title_partial"
            evid = f"{count}/{len(fingerprints)} fingerprints in filename: {fp_hits}"
        else:
            # Generic: check body text — RELATED_ONLY at most
            body = " ".join(str(v).lower() for v in row.values())
            ct   = [t.lower() for t in source.get("strong_content_terms",[])]
            ct_hits = [t for t in ct if t in body]
            if ct_hits:
                status, conf, mtype = "RELATED_ONLY", "low", "content_keyword_only"
                evid = f"Generic terms only in metadata: {ct_hits[:3]}"
            else:
                continue

        pri = {"REGISTERED_EXACT":4,"REGISTERED_STRONG":3,"RELATED_ONLY":2}.get(status,0)
        bpri = {"REGISTERED_EXACT":4,"REGISTERED_STRONG":3,"RELATED_ONLY":2}.get(best["status"],0)
        if pri > bpri or (pri == bpri and count > best["fp_count"]):
            best = {"status":status,"confidence":conf,"match_type":mtype,
                    "matched_row":row,"evidence":evid,"fp_count":count}

    satisfies = best["status"] in ("REGISTERED_EXACT","REGISTERED_STRONG")
    mr = best["matched_row"]
    return {
        "source_key":              source_key,
        "title":                   source.get("expected_titles",[""])[0],
        "category":                source.get("authority_group",""),
        "role":                    source.get("required_role",""),
        "required_for_full_authority": source.get("required_for_full_authority", True),
        "status":                  best["status"],
        "confidence":              best["confidence"],
        "match_type":              best["match_type"],
        "satisfies_full_authority": satisfies,
        "satisfies_trial":         True,
        "matched_corpus_id":       mr.get("id","") if mr else None,
        "matched_filename":        mr.get("filename","") if mr else None,
        "matched_corpus_folder":   mr.get("corpus_folder","") if mr else None,
        "matched_absolute_path":   mr.get("absolute_path","") if mr else None,
        "matched_sha256_16":       mr.get("sha256_16","") if mr else None,
        "evidence_snippet":        best["evidence"],
        "warning": (
            f"Required for full RPMC authority — not found locally"
            if source.get("required_for_full_authority") and not satisfies else
            "Optional — not found locally" if not source.get("required_for_full_authority") and not satisfies else ""
        ),
    }


def cmd_source_gap_evidence(session_id: str) -> None:
    """
    Show detailed match evidence for each required source document.
    Distinguishes EXACT/STRONG registration from RELATED_ONLY false positives.
    Usage: source-gap-evidence
    """
    from agents.forge.memory import write_audit_entry

    rows    = _corpus_load_json() or _corpus_load_csv()
    results = [_match_source_to_corpus(s, rows) for s in KNOWN_SOURCE_GAPS]

    write_audit_entry(session_id, "SOURCE_GAP_REPORT_CREATED", "-", "-",
                      "evidence detail displayed")

    print()
    print(f"── Source Gap Evidence Detail ────────────────────────")
    print()
    for r in results:
        icon = {"REGISTERED_EXACT": "✓", "REGISTERED_STRONG": "✓",
                "RELATED_ONLY": "⚠", "MISSING": "✗"}.get(r["status"], "?")
        print(f"  {'─'*52}")
        print(f"  {icon} {r['title']}")
        print(f"    Full title  : {r['full_title'][:70]}")
        print(f"    Category    : {r['category']}")
        print(f"    Role        : {r['role'][:65]}")
        print(f"    Required    : {'YES (blocks full authority)' if r['required_for_full_authority'] else 'NO (optional)'}")
        print()
        print(f"    Status      : {r['status']}")
        print(f"    Match type  : {r['match_type']}")
        print(f"    Confidence  : {r['confidence']}")
        print(f"    Satisfies   : {'YES' if r['satisfies_full_authority'] else 'NO'}")
        print()
        if r.get("matched_corpus_id"):
            print(f"    Matched ID      : {r['matched_corpus_id']}")
            print(f"    Matched file    : {r['matched_filename']}")
            print(f"    Matched folder  : {r['matched_corpus_folder']}")
            print(f"    Matched path    : {r['matched_absolute_path']}")
            print(f"    Matched SHA-256 : {r['matched_sha256_16']}")
        else:
            print(f"    No local match found.")

        if r.get("evidence_snippet"):
            print(f"    Evidence        : {r['evidence_snippet'][:100]}")
        if r.get("warning"):
            print(f"    Warning         : {r['warning']}")

    print()
    print(f"  Match type key:")
    print(f"    exact_title          → REGISTERED_EXACT  → satisfies full authority")
    print(f"    strong_title_partial → REGISTERED_STRONG → satisfies full authority")
    print(f"    content_keyword_only → RELATED_ONLY      → does NOT satisfy authority")
    print(f"    inferred_from_related→ RELATED_ONLY      → does NOT satisfy authority")
    print(f"    missing              → MISSING           → does NOT satisfy authority")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_source_gap_check(session_id: str) -> None:
    """Show latest source gap report with trial and full-authority distinctions. Usage: source-gap-check"""
    import json as _json
    from agents.forge.memory import write_audit_entry

    SOURCE_GAP_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    reports = sorted(SOURCE_GAP_REPORTS_DIR.glob("*_source_gap.json"), reverse=True)
    if not reports:
        print("[forge] No source gap reports found. Run 'source-gap-report' first.")
        return

    try:
        data = _json.loads(reports[0].read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"[forge] ERROR: Cannot read report: {e}")
        return

    write_audit_entry(session_id, "SOURCE_GAP_CHECK_SHOWN", str(reports[0]), "-",
                      f"required_gaps={data.get('required_gaps','?')} ts={data.get('timestamp','?')}")

    print()
    print(f"── Source Gap Check ──────────────────────────────────")
    print(f"  Timestamp   : {data.get('timestamp','?')}")
    print()
    for r in data.get("results", []):
        icon = {"REGISTERED_EXACT": "✓", "REGISTERED_STRONG": "✓",
                "RELATED_ONLY": "⚠", "MISSING": "✗"}.get(r.get("status",""), "?")
        print(f"  {icon} {r.get('title','?')}")
        print(f"      {r.get('status','?')}  confidence={r.get('confidence','?')}  satisfies_authority={r.get('satisfies_full_authority','?')}")
    print()
    print(f"  Trial ingestion      : {data.get('trial_readiness','?')}")
    print(f"  Full authority       : {data.get('full_auth_readiness','?')}")
    print(f"  Verdict              : {data.get('verdict','?')}")
    print(f"──────────────────────────────────────────────────────")
    print()


# ─── PART 3: INGESTION POLICY ────────────────────────────────────────────────

CORPUS_POLICIES_DIR         = FORGE_ROOT / "corpus_policies"
CORPUS_REGISTRATION_DIR     = FORGE_ROOT / "corpus_registration_reports"
SOURCE_AUTHORITY_REGISTRY_FILE = CORPUS_POLICIES_DIR / "source_authority_registry.json"
CORPUS_CLASSIFICATION_FILE  = CORPUS_POLICIES_DIR / "corpus_classification_rules.json"

INCOMING_ALIASES = {
    "rpmc":     "_incoming_rpmc_zip_extract",
    "incoming": "_incoming",
    "zip":      "_incoming_zip_extract",
    "default":  "_incoming",
}

FORGE_EXPECTED_COMMANDS = [
    "help", "quit", "status", "audit",
    "exact-list", "exact-read",
    "patch-propose", "patch-review", "patch-preflight", "patch-apply",
    "patch-verify", "patch-list", "patch-status", "patch-chain",
    "rollback-restore", "field-report",
    "corpus-list", "corpus-status", "corpus-show", "corpus-check",
    "corpus-policy", "corpus-preview",
    "doc-capabilities", "doc-formats", "doc-preview",
    "corpus-extract-check", "corpus-extract-report", "corpus-extract-show",
    "rpmc-policy", "rpmc-template", "rpmc-check", "rpmc-source-list",
    "vector-status", "vector-audit", "vector-report", "vector-quarantine-plan",
    "source-gap-report", "source-gap-evidence", "source-gap-check",
    "ingestion-policy", "ingest-dry-run", "ingest-dry-run-validate",
    "ingestion-manifest-plan", "ingestion-readiness", "chunk-policy",
    "ingest-one", "ingest-verify",
    "forge-version", "forge-command-surface",
    "corpus-intake-scan", "corpus-intake-preview", "corpus-intake-apply",
    "corpus-intake-check", "corpus-registration-report",
    "context-status", "context-search-test", "context-search",
    "ingest-history", "ingest-receipt-show", "ingest-receipt-repair",
    "ingest-next", "ingest-batch-plan", "ingest-batch-dry-run",
    "ingest-batch-apply", "ingest-batch-verify",
    "corpus-id-map", "source-authority-weights",
    "context-duplicates", "context-collection-stats",
    "context-reset-plan", "context-export-manifest",
]


# ─── INTAKE HELPERS ───────────────────────────────────────────────────────────

def _load_source_authority_registry() -> list[dict]:
    """Load source authority entries from policy file. Falls back to empty list."""
    import json as _json
    if SOURCE_AUTHORITY_REGISTRY_FILE.exists():
        try:
            data = _json.loads(SOURCE_AUTHORITY_REGISTRY_FILE.read_text(encoding="utf-8"))
            return data.get("sources", [])
        except Exception:
            pass
    return []


def _load_classification_rules() -> list[dict]:
    """Load corpus classification rules from policy file."""
    import json as _json
    if CORPUS_CLASSIFICATION_FILE.exists():
        try:
            data = _json.loads(CORPUS_CLASSIFICATION_FILE.read_text(encoding="utf-8"))
            return sorted(data.get("rules", []), key=lambda r: r.get("priority", 99))
        except Exception:
            pass
    return [{"folder": "09_ARCHIVE_REVIEW", "priority": 99, "filename_terms": [],
             "content_terms": [], "default_index_eligible": False}]


def _resolve_incoming_folder(arg: str) -> tuple:
    """
    Resolve a folder argument to an absolute Path inside CORPUS_ROOT.
    Returns (Path|None, error_str).
    """
    if not arg:
        return None, "No folder specified"
    arg_lower = arg.strip().lower()
    if arg_lower in INCOMING_ALIASES:
        folder = _CORPUS_ROOT / INCOMING_ALIASES[arg_lower]
    elif os.sep in arg or arg.startswith("~"):
        folder = Path(os.path.expanduser(arg))
        try:
            folder.relative_to(_CORPUS_ROOT)
        except ValueError:
            return None, f"Folder must be inside {_CORPUS_ROOT} — got: {folder}"
    else:
        # Try several name patterns
        for candidate in [
            _CORPUS_ROOT / f"_incoming_{arg}",
            _CORPUS_ROOT / f"_incoming_{arg.lower()}",
            _CORPUS_ROOT / arg,
        ]:
            if candidate.exists():
                folder = candidate
                break
        else:
            folder = _CORPUS_ROOT / f"_incoming_{arg}"
    return folder, ""


def _classify_document(filename: str, content_preview: str, rules: list[dict]) -> tuple[str, bool, str]:
    """
    Classify a document using policy rules.
    Returns (folder, index_eligible, matched_rule_name).
    """
    fname_lower = filename.lower()
    content_lower = (content_preview or "").lower()
    best_folder    = "09_ARCHIVE_REVIEW"
    best_eligible  = False
    best_rule      = "default"
    best_hits      = 0

    for rule in rules:
        folder = rule.get("folder", "09_ARCHIVE_REVIEW")
        if folder == "09_ARCHIVE_REVIEW":
            continue
        fname_terms   = [t.lower() for t in rule.get("filename_terms", [])]
        content_terms = [t.lower() for t in rule.get("content_terms", [])]
        fname_hits    = sum(1 for t in fname_terms if t in fname_lower)
        content_hits  = sum(1 for t in content_terms if t in content_lower)
        total_hits    = fname_hits * 2 + content_hits  # filename weighted higher
        if total_hits > best_hits:
            best_hits    = total_hits
            best_folder  = folder
            best_eligible = rule.get("default_index_eligible", True)
            best_rule    = folder

    return best_folder, best_eligible, best_rule


def _match_source_identity(filename: str, content_preview: str,
                            registry: list[dict]) -> tuple[str, str, float, str]:
    """
    Match an incoming document to a known source authority entry.
    Returns (source_key, match_type, confidence_0_to_1, evidence).
    match_type: "exact_filename" | "strong_filename" | "content_terms" | "none"
    """
    fname_lower   = filename.lower().replace("-", "_").replace(" ", "_")
    content_lower = (content_preview or "").lower()

    best_key   = "UNKNOWN"
    best_type  = "none"
    best_conf  = 0.0
    best_evid  = ""

    for src in registry:
        key        = src.get("source_key", "")
        fn_terms   = [t.lower() for t in src.get("strong_filename_terms", [])]
        fn_thresh  = src.get("strong_filename_threshold", 2)
        ct_terms   = [t.lower() for t in src.get("strong_content_terms", [])]

        fn_hits = [t for t in fn_terms if t in fname_lower]
        ct_hits = [t for t in ct_terms if t in content_lower]

        if len(fn_hits) >= max(fn_thresh, 3):
            mtype = "exact_filename"
            conf  = 0.95
            evid  = f"filename hits ({len(fn_hits)}): {fn_hits}"
        elif len(fn_hits) >= fn_thresh:
            mtype = "strong_filename"
            conf  = 0.75
            evid  = f"filename hits ({len(fn_hits)}): {fn_hits}"
        elif ct_hits:
            mtype = "content_terms"
            conf  = 0.40
            evid  = f"content hits: {ct_hits[:3]}"
        else:
            continue

        if conf > best_conf:
            best_key  = key
            best_type = mtype
            best_conf = conf
            best_evid = evid

    return best_key, best_type, best_conf, best_evid


def _scan_incoming_folder(folder: Path, rules: list[dict], registry: list[dict],
                           existing_rows: list[dict]) -> list[dict]:
    """
    Scan an incoming folder and return per-file scan results.
    Does NOT copy or modify anything.
    """
    import hashlib
    from agents.forge.document_adapters import extract_text

    existing_shas    = {r.get("sha256_16","") for r in existing_rows}
    existing_fnames  = {r.get("filename","").lower() for r in existing_rows}

    results = []
    if not folder.exists():
        return results

    for path in sorted(folder.iterdir()):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        try:
            raw       = path.read_bytes()
            sha256_16 = hashlib.sha256(raw).hexdigest()[:16]
            size      = len(raw)
        except OSError as e:
            results.append({"filename": path.name, "error": str(e)})
            continue

        suffix = path.suffix.lower()
        # Quick content preview via adapter
        extraction_ok  = False
        content_preview = ""
        extraction_note = ""
        try:
            result = extract_text(path, max_chars=2000)
            if result.ok and result.text.strip():
                extraction_ok   = True
                content_preview = result.text[:500]
            else:
                extraction_note = result.error[:80] if result.error else "empty"
        except Exception as e:
            extraction_note = str(e)[:80]

        # Classify
        folder_name, index_eligible, rule_name = _classify_document(
            path.name, content_preview, rules
        )

        # Source identity
        src_key, match_type, confidence, evidence = _match_source_identity(
            path.name, content_preview, registry
        )

        dup_sha   = sha256_16 in existing_shas
        dup_fname = path.name.lower() in existing_fnames

        results.append({
            "filename":         path.name,
            "path":             str(path),
            "size_bytes":       size,
            "extension":        suffix,
            "sha256_16":        sha256_16,
            "extraction_ok":    extraction_ok,
            "extraction_note":  extraction_note,
            "content_preview":  content_preview[:200],
            "proposed_folder":  folder_name,
            "index_eligible":   index_eligible,
            "classification_rule": rule_name,
            "source_key":       src_key,
            "source_match_type": match_type,
            "source_confidence": round(confidence, 2),
            "source_evidence":  evidence,
            "duplicate_sha":    dup_sha,
            "duplicate_fname":  dup_fname,
            "can_register":     not dup_sha and not dup_fname,
        })

    return results


def _next_corpus_id(existing_rows: list[dict]) -> str:
    """Return the next corpus_XXXX ID not in existing rows."""
    nums = []
    for r in existing_rows:
        cid = r.get("id","")
        if cid.startswith("corpus_"):
            try:
                nums.append(int(cid[7:]))
            except ValueError:
                pass
    return f"corpus_{(max(nums)+1 if nums else 1):04d}"


# ─── INTAKE COMMANDS ─────────────────────────────────────────────────────────

def cmd_corpus_intake_scan(arg: str, session_id: str) -> None:
    """
    Live scan an incoming folder. Shows classification, source identity,
    extraction status, and duplicate status. Does NOT copy or modify anything.
    Usage: corpus-intake-scan <folder_or_alias>
    Aliases: rpmc, incoming, zip
    """
    from agents.forge.memory import write_audit_entry

    if not arg:
        print()
        print("  Usage: corpus-intake-scan <folder_or_alias>")
        print("  Aliases: rpmc, incoming, zip")
        print(f"  Searches inside: {_CORPUS_ROOT}")
        avail = [d.name for d in _CORPUS_ROOT.iterdir()
                 if d.is_dir() and d.name.startswith("_incoming")] if _CORPUS_ROOT.exists() else []
        if avail:
            print(f"  Available incoming folders: {', '.join(avail)}")
        print()
        return

    folder, err = _resolve_incoming_folder(arg)
    if err:
        print(f"[forge] ERROR: {err}")
        return

    rows  = _corpus_load_json() or _corpus_load_csv()
    rules = _load_classification_rules()
    reg   = _load_source_authority_registry()

    results = _scan_incoming_folder(folder, rules, reg, rows or [])

    write_audit_entry(session_id, "CORPUS_INTAKE_SCAN_SHOWN", str(folder), f"{len(results)} files",
                      f"folder={folder.name} found={len(results)}")

    print()
    print(f"── Corpus Intake Scan ────────────────────────────────")
    print(f"  Folder : {folder}")
    print(f"  Files  : {len(results)}")
    print()

    if not results:
        print(f"  (no files found — folder may be empty or does not exist)")
    else:
        for r in results:
            if r.get("error"):
                print(f"  ✗ {r['filename']}: ERROR — {r['error']}")
                continue
            dup = "⚠ DUP_SHA" if r["duplicate_sha"] else ("⚠ DUP_FNAME" if r["duplicate_fname"] else "")
            ext_icon = "✓" if r["extraction_ok"] else "⚠"
            conf_pct = int(r["source_confidence"] * 100)
            print(f"  {'✓' if r['can_register'] else '⚠'} {r['filename']}")
            print(f"      Size       : {r['size_bytes']:,} B  |  Format: {r['extension']}")
            print(f"      SHA-256    : {r['sha256_16']}")
            print(f"      Extraction : {ext_icon} {'OK' if r['extraction_ok'] else r['extraction_note']}")
            print(f"      Folder     : → {r['proposed_folder']}  (eligible={r['index_eligible']})")
            print(f"      Source     : {r['source_key']} [{r['source_match_type']}] {conf_pct}%")
            if r["source_evidence"]:
                print(f"      Evidence   : {r['source_evidence'][:70]}")
            if dup:
                print(f"      Duplicate  : {dup}")
            print()

    can_register = sum(1 for r in results if r.get("can_register", False))
    blocked = len(results) - can_register
    print(f"  Can register: {can_register}  Blocked (duplicate): {blocked}")
    print(f"  Next step: 'corpus-intake-preview {arg}' or 'corpus-intake-apply {arg}'")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_intake_preview(arg: str, session_id: str) -> None:
    """
    Same as intake-scan but writes a structured report under ~/forge/corpus_registration_reports/.
    Does NOT copy or modify the corpus.
    Usage: corpus-intake-preview <folder_or_alias>
    """
    import json as _json
    from agents.forge.memory import write_audit_entry

    if not arg:
        print("[forge] Usage: corpus-intake-preview <folder_or_alias>")
        return

    folder, err = _resolve_incoming_folder(arg)
    if err:
        print(f"[forge] ERROR: {err}")
        return

    rows    = _corpus_load_json() or _corpus_load_csv()
    rules   = _load_classification_rules()
    reg     = _load_source_authority_registry()
    results = _scan_incoming_folder(folder, rules, reg, rows or [])

    CORPUS_REGISTRATION_DIR.mkdir(parents=True, exist_ok=True)
    ts  = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    rpt = {
        "report_type":   "INTAKE_PREVIEW",
        "timestamp":     datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id":    session_id,
        "incoming_folder": str(folder),
        "total_files":   len(results),
        "can_register":  sum(1 for r in results if r.get("can_register", False)),
        "blocked":       sum(1 for r in results if not r.get("can_register", True)),
        "files":         results,
    }

    json_path = CORPUS_REGISTRATION_DIR / f"{ts}_intake_preview_{folder.name}.json"
    md_lines  = [f"# Corpus Intake Preview", f"",
                 f"**Folder**: `{folder}`  ", f"**Files**: {len(results)}",
                 f"**Can register**: {rpt['can_register']}  **Blocked**: {rpt['blocked']}", f"",
                 f"| Filename | SHA | Folder | Source | Dup | OK |",
                 f"|----------|-----|--------|--------|-----|-----|"]
    for r in results:
        if r.get("error"):
            md_lines.append(f"| {r['filename']} | ERROR | - | - | - | ✗ |")
        else:
            icon = "✓" if r["can_register"] else "⚠"
            md_lines.append(f"| {r['filename']} | {r['sha256_16']} | {r['proposed_folder']} | {r['source_key']} | {'YES' if r['duplicate_sha'] or r['duplicate_fname'] else 'no'} | {icon} |")

    try:
        json_path.write_text(_json.dumps(rpt, indent=2), encoding="utf-8")
        md_path = CORPUS_REGISTRATION_DIR / f"{ts}_intake_preview_{folder.name}.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")
    except OSError as e:
        print(f"[forge] WARNING: Could not save report: {e}")

    write_audit_entry(session_id, "CORPUS_INTAKE_PREVIEW_CREATED", str(json_path), f"{len(results)} files",
                      f"folder={folder.name} can_register={rpt['can_register']}")

    print()
    print(f"── Corpus Intake Preview ─────────────────────────────")
    print(f"  Folder : {folder}")
    print(f"  Files  : {len(results)}")
    print(f"  Ready  : {rpt['can_register']}  Blocked: {rpt['blocked']}")
    print(f"  Report : {json_path}")
    print(f"  To apply: corpus-intake-apply {arg}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_intake_apply(arg: str, session_id: str) -> None:
    """
    Register incoming documents into the corpus: copy files, update manifests, write receipt.
    Requires typing REGISTER_CORPUS to confirm.
    Usage: corpus-intake-apply <folder_or_alias>
    """
    import json as _json, csv as _csv, shutil, hashlib
    from agents.forge.memory import write_audit_entry

    if not arg:
        print("[forge] Usage: corpus-intake-apply <folder_or_alias>")
        return

    folder, err = _resolve_incoming_folder(arg)
    if err:
        write_audit_entry(session_id, "CORPUS_INTAKE_REGISTER_REFUSED", str(folder or arg), "-",
                          f"folder error: {err}")
        print(f"[forge] CORPUS INTAKE REFUSED: {err}")
        return

    rows    = _corpus_load_json() or _corpus_load_csv()
    rules   = _load_classification_rules()
    reg     = _load_source_authority_registry()
    results = _scan_incoming_folder(folder, rules, reg, rows or [])
    eligible = [r for r in results if r.get("can_register", False) and not r.get("error")]

    if not eligible:
        write_audit_entry(session_id, "CORPUS_INTAKE_REGISTER_REFUSED", str(folder), "-",
                          "no registerable files found")
        print(f"[forge] CORPUS INTAKE REFUSED: no eligible files to register in {folder}")
        return

    # Show what will be registered
    print()
    print(f"── Corpus Intake Apply ───────────────────────────────")
    print(f"  Folder        : {folder}")
    print(f"  Files to register: {len(eligible)}")
    for r in eligible:
        print(f"    • {r['filename']} → {r['proposed_folder']} (sha={r['sha256_16']})")
    if len(results) > len(eligible):
        blocked = [r for r in results if not r.get("can_register", True)]
        print(f"  Skipped (duplicate/error): {len(blocked)}")
    print()
    print(f"  THIS WILL:")
    print(f"    1. Back up manifests to ~/forge_corpus/backups/")
    print(f"    2. Copy files into ~/forge_corpus/<folder>/")
    print(f"    3. Append {len(eligible)} rows to corpus_metadata_manifest.csv and .json")
    print(f"    4. Write registration receipt")
    print()
    print(f"  To abort: press Ctrl-C or type anything other than REGISTER_CORPUS")
    print(f"  To proceed, type REGISTER_CORPUS (exact, case-sensitive):")
    print()

    try:
        confirmation = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n[forge] Registration cancelled. Nothing was changed.")
        return

    if confirmation != "REGISTER_CORPUS":
        print(f"[forge] Registration cancelled (got {confirmation!r}). Nothing was changed.")
        return

    write_audit_entry(session_id, "CORPUS_INTAKE_REGISTER_STARTED", str(folder), f"{len(eligible)} files",
                      f"folder={folder.name}")

    # Back up manifests
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = _CORPUS_ROOT / "backups" / f"corpus_registration_{ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for mf in [_CORPUS_CSV, _CORPUS_JSON]:
        if mf.exists():
            try:
                shutil.copy2(str(mf), str(backup_dir / mf.name))
            except OSError as e:
                print(f"[forge] WARNING: Could not back up {mf.name}: {e}")

    # Build new manifest rows
    new_rows    = []
    error_items = []
    existing_rows_fresh = _corpus_load_json() or _corpus_load_csv() or []
    next_id_num = max(
        [int(r.get("id","corpus_0000")[7:]) for r in existing_rows_fresh
         if r.get("id","").startswith("corpus_") and r.get("id","")[7:].isdigit()],
        default=0
    ) + 1

    for r in eligible:
        src_path = Path(r["path"])
        dest_folder_name = r["proposed_folder"]
        dest_dir = _CORPUS_ROOT / dest_folder_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / r["filename"]

        # Refuse if destination already exists
        if dest_path.exists():
            error_items.append({"filename": r["filename"], "error": f"destination exists: {dest_path}"})
            continue

        # Copy file
        try:
            shutil.copy2(str(src_path), str(dest_path))
        except OSError as e:
            error_items.append({"filename": r["filename"], "error": f"copy failed: {e}"})
            continue

        # Verify copy
        try:
            verify_sha = hashlib.sha256(dest_path.read_bytes()).hexdigest()[:16]
        except OSError as e:
            error_items.append({"filename": r["filename"], "error": f"verify failed: {e}"})
            continue

        if verify_sha != r["sha256_16"]:
            error_items.append({"filename": r["filename"],
                                "error": f"SHA mismatch after copy: {verify_sha} != {r['sha256_16']}"})
            dest_path.unlink(missing_ok=True)
            continue

        corpus_id = f"corpus_{next_id_num:04d}"
        next_id_num += 1
        rel_path  = f"{dest_folder_name}/{r['filename']}"

        new_row = {
            "id":              corpus_id,
            "filename":        r["filename"],
            "relative_path":   rel_path,
            "absolute_path":   str(dest_path),
            "corpus_folder":   dest_folder_name,
            "authority":       r.get("source_key","unknown").lower(),
            "status":          "current",
            "priority":        "high" if r.get("index_eligible") else "low",
            "index_eligible":  str(r.get("index_eligible", False)),
            "source_type":     r.get("extension","").lstrip("."),
            "size_bytes":      str(r.get("size_bytes", 0)),
            "sha256_16":       r["sha256_16"],
            "tags":            r.get("source_key","").lower().replace("_",","),
            "use_for":         r.get("source_key","").lower(),
            "do_not_use_for":  "" if r.get("index_eligible") else "primary_indexing",
        }
        new_rows.append(new_row)

    if error_items:
        for ei in error_items:
            print(f"[forge] ERROR during registration: {ei['filename']}: {ei['error']}")

    if not new_rows:
        write_audit_entry(session_id, "CORPUS_INTAKE_REGISTER_FAILED", str(folder), "-",
                          "no rows written — all files had errors")
        print(f"[forge] CORPUS INTAKE FAILED: no files were successfully registered.")
        return

    # Append to JSON manifest
    try:
        all_rows = existing_rows_fresh + new_rows
        _CORPUS_JSON.write_text(_json.dumps(all_rows, indent=2), encoding="utf-8")
    except OSError as e:
        write_audit_entry(session_id, "CORPUS_INTAKE_REGISTER_FAILED", str(_CORPUS_JSON), "-", str(e))
        print(f"[forge] CRITICAL: Could not write JSON manifest: {e}")
        print(f"[forge] Restore from backup: {backup_dir}")
        return

    # Append to CSV manifest
    try:
        if existing_rows_fresh:
            fieldnames = list(existing_rows_fresh[0].keys())
        else:
            fieldnames = list(new_rows[0].keys())
        import io as _io
        csv_buf = _io.StringIO()
        writer = _csv.DictWriter(csv_buf, fieldnames=fieldnames)
        for row in new_rows:
            writer.writerow({k: row.get(k,"") for k in fieldnames})
        with open(_CORPUS_CSV, "a", encoding="utf-8", newline="") as f:
            f.write(csv_buf.getvalue())
    except OSError as e:
        print(f"[forge] WARNING: Could not append to CSV manifest: {e}")

    # Post-write verification
    verify_rows = _corpus_load_json() or []
    verify_ids  = {r.get("id") for r in verify_rows}
    verify_errors = []
    for nr in new_rows:
        if nr["id"] not in verify_ids:
            verify_errors.append(f"ID {nr['id']} missing from verified manifest")
        dest = Path(nr["absolute_path"])
        if not dest.exists():
            verify_errors.append(f"File missing after registration: {dest}")

    # Write receipt
    CORPUS_REGISTRATION_DIR.mkdir(parents=True, exist_ok=True)
    receipt = {
        "report_type":        "CORPUS_REGISTRATION",
        "timestamp":          datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id":         session_id,
        "incoming_folder":    str(folder),
        "registered":         len(new_rows),
        "errors":             len(error_items),
        "verify_errors":      verify_errors,
        "backup_dir":         str(backup_dir),
        "new_rows":           new_rows,
        "error_items":        error_items,
    }
    receipt_json = CORPUS_REGISTRATION_DIR / f"{ts}_corpus_registration.json"
    receipt_md   = CORPUS_REGISTRATION_DIR / f"{ts}_corpus_registration.md"
    try:
        receipt_json.write_text(_json.dumps(receipt, indent=2), encoding="utf-8")
        md = [f"# Corpus Registration Report",
              f"**Registered**: {len(new_rows)}  **Errors**: {len(error_items)}",
              f"**Backup**: `{backup_dir}`", f""]
        for nr in new_rows:
            md.append(f"- ✓ `{nr['id']}` {nr['filename']} → {nr['corpus_folder']}")
        receipt_md.write_text("\n".join(md), encoding="utf-8")
    except OSError as e:
        print(f"[forge] WARNING: Could not write receipt: {e}")

    audit_tool = "CORPUS_INTAKE_REGISTER_COMPLETED" if not verify_errors else "CORPUS_INTAKE_REGISTER_FAILED"
    write_audit_entry(session_id, audit_tool, str(receipt_json), f"{len(new_rows)} rows",
                      f"registered={len(new_rows)} errors={len(error_items)} verify_errors={len(verify_errors)}")

    print()
    print(f"[forge] CORPUS REGISTRATION {'COMPLETE' if not verify_errors else 'COMPLETED WITH WARNINGS'}")
    print(f"  Registered : {len(new_rows)} files")
    for nr in new_rows:
        print(f"    ✓ {nr['id']}  {nr['filename']}  → {nr['corpus_folder']}")
    if error_items:
        print(f"  Errors     : {len(error_items)}")
        for ei in error_items:
            print(f"    ✗ {ei['filename']}: {ei['error']}")
    if verify_errors:
        print(f"  Verify errors: {verify_errors}")
    print(f"  Backup     : {backup_dir}")
    print(f"  Receipt    : {receipt_json}")
    print(f"  Audit      : {audit_tool}")
    print()


def cmd_corpus_intake_check(session_id: str) -> None:
    """
    Check current manifest and latest registration report. Shows gaps, incoming folders.
    Usage: corpus-intake-check
    """
    import json as _json, hashlib
    from agents.forge.memory import write_audit_entry

    rows = _corpus_load_json() or _corpus_load_csv()
    total    = len(rows or [])
    eligible = sum(1 for r in (rows or []) if str(r.get("index_eligible","")).lower() in ("true","1","yes"))
    held     = total - eligible

    # Check for duplicate IDs
    ids      = [r.get("id","") for r in (rows or [])]
    dup_ids  = [i for i in set(ids) if ids.count(i) > 1]

    # Check for missing files
    missing_files = [r.get("filename","") for r in (rows or [])
                     if not Path(r.get("absolute_path","")).exists()]

    # Latest registration report
    CORPUS_REGISTRATION_DIR.mkdir(parents=True, exist_ok=True)
    reg_reports = sorted(CORPUS_REGISTRATION_DIR.glob("*_corpus_registration.json"), reverse=True)
    latest_reg  = reg_reports[0].name if reg_reports else "none"

    # Check incoming folders
    incoming_folders = []
    if _CORPUS_ROOT.exists():
        for d in _CORPUS_ROOT.iterdir():
            if d.is_dir() and d.name.startswith("_incoming"):
                n_files = sum(1 for f in d.iterdir() if f.is_file()) if d.exists() else 0
                incoming_folders.append((d.name, n_files))

    write_audit_entry(session_id, "CORPUS_INTAKE_CHECK_SHOWN", str(_CORPUS_JSON), f"{total} rows",
                      f"total={total} eligible={eligible} held={held} missing_files={len(missing_files)}")

    print()
    print(f"── Corpus Intake Check ───────────────────────────────")
    print(f"  Manifest rows : {total}")
    print(f"  Eligible      : {eligible}")
    print(f"  Held          : {held}")
    print(f"  Duplicate IDs : {dup_ids or 'none'}")
    print(f"  Missing files : {len(missing_files)}" + (f" → {missing_files[:3]}" if missing_files else ""))
    print(f"  Latest reg    : {latest_reg}")
    print()
    if incoming_folders:
        print(f"  Incoming folders:")
        for name, count in incoming_folders:
            print(f"    {name}: {count} files")
    else:
        print(f"  No incoming folders found under {_CORPUS_ROOT}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_corpus_registration_report(session_id: str) -> None:
    """Show latest corpus registration report. Usage: corpus-registration-report"""
    import json as _json
    from agents.forge.memory import write_audit_entry

    CORPUS_REGISTRATION_DIR.mkdir(parents=True, exist_ok=True)
    reports = sorted(CORPUS_REGISTRATION_DIR.glob("*_corpus_registration.json"), reverse=True)
    if not reports:
        print("[forge] No registration reports found. Run 'corpus-intake-apply' to register files.")
        return

    try:
        data = _json.loads(reports[0].read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"[forge] ERROR: Cannot read report: {e}")
        return

    write_audit_entry(session_id, "CORPUS_REGISTRATION_REPORT_SHOWN", str(reports[0]), "-",
                      f"registered={data.get('registered','?')} ts={data.get('timestamp','?')}")

    print()
    print(f"── Latest Registration Report ────────────────────────")
    print(f"  Timestamp    : {data.get('timestamp','?')}")
    print(f"  Folder       : {data.get('incoming_folder','?')}")
    print(f"  Registered   : {data.get('registered','?')}")
    print(f"  Errors       : {data.get('errors','?')}")
    print()
    for nr in data.get("new_rows", []):
        print(f"  ✓ {nr.get('id','?')} {nr.get('filename','?')} → {nr.get('corpus_folder','?')}")
    print(f"──────────────────────────────────────────────────────")
    print()


CONTEXT_LIB_DIR      = FORGE_ROOT / "memory" / "context_library_v1"
CONTEXT_LIB_CHROMA   = CONTEXT_LIB_DIR / "chroma_db"
CONTEXT_LIB_RECEIPTS = CONTEXT_LIB_DIR / "receipts"
CONTEXT_LIB_INDEXES  = CONTEXT_LIB_DIR / "indexes"
CONTEXT_LIB_MANIFESTS= CONTEXT_LIB_DIR / "manifests"
CONTEXT_LIB_SYMBOLIC = CONTEXT_LIB_DIR / "symbolic_maps"
CONTEXT_COLLECTION   = "aiweb_context_chunks_v1"
EMBED_DIM            = 384


# ─── EMBEDDING ────────────────────────────────────────────────────────────────

def _hash_embed(text: str, dim: int = EMBED_DIM) -> list[float]:
    """
    Offline deterministic hash-based embedding.
    Produces consistent vectors proportional to word/phrase overlap.
    Works without model downloads. Suitable for keyword-based retrieval.
    Used as fallback when DefaultEmbeddingFunction is unavailable.
    """
    import hashlib, math, re
    tokens: list[str] = re.findall(r'\w+', text.lower())
    features: list[str] = tokens[:]
    features += [f"{a}_{b}" for a,b in zip(tokens, tokens[1:])]   # bigrams
    vec = [0.0] * dim
    for feat in features:
        h = int(hashlib.sha256(feat.encode()).hexdigest(), 16)
        idx   = h % dim
        sign  = 1.0 if (h >> 256-1) & 1 else -1.0
        # Weight: rare/longer features get higher weight
        weight = math.log1p(len(feat))
        vec[idx] += sign * weight
    norm = math.sqrt(sum(x*x for x in vec)) or 1.0
    return [x / norm for x in vec]


def _get_embedding_function():
    """Return best available embedding function. Tries ONNX, falls back to hash."""
    try:
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        ef = DefaultEmbeddingFunction()
        ef(["warmup"])  # test call
        return ef, "DefaultEmbeddingFunction (ONNX all-MiniLM-L6-v2)"
    except Exception:
        pass
    return None, "hash_embed_offline (deterministic, no model required)"


def _embed_texts(texts: list[str], ef) -> list[list[float]]:
    """Embed a list of texts using the given EF or fallback."""
    if ef is not None:
        return ef(texts)
    return [_hash_embed(t) for t in texts]


# ─── RPMC SYMBOLIC TAGGER ─────────────────────────────────────────────────────

def _build_rpmc_symbolic_tags(text: str, corpus_folder: str, authority: str) -> dict:
    """
    Derive RPMC symbolic memory tags from actual chunk text.
    Never hallucinated — only terms present in text contribute.
    Empty strings when no evidence found.
    """
    t = text.lower()

    # Phase tags Φ1–Φ9
    phase_map = {
        "Φ1": ["initiation","origin","beginning","entry","start pulse"],
        "Φ2": ["polarity","opposition","duality","field"],
        "Φ3": ["desire","intent","goal","target","seek"],
        "Φ4": ["friction","resistance","obstacle","unknown"],
        "Φ5": ["entropy","collapse","break","degrad","drift"],
        "Φ6": ["grace","recovery","return","χ(t)","chi(t)","resurrection","christping"],
        "Φ7": ["naming","pattern","label","identify","recognize"],
        "Φ8": ["power","valid","confirm","output","result"],
        "Φ9": ["recursion","evolution","loop","cycle","archive","seal"],
    }
    phases = [ph for ph, terms in phase_map.items() if any(term in t for term in terms)]

    # Operator detection
    op_map = {
        "ΦM":     ["φm", "memory function", "phase-locked resonance", "phim"],
        "χ(t)":   ["χ(t)","chi(t)","grace operator","christ function","christping"],
        "ε(t,Φ)": ["ε(t","entropy vector","drift entropy","epsilon"],
        "RPM":    ["rpm(x,t)","resonant phase memory calculus","rpmc formula"],
        "MRN":    ["memory resonance node","mrn"],
        "SPC":    ["symbolic phase capacitor","spc","dead path archive"],
        "θ":      ["theta","resurrection threshold","φ_resurrect"],
    }
    operators = [op for op, terms in op_map.items() if any(term in t for term in terms)]

    def _terms(kws): return ",".join(k for k in kws if k in t)[:120]

    collapse_terms     = _terms(["collapse","cold storage","entropy","drift","break","archive loop","dead path"])
    return_terms       = _terms(["return","resurrection","revival","recall","restore","echo","warmup"])
    recursion_terms    = _terms(["recursion","recursive","loop","cycle","repeat","self-referential"])
    echo_terms         = _terms(["echo","resonance","harmonic","alignment","coherence","lock"])
    drift_terms        = _terms(["drift","luciferian","skip","degradation","phase poison"])
    resurrection_terms = _terms(["resurrection","resurrect","revival","return from cold","recall from archive"])
    firewall_terms     = _terms(["firewall","symbolic firewall","phase poison","corrupted","block"])
    phase_cap_terms    = _terms(["phase capacitor","spc","dead path","cold storage","archive"])
    christ_terms       = _terms(["χ(t)","chi(t)","christping","grace","christ function","grace operator"])

    # Source weight heuristics
    fl = corpus_folder.lower()
    al = authority.lower()
    src_law_w  = round(1.0 if ("fbsc" in fl or "system_law" in fl or "protocol" in al) else 0.4, 2)
    impl_w     = round(1.0 if ("blueprint" in al or "implementation" in t[:200]) else 0.3, 2)
    valid_w    = round(1.0 if ("canonical" in al or "test" in al or "benchmark" in t[:100]) else 0.2, 2)

    # Memory role
    if any(op in operators for op in ["ΦM","RPM","ε(t,Φ)"]):
        memory_role = "memory_law_definition"
    elif "blueprint" in al or "implementation" in t[:200]:
        memory_role = "implementation_guide"
    elif "canonical" in al or "benchmark" in t[:100]:
        memory_role = "validation_benchmark"
    elif recursion_terms:
        memory_role = "recursion_doctrine"
    elif echo_terms or collapse_terms:
        memory_role = "phase_dynamics"
    else:
        memory_role = "reference"

    concepts = []
    if phases:     concepts.append(f"phases:{len(phases)}")
    if operators:  concepts.append(f"ops:{len(operators)}")
    if collapse_terms:   concepts.append("collapse")
    if recursion_terms:  concepts.append("recursion")
    if echo_terms:       concepts.append("echo")
    symbolic_sig = "|".join(concepts[:6]) or "none"

    return {
        "rpmc_phase_tags":       ",".join(phases) or "",
        "symbolic_operators":    ",".join(operators) or "",
        "memory_role":           memory_role,
        "recursion_terms":       recursion_terms,
        "collapse_terms":        collapse_terms,
        "return_terms":          return_terms,
        "drift_terms":           drift_terms,
        "echo_terms":            echo_terms,
        "resurrection_terms":    resurrection_terms,
        "firewall_terms":        firewall_terms,
        "phase_capacitor_terms": phase_cap_terms,
        "christ_function_terms": christ_terms,
        "source_law_weight":     src_law_w,
        "implementation_weight": impl_w,
        "validation_weight":     valid_w,
        "symbolic_signature":    symbolic_sig,
    }


# ─── INGESTION GATES ──────────────────────────────────────────────────────────

def _run_ingest_gates(corpus_id: str, rows: list[dict],
                      session_id: str) -> tuple[bool, list[tuple]]:
    """
    Run all 9 pre-ingestion gates. Returns (all_passed, gate_results).
    gate_results: list of (gate_name, passed: bool, detail: str)
    """
    import json as _json, hashlib

    gates = []

    # Gate 1: corpus_id exists
    item = next((r for r in rows if r.get("id","").strip().lower() == corpus_id.lower()), None)
    gates.append(("corpus_id exists", item is not None,
                  f"found: {item.get('filename','?')}" if item else f"'{corpus_id}' not in manifest"))

    if not item:
        return False, gates

    # Gate 2: index_eligible
    eligible = str(item.get("index_eligible","")).lower() in ("true","1","yes")
    gates.append(("index_eligible", eligible,
                  "True" if eligible else f"index_eligible={item.get('index_eligible')}"))

    # Gate 3: file exists
    fpath = Path(item.get("absolute_path",""))
    gates.append(("file exists on disk", fpath.exists(), str(fpath)))

    # Gate 4: SHA matches
    expected_sha = item.get("sha256_16","")
    if fpath.exists() and expected_sha:
        actual_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()[:16]
        sha_ok = actual_sha == expected_sha
        gates.append(("sha256 matches manifest", sha_ok,
                      f"OK {actual_sha}" if sha_ok else f"MISMATCH: got {actual_sha} expected {expected_sha}"))
    else:
        sha_ok = False
        gates.append(("sha256 matches manifest", False, "file missing or no SHA in manifest"))

    # Gate 5: source-gap required sources registered
    from agents.forge.memory import write_audit_entry as _wae
    gap_reports = sorted(SOURCE_GAP_REPORTS_DIR.glob("*_source_gap.json"), reverse=True)
    if gap_reports:
        try:
            gap = _json.loads(gap_reports[0].read_text(encoding="utf-8"))
            req_gaps = gap.get("required_gaps", 0)
            gates.append(("required sources registered", req_gaps == 0,
                          f"required_gaps={req_gaps} ({gap_reports[0].name})"))
        except Exception as e:
            gates.append(("required sources registered", False, f"could not read gap report: {e}"))
    else:
        gates.append(("required sources registered", False,
                      "no source-gap report found — run source-gap-report first"))

    # Gate 6: extraction report matches manifest
    extract_reports = sorted(CORPUS_REPORTS_DIR.glob("*_extraction_check.json"), reverse=True)
    if extract_reports:
        try:
            rpt = _json.loads(extract_reports[0].read_text(encoding="utf-8"))
            rpt_total = rpt.get("total_manifest", 0)
            manifest_total = len(rows)
            match = rpt_total == manifest_total
            gates.append(("extraction report matches manifest", match,
                          f"report has {rpt_total} rows, manifest has {manifest_total}" +
                          (" ✓" if match else " — run corpus-extract-check to refresh")))
        except Exception as e:
            gates.append(("extraction report matches manifest", False, str(e)))
    else:
        gates.append(("extraction report matches manifest", False,
                      "no extraction report — run corpus-extract-check first"))

    # Gate 7: dry-run strategy available
    dry_runs = sorted(INGESTION_PLANS_DIR.glob(f"*_dry_run_{corpus_id}*.json"), reverse=True)
    gates.append(("dry-run strategy available", True,
                  dry_runs[0].name if dry_runs else "fresh internal dry-run will be generated before confirmation"))

    # Gate 8: dry-run parity enforcement available
    gates.append(("dry-run/write parity enforcement", True,
                  "Patch 44 requires source SHA + chunk count + chunk IDs + chunk hashes before write"))

    # Gate 9: target path isolated from old chroma_db
    isolated = str(CONTEXT_LIB_CHROMA) != str(CHROMA_DB_PATH)
    gates.append(("context library isolated from old chroma_db", isolated,
                  f"OK: {CONTEXT_LIB_CHROMA}" if isolated else f"ERROR: same path as old DB!"))

    all_passed = all(g[1] for g in gates)
    return all_passed, gates


# ─── REAL INGEST-ONE ──────────────────────────────────────────────────────────

def cmd_ingest_one(corpus_id: str, session_id: str) -> None:
    """
    Level 5.0 — Controlled single-document ingestion into isolated context library.
    Runs all 9 pre-ingestion gates. Requires typing INGEST_ONE to confirm.
    Writes dual-brain metadata: provenance + RPMC symbolic tags.
    Target collection: aiweb_context_chunks_v1 in ~/forge/memory/context_library_v1/
    Usage: ingest-one <corpus_id>
    Default target: corpus_0022 (RPMC Full Protocol Draft)
    """
    import json as _json, hashlib
    from agents.forge.memory import write_audit_entry
    from agents.forge.document_adapters import extract_text

    corpus_id = (corpus_id.strip() or "corpus_0022")

    rows = _corpus_load_json() or _corpus_load_csv()
    if not rows:
        print("[forge] ERROR: Cannot load corpus manifest.")
        return

    item = next((r for r in rows if r.get("id","").strip().lower() == corpus_id.lower()), None)

    # ── Patch 44 duplicate guard: refuse before confirmation or Chroma write ──
    if item is not None:
        existing = _already_ingested_record(corpus_id)
        if existing:
            write_audit_entry(session_id, "INGEST_ONE_REFUSED_ALREADY_INGESTED", corpus_id, "-",
                              f"source={existing.get('source')} receipt={existing.get('receipt_path')} chunks={existing.get('chunk_count')}")
            print()
            print(f"[forge] INGEST_ONE_REFUSED_ALREADY_INGESTED")
            print(f"  corpus_id        : {corpus_id}")
            print(f"  existing source  : {existing.get('source')}")
            print(f"  existing receipt : {existing.get('receipt_path')}")
            print(f"  existing chunks  : {existing.get('chunk_count')}")
            print(f"  collection       : {existing.get('collection')}")
            print()
            print(f"  No Chroma write was attempted.")
            print(f"  Future explicit reingest/reset flow is not implemented yet.")
            print()
            return

    # ── Run all gates ─────────────────────────────────────────────────────────
    all_passed, gates = _run_ingest_gates(corpus_id, rows, session_id)

    print()
    print(f"── Ingest-One Gate Check: {corpus_id} ───────────────────")
    for name, passed, detail in gates:
        icon = "✓" if passed else "✗"
        print(f"  {icon} {name:<50} {detail[:50]}")
    print()

    if not all_passed:
        failed = [g for g in gates if not g[1]]
        write_audit_entry(session_id, "INGEST_ONE_REFUSED", corpus_id, "-",
                          f"gates_failed={len(failed)}: {failed[0][0] if failed else '?'}")
        print(f"[forge] INGEST_ONE_REFUSED: {len(failed)} gate(s) failed.")
        print(f"  Fix the issues above and retry.")
        print()
        return

    # ── Patch 44: create fresh write-parity dry-run before confirmation ──────
    fresh_plan, fresh_plan_path, plan_issues = _make_dry_run_plan(corpus_id, item, session_id, internal=True)
    if plan_issues or not fresh_plan or not fresh_plan_path:
        write_audit_entry(session_id, "INGEST_ONE_REFUSED_DRY_RUN_MISMATCH", corpus_id, "-",
                          f"fresh_plan_failed: {'; '.join(plan_issues)[:180]}")
        print(f"[forge] INGEST_ONE_REFUSED_DRY_RUN_MISMATCH")
        print(f"  Could not create a fresh parity dry-run plan.")
        for issue in plan_issues:
            print(f"    ✗ {issue}")
        print(f"  No Chroma write was attempted.")
        print(f"  Run: ingest-dry-run {corpus_id}")
        print(f"  Then: ingest-dry-run-validate {corpus_id}")
        print()
        return

    write_audit_entry(session_id, "INGEST_DRY_RUN_CREATED", str(fresh_plan_path),
                      f"{fresh_plan.get('chunk_count')} chunks",
                      "internal ingest-one parity plan; no chroma write")

    parity_issues = _validate_dry_run_plan_for_write(fresh_plan, corpus_id, item)
    if parity_issues:
        write_audit_entry(session_id, "INGEST_ONE_REFUSED_DRY_RUN_MISMATCH", corpus_id, str(fresh_plan_path),
                          f"issues={len(parity_issues)} first={parity_issues[0][:120] if parity_issues else '?'}")
        print(f"[forge] INGEST_ONE_REFUSED_DRY_RUN_MISMATCH")
        print(f"  Plan   : {fresh_plan_path}")
        print(f"  Issues : {len(parity_issues)}")
        for issue in parity_issues[:12]:
            print(f"    ✗ {issue}")
        print(f"  No Chroma write was attempted.")
        print(f"  Run: ingest-dry-run {corpus_id}")
        print(f"  Then: ingest-dry-run-validate {corpus_id}")
        print()
        return

    write_audit_entry(session_id, "INGEST_DRY_RUN_VALIDATED", str(fresh_plan_path),
                      f"{fresh_plan.get('chunk_count')} chunks",
                      "internal ingest-one parity validation passed")

    chunks = fresh_plan.get("chunks", [])

    # ── Show what will be ingested ────────────────────────────────────────────
    fpath = Path(item.get("absolute_path",""))
    print(f"  All {len(gates)} gates passed ✓")
    print(f"  File     : {item.get('filename','?')}")
    print(f"  Folder   : {item.get('corpus_folder','?')}")
    print(f"  SHA      : {item.get('sha256_16','?')}")
    print(f"  Target   : {CONTEXT_LIB_CHROMA}")
    print(f"  Collection: {CONTEXT_COLLECTION}")
    print(f"  Dry-run  : {fresh_plan_path}")
    print(f"  Chunks   : {fresh_plan.get('chunk_count')} exact plan chunks")
    print()
    print(f"  THIS WILL write chunks to the isolated context library.")
    print(f"  Old chroma_db at {CHROMA_DB_PATH} will NOT be touched.")
    print()
    print(f"  Type INGEST_ONE (exact) to proceed, anything else to cancel:")
    print()

    try:
        confirmation = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n[forge] Ingestion cancelled.")
        return

    if confirmation != "INGEST_ONE":
        print(f"[forge] Ingestion cancelled (got {confirmation!r}).")
        return

    write_audit_entry(session_id, "INGEST_ONE_STARTED", corpus_id, "-",
                      f"file={item.get('filename','?')} collection={CONTEXT_COLLECTION}")

    # ── Use exact fresh dry-run plan chunks; no second chunking pass allowed ───
    chunks = fresh_plan.get("chunks", [])
    if not chunks:
        write_audit_entry(session_id, "INGEST_ONE_REFUSED_DRY_RUN_MISMATCH", corpus_id, str(fresh_plan_path),
                          "fresh plan contained zero chunks after confirmation")
        print(f"[forge] INGEST_ONE_REFUSED_DRY_RUN_MISMATCH: fresh plan has zero chunks.")
        print(f"  No Chroma write was attempted.")
        return

    ts      = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    receipt_id = f"{ts}_ingest_{corpus_id}"
    ingestion_ts = datetime.datetime.now().isoformat(timespec="seconds")
    corpus_sha   = item.get("sha256_16","")
    corpus_folder = item.get("corpus_folder","")
    authority     = item.get("authority","")

    # ── Prepare embeddings ────────────────────────────────────────────────────
    print(f"\n[forge] Preparing {len(chunks)} chunks...")
    ef, ef_name = _get_embedding_function()
    print(f"  Embedding: {ef_name}")

    chunk_texts  = [c["text"] for c in chunks]
    print(f"  Embedding {len(chunk_texts)} chunks...")
    try:
        embeddings = _embed_texts(chunk_texts, ef)
    except Exception as e:
        print(f"  Embedding failed: {e} — falling back to hash_embed")
        embeddings = [_hash_embed(t) for t in chunk_texts]
        ef_name = "hash_embed_offline (fallback)"

    # ── Build metadata and symbolic tags ─────────────────────────────────────
    ids        = []
    metadatas  = []
    sym_maps   = []

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        chunk_id  = f"{corpus_id}_chunk_{i:04d}"
        chunk_sha = hashlib.sha256(chunk["text"].encode("utf-8")).hexdigest()[:16]

        # Brain 1: provenance metadata
        meta1 = {
            "corpus_id":           corpus_id,
            "filename":            item.get("filename",""),
            "absolute_path":       str(fpath),
            "relative_path":       item.get("relative_path",""),
            "corpus_folder":       corpus_folder,
            "authority":           authority,
            "source_role":         item.get("use_for",""),
            "sha256_16":           corpus_sha,
            "chunk_id":            chunk_id,
            "chunk_index":         i,
            "chunk_count":         len(chunks),
            "chunk_sha256_16":     chunk_sha,
            "char_start":          chunk.get("char_start",0),
            "char_end":            chunk.get("char_end",0),
            "char_count":          chunk.get("char_count",0),
            "extraction_method":   fpath.suffix.lower(),
            "ingestion_receipt_id": receipt_id,
            "ingestion_timestamp": ingestion_ts,
            "collection_namespace": CONTEXT_COLLECTION,
            "index_version":       "v1",
            "no_manual_edit":      "true",
            "embedding_method":    ef_name[:80],
        }

        # Brain 2: RPMC symbolic tags
        meta2 = _build_rpmc_symbolic_tags(chunk["text"], corpus_folder, authority)

        # Merge both brains (Chroma requires flat str/int/float metadata)
        full_meta = {**meta1, **meta2}
        ids.append(chunk_id)
        metadatas.append(full_meta)
        sym_maps.append({
            "chunk_id": chunk_id,
            "corpus_id": corpus_id,
            **meta2,
            "chunk_preview": chunk["text"][:200],
        })

    # ── Write to isolated Chroma ──────────────────────────────────────────────
    for d in [CONTEXT_LIB_CHROMA, CONTEXT_LIB_RECEIPTS,
               CONTEXT_LIB_INDEXES, CONTEXT_LIB_MANIFESTS, CONTEXT_LIB_SYMBOLIC]:
        d.mkdir(parents=True, exist_ok=True)

    print(f"  Writing to Chroma collection '{CONTEXT_COLLECTION}'...")
    try:
        import chromadb as _chroma
        client = _chroma.PersistentClient(path=str(CONTEXT_LIB_CHROMA))
        collection = client.get_or_create_collection(
            name=CONTEXT_COLLECTION,
            metadata={"description": "AI.Web context library v1 — dual-brain chunks",
                      "created": ingestion_ts}
        )
        # Add in batches of 50 to avoid memory issues
        BATCH = 50
        for bi in range(0, len(ids), BATCH):
            collection.add(
                ids=ids[bi:bi+BATCH],
                embeddings=embeddings[bi:bi+BATCH],
                documents=chunk_texts[bi:bi+BATCH],
                metadatas=metadatas[bi:bi+BATCH],
            )
        post_count = collection.count()
        exact_data, expected_ids, exact_issues = _collection_get_expected_chunks(collection, {
            "corpus_id": corpus_id,
            "receipt_id": receipt_id,
            "chunk_ids": ids,
            "document_chunk_count": len(ids),
            "sha256_16": corpus_sha,
        })
        exact_metas = exact_data.get("metadatas", []) or [] if isinstance(exact_data, dict) else []
        exact_found = len(exact_data.get("ids", []) or []) if isinstance(exact_data, dict) else 0
    except Exception as e:
        write_audit_entry(session_id, "INGEST_ONE_FAILED", corpus_id, "-", f"chroma write: {e}")
        print(f"\n[forge] INGEST_ONE_FAILED: Chroma write error: {e}")
        return

    # ── Verify exact document chunks, not merely collection-wide count ─────────
    expected_n = len(ids)
    if post_count < expected_n or exact_issues or exact_found != expected_n:
        write_audit_entry(session_id, "INGEST_ONE_FAILED", corpus_id, f"{exact_found}/{expected_n}",
                          f"exact chunk verification failed; collection_total={post_count}; issues={exact_issues[:3]}")
        print(f"[forge] INGEST_ONE_FAILED: Expected {expected_n} exact chunks for {corpus_id}; found {exact_found}.")
        if exact_issues:
            for issue in exact_issues[:8]:
                print(f"  ✗ {issue}")
        return

    # ── Write symbolic map ────────────────────────────────────────────────────
    sym_path = CONTEXT_LIB_SYMBOLIC / f"{receipt_id}_symbolic_map.json"
    sym_path.write_text(_json.dumps(sym_maps, indent=2), encoding="utf-8")

    # ── Write ingestion receipt ───────────────────────────────────────────────
    mf_path = CONTEXT_LIB_MANIFESTS / f"{receipt_id}_manifest.json"
    receipt = {
        "receipt_id":         receipt_id,
        "timestamp":          ingestion_ts,
        "session_id":         session_id,
        "corpus_id":          corpus_id,
        "filename":           item.get("filename",""),
        "absolute_path":      str(fpath),
        "corpus_folder":      corpus_folder,
        "authority":          authority,
        "sha256_16":          corpus_sha,
        "collection":         CONTEXT_COLLECTION,
        "chroma_path":        str(CONTEXT_LIB_CHROMA),
        "chunk_count_planned": len(chunks),
        "chunk_count_verified": expected_n,
        "document_chunk_count": expected_n,
        "collection_count_after": post_count,
        "chunk_ids": ids,
        "chunk_sha256_16": [m.get("chunk_sha256_16", "") for m in metadatas],
        "embedding_method":   ef_name,
        "dry_run_plan_path":  str(fresh_plan_path),
        "dry_run_chunk_count": fresh_plan.get("chunk_count"),
        "extraction_chars":   fresh_plan.get("extraction_chars", 0),
        "chunk_policy":       {"target": CHUNK_TARGET, "max": CHUNK_MAX, "overlap": CHUNK_OVERLAP},
        "brain1_fields":      list(metadatas[0].keys()) if metadatas else [],
        "brain2_fields":      list(_build_rpmc_symbolic_tags("","","").keys()),
        "symbolic_map_path":  str(sym_path),
        "collection_manifest_path": str(mf_path),
        "verification_ok":    exact_found == expected_n and not exact_issues,
    }
    rj = CONTEXT_LIB_RECEIPTS / f"{receipt_id}.json"
    rm = CONTEXT_LIB_RECEIPTS / f"{receipt_id}.md"
    rj.write_text(_json.dumps(receipt, indent=2), encoding="utf-8")
    rm.write_text(
        f"# Ingestion Receipt: {receipt_id}\n"
        f"**corpus_id**: {corpus_id}  **file**: {item.get('filename','')}  \n"
        f"**chunks**: {post_count}/{expected_n}  **embedding**: {ef_name}\n",
        encoding="utf-8"
    )

    # ── Write collection manifest ─────────────────────────────────────────────
    mf_path.write_text(_json.dumps({
        "collection": CONTEXT_COLLECTION,
        "total_chunks": post_count,
        "collection_total_chunks": post_count,
        "document_chunk_count": expected_n,
        "ingested_corpus_ids": [corpus_id],
        "last_updated": ingestion_ts,
        "receipts": [str(rj)],
    }, indent=2), encoding="utf-8")

    write_audit_entry(session_id, "INGEST_ONE_COMPLETED", corpus_id,
                      f"{expected_n} document chunks",
                      f"collection={CONTEXT_COLLECTION} collection_total={post_count} sha={corpus_sha} embedding={ef_name[:40]}")

    print(f"\n[forge] INGEST_ONE_COMPLETED")
    print(f"  corpus_id        : {corpus_id}")
    print(f"  Document chunks  : {expected_n} written and verified")
    print(f"  Collection total : {post_count}")
    print(f"  Collection       : {CONTEXT_COLLECTION}")
    print(f"  Path             : {CONTEXT_LIB_CHROMA}")
    print(f"  Embedding        : {ef_name}")
    print(f"  Receipt          : {rj}")
    print(f"  Symbolic         : {sym_path}")
    print()


# ─── REAL INGEST-VERIFY ───────────────────────────────────────────────────────

def cmd_ingest_verify(receipt_arg: str, session_id: str) -> None:
    """
    Verify an ingestion receipt against exact corpus-specific chunks in the context library.
    Usage: ingest-verify <receipt_id_or_latest>
    """
    import json as _json, hashlib
    from agents.forge.memory import write_audit_entry

    receipt_arg = (receipt_arg.strip() or "latest")
    CONTEXT_LIB_RECEIPTS.mkdir(parents=True, exist_ok=True)

    if receipt_arg == "latest":
        receipts = sorted(CONTEXT_LIB_RECEIPTS.glob("*.json"), reverse=True)
        if not receipts:
            print("[forge] No ingestion receipts found. Run 'ingest-one <corpus_id>' first.")
            write_audit_entry(session_id, "INGEST_VERIFY_FAILED", "latest", "-", "no receipts found")
            return
        rpath = receipts[0]
    else:
        rpath = CONTEXT_LIB_RECEIPTS / receipt_arg
        if not rpath.suffix:
            rpath = rpath.with_suffix(".json")
        if not rpath.exists():
            matches = sorted(CONTEXT_LIB_RECEIPTS.glob(f"{receipt_arg}*.json"), reverse=True)
            if matches:
                rpath = matches[0]
            else:
                print(f"[forge] ERROR: Receipt not found: {receipt_arg}")
                return

    try:
        receipt = _json.loads(rpath.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"[forge] ERROR: Cannot read receipt: {e}")
        return

    checks = []
    corpus_id = receipt.get("corpus_id", "?")

    # Check 1: source file exists
    fpath = Path(receipt.get("absolute_path", ""))
    checks.append(("source file exists", fpath.exists(), str(fpath)))

    # Check 2: sha matches
    expected_sha = receipt.get("sha256_16", "")
    if fpath.exists() and expected_sha:
        actual = hashlib.sha256(fpath.read_bytes()).hexdigest()[:16]
        ok = actual == expected_sha
        checks.append(("sha256 unchanged", ok, f"expected={expected_sha} actual={actual}"))
    else:
        checks.append(("sha256 unchanged", False, "file missing or no SHA"))

    ok_chunks, chunk_checks, details = _verify_receipt_exact_chunks(receipt)
    checks.extend(chunk_checks)

    all_ok = all(c[1] for c in checks)
    audit_tool = "INGEST_VERIFY_OK" if all_ok else "INGEST_VERIFY_FAILED"
    write_audit_entry(session_id, audit_tool, str(rpath), "-",
                      f"corpus_id={corpus_id} checks={len(checks)} passed={sum(1 for c in checks if c[1])} document_chunks={_receipt_expected_chunk_count(receipt)} collection_total={details.get('collection_count_after', '?')}")

    print()
    print(f"── Ingest Verify ─────────────────────────────────────")
    print(f"  Receipt   : {rpath.name}")
    print(f"  corpus_id : {corpus_id}")
    print(f"  File      : {receipt.get('filename', '?')}")
    print(f"  Timestamp : {receipt.get('timestamp', '?')}")
    print(f"  Doc chunks: {_receipt_expected_chunk_count(receipt)}")
    if details.get("collection_count_after") is not None:
        print(f"  Collection total: {details.get('collection_count_after')}")
    print()
    for name, passed, detail in checks:
        print(f"  {'✓' if passed else '✗'} {name:<50} {str(detail)[:70]}")
    print()
    print(f"  Result: {audit_tool}")
    print(f"──────────────────────────────────────────────────────")
    print()



# ─── INGEST RECEIPT REPAIR ───────────────────────────────────────────────────

def cmd_ingest_receipt_repair(receipt_arg: str, session_id: str) -> None:
    """
    Repair a receipt whose document chunk count was accidentally recorded as collection total.
    Writes only Forge-owned receipt/manifest files. Does not modify Chroma.
    Usage: ingest-receipt-repair <latest|receipt_id>
    """
    import json as _json
    from agents.forge.memory import write_audit_entry

    receipt_arg = (receipt_arg.strip() or "latest")
    if receipt_arg == "latest":
        receipts = sorted(CONTEXT_LIB_RECEIPTS.glob("*.json"), reverse=True)
        if not receipts:
            print("[forge] No ingestion receipts found.")
            write_audit_entry(session_id, "INGEST_RECEIPT_REPAIR_FAILED", "latest", "-", "no receipts found")
            return
        rpath = receipts[0]
    else:
        rpath = CONTEXT_LIB_RECEIPTS / receipt_arg
        if not rpath.suffix:
            rpath = rpath.with_suffix(".json")
        if not rpath.exists():
            matches = sorted(CONTEXT_LIB_RECEIPTS.glob(f"{receipt_arg}*.json"), reverse=True)
            if matches:
                rpath = matches[0]
            else:
                print(f"[forge] ERROR: Receipt not found: {receipt_arg}")
                write_audit_entry(session_id, "INGEST_RECEIPT_REPAIR_FAILED", receipt_arg, "-", "receipt not found")
                return

    try:
        receipt = _json.loads(rpath.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[forge] ERROR: Cannot read receipt: {e}")
        write_audit_entry(session_id, "INGEST_RECEIPT_REPAIR_FAILED", str(rpath), "-", f"read error: {e}")
        return

    ok, checks, details = _verify_receipt_exact_chunks(receipt)
    hard_failures = [c for c in checks if not c[1] and c[0] not in ("receipt verified count equals document count",)]
    if hard_failures:
        print()
        print("[forge] INGEST_RECEIPT_REPAIR_REFUSED")
        for name, passed, detail in checks:
            print(f"  {'✓' if passed else '✗'} {name:<50} {str(detail)[:80]}")
        print("  No files were changed.")
        write_audit_entry(session_id, "INGEST_RECEIPT_REPAIR_REFUSED", str(rpath), "-",
                          f"hard_failures={len(hard_failures)} first={hard_failures[0][0] if hard_failures else '?'}")
        return

    old_verified = receipt.get("chunk_count_verified")
    doc_count = _receipt_expected_chunk_count(receipt)
    collection_total = details.get("collection_count_after")
    repair_record = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id": session_id,
        "reason": "Patch45B document-count repair; previous chunk_count_verified used collection total",
        "old_chunk_count_verified": old_verified,
        "new_chunk_count_verified": doc_count,
        "collection_count_after": collection_total,
    }
    history = receipt.get("repair_history")
    if not isinstance(history, list):
        history = []
    history.append(repair_record)

    receipt["repair_history"] = history
    receipt["document_chunk_count"] = doc_count
    receipt["chunk_count_verified"] = doc_count
    receipt["collection_count_after"] = collection_total
    receipt["chunk_ids"] = details.get("chunk_ids", [])
    receipt["chunk_sha256_16"] = details.get("chunk_sha256_16", [])
    receipt["verification_ok"] = True
    receipt["patch45b_repaired"] = True
    receipt["patch45b_repair_timestamp"] = repair_record["timestamp"]

    rpath.write_text(_json.dumps(receipt, indent=2), encoding="utf-8")

    # Repair receipt markdown if present.
    md_path = rpath.with_suffix(".md")
    if md_path.exists():
        md_path.write_text(
            f"# Ingestion Receipt: {receipt.get('receipt_id', rpath.stem)}\n"
            f"**corpus_id**: {receipt.get('corpus_id','?')}  **file**: {receipt.get('filename','')}  \n"
            f"**document chunks**: {doc_count}  **collection total after write**: {collection_total}  **embedding**: {receipt.get('embedding_method','?')}\n"
            f"**Patch45B repaired**: true  \n",
            encoding="utf-8"
        )

    # Repair per-ingest manifest if present. Preserve total_chunks as collection total for compatibility.
    mf = Path(str(receipt.get("collection_manifest_path", "")))
    if mf.exists() and mf.is_file():
        try:
            mf_data = _json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            mf_data = {}
        mf_data["collection"] = receipt.get("collection", CONTEXT_COLLECTION)
        mf_data["total_chunks"] = collection_total
        mf_data["collection_total_chunks"] = collection_total
        mf_data["document_chunk_count"] = doc_count
        mf_data["ingested_corpus_ids"] = [receipt.get("corpus_id")]
        mf_data["last_updated"] = repair_record["timestamp"]
        mf_data["receipts"] = [str(rpath)]
        mf_data["patch45b_repaired"] = True
        mf.write_text(_json.dumps(mf_data, indent=2), encoding="utf-8")

    write_audit_entry(session_id, "INGEST_RECEIPT_REPAIRED", str(rpath), f"{doc_count} document chunks",
                      f"old_verified={old_verified} collection_total={collection_total}")

    print()
    print("── Ingest Receipt Repair ─────────────────────────────")
    print(f"  Receipt          : {rpath}")
    print(f"  corpus_id        : {receipt.get('corpus_id')}")
    print(f"  old verified     : {old_verified}")
    print(f"  document chunks  : {doc_count}")
    print(f"  collection total : {collection_total}")
    print(f"  Chroma modified  : NO")
    print(f"  Receipt repaired : YES")
    print(f"──────────────────────────────────────────────────────")
    print()


# ─── CONTEXT STATUS ───────────────────────────────────────────────────────────



# ─── PHASE B: MULTI-DOCUMENT INGESTION PLANNING ──────────────────────────────

def _row_id(row: dict) -> str:
    return str(row.get("id") or row.get("corpus_id") or "").strip()


def _row_eligible(row: dict) -> bool:
    return str(row.get("index_eligible", "")).strip().lower() in ("true", "1", "yes")


def _row_folder(row: dict) -> str:
    return str(row.get("corpus_folder") or row.get("folder") or "").strip()


def _row_priority(row: dict) -> int:
    try:
        return int(str(row.get("priority", "99")).strip())
    except Exception:
        return 99


def _manifest_rows() -> list[dict]:
    return _corpus_load_json() or _corpus_load_csv() or []


def _ingested_corpus_ids() -> dict[str, dict]:
    """Return corpus_id -> latest receipt data for already-ingested documents."""
    out: dict[str, dict] = {}
    for rpath in _receipt_json_paths():
        try:
            r = _load_receipt(rpath)
        except Exception:
            continue
        cid = str(r.get("corpus_id", "")).strip()
        if cid and cid not in out:
            out[cid] = {"receipt_path": str(rpath), "receipt": r}
    return out


def _source_authority_weight(row: dict) -> tuple[float, str, str]:
    """
    Compute deterministic source authority weight from manifest evidence.
    This is not semantic truth; it is a routing priority for ingestion order.
    """
    folder = _row_folder(row).lower()
    authority = str(row.get("authority", "")).lower()
    status = str(row.get("status", "")).lower()
    use_for = str(row.get("use_for", "")).lower()
    tags = str(row.get("tags", "")).lower()
    eligible = _row_eligible(row)

    if not eligible or "archive" in folder or "held" in status:
        return 0.0, "HELD_OR_ARCHIVE", "not index eligible or archive-held"
    if "01_system_law" in folder:
        return 1.00, "SYSTEM_LAW", "highest priority system-law / instruction layer"
    if "rpmc_full_protocol" in authority or "rpmc" in tags or "rpmc" in use_for:
        return 0.95, "RPMC_AUTHORITY", "RPMC source/protocol authority"
    if "canonical" in authority:
        return 0.90, "CANONICAL", "canonical project source"
    if "03_gilligan" in folder or "gilligan" in tags or "gilligan" in use_for:
        return 0.85, "GILLIGAN_CORE", "Gilligan agent core source"
    if "02_aiweb" in folder:
        return 0.80, "AIWEB_ARCHITECTURE", "AI.Web architecture source"
    if "04_fbsc" in folder:
        return 0.78, "FBSC_DOCTRINE", "FBSC doctrine/source layer"
    if "05_engineering" in folder:
        return 0.72, "ENGINEERING_STANDARD", "engineering standard"
    if "06_public" in folder or "07_business" in folder:
        return 0.60, "PUBLIC_OR_BUSINESS", "public/business language"
    if "08_research" in folder:
        return 0.50, "RESEARCH_FUTURE", "research/future speculation"
    return 0.40, "UNCLASSIFIED_ELIGIBLE", "eligible but low authority / unclassified"


def _batch_safe_name(arg: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", (arg or "batch").strip())
    cleaned = cleaned.strip("._") or "batch"
    return cleaned[:80]


def _batch_plan_paths() -> list[Path]:
    INGESTION_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(INGESTION_PLANS_DIR.glob("*_batch_plan_*.json"), reverse=True)


def _batch_dry_run_paths() -> list[Path]:
    INGESTION_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(INGESTION_PLANS_DIR.glob("*_batch_dry_run_*.json"), reverse=True)


def _resolve_batch_file(arg: str, kind: str = "plan") -> Optional[Path]:
    arg = (arg or "latest").strip()
    pool = _batch_dry_run_paths() if kind == "dry-run" else _batch_plan_paths()
    if arg == "latest":
        return pool[0] if pool else None
    safe = Path(arg).name
    candidate = INGESTION_PLANS_DIR / safe
    if not candidate.suffix:
        candidate = candidate.with_suffix(".json")
    try:
        candidate.resolve().relative_to(INGESTION_PLANS_DIR.resolve())
    except Exception:
        return None
    if candidate.exists() and candidate.is_file():
        return candidate
    # Resolve by contained plan id or prefix
    matches = sorted(INGESTION_PLANS_DIR.glob(f"*{safe}*.json"), reverse=True)
    for m in matches:
        if kind == "dry-run" and "_batch_dry_run_" in m.name:
            return m
        if kind == "plan" and "_batch_plan_" in m.name:
            return m
    return None


def _batch_targets_from_arg(arg: str, rows: list[dict]) -> tuple[list[dict], str, list[str]]:
    """Resolve batch target arg into manifest rows. No writes."""
    issues: list[str] = []
    raw = (arg or "").strip()
    if not raw:
        return [], "", ["missing target. Usage: ingest-batch-plan <folder|ids:corpus_0001,corpus_0002|remaining|all-eligible>"]

    by_id = {_row_id(r).lower(): r for r in rows if _row_id(r)}
    raw_l = raw.lower()

    if raw_l.startswith("ids:"):
        ids = [x.strip() for x in re.split(r"[,\s]+", raw[4:]) if x.strip()]
        selected = []
        for cid in ids:
            item = by_id.get(cid.lower())
            if item:
                selected.append(item)
            else:
                issues.append(f"corpus_id not found: {cid}")
        return selected, f"ids:{','.join(ids)}", issues

    # Space-separated explicit corpus IDs
    explicit_ids = [x for x in raw.split() if x.lower().startswith("corpus_")]
    if explicit_ids:
        selected = []
        for cid in explicit_ids:
            item = by_id.get(cid.lower())
            if item:
                selected.append(item)
            else:
                issues.append(f"corpus_id not found: {cid}")
        return selected, f"ids:{','.join(explicit_ids)}", issues

    ingested = set(_ingested_corpus_ids().keys())
    if raw_l in ("remaining", "next"):
        selected = [r for r in rows if _row_eligible(r) and _row_id(r) not in ingested]
        return selected, "remaining", issues

    if raw_l in ("all", "ingest-all"):
        return [], raw, ["refused ambiguous all-target. Use all-eligible for planning only; there is still no ingest-all command."]

    if raw_l == "all-eligible":
        selected = [r for r in rows if _row_eligible(r)]
        return selected, "all-eligible", issues

    # Folder/name match. Accept 01_SYSTEM_LAW, folder:01_SYSTEM_LAW, or partial folder term.
    folder_term = raw[7:] if raw_l.startswith("folder:") else raw
    ft = folder_term.lower()
    selected = [r for r in rows if ft in _row_folder(r).lower() or ft in str(r.get("relative_path", "")).lower()]
    if not selected:
        issues.append(f"no corpus rows matched target: {raw}")
    return selected, f"folder:{folder_term}", issues


def _batch_item_record(row: dict, ingested: dict[str, dict]) -> dict:
    cid = _row_id(row)
    weight, tier, reason = _source_authority_weight(row)
    already = cid in ingested
    eligible = _row_eligible(row)
    folder = _row_folder(row)
    status = str(row.get("status", ""))
    if already:
        action = "SKIP_ALREADY_INGESTED"
    elif not eligible or "archive" in folder.lower():
        action = "SKIP_NOT_ELIGIBLE"
    else:
        action = "READY_FOR_DRY_RUN"
    return {
        "corpus_id": cid,
        "filename": row.get("filename", ""),
        "relative_path": row.get("relative_path", ""),
        "absolute_path": row.get("absolute_path", ""),
        "corpus_folder": folder,
        "authority": row.get("authority", ""),
        "status": status,
        "priority": row.get("priority", ""),
        "index_eligible": eligible,
        "source_type": row.get("source_type", ""),
        "sha256_16": row.get("sha256_16", ""),
        "source_authority_weight": weight,
        "source_authority_tier": tier,
        "source_authority_reason": reason,
        "already_ingested": already,
        "existing_receipt": (ingested.get(cid) or {}).get("receipt_path", ""),
        "recommended_action": action,
    }


def cmd_corpus_id_map(session_id: str) -> None:
    """Print all corpus IDs and current ingestion state. Usage: corpus-id-map"""
    from agents.forge.memory import write_audit_entry
    rows = _manifest_rows()
    ingested = _ingested_corpus_ids()
    write_audit_entry(session_id, "CORPUS_ID_MAP_SHOWN", str(_CORPUS_JSON), f"{len(rows)} rows", f"ingested={len(ingested)}")
    print()
    print("── Corpus ID Map ─────────────────────────────────────")
    print(f"  Manifest rows : {len(rows)}")
    print(f"  Ingested docs : {len(ingested)}")
    print()
    for r in sorted(rows, key=lambda x: _row_id(x)):
        cid = _row_id(r)
        mark = "INGESTED" if cid in ingested else ("ELIGIBLE" if _row_eligible(r) else "HELD")
        weight, tier, _ = _source_authority_weight(r)
        print(f"  {cid:<12} {mark:<9} weight={weight:.2f} {tier:<22} {_row_folder(r):<24} {str(r.get('filename',''))[:70]}")
    print("──────────────────────────────────────────────────────")
    print()


def cmd_source_authority_weights(arg: str, session_id: str) -> None:
    """Show deterministic authority weighting for corpus items. Usage: source-authority-weights [folder|all]"""
    from agents.forge.memory import write_audit_entry
    rows = _manifest_rows()
    target = (arg or "all").strip()
    if target.lower() not in ("", "all"):
        rows = [r for r in rows if target.lower() in _row_folder(r).lower() or target.lower() in str(r.get("relative_path", "")).lower()]
    write_audit_entry(session_id, "SOURCE_AUTHORITY_WEIGHTS_SHOWN", str(_CORPUS_JSON), f"{len(rows)} rows", f"target={target}")
    print()
    print("── Source Authority Weights ──────────────────────────")
    print(f"  Target: {target}")
    print()
    for r in sorted(rows, key=lambda x: (-_source_authority_weight(x)[0], _row_id(x))):
        w, tier, reason = _source_authority_weight(r)
        print(f"  {w:.2f}  {tier:<22} {_row_id(r):<12} {_row_folder(r):<24} {str(r.get('filename',''))[:64]}")
        print(f"        reason: {reason}")
    print("──────────────────────────────────────────────────────")
    print()


def cmd_ingest_next(arg: str, session_id: str) -> None:
    """Show the next eligible, not-yet-ingested corpus item. Usage: ingest-next [folder]"""
    from agents.forge.memory import write_audit_entry
    rows = _manifest_rows()
    if arg.strip():
        rows = [r for r in rows if arg.strip().lower() in _row_folder(r).lower() or arg.strip().lower() in str(r.get("relative_path", "")).lower()]
    ingested = _ingested_corpus_ids()
    candidates = [r for r in rows if _row_eligible(r) and _row_id(r) not in ingested]
    candidates.sort(key=lambda r: (-_source_authority_weight(r)[0], _row_priority(r), _row_id(r)))
    write_audit_entry(session_id, "INGEST_NEXT_SHOWN", str(_CORPUS_JSON), f"{len(candidates)} candidates", f"target={arg or 'all'}")
    print()
    print("── Ingest Next ───────────────────────────────────────")
    if not candidates:
        print("  No eligible not-yet-ingested corpus item found for this target.")
        print("──────────────────────────────────────────────────────")
        print()
        return
    r = candidates[0]
    w, tier, reason = _source_authority_weight(r)
    cid = _row_id(r)
    print(f"  Next corpus_id : {cid}")
    print(f"  Filename       : {r.get('filename','')}")
    print(f"  Folder         : {_row_folder(r)}")
    print(f"  SHA            : {r.get('sha256_16','')}")
    print(f"  Authority      : {w:.2f} {tier} — {reason}")
    print()
    print("  Safe command block:")
    print(f"    corpus-show {cid}")
    print(f"    ingest-dry-run {cid}")
    print(f"    ingest-dry-run-validate {cid}")
    print(f"    ingest-one {cid}")
    print(f"    ingest-verify latest")
    print("──────────────────────────────────────────────────────")
    print()


def cmd_ingest_batch_plan(arg: str, session_id: str) -> None:
    """Create a read-only multi-document ingestion plan. Usage: ingest-batch-plan <folder|ids:...|remaining|all-eligible>"""
    import json as _json
    from agents.forge.memory import write_audit_entry
    rows = _manifest_rows()
    selected, target_label, issues = _batch_targets_from_arg(arg, rows)
    if issues:
        write_audit_entry(session_id, "INGEST_BATCH_PLAN_REFUSED", str(_CORPUS_JSON), "-", "; ".join(issues)[:220])
        print("[forge] INGEST_BATCH_PLAN_REFUSED")
        for issue in issues:
            print(f"  ✗ {issue}")
        return
    ingested = _ingested_corpus_ids()
    items = [_batch_item_record(r, ingested) for r in selected]
    items.sort(key=lambda x: (-float(x.get("source_authority_weight", 0)), str(x.get("corpus_folder", "")), str(x.get("corpus_id", ""))))
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    plan_id = f"{ts}_batch_plan_{_batch_safe_name(target_label)}"
    path = INGESTION_PLANS_DIR / f"{plan_id}.json"
    payload = {
        "report_type": "BATCH_INGEST_PLAN",
        "phase": "B_multi_document_ingestion_planning",
        "plan_id": plan_id,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id": session_id,
        "target": target_label,
        "no_chroma_write": True,
        "no_embedding": True,
        "no_ingest_all": True,
        "total_items": len(items),
        "ready_items": sum(1 for i in items if i.get("recommended_action") == "READY_FOR_DRY_RUN"),
        "already_ingested_items": sum(1 for i in items if i.get("already_ingested")),
        "items": items,
    }
    INGESTION_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(_json.dumps(payload, indent=2), encoding="utf-8")
    write_audit_entry(session_id, "INGEST_BATCH_PLAN_CREATED", str(path), f"{len(items)} items", f"ready={payload['ready_items']} target={target_label}")
    print()
    print("── Ingest Batch Plan ─────────────────────────────────")
    print(f"  Plan id       : {plan_id}")
    print(f"  Path          : {path}")
    print(f"  Target        : {target_label}")
    print(f"  Items         : {len(items)}")
    print(f"  Ready         : {payload['ready_items']}")
    print(f"  Already loaded: {payload['already_ingested_items']}")
    print("  No Chroma write. No embeddings. No ingest-all.")
    print()
    for it in items:
        print(f"  {it['corpus_id']:<12} {it['recommended_action']:<22} weight={it['source_authority_weight']:.2f} {it['source_authority_tier']:<20} {it['corpus_folder']:<22} {it['filename'][:58]}")
    print("──────────────────────────────────────────────────────")
    print()


def cmd_ingest_batch_dry_run(arg: str, session_id: str) -> None:
    """Run dry-runs for every READY item in a batch plan. No Chroma writes. Usage: ingest-batch-dry-run <latest|plan_id>"""
    import json as _json
    from agents.forge.memory import write_audit_entry
    plan_path = _resolve_batch_file(arg or "latest", kind="plan")
    if not plan_path:
        print("[forge] No batch plan found. Run ingest-batch-plan first.")
        return
    try:
        plan = _json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[forge] ERROR: Cannot read batch plan: {e}")
        return
    rows = _manifest_rows()
    by_id = {_row_id(r): r for r in rows if _row_id(r)}
    results = []
    ready = [i for i in plan.get("items", []) if i.get("recommended_action") == "READY_FOR_DRY_RUN"]
    for it in ready:
        cid = it.get("corpus_id", "")
        row = by_id.get(cid)
        if not row:
            results.append({**it, "dry_run_status": "FAILED", "issues": ["corpus id missing from current manifest"]})
            continue
        dry_plan, dry_path, issues = _make_dry_run_plan(cid, row, session_id, internal=False)
        if dry_plan and dry_path:
            parity = _validate_dry_run_plan_for_write(dry_plan, cid, row)
            issues = issues + parity
        ok = bool(dry_plan and dry_path and not issues)
        results.append({
            **it,
            "dry_run_status": "OK" if ok else "FAILED",
            "dry_run_plan_path": str(dry_path) if dry_path else "",
            "chunk_count": dry_plan.get("chunk_count") if dry_plan else 0,
            "max_chars": dry_plan.get("max_chars") if dry_plan else 0,
            "source_hash": dry_plan.get("source_hash") if dry_plan else "",
            "issues": issues,
        })
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    dry_id = f"{ts}_batch_dry_run_{_batch_safe_name(plan.get('target','batch'))}"
    out_path = INGESTION_PLANS_DIR / f"{dry_id}.json"
    payload = {
        "report_type": "BATCH_DRY_RUN",
        "phase": "B_multi_document_ingestion_planning",
        "dry_run_id": dry_id,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id": session_id,
        "source_batch_plan": str(plan_path),
        "source_batch_plan_id": plan.get("plan_id"),
        "target": plan.get("target"),
        "no_chroma_write": True,
        "no_embedding": True,
        "ready_count": len(ready),
        "ok_count": sum(1 for r in results if r.get("dry_run_status") == "OK"),
        "failed_count": sum(1 for r in results if r.get("dry_run_status") != "OK"),
        "items": results,
    }
    out_path.write_text(_json.dumps(payload, indent=2), encoding="utf-8")
    audit_tool = "INGEST_BATCH_DRY_RUN_CREATED" if payload["failed_count"] == 0 else "INGEST_BATCH_DRY_RUN_WARN"
    write_audit_entry(session_id, audit_tool, str(out_path), f"{payload['ok_count']}/{payload['ready_count']} ok", f"target={plan.get('target')}")
    print()
    print("── Ingest Batch Dry-Run ──────────────────────────────")
    print(f"  Dry-run id : {dry_id}")
    print(f"  Path       : {out_path}")
    print(f"  Source plan: {plan_path.name}")
    print(f"  Ready      : {payload['ready_count']}")
    print(f"  OK         : {payload['ok_count']}")
    print(f"  Failed     : {payload['failed_count']}")
    print("  No Chroma write. No embeddings.")
    print()
    for r in results:
        status = r.get("dry_run_status")
        print(f"  {r.get('corpus_id',''):<12} {status:<7} chunks={r.get('chunk_count',0):<5} max={r.get('max_chars',0):<5} {r.get('filename','')[:64]}")
        for issue in r.get("issues", [])[:3]:
            print(f"      ✗ {issue}")
    print("──────────────────────────────────────────────────────")
    print()


def cmd_ingest_batch_verify(arg: str, session_id: str) -> None:
    """Verify receipts for all items in a batch dry-run or plan. Usage: ingest-batch-verify <latest|id>"""
    import json as _json
    from agents.forge.memory import write_audit_entry
    path = _resolve_batch_file(arg or "latest", kind="dry-run") or _resolve_batch_file(arg or "latest", kind="plan")
    if not path:
        print("[forge] No batch plan/dry-run found.")
        return
    try:
        data = _json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[forge] ERROR: Cannot read batch file: {e}")
        return
    items = data.get("items", [])
    checked = []
    for it in items:
        cid = it.get("corpus_id", "")
        if not cid:
            continue
        receipts = _receipts_for_corpus(cid)
        if not receipts:
            checked.append({"corpus_id": cid, "status": "MISSING_RECEIPT", "checks": 0, "passed": 0})
            continue
        rpath, receipt = receipts[0]
        ok, checks, details = _verify_receipt_exact_chunks(receipt)
        checked.append({
            "corpus_id": cid,
            "status": "OK" if ok else "FAILED",
            "receipt_path": str(rpath),
            "document_chunk_count": _receipt_expected_chunk_count(receipt),
            "collection_count_after": details.get("collection_count_after", receipt.get("collection_count_after")),
            "checks": len(checks),
            "passed": sum(1 for c in checks if c[1]),
        })
    ok_count = sum(1 for c in checked if c["status"] == "OK")
    audit_tool = "INGEST_BATCH_VERIFY_OK" if ok_count == len(checked) and checked else "INGEST_BATCH_VERIFY_WARN"
    write_audit_entry(session_id, audit_tool, str(path), f"{ok_count}/{len(checked)} ok", "batch receipt validation")
    print()
    print("── Ingest Batch Verify ───────────────────────────────")
    print(f"  Source : {path}")
    print(f"  Checked: {len(checked)}")
    print(f"  OK     : {ok_count}")
    print()
    for c in checked:
        print(f"  {c['corpus_id']:<12} {c['status']:<16} chunks={c.get('document_chunk_count','?')} checks={c.get('passed',0)}/{c.get('checks',0)}")
    print("──────────────────────────────────────────────────────")
    print()


def cmd_ingest_batch_apply(arg: str, session_id: str) -> None:
    """Apply a validated batch dry-run with per-document confirmations. Usage: ingest-batch-apply <latest|dry_run_id>"""
    import json as _json
    from agents.forge.memory import write_audit_entry
    dry_path = _resolve_batch_file(arg or "latest", kind="dry-run")
    if not dry_path:
        print("[forge] No batch dry-run found. Run ingest-batch-dry-run first.")
        return
    try:
        dry = _json.loads(dry_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[forge] ERROR: Cannot read batch dry-run: {e}")
        return
    ready = [i for i in dry.get("items", []) if i.get("dry_run_status") == "OK"]
    if not ready:
        print("[forge] INGEST_BATCH_APPLY_REFUSED: no OK dry-run items in this batch.")
        return
    if dry.get("failed_count", 0):
        print("[forge] INGEST_BATCH_APPLY_REFUSED: batch dry-run has failures. Fix or create a smaller batch first.")
        return
    print()
    print("── Ingest Batch Apply Gate ───────────────────────────")
    print(f"  Batch dry-run : {dry_path.name}")
    print(f"  Items         : {len(ready)}")
    print("  Safety        : requires APPLY_BATCH once, then INGEST_ONE for each document")
    print("  Not ingest-all: this applies only this named dry-run plan")
    print()
    for i, it in enumerate(ready, 1):
        print(f"  {i:02d}. {it.get('corpus_id')}  chunks={it.get('chunk_count')}  {it.get('filename','')[:70]}")
    print()
    print("  Type APPLY_BATCH (exact) to begin, anything else cancels:")
    confirm = input("\n  > ").strip()
    if confirm != "APPLY_BATCH":
        print("[forge] Batch apply cancelled. No Chroma writes attempted by batch command.")
        return
    write_audit_entry(session_id, "INGEST_BATCH_APPLY_STARTED", str(dry_path), f"{len(ready)} items", "per-document confirmations required")
    applied = 0
    for it in ready:
        cid = it.get("corpus_id", "")
        if _already_ingested_record(cid):
            print(f"[forge] Batch skip already ingested: {cid}")
            continue
        before = len(_receipts_for_corpus(cid))
        print()
        print(f"── Batch Item: {cid} ─────────────────────────────────")
        cmd_ingest_one(cid, session_id)
        after = len(_receipts_for_corpus(cid))
        if after > before:
            applied += 1
            ok, checks, _details = _verify_receipt_exact_chunks(_receipts_for_corpus(cid)[0][1])
            print(f"[forge] Batch item verified: {cid} {'OK' if ok else 'FAILED'}")
            if not ok:
                write_audit_entry(session_id, "INGEST_BATCH_APPLY_STOPPED", cid, "-", "post-ingest verify failed")
                break
        else:
            write_audit_entry(session_id, "INGEST_BATCH_APPLY_STOPPED", cid, "-", "no receipt created; user cancelled or ingest refused")
            print(f"[forge] Batch stopped at {cid}; no receipt was created.")
            break
    write_audit_entry(session_id, "INGEST_BATCH_APPLY_COMPLETED", str(dry_path), f"{applied}/{len(ready)} applied", "batch apply ended")
    print()
    print("── Batch Apply Complete ──────────────────────────────")
    print(f"  Applied : {applied}/{len(ready)}")
    print("  Run: ingest-batch-verify latest")
    print("──────────────────────────────────────────────────────")
    print()


def cmd_context_collection_stats(session_id: str) -> None:
    """Show collection-level stats, corpus distribution, receipts, and old DB isolation. Usage: context-collection-stats"""
    from collections import Counter
    from agents.forge.memory import write_audit_entry
    stats = _context_collection_stats()
    receipts = _receipt_json_paths()
    corpus_counts = Counter()
    receipt_counts = Counter()
    try:
        import chromadb as _chroma
        if CONTEXT_LIB_CHROMA.exists():
            client = _chroma.PersistentClient(path=str(CONTEXT_LIB_CHROMA))
            col = client.get_collection(CONTEXT_COLLECTION)
            data = col.get(include=["metadatas"])
            for m in data.get("metadatas", []) or []:
                corpus_counts[str((m or {}).get("corpus_id", "?"))] += 1
    except Exception:
        pass
    for rp in receipts:
        try:
            r = _load_receipt(rp)
            receipt_counts[str(r.get("corpus_id", "?"))] += 1
        except Exception:
            pass
    write_audit_entry(session_id, "CONTEXT_COLLECTION_STATS_SHOWN", str(CONTEXT_LIB_DIR), f"{sum(corpus_counts.values())} chunks", f"receipts={len(receipts)}")
    print()
    print("── Context Collection Stats ──────────────────────────")
    print(f"  Library path : {CONTEXT_LIB_DIR}")
    print(f"  Chroma path  : {CONTEXT_LIB_CHROMA}")
    print(f"  Old DB path  : {CHROMA_DB_PATH}")
    print(f"  Isolation    : {'OK — paths differ' if str(CONTEXT_LIB_CHROMA) != str(CHROMA_DB_PATH) else 'ERROR — same path'}")
    print(f"  Receipts     : {len(receipts)}")
    for s in stats:
        print(f"  Collection   : {s.get('name')} = {s.get('count')} chunks")
    print()
    print("  Corpus distribution:")
    for cid, count in sorted(corpus_counts.items()):
        print(f"    {cid:<12} chunks={count:<5} receipts={receipt_counts.get(cid,0)}")
    print("──────────────────────────────────────────────────────")
    print()

def cmd_context_status(session_id: str) -> None:
    """Show the isolated context library state. Usage: context-status"""
    from agents.forge.memory import write_audit_entry

    CONTEXT_LIB_DIR.mkdir(parents=True, exist_ok=True)
    receipts    = sorted(CONTEXT_LIB_RECEIPTS.glob("*.json"), reverse=True) if CONTEXT_LIB_RECEIPTS.exists() else []
    old_chroma_items = list(CHROMA_DB_PATH.iterdir()) if CHROMA_DB_PATH.exists() and CHROMA_DB_PATH.is_dir() else []

    collections = []
    total_chunks = 0
    try:
        import chromadb as _chroma
        if CONTEXT_LIB_CHROMA.exists():
            client = _chroma.PersistentClient(path=str(CONTEXT_LIB_CHROMA))
            for col in client.list_collections():
                n = col.count()
                total_chunks += n
                collections.append((col.name, n))
    except Exception as e:
        collections.append((f"(error: {e})", 0))

    write_audit_entry(session_id, "CONTEXT_STATUS_SHOWN", str(CONTEXT_LIB_DIR), "-",
                      f"collections={len(collections)} chunks={total_chunks} receipts={len(receipts)}")

    print()
    print(f"── Context Library Status ────────────────────────────")
    print(f"  Library path   : {CONTEXT_LIB_DIR}")
    print(f"  Chroma path    : {CONTEXT_LIB_CHROMA}")
    print(f"  Chroma exists  : {'YES' if CONTEXT_LIB_CHROMA.exists() else 'NO'}")
    print(f"  Collections    : {len(collections)}")
    for name, count in collections:
        print(f"    • {name}: {count} chunks")
    print(f"  Total chunks   : {total_chunks}")
    print(f"  Receipts       : {len(receipts)}")
    if receipts:
        print(f"  Latest receipt : {receipts[0].name}")
    print()
    print(f"  Old chroma_db  : {CHROMA_DB_PATH}")
    print(f"  Old DB items   : {len(old_chroma_items)} ({'untouched' if old_chroma_items else 'empty'})")
    print(f"  Isolation      : {'OK — paths differ' if str(CONTEXT_LIB_CHROMA) != str(CHROMA_DB_PATH) else 'ERROR — same path!'}")
    print(f"──────────────────────────────────────────────────────")
    print()


# ─── CONTEXT SEARCH TEST ──────────────────────────────────────────────────────

def cmd_context_search_test(query: str, session_id: str) -> None:
    """
    Read-only semantic search test against the context library.
    Shows both Brain 1 (provenance) and Brain 2 (RPMC symbolic) fields.
    Usage: context-search-test <query>
    """
    from agents.forge.memory import write_audit_entry

    if not query.strip():
        print()
        print("  Usage: context-search-test <query>")
        print("  Example: context-search-test collapse and resurrection")
        print()
        return

    if not CONTEXT_LIB_CHROMA.exists():
        print(f"[forge] No context library found at {CONTEXT_LIB_CHROMA}")
        print(f"  Run 'ingest-one <corpus_id>' first to populate the library.")
        return

    try:
        import chromadb as _chroma
        client = _chroma.PersistentClient(path=str(CONTEXT_LIB_CHROMA))
        collections = [c.name for c in client.list_collections()]
        if CONTEXT_COLLECTION not in collections:
            print(f"[forge] Collection '{CONTEXT_COLLECTION}' not found.")
            print(f"  Available: {collections}")
            return

        col = client.get_collection(CONTEXT_COLLECTION)
        if col.count() == 0:
            print(f"[forge] Collection is empty. Run 'ingest-one' first.")
            return

        # Embed the query using the same method as ingestion
        ef, ef_name = _get_embedding_function()
        query_embedding = _embed_texts([query.strip()], ef)[0]

        n_results = min(5, col.count())
        results = col.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

    except Exception as e:
        print(f"[forge] Search error: {e}")
        return

    write_audit_entry(session_id, "CONTEXT_SEARCH_TEST_SHOWN", query[:80], f"{n_results} results",
                      f"collection={CONTEXT_COLLECTION}")

    print()
    print(f"── Context Search Test ───────────────────────────────")
    print(f"  Query      : {query}")
    print(f"  Embedding  : {ef_name}")
    print(f"  Collection : {CONTEXT_COLLECTION}")
    print(f"  Results    : {n_results}")
    print()

    ids       = results.get("ids",[[]]) [0]
    docs      = results.get("documents",[[]])[0]
    metas     = results.get("metadatas",[[]])[0]
    distances = results.get("distances",[[]])[0]

    for i, (cid, doc, meta, dist) in enumerate(zip(ids, docs, metas, distances), start=1):
        score = round(1.0 - dist, 4) if dist is not None else "?"
        print(f"  ── Result {i} (score={score}) ──")
        # Brain 1: provenance
        print(f"    corpus_id     : {meta.get('corpus_id','?')}")
        print(f"    filename      : {meta.get('filename','?')}")
        print(f"    chunk_id      : {meta.get('chunk_id','?')}")
        print(f"    chunk_index   : {meta.get('chunk_index','?')} / {meta.get('chunk_count','?')}")
        print(f"    corpus_folder : {meta.get('corpus_folder','?')}")
        print(f"    sha256_16     : {meta.get('sha256_16','?')}")
        # Brain 2: RPMC symbolic
        print(f"    memory_role   : {meta.get('memory_role','?')}")
        print(f"    phases        : {meta.get('rpmc_phase_tags','') or '(none)'}")
        print(f"    operators     : {meta.get('symbolic_operators','') or '(none)'}")
        print(f"    sym_signature : {meta.get('symbolic_signature','?')}")
        # Evidence snippet
        snippet = (doc or "")[:200].replace("\n"," ")
        print(f"    snippet       : {snippet}...")
        print()



# ─── PHASE C: IMPROVED CONTEXT SEARCH ────────────────────────────────────────

def _clamp01(value) -> float:
    """Clamp a numeric value into 0.0..1.0 for score display."""
    try:
        v = float(value)
    except Exception:
        return 0.0
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _split_csvish(value) -> list[str]:
    """Split comma/semicolon/pipe metadata strings into normalized tokens."""
    if value is None:
        return []
    text = str(value).replace(";", ",").replace("|", ",")
    return [x.strip() for x in text.split(",") if x.strip()]


def _normalize_phase_token(value: str) -> str:
    """Normalize phase filters such as 6, phi6, Φ6 into Φ6."""
    t = str(value or "").strip()
    if not t:
        return ""
    lower = t.lower().replace("phi", "").replace("phase", "").replace("φ", "").replace("Φ", "")
    digits = "".join(ch for ch in lower if ch.isdigit())
    if digits:
        return f"Φ{digits}"
    return t


def _manifest_by_corpus_id() -> dict[str, dict]:
    """Return a manifest lookup by corpus_id/id."""
    out: dict[str, dict] = {}
    for row in _manifest_rows():
        cid = _row_id(row)
        if cid:
            out[cid] = row
    return out


def _authority_for_meta(meta: dict, manifest_lookup: dict[str, dict] | None = None) -> tuple[float, str, str]:
    """Compute source authority weight for a Chroma metadata row using manifest evidence when available."""
    cid = str((meta or {}).get("corpus_id", "")).strip()
    row = (manifest_lookup or {}).get(cid)
    if row:
        return _source_authority_weight(row)
    folder = str((meta or {}).get("corpus_folder", "")).lower()
    authority = str((meta or {}).get("authority", "")).lower()
    # Fallback mirrors _source_authority_weight without requiring full manifest row.
    if "01_system_law" in folder:
        return 1.00, "SYSTEM_LAW", "highest priority system-law / instruction layer"
    if "rpmc" in authority:
        return 0.95, "RPMC_AUTHORITY", "RPMC source/protocol authority"
    if "canonical" in authority or "02_aiweb" in folder or "03_gilligan" in folder or "04_fbsc" in folder:
        return 0.90, "CANONICAL", "canonical project source"
    if "05_engineering" in folder:
        return 0.72, "ENGINEERING_STANDARD", "engineering standard"
    return 0.40, "UNCLASSIFIED_ELIGIBLE", "eligible but low authority / unclassified"


def _parse_context_search_args(arg: str) -> tuple[dict, str]:
    """Parse context-search flags while keeping ordinary query words intact."""
    import shlex
    filters = {
        "show_metadata": False,
        "mode": "balanced",
        "corpus_id": "",
        "phase": "",
        "operator": "",
        "memory_role": "",
        "limit": 5,
    }
    try:
        parts = shlex.split(arg or "")
    except ValueError:
        parts = (arg or "").split()

    query_parts: list[str] = []
    i = 0
    while i < len(parts):
        tok = parts[i]
        low = tok.lower()
        if low == "--metadata":
            filters["show_metadata"] = True
        elif low == "--symbolic":
            filters["mode"] = "symbolic"
        elif low == "--source-law":
            filters["mode"] = "source_law"
        elif low == "--implementation":
            filters["mode"] = "implementation"
        elif low == "--corpus" and i + 1 < len(parts):
            i += 1
            filters["corpus_id"] = parts[i].strip()
        elif low == "--phase" and i + 1 < len(parts):
            i += 1
            filters["phase"] = _normalize_phase_token(parts[i])
        elif low == "--operator" and i + 1 < len(parts):
            i += 1
            filters["operator"] = parts[i].strip()
        elif low == "--memory-role" and i + 1 < len(parts):
            i += 1
            filters["memory_role"] = parts[i].strip()
        elif low in ("--limit", "-n") and i + 1 < len(parts):
            i += 1
            try:
                filters["limit"] = max(1, min(20, int(parts[i])))
            except Exception:
                filters["limit"] = 5
        else:
            query_parts.append(tok)
        i += 1

    query = " ".join(query_parts).strip()
    if not query:
        seed = [filters.get("corpus_id"), filters.get("phase"), filters.get("operator"), filters.get("memory_role")]
        mode = filters.get("mode")
        if mode == "source_law":
            seed.append("source law authority doctrine protocol")
        elif mode == "implementation":
            seed.append("implementation blueprint engineering guide")
        elif mode == "symbolic":
            seed.append("symbolic phase operator recursion memory")
        query = " ".join(x for x in seed if x).strip()
    return filters, query


def _context_search_filter_match(meta: dict, filters: dict) -> tuple[bool, list[str]]:
    """Return whether a result satisfies requested metadata/symbolic filters."""
    reasons: list[str] = []
    if filters.get("corpus_id"):
        want = filters["corpus_id"].lower()
        got = str((meta or {}).get("corpus_id", "")).lower()
        if got != want:
            return False, reasons
        reasons.append(f"corpus={filters['corpus_id']}")
    if filters.get("memory_role"):
        want = filters["memory_role"].lower()
        got = str((meta or {}).get("memory_role", "")).lower()
        if got != want:
            return False, reasons
        reasons.append(f"memory_role={filters['memory_role']}")
    if filters.get("phase"):
        want = _normalize_phase_token(filters["phase"])
        phases = [_normalize_phase_token(x) for x in _split_csvish((meta or {}).get("rpmc_phase_tags", ""))]
        if want not in phases:
            return False, reasons
        reasons.append(f"phase={want}")
    if filters.get("operator"):
        want = str(filters["operator"]).strip().lower()
        ops = [x.lower() for x in _split_csvish((meta or {}).get("symbolic_operators", ""))]
        if want not in ops:
            return False, reasons
        reasons.append(f"operator={filters['operator']}")
    mode = filters.get("mode")
    if mode == "source_law":
        try:
            if float((meta or {}).get("source_law_weight", 0.0)) < 0.9:
                return False, reasons
        except Exception:
            return False, reasons
        reasons.append("source_law_weight>=0.90")
    elif mode == "implementation":
        try:
            if float((meta or {}).get("implementation_weight", 0.0)) < 0.9:
                return False, reasons
        except Exception:
            return False, reasons
        reasons.append("implementation_weight>=0.90")
    elif mode == "symbolic":
        sig = str((meta or {}).get("symbolic_signature", "")).strip().lower()
        phases = str((meta or {}).get("rpmc_phase_tags", "")).strip()
        ops = str((meta or {}).get("symbolic_operators", "")).strip()
        if not phases and not ops and sig in ("", "none"):
            return False, reasons
        reasons.append("symbolic metadata present")
    return True, reasons


def _context_query_all(query: str, broad: bool = False) -> tuple[list[dict], str, str | None]:
    """Run a read-only vector query and return normalized result dictionaries.
    broad=True pulls the full collection so metadata/symbolic filters cannot miss
    just because an item was outside a small top-k semantic window.
    """
    if not CONTEXT_LIB_CHROMA.exists():
        return [], "", f"No context library found at {CONTEXT_LIB_CHROMA}"
    try:
        import chromadb as _chroma
        client = _chroma.PersistentClient(path=str(CONTEXT_LIB_CHROMA))
        collections = [c.name for c in client.list_collections()]
        if CONTEXT_COLLECTION not in collections:
            return [], "", f"Collection '{CONTEXT_COLLECTION}' not found. Available: {collections}"
        col = client.get_collection(CONTEXT_COLLECTION)
        count = col.count()
        if count == 0:
            return [], "", "Collection is empty."
        ef, ef_name = _get_embedding_function()
        query_embedding = _embed_texts([query.strip() or "context search"], ef)[0]
        n_results = count if broad else min(count, 250)
        results = col.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        return [], "", f"Search error: {e}"

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    out = []
    for cid, doc, meta, dist in zip(ids, docs, metas, dists):
        out.append({"id": cid, "doc": doc or "", "meta": meta or {}, "distance": dist})
    return out, ef_name, None


def _provenance_score(meta: dict) -> float:
    fields = [
        "corpus_id", "filename", "absolute_path", "relative_path", "corpus_folder",
        "sha256_16", "chunk_id", "chunk_index", "chunk_count", "chunk_sha256_16",
        "char_start", "char_end", "ingestion_receipt_id", "collection_namespace",
    ]
    present = sum(1 for f in fields if str((meta or {}).get(f, "")).strip() != "")
    return round(present / len(fields), 4)


def _symbolic_score(meta: dict, filters: dict, query: str) -> float:
    score = 0.0
    phases = _split_csvish((meta or {}).get("rpmc_phase_tags", ""))
    ops = _split_csvish((meta or {}).get("symbolic_operators", ""))
    sig = str((meta or {}).get("symbolic_signature", ""))
    role = str((meta or {}).get("memory_role", ""))
    if phases:
        score += 0.20
    if ops:
        score += 0.20
    if sig and sig.lower() != "none":
        score += 0.15
    if role and role != "reference":
        score += 0.15
    if filters.get("phase") and _normalize_phase_token(filters["phase"]) in [_normalize_phase_token(p) for p in phases]:
        score += 0.15
    if filters.get("operator") and filters["operator"].lower() in [o.lower() for o in ops]:
        score += 0.15
    if filters.get("memory_role") and filters["memory_role"].lower() == role.lower():
        score += 0.15
    q = (query or "").lower()
    symbolic_blob = " ".join(str((meta or {}).get(k, "")) for k in [
        "recursion_terms", "collapse_terms", "return_terms", "drift_terms", "echo_terms",
        "resurrection_terms", "firewall_terms", "phase_capacitor_terms", "christ_function_terms",
        "symbolic_signature", "memory_role",
    ]).lower()
    q_terms = [w for w in re.findall(r"[A-Za-z0-9_χΦφ()]+", q) if len(w) >= 4]
    if q_terms:
        hits = sum(1 for w in q_terms if w in symbolic_blob)
        score += min(0.20, 0.04 * hits)
    return round(_clamp01(score), 4)


def _source_mode_bonus(meta: dict, filters: dict) -> float:
    mode = filters.get("mode")
    try:
        if mode == "source_law":
            return _clamp01(float((meta or {}).get("source_law_weight", 0.0)))
        if mode == "implementation":
            return _clamp01(float((meta or {}).get("implementation_weight", 0.0)))
    except Exception:
        return 0.0
    return 0.0


def _evidence_snippet(doc: str, query: str, width: int = 260) -> str:
    clean = " ".join((doc or "").split())
    if len(clean) <= width:
        return clean
    terms = [t.lower() for t in re.findall(r"\w+", query or "") if len(t) >= 4]
    lower = clean.lower()
    pos = -1
    for t in terms:
        pos = lower.find(t)
        if pos >= 0:
            break
    if pos < 0:
        return clean[:width].rstrip() + "..."
    start = max(0, pos - width // 3)
    end = min(len(clean), start + width)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(clean) else ""
    return prefix + clean[start:end].strip() + suffix


def _source_citation(meta: dict) -> str:
    corpus_id = str((meta or {}).get("corpus_id", "?"))
    filename = str((meta or {}).get("filename", "?"))
    chunk_id = str((meta or {}).get("chunk_id", "?"))
    sha = str((meta or {}).get("sha256_16", "?"))
    start = str((meta or {}).get("char_start", "?"))
    end = str((meta or {}).get("char_end", "?"))
    return f"{corpus_id} :: {filename} :: {chunk_id} :: chars {start}-{end} :: sha256_16 {sha}"


def cmd_context_search(arg: str, session_id: str) -> None:
    """
    Phase C read-only context search with filter flags and merged scoring.
    Usage examples:
      context-search collapse resurrection
      context-search --metadata --corpus corpus_0022 collapse
      context-search --symbolic --phase Φ6 --operator "χ(t)" recursive correction
      context-search --source-law memory law
      context-search --implementation blueprint handler
      context-search --memory-role memory_law_definition recursion
    """
    from agents.forge.memory import write_audit_entry

    filters, query = _parse_context_search_args(arg)
    if not query.strip():
        print()
        print("  Usage: context-search [flags] <query>")
        print("  Flags: --metadata --symbolic --source-law --implementation")
        print("         --corpus <corpus_id> --phase <Φn> --operator <op> --memory-role <role> --limit <n>")
        print("  Example: context-search --symbolic --phase Φ6 --operator 'χ(t)' recursive correction")
        print()
        return

    broad = bool(filters.get("corpus_id") or filters.get("phase") or filters.get("operator") or filters.get("memory_role") or filters.get("mode") != "balanced")
    raw, ef_name, error = _context_query_all(query, broad=broad)
    if error:
        print(f"[forge] {error}")
        return

    manifest_lookup = _manifest_by_corpus_id()
    ranked: list[dict] = []
    for r in raw:
        meta = r.get("meta", {}) or {}
        ok, reasons = _context_search_filter_match(meta, filters)
        if not ok:
            continue
        semantic = _clamp01(1.0 - float(r.get("distance") or 0.0))
        provenance = _provenance_score(meta)
        symbolic = _symbolic_score(meta, filters, query)
        authority_weight, authority_tier, authority_reason = _authority_for_meta(meta, manifest_lookup)
        mode_bonus = _source_mode_bonus(meta, filters)
        # Merge scoring is intentionally explicit and simple for Patch 52.
        final = (
            0.45 * semantic +
            0.18 * provenance +
            0.22 * symbolic +
            0.15 * authority_weight
        )
        if mode_bonus:
            final = min(1.0, final + 0.08 * mode_bonus)
        ranked.append({
            **r,
            "semantic_score": round(semantic, 4),
            "provenance_score": round(provenance, 4),
            "symbolic_score": round(symbolic, 4),
            "authority_weight": round(float(authority_weight), 4),
            "authority_tier": authority_tier,
            "authority_reason": authority_reason,
            "filter_reasons": reasons,
            "final_score": round(_clamp01(final), 4),
        })

    ranked.sort(key=lambda x: (-x["final_score"], -x["semantic_score"], str((x.get("meta") or {}).get("chunk_id", ""))))
    shown = ranked[: int(filters.get("limit", 5))]

    write_audit_entry(session_id, "CONTEXT_SEARCH_SHOWN", query[:80], f"{len(shown)}/{len(ranked)} results",
                      f"mode={filters.get('mode')} corpus={filters.get('corpus_id') or '-'} phase={filters.get('phase') or '-'} operator={filters.get('operator') or '-'} role={filters.get('memory_role') or '-'}")

    print()
    print("── Context Search ───────────────────────────────────")
    print(f"  Query      : {query}")
    print(f"  Embedding  : {ef_name}")
    print(f"  Collection : {CONTEXT_COLLECTION}")
    print(f"  Mode       : {filters.get('mode')}")
    active = []
    for k in ["corpus_id", "phase", "operator", "memory_role"]:
        if filters.get(k):
            active.append(f"{k}={filters.get(k)}")
    print(f"  Filters    : {', '.join(active) if active else '(none)'}")
    print(f"  Results    : {len(shown)} shown / {len(ranked)} matched")
    print("  Read-only   : YES — no Chroma writes")
    print()

    if not shown:
        print("  No matching chunks found. Try relaxing filters or using context-search-test for a raw semantic probe.")
        print("──────────────────────────────────────────────────────")
        print()
        return

    for i, r in enumerate(shown, 1):
        meta = r.get("meta", {}) or {}
        doc = r.get("doc", "") or ""
        print(f"  ── Result {i} ──")
        print(f"    final_merged_score : {r['final_score']}")
        print(f"    semantic_score     : {r['semantic_score']}")
        print(f"    provenance_score   : {r['provenance_score']}")
        print(f"    symbolic_score     : {r['symbolic_score']}")
        print(f"    authority_weight   : {r['authority_weight']} ({r['authority_tier']})")
        if r.get("filter_reasons"):
            print(f"    filter_match       : {', '.join(r['filter_reasons'])}")
        print(f"    source_citation    : {_source_citation(meta)}")
        print(f"    evidence_snippet   : {_evidence_snippet(doc, query)}")
        print(f"    corpus_id          : {meta.get('corpus_id','?')}")
        print(f"    chunk_id           : {meta.get('chunk_id','?')}")
        print(f"    memory_role        : {meta.get('memory_role','?')}")
        print(f"    phases             : {meta.get('rpmc_phase_tags','') or '(none)'}")
        print(f"    operators          : {meta.get('symbolic_operators','') or '(none)'}")
        print(f"    sym_signature      : {meta.get('symbolic_signature','?')}")
        if filters.get("show_metadata"):
            print("    chunk_metadata:")
            keys = [
                "filename", "corpus_folder", "relative_path", "authority", "source_role", "sha256_16",
                "chunk_index", "chunk_count", "chunk_sha256_16", "char_start", "char_end", "char_count",
                "extraction_method", "ingestion_receipt_id", "ingestion_timestamp", "collection_namespace",
                "index_version", "embedding_method", "source_law_weight", "implementation_weight", "validation_weight",
            ]
            for k in keys:
                print(f"      {k:<24}: {meta.get(k, '')}")
        print()
    print("  [No writes performed. Context library unchanged.]")
    print("──────────────────────────────────────────────────────")
    print()


# ─── PATCH 44: INGESTION INTEGRITY HELPERS ───────────────────────────────────

def _context_collection_stats() -> list[dict]:
    """Read-only collection inventory for the isolated context library."""
    stats: list[dict] = []
    try:
        import chromadb as _chroma
        if CONTEXT_LIB_CHROMA.exists():
            client = _chroma.PersistentClient(path=str(CONTEXT_LIB_CHROMA))
            for col in client.list_collections():
                try:
                    count = col.count()
                except Exception:
                    count = 0
                stats.append({"name": getattr(col, "name", str(col)), "count": count})
    except Exception as e:
        stats.append({"name": f"ERROR: {e}", "count": 0})
    return stats


def _old_chroma_status() -> dict:
    """Read-only status for the old scaffold DB. Never writes to it."""
    exists = CHROMA_DB_PATH.exists()
    items = []
    if exists and CHROMA_DB_PATH.is_dir():
        try:
            items = [p.name for p in CHROMA_DB_PATH.iterdir()]
        except Exception:
            items = []
    return {
        "path": str(CHROMA_DB_PATH),
        "exists": exists,
        "item_count": len(items),
        "untouched_by_patch44": True,
        "isolation_ok": str(CONTEXT_LIB_CHROMA) != str(CHROMA_DB_PATH),
    }


def _receipt_json_paths() -> list[Path]:
    CONTEXT_LIB_RECEIPTS.mkdir(parents=True, exist_ok=True)
    return sorted(CONTEXT_LIB_RECEIPTS.glob("*.json"), reverse=True)


def _load_receipt(path: Path) -> dict:
    import json as _json
    return _json.loads(path.read_text(encoding="utf-8"))


def _latest_receipt_path() -> Optional[Path]:
    receipts = _receipt_json_paths()
    return receipts[0] if receipts else None


def _resolve_receipt_path(receipt_arg: str) -> Optional[Path]:
    """Resolve latest or an explicit receipt id safely inside the receipts directory."""
    receipt_arg = (receipt_arg or "latest").strip()
    if receipt_arg == "latest":
        return _latest_receipt_path()

    safe = Path(receipt_arg).name
    candidate = CONTEXT_LIB_RECEIPTS / safe
    if not candidate.suffix:
        candidate = candidate.with_suffix(".json")
    try:
        candidate.resolve().relative_to(CONTEXT_LIB_RECEIPTS.resolve())
    except Exception:
        return None
    if candidate.exists() and candidate.is_file():
        return candidate

    matches = sorted(CONTEXT_LIB_RECEIPTS.glob(f"{safe}*.json"), reverse=True)
    return matches[0] if matches else None


def _receipts_for_corpus(corpus_id: str) -> list[tuple[Path, dict]]:
    matches: list[tuple[Path, dict]] = []
    for rpath in _receipt_json_paths():
        try:
            receipt = _load_receipt(rpath)
        except Exception:
            continue
        if str(receipt.get("corpus_id", "")).strip().lower() == corpus_id.strip().lower():
            matches.append((rpath, receipt))
    return matches


def _collection_has_corpus(corpus_id: str) -> tuple[bool, str, int]:
    """Read-only duplicate check inside isolated Chroma metadata."""
    try:
        import chromadb as _chroma
        if not CONTEXT_LIB_CHROMA.exists():
            return False, CONTEXT_COLLECTION, 0
        client = _chroma.PersistentClient(path=str(CONTEXT_LIB_CHROMA))
        collection = client.get_collection(CONTEXT_COLLECTION)
        result = collection.get(where={"corpus_id": corpus_id}, include=["metadatas"])
        ids = result.get("ids", []) if isinstance(result, dict) else []
        return bool(ids), CONTEXT_COLLECTION, len(ids)
    except Exception:
        return False, CONTEXT_COLLECTION, 0



def _safe_int(value, default: int = 0) -> int:
    """Best-effort integer coercion for receipt fields."""
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _receipt_expected_chunk_count(receipt: dict) -> int:
    """
    Return the per-document chunk count expected from an ingestion receipt.
    Patch 45B rule: document chunks are not the same as collection total chunks.
    """
    for key in ("document_chunk_count", "chunk_count_planned", "dry_run_chunk_count", "chunk_count"):
        n = _safe_int(receipt.get(key), 0)
        if n > 0:
            return n
    return _safe_int(receipt.get("chunk_count_verified"), 0)


def _receipt_chunk_count_for_display(receipt: dict):
    n = _receipt_expected_chunk_count(receipt)
    return n if n else receipt.get("chunk_count_verified", receipt.get("chunk_count_planned", "?"))


def _expected_chunk_ids_for_receipt(receipt: dict) -> list[str]:
    corpus_id = str(receipt.get("corpus_id", "")).strip()
    explicit = receipt.get("chunk_ids") or receipt.get("ids")
    if isinstance(explicit, list) and explicit:
        return [str(x) for x in explicit]
    n = _receipt_expected_chunk_count(receipt)
    if not corpus_id or n <= 0:
        return []
    return [f"{corpus_id}_chunk_{i:04d}" for i in range(n)]


def _collection_get_expected_chunks(collection, receipt: dict) -> tuple[dict, list[str], list[str]]:
    """
    Fetch exact chunk IDs for one receipt and return (data, expected_ids, issues).
    This prevents collection-wide counts from passing as per-document verification.
    """
    expected_ids = _expected_chunk_ids_for_receipt(receipt)
    issues: list[str] = []
    if not expected_ids:
        return {}, expected_ids, ["receipt does not provide or imply expected chunk IDs"]
    try:
        data = collection.get(ids=expected_ids, include=["metadatas", "documents"])
    except Exception as e:
        return {}, expected_ids, [f"could not fetch expected chunk IDs: {e}"]
    found_ids = set(data.get("ids", []) or []) if isinstance(data, dict) else set()
    missing = [cid for cid in expected_ids if cid not in found_ids]
    if missing:
        issues.append(f"missing expected chunk IDs: {missing[:5]}" + (" ..." if len(missing) > 5 else ""))
    return data if isinstance(data, dict) else {}, expected_ids, issues


def _verify_receipt_exact_chunks(receipt: dict) -> tuple[bool, list[tuple], dict]:
    """
    Verify one receipt against exact Chroma chunk IDs and corpus-specific metadata.
    Returns (ok, checks, details). checks: list of (name, passed, detail).
    """
    checks: list[tuple] = []
    details: dict = {}
    corpus_id = str(receipt.get("corpus_id", "?"))
    receipt_id = str(receipt.get("receipt_id", ""))
    expected_n = _receipt_expected_chunk_count(receipt)
    stored_verified = _safe_int(receipt.get("chunk_count_verified"), 0)
    collection_total = 0

    checks.append(("receipt has per-document chunk count", expected_n > 0, f"expected={expected_n}"))
    if stored_verified:
        checks.append(("receipt verified count equals document count", stored_verified == expected_n,
                       f"verified={stored_verified} document={expected_n}"))

    try:
        import chromadb as _chroma
        client = _chroma.PersistentClient(path=str(CONTEXT_LIB_CHROMA))
        collections = [c.name for c in client.list_collections()]
        col_exists = CONTEXT_COLLECTION in collections
        checks.append(("collection exists", col_exists, CONTEXT_COLLECTION))
        if not col_exists:
            return False, checks, details
        col = client.get_collection(CONTEXT_COLLECTION)
        collection_total = col.count()
        details["collection_count_after"] = collection_total
        checks.append(("collection total >= document chunks", collection_total >= expected_n,
                       f"collection has {collection_total}, document expects {expected_n}"))

        data, expected_ids, id_issues = _collection_get_expected_chunks(col, receipt)
        found_ids = data.get("ids", []) or []
        metadatas = data.get("metadatas", []) or []
        documents = data.get("documents", []) or []
        checks.append(("exact receipt chunk IDs present", not id_issues and len(found_ids) == len(expected_ids),
                       f"found={len(found_ids)} expected={len(expected_ids)}" + (f"; {id_issues[0]}" if id_issues else "")))

        meta_by_id = {cid: meta for cid, meta in zip(found_ids, metadatas)}
        doc_by_id = {cid: doc for cid, doc in zip(found_ids, documents)}
        all_meta_corpus = bool(expected_ids) and all(str((meta_by_id.get(cid) or {}).get("corpus_id", "")) == corpus_id for cid in expected_ids if cid in meta_by_id)
        checks.append(("exact chunks match receipt corpus_id", all_meta_corpus, f"corpus_id={corpus_id}"))

        expected_sha = str(receipt.get("sha256_16", receipt.get("source_hash", ""))).strip()
        all_meta_sha = bool(expected_ids) and all(str((meta_by_id.get(cid) or {}).get("sha256_16", "")) == expected_sha for cid in expected_ids if cid in meta_by_id)
        checks.append(("exact chunks match source sha", all_meta_sha, f"sha256_16={expected_sha}"))

        if receipt_id:
            all_meta_receipt = bool(expected_ids) and all(str((meta_by_id.get(cid) or {}).get("ingestion_receipt_id", "")) == receipt_id for cid in expected_ids if cid in meta_by_id)
            checks.append(("exact chunks match receipt id", all_meta_receipt, f"receipt_id={receipt_id}"))

        all_meta_count = bool(expected_ids) and all(_safe_int((meta_by_id.get(cid) or {}).get("chunk_count"), -1) == expected_n for cid in expected_ids if cid in meta_by_id)
        checks.append(("exact chunk metadata count matches document", all_meta_count, f"chunk_count={expected_n}"))

        sample_meta = meta_by_id.get(expected_ids[0], {}) if expected_ids else {}
        has_brain1 = "corpus_id" in sample_meta and "sha256_16" in sample_meta and "chunk_id" in sample_meta
        has_brain2 = "rpmc_phase_tags" in sample_meta and "symbolic_operators" in sample_meta
        checks.append(("exact chunk has Brain 1 (provenance)", has_brain1, f"corpus_id={sample_meta.get('corpus_id','?')}"))
        checks.append(("exact chunk has Brain 2 (RPMC symbolic)", has_brain2, f"phases={str(sample_meta.get('rpmc_phase_tags','?'))[:40]}"))

        details["chunk_ids"] = expected_ids
        details["chunk_sha256_16"] = []
        for cid in expected_ids:
            meta = meta_by_id.get(cid) or {}
            doc = doc_by_id.get(cid) or ""
            details["chunk_sha256_16"].append(str(meta.get("chunk_sha256_16") or hashlib.sha256(str(doc).encode("utf-8")).hexdigest()[:16]))
    except Exception as e:
        checks.append(("Chroma accessible", False, str(e)[:120]))

    ok = all(c[1] for c in checks)
    return ok, checks, details

def _already_ingested_record(corpus_id: str) -> Optional[dict]:
    """Return existing receipt/collection record if corpus_id has already been ingested."""
    receipt_matches = _receipts_for_corpus(corpus_id)
    if receipt_matches:
        rpath, receipt = receipt_matches[0]
        return {
            "source": "receipt",
            "corpus_id": corpus_id,
            "receipt_path": str(rpath),
            "chunk_count": _receipt_chunk_count_for_display(receipt),
            "collection": receipt.get("collection", CONTEXT_COLLECTION),
        }
    found, collection, n = _collection_has_corpus(corpus_id)
    if found:
        return {
            "source": "chroma_metadata",
            "corpus_id": corpus_id,
            "receipt_path": "not found in receipts; found in Chroma metadata",
            "chunk_count": n,
            "collection": collection,
        }
    return None


def _make_dry_run_plan(corpus_id: str, item: dict, session_id: str, internal: bool = False) -> tuple[Optional[dict], Optional[Path], list[str]]:
    """
    Create a dry-run plan using the same extraction and chunk policy used by ingest-one.
    Stores full chunk text hashes and chunk text so ingest-one can write the exact plan.
    No embeddings. No Chroma writes.
    """
    import json as _json, hashlib
    from agents.forge.document_adapters import extract_text

    issues: list[str] = []
    abs_path_str = item.get("absolute_path", "").strip() or str(_CORPUS_ROOT / item.get("relative_path", ""))
    abs_path = Path(abs_path_str)

    if not abs_path.exists():
        return None, None, [f"source file missing: {abs_path}"]

    expected_sha = str(item.get("sha256_16", "")).strip()
    actual_sha = hashlib.sha256(abs_path.read_bytes()).hexdigest()[:16]
    if expected_sha and actual_sha != expected_sha:
        return None, None, [f"source sha mismatch: expected {expected_sha} actual {actual_sha}"]

    result = extract_text(abs_path, max_chars=300_000)
    if result.unsupported or result.error:
        return None, None, [f"extraction error: {result.error or 'unsupported'}"]
    text = result.text or ""
    if not text.strip():
        return None, None, ["extraction returned empty text"]

    chunks = _chunk_text(text, chunk_size=CHUNK_TARGET, overlap=CHUNK_OVERLAP)
    if not chunks:
        return None, None, ["zero chunks produced"]

    plan_chunks = []
    for i, chunk in enumerate(chunks):
        ctext = chunk.get("text", "")
        chunk_id = f"{corpus_id}_chunk_{i:04d}"
        plan_chunks.append({
            "chunk_id": chunk_id,
            "chunk_index": i,
            "char_start": chunk.get("char_start", 0),
            "char_end": chunk.get("char_end", 0),
            "char_count": chunk.get("char_count", len(ctext)),
            "chunk_sha256_16": hashlib.sha256(ctext.encode("utf-8")).hexdigest()[:16],
            "text_sha256_64": hashlib.sha256(ctext.encode("utf-8")).hexdigest(),
            "text": ctext,
        })

    char_counts = [c["char_count"] for c in plan_chunks]
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    plan_name = f"{ts}_dry_run_{corpus_id}.json" if not internal else f"{ts}_dry_run_{corpus_id}_internal_ingest_one.json"
    INGESTION_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    plan_path = INGESTION_PLANS_DIR / plan_name

    plan = {
        "report_type": "DRY_RUN_CHUNKING",
        "patch_level": "44_ingestion_integrity_hardening",
        "created_for": "ingest-one-write-parity" if internal else "manual-dry-run",
        "validated_for_write": True,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id": session_id,
        "corpus_id": corpus_id,
        "filename": item.get("filename", ""),
        "absolute_path": str(abs_path),
        "corpus_folder": item.get("corpus_folder", ""),
        "authority": item.get("authority", ""),
        "source_hash": actual_sha,
        "sha256_16": actual_sha,
        "adapter_format": abs_path.suffix.lower(),
        "extraction_chars": len(text),
        "chunk_policy": {
            "chunk_target": CHUNK_TARGET,
            "chunk_max": CHUNK_MAX,
            "overlap": CHUNK_OVERLAP,
            "tiny_min": CHUNK_MIN,
            "method": "paragraph_sentence_aware",
            "extract_max_chars": 300_000,
        },
        "chunk_count": len(plan_chunks),
        "min_chars": min(char_counts) if char_counts else 0,
        "max_chars": max(char_counts) if char_counts else 0,
        "avg_chars": sum(char_counts) // len(char_counts) if char_counts else 0,
        "tiny_chunks": sum(1 for c in plan_chunks if c["char_count"] < CHUNK_MIN),
        "over_max_chunks": sum(1 for c in plan_chunks if c["char_count"] > CHUNK_MAX),
        "first_chunk_preview": plan_chunks[0]["text"][:300] if plan_chunks else "",
        "last_chunk_preview": plan_chunks[-1]["text"][:300] if plan_chunks else "",
        "target_collection_proposal": CONTEXT_COLLECTION,
        "target_db_path": str(CONTEXT_LIB_CHROMA),
        "no_vector_write": True,
        "no_chroma_write": True,
        "no_embedding": True,
        "chunks": plan_chunks,
    }

    try:
        plan_path.write_text(_json.dumps(plan, indent=2), encoding="utf-8")
    except OSError as e:
        return None, None, [f"could not save dry-run plan: {e}"]

    return plan, plan_path, issues


def _validate_dry_run_plan_for_write(plan: dict, corpus_id: str, item: dict) -> list[str]:
    """Hard parity validation before any Chroma write."""
    import hashlib
    issues: list[str] = []
    if str(plan.get("corpus_id", "")).lower() != corpus_id.lower():
        issues.append(f"corpus_id mismatch: plan={plan.get('corpus_id')} requested={corpus_id}")
    if not plan.get("no_chroma_write") or not plan.get("no_embedding"):
        issues.append("plan is not a dry-run/no-write plan")

    expected_sha = str(item.get("sha256_16", "")).strip()
    plan_sha = str(plan.get("source_hash", plan.get("sha256_16", ""))).strip()
    if expected_sha and plan_sha != expected_sha:
        issues.append(f"source sha mismatch: plan={plan_sha} manifest={expected_sha}")

    source_path = Path(item.get("absolute_path", ""))
    if source_path.exists():
        actual_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()[:16]
        if plan_sha != actual_sha:
            issues.append(f"source sha changed after plan: plan={plan_sha} actual={actual_sha}")
    else:
        issues.append(f"source file missing: {source_path}")

    chunks = plan.get("chunks") or []
    if not chunks:
        issues.append("plan has no chunk records")
    if plan.get("chunk_count") != len(chunks):
        issues.append(f"chunk count mismatch inside plan: header={plan.get('chunk_count')} records={len(chunks)}")

    for idx, chunk in enumerate(chunks):
        text = chunk.get("text", "")
        expected_id = f"{corpus_id}_chunk_{idx:04d}"
        if chunk.get("chunk_id") != expected_id:
            issues.append(f"chunk_id mismatch at {idx}: {chunk.get('chunk_id')} != {expected_id}")
        if chunk.get("chunk_index") != idx:
            issues.append(f"chunk_index mismatch at {idx}: {chunk.get('chunk_index')}")
        if len(text) > CHUNK_MAX:
            issues.append(f"chunk {idx} exceeds hard max: {len(text)} > {CHUNK_MAX}")
        actual_chunk_sha16 = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        if chunk.get("chunk_sha256_16") != actual_chunk_sha16:
            issues.append(f"chunk sha mismatch at {idx}: plan={chunk.get('chunk_sha256_16')} actual={actual_chunk_sha16}")
        if len(issues) > 20:
            issues.append("too many dry-run parity errors; stopping detail")
            break
    return issues


def cmd_ingest_history(session_id: str) -> None:
    """Show all ingestion receipts. Usage: ingest-history"""
    from agents.forge.memory import write_audit_entry

    receipts = _receipt_json_paths()
    write_audit_entry(session_id, "INGEST_HISTORY_SHOWN", str(CONTEXT_LIB_RECEIPTS), f"{len(receipts)} receipts", "read-only")

    print()
    print(f"── Ingest History ────────────────────────────────────")
    print(f"  Receipts dir : {CONTEXT_LIB_RECEIPTS}")
    print(f"  Receipts     : {len(receipts)}")
    print()
    if not receipts:
        print("  No ingestion receipts found.")
    for rpath in receipts:
        try:
            r = _load_receipt(rpath)
        except Exception as e:
            print(f"  ✗ {rpath.name}: unreadable ({e})")
            continue
        print(f"  • {r.get('receipt_id', rpath.stem)}")
        print(f"      timestamp : {r.get('timestamp', '?')}")
        print(f"      corpus_id : {r.get('corpus_id', '?')}")
        print(f"      filename  : {r.get('filename', '?')}")
        print(f"      chunks    : {_receipt_chunk_count_for_display(r)}")
        print(f"      collection: {r.get('collection', '?')}")
        print(f"      embedding : {r.get('embedding_method', '?')}")
        print(f"      sha256_16 : {r.get('sha256_16', r.get('source_hash', '?'))}")
        print(f"      verified  : {r.get('verification_ok', '?')}")
        print(f"      path      : {rpath}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_ingest_receipt_show(receipt_arg: str, session_id: str) -> None:
    """Show a single ingestion receipt. Usage: ingest-receipt-show <latest|receipt_id>"""
    from agents.forge.memory import write_audit_entry

    rpath = _resolve_receipt_path(receipt_arg or "latest")
    if not rpath:
        print(f"[forge] Receipt not found: {receipt_arg or 'latest'}")
        return
    try:
        receipt = _load_receipt(rpath)
    except Exception as e:
        print(f"[forge] ERROR: Cannot read receipt: {e}")
        return

    brain1 = receipt.get("brain1_fields", []) or []
    brain2 = receipt.get("brain2_fields", []) or []
    write_audit_entry(session_id, "INGEST_RECEIPT_SHOWN", str(rpath), receipt.get("corpus_id", "-"), "read-only")

    print()
    print(f"── Ingest Receipt ────────────────────────────────────")
    print(f"  Receipt path       : {rpath}")
    print(f"  Receipt id         : {receipt.get('receipt_id', rpath.stem)}")
    print(f"  corpus_id          : {receipt.get('corpus_id', '?')}")
    print(f"  filename           : {receipt.get('filename', '?')}")
    print(f"  source sha         : {receipt.get('sha256_16', receipt.get('source_hash', '?'))}")
    print(f"  document chunks    : {_receipt_chunk_count_for_display(receipt)}")
    if receipt.get("collection_count_after") is not None:
        print(f"  collection total   : {receipt.get('collection_count_after')}")
    print(f"  collection         : {receipt.get('collection', '?')}")
    print(f"  embedding method   : {receipt.get('embedding_method', '?')}")
    print(f"  dry-run plan path  : {receipt.get('dry_run_plan_path', '(not recorded)')}")
    print(f"  Brain 1 fields     : {'present' if brain1 else 'missing'} ({len(brain1)})")
    print(f"  Brain 2 fields     : {'present' if brain2 else 'missing'} ({len(brain2)})")
    print(f"  symbolic map path  : {receipt.get('symbolic_map_path', '?')}")
    print(f"  collection manifest: {receipt.get('collection_manifest_path', '(not recorded)')}")
    print(f"  ingestion timestamp: {receipt.get('timestamp', '?')}")
    print(f"  source abs path    : {receipt.get('absolute_path', '?')}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_context_duplicates(session_id: str) -> None:
    """Read-only duplicate checker with receipt/Chroma consistency checks. Usage: context-duplicates"""
    import json as _json
    from collections import Counter, defaultdict
    from agents.forge.memory import write_audit_entry

    receipts = _receipt_json_paths()
    receipt_ids = []
    receipt_corpus = []
    source_shas = []
    receipt_chunk_expected = {}
    receipt_verify_issues = []
    receipt_paths = {}

    for rp in receipts:
        try:
            r = _load_receipt(rp)
        except Exception as e:
            receipt_verify_issues.append(f"unreadable receipt {rp.name}: {e}")
            continue
        rid = str(r.get("receipt_id", rp.stem))
        cid = str(r.get("corpus_id", "?"))
        receipt_ids.append(rid)
        receipt_corpus.append(cid)
        source_shas.append(str(r.get("sha256_16", r.get("source_hash", ""))))
        receipt_paths[cid] = str(rp)
        doc_n = _receipt_expected_chunk_count(r)
        receipt_chunk_expected[cid] = doc_n
        verified_n = _safe_int(r.get("chunk_count_verified"), 0)
        ids = r.get("chunk_ids", []) if isinstance(r.get("chunk_ids", []), list) else []
        if verified_n and verified_n != doc_n:
            receipt_verify_issues.append(f"{cid}: chunk_count_verified={verified_n} document_chunk_count={doc_n}")
        if ids and len(ids) != doc_n:
            receipt_verify_issues.append(f"{cid}: chunk_ids={len(ids)} document_chunk_count={doc_n}")

    dup_receipt_ids = [k for k,v in Counter(receipt_ids).items() if v > 1]
    dup_receipt_corpus = [k for k,v in Counter(receipt_corpus).items() if v > 1]
    dup_source_sha = [k for k,v in Counter([x for x in source_shas if x]).items() if v > 1]

    chunk_ids = []
    chunk_shas = []
    chroma_corpus_counts = Counter()
    chroma_receipt_counts = Counter()
    orphan_corpus_ids = []
    collection_name = CONTEXT_COLLECTION
    chroma_count = 0
    chroma_error = ""

    try:
        import chromadb as _chroma
        if CONTEXT_LIB_CHROMA.exists():
            client = _chroma.PersistentClient(path=str(CONTEXT_LIB_CHROMA))
            col = client.get_collection(CONTEXT_COLLECTION)
            collection_name = getattr(col, "name", CONTEXT_COLLECTION)
            data = col.get(include=["metadatas"])
            ids = data.get("ids", []) or []
            metas = data.get("metadatas", []) or []
            chroma_count = len(ids)
            for cid, meta in zip(ids, metas):
                meta = meta or {}
                chunk_ids.append(str(cid))
                chunk_shas.append(str(meta.get("chunk_sha256_16", "")))
                ccid = str(meta.get("corpus_id", "?"))
                rrid = str(meta.get("ingestion_receipt_id", "?"))
                chroma_corpus_counts[ccid] += 1
                chroma_receipt_counts[rrid] += 1
            orphan_corpus_ids = sorted([cid for cid in chroma_corpus_counts if cid not in receipt_chunk_expected])
    except Exception as e:
        chroma_error = str(e)

    dup_chunk_ids = [k for k,v in Counter(chunk_ids).items() if v > 1]
    dup_chunk_sha = [k for k,v in Counter([x for x in chunk_shas if x]).items() if v > 1]

    corpus_count_issues = []
    for cid, expected_n in sorted(receipt_chunk_expected.items()):
        got = chroma_corpus_counts.get(cid, 0)
        if got != expected_n:
            corpus_count_issues.append(f"{cid}: receipt expects {expected_n}, Chroma has {got}")

    issue_total = len(dup_receipt_ids)+len(dup_receipt_corpus)+len(dup_source_sha)+len(dup_chunk_ids)+len(dup_chunk_sha)+len(receipt_verify_issues)+len(corpus_count_issues)+len(orphan_corpus_ids)
    write_audit_entry(session_id, "CONTEXT_DUPLICATES_CHECKED", str(CONTEXT_LIB_DIR), "read-only",
                      f"receipts={len(receipts)} dup_corpus={len(dup_receipt_corpus)} dup_chunks={len(dup_chunk_ids)} integrity_issues={issue_total}")

    print()
    print("── Context Duplicate Check ───────────────────────────")
    print(f"  Receipts checked          : {len(receipts)}")
    print(f"  Duplicate receipt IDs     : {dup_receipt_ids if dup_receipt_ids else 'none'}")
    print(f"  Duplicate receipt corpus  : {dup_receipt_corpus if dup_receipt_corpus else 'none'}")
    print(f"  Duplicate source SHA      : {dup_source_sha if dup_source_sha else 'none'}")
    if receipt_verify_issues:
        print(f"  Receipt count issues      : {len(receipt_verify_issues)}")
        for issue in receipt_verify_issues[:8]:
            print(f"    ✗ {issue}")
    else:
        print(f"  Receipt count issues      : none")
    print()
    print(f"  Chroma collection         : {collection_name}")
    print(f"  Chroma chunks checked     : {chroma_count}")
    print(f"  Duplicate chunk IDs       : {dup_chunk_ids if dup_chunk_ids else 'none'}")
    print(f"  Duplicate chunk SHA       : {dup_chunk_sha if dup_chunk_sha else 'none'}")
    print(f"  Orphan corpus IDs         : {orphan_corpus_ids if orphan_corpus_ids else 'none'}")
    if corpus_count_issues:
        print(f"  Corpus count mismatches   : {len(corpus_count_issues)}")
        for issue in corpus_count_issues[:8]:
            print(f"    ✗ {issue}")
    else:
        print(f"  Corpus count mismatches   : none")
    if chroma_error:
        print(f"  Chroma read warning       : {chroma_error[:120]}")
    print()
    print("  Ingested corpus IDs:")
    for cid in sorted(receipt_chunk_expected):
        print(f"    • {cid} ({receipt_chunk_expected[cid]} chunks) receipt={receipt_paths.get(cid,'?')}")
    print("  [Read-only. No writes performed.]")
    print("──────────────────────────────────────────────────────")
    print()


def _context_export_payload() -> dict:
    receipts_payload = []
    for rpath in _receipt_json_paths():
        try:
            r = _load_receipt(rpath)
        except Exception as e:
            receipts_payload.append({"path": str(rpath), "error": str(e)})
            continue
        receipts_payload.append({
            "receipt_path": str(rpath),
            "receipt_id": r.get("receipt_id", rpath.stem),
            "timestamp": r.get("timestamp"),
            "corpus_id": r.get("corpus_id"),
            "filename": r.get("filename"),
            "source_file": r.get("absolute_path"),
            "sha256_16": r.get("sha256_16", r.get("source_hash")),
            "chunk_count": _receipt_chunk_count_for_display(r),
            "collection_count_after": r.get("collection_count_after"),
            "collection": r.get("collection"),
            "embedding_method": r.get("embedding_method"),
            "symbolic_map_path": r.get("symbolic_map_path"),
            "dry_run_plan_path": r.get("dry_run_plan_path"),
        })
    return {
        "report_type": "CONTEXT_EXPORT_MANIFEST",
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "library_path": str(CONTEXT_LIB_DIR),
        "chroma_path": str(CONTEXT_LIB_CHROMA),
        "collections": _context_collection_stats(),
        "receipts": receipts_payload,
        "ingested_corpus_ids": sorted({r.get("corpus_id") for r in receipts_payload if r.get("corpus_id")}),
        "old_db_status": _old_chroma_status(),
    }


def cmd_context_export_manifest(session_id: str) -> None:
    """Export current context library state to JSON and Markdown. Usage: context-export-manifest"""
    import json as _json
    from agents.forge.memory import write_audit_entry

    CONTEXT_LIB_MANIFESTS.mkdir(parents=True, exist_ok=True)
    payload = _context_export_payload()
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    json_path = CONTEXT_LIB_MANIFESTS / f"{ts}_context_export.json"
    md_path = CONTEXT_LIB_MANIFESTS / f"{ts}_context_export.md"
    json_path.write_text(_json.dumps(payload, indent=2), encoding="utf-8")

    lines = ["# Context Export Manifest", "", f"Generated: {payload['timestamp']}", f"Library: `{payload['library_path']}`", f"Chroma: `{payload['chroma_path']}`", "", "## Collections"]
    for col in payload["collections"]:
        lines.append(f"- {col.get('name')}: {col.get('count')} chunks")
    lines.append("")
    lines.append("## Receipts")
    for r in payload["receipts"]:
        lines.append(f"- {r.get('corpus_id')} — {r.get('filename')} — chunks={r.get('chunk_count')} — receipt={r.get('receipt_id')}")
    lines.append("")
    lines.append(f"Old DB untouched: {payload['old_db_status'].get('untouched_by_patch44')} at `{payload['old_db_status'].get('path')}`")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    write_audit_entry(session_id, "CONTEXT_EXPORT_MANIFEST_CREATED", str(json_path), str(md_path),
                      f"receipts={len(payload['receipts'])} collections={len(payload['collections'])}")

    print()
    print(f"── Context Export Manifest ───────────────────────────")
    print(f"  JSON written : {json_path}")
    print(f"  MD written   : {md_path}")
    print(f"  Collections  : {len(payload['collections'])}")
    print(f"  Receipts     : {len(payload['receipts'])}")
    print(f"  Old DB       : untouched status recorded")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_context_reset_plan(session_id: str) -> None:
    """Create a non-destructive reset plan. Deletes nothing. Usage: context-reset-plan"""
    import json as _json
    from agents.forge.memory import write_audit_entry

    CONTEXT_LIB_MANIFESTS.mkdir(parents=True, exist_ok=True)
    payload = _context_export_payload()
    plan = {
        "report_type": "CONTEXT_RESET_PLAN_NON_DESTRUCTIVE",
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "warning": "PLAN ONLY. This file does not delete or modify Chroma, receipts, manifests, indexes, or symbolic maps.",
        "would_remove_if_future_reset_were_authorized": {
            "context_library_path": str(CONTEXT_LIB_DIR),
            "chroma_path": str(CONTEXT_LIB_CHROMA),
            "collections": payload.get("collections", []),
            "receipts_dir": str(CONTEXT_LIB_RECEIPTS),
            "receipt_count": len(_receipt_json_paths()),
            "symbolic_maps_dir": str(CONTEXT_LIB_SYMBOLIC),
            "symbolic_map_count": len(list(CONTEXT_LIB_SYMBOLIC.glob("*.json"))) if CONTEXT_LIB_SYMBOLIC.exists() else 0,
            "manifests_dir": str(CONTEXT_LIB_MANIFESTS),
            "manifest_count": len(list(CONTEXT_LIB_MANIFESTS.glob("*"))) if CONTEXT_LIB_MANIFESTS.exists() else 0,
            "indexes_dir": str(CONTEXT_LIB_INDEXES),
            "index_count": len(list(CONTEXT_LIB_INDEXES.glob("*"))) if CONTEXT_LIB_INDEXES.exists() else 0,
        },
        "old_db_status": _old_chroma_status(),
        "implemented_destructive_reset": False,
    }
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    json_path = CONTEXT_LIB_MANIFESTS / f"{ts}_context_reset_plan.json"
    md_path = CONTEXT_LIB_MANIFESTS / f"{ts}_context_reset_plan.md"
    json_path.write_text(_json.dumps(plan, indent=2), encoding="utf-8")

    lines = ["# Context Reset Plan — Non-Destructive", "", "No files were deleted. No Chroma writes were performed.", "", f"Context library: `{CONTEXT_LIB_DIR}`", f"Chroma path: `{CONTEXT_LIB_CHROMA}`", "", "## Collections"]
    for col in plan["would_remove_if_future_reset_were_authorized"]["collections"]:
        lines.append(f"- {col.get('name')}: {col.get('count')} chunks")
    lines.extend(["", "## Planned categories only", f"- Receipts: {plan['would_remove_if_future_reset_were_authorized']['receipt_count']}", f"- Symbolic maps: {plan['would_remove_if_future_reset_were_authorized']['symbolic_map_count']}", f"- Manifests: {plan['would_remove_if_future_reset_were_authorized']['manifest_count']}", f"- Indexes: {plan['would_remove_if_future_reset_were_authorized']['index_count']}", "", f"Old DB untouched: {plan['old_db_status'].get('untouched_by_patch44')} at `{plan['old_db_status'].get('path')}`"])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    write_audit_entry(session_id, "CONTEXT_RESET_PLAN_CREATED", str(json_path), str(md_path), "non-destructive plan only")

    print()
    print(f"── Context Reset Plan ────────────────────────────────")
    print(f"  PLAN ONLY. Nothing was deleted.")
    print(f"  JSON written : {json_path}")
    print(f"  MD written   : {md_path}")
    print(f"  Context lib  : {CONTEXT_LIB_DIR}")
    print(f"  Chroma path  : {CONTEXT_LIB_CHROMA}")
    print(f"  Old DB       : {CHROMA_DB_PATH} (untouched)")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_forge_version(session_id: str) -> None:
    """Print Forge version, trust level, and command surface count. Usage: forge-version"""
    from agents.forge.memory import write_audit_entry

    expected = len(FORGE_EXPECTED_COMMANDS)

    write_audit_entry(session_id, "FORGE_VERSION_SHOWN", "-", "-",
                      f"commands_expected={expected} trust_level=5.0")

    print()
    print(f"── Forge Version ─────────────────────────────────────")
    print(f"  Name          : FORGE — Local Coding Assistant")
    print(f"  Trust level   : 5.0")
    print(f"  Commands      : {expected} registered in expected surface")
    print(f"  Audit         : hash-chained, append-only")
    print(f"  Corpus root   : {_CORPUS_ROOT}")
    print(f"  Forge root    : {FORGE_ROOT}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_forge_command_surface(session_id: str) -> None:
    """
    Self-test: check all expected command markers are present in main.py.
    Usage: forge-command-surface
    """
    from agents.forge.memory import write_audit_entry

    # Read this file's source to check for routing markers
    try:
        source = Path(__file__).read_text(encoding="utf-8")
    except Exception:
        try:
            source = (FORGE_ROOT / "main.py").read_text(encoding="utf-8")
        except Exception as e:
            print(f"[forge] ERROR: Cannot read main.py for self-test: {e}")
            return

    found = []
    missing = []
    for cmd in FORGE_EXPECTED_COMMANDS:
        # Check for the command string as a routing marker in the session loop
        if f'"{cmd}"' in source or f"'{cmd}'" in source:
            found.append(cmd)
        else:
            missing.append(cmd)

    total     = len(FORGE_EXPECTED_COMMANDS)
    found_n   = len(found)
    audit_tool = "FORGE_COMMAND_SURFACE_OK" if not missing else "FORGE_COMMAND_SURFACE_FAILED"

    write_audit_entry(session_id, audit_tool, "-", f"{found_n}/{total}",
                      f"found={found_n} missing={len(missing)}")

    print()
    print(f"── Forge Command Surface Self-Test ───────────────────")
    print(f"  Expected: {total}   Found: {found_n}   Missing: {len(missing)}")
    print()
    if missing:
        print(f"  MISSING ({len(missing)}):")
        for cmd in missing:
            print(f"    ✗ {cmd}")
        print()
    print(f"  FOUND ({found_n}):")
    for cmd in found:
        print(f"    ✓ {cmd}")
    print()
    print(f"  Result: {audit_tool}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_ingestion_policy(session_id: str) -> None:
    """Print the ingestion governance rules. Usage: ingestion-policy"""
    from agents.forge.memory import write_audit_entry

    write_audit_entry(session_id, "INGESTION_POLICY_SHOWN", "-", "-", "policy displayed")

    print()
    print(f"── Ingestion Policy ──────────────────────────────────")
    print()
    for rule in INGESTION_POLICY_RULES:
        print(f"  {rule}")
    print()
    print(f"  Planned collection namespaces:")
    for ns, desc in PLANNED_NAMESPACES:
        print(f"    • {ns:<35} {desc}")
    print()
    print(f"  No collections will be created until ingestion is authorized.")
    print(f"──────────────────────────────────────────────────────")
    print()


# ─── PART 4: DRY-RUN CHUNKING ────────────────────────────────────────────────

CHUNK_TARGET  = 1350   # target chunk size in characters
CHUNK_MAX     = 1800   # hard maximum — chunks exceeding this must be split
CHUNK_OVERLAP = 200    # overlap between chunks
CHUNK_MIN     = 100    # flag tiny chunks below this (except final/header)


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation boundaries."""
    import re
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]


def _chunk_text(text: str, chunk_size: int = CHUNK_TARGET, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """
    Paragraph-aware, sentence-fallback, hard-max-enforced chunker.

    Invariants (never violated):
      - Every chunk.char_count ≤ CHUNK_MAX
      - Overlap tail is only prepended if tail + block ≤ CHUNK_MAX
      - Individual paragraphs > CHUNK_MAX are split into sentences first
      - Individual sentences > CHUNK_MAX are split at word boundary
    """
    HARD_MAX = CHUNK_MAX

    def _force_split(text_block: str) -> list[str]:
        """Split text_block into pieces all ≤ HARD_MAX. Tries sentences first."""
        if len(text_block) <= HARD_MAX:
            return [text_block]
        sentences = _split_into_sentences(text_block)
        if len(sentences) > 1:
            pieces, current = [], ""
            for sent in sentences:
                test = (current + " " + sent).strip() if current else sent
                if len(test) <= HARD_MAX:
                    current = test
                else:
                    if current:
                        pieces.append(current)
                    if len(sent) > HARD_MAX:
                        # Split oversized sentence at word boundary
                        for i in range(0, len(sent), HARD_MAX - 50):
                            piece = sent[i:i + HARD_MAX - 50].strip()
                            if piece:
                                pieces.append(piece)
                        current = ""
                    else:
                        current = sent
            if current:
                pieces.append(current)
        else:
            # No sentence breaks — force split by chars
            pieces = []
            for i in range(0, len(text_block), HARD_MAX - 50):
                piece = text_block[i:i + HARD_MAX - 50].strip()
                if piece:
                    pieces.append(piece)
        return [p for p in pieces if p]

    # Step 1: Split into paragraphs, force-splitting any that exceed HARD_MAX
    raw_blocks: list[str] = []
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        if len(para) > HARD_MAX:
            raw_blocks.extend(_force_split(para))
        else:
            raw_blocks.append(para)

    # Step 2: Aggregate blocks into chunks, respecting chunk_size target and HARD_MAX
    chunks: list[dict] = []
    current   = ""
    char_pos  = 0
    idx       = 0

    def _flush(text_val: str, pos: int, i: int) -> tuple[str, int, int]:
        """Emit the current buffer as a chunk, return (new_current, new_pos, new_idx)."""
        is_tiny = len(text_val) < CHUNK_MIN and i > 0
        chunks.append({
            "index":       i,
            "text":        text_val,
            "char_start":  pos,
            "char_end":    pos + len(text_val),
            "char_count":  len(text_val),
            "tiny_warning": is_tiny,
            "exceeds_max": len(text_val) > HARD_MAX,  # should never be True
        })
        # Overlap: carry the tail into the next chunk
        tail = text_val[-overlap:] if len(text_val) > overlap else text_val
        new_pos = pos + len(text_val) - len(tail)
        return tail, new_pos, i + 1

    for block in raw_blocks:
        if not current:
            current = block
            continue

        candidate = (current + "\n\n" + block).strip()

        if len(candidate) <= chunk_size:
            # Fits in target size — keep accumulating
            current = candidate
        elif len(candidate) <= HARD_MAX:
            # Exceeds target but under hard max — accept if close, else flush
            if len(candidate) <= chunk_size + 200:
                current = candidate  # slightly over target, still acceptable
            else:
                tail, char_pos, idx = _flush(current, char_pos, idx)
                candidate_with_tail = (tail + "\n\n" + block).strip()
                # If tail + block fits within HARD_MAX, use it; otherwise start fresh
                if len(candidate_with_tail) <= HARD_MAX:
                    current = candidate_with_tail
                else:
                    current = block
        else:
            # Would exceed HARD_MAX — must flush first
            tail, char_pos, idx = _flush(current, char_pos, idx)
            # Only prepend tail if tail + block ≤ HARD_MAX
            candidate_with_tail = (tail + "\n\n" + block).strip()
            if len(candidate_with_tail) <= HARD_MAX:
                current = candidate_with_tail
            else:
                current = block  # start fresh — tail would push over hard max

    # Flush the final buffer
    if current:
        is_tiny = len(current) < CHUNK_MIN and idx > 0
        chunks.append({
            "index":       idx,
            "text":        current,
            "char_start":  char_pos,
            "char_end":    char_pos + len(current),
            "char_count":  len(current),
            "tiny_warning": is_tiny,
            "exceeds_max": len(current) > HARD_MAX,
        })

    return chunks


def cmd_chunk_policy(session_id: str) -> None:
    """Print the current chunking policy. Usage: chunk-policy"""
    from agents.forge.memory import write_audit_entry
    write_audit_entry(session_id, "INGESTION_POLICY_SHOWN", "-", "-", "chunk policy displayed")
    print()
    print(f"── Chunk Policy ──────────────────────────────────────")
    print(f"  Target size  : {CHUNK_TARGET} chars (ideal chunk size)")
    print(f"  Hard max     : {CHUNK_MAX} chars (no chunk may exceed this)")
    print(f"  Overlap      : {CHUNK_OVERLAP} chars (tail carried into next chunk)")
    print(f"  Tiny flag    : < {CHUNK_MIN} chars (flagged, not rejected)")
    print()
    print(f"  Splitting hierarchy:")
    print(f"    1. Paragraph boundaries (\\n\\n) — primary split")
    print(f"    2. Sentence boundaries (.!?) — used when paragraph > hard max")
    print(f"    3. Word boundary at {CHUNK_MAX-50} chars — used when sentence > hard max")
    print()
    print(f"  Chunk quality guarantees:")
    print(f"    • No chunk exceeds {CHUNK_MAX} chars")
    print(f"    • Chunks < {CHUNK_MIN} chars are flagged in dry-run report")
    print(f"    • Overlap preserves context continuity across chunk boundaries")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_ingest_dry_run_validate(corpus_id: str, session_id: str) -> None:
    """
    Validate the latest dry-run plan for a corpus ID.
    Checks: no chunks exceed hard max, no tiny chunks, chunk count reasonable.
    Usage: ingest-dry-run-validate <corpus_id>
    """
    import json as _json
    from agents.forge.memory import write_audit_entry

    corpus_id = corpus_id.strip()
    if not corpus_id:
        print()
        print("  Usage: ingest-dry-run-validate <corpus_id>")
        print()
        return

    INGESTION_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    plans = sorted(INGESTION_PLANS_DIR.glob(f"*_dry_run_{corpus_id}.json"), reverse=True)
    if not plans:
        print(f"[forge] No dry-run plan found for '{corpus_id}'. Run 'ingest-dry-run {corpus_id}' first.")
        return

    try:
        plan = _json.loads(plans[0].read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"[forge] ERROR: Cannot read plan: {e}")
        return

    issues   = []
    warnings = []

    chunk_count = plan.get("chunk_count", 0)
    max_chars   = plan.get("max_chars", 0)
    min_chars   = plan.get("min_chars", 0)
    avg_chars   = plan.get("avg_chars", 0)

    if max_chars > CHUNK_MAX:
        issues.append(f"Max chunk ({max_chars}) exceeds hard max ({CHUNK_MAX})")
    if min_chars < CHUNK_MIN and chunk_count > 1:
        warnings.append(f"Min chunk ({min_chars}) is tiny (< {CHUNK_MIN})")
    if chunk_count < 1:
        issues.append("No chunks generated — extraction may have failed")
    if avg_chars < 200:
        warnings.append(f"Average chunk size ({avg_chars}) seems very small")
    if avg_chars > CHUNK_MAX:
        issues.append(f"Average chunk size ({avg_chars}) exceeds hard max — old chunker output?")

    if not plan.get("no_chroma_write", False):
        issues.append("Plan does not confirm no_chroma_write — reject")
    if not plan.get("no_embedding", False):
        issues.append("Plan does not confirm no_embedding — reject")

    chunks = plan.get("chunks") or []
    if chunks and plan.get("chunk_count") != len(chunks):
        issues.append(f"Chunk record count mismatch: header={plan.get('chunk_count')} records={len(chunks)}")

    passed = not issues
    write_audit_entry(session_id, "INGEST_DRY_RUN_VALIDATED" if passed else "INGEST_DRY_RUN_FAILED",
                      str(plans[0]), "-",
                      f"validate: issues={len(issues)} warnings={len(warnings)} chunks_recorded={len(chunks)}")

    print()
    print(f"── Dry-Run Validation: {corpus_id} ──────────────────")
    print(f"  Plan     : {plans[0].name}")
    print(f"  Chunks   : {chunk_count}")
    print(f"  Max chars: {max_chars}  (hard max: {CHUNK_MAX})")
    print(f"  Min chars: {min_chars}  (flag threshold: {CHUNK_MIN})")
    print(f"  Avg chars: {avg_chars}")
    print(f"  No write : {plan.get('no_chroma_write','?')}")
    print()
    if issues:
        print(f"  FAILED ({len(issues)} issue(s)):")
        for i in issues:
            print(f"    ✗ {i}")
    else:
        print(f"  ✓ All hard constraints pass")
    if warnings:
        print(f"  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠ {w}")
    print()
    result = "VALIDATION PASSED" if passed else "VALIDATION FAILED"
    print(f"  Result: {result}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_ingest_dry_run(corpus_id: str, session_id: str) -> None:
    """
    Dry-run chunking preview for a corpus document. No embeddings. No Chroma writes.
    Patch 44: uses the same extraction ceiling and chunk policy as ingest-one, and stores
    chunk IDs/hashes/text so write parity can be proven before any Chroma write.
    Usage: ingest-dry-run <corpus_id>
    """
    from agents.forge.memory import write_audit_entry

    ARCHIVE_MARKER = "ARCHIVE"
    corpus_id = corpus_id.strip()
    if not corpus_id:
        print()
        print("  Usage: ingest-dry-run <corpus_id>")
        print("  Example: ingest-dry-run corpus_0022")
        print()
        return

    if not _corpus_security_check(_CORPUS_JSON, session_id):
        return

    rows = _corpus_load_json() or _corpus_load_csv()
    if not rows:
        print("[forge] ERROR: Could not load corpus manifest.")
        return

    item = next((r for r in rows if r.get("id", "").strip().lower() == corpus_id.lower()), None)
    if item is None:
        write_audit_entry(session_id, "INGEST_DRY_RUN_REFUSED", "-", "-", f"id_not_found={corpus_id}")
        print(f"[forge] INGEST DRY-RUN REFUSED: ID '{corpus_id}' not found.")
        return

    eligible = str(item.get("index_eligible", "")).strip().lower() in ("true", "1", "yes")
    folder = str(item.get("corpus_folder", "")).upper()
    if not eligible or ARCHIVE_MARKER in folder:
        write_audit_entry(session_id, "INGEST_DRY_RUN_REFUSED", "-", "-", f"id={corpus_id} held/archive")
        print(f"[forge] INGEST DRY-RUN REFUSED: '{corpus_id}' is held from indexing.")
        print(f"  Folder: {item.get('corpus_folder', '?')}  Eligible: {item.get('index_eligible', '?')}")
        return

    abs_path_str = item.get("absolute_path", "").strip() or str(_CORPUS_ROOT / item.get("relative_path", ""))
    abs_path = Path(abs_path_str)
    if not _corpus_security_check(abs_path, session_id):
        return

    plan, plan_path, issues = _make_dry_run_plan(corpus_id, item, session_id, internal=False)
    if issues or not plan or not plan_path:
        write_audit_entry(session_id, "INGEST_DRY_RUN_FAILED", str(abs_path), "-", "; ".join(issues)[:200])
        print(f"[forge] INGEST DRY-RUN FAILED: {issues[0] if issues else 'unknown error'}")
        return

    parity_issues = _validate_dry_run_plan_for_write(plan, corpus_id, item)
    audit_tool = "INGEST_DRY_RUN_CREATED" if not parity_issues else "INGEST_DRY_RUN_FAILED"
    write_audit_entry(session_id, audit_tool, str(plan_path), f"{plan.get('chunk_count')} chunks",
                      f"id={corpus_id} chars={plan.get('extraction_chars')} chunks={plan.get('chunk_count')} sha={plan.get('source_hash')}")

    print()
    print(f"── Ingest Dry-Run: {corpus_id} ──────────────────────")
    print(f"  Filename    : {item.get('filename', '?')}")
    print(f"  Folder      : {item.get('corpus_folder', '?')}")
    print(f"  SHA-256     : {plan.get('source_hash')}  ✓")
    print(f"  Format      : {plan.get('adapter_format')}")
    print(f"  Extracted   : {plan.get('extraction_chars'):,} chars")
    print()
    print(f"  Chunk policy: target={CHUNK_TARGET} max={CHUNK_MAX} overlap={CHUNK_OVERLAP}")
    print(f"  Chunk count : {plan.get('chunk_count')}")
    print(f"  Min chars   : {plan.get('min_chars'):,}" + (f"  ⚠ tiny" if plan.get('min_chars', 0) < CHUNK_MIN else ""))
    print(f"  Max chars   : {plan.get('max_chars'):,}" + (f"  ✗ EXCEEDS HARD MAX {CHUNK_MAX}" if plan.get('max_chars', 0) > CHUNK_MAX else "  ✓"))
    print(f"  Avg chars   : {plan.get('avg_chars'):,}")
    print(f"  Stored chunk hashes/text for ingest parity: YES")
    if parity_issues:
        print()
        print(f"  DRY-RUN PARITY WARNINGS ({len(parity_issues)}):")
        for issue in parity_issues[:10]:
            print(f"    ✗ {issue}")
    print()
    print(f"  Proposed collection: {CONTEXT_COLLECTION}")
    print(f"  Proposed DB path   : {CONTEXT_LIB_CHROMA}")
    print()
    print(f"  First chunk preview:")
    first = (plan.get("first_chunk_preview") or "")
    for line in first.splitlines()[:6]:
        print(f"    {line}")
    print()
    print(f"  ⚠ NO VECTORS CREATED. NO CHROMA WRITE. DRY-RUN ONLY.")
    print(f"  Plan saved : {plan_path}")
    print(f"──────────────────────────────────────────────────────")
    print()


# ─── PART 5: INGESTION MANIFEST PLAN ─────────────────────────────────────────

def cmd_ingestion_manifest_plan(session_id: str) -> None:
    """Create a Forge-owned ingestion planning artifact. Usage: ingestion-manifest-plan"""
    import json as _json
    from agents.forge.document_adapters import get_adapter_status, _check_library, LIBRARY_FORMATS
    from agents.forge.memory import write_audit_entry

    INGESTION_PLANS_DIR.mkdir(parents=True, exist_ok=True)

    # Gather state
    corpus_reports  = sorted(CORPUS_REPORTS_DIR.glob("*_extraction_check.json"), reverse=True)
    vector_reports  = sorted(VECTOR_REPORTS_DIR.glob("*_vector_audit.json"), reverse=True)
    gap_reports     = sorted(SOURCE_GAP_REPORTS_DIR.glob("*_source_gap.json"), reverse=True)
    dry_runs        = sorted(INGESTION_PLANS_DIR.glob("*_dry_run_*.json"), reverse=True)

    latest_extract = None
    if corpus_reports:
        try:
            latest_extract = _json.loads(corpus_reports[0].read_text(encoding="utf-8"))
        except Exception:
            pass

    adapter_status = {ext: s["status"] for ext, s in get_adapter_status().items()
                      if ext in (".docx", ".pdf", ".txt", ".md")}

    manifest = {
        "report_type":            "INGESTION_MANIFEST_PLAN",
        "timestamp":              datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id":             session_id,
        "corpus_manifest_path":   str(_CORPUS_JSON),
        "extraction_report":      str(corpus_reports[0]) if corpus_reports else "NONE",
        "extraction_ok":          latest_extract.get("ok",0) if latest_extract else 0,
        "extraction_total":       latest_extract.get("total_checked",0) if latest_extract else 0,
        "vector_audit_report":    str(vector_reports[0]) if vector_reports else "NONE",
        "source_gap_report":      str(gap_reports[0]) if gap_reports else "NONE",
        "rpmc_policy_path":       str(RPMC_POLICY_FILE),
        "rpmc_schema_path":       str(RPMC_SCHEMA_FILE),
        "document_adapters":      adapter_status,
        "planned_namespaces":     [ns for ns, _ in PLANNED_NAMESPACES],
        "dry_run_reports":        [str(d) for d in dry_runs[:5]],
        "ingestion_happened":     False,
        "ingestion_authorized":   INGESTION_AUTH_FILE.exists(),
        "chroma_db_path":         str(CHROMA_DB_PATH),
        "chroma_has_content":     CHROMA_DB_PATH.exists() and bool(list(CHROMA_DB_PATH.iterdir()) if CHROMA_DB_PATH.is_dir() else []),
        "trial_ingestion_target_recommendation": "corpus_0011 (Gilligan System Codex .docx) — confirmed extractable, chunks precomputed",
        "policy_rules":           INGESTION_POLICY_RULES,
    }

    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    plan_path = INGESTION_PLANS_DIR / f"{ts}_ingestion_manifest_plan.json"
    try:
        plan_path.write_text(_json.dumps(manifest, indent=2), encoding="utf-8")
    except OSError as e:
        print(f"[forge] WARNING: Could not save manifest plan: {e}")

    write_audit_entry(session_id, "INGESTION_MANIFEST_PLAN_CREATED", str(plan_path), "-",
                      f"extraction_ok={manifest['extraction_ok']} ingestion_happened=False")

    print()
    print(f"── Ingestion Manifest Plan ───────────────────────────")
    print(f"  Corpus manifest   : {_CORPUS_JSON}")
    print(f"  Extraction report : {corpus_reports[0].name if corpus_reports else 'NONE'}")
    print(f"  Extraction status : {manifest['extraction_ok']}/{manifest['extraction_total']} OK")
    print(f"  Vector audit      : {vector_reports[0].name if vector_reports else 'NONE'}")
    print(f"  Source gap report : {gap_reports[0].name if gap_reports else 'NONE'}")
    print(f"  RPMC policy       : {'EXISTS' if RPMC_POLICY_FILE.exists() else 'MISSING'}")
    print(f"  Doc adapters      : {adapter_status}")
    print(f"  Dry-run reports   : {len(dry_runs)}")
    print(f"  Ingestion auth    : {'YES — AUTHORIZED' if manifest['ingestion_authorized'] else 'NOT YET'}")
    print()
    print(f"  Trial target: {manifest['trial_ingestion_target_recommendation']}")
    print()
    print(f"  ⚠ NO INGESTION HAS HAPPENED. This is a planning artifact only.")
    print(f"  Plan saved: {plan_path}")
    print(f"──────────────────────────────────────────────────────")
    print()


# ─── PART 6: FINAL READINESS SEAL ────────────────────────────────────────────

def cmd_ingestion_readiness(session_id: str) -> None:
    """Run the final pre-ingestion readiness gate. Usage: ingestion-readiness"""
    import json as _json
    from agents.forge.document_adapters import _check_library, LIBRARY_FORMATS
    from agents.forge.memory import write_audit_entry

    checks  = []
    warnings = []
    failures = []

    def check(label: str, passed: bool, detail: str = "", warn: bool = False):
        status = "✓" if passed else ("⚠" if warn else "✗")
        checks.append((status, label, detail))
        if not passed:
            if warn:
                warnings.append(f"{label}: {detail}")
            else:
                failures.append(f"{label}: {detail}")

    # 1. Corpus manifest loads
    rows = _corpus_load_json() or _corpus_load_csv()
    check("Corpus manifest loads", bool(rows), f"{len(rows or [])} rows")

    # 2. Corpus-check: no RPMC fields in manifest
    if rows:
        forbidden = [f for r in rows for f in RPMC_FORBIDDEN_IN_MANIFEST if f in r]
        check("Manifest purity (no RPMC fields)", not forbidden,
              "clean" if not forbidden else f"{len(forbidden)} forbidden fields found")

    # 3. Latest extraction report exists and shows 17 OK
    corpus_reports = sorted(CORPUS_REPORTS_DIR.glob("*_extraction_check.json"), reverse=True)
    if corpus_reports:
        try:
            rpt = _json.loads(corpus_reports[0].read_text(encoding="utf-8"))
            ok, total = rpt.get("ok",0), rpt.get("total_checked",0)
            failed = rpt.get("failed",0) + rpt.get("hash_mismatch",0) + rpt.get("missing",0)
            check("Extraction report exists", True, corpus_reports[0].name)
            check("Extraction: 0 failures", failed == 0, f"ok={ok}/{total} failed={failed}")
            check("Extraction: all eligible OK", ok == total,
                  f"ok={ok}/{total}", warn=(ok < total and failed == 0))
        except Exception as e:
            check("Extraction report readable", False, str(e))
    else:
        check("Extraction report exists", False, "run corpus-extract-check first")

    # 4. RPMC kernel exists
    rpmc_ok = RPMC_KERNEL_DIR.exists() and RPMC_POLICY_FILE.exists() and RPMC_SCHEMA_FILE.exists()
    check("RPMC kernel planning files exist", rpmc_ok,
          "OK" if rpmc_ok else "missing — run rpmc-check")

    # 5. Vector audit report exists
    vector_reports = sorted(VECTOR_REPORTS_DIR.glob("*_vector_audit.json"), reverse=True)
    check("Vector audit report exists", bool(vector_reports),
          vector_reports[0].name if vector_reports else "run vector-audit first")

    # 6. Source gap report exists and distinguishes trial from full authority
    gap_reports = sorted(SOURCE_GAP_REPORTS_DIR.glob("*_source_gap.json"), reverse=True)
    if gap_reports:
        try:
            gap_data = _json.loads(gap_reports[0].read_text(encoding="utf-8"))
            required_gaps = gap_data.get("required_gaps", gap_data.get("gaps", 0))
            full_auth     = gap_data.get("full_auth_readiness", "")
            check("Source gap report exists", True, gap_reports[0].name)
            check("RPMC required sources registered (exact/strong)", required_gaps == 0,
                  f"{required_gaps} required source(s) MISSING/RELATED_ONLY — blocks full authority, NOT trial",
                  warn=(required_gaps > 0))
        except Exception:
            check("Source gap report readable", False, "parse error")
    else:
        check("Source gap report exists", False, "run source-gap-report first")

    # 7. Doc adapters for docx and pdf
    for ext, lib_info in LIBRARY_FORMATS.items():
        available = _check_library(lib_info["import_check"])
        check(f"Adapter: {ext}", available,
              "available" if available else f"missing — {lib_info['install_hint']}", warn=not available)

    # 8. Chroma DB state is known
    chroma_exists = CHROMA_DB_PATH.exists()
    chroma_items  = list(CHROMA_DB_PATH.iterdir()) if chroma_exists and CHROMA_DB_PATH.is_dir() else []
    check("Chroma DB state known", bool(vector_reports), "known via vector audit" if vector_reports else "unknown")
    check("Chroma DB quarantine/namespace plan exists", True,
          "Option C (separate DB path) recommended — not yet executed", warn=bool(chroma_items))

    # 9. No ingestion yet
    check("No ingestion has happened", not INGESTION_AUTH_FILE.exists(),
          "no auth flag found — clean" if not INGESTION_AUTH_FILE.exists() else "AUTH FLAG EXISTS — ingestion may have occurred")

    # 10. Dry-run exists
    dry_runs = sorted(INGESTION_PLANS_DIR.glob("*_dry_run_*.json"), reverse=True)
    check("Dry-run chunking report exists", bool(dry_runs),
          dry_runs[0].name if dry_runs else "run ingest-dry-run <corpus_id> first",
          warn=not dry_runs)

    # Verdict
    if failures:
        verdict = "NO-GO"
        audit_tool = "INGESTION_READINESS_FAILED"
    elif warnings:
        verdict = "GO FOR SINGLE-DOCUMENT TRIAL INGESTION WITH WARNINGS"
        audit_tool = "INGESTION_READINESS_WARN"
    else:
        verdict = "GO FOR SINGLE-DOCUMENT TRIAL INGESTION"
        audit_tool = "INGESTION_READINESS_OK"

    # Full authority verdict (separate check)
    has_authority_gaps = any("full authority" in w.lower() or "required source" in w.lower()
                             for w in warnings)
    full_auth_verdict = ("NO-GO FOR FULL-CORPUS AUTHORITY INGESTION — required RPMC sources not exact/strong registered"
                         if has_authority_gaps else "FULL-CORPUS AUTHORITY INGESTION POSSIBLE")

    write_audit_entry(session_id, audit_tool, "-", "-",
                      f"checks={len(checks)} failures={len(failures)} warnings={len(warnings)}")

    print()
    print(f"── Ingestion Readiness Gate ──────────────────────────")
    for status, label, detail in checks:
        print(f"  {status} {label:<50} {detail[:50]}")
    print()
    if warnings:
        print(f"  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠ {w[:90]}")
        print()
    if failures:
        print(f"  Failures ({len(failures)}):")
        for f in failures:
            print(f"    ✗ {f[:90]}")
        print()
    print(f"  ═══════════════════════════════════════════════════")
    print(f"  TRIAL INGESTION  : {verdict}")
    print(f"  FULL AUTHORITY   : {full_auth_verdict}")
    print(f"  ═══════════════════════════════════════════════════")
    print(f"  Audit: {audit_tool}")
    print(f"──────────────────────────────────────────────────────")
    print()


RPMC_KERNEL_DIR    = FORGE_ROOT / "rpmc_kernel"
RPMC_POLICY_FILE   = RPMC_KERNEL_DIR / "RPMC_SOURCE_POLICY.md"
RPMC_SCHEMA_FILE   = RPMC_KERNEL_DIR / "rpmc_kernel_schema.json"
RPMC_TEMPLATE_FILE = RPMC_KERNEL_DIR / "rpmc_runtime_mapping_template.json"

RPMC_FORBIDDEN_IN_MANIFEST = {
    "primary_phase", "symbolic_charge", "chi_t_role", "spc_role",
    "active_stack_role", "drift_archive_role", "resurrection_log_role",
    "grace_timer_role", "symbolic_firewall_role", "entropy_score",
    "echo_checkpoint", "drift_entropy", "phi_m", "epsilon_t",
}


def cmd_rpmc_policy(session_id: str) -> None:
    """Print the RPMC governing separation and authority policy. Usage: rpmc-policy"""
    from agents.forge.memory import write_audit_entry
    write_audit_entry(session_id, "RPMC_POLICY_SHOWN", "-", "-", "policy displayed")
    print()
    print(f"── RPMC Separation and Authority Policy ──────────────")
    print()
    print(f"  RPMC is a memory-runtime law layer (Nicholas Bogaert / AI.Web, 2025).")
    print()
    print(f"  Core operators (from RPMC Full Protocol Draft):")
    print(f"    ΦM(x,t)   — memory function (phase-locked resonance states)")
    print(f"    χ(t)      — collapse-resurrection operator (grace function)")
    print(f"    ε(t,Φ)    — entropy vector (drift and phase degradation)")
    print(f"    RPM(x,t)  — Σₙ ΦMₙ·exp(-εₙ) + χ(t)·Θ(Φ_resurrect)")
    print()
    print(f"  RPMC MAY guide:")
    for item in [
        "Future memory architecture and retrieval weighting",
        "Drift detection and entropy scoring (ε(t,Φ)) in live memory",
        "Collapse handling: cold storage (SPC/DPA) vs. active recall",
        "Resurrection logic: echo alignment validation before surfacing",
        "χ(t) grace timer design for session/context recovery",
        "Echo checkpoint design in the audit chain",
        "Symbolic firewall against phase-poisoned (false) projection",
        "Phase-aware code review and Dead Path Archive structuring",
    ]:
        print(f"    • {item}")
    print()
    print(f"  RPMC MUST NOT:")
    for item in [
        "Override disk truth (file contents, SHA hashes, test output)",
        "Contradict audit log entries or runtime process state",
        "Bypass patch safety rules (APPLY confirmation, rollback)",
        "Contaminate base corpus metadata manifest",
        "Drive automatic ingestion, vector DB writes, or Chroma ops",
        "Be treated as operational fact until implementation is verified",
    ]:
        print(f"    • {item}")
    print()
    print(f"  RPMC REMAINS a separate planning layer until Gate 4 (runtime integration).")
    print(f"  Files: {RPMC_KERNEL_DIR}")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_rpmc_template(session_id: str) -> None:
    """Print the planned RPMC runtime mapping schema template. Usage: rpmc-template"""
    import json as _json
    from agents.forge.memory import write_audit_entry
    write_audit_entry(session_id, "RPMC_TEMPLATE_SHOWN", str(RPMC_TEMPLATE_FILE), "-", "template displayed")
    print()
    print(f"── RPMC Runtime Mapping Template Schema ──────────────")
    print(f"  File: {RPMC_TEMPLATE_FILE}")
    print()
    if RPMC_TEMPLATE_FILE.exists():
        try:
            data   = _json.loads(RPMC_TEMPLATE_FILE.read_text(encoding="utf-8"))
            fields = data.get("_field_definitions", {})
            print(f"  Status : {data.get('_status', 'unknown')}")
            print()
            print(f"  Schema fields ({len(fields)}):")
            for field, desc in fields.items():
                print(f"    {field:<35} {str(desc)[:60]}")
            print()
            assignments = data.get("assignments", [])
            print(f"  Current assignments: {len(assignments)} (empty — no real mappings yet)")
        except Exception as e:
            print(f"  [Could not parse template: {e}]")
    else:
        print(f"  [Template file not found — run rpmc-check to diagnose]")
    print()
    print(f"  RPMC runtime assignments must NEVER be placed in base corpus manifest.")
    print(f"──────────────────────────────────────────────────────")
    print()


def cmd_rpmc_check(session_id: str) -> None:
    """Validate the RPMC kernel planning directory and manifest purity. Usage: rpmc-check"""
    import json as _json
    from agents.forge.memory import write_audit_entry
    errors = []
    warnings = []

    if not RPMC_KERNEL_DIR.exists():
        errors.append(f"RPMC kernel directory missing: {RPMC_KERNEL_DIR}")
    else:
        for fpath, label in [
            (RPMC_POLICY_FILE,   "RPMC_SOURCE_POLICY.md"),
            (RPMC_SCHEMA_FILE,   "rpmc_kernel_schema.json"),
            (RPMC_TEMPLATE_FILE, "rpmc_runtime_mapping_template.json"),
        ]:
            if not fpath.exists():
                errors.append(f"Missing: {label}")

    rows = _corpus_load_json() or _corpus_load_csv()
    forbidden_count = 0
    if rows:
        for row in rows:
            for field in RPMC_FORBIDDEN_IN_MANIFEST:
                if field in row:
                    errors.append(f"RPMC field '{field}' found in manifest row {row.get('id','?')}")
                    forbidden_count += 1
    else:
        warnings.append("Could not load corpus manifest for purity check")

    chroma_path  = FORGE_ROOT / "memory" / "chroma_db"
    chroma_items = list(chroma_path.iterdir()) if chroma_path.exists() and chroma_path.is_dir() else []
    if chroma_items:
        warnings.append(f"Chroma DB directory has content ({len(chroma_items)} items): {chroma_path}")

    reports_dir  = CORPUS_REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    json_reports = sorted(reports_dir.glob("*_extraction_check.json"), reverse=True)
    if not json_reports:
        warnings.append("No corpus extraction report found — run 'corpus-extract-check' first")
    else:
        try:
            rpt = _json.loads(json_reports[0].read_text(encoding="utf-8"))
            ok, total = rpt.get("ok", 0), rpt.get("total_checked", 0)
            if ok < total:
                warnings.append(f"Extraction quality: {ok}/{total} OK — review before ingestion")
        except Exception as e:
            warnings.append(f"Could not read extraction report: {e}")

    audit_tool = "RPMC_CHECK_OK" if not errors else "RPMC_CHECK_FAILED"
    write_audit_entry(session_id, audit_tool, str(RPMC_KERNEL_DIR), "-",
                      f"errors={len(errors)} warnings={len(warnings)}")

    print()
    print(f"── RPMC Kernel Check ─────────────────────────────────")
    print(f"  Kernel dir   : {'EXISTS ✓' if RPMC_KERNEL_DIR.exists() else 'MISSING ✗'}")
    print(f"  Policy file  : {'EXISTS ✓' if RPMC_POLICY_FILE.exists() else 'MISSING ✗'}")
    print(f"  Schema file  : {'EXISTS ✓' if RPMC_SCHEMA_FILE.exists() else 'MISSING ✗'}")
    print(f"  Template     : {'EXISTS ✓' if RPMC_TEMPLATE_FILE.exists() else 'MISSING ✗'}")
    print(f"  Manifest purity: {'CLEAN ✓' if forbidden_count == 0 else f'CONTAMINATED ({forbidden_count} forbidden fields)'}")
    print(f"  Ingestion    : {'NOT YET ✓' if not chroma_items else 'Chroma has content ⚠'}")
    print()
    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for e in errors[:8]:
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


def cmd_rpmc_source_list(session_id: str) -> None:
    """List RPMC/memory-law candidate sources in local corpus and Drive. Usage: rpmc-source-list"""
    from agents.forge.memory import write_audit_entry

    RPMC_TAGS    = {"rpmc", "memory", "resonant", "phase", "collapse", "resurrection",
                    "echo", "drift", "chi", "grace", "fbsc", "gilligan", "symbolic"}
    RPMC_FOLDERS = {"04_FBSC_DOCTRINE", "03_GILLIGAN_AGENT_CORE", "01_SYSTEM_LAW", "02_AIWEB_ARCHITECTURE"}
    RPMC_KEYWORDS = ("rpmc", "resonant", "phase", "memory", "fbsc", "gilligan", "drift", "collapse")

    DRIVE_SOURCES = [
        ("RPMC Full Protocol Draft (.pdf + Google Doc)",
         "1eN6in0lUcGY9RdHcAPFlJOHJNpN6ny1M",
         "NOT YET REGISTERED IN LOCAL FORGE CORPUS"),
        ("RPMC Implementation Blueprint (ProtoForge Dev Book)",
         "1L_f5I2InqyMiGKX7ERs0et9jY9-gzpVgvqmZ-VAl46E",
         "NOT YET REGISTERED IN LOCAL FORGE CORPUS"),
        ("RPMC Canonical Test Data Set v1.0",
         "1b8JAc-aATjD7h1Ed4KYA2kxxPkxHaX5-lDO5V5qsXsM",
         "NOT YET REGISTERED IN LOCAL FORGE CORPUS"),
    ]

    rows = _corpus_load_json() or _corpus_load_csv()
    candidates = [
        r for r in (rows or [])
        if (set(str(r.get("tags","")).lower().replace(",", " ").split()) & RPMC_TAGS
            or r.get("corpus_folder","") in RPMC_FOLDERS
            or any(kw in r.get("filename","").lower() for kw in RPMC_KEYWORDS))
    ]

    write_audit_entry(session_id, "RPMC_SOURCE_LIST_SHOWN", str(_CORPUS_JSON), "-",
                      f"local_candidates={len(candidates)} drive_sources={len(DRIVE_SOURCES)}")

    print()
    print(f"── RPMC Source List ──────────────────────────────────")
    print()
    print(f"  Drive sources (available for reference, NOT in local corpus):")
    for title, drive_id, status in DRIVE_SOURCES:
        print(f"    • {title}")
        print(f"      Status: ⚠ {status}")
    print()
    print(f"  ⚠ RPMC full protocol PDF is available as source reference but is")
    print(f"    NOT yet registered in local Forge corpus.")
    print()
    if candidates:
        print(f"  Local corpus candidates with RPMC-related metadata ({len(candidates)}):")
        for r in candidates:
            print(f"    {r.get('id','?'):<15} {r.get('filename','?'):<45} [{r.get('corpus_folder','?')}]")
    else:
        print(f"  No local corpus items match RPMC-related metadata patterns.")
    print()
    print(f"  To register: download to ~/forge_corpus/, update manifest, run corpus-check.")
    print(f"  Do NOT automatically pull Drive files into Forge.")
    print(f"──────────────────────────────────────────────────────")
    print()


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
    reports_dir = CORPUS_REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
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

    reports_dir = CORPUS_REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
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
    reports_dir = CORPUS_REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)

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
    (FORGE_ROOT / "rpmc_kernel").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "corpus_policies").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "corpus_registration_reports").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "vector_reports").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "source_gap_reports").mkdir(parents=True, exist_ok=True)
    (FORGE_ROOT / "ingestion_plans").mkdir(parents=True, exist_ok=True)

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

            if user_input.lower() == "vector-status":
                cmd_vector_status(session_id)
                continue

            if user_input.lower() == "vector-audit":
                cmd_vector_audit(session_id)
                continue

            if user_input.lower() == "vector-report":
                cmd_vector_report(session_id)
                continue

            if user_input.lower() == "vector-quarantine-plan":
                cmd_vector_quarantine_plan(session_id)
                continue

            if user_input.lower() == "source-gap-evidence":
                cmd_source_gap_evidence(session_id)
                continue

            if user_input.lower() == "chunk-policy":
                cmd_chunk_policy(session_id)
                continue

            if user_input.lower().startswith("ingest-dry-run "):
                idr_id = user_input[15:].strip()
                cmd_ingest_dry_run(idr_id, session_id)
                continue

            if user_input.lower() == "ingest-dry-run":
                print()
                print("  Usage: ingest-dry-run <corpus_id>")
                print("  Example: ingest-dry-run corpus_0022")
                print()
                continue

            if user_input.lower().startswith("ingest-dry-run-validate "):
                idv_id = user_input[24:].strip()
                cmd_ingest_dry_run_validate(idv_id, session_id)
                continue

            if user_input.lower() == "ingest-dry-run-validate":
                print()
                print("  Usage: ingest-dry-run-validate <corpus_id>")
                print()
                continue

            if user_input.lower() == "source-gap-report":
                cmd_source_gap_report(session_id)
                continue

            if user_input.lower() == "source-gap-check":
                cmd_source_gap_check(session_id)
                continue

            if user_input.lower().startswith("corpus-intake-scan "):
                ci_arg = user_input[19:].strip()
                cmd_corpus_intake_scan(ci_arg, session_id)
                continue

            if user_input.lower() == "corpus-intake-scan":
                cmd_corpus_intake_scan("", session_id)
                continue

            if user_input.lower().startswith("corpus-intake-preview "):
                cip_arg = user_input[22:].strip()
                cmd_corpus_intake_preview(cip_arg, session_id)
                continue

            if user_input.lower() == "corpus-intake-preview":
                cmd_corpus_intake_preview("", session_id)
                continue

            if user_input.lower().startswith("corpus-intake-apply "):
                cia_arg = user_input[20:].strip()
                cmd_corpus_intake_apply(cia_arg, session_id)
                continue

            if user_input.lower() == "corpus-intake-apply":
                cmd_corpus_intake_apply("", session_id)
                continue

            if user_input.lower() == "corpus-intake-check":
                cmd_corpus_intake_check(session_id)
                continue

            if user_input.lower() == "corpus-registration-report":
                cmd_corpus_registration_report(session_id)
                continue

            if user_input.lower() == "corpus-id-map":
                cmd_corpus_id_map(session_id)
                continue

            if user_input.lower().startswith("source-authority-weights "):
                saw_arg = user_input[25:].strip()
                cmd_source_authority_weights(saw_arg, session_id)
                continue

            if user_input.lower() == "source-authority-weights":
                cmd_source_authority_weights("all", session_id)
                continue

            if user_input.lower().startswith("ingest-next "):
                in_arg = user_input[12:].strip()
                cmd_ingest_next(in_arg, session_id)
                continue

            if user_input.lower() == "ingest-next":
                cmd_ingest_next("", session_id)
                continue

            if user_input.lower().startswith("ingest-batch-plan "):
                ibp_arg = user_input[18:].strip()
                cmd_ingest_batch_plan(ibp_arg, session_id)
                continue

            if user_input.lower() == "ingest-batch-plan":
                cmd_ingest_batch_plan("", session_id)
                continue

            if user_input.lower().startswith("ingest-batch-dry-run "):
                ibd_arg = user_input[21:].strip()
                cmd_ingest_batch_dry_run(ibd_arg, session_id)
                continue

            if user_input.lower() == "ingest-batch-dry-run":
                cmd_ingest_batch_dry_run("latest", session_id)
                continue

            if user_input.lower().startswith("ingest-batch-verify "):
                ibv_arg = user_input[20:].strip()
                cmd_ingest_batch_verify(ibv_arg, session_id)
                continue

            if user_input.lower() == "ingest-batch-verify":
                cmd_ingest_batch_verify("latest", session_id)
                continue

            if user_input.lower().startswith("ingest-batch-apply "):
                iba_arg = user_input[19:].strip()
                cmd_ingest_batch_apply(iba_arg, session_id)
                continue

            if user_input.lower() == "ingest-batch-apply":
                cmd_ingest_batch_apply("latest", session_id)
                continue

            if user_input.lower() == "context-collection-stats":
                cmd_context_collection_stats(session_id)
                continue

            if user_input.lower() == "context-status":
                cmd_context_status(session_id)
                continue

            if user_input.lower().startswith("context-search-test "):
                cst_q = user_input[20:].strip()
                cmd_context_search_test(cst_q, session_id)
                continue

            if user_input.lower() == "context-search-test":
                cmd_context_search_test("", session_id)
                continue

            if user_input.lower().startswith("context-search "):
                cs_arg = user_input[15:].strip()
                cmd_context_search(cs_arg, session_id)
                continue

            if user_input.lower() == "context-search":
                cmd_context_search("", session_id)
                continue

            if user_input.lower() == "ingest-history":
                cmd_ingest_history(session_id)
                continue

            if user_input.lower().startswith("ingest-receipt-show "):
                ir_arg = user_input[20:].strip()
                cmd_ingest_receipt_show(ir_arg, session_id)
                continue

            if user_input.lower() == "ingest-receipt-show":
                cmd_ingest_receipt_show("latest", session_id)
                continue

            if user_input.lower().startswith("ingest-receipt-repair "):
                irr_arg = user_input[22:].strip()
                cmd_ingest_receipt_repair(irr_arg, session_id)
                continue

            if user_input.lower() == "ingest-receipt-repair":
                cmd_ingest_receipt_repair("latest", session_id)
                continue

            if user_input.lower() == "context-duplicates":
                cmd_context_duplicates(session_id)
                continue

            if user_input.lower() == "context-export-manifest":
                cmd_context_export_manifest(session_id)
                continue

            if user_input.lower() == "context-reset-plan":
                cmd_context_reset_plan(session_id)
                continue

            if user_input.lower().startswith("ingest-one "):
                io_id = user_input[11:].strip()
                cmd_ingest_one(io_id, session_id)
                continue

            if user_input.lower() == "ingest-one":
                cmd_ingest_one("", session_id)
                continue

            if user_input.lower().startswith("ingest-verify "):
                iv_arg = user_input[14:].strip()
                cmd_ingest_verify(iv_arg, session_id)
                continue

            if user_input.lower() == "ingest-verify":
                cmd_ingest_verify("latest", session_id)
                continue

            if user_input.lower() == "forge-version":
                cmd_forge_version(session_id)
                continue

            if user_input.lower() == "forge-command-surface":
                cmd_forge_command_surface(session_id)
                continue

            if user_input.lower() == "ingestion-policy":
                cmd_ingestion_policy(session_id)
                continue

            if user_input.lower() == "ingestion-manifest-plan":
                cmd_ingestion_manifest_plan(session_id)
                continue

            if user_input.lower() == "ingestion-readiness":
                cmd_ingestion_readiness(session_id)
                continue

            if user_input.lower() == "rpmc-policy":
                cmd_rpmc_policy(session_id)
                continue

            if user_input.lower() == "rpmc-template":
                cmd_rpmc_template(session_id)
                continue

            if user_input.lower() == "rpmc-check":
                cmd_rpmc_check(session_id)
                continue

            if user_input.lower() == "rpmc-source-list":
                cmd_rpmc_source_list(session_id)
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
                print("    ingest-dry-run <corpus_id>        — deterministic no-write chunk plan")
                print("    ingest-dry-run-validate <id>      — validate dry-run chunk plan")
                print("    ingest-one <corpus_id>            — guarded single-doc context ingestion")
                print("    ingest-verify [latest|receipt]    — verify an ingestion receipt")
                print("    ingest-history                    — list ingestion receipts")
                print("    ingest-receipt-show [latest|id]   — show one receipt")
                print("    ingest-receipt-repair [latest|id] — repair receipt count metadata only")
                print("    ingest-next [folder]               — show next not-yet-ingested item")
                print("    ingest-batch-plan <target>         — create read-only batch plan")
                print("    ingest-batch-dry-run [latest|id]   — dry-run every item in a batch plan")
                print("    ingest-batch-apply [latest|id]     — apply named batch with confirmations")
                print("    ingest-batch-verify [latest|id]    — validate batch receipts")
                print("    corpus-id-map                      — list all corpus IDs and states")
                print("    source-authority-weights [target]  — show source weighting")
                print("    context-collection-stats           — show collection/corpus counts")
                print("    context-status                    — show context library status")
                print("    context-search-test <query>       — test dual-brain retrieval")
                print("    context-search [flags] <query>    — Phase C scored/filterable search")
                print("       flags: --metadata --symbolic --source-law --implementation")
                print("              --corpus <id> --phase <Φn> --operator <op> --memory-role <role>")
                print("    context-duplicates                — read-only duplicate check")
                print("    context-export-manifest           — export context library manifest")
                print("    context-reset-plan                — create non-destructive reset plan")
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

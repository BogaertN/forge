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
    print("│  FORGE  —  Local Coding Assistant  —  Level 0.9    │")
    print("│  Proposal Hygiene + Expanded Diagnostics.           │")
    print("│  No files will be changed by Forge.                 │")
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

    _print_banner(session_id, scope)

    files_changed = False

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

            if user_input.lower().startswith("propose "):
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
                print("    status                      — show current config")
                print("    audit                       — check audit log integrity")
                print("    propose <command>           — validate and create a proposal (bypasses LLM)")
                print("    diag <command>              — paste multi-line terminal output")
                print("    diag-session start <topic>  — start a diagnostic session")
                print("    diag-session status         — show active session chain")
                print("    diag-session close resolved — close session as resolved")
                print("    diag-session list           — list recent sessions")
                print("    quit                        — end session")
                print()
                print("  propose + diag workflow:")
                print("    forge> propose ollama version          ← validates & saves proposal")
                print("    [Nic runs: ollama version]")
                print("    forge> diag ollama version             ← paste output for analysis")
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
        # Always write session end to audit log
        write_session_end(session_id, files_changed)

        print()
        if files_changed:
            print("[forge] Session ended. Files were changed this session. See forge_audit.log.")
        else:
            print("[forge] Session ended. No files were changed this session.")
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

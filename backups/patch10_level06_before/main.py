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
import json
import datetime
import argparse
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parent
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
    print("│  FORGE  —  Local Coding Assistant  —  Level 0.5    │")
    print("│  Read-only observer mode. No files will be changed. │")
    print("└─────────────────────────────────────────────────────┘")
    print(f"  Session : {session_id}")
    print(f"  Scope   : {', '.join(scope) if scope else '(none)'}")
    print(f"  Model   : qwen3:8b via Ollama")
    print(f"  Audit   : {AUDIT_LOG}")
    print()
    print("  Type your question. 'quit' or Ctrl-C to exit.")
    print("  'status' to see config. 'audit' to check audit log.")
    print()


def _print_response(response: str):
    print()
    print(response)
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

            if user_input.lower() == "help":
                print()
                print("  Commands:")
                print("    status   — show current config")
                print("    audit    — check audit log integrity")
                print("    quit     — end session")
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

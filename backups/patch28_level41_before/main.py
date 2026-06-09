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
    print("│  FORGE  —  Local Coding Assistant  —  Level 4.0    │")
    print("│  Approval-Gated Patch Application.                  │")
    print("│  Type APPLY to write. Rollback always saved first.  │")
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
        print(f"[forge] PATCH APPLIED")
        print(f"  Target file  : {result['target_file']}")
        print(f"  Post SHA-256 : {result['post_sha256']}  ✓ matches plan future_sha256")
        print(f"  Rollback at  : {result['backup_path']}")
        print(f"  Audit hash   : {result['audit_hash']}  (PATCH_APPLIED)")
        print()
        print(f"  If anything is wrong, restore from rollback:")
        print(f"    Open: {result['backup_path']}")
        print(f"    Copy content between the separator lines back into: {result['target_file']}")
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
    (FORGE_ROOT / "apply_plans").mkdir(parents=True, exist_ok=True)

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

            if user_input.lower().startswith("patch-apply "):
                pa_arg = user_input[12:].strip()
                cmd_patch_apply(pa_arg, session_id)
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
                print("    patch-apply <plan_file>         — apply a preflighted patch (type APPLY to confirm)")
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

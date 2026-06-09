"""
Forge patcher.py
Level 2.0 — Patch Proposal Engine.

write_proposed_patch() creates a structured patch proposal document inside
~/forge/proposed_patches/. It NEVER modifies any project file.

SECURITY CONSTRAINTS:
  - Writes ONLY to ~/forge/proposed_patches/
  - Never writes to project directories
  - Never overwrites existing proposal files
  - target_file is treated as informational — used to read the original
    snippet for context, never written to
  - Refuses if target_file is outside approved/session scope
  - Refuses if target_file is in blocked_paths
  - Warns or refuses if proposed_snippet contains destructive shell patterns
    in code files (allows in documentation files)
  - No subprocess. No os.system. No shell. Storage and validation only.
"""

import os
import re
import datetime
import hashlib
from pathlib import Path
from typing import Optional

from . import memory as _mem
from .permissions import (
    is_path_allowed,
    is_path_blocked,
    is_filetype_allowed,
    get_approved_paths,
)

FORGE_ROOT      = Path(__file__).resolve().parents[2]
PATCHES_DIR     = FORGE_ROOT / "proposed_patches"

VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}

# Extensions where destructive shell patterns in proposed_snippet = REFUSE
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".sh", ".bash",
    ".rb", ".go", ".rs", ".c", ".cpp", ".h", ".java",
}

# Extensions where destructive shell patterns = WARN only (documentation context)
DOC_EXTENSIONS = {
    ".md", ".txt", ".rst", ".html", ".tex",
}

# Patterns in proposed_snippet that indicate destructive shell logic
DESTRUCTIVE_SNIPPET_PATTERNS = [
    (r"\brm\s+-rf?\b",                "rm -r or rm -rf detected"),
    (r"\bsudo\b",                     "sudo detected"),
    (r"\b(chmod|chown)\b",            "chmod/chown detected"),
    (r"\bmkfs\b",                     "mkfs (format disk) detected"),
    (r"\bdd\s+if=",                   "dd disk operation detected"),
    (r">\s*/dev/sd",                  "redirect to block device detected"),
    (r"\bshred\b",                    "shred detected"),
    (r"\bwipefs\b",                   "wipefs detected"),
    (r"\btruncate\b",                 "truncate detected"),
    (r"os\.system\(",                 "os.system() detected"),
    (r"subprocess\.call\(",           "subprocess.call() detected"),
    (r"shell\s*=\s*True",             "shell=True detected"),
]


# ─── VALIDATION ───────────────────────────────────────────────────────────────

def _check_destructive_snippet(
    proposed_snippet: str,
    target_ext: str,
) -> list[str]:
    """
    Scan the proposed_snippet for destructive patterns.
    Returns a list of warning strings (empty = clean).
    """
    warnings = []
    for pattern, label in DESTRUCTIVE_SNIPPET_PATTERNS:
        if re.search(pattern, proposed_snippet, re.IGNORECASE):
            warnings.append(label)
    return warnings


def _validate_patch_request(
    target_file: str,
    proposed_snippet: str,
    risk_level: str,
) -> tuple[bool, str, list[str]]:
    """
    Validate a patch proposal request.
    Returns (allowed: bool, reason: str, warnings: list[str]).
    """
    warnings = []

    # 1. Normalize target path
    target_file = os.path.expanduser(target_file.strip())

    # 2. Block check
    blocked, reason = is_path_blocked(target_file)
    if blocked:
        return False, f"Target file is in a blocked path: {reason}", []

    # 3. Scope check
    allowed, reason = is_path_allowed(target_file)
    if not allowed:
        return False, f"Target file is outside approved/session scope: {reason}", []

    # 4. Risk level
    if risk_level.upper() not in VALID_RISK_LEVELS:
        return False, f"Invalid risk_level '{risk_level}'. Use LOW, MEDIUM, or HIGH.", []

    # 5. Snippet destructive check
    ext = Path(target_file).suffix.lower()
    snippet_warnings = _check_destructive_snippet(proposed_snippet, ext)
    if snippet_warnings:
        if ext in CODE_EXTENSIONS:
            # Refuse for code files
            return (
                False,
                f"Proposed snippet contains destructive patterns in a code file ({ext}): "
                + "; ".join(snippet_warnings),
                [],
            )
        elif ext in DOC_EXTENSIONS:
            # Warn for documentation files (may be documenting shell commands)
            warnings.extend([f"WARNING: {w} (in doc file — allowed)" for w in snippet_warnings])
        else:
            # Unknown extension — warn
            warnings.extend([f"WARNING: {w}" for w in snippet_warnings])

    return True, "", warnings


# ─── PROPOSAL FILE FORMAT ─────────────────────────────────────────────────────

def _make_slug(target_file: str) -> str:
    name = os.path.basename(target_file)
    slug = re.sub(r"[^\w]", "_", name)
    return slug[:40].rstrip("_")


def _format_patch_proposal(
    session_id: str,
    target_file: str,
    problem_summary: str,
    original_snippet: str,
    proposed_snippet: str,
    reasoning: str,
    risk_level: str,
    test_plan: str,
    rollback_notes: str,
    warnings: list[str],
    proposal_path: Path,
    audit_hash: str,
) -> str:
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")

    warning_block = ""
    if warnings:
        warning_block = (
            "\n⚠ WARNINGS\n"
            "──────────\n"
            + "\n".join(f"  {w}" for w in warnings)
            + "\n"
        )

    return f"""FORGE PATCH PROPOSAL
{'═' * 66}
Target file     : {target_file}
Timestamp       : {timestamp}
Session ID      : {session_id}
Forge Level     : 2.0 — Patch Proposal Engine
Risk level      : {risk_level.upper()}
Proposal file   : {proposal_path}
{'═' * 66}
{warning_block}
PROBLEM SUMMARY
───────────────
{problem_summary}


ORIGINAL (current content of target region)
────────────────────────────────────────────
{original_snippet}


PROPOSED CHANGE
───────────────
{proposed_snippet}


REASONING
─────────
{reasoning}


TEST PLAN
─────────
{test_plan}


ROLLBACK NOTES
──────────────
{rollback_notes}


{'═' * 66}
IMPORTANT: THIS IS A PROPOSAL ONLY.

No project files were created, edited, moved, deleted, or executed.
Forge only wrote this proposal inside ~/forge/proposed_patches/.

To apply this change, Nic must manually edit the target file.
A future Forge apply-patch command may be added at a higher trust level.
{'═' * 66}
Audit entry hash : {audit_hash}
"""


# ─── MAIN ENTRY POINT ────────────────────────────────────────────────────────

def write_proposed_patch(
    session_id: str,
    target_file: str,
    problem_summary: str,
    original_snippet: str,
    proposed_snippet: str,
    reasoning: str,
    risk_level: str,
    test_plan: str,
    rollback_notes: str,
) -> dict:
    """
    Create a patch proposal document inside ~/forge/proposed_patches/.

    NEVER modifies any project file.
    NEVER overwrites an existing proposal file.
    Validates target_file scope and snippet safety before writing.
    """
    risk_level = risk_level.upper().strip()
    target_file = os.path.expanduser(target_file.strip())

    # ── Validate ──────────────────────────────────────────────────────────────
    allowed, reason, warnings = _validate_patch_request(
        target_file, proposed_snippet, risk_level
    )

    if not allowed:
        # Write refusal audit entry
        audit_hash = _mem.write_audit_entry(
            session_id=session_id,
            tool="PATCH_PROPOSAL_REFUSED",
            path=target_file,
            lines="-",
            reason=f"reason={reason[:120]}"
        )
        return {
            "ok": False,
            "allowed": False,
            "reason": reason,
            "audit_hash": audit_hash,
            "message": (
                f"PATCH PROPOSAL REFUSED\n\n"
                f"Target    : {target_file}\n"
                f"Reason    : {reason}\n\n"
                f"No files were modified.\n"
                f"Refusal logged. Audit hash: {audit_hash}"
            ),
        }

    # ── Create proposal file ──────────────────────────────────────────────────
    PATCHES_DIR.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = _make_slug(target_file)
    proposal_filename = f"{timestamp_str}_PATCH_{slug}.txt"
    proposal_path = PATCHES_DIR / proposal_filename

    # Never overwrite
    if proposal_path.exists():
        proposal_filename = f"{timestamp_str}_PATCH_{slug}_{os.getpid()}.txt"
        proposal_path = PATCHES_DIR / proposal_filename

    # ── Audit: PATCH_PROPOSAL_CREATED ─────────────────────────────────────────
    audit_hash = _mem.write_audit_entry(
        session_id=session_id,
        tool="PATCH_PROPOSAL_CREATED",
        path=str(proposal_path),
        lines="-",
        reason=(
            f"target={target_file} | "
            f"risk={risk_level} | "
            f"warnings={len(warnings)}"
        )
    )

    # ── Write proposal file ───────────────────────────────────────────────────
    doc = _format_patch_proposal(
        session_id=session_id,
        target_file=target_file,
        problem_summary=problem_summary,
        original_snippet=original_snippet,
        proposed_snippet=proposed_snippet,
        reasoning=reasoning,
        risk_level=risk_level,
        test_plan=test_plan,
        rollback_notes=rollback_notes,
        warnings=warnings,
        proposal_path=proposal_path,
        audit_hash=audit_hash,
    )

    try:
        proposal_path.write_text(doc, encoding="utf-8")
    except OSError as e:
        return {
            "ok": False,
            "error": f"Could not write proposal file: {e}",
            "audit_hash": audit_hash,
        }

    warning_note = ""
    if warnings:
        warning_note = (
            f"\n⚠ Warnings:\n" +
            "\n".join(f"  {w}" for w in warnings)
        )

    return {
        "ok": True,
        "allowed": True,
        "proposal_path": str(proposal_path),
        "audit_hash": audit_hash,
        "warnings": warnings,
        "message": (
            f"PATCH PROPOSAL CREATED\n\n"
            f"Target file   : {target_file}\n"
            f"Risk level    : {risk_level}\n"
            f"Proposal file : {proposal_path}\n"
            f"Audit hash    : {audit_hash}"
            f"{warning_note}\n\n"
            f"{'─' * 50}\n"
            f"IMPORTANT: No project files were modified.\n"
            f"Forge only wrote this proposal inside ~/forge/proposed_patches/.\n"
            f"To apply the change, Nic must manually edit the target file.\n"
            f"{'─' * 50}"
        ),
    }

"""
Forge preflight.py
Level 3.0 — Rollback Registry / Apply Preflight.

run_preflight() validates a patch proposal for readiness, saves a rollback
snapshot of the target file, and generates a complete apply plan.

It NEVER modifies any project file.

Steps:
  1. Validate proposal file is inside ~/forge/proposed_patches/
  2. Parse proposal: target_file, original_snippet, proposed_snippet
  3. Confirm target_file exists, is approved, not blocked
  4. Confirm original_snippet exists in target_file (count occurrences)
  5. Compute exact future file content
  6. Save rollback snapshot → ~/forge/rollback_registry/
  7. Save apply plan     → ~/forge/apply_plans/
  8. Audit PATCH_APPLY_PLAN_CREATED
  9. Return result dict

SECURITY CONSTRAINTS:
  No subprocess. No os.system. No shell. No project file writes.
  Reads target file for snapshot/plan. Writes ONLY to Forge internal dirs.
"""

import os
import re
import hashlib
import datetime
from pathlib import Path

from . import memory as _mem
from .permissions import is_path_allowed, is_path_blocked

FORGE_ROOT        = Path(__file__).resolve().parents[2]
PROPOSALS_DIR     = FORGE_ROOT / "proposed_patches"
ROLLBACK_DIR      = FORGE_ROOT / "rollback_registry"
APPLY_PLANS_DIR   = FORGE_ROOT / "apply_plans"

MAX_FILE_SIZE_BYTES = 1_048_576   # 1 MB cap on files we snapshot


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _find_snippet_line(content: str, snippet: str) -> int | None:
    """Return the 1-indexed line number where snippet starts, or None."""
    lines = content.splitlines()
    snippet_lines = snippet.splitlines()
    if not snippet_lines:
        return None
    first_line = snippet_lines[0]
    for i, line in enumerate(lines):
        if first_line in line or line in first_line:
            # Verify full multi-line match
            block = "\n".join(lines[i:i + len(snippet_lines)])
            if snippet in content[content.find(block):content.find(block) + len(block) + 1]:
                return i + 1
    # Fallback: find by substring offset
    idx = content.find(snippet)
    if idx == -1:
        return None
    return content[:idx].count("\n") + 1


def _count_occurrences(content: str, snippet: str) -> int:
    count = 0
    start = 0
    while True:
        idx = content.find(snippet, start)
        if idx == -1:
            break
        count += 1
        start = idx + 1
    return count


# ─── DOCUMENT FORMATTERS ──────────────────────────────────────────────────────

def _format_rollback_snapshot(
    target_file: str,
    original_content: str,
    file_sha256: str,
    proposal_name: str,
    snapshot_path: Path,
) -> str:
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    return f"""FORGE ROLLBACK SNAPSHOT
{'═' * 66}
Target file     : {target_file}
Snapshot time   : {timestamp}
File SHA-256    : {file_sha256}
Proposal        : {proposal_name}
Snapshot file   : {snapshot_path}
{'═' * 66}

{original_content}

{'═' * 66}
RESTORE INSTRUCTION:
  Copy the content above (between the two separator lines) back into
  the target file verbatim to undo the applied change.
  Verify with: sha256sum {target_file}   (should match {file_sha256})
{'═' * 66}
"""


def _format_apply_plan(
    proposal_path: Path,
    target_file: str,
    original_snippet: str,
    proposed_snippet: str,
    original_content: str,
    future_content: str,
    original_sha256: str,
    future_sha256: str,
    snippet_line: int | None,
    occurrence_count: int,
    rollback_path: Path,
    session_id: str,
    audit_hash: str,
    test_plan: str,
) -> str:
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    line_info = f"line {snippet_line}" if snippet_line else "offset unknown"

    warning = ""
    if occurrence_count > 1:
        warning = (
            f"\n  ⚠ WARNING: Original snippet appears {occurrence_count} times in target.\n"
            f"    Only the FIRST occurrence will be replaced when applying.\n"
            f"    Review carefully before applying.\n"
        )

    return f"""FORGE APPLY PLAN
{'═' * 66}
Proposal file   : {proposal_path}
Target file     : {target_file}
Timestamp       : {timestamp}
Session ID      : {session_id}
Apply plan hash : {audit_hash}
{'═' * 66}

PREFLIGHT STATUS
────────────────
  Proposal file        : FOUND
  Target file          : FOUND  ({len(original_content):,} bytes)
  Original snippet     : FOUND at {line_info}
  Snippet occurrences  : {occurrence_count}
  Original SHA-256     : {original_sha256}
  Future SHA-256       : {future_sha256}
{warning}
ROLLBACK SNAPSHOT
─────────────────
  Saved to   : {rollback_path}
  File SHA-256 (before change) : {original_sha256}
  ← Keep this file safe before applying any change.

COMPUTED FUTURE CONTENT
───────────────────────
{future_content}

APPLY INSTRUCTION (manual — Forge does NOT apply automatically)
───────────────────────────────────────────────────────────────
  1. Verify rollback snapshot:  ls -lh {rollback_path}
  2. Open the target file:      {target_file}
  3. Find the original snippet (around {line_info}).
  4. Replace it with the proposed snippet.
     OR: copy the COMPUTED FUTURE CONTENT above directly into the file.
  5. Verify the SHA-256 of the modified file matches: {future_sha256}
     Command: sha256sum {target_file}   (first 16 chars)
  6. Run test plan: {test_plan or '(see proposal file for test plan)'}
  7. If anything goes wrong: restore from rollback at step 1.

{'═' * 66}
No project files were modified by this preflight.
Audit hash : {audit_hash}  (PATCH_APPLY_PLAN_CREATED)
{'═' * 66}
"""


# ─── MAIN ENTRY POINT ─────────────────────────────────────────────────────────

def run_preflight(
    session_id: str,
    proposal_file_arg: str,
    parsed_fields: dict | None = None,
) -> dict:
    """
    Run the full apply preflight for a patch proposal.

    parsed_fields: optional pre-parsed dict (target_file, original_snippet,
    proposed_snippet, test_plan). If not provided, parses from proposal_file_arg.

    Returns a result dict with ok, apply_plan_path, rollback_path, status details.
    """
    # ── Validate proposal path ────────────────────────────────────────────────
    proposal_path = Path(os.path.expanduser(proposal_file_arg.strip()))

    # Accept bare filename
    if not proposal_path.is_absolute():
        candidate = PROPOSALS_DIR / proposal_file_arg.strip()
        if candidate.exists():
            proposal_path = candidate

    # Path boundary check before existence check
    if proposal_path.is_absolute():
        try:
            proposal_path.relative_to(PROPOSALS_DIR)
        except ValueError:
            return {
                "ok": False,
                "error": f"Proposal must be inside ~/forge/proposed_patches/ — got: {proposal_path}",
                "refused_reason": "path_outside_proposals_dir",
            }

    if not proposal_path.exists():
        return {"ok": False, "error": f"Proposal file not found: {proposal_path}"}

    # ── Parse fields ──────────────────────────────────────────────────────────
    if parsed_fields is None:
        content = proposal_path.read_text(encoding="utf-8")
        from main import _parse_proposal_file
        parsed_fields = _parse_proposal_file(content)
        # Also extract test_plan if possible
        tp_match = re.search(r"TEST PLAN\n─+\n(.*?)\n\n\nROLLBACK", content, re.DOTALL)
        parsed_fields["test_plan"] = tp_match.group(1).strip() if tp_match else ""

    target_file      = parsed_fields.get("target_file", "").strip()
    original_snippet = parsed_fields.get("original_snippet", "").strip("\n")
    proposed_snippet = parsed_fields.get("proposed_snippet", "").strip("\n")
    test_plan        = parsed_fields.get("test_plan", "")

    if not target_file:
        return {"ok": False, "error": "Cannot parse 'Target file' from proposal."}
    if not original_snippet:
        return {"ok": False, "error": "Cannot parse 'ORIGINAL' snippet from proposal."}
    if not proposed_snippet:
        return {"ok": False, "error": "Cannot parse 'PROPOSED CHANGE' snippet from proposal."}

    # ── Validate target file ──────────────────────────────────────────────────
    blocked, reason = is_path_blocked(target_file)
    if blocked:
        _mem.write_audit_entry(
            session_id=session_id,
            tool="PATCH_APPLY_PLAN_REFUSED",
            path=target_file,
            lines="-",
            reason=f"target blocked: {reason[:120]}"
        )
        return {"ok": False, "error": f"Target file is blocked: {reason}"}

    allowed, reason = is_path_allowed(target_file)
    if not allowed:
        _mem.write_audit_entry(
            session_id=session_id,
            tool="PATCH_APPLY_PLAN_REFUSED",
            path=target_file,
            lines="-",
            reason=f"target out of scope: {reason[:120]}"
        )
        return {"ok": False, "error": f"Target file is outside approved/session scope: {reason}"}

    if not os.path.exists(target_file):
        return {"ok": False, "error": f"Target file does not exist: {target_file}"}

    # ── Read target file ──────────────────────────────────────────────────────
    file_size = os.path.getsize(target_file)
    if file_size > MAX_FILE_SIZE_BYTES:
        return {
            "ok": False,
            "error": f"Target file too large for preflight: {file_size:,} bytes (max {MAX_FILE_SIZE_BYTES:,})"
        }

    try:
        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            original_content = f.read()
    except OSError as e:
        return {"ok": False, "error": f"Cannot read target file: {e}"}

    # ── Verify original snippet exists ────────────────────────────────────────
    if original_snippet not in original_content:
        return {
            "ok": False,
            "error": (
                "Original snippet NOT found in target file. "
                "The file may have changed since this proposal was written. "
                "Create a fresh proposal with the current content."
            ),
            "snippet_found": False,
        }

    occurrence_count = _count_occurrences(original_content, original_snippet)
    snippet_line     = _find_snippet_line(original_content, original_snippet)

    # ── Compute future content ────────────────────────────────────────────────
    future_content   = original_content.replace(original_snippet, proposed_snippet, 1)
    original_sha256  = _sha256(original_content)
    future_sha256    = _sha256(future_content)

    # ── Save rollback snapshot ────────────────────────────────────────────────
    ROLLBACK_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_str  = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug           = re.sub(r"[^\w]", "_", os.path.basename(target_file))[:30]
    rollback_name  = f"{timestamp_str}_ROLLBACK_{slug}.txt"
    rollback_path  = ROLLBACK_DIR / rollback_name

    rollback_doc = _format_rollback_snapshot(
        target_file=target_file,
        original_content=original_content,
        file_sha256=original_sha256,
        proposal_name=proposal_path.name,
        snapshot_path=rollback_path,
    )

    try:
        rollback_path.write_text(rollback_doc, encoding="utf-8")
    except OSError as e:
        return {"ok": False, "error": f"Cannot write rollback snapshot: {e}"}

    # ── Write audit then build apply plan (audit_hash goes in the plan) ───────
    APPLY_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    plan_name  = f"{timestamp_str}_PLAN_{slug}.txt"
    plan_path  = APPLY_PLANS_DIR / plan_name

    audit_hash = _mem.write_audit_entry(
        session_id=session_id,
        tool="PATCH_APPLY_PLAN_CREATED",
        path=str(plan_path),
        lines=f"{len(future_content.splitlines())} lines in future content",
        reason=(
            f"proposal={proposal_path.name} | "
            f"target={target_file} | "
            f"snippet_line={snippet_line} | "
            f"occurrences={occurrence_count} | "
            f"original_sha256={original_sha256} | "
            f"future_sha256={future_sha256} | "
            f"rollback={rollback_name}"
        )
    )

    # ── Save apply plan ───────────────────────────────────────────────────────
    plan_doc = _format_apply_plan(
        proposal_path=proposal_path,
        target_file=target_file,
        original_snippet=original_snippet,
        proposed_snippet=proposed_snippet,
        original_content=original_content,
        future_content=future_content,
        original_sha256=original_sha256,
        future_sha256=future_sha256,
        snippet_line=snippet_line,
        occurrence_count=occurrence_count,
        rollback_path=rollback_path,
        session_id=session_id,
        audit_hash=audit_hash,
        test_plan=test_plan,
    )

    try:
        plan_path.write_text(plan_doc, encoding="utf-8")
    except OSError as e:
        return {"ok": False, "error": f"Cannot write apply plan: {e}"}

    return {
        "ok":              True,
        "apply_plan_path": str(plan_path),
        "rollback_path":   str(rollback_path),
        "target_file":     target_file,
        "original_sha256": original_sha256,
        "future_sha256":   future_sha256,
        "snippet_line":    snippet_line,
        "occurrence_count": occurrence_count,
        "audit_hash":      audit_hash,
    }

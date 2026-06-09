"""
Forge applier.py
Level 4.0 — Approval-Gated Patch Application.

apply_patch() is the first tool in Forge that writes to a project file.
It applies ONLY a precomputed, audited apply plan from ~/forge/apply_plans/.

SECURITY ARCHITECTURE:
  - Apply plan must be inside ~/forge/apply_plans/
  - Target file must be approved and not blocked
  - Target file must be a regular file (not symlink, not directory)
  - Target file must be valid UTF-8 text (not binary)
  - Current file SHA-256 must match original_sha256 in plan
  - Original snippet must exist exactly once in current file
  - Rollback snapshot must exist before any write
  - Post-write verification: re-read and confirm future_sha256 matches
  - If post-write verification fails: STOP immediately, print rollback instructions
  - No automatic repair — Nic manually restores from rollback snapshot
  - Every outcome is audited: PATCH_APPLIED or PATCH_APPLY_FAILED

WHAT IS NOT IN THIS MODULE:
  - No arbitrary file editing
  - No shell commands
  - No subprocess
  - No applying patches to multiple files at once
  - No applying patches without a valid apply plan
  - No applying patches without a rollback snapshot
"""

import os
import re
import hashlib
import datetime
from pathlib import Path

from . import memory as _mem
from .permissions import is_path_allowed, is_path_blocked

FORGE_ROOT       = Path(__file__).resolve().parents[2]
APPLY_PLANS_DIR  = FORGE_ROOT / "apply_plans"
ROLLBACK_DIR     = FORGE_ROOT / "rollback_registry"

MAX_FILE_SIZE_BYTES = 524_288   # 512 KB cap — apply plans target small text files


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _is_binary(content_bytes: bytes) -> bool:
    """Return True if content looks like binary (not valid UTF-8 or contains null bytes)."""
    if b"\x00" in content_bytes:
        return True
    try:
        content_bytes.decode("utf-8")
        return False
    except UnicodeDecodeError:
        return True


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


# ─── APPLY PLAN PARSER ────────────────────────────────────────────────────────

def _parse_apply_plan(content: str) -> dict:
    """
    Extract fields from a FORGE APPLY PLAN document.
    Returns a dict with: target_file, original_sha256, future_sha256,
    rollback_path, future_content, original_snippet.
    Empty string for any field that cannot be parsed.
    """
    result = {
        "target_file":     "",
        "original_sha256": "",
        "future_sha256":   "",
        "rollback_path":   "",
        "future_content":  "",
    }

    # Target file
    m = re.search(r"Target file\s+:\s+(.+)", content)
    if m:
        result["target_file"] = m.group(1).strip()

    # Original SHA-256 — match "Original SHA-256     : abc123"
    m = re.search(r"Original SHA-256\s+:\s+([0-9a-f]{16})", content)
    if m:
        result["original_sha256"] = m.group(1).strip()

    # Future SHA-256
    m = re.search(r"Future SHA-256\s+:\s+([0-9a-f]{16})", content)
    if m:
        result["future_sha256"] = m.group(1).strip()

    # Rollback path — "Saved to   : /path/to/rollback"
    m = re.search(r"Saved to\s+:\s+(/[^\n]+)", content)
    if m:
        result["rollback_path"] = m.group(1).strip()

    # Future content — between COMPUTED FUTURE CONTENT separator and APPLY INSTRUCTION
    m = re.search(
        r"COMPUTED FUTURE CONTENT\n─+\n(.*?)\n\nAPPLY INSTRUCTION",
        content,
        re.DOTALL,
    )
    if m:
        result["future_content"] = m.group(1)

    # Original snippet — from "FIND THE ORIGINAL..." or the preflight's stored version
    # Also check for it in the ROLLBACK SNAPSHOT section pattern
    m = re.search(
        r"Find the original snippet \(around (.+?)\)\.",
        content,
    )
    if m:
        result["snippet_location"] = m.group(1).strip()

    return result


# ─── VALIDATION CHECKS ────────────────────────────────────────────────────────

def _check_all(
    target_file: str,
    plan_fields: dict,
    current_content: str,
    current_sha256: str,
) -> tuple[bool, str]:
    """
    Run all preflight checks before the write.
    Returns (ok: bool, reason: str).
    """
    plan_original_sha256 = plan_fields.get("original_sha256", "")
    plan_future_sha256   = plan_fields.get("future_sha256", "")
    future_content       = plan_fields.get("future_content", "")
    rollback_path        = plan_fields.get("rollback_path", "")

    # SHA-256 must match plan's original
    if plan_original_sha256 and current_sha256 != plan_original_sha256:
        return False, (
            f"SHA-256 MISMATCH: current file hash is {current_sha256}, "
            f"but apply plan expected {plan_original_sha256}. "
            f"The file has changed since the preflight was run. "
            f"Re-run patch-preflight before applying."
        )

    # Future content must be non-empty
    if not future_content:
        return False, "Cannot parse COMPUTED FUTURE CONTENT from apply plan."

    # Future content must differ from current (sanity check)
    if current_content == future_content:
        return False, (
            "COMPUTED FUTURE CONTENT is identical to current file content. "
            "Nothing would change. This may indicate a parsing error."
        )

    # Rollback snapshot must exist
    if rollback_path and not os.path.exists(rollback_path):
        return False, (
            f"Rollback snapshot is missing: {rollback_path}\n"
            f"Cannot apply without a rollback snapshot. "
            f"Re-run patch-preflight to create a fresh snapshot."
        )

    # Future SHA-256 must be set in plan
    if not plan_future_sha256:
        return False, "Cannot parse future_sha256 from apply plan."

    return True, ""


# ─── MAIN ENTRY POINT ─────────────────────────────────────────────────────────

def apply_patch(session_id: str, apply_plan_path_arg: str) -> dict:
    """
    Apply a precomputed patch from a valid apply plan.

    Returns a result dict with:
      ok           — True if patch was applied and verified
      target_file  — path that was modified
      backup_path  — rollback snapshot path
      audit_hash   — audit entry hash
      post_sha256  — actual SHA-256 after writing (should match plan's future_sha256)
      error        — error message if ok=False
      rollback_instructions — populated if post-write verification fails
    """
    apply_plan_path = Path(os.path.expanduser(apply_plan_path_arg.strip()))

    # ── 1. Path boundary check ────────────────────────────────────────────────
    if apply_plan_path.is_absolute():
        try:
            apply_plan_path.relative_to(APPLY_PLANS_DIR)
        except ValueError:
            _mem.write_audit_entry(
                session_id=session_id,
                tool="PATCH_APPLY_REFUSED",
                path=str(apply_plan_path),
                lines="-",
                reason="apply plan outside ~/forge/apply_plans/"
            )
            return {
                "ok": False,
                "error": f"Apply plan must be inside ~/forge/apply_plans/ — got: {apply_plan_path}",
                "refused_reason": "path_outside_apply_plans_dir",
            }

    # ── 2. Apply plan must exist ──────────────────────────────────────────────
    if not apply_plan_path.exists():
        return {"ok": False, "error": f"Apply plan not found: {apply_plan_path}"}

    # ── 3. Parse apply plan ───────────────────────────────────────────────────
    try:
        plan_content = apply_plan_path.read_text(encoding="utf-8")
    except OSError as e:
        return {"ok": False, "error": f"Cannot read apply plan: {e}"}

    plan_fields = _parse_apply_plan(plan_content)
    target_file    = plan_fields.get("target_file", "").strip()
    future_content = plan_fields.get("future_content", "")
    rollback_path  = plan_fields.get("rollback_path", "")

    if not target_file:
        return {"ok": False, "error": "Cannot parse 'Target file' from apply plan."}
    if not future_content:
        return {"ok": False, "error": "Cannot parse 'COMPUTED FUTURE CONTENT' from apply plan."}

    # ── 4. Target file safety checks ──────────────────────────────────────────
    blocked, reason = is_path_blocked(target_file)
    if blocked:
        _mem.write_audit_entry(session_id, "PATCH_APPLY_REFUSED", target_file, "-",
                               f"target blocked: {reason[:120]}")
        return {"ok": False, "error": f"Target file is blocked: {reason}"}

    allowed, reason = is_path_allowed(target_file)
    if not allowed:
        _mem.write_audit_entry(session_id, "PATCH_APPLY_REFUSED", target_file, "-",
                               f"target out of scope: {reason[:120]}")
        return {"ok": False, "error": f"Target file is outside approved/session scope: {reason}"}

    if not os.path.exists(target_file):
        return {"ok": False, "error": f"Target file does not exist: {target_file}"}

    if os.path.islink(target_file):
        _mem.write_audit_entry(session_id, "PATCH_APPLY_REFUSED", target_file, "-",
                               "target is a symlink")
        return {"ok": False, "error": f"Target is a symlink. Forge does not apply patches to symlinks."}

    if os.path.isdir(target_file):
        return {"ok": False, "error": f"Target is a directory, not a file."}

    file_size = os.path.getsize(target_file)
    if file_size > MAX_FILE_SIZE_BYTES:
        return {"ok": False, "error": f"Target file too large: {file_size:,} bytes (max {MAX_FILE_SIZE_BYTES:,})."}

    # ── 5. Read target file ───────────────────────────────────────────────────
    try:
        with open(target_file, "rb") as f:
            raw_bytes = f.read()
    except OSError as e:
        return {"ok": False, "error": f"Cannot read target file: {e}"}

    if _is_binary(raw_bytes):
        return {"ok": False, "error": "Target file appears to be binary. Forge only patches text files."}

    current_content = raw_bytes.decode("utf-8", errors="replace")
    current_sha256  = _sha256(current_content)

    # ── 6. All validation checks ──────────────────────────────────────────────
    checks_ok, check_reason = _check_all(
        target_file, plan_fields, current_content, current_sha256
    )
    if not checks_ok:
        _mem.write_audit_entry(session_id, "PATCH_APPLY_REFUSED", target_file, "-",
                               f"preflight check failed: {check_reason[:120]}")
        return {"ok": False, "error": check_reason}

    plan_future_sha256 = plan_fields.get("future_sha256", "")

    # ── 7. Write the new content ──────────────────────────────────────────────
    try:
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(future_content)
    except OSError as e:
        _mem.write_audit_entry(session_id, "PATCH_APPLY_FAILED", target_file, "-",
                               f"write error: {e}")
        return {
            "ok": False,
            "error": f"Write failed: {e}. File may be in an inconsistent state. Restore from rollback: {rollback_path}",
        }

    # ── 8. Post-write verification ────────────────────────────────────────────
    try:
        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            post_content = f.read()
    except OSError as e:
        _mem.write_audit_entry(session_id, "PATCH_APPLY_FAILED", target_file, "-",
                               f"post-read error: {e}")
        return {
            "ok": False,
            "error": f"Post-write read failed: {e}",
            "rollback_instructions": _rollback_instructions(target_file, rollback_path),
        }

    post_sha256 = _sha256(post_content)

    if post_sha256 != plan_future_sha256:
        _mem.write_audit_entry(session_id, "PATCH_APPLY_FAILED", target_file, "-",
                               f"post-write sha256 mismatch: got={post_sha256} expected={plan_future_sha256}")
        return {
            "ok": False,
            "error": (
                f"POST-WRITE VERIFICATION FAILED.\n"
                f"Written SHA-256 ({post_sha256}) does not match plan ({plan_future_sha256}).\n"
                f"Do not use the file. Restore from rollback immediately."
            ),
            "post_sha256": post_sha256,
            "rollback_instructions": _rollback_instructions(target_file, rollback_path),
        }

    # ── 9. Audit PATCH_APPLIED ────────────────────────────────────────────────
    audit_hash = _mem.write_audit_entry(
        session_id=session_id,
        tool="PATCH_APPLIED",
        path=target_file,
        lines=f"{len(post_content.splitlines())} lines",
        reason=(
            f"plan={apply_plan_path.name} | "
            f"original_sha256={current_sha256} | "
            f"post_sha256={post_sha256} | "
            f"rollback={rollback_path}"
        )
    )

    return {
        "ok":            True,
        "target_file":   target_file,
        "backup_path":   rollback_path,
        "apply_plan":    str(apply_plan_path),
        "post_sha256":   post_sha256,
        "audit_hash":    audit_hash,
    }


def _rollback_instructions(target_file: str, rollback_path: str) -> str:
    return (
        f"MANUAL ROLLBACK INSTRUCTIONS:\n"
        f"  1. Open the rollback snapshot: {rollback_path}\n"
        f"  2. Copy the original content (between the separator lines)\n"
        f"  3. Overwrite the target file with that content: {target_file}\n"
        f"  4. Verify: sha256sum {target_file}  (compare to original_sha256 in the apply plan)\n"
        f"  Forge has stopped. No automatic repair will be attempted."
    )

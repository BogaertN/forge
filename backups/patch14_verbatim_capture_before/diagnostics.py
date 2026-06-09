"""
Forge diagnostics.py
Level 0.7 — Manual Diagnostic Loop.

analyze_command_output() receives terminal output that Nic pasted manually,
validates it, stores it in a diagnostic session file, and audits the event.

CRITICAL IMPLEMENTATION CONTRACT:
  This module NEVER executes any command.
  No subprocess. No os.system. No os.popen. No eval. No exec. No shell=True.
  Receive, validate, store, audit only.
  The LLM performs the analysis after this tool returns.
"""

import os
import re
import datetime
from pathlib import Path

from . import memory as _mem

FORGE_ROOT       = Path(__file__).resolve().parents[2]
DIAGNOSTICS_DIR  = FORGE_ROOT / "diagnostics"

MAX_OUTPUT_BYTES   = 51_200   # 50 KB — prevents absurd pastes
MAX_COMMAND_LENGTH = 500
MAX_CONTEXT_LENGTH = 1000

# Patterns that suggest sensitive data in pasted output.
# We warn but do not block — Nic controls what he pastes.
SENSITIVE_OUTPUT_PATTERNS = [
    (r"(?i)password\s*[:=]\s*\S+",    "possible password in output"),
    (r"(?i)secret\s*[:=]\s*\S+",      "possible secret in output"),
    (r"(?i)api[_\-]?key\s*[:=]\s*\S+","possible API key in output"),
    (r"(?i)token\s*[:=]\s*\S+",       "possible token in output"),
    (r"BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY", "private key material in output"),
    (r"-----BEGIN CERTIFICATE-----",   "certificate material in output"),
]


# ─── SENSITIVE OUTPUT SCAN ────────────────────────────────────────────────────

def _scan_for_sensitive(output: str) -> list[str]:
    """
    Scan pasted output for patterns that look like sensitive data.
    Returns a list of warning strings (empty if clean).
    Does not block — only warns so Nic is aware before it's stored.
    """
    warnings = []
    for pattern, label in SENSITIVE_OUTPUT_PATTERNS:
        if re.search(pattern, output):
            warnings.append(label)
    return warnings


# ─── DIAGNOSTIC FILE FORMATTING ───────────────────────────────────────────────

def _make_topic_slug(command: str, context: str) -> str:
    """Generate a filename-safe slug from the command or context."""
    source = context if context.strip() else command
    slug = re.sub(r"[^\w\s-]", "", source)
    slug = re.sub(r"\s+", "_", slug.strip())
    return slug[:40].rstrip("_") or "diagnostic"


def _format_diagnostic_file(
    session_id: str,
    command: str,
    output: str,
    context: str,
    sensitive_warnings: list[str],
    diagnostic_path: Path,
    audit_hash: str,
) -> str:
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    output_lines = output.count("\n") + 1
    output_bytes = len(output.encode("utf-8"))

    warnings_section = ""
    if sensitive_warnings:
        warnings_section = (
            "\n⚠ SENSITIVE DATA WARNINGS\n"
            "─────────────────────────\n"
            + "\n".join(f"  - {w}" for w in sensitive_warnings)
            + "\n\n"
            "This file contains output that may include sensitive data.\n"
            "Do not share this diagnostic file publicly.\n"
        )

    return f"""FORGE DIAGNOSTIC SESSION
{'═' * 66}
Command run     : {command}
Timestamp       : {timestamp}
Session ID      : {session_id}
Forge Level     : 0.7 — Manual Diagnostic Loop
Context         : {context or '(none provided)'}
Output size     : {output_lines} lines / {output_bytes} bytes
Diagnostic file : {diagnostic_path}
{'═' * 66}
{warnings_section}

COMMAND RUN BY NIC
──────────────────
  {command}


TERMINAL OUTPUT (pasted by Nic)
────────────────────────────────
{output}


{'═' * 66}
NOTE: Forge analysis appears in the session conversation.
      The next diagnostic step, if any, is in a PROPOSAL file.
{'═' * 66}
Audit entry hash : {audit_hash}
"""


# ─── MAIN ENTRY POINT ────────────────────────────────────────────────────────

def analyze_command_output(
    session_id: str,
    command: str,
    output: str,
    context: str = "",
) -> dict:
    """
    Receive, validate, store, and audit terminal output pasted by Nic.
    Returns a result dict for the LLM to analyze.

    NEVER executes anything. NEVER calls subprocess. NEVER calls os.system.
    Pure receive-validate-store-audit loop.
    """
    # ── Validate inputs ───────────────────────────────────────────────────────

    command = command.strip()
    output  = output.strip()
    context = context.strip()

    if not command:
        return {"ok": False, "error": "No command provided. What command did Nic run?"}

    if len(command) > MAX_COMMAND_LENGTH:
        return {"ok": False, "error": f"Command too long (max {MAX_COMMAND_LENGTH} chars)."}

    if not output:
        return {
            "ok": False,
            "error": (
                "No output provided. Paste the terminal output from the command. "
                "If the command produced no output, say 'no output' explicitly."
            )
        }

    output_bytes = len(output.encode("utf-8"))
    if output_bytes > MAX_OUTPUT_BYTES:
        return {
            "ok": False,
            "error": (
                f"Output is too large ({output_bytes:,} bytes, max {MAX_OUTPUT_BYTES:,}). "
                f"Paste the first 200 lines instead: use `head -n 200` on the output."
            )
        }

    if len(context) > MAX_CONTEXT_LENGTH:
        context = context[:MAX_CONTEXT_LENGTH] + " [truncated]"

    # ── Sensitive data scan ───────────────────────────────────────────────────
    sensitive_warnings = _scan_for_sensitive(output)

    # ── Save diagnostic file ──────────────────────────────────────────────────
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = _make_topic_slug(command, context)
    diag_filename = f"{timestamp_str}_{slug}.txt"
    diag_path = DIAGNOSTICS_DIR / diag_filename

    # ── Audit: DIAGNOSTIC_OUTPUT_RECEIVED ─────────────────────────────────────
    audit_hash = _mem.write_audit_entry(
        session_id=session_id,
        tool="DIAGNOSTIC_OUTPUT_RECEIVED",
        path=str(diag_path),
        lines=f"{output.count(chr(10)) + 1} lines",
        reason=(
            f"command={command[:60]} | "
            f"output_bytes={output_bytes} | "
            f"sensitive_warnings={len(sensitive_warnings)}"
        )
    )

    # ── Write file ────────────────────────────────────────────────────────────
    doc = _format_diagnostic_file(
        session_id=session_id,
        command=command,
        output=output,
        context=context,
        sensitive_warnings=sensitive_warnings,
        diagnostic_path=diag_path,
        audit_hash=audit_hash,
    )

    try:
        diag_path.write_text(doc, encoding="utf-8")
    except OSError as e:
        return {"ok": False, "error": f"Could not save diagnostic file: {e}"}

    # ── Audit: DIAGNOSTIC_SESSION_SAVED ───────────────────────────────────────
    _mem.write_audit_entry(
        session_id=session_id,
        tool="DIAGNOSTIC_SESSION_SAVED",
        path=str(diag_path),
        lines="-",
        reason=f"diagnostic file written | slug={slug}"
    )

    # ── Return structured data for LLM analysis ───────────────────────────────
    output_lines = output.splitlines()
    preview_lines = output_lines[:50]
    truncated = len(output_lines) > 50

    result = {
        "ok": True,
        "command": command,
        "output_line_count": len(output_lines),
        "output_bytes": output_bytes,
        "diagnostic_path": str(diag_path),
        "audit_hash": audit_hash,
        "sensitive_warnings": sensitive_warnings,
        "context": context or "",
        "output_preview": "\n".join(preview_lines) + (
            f"\n... [{len(output_lines) - 50} more lines — full output in diagnostic file]"
            if truncated else ""
        ),
        "full_output": output,
    }

    # Build the message the LLM sees after calling this tool
    warning_note = ""
    if sensitive_warnings:
        warning_note = (
            f"\n\n⚠ SENSITIVE DATA DETECTED IN OUTPUT:\n"
            + "\n".join(f"  - {w}" for w in sensitive_warnings)
            + "\nNote this in your analysis."
        )

    result["message"] = (
        f"Diagnostic output received and stored.\n\n"
        f"Command    : {command}\n"
        f"Output     : {len(output_lines)} lines / {output_bytes} bytes\n"
        f"Saved to   : {diag_path}\n"
        f"Audit hash : {audit_hash}"
        f"{warning_note}\n\n"
        f"─── OUTPUT ───\n{result['output_preview']}\n─────────────\n\n"
        f"Now analyze this output. Explain:\n"
        f"1. What it says (literal interpretation)\n"
        f"2. What it means (in context of the question)\n"
        f"3. Any warnings or errors found\n"
        f"4. Whether a next diagnostic step is needed\n"
        f"If a next step is needed, call propose_command with the next safe diagnostic command."
    )

    return result

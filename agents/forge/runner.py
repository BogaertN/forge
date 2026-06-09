"""
Forge runner.py
Level 1.0 — Read-Only Command Runner.

run_safe_command() executes ONLY commands from a hard-coded allowlist.
Each command is a fixed argv list stored in EXEC_ALLOWLIST.
No shell=True. No string interpolation. No user input reaches subprocess argv.

SECURITY ARCHITECTURE:
  - The allowlist maps command_name → fixed argv list
  - User input determines WHICH command to run (by name lookup)
  - User input NEVER reaches argv
  - subprocess is called with shell=False always
  - Output is captured, size-limited, hashed, and returned
  - Every execution is written to the audit log before returning
  - Timeout enforced on every call

To add a command to the allowlist:
  1. Add an entry to EXEC_ALLOWLIST below
  2. Update the tool schema enum in tools.py
  3. Update the system prompt command list in context_builder.py
  These are the only three places that need to change.
"""

import hashlib
import datetime
import subprocess
from pathlib import Path

from . import memory as _mem

FORGE_ROOT = Path(__file__).resolve().parents[2]

COMMAND_TIMEOUT_SECONDS = 30
MAX_OUTPUT_BYTES        = 51_200   # 50 KB cap on captured output

# ─── ALLOWLIST ────────────────────────────────────────────────────────────────
# This is the COMPLETE set of commands Level 1.0 can execute.
# argv lists are fixed at definition time — no runtime construction.
# Adding a command here does not automatically expose it to the LLM;
# the tool schema enum in tools.py must also be updated.

EXEC_ALLOWLIST: dict[str, dict] = {
    "nvidia-smi": {
        "argv":        ["nvidia-smi"],
        "description": "Show NVIDIA GPU status, driver version, and VRAM usage.",
        "risk":        "LOW",
    },
    "ollama ps": {
        "argv":        ["ollama", "ps"],
        "description": "Show currently running Ollama models and their memory usage.",
        "risk":        "LOW",
    },
    "ollama version": {
        "argv":        ["ollama", "--version"],
        "description": "Show the installed Ollama version string.",
        "risk":        "LOW",
    },
    "free -h": {
        "argv":        ["free", "-h"],
        "description": "Show total, used, and free RAM and swap in human-readable units.",
        "risk":        "LOW",
    },
    "df -h": {
        "argv":        ["df", "-h"],
        "description": "Show disk usage for all mounted filesystems.",
        "risk":        "LOW",
    },
    "lscpu": {
        "argv":        ["lscpu"],
        "description": "Show CPU architecture, core count, and frequency information.",
        "risk":        "LOW",
    },
    "lsblk": {
        "argv":        ["lsblk"],
        "description": "Show block devices (disks, partitions, mount points).",
        "risk":        "LOW",
    },
}

COMMAND_NAMES = sorted(EXEC_ALLOWLIST.keys())


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _resolve_command_name(name: str) -> str | None:
    """
    Return the canonical command name if it exists in the allowlist.
    Tries exact match first, then case-insensitive match.
    Returns None if not found.
    """
    name = name.strip()
    if name in EXEC_ALLOWLIST:
        return name
    lower = name.lower()
    for canonical in EXEC_ALLOWLIST:
        if canonical.lower() == lower:
            return canonical
    return None


def _hash_output(output: str) -> str:
    return hashlib.sha256(output.encode("utf-8")).hexdigest()[:16]


def _save_to_diagnostics(
    session_id: str,
    command_name: str,
    argv: list[str],
    output: str,
    exit_code: int,
    duration_ms: int,
    output_sha256: str,
) -> Path:
    """
    Save command output to ~/forge/diagnostics/ for the session record.
    Returns the path of the created file.
    """
    from pathlib import Path as _Path
    import re as _re

    diag_dir = FORGE_ROOT / "diagnostics"
    diag_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = _re.sub(r"[^\w]", "_", command_name)[:30].rstrip("_")
    filename = f"{timestamp_str}_RUN_{slug}.txt"
    diag_path = diag_dir / filename

    doc = f"""FORGE EXECUTED COMMAND RECORD
{'═' * 66}
Command name    : {command_name}
argv            : {argv}
Timestamp       : {datetime.datetime.now().isoformat(timespec='seconds')}
Session ID      : {session_id}
Forge Level     : 1.0 — Read-Only Command Runner
Exit code       : {exit_code} ({'OK' if exit_code == 0 else 'ERROR'})
Duration        : {duration_ms}ms
Output lines    : {output.count(chr(10)) + 1}
Output SHA-256  : {output_sha256}
{'═' * 66}

COMMAND OUTPUT (captured verbatim)
───────────────────────────────────
{output}

{'═' * 66}
NOTE: This command was executed by Forge Level 1.0 from the hard-coded allowlist.
      No shell, no pipes, no redirects, no user input reached argv.
{'═' * 66}
"""
    diag_path.write_text(doc, encoding="utf-8")
    return diag_path


# ─── MAIN ENTRY POINT ─────────────────────────────────────────────────────────

def run_safe_command(session_id: str, command_name: str) -> dict:
    """
    Execute a command from EXEC_ALLOWLIST.

    Returns a result dict:
      ok           — True if exit code 0
      command_name — the canonical command name
      argv         — the exact argv list that was executed
      exit_code    — subprocess return code
      output       — captured stdout (+ stderr on error)
      output_sha256 — sha256[:16] of captured output
      line_count   — number of lines in output
      duration_ms  — wall-clock milliseconds
      diag_path    — path of saved diagnostic file
      message      — formatted string for LLM analysis

    NEVER executes outside EXEC_ALLOWLIST.
    NEVER uses shell=True.
    NEVER allows user input into argv.
    """
    # ── Validate command name ─────────────────────────────────────────────────
    canonical = _resolve_command_name(command_name)
    if canonical is None:
        return {
            "ok": False,
            "error": (
                f"'{command_name}' is not in the Level 1.0 execution allowlist.\n"
                f"Allowed commands: {', '.join(COMMAND_NAMES)}"
            )
        }

    entry = EXEC_ALLOWLIST[canonical]
    argv  = entry["argv"]   # fixed list — never modified

    # ── Execute ───────────────────────────────────────────────────────────────
    start = datetime.datetime.now()

    try:
        proc = subprocess.run(
            argv,                          # fixed argv — no shell string
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
            shell=False,                   # ALWAYS False — never shell
        )
        duration_ms = int((datetime.datetime.now() - start).total_seconds() * 1000)

    except subprocess.TimeoutExpired:
        duration_ms = COMMAND_TIMEOUT_SECONDS * 1000
        _mem.write_audit_entry(
            session_id=session_id,
            tool="COMMAND_TIMEOUT",
            path=canonical,
            lines="-",
            reason=f"command={canonical} | timeout={COMMAND_TIMEOUT_SECONDS}s"
        )
        return {
            "ok": False,
            "error": f"Command timed out after {COMMAND_TIMEOUT_SECONDS}s: {canonical}"
        }

    except FileNotFoundError:
        _mem.write_audit_entry(
            session_id=session_id,
            tool="COMMAND_NOT_FOUND",
            path=canonical,
            lines="-",
            reason=f"command={canonical} | argv[0]={argv[0]} not found on PATH"
        )
        return {
            "ok": False,
            "error": (
                f"'{argv[0]}' was not found on PATH. "
                f"It may not be installed. "
                f"Try: propose {canonical}"
            )
        }

    # ── Collect output ────────────────────────────────────────────────────────
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    # Combine: always include stdout; include stderr only on non-zero exit
    if proc.returncode != 0 and stderr.strip():
        combined = stdout + "\n--- stderr ---\n" + stderr
    else:
        combined = stdout

    # Size limit
    output_bytes = len(combined.encode("utf-8"))
    if output_bytes > MAX_OUTPUT_BYTES:
        combined = combined[:MAX_OUTPUT_BYTES] + (
            f"\n... [output truncated at {MAX_OUTPUT_BYTES:,} bytes]"
        )

    output_sha256 = _hash_output(combined)
    line_count    = combined.count("\n") + 1

    # ── Audit: COMMAND_EXECUTED ───────────────────────────────────────────────
    _mem.write_audit_entry(
        session_id=session_id,
        tool="COMMAND_EXECUTED",
        path=canonical,
        lines=f"{line_count} lines",
        reason=(
            f"argv={argv} | "
            f"exit_code={proc.returncode} | "
            f"output_sha256={output_sha256} | "
            f"duration_ms={duration_ms}"
        )
    )

    # ── Save to diagnostics ───────────────────────────────────────────────────
    diag_path = _save_to_diagnostics(
        session_id=session_id,
        command_name=canonical,
        argv=argv,
        output=combined,
        exit_code=proc.returncode,
        duration_ms=duration_ms,
        output_sha256=output_sha256,
    )

    _mem.write_audit_entry(
        session_id=session_id,
        tool="DIAGNOSTIC_SESSION_SAVED",
        path=str(diag_path),
        lines="-",
        reason=f"auto-saved by run_safe_command | command={canonical}"
    )

    ok = proc.returncode == 0
    status_str = "OK" if ok else f"ERROR (exit {proc.returncode})"

    return {
        "ok":           ok,
        "command_name": canonical,
        "argv":         argv,
        "exit_code":    proc.returncode,
        "output":       combined,
        "output_sha256": output_sha256,
        "line_count":   line_count,
        "duration_ms":  duration_ms,
        "diag_path":    str(diag_path),
        "message": (
            f"Command executed: {canonical}  [{status_str}]\n"
            f"Duration  : {duration_ms}ms\n"
            f"Lines     : {line_count}\n"
            f"SHA-256   : {output_sha256}\n"
            f"Saved to  : {diag_path}\n\n"
            f"─── OUTPUT ─────────────────────────────────────────\n"
            f"{combined}\n"
            f"────────────────────────────────────────────────────\n\n"
            f"Analyze this output. Explain what it means in plain language "
            f"and whether a next diagnostic step is needed."
        )
    }

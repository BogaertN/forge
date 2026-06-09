"""
Forge proposals.py
Level 0.6 — Diagnostic Proposal Mode.

propose_command() validates a command against strict rules, formats a proposal
document, saves it to ~/forge/proposals/, and writes to the audit log.

CRITICAL IMPLEMENTATION CONTRACT:
  This module NEVER executes any command.
  No subprocess. No os.system. No os.popen. No eval. No exec.
  No shell=True anywhere in this file.
  Validate, format, save, audit only.
"""

import os
import re
import datetime
from pathlib import Path
from typing import Optional

from . import memory as _mem
from .permissions import get_approved_paths, is_path_blocked

FORGE_ROOT     = Path(__file__).resolve().parents[2]
PROPOSALS_DIR  = FORGE_ROOT / "proposals"

# ─── RISK LEVELS ─────────────────────────────────────────────────────────────

RISK_LOW    = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH   = "HIGH"

VALID_RISK_LEVELS = {RISK_LOW, RISK_MEDIUM, RISK_HIGH}

# ─── COMPOSITION OPERATORS — always blocked at Level 0.6 ─────────────────────
# No chaining. No pipes. No redirects. One command at a time.

BLOCKED_OPERATORS = [
    "&&", "||", ";;",
    " | ",   # pipe (space-padded to avoid false positives in args)
    "; ",    # semicolon separator
    " ;",
    "$(", "`",
    " > ", ">",   # overwrite redirect
    " >> ", ">>",  # append redirect
    " < ",   # input redirect
    "2>", "2 >",  # stderr redirect
    "&>",    # combined redirect
]

# ─── BLOCKED COMMAND NAMES — refuse to propose these at all ──────────────────

BLOCKED_FIRST_TOKENS = {
    "rm", "rmdir", "sudo", "su", "doas",
    "chmod", "chown", "chgrp",
    "mv", "cp",       # blocked outright — Level 0.6 is read-only
    "dd", "mkfs", "fdisk", "parted", "mount", "umount",
    "wipefs", "shred", "truncate",
    "kill", "killall", "pkill", "pkexec",
    "reboot", "shutdown", "poweroff", "halt", "init",
    "tee",            # writes files
    "perl",           # can write/exec
    "awk",            # can write/exec via system()
    "python", "python3",   # blocked as standalone — only --version allowed
    "node", "ruby", "bash", "sh", "zsh", "fish",  # shell execution
    "exec", "eval",
    "at", "cron", "crontab",
    "passwd", "useradd", "userdel", "usermod", "groupadd",
    "visudo", "vipw",
    "nc", "netcat", "ncat",
    "curl", "wget",   # can download+execute
    "ssh", "scp", "sftp", "rsync",
    # docker: destructive subcommands are in BLOCKED_SUBCOMMAND_PATTERNS
    # docker ps / docker info / docker version are allowed via ALLOWED_PATTERNS
    "kubectl", "helm",
    "ansible", "terraform",
    "make",           # can execute arbitrary recipes
    "xargs",          # can compose into destructive commands
}

# ─── BLOCKED SUBCOMMAND PATTERNS — refuse specific subcommands ───────────────
# Applied after the base command passes the first-token check.

BLOCKED_SUBCOMMAND_PATTERNS = [
    # git destructive operations
    (r"^git\s+reset", "git reset can rewrite history"),
    (r"^git\s+clean", "git clean deletes untracked files"),
    (r"^git\s+checkout\s+\.", "git checkout . discards local changes"),
    (r"^git\s+restore\s+\.", "git restore . discards local changes"),
    (r"^git\s+stash\s+drop", "git stash drop deletes stash entries"),
    (r"^git\s+branch\s+.*-[dD]", "git branch -D force-deletes branches"),

    # find with execution or deletion
    (r"find\s+.*-delete", "find -delete removes files"),
    (r"find\s+.*-exec\s+rm", "find -exec rm removes files"),
    (r"find\s+.*-exec\s+sh", "find -exec sh executes arbitrary commands"),
    (r"find\s+.*-exec\s+bash", "find -exec bash executes arbitrary commands"),
    (r"find\s+.*-exec\s+python", "find -exec python executes arbitrary code"),

    # sed with in-place edit
    (r"^sed\s+.*-i", "sed -i modifies files in place"),
    (r"^sed\s+.*--in-place", "sed --in-place modifies files in place"),

    # systemctl destructive operations
    (r"^systemctl\s+stop\b", "systemctl stop stops services"),
    (r"^systemctl\s+disable\b", "systemctl disable disables services"),
    (r"^systemctl\s+restart\b", "systemctl restart restarts services"),
    (r"^systemctl\s+mask\b", "systemctl mask disables services permanently"),

    # pip/npm install
    (r"^pip3?\s+install\b", "pip install modifies packages"),
    (r"^npm\s+install\b", "npm install modifies packages"),
    (r"^pip3?\s+uninstall\b", "pip uninstall modifies packages"),

    # docker destructive
    (r"^docker\s+(rm|rmi|system|volume|network)", "docker destructive operation"),
]

# ─── SENSITIVE PATH PATTERNS — block if found anywhere in the command ─────────

SENSITIVE_PATH_PATTERNS = [
    r"\.ssh", r"\.gnupg", r"\.git-credentials", r"\.npmrc",
    r"identity-vault",
    r"\btoken\b", r"\btokens\b", r"\bsecret\b", r"\bsecrets\b",
    r"\bcredential\b", r"\bcredentials\b",
    r"private.?key", r"private_key",
    r"\.env\b",
    r"shadow", r"/etc/passwd",
]

# ─── ALLOWED COMMAND PATTERNS (whitelist) ────────────────────────────────────
# Command must match at least one of these patterns to be proposed.
# This is the positive gate — even if a command passes all blocklists,
# it must also match something here.

ALLOWED_PATTERNS = [
    # Navigation
    r"^pwd$",
    r"^ls(\s+(-[lahRt1]+|\S+|\./\S+|~/\S+|/\S+))*$",
    r"^tree(\s+(-L\s+\d+|-a|-d|-f))*(\s+\S+)?$",

    # File reading (not writing)
    r"^cat\s+\S+$",
    r"^head(\s+-n\s+\d+)?\s+\S+$",
    r"^tail(\s+-n\s+\d+)?\s+\S+$",
    r"^sed\s+-n\s+'[^']+'\s+\S+$",    # sed read-only (no -i)
    r"^wc(\s+-[lLwc]+)?\s+\S+$",

    # Search
    r"^grep(\s+-[rRniIlLEFPc]+)*\s+\S+.*",
    r"^find\s+\S+(\s+-maxdepth\s+\d+)?(\s+-type\s+[fdl])?(\s+-name\s+\S+)?(\s+-not\s+-path\s+\S+)*\s*$",

    # Python version only
    r"^python3?\s+--version$",
    r"^pip3?\s+--version$",
    r"^pip3?\s+list$",
    r"^pip3?\s+show\s+\S+$",

    # Git read-only
    r"^git\s+(status|log|diff|show|branch|remote|tag|stash\s+list|shortlog)(\s+.*)?$",

    # Ollama read-only (expanded: version, running, inspect)
    r"^ollama\s+(ps|list|show|version|--version|run\s+--help)(\s+\S+)?$",

    # System diagnostics
    r"^nvidia-smi(\s+\S+)*$",
    r"^df(\s+-[hHBkmT]+)?(\s+\S+)?$",
    r"^free(\s+-[hmgbtks]+)?$",
    r"^du(\s+-[shHk]+)+(\s+\S+)?$",
    r"^uname(\s+-[asnrvmpio]+)?$",
    r"^whoami$",
    r"^id(\s+\S+)?$",
    r"^which\s+\S+$",
    r"^type\s+\S+$",
    r"^env$",
    r"^printenv(\s+\S+)?$",
    r"^ps(\s+(aux|axf|aux\s+--sort=\S+))?$",

    # Hardware info (read-only)
    r"^lscpu$",
    r"^lsblk(\s+-[a-zA-Z]+)*(\s+\S+)?$",
    r"^lspci(\s+-[a-zA-Z]+)*$",
    r"^lsusb(\s+-[a-zA-Z]+)*$",
    r"^lsmod$",
    r"^dmidecode(\s+-t\s+\S+)?$",

    # Network info (read-only, no connections)
    r"^ip\s+(addr|link|route|neigh)(\s+show)?(\s+\S+)?$",
    r"^ifconfig(\s+\S+)?$",
    r"^hostname(\s+-[a-zA-Z])?$",

    # Service status (read-only)
    r"^systemctl\s+status\s+\S+(\s+--no-pager)?$",
    r"^systemctl\s+is-(active|enabled|failed)\s+\S+$",

    # Journal log reading (read-only, service-scoped, no redirect)
    r"^journalctl\s+-u\s+\S+(\s+--since\s+['\"][^'\"]+['\"])?(\s+--no-pager)?(\s+-n\s+\d+)?(\s+--lines=\d+)?$",
    r"^journalctl\s+-u\s+\S+(\s+-n\s+\d+)?(\s+--no-pager)?$",

    # Package info (read-only)
    r"^dpkg\s+-l(\s+\S+)?$",
    r"^dpkg\s+--list(\s+\S+)?$",
    r"^apt\s+list(\s+--installed)?(\s+--upgradable)?$",
    r"^apt-cache\s+(show|policy)\s+\S+$",
    r"^snap\s+list$",

    # Package/version checks
    r"^node\s+--version$",
    r"^npm\s+--version$",
    r"^git\s+--version$",
    r"^ollama\s+--version$",
    r"^docker\s+--version$",
    r"^docker\s+(ps|images|info|version)(\s+-[a-zA-Z]+)*$",
    r"^nvcc\s+--version$",
    r"^cuda\s+--version$",
]


# ─── VALIDATION ───────────────────────────────────────────────────────────────

class ValidationResult:
    def __init__(self, allowed: bool, reason: str, risk: str = RISK_LOW):
        self.allowed = allowed
        self.reason  = reason
        self.risk    = risk


def validate_command(command: str) -> ValidationResult:
    """
    Validate a proposed command against all Level 0.6 rules.
    Returns a ValidationResult with allowed=True/False and the reason.

    This function NEVER executes anything. Pure string analysis only.
    """
    command = command.strip()

    if not command:
        return ValidationResult(False, "Empty command.")

    if len(command) > 500:
        return ValidationResult(False, "Command too long (max 500 characters).")

    # 1. Block composition operators — no chaining at Level 0.6
    for op in BLOCKED_OPERATORS:
        # Check for the operator, but be careful about args that contain these chars
        # Use a cleaned version for checking (strip quoted strings first)
        cmd_for_op_check = re.sub(r"'[^']*'", "''", command)  # remove single-quoted args
        cmd_for_op_check = re.sub(r'"[^"]*"', '""', cmd_for_op_check)
        if op in cmd_for_op_check:
            return ValidationResult(
                False,
                f"Command composition not allowed at Level 0.6: '{op.strip()}' detected. "
                f"One diagnostic command at a time only."
            )

    # 2. Block first token
    first_token = command.strip().split()[0].lower()
    # Strip leading path (e.g. /usr/bin/rm -> rm)
    first_token_base = os.path.basename(first_token)

    if first_token_base in BLOCKED_FIRST_TOKENS:
        # Allow specific safe subforms
        if first_token_base in ("python", "python3") and "--version" in command:
            pass  # python --version is OK, will be caught by allowlist
        elif first_token_base in ("python", "python3"):
            return ValidationResult(
                False,
                f"'{first_token_base}' cannot be proposed at Level 0.6 except for --version check. "
                f"Level 0.6 is diagnostic only."
            )
        else:
            return ValidationResult(
                False,
                f"'{first_token_base}' is blocked at Level 0.6. "
                f"Only safe diagnostic commands may be proposed."
            )

    # 3. Block specific subcommand patterns
    for pattern, reason in BLOCKED_SUBCOMMAND_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return ValidationResult(False, f"Blocked: {reason}.")

    # 4. Block sensitive path patterns
    for pattern in SENSITIVE_PATH_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return ValidationResult(
                False,
                f"Command references a sensitive path or term. "
                f"Forge cannot propose commands touching credentials or private data."
            )

    # 5. Whitelist check — command must match at least one allowed pattern
    matched_pattern = False
    for pattern in ALLOWED_PATTERNS:
        if re.match(pattern, command.strip(), re.IGNORECASE):
            matched_pattern = True
            break

    if not matched_pattern:
        return ValidationResult(
            False,
            f"Command does not match any Level 0.6 allowed diagnostic pattern. "
            f"Allowed examples: pwd, ls, git status, grep, find -maxdepth, "
            f"cat <file>, df -h, free -h, nvidia-smi, systemctl status <service>."
        )

    # 6. Assess risk level
    risk = _assess_risk(command)

    return ValidationResult(True, "Command passed all Level 0.6 validation checks.", risk)


def _assess_risk(command: str) -> str:
    """
    Assign a risk level to a validated command.
    LOW: reads a single file or shows version/status.
    MEDIUM: walks a directory tree or reads many files.
    HIGH: anything involving system state that could be surprising.
    """
    cmd_lower = command.lower()

    # Anything touching system state
    if any(t in cmd_lower for t in ["systemctl", "ps ", "ps\n", "uname", "nvidia-smi"]):
        return RISK_MEDIUM

    # Directory walks
    if any(t in cmd_lower for t in ["find ", "grep -r", "grep -R", "tree ", "du "]):
        return RISK_MEDIUM

    return RISK_LOW


# ─── PROPOSAL FORMATTING ──────────────────────────────────────────────────────

def _make_slug(command: str) -> str:
    """Generate a short filename-safe slug from a command."""
    slug = re.sub(r"[^\w\s-]", "", command)
    slug = re.sub(r"\s+", "_", slug.strip())
    return slug[:40].rstrip("_")


def _suggest_safe_alternative(command: str) -> str:
    """
    Given a refused command, suggest the safest read-only inspection equivalent.
    Returns a suggestion string, or empty string if no reasonable alternative exists.
    """
    cmd = command.strip()

    # find -delete → find without -delete
    if re.search(r"find\s+.*-delete", cmd):
        safe = re.sub(r"\s+-delete\b", "", cmd).strip()
        return safe

    # find -exec rm ... → find without -exec
    if re.search(r"find\s+.*-exec\s+rm", cmd):
        safe = re.sub(r"\s+-exec\s+rm.*", "", cmd).strip()
        return safe

    # find -exec sh/bash → find without -exec
    if re.search(r"find\s+.*-exec\s+(sh|bash|python)", cmd):
        safe = re.sub(r"\s+-exec\s+.*", "", cmd).strip()
        return safe

    # rm / rmdir → suggest find to see what would be removed
    if re.match(r"^(rm|rmdir)\b", cmd):
        # Extract any path or pattern from the rm command
        parts = cmd.split()
        path_parts = [p for p in parts[1:] if not p.startswith("-")]
        if path_parts:
            target = path_parts[0]
            if "*" in target:
                # e.g. rm *.pyc → find . -name "*.pyc"
                name = os.path.basename(target)
                return f'find . -name "{name}"'
            else:
                return f"ls -lah {target}"
        return ""

    # sed -i → sed -n (read-only)
    if re.search(r"sed\s+.*-i\b", cmd):
        safe = re.sub(r"-i\b", "-n", cmd)
        safe = safe + "p"  # add print action for read-only
        return safe

    # pip install → pip show or pip list
    if re.match(r"pip3?\s+install\b", cmd):
        parts = cmd.split()
        if len(parts) > 2:
            pkg = parts[2]
            return f"pip show {pkg}"
        return "pip list"

    return ""


def _format_proposal(
    session_id: str,
    user_question: str,
    command: str,
    purpose: str,
    safety_rationale: str,
    risk_level: str,
    expected_output: str,
    what_could_go_wrong: str,
    validation: ValidationResult,
    proposal_path: Path,
    audit_hash: str,
) -> str:
    """
    Format the complete proposal document.
    Approved and refused proposals use different section labels and footers.
    Refused proposals NEVER instruct Nic to copy/paste the refused command.
    """
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    approved = get_approved_paths()

    paths_in_command = [p for p in approved if p in command]
    paths_str = "\n  ".join(paths_in_command) if paths_in_command else "(no approved paths explicitly referenced)"

    is_refused = not validation.allowed

    safety_section_label = "WHY IT IS REFUSED" if is_refused else "WHY IT IS SAFE"

    if validation.allowed:
        validation_line = "PASS — no blocked patterns detected"
    else:
        validation_line = f"REFUSED — {validation.reason}"

    if is_refused:
        safe_alt = _suggest_safe_alternative(command)
        safe_alt_line = (
            f"Safe diagnostic alternative:\n\n  {safe_alt}"
            if safe_alt
            else "Consult Forge for a safe inspection alternative."
        )
        manual_section = f"""\
THIS COMMAND WAS REFUSED BY FORGE LEVEL 0.6 SAFETY RULES.
DO NOT RUN THIS COMMAND.

{safe_alt_line}

Forge refused this proposal to protect your system.
The refusal has been logged to the audit trail."""
    else:
        manual_section = f"""\
Forge cannot execute commands. This is by design.

If you choose to run this command, copy and paste it yourself:

  {command}

Forge will never execute commands on your behalf at any trust level
unless you explicitly enable execution mode in a future version."""

    return f"""FORGE DIAGNOSTIC PROPOSAL
{'═' * 66}
Title           : {purpose[:80]}
Status          : {'REFUSED' if is_refused else 'APPROVED FOR REVIEW'}
Timestamp       : {timestamp}
Session ID      : {session_id}
Forge Level     : 0.6 — Diagnostic Proposal Mode
Proposal File   : {proposal_path}
{'═' * 66}

USER QUESTION
─────────────
{user_question}


PROPOSED COMMAND
────────────────
  {command}


PURPOSE
───────
{purpose}


{safety_section_label}
{'─' * len(safety_section_label)}
{safety_rationale if safety_rationale else validation.reason}


RISK LEVEL
──────────
{risk_level}


VALIDATION CHECK
────────────────
{validation_line}

Blocked operators checked : &&  ;  |  $()  >  >>  ` (checked)
Sensitive paths checked   : .ssh  .gnupg  credentials  secrets  (checked)
Composition check         : single command only, no chaining


APPROVED PATHS INVOLVED
───────────────────────
  {paths_str}


EXPECTED OUTPUT
───────────────
{expected_output if expected_output else '(not applicable — command was refused)'}


WHAT COULD GO WRONG
───────────────────
{what_could_go_wrong if what_could_go_wrong else '(not applicable — command was refused before proposal was completed)'}


{'═' * 66}
MANUAL INSTRUCTION
──────────────────
{manual_section}
{'═' * 66}
Audit entry hash : {audit_hash}
"""


# ─── DUPLICATE DETECTION ─────────────────────────────────────────────────────

def _find_existing_proposal(session_id: str, command: str) -> Path | None:
    """
    Check whether an approved proposal for this exact command already exists
    in ~/forge/proposals/ from the current Forge session.

    Returns the Path if found, None if not.
    Only checks PROPOSAL_ files (not REFUSED_) from this session.
    Only matches approved proposals for the identical command string.
    """
    if not PROPOSALS_DIR.exists():
        return None

    slug = _make_slug(command)
    # Proposals from this session contain the session_id in their content
    for proposal_file in sorted(PROPOSALS_DIR.glob(f"*_PROPOSAL_{slug}*.txt"), reverse=True):
        try:
            content = proposal_file.read_text(encoding="utf-8")
            if f"Session ID      : {session_id}" in content:
                return proposal_file
        except OSError:
            continue
    return None


# ─── MAIN ENTRY POINT ────────────────────────────────────────────────────────

def propose_command(
    session_id: str,
    user_question: str,
    command: str,
    purpose: str,
    safety_rationale: str,
    risk_level: str,
    expected_output: str,
    what_could_go_wrong: str,
) -> dict:
    """
    Validate, format, save, and audit a proposed command.
    Returns a result dict with ok, message, proposal_path, and audit_hash.

    NEVER executes the command. NEVER calls subprocess. NEVER calls os.system.
    """
    # Normalize risk level
    risk_level = risk_level.upper().strip()
    if risk_level not in VALID_RISK_LEVELS:
        risk_level = RISK_MEDIUM

    # Validate
    validation = validate_command(command)

    # ── Duplicate detection ───────────────────────────────────────────────────
    # If this command was already proposed in the current Forge session,
    # return the existing proposal instead of creating a duplicate.
    if validation.allowed:
        existing = _find_existing_proposal(session_id, command)
        if existing:
            return {
                "ok": True,
                "allowed": True,
                "duplicate": True,
                "risk_level": risk_level,
                "proposal_path": str(existing),
                "audit_hash": "duplicate",
                "message": (
                    f"DIAGNOSTIC PROPOSAL (already exists this session)\n\n"
                    f"Command    : {command}\n"
                    f"This command was already proposed this session.\n"
                    f"Existing proposal: {existing}\n\n"
                    f"{'─' * 50}\n"
                    f"MANUAL INSTRUCTION:\n"
                    f"Copy and paste the command yourself if you approve:\n\n"
                    f"  {command}\n\n"
                    f"{'─' * 50}\n"
                    f"(No new file created — reusing existing proposal.)"
                ),
            }

    # Build proposal path (even for refused proposals — we log refusals)
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = _make_slug(command)
    status_prefix = "PROPOSAL" if validation.allowed else "REFUSED"
    proposal_filename = f"{timestamp_str}_{status_prefix}_{slug}.txt"
    proposal_path = PROPOSALS_DIR / proposal_filename

    # Write audit entry first to get hash
    audit_tool = "PROPOSE_COMMAND" if validation.allowed else "PROPOSE_COMMAND_REFUSED"
    audit_hash = _mem.write_audit_entry(
        session_id=session_id,
        tool=audit_tool,
        path=str(proposal_path),
        lines="-",
        reason=(
            f"command={command[:80]} | "
            f"risk={risk_level} | "
            f"allowed={validation.allowed} | "
            f"validation={validation.reason[:80]}"
        )
    )

    # Format the proposal document
    doc = _format_proposal(
        session_id=session_id,
        user_question=user_question,
        command=command,
        purpose=purpose,
        safety_rationale=safety_rationale,
        risk_level=risk_level,
        expected_output=expected_output,
        what_could_go_wrong=what_could_go_wrong,
        validation=validation,
        proposal_path=proposal_path,
        audit_hash=audit_hash,
    )

    # Save to proposals directory
    try:
        with open(proposal_path, "w", encoding="utf-8") as f:
            f.write(doc)
    except OSError as e:
        return {
            "ok": False,
            "error": f"Could not save proposal file: {e}",
            "allowed": validation.allowed,
        }

    if not validation.allowed:
        safe_alt = _suggest_safe_alternative(command)
        safe_alt_msg = f"\n\nSafe diagnostic alternative: {safe_alt}" if safe_alt else ""
        return {
            "ok": False,
            "allowed": False,
            "reason": validation.reason,
            "proposal_path": str(proposal_path),
            "audit_hash": audit_hash,
            "message": (
                f"PROPOSAL REFUSED\n\n"
                f"Command: {command}\n\n"
                f"Reason: {validation.reason}\n\n"
                f"Level 0.6 allows diagnostic read-only commands only. "
                f"Deletion, modification, and execution commands cannot be proposed at this level."
                f"{safe_alt_msg}\n\n"
                f"Refusal logged to: {proposal_path}"
            ),
        }

    return {
        "ok": True,
        "allowed": True,
        "risk_level": risk_level,
        "proposal_path": str(proposal_path),
        "audit_hash": audit_hash,
        "message": (
            f"DIAGNOSTIC PROPOSAL\n\n"
            f"Command     : {command}\n"
            f"Purpose     : {purpose}\n"
            f"Risk level  : {risk_level}\n"
            f"Safety      : {safety_rationale}\n\n"
            f"Expected output:\n{expected_output}\n\n"
            f"What could go wrong:\n{what_could_go_wrong}\n\n"
            f"{'─' * 50}\n"
            f"MANUAL INSTRUCTION:\n"
            f"Forge cannot run this. Copy and paste it yourself if you approve:\n\n"
            f"  {command}\n\n"
            f"{'─' * 50}\n"
            f"Full proposal saved to: {proposal_path}\n"
            f"Audit hash: {audit_hash}"
        ),
    }

"""
Forge ledger.py
Level 4.3 — Patch Lifecycle Ledger.

Scans Forge-owned patch directories, parses artifacts, groups by target file,
and shows lifecycle chains: proposal → diff → plan → apply → rollback → safety.

SECURITY CONSTRAINTS:
  - Only reads from Forge-owned patch directories and approved target files
  - Paths outside allowed directories are refused before reading
  - No subprocess. No shell. No project file writes.
"""

import os
import re
import hashlib
import datetime
from pathlib import Path
from typing import Optional

FORGE_ROOT  = Path(__file__).resolve().parents[2]

PROPOSALS_DIR  = FORGE_ROOT / "proposed_patches"
DIFFS_DIR      = FORGE_ROOT / "proposed_patches" / "diffs"
PLANS_DIR      = FORGE_ROOT / "apply_plans"
ROLLBACK_DIR   = FORGE_ROOT / "rollback_registry"
SAFETY_DIR     = FORGE_ROOT / "rollback_registry" / "restore_safety_snapshots"

# All directories the ledger is allowed to read from
ALLOWED_LEDGER_DIRS = [
    PROPOSALS_DIR,
    DIFFS_DIR,
    PLANS_DIR,
    ROLLBACK_DIR,
    SAFETY_DIR,
]

# Artifact type detection from filename prefix
ARTIFACT_TYPES = {
    "PATCH":    "PROPOSAL",
    "PROPOSAL": "PROPOSAL",
    "REFUSED":  "REFUSED_PROPOSAL",
    "DIFF":     "DIFF",
    "PLAN":     "APPLY_PLAN",
    "ROLLBACK": "ROLLBACK_SNAPSHOT",
    "SAFETY":   "SAFETY_SNAPSHOT",
}


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _extract_timestamp(filename: str) -> str:
    """Extract YYYY-MM-DD_HHMMSS prefix from filename, or '' if not found."""
    m = re.match(r"(\d{4}-\d{2}-\d{2}_\d{6})", filename)
    return m.group(1) if m else ""


def _detect_type(filename: str) -> str:
    """Detect artifact type from filename prefix."""
    name = filename.upper()
    for prefix, atype in ARTIFACT_TYPES.items():
        if f"_{prefix}_" in name or name.startswith(prefix + "_"):
            return atype
    return "UNKNOWN"


def _parse_target_file(content: str) -> str:
    """Extract target file path from artifact content."""
    m = re.search(r"Target file\s+:\s+(.+)", content)
    return m.group(1).strip() if m else ""


def _parse_original_sha(content: str) -> str:
    m = re.search(r"Original SHA-256\s+:\s+([0-9a-f]{16})", content)
    return m.group(1).strip() if m else ""


def _parse_future_sha(content: str) -> str:
    m = re.search(r"Future SHA-256\s+:\s+([0-9a-f]{16})", content)
    return m.group(1).strip() if m else ""


def _parse_rollback_sha(content: str) -> str:
    m = re.search(r"File SHA-256\s+:\s+([0-9a-f]{16})", content)
    return m.group(1).strip() if m else ""


def _parse_rollback_ref(content: str) -> str:
    """Extract rollback snapshot filename reference from apply plan."""
    m = re.search(r"rollback=([^\s|]+\.txt)", content)
    return m.group(1).strip() if m else ""


def _parse_proposal_ref(content: str) -> str:
    """Extract proposal filename reference from apply plan or diff."""
    m = re.search(r"Proposal file\s+:\s+(.+)", content)
    if m:
        return Path(m.group(1).strip()).name
    return ""


def is_in_ledger_dirs(path: Path) -> bool:
    """Return True if path is inside one of the allowed ledger directories."""
    for d in ALLOWED_LEDGER_DIRS:
        try:
            path.relative_to(d)
            return True
        except ValueError:
            continue
    return False


def find_artifact_path(filename: str) -> Optional[Path]:
    """
    Locate an artifact file by filename (without requiring full path).
    Searches all allowed ledger directories.
    """
    name = Path(filename).name  # strip any path prefix
    for d in ALLOWED_LEDGER_DIRS:
        candidate = d / name
        if candidate.exists():
            return candidate
    return None


# ─── ARTIFACT PARSING ─────────────────────────────────────────────────────────

def parse_artifact(path: Path) -> dict:
    """
    Read and parse a single artifact file.
    Returns a dict with all extractable metadata.
    """
    info = {
        "path":           path,
        "filename":       path.name,
        "type":           _detect_type(path.name),
        "timestamp":      _extract_timestamp(path.name),
        "target_file":    "",
        "original_sha":   "",
        "future_sha":     "",
        "rollback_sha":   "",
        "proposal_ref":   "",
        "rollback_ref":   "",
        "readable":       False,
        "error":          "",
    }

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        info["readable"] = True
        info["target_file"]  = _parse_target_file(content)
        info["original_sha"] = _parse_original_sha(content)
        info["future_sha"]   = _parse_future_sha(content)
        info["rollback_sha"] = _parse_rollback_sha(content)
        info["proposal_ref"] = _parse_proposal_ref(content)
        info["rollback_ref"] = _parse_rollback_ref(content)
    except OSError as e:
        info["error"] = str(e)

    return info


# ─── SCANNING ─────────────────────────────────────────────────────────────────

def scan_all_artifacts() -> list[dict]:
    """
    Scan all five Forge-owned patch directories.
    Returns a list of parsed artifact dicts, sorted by timestamp then filename.
    """
    artifacts = []
    for d in ALLOWED_LEDGER_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if p.is_file() and p.suffix == ".txt" and not p.name.startswith("."):
                artifacts.append(parse_artifact(p))

    # Sort: timestamp descending (newest first), then filename
    artifacts.sort(key=lambda a: (a["timestamp"] or "0000-00-00_000000"), reverse=True)
    return artifacts


def group_by_target(artifacts: list[dict]) -> dict[str, list[dict]]:
    """
    Group artifact dicts by target_file.
    Returns a dict mapping target_file → [artifacts], oldest-first.
    """
    groups: dict[str, list[dict]] = {}
    ungrouped = []
    for a in artifacts:
        t = a.get("target_file", "")
        if t:
            groups.setdefault(t, []).append(a)
        else:
            ungrouped.append(a)

    if ungrouped:
        groups["(target unknown)"] = ungrouped

    # Sort each group oldest-first
    for t in groups:
        groups[t].sort(key=lambda a: a["timestamp"] or "0000")

    return groups


# ─── STATE DETERMINATION ──────────────────────────────────────────────────────

def get_current_state(
    target_file: str,
    original_sha: str,
    future_sha: str,
) -> tuple[str, str]:
    """
    Read the target file and determine its current state relative to an apply plan.
    Returns (state_code, current_sha).
    state_code: APPLIED | ORIGINAL | DRIFT | UNREADABLE | MISSING | UNKNOWN
    """
    if not target_file or not os.path.exists(target_file):
        return "MISSING", ""

    try:
        content = Path(target_file).read_text(encoding="utf-8", errors="replace")
        current_sha = _sha256(content)
    except OSError:
        return "UNREADABLE", ""

    if future_sha and current_sha == future_sha:
        return "APPLIED", current_sha
    elif original_sha and current_sha == original_sha:
        return "ORIGINAL", current_sha
    elif original_sha or future_sha:
        return "DRIFT", current_sha
    else:
        return "UNKNOWN", current_sha


# ─── CHAIN DETECTION ─────────────────────────────────────────────────────────

def find_chain(artifact: dict, all_artifacts: list[dict]) -> list[dict]:
    """
    Given a starting artifact, find all related artifacts that form a chain.
    Linking logic:
      1. Same target_file
      2. File name cross-references (proposal_ref, rollback_ref)
      3. Same timestamp prefix (same second → same preflight run)
    Returns the chain sorted oldest-first.
    """
    chain_paths = {artifact["path"]}
    target = artifact.get("target_file", "")
    ts     = artifact.get("timestamp", "")
    fname  = artifact["filename"]

    for a in all_artifacts:
        if a["path"] in chain_paths:
            continue

        # Same target file
        if target and a.get("target_file") == target:
            # Only include if timestamps are close or files reference each other
            a_ts = a.get("timestamp", "")
            # Include if same-second timestamp (proposal + plan created together)
            if ts and a_ts and ts == a_ts:
                chain_paths.add(a["path"])
                continue
            # Include if this file references the artifact by name
            for ref_field in ("proposal_ref", "rollback_ref"):
                ref = a.get(ref_field, "")
                if ref and (ref in fname or fname in ref):
                    chain_paths.add(a["path"])
                    break
            # Include if the artifact references this file by name
            for ref_field in ("proposal_ref", "rollback_ref"):
                ref = artifact.get(ref_field, "")
                if ref and (ref in a["filename"] or a["filename"] in ref):
                    chain_paths.add(a["path"])
                    break

    result = [a for a in all_artifacts if a["path"] in chain_paths]
    result.sort(key=lambda a: (a["timestamp"] or "0000", a["filename"]))
    return result


# ─── DISPLAY FORMATTERS ───────────────────────────────────────────────────────

TYPE_LABELS = {
    "PROPOSAL":          "PROPOSAL ",
    "REFUSED_PROPOSAL":  "REFUSED  ",
    "DIFF":              "DIFF     ",
    "APPLY_PLAN":        "PLAN     ",
    "ROLLBACK_SNAPSHOT": "ROLLBACK ",
    "SAFETY_SNAPSHOT":   "SAFETY   ",
    "UNKNOWN":           "UNKNOWN  ",
}

TYPE_ORDER = {
    "PROPOSAL": 0,
    "REFUSED_PROPOSAL": 1,
    "DIFF": 2,
    "APPLY_PLAN": 3,
    "ROLLBACK_SNAPSHOT": 4,
    "SAFETY_SNAPSHOT": 5,
    "UNKNOWN": 9,
}


def format_artifact_line(a: dict, current_sha: str = "") -> str:
    """Format a single artifact as a one-line summary."""
    label = TYPE_LABELS.get(a["type"], "UNKNOWN  ")
    ts    = a["timestamp"] or "unknown-time"

    sha_note = ""
    if a["type"] == "APPLY_PLAN":
        orig = a.get("original_sha", "")
        fut  = a.get("future_sha", "")
        if orig and fut:
            sha_note = f"  [{orig}→{fut}]"
    elif a["type"] in ("ROLLBACK_SNAPSHOT", "SAFETY_SNAPSHOT"):
        rsha = a.get("rollback_sha", "")
        if rsha:
            sha_note = f"  [sha:{rsha}]"

    # State indicator for apply plans
    state_marker = ""
    if a["type"] == "APPLY_PLAN" and current_sha:
        if current_sha == a.get("future_sha"):
            state_marker = " ← APPLIED"
        elif current_sha == a.get("original_sha"):
            state_marker = " ← original state"

    return f"  {ts}  {label}  {a['filename']}{sha_note}{state_marker}"


def format_patch_list(groups: dict, current_shas: dict[str, str]) -> str:
    """Format the full patch list grouped by target."""
    if not groups:
        return "  (no patch artifacts found)\n"

    lines = []
    for target, artifacts in sorted(groups.items()):
        current_sha = current_shas.get(target, "")
        lines.append(f"\n  Target: {target}")
        if current_sha:
            lines.append(f"    Current SHA: {current_sha}")
        for a in sorted(artifacts, key=lambda x: (x["timestamp"] or "0000", x["filename"])):
            lines.append(format_artifact_line(a, current_sha))
    return "\n".join(lines)

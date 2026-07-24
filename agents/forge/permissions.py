"""
Forge permissions.py
Path validation and trust level enforcement.

Rule: Forge can only access paths that exist in BOTH approved_paths.json AND session_scope.json.
Blocked paths are always blocked regardless of any approval.
"""

import os
import json
import fnmatch
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = FORGE_ROOT / "config"

APPROVED_PATHS_FILE = CONFIG_DIR / "approved_paths.json"
SESSION_SCOPE_FILE  = CONFIG_DIR / "session_scope.json"
BLOCKED_PATHS_FILE  = CONFIG_DIR / "blocked_paths.json"
FILETYPE_POLICY_FILE = CONFIG_DIR / "filetype_policy.json"
TOOL_REGISTRY_FILE  = CONFIG_DIR / "tool_registry.json"

XDG_STATE_HOME = Path(
    os.environ.get(
        "XDG_STATE_HOME",
        str(Path.home() / ".local" / "state"),
    )
)
RUNTIME_STATE_ROOT = XDG_STATE_HOME / "aiweb-forge" / "legacy-workshop-v1"
RUNTIME_APPROVED_PATHS_FILE = RUNTIME_STATE_ROOT / "approved_paths.json"
RUNTIME_SESSION_SCOPE_FILE = RUNTIME_STATE_ROOT / "session_scope.json"

_APPROVED_PATH_KEYS = (
    "paths",
    "approved_paths",
    "allowed_paths",
    "approved_roots",
    "allowed_roots",
    "approved_implementation_roots",
)
_SESSION_PATH_KEYS = (
    "paths",
    "approved_paths",
    "allowed_paths",
)


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def _load_optional_json(path: Path) -> dict:
    try:
        return _load_json(path)
    except FileNotFoundError:
        return {}


def _paths_from_keys(data: dict, keys: tuple[str, ...]) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()

    for key in keys:
        values = data.get(key, [])
        if not isinstance(values, list):
            continue

        for value in values:
            if not isinstance(value, str) or not value.strip():
                continue

            expanded = os.path.expanduser(value.strip())
            normalized = os.path.realpath(os.path.abspath(expanded))

            if normalized in seen:
                continue

            seen.add(normalized)
            paths.append(normalized)

    return paths


def get_approved_paths() -> list[str]:
    """
    Return the union of the accepted source baseline and the local runtime overlay.

    The accepted Slice 0B source record predates the historical runtime's single
    ``paths`` key and uses explicit approved/allowed path fields. Runtime approvals
    live outside the Git repository and may extend, but never erase, that baseline.
    """
    baseline = _paths_from_keys(
        _load_json(APPROVED_PATHS_FILE),
        _APPROVED_PATH_KEYS,
    )
    runtime = _paths_from_keys(
        _load_optional_json(RUNTIME_APPROVED_PATHS_FILE),
        ("paths",),
    )

    result: list[str] = []
    seen: set[str] = set()

    for path in [*baseline, *runtime]:
        if path in seen:
            continue
        seen.add(path)
        result.append(path)

    return result


def get_session_paths() -> list[str]:
    """
    Return the active runtime session scope.

    New sessions are stored under XDG state, outside the source repository. The
    committed Slice 0B record remains a read-only fallback for migration and
    recovery when no runtime session has yet been created.
    """
    runtime = _paths_from_keys(
        _load_optional_json(RUNTIME_SESSION_SCOPE_FILE),
        ("paths",),
    )
    if runtime:
        return runtime

    return _paths_from_keys(
        _load_json(SESSION_SCOPE_FILE),
        _SESSION_PATH_KEYS,
    )


def get_blocked_config() -> dict:
    return _load_json(BLOCKED_PATHS_FILE)


def get_filetype_policy() -> dict:
    return _load_json(FILETYPE_POLICY_FILE)


def get_current_trust_level() -> float:
    data = _load_json(TOOL_REGISTRY_FILE)
    return float(data.get("current_trust_level", 0.5))


def _is_under_any(path: str, directories: list[str]) -> bool:
    """Return True if path is equal to or nested inside any directory in the list."""
    resolved = os.path.realpath(os.path.abspath(path))
    for d in directories:
        d_resolved = os.path.realpath(os.path.abspath(d))
        if resolved == d_resolved or resolved.startswith(d_resolved + os.sep):
            return True
    return False


def _matches_any_pattern(path: str, patterns: list[str]) -> bool:
    """Return True if the path or any component matches a blocked pattern."""
    resolved = os.path.realpath(os.path.abspath(path))
    basename = os.path.basename(resolved)
    # Check basename against patterns
    for pattern in patterns:
        if fnmatch.fnmatch(basename.lower(), pattern.lower()):
            return True
        if fnmatch.fnmatch(resolved.lower(), pattern.lower()):
            return True
    return False


def _has_blocked_component(path: str, blocked_dirs: list[str]) -> bool:
    """Return True if any path component is a blocked directory name."""
    resolved = os.path.realpath(os.path.abspath(path))
    parts = resolved.split(os.sep)
    for blocked in blocked_dirs:
        # blocked may be a name like '.ssh' or a subpath like '.config/google-chrome'
        blocked_parts = blocked.strip(os.sep).split(os.sep)
        for i in range(len(parts) - len(blocked_parts) + 1):
            if parts[i:i+len(blocked_parts)] == blocked_parts:
                return True
    return False


def is_path_blocked(path: str) -> tuple[bool, str]:
    """
    Check whether a path is blocked by blocked_paths.json.
    Returns (blocked: bool, reason: str).
    """
    blocked = get_blocked_config()
    resolved = os.path.realpath(os.path.abspath(os.path.expanduser(path)))

    # Check exact blocked paths
    for exact in blocked.get("blocked_exact", []):
        exact_resolved = os.path.realpath(os.path.abspath(os.path.expanduser(exact)))
        if resolved == exact_resolved or resolved.startswith(exact_resolved + os.sep):
            return True, f"Path is in blocked_exact list: {exact}"

    # Check blocked patterns (filename and full path)
    if _matches_any_pattern(resolved, blocked.get("blocked_patterns", [])):
        return True, f"Path matches a blocked pattern"

    # Check blocked directory components
    if _has_blocked_component(resolved, blocked.get("blocked_directories", [])):
        return True, f"Path contains a blocked directory component"

    return False, ""


def is_path_in_approved_scope(path: str) -> tuple[bool, str]:
    """
    Check whether a path is within approved_paths ∩ session_scope.
    Returns (allowed: bool, reason: str).
    """
    approved = get_approved_paths()
    session  = get_session_paths()

    if not approved:
        return False, "No approved paths have been configured. Run 'forge approve <path>' first."

    if not session:
        return False, "No session scope is active. Start a session first."

    # Intersection: must be under at least one approved AND at least one session path
    under_approved = _is_under_any(path, approved)
    under_session  = _is_under_any(path, session)

    if not under_approved:
        return False, f"Path is not within any approved path. Approved: {approved}"
    if not under_session:
        return False, f"Path is not within the current session scope. Session: {session}"

    return True, ""


def is_path_allowed(path: str) -> tuple[bool, str]:
    """
    Full check: not blocked AND within approved ∩ session scope.
    Returns (allowed: bool, reason: str).
    This is the single function all tools must call before accessing any path.
    """
    path = os.path.expanduser(path)

    blocked, reason = is_path_blocked(path)
    if blocked:
        return False, f"BLOCKED: {reason}"

    allowed, reason = is_path_in_approved_scope(path)
    if not allowed:
        return False, f"OUT OF SCOPE: {reason}"

    return True, ""


def is_filetype_allowed(path: str) -> tuple[bool, str]:
    """
    Check whether Forge is allowed to read this file type.
    Returns (allowed: bool, reason: str).
    """
    policy = get_filetype_policy()
    path_lower = path.lower()
    basename = os.path.basename(path_lower)

    # Check excluded filenames first
    for name in policy.get("excluded_filenames", []):
        if basename == name.lower():
            return False, f"Filename '{basename}' is in the excluded filenames list."

    # Check excluded extensions
    _, ext = os.path.splitext(path_lower)
    for excluded_ext in policy.get("excluded_extensions", []):
        if ext == excluded_ext.lower() or path_lower.endswith(excluded_ext.lower()):
            return False, f"File extension '{ext}' is excluded by filetype policy."

    # Check file size if file exists
    if os.path.isfile(path):
        size_kb = os.path.getsize(path) / 1024
        max_kb = policy.get("max_file_size_kb", 512)
        if size_kb > max_kb:
            return False, f"File size {size_kb:.1f}KB exceeds max allowed {max_kb}KB."

    # Check allowed extensions (if list is non-empty, file must match one)
    allowed_exts = policy.get("allowed_extensions", [])
    if allowed_exts:
        matched = False
        for allowed_ext in allowed_exts:
            if ext == allowed_ext.lower() or basename == allowed_ext.lower():
                matched = True
                break
        if not matched:
            return False, f"File extension '{ext}' is not in the allowed extensions list."

    return True, ""


def is_tool_allowed(tool_name: str) -> tuple[bool, str]:
    """
    Check whether a tool is available at the current trust level.
    Returns (allowed: bool, reason: str).
    """
    data = _load_json(TOOL_REGISTRY_FILE)
    current_level = float(data.get("current_trust_level", 0.5))
    tools = data.get("tools", {})

    if tool_name not in tools:
        return False, f"Tool '{tool_name}' does not exist in the tool registry."

    required_level = float(tools[tool_name].get("trust_level", 99))
    if current_level < required_level:
        return False, (
            f"Tool '{tool_name}' requires trust level {required_level}. "
            f"Current level is {current_level}."
        )

    return True, ""

"""
Forge tools.py
All Level 0.5 tool implementations.

Every tool:
  1. Validates path permissions before accessing anything
  2. Returns a structured result dict
  3. Never writes, never executes commands
  4. Caller is responsible for writing the audit log entry

Tools at Level 0.5:
  - list_allowed_folders()
  - list_files(path, max_depth)
  - read_file(path, start_line, end_line)
  - search_text(query, path, case_sensitive)
"""

import os
import fnmatch
from pathlib import Path
from typing import Optional

from .permissions import (
    is_path_allowed,
    is_filetype_allowed,
    get_approved_paths,
    get_session_paths,
    get_filetype_policy,
)


# ─── RESULT BUILDER ───────────────────────────────────────────────────────────

def _ok(data: str | list | dict) -> dict:
    return {"ok": True, "data": data}


def _err(message: str) -> dict:
    return {"ok": False, "error": message}


# ─── TOOL: list_allowed_folders ───────────────────────────────────────────────

def list_allowed_folders() -> dict:
    """
    Return the intersection of approved_paths and session_scope.
    This is everything Forge is allowed to access right now.
    """
    approved = get_approved_paths()
    session  = get_session_paths()

    if not approved:
        return _err("No approved paths configured. Run 'forge approve <path>' first.")
    if not session:
        return _err("No session scope is active.")

    # Intersection: session paths that are within approved paths
    accessible = []
    for sp in session:
        sp_real = os.path.realpath(os.path.abspath(sp))
        for ap in approved:
            ap_real = os.path.realpath(os.path.abspath(ap))
            if sp_real == ap_real or sp_real.startswith(ap_real + os.sep):
                accessible.append(sp_real)
                break

    if not accessible:
        return _err(
            "Session scope has no overlap with approved paths. "
            f"Session: {session} | Approved: {approved}"
        )

    lines = ["Accessible paths for this session:"]
    for p in accessible:
        exists = os.path.exists(p)
        lines.append(f"  {'✓' if exists else '✗ (missing)'} {p}")

    return _ok("\n".join(lines))


# ─── TOOL: list_files ─────────────────────────────────────────────────────────

def list_files(path: str, max_depth: int = 2) -> dict:
    """
    List files and directories inside an approved path.
    Respects filetype policy for what gets shown.
    max_depth: how many directory levels to recurse (1 = top level only).
    """
    path = os.path.expanduser(path)

    allowed, reason = is_path_allowed(path)
    if not allowed:
        return _err(reason)

    if not os.path.exists(path):
        return _err(f"Path does not exist: {path}")

    if os.path.isfile(path):
        return _err(f"'{path}' is a file, not a directory. Use read_file instead.")

    policy = get_filetype_policy()
    excluded_exts = set(e.lower() for e in policy.get("excluded_extensions", []))
    excluded_names = set(n.lower() for n in policy.get("excluded_filenames", []))
    blocked_dirs = [
        ".ssh", ".gnupg", ".config", ".cache", ".local", "node_modules",
        "__pycache__", ".git", ".venv", ".env"
    ]

    lines = [f"Contents of {path}:"]
    entry_count = 0
    max_entries = 200

    def _recurse(current_path: str, depth: int, prefix: str):
        nonlocal entry_count
        if depth > max_depth or entry_count >= max_entries:
            return

        try:
            entries = sorted(os.scandir(current_path), key=lambda e: (not e.is_dir(), e.name))
        except PermissionError:
            lines.append(f"{prefix}[permission denied]")
            return

        for entry in entries:
            if entry_count >= max_entries:
                lines.append(f"{prefix}... (truncated at {max_entries} entries)")
                return

            name = entry.name
            name_lower = name.lower()

            # Skip hidden files except common important ones
            if name.startswith(".") and name not in (
                ".gitignore", ".gitattributes", ".env.example", ".python-version"
            ):
                continue

            # Skip blocked directory names
            if entry.is_dir() and name_lower in (d.lower() for d in blocked_dirs):
                continue

            if entry.is_dir():
                # Check directory is within allowed scope before recursing
                allowed, _ = is_path_allowed(entry.path)
                if not allowed:
                    continue
                lines.append(f"{prefix}📁 {name}/")
                entry_count += 1
                if depth < max_depth:
                    _recurse(entry.path, depth + 1, prefix + "   ")
            else:
                # Check file extension
                _, ext = os.path.splitext(name_lower)
                if name_lower in excluded_names or ext in excluded_exts:
                    continue
                size = entry.stat().st_size
                size_str = _format_size(size)
                lines.append(f"{prefix}📄 {name}  ({size_str})")
                entry_count += 1

    _recurse(path, 1, "  ")

    if entry_count == 0:
        lines.append("  (empty or all entries filtered)")

    return _ok("\n".join(lines))


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f}KB"
    else:
        return f"{size_bytes/(1024*1024):.1f}MB"


# ─── TOOL: read_file ──────────────────────────────────────────────────────────

def read_file(
    path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None
) -> dict:
    """
    Read the contents of a file within an approved path.
    Optionally read only a range of lines (1-indexed, inclusive).
    Respects filetype policy and max_lines_per_read.
    """
    path = os.path.expanduser(path)

    allowed, reason = is_path_allowed(path)
    if not allowed:
        return _err(reason)

    allowed_type, reason = is_filetype_allowed(path)
    if not allowed_type:
        return _err(f"File type not allowed: {reason}")

    if not os.path.exists(path):
        return _err(f"File does not exist: {path}")

    if not os.path.isfile(path):
        return _err(f"'{path}' is a directory. Use list_files instead.")

    policy = get_filetype_policy()
    max_lines = policy.get("max_lines_per_read", 500)

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
    except OSError as e:
        return _err(f"Cannot read file: {e}")

    total_lines = len(all_lines)

    # Apply line range
    if start_line is not None or end_line is not None:
        s = (start_line - 1) if start_line else 0
        e = end_line if end_line else total_lines
        s = max(0, s)
        e = min(total_lines, e)
        selected = all_lines[s:e]
        line_info = f"lines {s+1}–{min(e, total_lines)} of {total_lines}"
    else:
        selected = all_lines[:max_lines]
        line_info = (
            f"all {total_lines} lines"
            if total_lines <= max_lines
            else f"first {max_lines} of {total_lines} lines (use start_line/end_line for more)"
        )

    # Further limit by max_lines
    if len(selected) > max_lines:
        selected = selected[:max_lines]
        line_info += f" (truncated to {max_lines})"

    content = "".join(selected)
    header = f"── {path}  [{line_info}] ──\n"

    return _ok(header + content)


# ─── TOOL: search_text ────────────────────────────────────────────────────────

def search_text(
    query: str,
    path: str,
    case_sensitive: bool = False,
    max_results: int = 50
) -> dict:
    """
    Search for a text string across files in an approved path.
    Returns matching lines with file path and line number.
    Works on a single file or recursively across a directory.
    """
    path = os.path.expanduser(path)

    allowed, reason = is_path_allowed(path)
    if not allowed:
        return _err(reason)

    if not os.path.exists(path):
        return _err(f"Path does not exist: {path}")

    policy = get_filetype_policy()
    excluded_exts = set(e.lower() for e in policy.get("excluded_extensions", []))
    excluded_names = set(n.lower() for n in policy.get("excluded_filenames", []))
    max_file_kb = policy.get("max_file_size_kb", 512)

    search_query = query if case_sensitive else query.lower()
    results = []

    def _search_file(filepath: str):
        if len(results) >= max_results:
            return

        # Check path is allowed
        allowed, _ = is_path_allowed(filepath)
        if not allowed:
            return

        name_lower = os.path.basename(filepath).lower()
        _, ext = os.path.splitext(name_lower)
        if name_lower in excluded_names or ext in excluded_exts:
            return

        if os.path.getsize(filepath) / 1024 > max_file_kb:
            return

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, start=1):
                    if len(results) >= max_results:
                        break
                    compare = line if case_sensitive else line.lower()
                    if search_query in compare:
                        results.append(
                            f"{filepath}:{line_num}: {line.rstrip()}"
                        )
        except OSError:
            pass

    if os.path.isfile(path):
        _search_file(path)
    else:
        for dirpath, dirnames, filenames in os.walk(path):
            # Prune blocked/hidden directories in-place
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".")
                and d not in ("node_modules", "__pycache__", ".venv", ".git")
            ]
            for fname in sorted(filenames):
                if len(results) >= max_results:
                    break
                _search_file(os.path.join(dirpath, fname))

    if not results:
        return _ok(f"No matches found for '{query}' in {path}")

    header = f"Search results for '{query}' in {path} ({len(results)} match{'es' if len(results) != 1 else ''}):\n"
    truncation = f"\n... (showing first {max_results} results)" if len(results) >= max_results else ""
    return _ok(header + "\n".join(results) + truncation)


# ─── TOOL DISPATCHER ──────────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_allowed_folders",
            "description": "List the folders Forge is allowed to access in this session. Always call this first if unsure what is accessible.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and subdirectories inside an approved directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the directory to list."
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "How many directory levels to recurse. Default 2. Max 4.",
                        "default": 2
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file. Optionally specify a line range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file to read."
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "First line to read (1-indexed). Optional."
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Last line to read (inclusive, 1-indexed). Optional."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_text",
            "description": "Search for a text string across files in an approved path. Works on a single file or a whole directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The text to search for."
                    },
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file or directory to search."
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether to match case. Default false.",
                        "default": False
                    }
                },
                "required": ["query", "path"]
            }
        }
    }
]


def dispatch(tool_name: str, args: dict) -> dict:
    """
    Route a tool call to its implementation.
    Returns the tool result dict.
    """
    if tool_name == "list_allowed_folders":
        return list_allowed_folders()

    elif tool_name == "list_files":
        path = args.get("path", "")
        depth = min(int(args.get("max_depth", 2)), 4)
        return list_files(path, depth)

    elif tool_name == "read_file":
        path = args.get("path", "")
        start = args.get("start_line", None)
        end   = args.get("end_line", None)
        if start is not None:
            start = int(start)
        if end is not None:
            end = int(end)
        return read_file(path, start, end)

    elif tool_name == "search_text":
        query = args.get("query", "")
        path  = args.get("path", "")
        case  = bool(args.get("case_sensitive", False))
        return search_text(query, path, case)

    else:
        return _err(f"Unknown tool: '{tool_name}'. Available: list_allowed_folders, list_files, read_file, search_text")

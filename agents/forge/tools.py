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
  - search_knowledge_base(query, n_results)
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
from .knowledge_base import search_knowledge_base as _kb_search
from . import proposals as _proposals
from . import diagnostics as _diagnostics
from . import runner as _runner
from . import patcher as _patcher


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
    },
    {
        "type": "function",
        "function": {
            "name": "propose_command",
            "description": (
                "Propose a safe diagnostic shell command for Nic to run manually. "
                "Forge NEVER executes the command — it only validates, explains, and saves a proposal. "
                "Only safe, read-only diagnostic commands are allowed. "
                "Always fully explain purpose, safety rationale, expected output, and risks before proposing. "
                "If a command would be destructive, modify files, execute code, or touch sensitive paths, "
                "do NOT call this tool — explain why you cannot propose it instead."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The exact command string to propose. Must be a single diagnostic command with no chaining, pipes, or redirects."
                    },
                    "purpose": {
                        "type": "string",
                        "description": "What this command checks or reveals. One or two sentences."
                    },
                    "safety_rationale": {
                        "type": "string",
                        "description": "Why this specific command is safe to run. Be specific."
                    },
                    "risk_level": {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH"],
                        "description": "LOW = reads one file or shows version. MEDIUM = walks a directory or reads many files. HIGH = touches system state."
                    },
                    "expected_output": {
                        "type": "string",
                        "description": "What the terminal output will look like when Nic runs this command."
                    },
                    "what_could_go_wrong": {
                        "type": "string",
                        "description": "Edge cases, caveats, or unexpected output to be aware of."
                    }
                },
                "required": ["command", "purpose", "safety_rationale", "risk_level", "expected_output", "what_could_go_wrong"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_command_output",
            "description": (
                "Receive and store terminal output that Nic pasted from a command he ran manually. "
                "Call this FIRST when Nic provides terminal output for analysis. "
                "CRITICAL: The 'output' argument MUST be copied verbatim from Nic's message — "
                "character for character, exactly as it appears above in the conversation. "
                "NEVER substitute example values, expected values, training data, or fabricated output. "
                "If Nic pasted 'Mem: 62Gi 7.8Gi' then output must be 'Mem: 62Gi 7.8Gi', not anything else. "
                "If you cannot find the exact output in the conversation, do NOT call this tool — "
                "instead ask Nic to paste the output again."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The exact command Nic ran that produced this output."
                    },
                    "output": {
                        "type": "string",
                        "description": (
                            "The EXACT terminal output copied verbatim from Nic's message above. "
                            "Do not modify, truncate, paraphrase, or substitute. "
                            "Do not use example values from the tool schema or your training data. "
                            "If not found in the conversation, use the literal string: OUTPUT_NOT_FOUND"
                        )
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional: what we are trying to diagnose. One sentence."
                    }
                },
                "required": ["command", "output"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_safe_command",
            "description": (
                "Execute a safe read-only diagnostic command from the hard-coded Level 1.0 allowlist. "
                "The command runs with a fixed argv list — no shell, no pipes, no redirects. "
                "Output is captured, saved to diagnostics, and audited automatically. "
                "Only the listed command_name values are accepted. "
                "Use this when you need live system data that cannot be read from files. "
                "After calling this, analyze the output and explain what it means."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command_name": {
                        "type": "string",
                        "enum": [
                            "nvidia-smi",
                            "ollama ps",
                            "ollama version",
                            "free -h",
                            "df -h",
                            "lscpu",
                            "lsblk",
                        ],
                        "description": (
                            "The name of the allowlisted command to execute. "
                            "Must be one of the exact strings in the enum list."
                        )
                    }
                },
                "required": ["command_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_proposed_patch",
            "description": (
                "Create a structured patch proposal document inside ~/forge/proposed_patches/. "
                "NEVER modifies any project file. "
                "Use this when you have analyzed a file and have a concrete, well-reasoned "
                "change to propose. Include the exact original snippet and the exact proposed "
                "replacement. Nic reviews and applies manually — Forge never applies patches. "
                "Refuse to propose if the change is destructive, risky, or outside scope."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "target_file": {
                        "type": "string",
                        "description": "Absolute path to the file this patch applies to. Must be within approved scope."
                    },
                    "problem_summary": {
                        "type": "string",
                        "description": "One or two sentences describing the problem this patch fixes."
                    },
                    "original_snippet": {
                        "type": "string",
                        "description": "The exact current content of the region being changed. Must be verbatim from the file."
                    },
                    "proposed_snippet": {
                        "type": "string",
                        "description": "The exact proposed replacement content."
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Why this change is correct, safe, and necessary."
                    },
                    "risk_level": {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH"],
                        "description": "LOW = cosmetic/docs. MEDIUM = logic change. HIGH = architecture or data change."
                    },
                    "test_plan": {
                        "type": "string",
                        "description": "How to verify the change works correctly after applying."
                    },
                    "rollback_notes": {
                        "type": "string",
                        "description": "How to undo this change if it causes problems."
                    }
                },
                "required": [
                    "target_file", "problem_summary", "original_snippet",
                    "proposed_snippet", "reasoning", "risk_level",
                    "test_plan", "rollback_notes"
                ]
            }
        }
    }
]


def dispatch(tool_name: str, args: dict, session_id: str = "unknown", user_question: str = "") -> dict:
    """
    Route a tool call to its implementation.
    Returns the tool result dict.
    session_id and user_question are needed for propose_command.
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

    elif tool_name == "search_knowledge_base":
        query    = args.get("query", "")
        n        = min(int(args.get("n_results", 5)), 10)
        result   = _kb_search(query, n)
        if result["ok"]:
            return _ok(result["data"])
        return _err(result["error"])

    elif tool_name == "propose_command":
        result = _proposals.propose_command(
            session_id=session_id,
            user_question=user_question,
            command=args.get("command", ""),
            purpose=args.get("purpose", ""),
            safety_rationale=args.get("safety_rationale", ""),
            risk_level=args.get("risk_level", "MEDIUM"),
            expected_output=args.get("expected_output", ""),
            what_could_go_wrong=args.get("what_could_go_wrong", ""),
        )
        if result["ok"]:
            return _ok(result["message"])
        # Refused proposals still return a message (the refusal explanation)
        return _ok(result.get("message", result.get("reason", "Proposal refused.")))

    elif tool_name == "analyze_command_output":
        result = _diagnostics.analyze_command_output(
            session_id=session_id,
            command=args.get("command", ""),
            output=args.get("output", ""),
            context=args.get("context", ""),
        )
        if result["ok"]:
            return _ok(result["message"])
        return _err(result["error"])

    elif tool_name == "run_safe_command":
        result = _runner.run_safe_command(
            session_id=session_id,
            command_name=args.get("command_name", ""),
        )
        if result["ok"] or "output" in result:
            return _ok(result["message"])
        return _err(result.get("error", "Command failed."))

    elif tool_name == "write_proposed_patch":
        result = _patcher.write_proposed_patch(
            session_id=session_id,
            target_file=args.get("target_file", ""),
            problem_summary=args.get("problem_summary", ""),
            original_snippet=args.get("original_snippet", ""),
            proposed_snippet=args.get("proposed_snippet", ""),
            reasoning=args.get("reasoning", ""),
            risk_level=args.get("risk_level", "MEDIUM"),
            test_plan=args.get("test_plan", ""),
            rollback_notes=args.get("rollback_notes", ""),
        )
        if result["ok"]:
            return _ok(result["message"])
        return _ok(result.get("message", result.get("reason", "Patch proposal refused.")))

    else:
        return _err(
            f"Unknown tool: '{tool_name}'. "
            "Available: list_allowed_folders, list_files, read_file, "
            "search_text, search_knowledge_base, propose_command, "
            "analyze_command_output, run_safe_command, write_proposed_patch"
        )

# --- BEGIN PATCH 212 RMC READ-ONLY TOOL REGISTRATION ---
# This block is appended by scripts/rmc_patch212_register_readonly_tools.py.
# It registers only preview/read-only RMC helpers. It does not write RMC memory,
# does not wire Gilligan, and does not modify Identity Vault or tool_registry.json.
try:
    from . import rmc_tools as _rmc_tools
except Exception as _forge_patch212_rmc_import_exc:  # pragma: no cover - runtime guard
    _rmc_tools = None
    _FORGE_PATCH212_RMC_IMPORT_ERROR = str(_forge_patch212_rmc_import_exc)
else:
    _FORGE_PATCH212_RMC_IMPORT_ERROR = ""

RMC_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "rmc_phase_parse_preview",
            "description": (
                "Preview RMC phase parsing for supplied text without writing memory. "
                "Returns phase number/name, confidence, cues, routing, and warnings."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to phase-parse."
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context metadata for the parser.",
                        "default": {}
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rmc_drift_check_preview",
            "description": (
                "Preview RMC drift arbitration for supplied text and phase context without "
                "applying correction or writing memory."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to drift-check."
                    },
                    "current_phase": {
                        "type": "integer",
                        "description": "Optional current phase number, 1 through 9. If omitted, RMC will parse it."
                    },
                    "phase_history": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Optional prior phase sequence.",
                        "default": []
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rmc_echo_validate_preview",
            "description": (
                "Preview RMC echo validation by comparing rendered output against a "
                "manifest-like object without writing memory."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "rendered_output": {
                        "type": "string",
                        "description": "Rendered text/output to validate."
                    },
                    "manifest": {
                        "type": "object",
                        "description": "Manifest-like object containing claim, phase, confidence, drift status, etc."
                    },
                    "modality": {
                        "type": "string",
                        "description": "Output modality, usually language.",
                        "default": "language"
                    }
                },
                "required": ["rendered_output", "manifest"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rmc_pipeline_preview",
            "description": (
                "Run the RMC orchestrator preview pipeline without persistent memory writes. "
                "Uses enable_memory=False and store_to_memory=False."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "input_text": {
                        "type": "string",
                        "description": "Input text to pass through the RMC preview pipeline."
                    },
                    "modality": {
                        "type": "string",
                        "description": "Output modality, usually language.",
                        "default": "language"
                    }
                },
                "required": ["input_text"]
            }
        }
    }
]


def _forge_patch212_register_rmc_tool_definitions() -> None:
    """Append RMC tool definitions once, preserving the existing Forge list."""
    try:
        existing = {
            item.get("function", {}).get("name")
            for item in TOOL_DEFINITIONS
            if isinstance(item, dict)
        }
        for item in RMC_TOOL_DEFINITIONS:
            name = item.get("function", {}).get("name")
            if name and name not in existing:
                TOOL_DEFINITIONS.append(item)
                existing.add(name)
    except Exception:
        # Do not break Forge import because of registration metadata trouble.
        pass


_forge_patch212_register_rmc_tool_definitions()

_FORGE_PATCH212_RMC_TOOL_NAMES = {
    "rmc_phase_parse_preview",
    "rmc_drift_check_preview",
    "rmc_echo_validate_preview",
    "rmc_pipeline_preview",
}

_FORGE_PATCH212_BASE_DISPATCH = dispatch


def _forge_patch212_dispatch_rmc_preview(tool_name: str, args: dict) -> dict:
    if _rmc_tools is None:
        return _err(f"RMC read-only wrapper unavailable: {_FORGE_PATCH212_RMC_IMPORT_ERROR}")

    try:
        if tool_name == "rmc_phase_parse_preview":
            return _rmc_tools.rmc_phase_parse_preview(
                text=args.get("text", ""),
                context=args.get("context") or {},
            )

        if tool_name == "rmc_drift_check_preview":
            return _rmc_tools.rmc_drift_check_preview(
                text=args.get("text", ""),
                current_phase=args.get("current_phase", None),
                phase_history=args.get("phase_history") or [],
            )

        if tool_name == "rmc_echo_validate_preview":
            return _rmc_tools.rmc_echo_validate_preview(
                rendered_output=args.get("rendered_output", ""),
                manifest=args.get("manifest") or {},
                modality=args.get("modality", "language"),
            )

        if tool_name == "rmc_pipeline_preview":
            return _rmc_tools.rmc_pipeline_preview(
                input_text=args.get("input_text", ""),
                modality=args.get("modality", "language"),
            )

        return _err(f"Unknown RMC preview tool: {tool_name}")
    except Exception as exc:  # pragma: no cover - runtime guard
        return _err(f"RMC preview tool failed: {type(exc).__name__}: {exc}")


def dispatch(tool_name: str, args: dict, session_id: str = "unknown", user_question: str = "") -> dict:
    """
    Patch 212 dispatch wrapper.
    RMC preview tools are handled here; every other tool falls back to the original Forge dispatcher.
    """
    if tool_name in _FORGE_PATCH212_RMC_TOOL_NAMES:
        return _forge_patch212_dispatch_rmc_preview(tool_name, args or {})
    return _FORGE_PATCH212_BASE_DISPATCH(
        tool_name,
        args,
        session_id=session_id,
        user_question=user_question,
    )
# --- END PATCH 212 RMC READ-ONLY TOOL REGISTRATION ---

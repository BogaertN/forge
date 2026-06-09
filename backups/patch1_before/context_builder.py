"""
Forge context_builder.py
Assembles the system prompt and per-query context for the LLM.

The system prompt tells qwen3:8b exactly what it is, what it can do,
what it cannot do, and how to format its responses.
"""

import os
import json
from pathlib import Path

from .permissions import get_approved_paths, get_session_paths
from .memory import load_user_profile, load_project_profile, SessionMemory

FORGE_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = FORGE_ROOT / "config"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def build_system_prompt(session_id: str, session_memory: SessionMemory) -> str:
    """
    Build the full system prompt for qwen3:8b.
    Called once per session. Tells the model exactly what Forge is.
    """
    approved = get_approved_paths()
    session  = get_session_paths()
    user     = load_user_profile()
    project  = load_project_profile()

    approved_str = "\n".join(f"  - {p}" for p in approved) if approved else "  (none configured)"
    session_str  = "\n".join(f"  - {p}" for p in session) if session else "  (none configured)"

    project_root = project.get("project_root", "not set")
    project_name = project.get("current_project", "unknown")
    user_name    = user.get("name", "Nic")

    return f"""You are Forge, a local coding assistant and computer-awareness agent built by {user_name} as part of the AI.Web system.

SESSION ID: {session_id}

YOUR ROLE:
You help {user_name} understand what is happening on their own machine. You read files, explain code, search projects, and answer questions about the local system — clearly, honestly, and in plain language.

YOU ARE IN READ-ONLY MODE (Level 0.5):
- You may read files within the approved and session-scoped paths
- You may list directories within those paths
- You may search for text within those paths
- You may NOT write any files
- You may NOT execute any shell commands
- You may NOT access paths outside the approved scope
- You may NOT modify, delete, or move anything

ACCESSIBLE PATHS THIS SESSION:
Permanently approved paths:
{approved_str}

Current session scope:
{session_str}

Access rule: You can only access paths that appear in BOTH lists (the intersection). If a path is missing from either list, refuse to access it and explain why.

CURRENT PROJECT CONTEXT:
Project name: {project_name}
Project root: {project_root}

TOOL USE:
You have four tools available:
1. list_allowed_folders — always call this first if unsure what you can access
2. list_files(path, max_depth) — list directory contents
3. read_file(path, start_line, end_line) — read a file or part of it
4. search_text(query, path, case_sensitive) — search for text across files

Always use tools to gather evidence before answering. Never guess at file contents. If you need to see something, read it.

RESPONSE FORMAT:
After completing your tool calls and analysis, structure your response exactly like this:

─── FORGE ───────────────────────────────────────
What I checked:   [list the files/paths you accessed]
What I found:     [plain language description of what you found]
What it means:    [your interpretation and explanation]
What I did not touch: [confirmation of what was not modified]
─────────────────────────────────────────────────
[Your full explanation here in plain language. Be specific. Cite line numbers and file names.]
─────────────────────────────────────────────────
No files were changed this session.

RULES:
- Never fabricate file contents. If you cannot read a file, say so.
- Never claim a path is accessible without verifying it with list_allowed_folders first.
- If a question requires accessing a blocked or out-of-scope path, explain why you cannot help with that specific request.
- Be direct. {user_name} is an experienced builder. Do not over-explain basics.
- If you are uncertain about something, say so. Do not guess.
- End every response with either "No files were changed this session." or "The following files were changed: [list]."
"""


def build_user_context(question: str, session_memory: SessionMemory) -> list[dict]:
    """
    Build the messages list for the LLM API call.
    Includes conversation history from session memory.
    """
    messages = []

    # If there are previous tool results in session memory, include them
    previous_results = session_memory.get_tool_results_for_context()
    for result in previous_results:
        messages.append({
            "role": "tool",
            "content": result["content"]
        })

    # The current user question
    messages.append({
        "role": "user",
        "content": question
    })

    return messages

#!/usr/bin/env python3
"""
Patch 212 — Register Forge RMC Read-Only Preview Tools

This script performs a careful, idempotent append-only registration of the
Patch 211 RMC read-only wrapper functions into Forge's tool surface.

Boundary:
- Modifies only ~/forge/agents/forge/tools.py.
- Does not modify tool_registry.json.
- Does not touch AI.Web wrappers, Identity Vault, databases, or Gilligan wiring.
- Registers preview-only functions that call forge.agents.forge.rmc_tools.
"""
from __future__ import annotations

import datetime as _dt
import json
import shutil
from pathlib import Path

PATCH_ID = "patch212_rmc_readonly_tool_registration"
BEGIN_MARKER = "# --- BEGIN PATCH 212 RMC READ-ONLY TOOL REGISTRATION ---"
END_MARKER = "# --- END PATCH 212 RMC READ-ONLY TOOL REGISTRATION ---"

BLOCK = r'''
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
'''


def _home() -> Path:
    return Path.home()


def _forge_root() -> Path:
    return _home() / "forge"


def _tools_path() -> Path:
    return _forge_root() / "agents" / "forge" / "tools.py"


def _report_root() -> Path:
    return _forge_root() / "memory" / "rmc_patch212_tool_registration_v1"


def _count_rmc_tool_names(text: str) -> int:
    return sum(text.count(name) for name in [
        "rmc_phase_parse_preview",
        "rmc_drift_check_preview",
        "rmc_echo_validate_preview",
        "rmc_pipeline_preview",
    ])


def main() -> int:
    ts = _dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S_UTC")
    forge = _forge_root()
    tools = _tools_path()
    report_dir = _report_root() / ts
    report_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "patch": PATCH_ID,
        "timestamp": ts,
        "tools_path": str(tools),
        "modified": False,
        "already_registered": False,
        "backup_path": None,
        "checks": {},
        "verdict": "FAIL",
    }

    if not tools.exists():
        result["checks"]["tools_exists"] = False
        _write_reports(result, report_dir)
        print("Patch 212 registration refused: tools.py not found.")
        return 1

    original = tools.read_text(encoding="utf-8", errors="replace")
    result["checks"]["tools_exists"] = True
    result["checks"]["begin_marker_before"] = BEGIN_MARKER in original
    result["checks"]["rmc_tool_name_mentions_before"] = _count_rmc_tool_names(original)

    if BEGIN_MARKER in original and END_MARKER in original:
        result["already_registered"] = True
        result["verdict"] = "PASS"
    elif BEGIN_MARKER in original or END_MARKER in original:
        result["verdict"] = "FAIL_PARTIAL_MARKER"
        _write_reports(result, report_dir)
        print("Patch 212 registration refused: partial marker state detected in tools.py.")
        return 1
    else:
        backup_dir = forge / "backups" / "patch212_rmc_tool_registration_before"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / f"{ts}_tools.py"
        shutil.copy2(tools, backup)
        result["backup_path"] = str(backup)

        updated = original.rstrip() + "\n\n" + BLOCK.strip() + "\n"
        tools.write_text(updated, encoding="utf-8")
        result["modified"] = True
        result["verdict"] = "PASS"

    after = tools.read_text(encoding="utf-8", errors="replace")
    result["checks"]["begin_marker_after"] = BEGIN_MARKER in after
    result["checks"]["end_marker_after"] = END_MARKER in after
    result["checks"]["rmc_tool_name_mentions_after"] = _count_rmc_tool_names(after)
    result["checks"]["tool_registry_untouched"] = True

    _write_reports(result, report_dir)
    print("RMC Patch 212 read-only tool registration complete.")
    print(f"Run directory: {report_dir}")
    print(f"Report: {_report_root() / 'latest_rmc_patch212_tool_registration.md'}")
    print(f"Verdict: {result['verdict']}")
    return 0 if result["verdict"] == "PASS" else 1


def _write_reports(result: dict, report_dir: Path) -> None:
    root = _report_root()
    root.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / f"{result['timestamp']}_rmc_patch212_tool_registration.json"
    md_path = report_dir / f"{result['timestamp']}_rmc_patch212_tool_registration.md"
    latest_json = root / "latest_rmc_patch212_tool_registration.json"
    latest_md = root / "latest_rmc_patch212_tool_registration.md"

    json_text = json.dumps(result, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")

    lines = [
        "# RMC Patch 212 Tool Registration Report",
        "",
        f"Timestamp: `{result['timestamp']}`",
        f"Tools file: `{result['tools_path']}`",
        f"Verdict: **{result['verdict']}**",
        "",
        "## Boundary",
        "- Registered only read-only RMC preview tool definitions and dispatch hooks.",
        "- Did not modify `tool_registry.json`.",
        "- Did not wire Gilligan personality.",
        "- Did not touch Identity Vault, databases, or persistent RMC memory.",
        "",
        "## Change State",
        f"- modified: `{result.get('modified')}`",
        f"- already_registered: `{result.get('already_registered')}`",
        f"- backup_path: `{result.get('backup_path')}`",
        "",
        "## Checks",
    ]
    for key, value in result.get("checks", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines += [
        "",
        "## Next Safe Step",
        "Run `python scripts/rmc_patch212_verify.py` to verify Forge can import and dispatch the read-only RMC preview tools. Do not wire Gilligan yet.",
    ]
    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

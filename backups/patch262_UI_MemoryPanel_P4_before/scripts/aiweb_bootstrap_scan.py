#!/usr/bin/env python3
"""
Patch 206 - AI.Web Bootstrap Boundary Scanner
Read-only scanner for Forge / AI.Web / RMC / Identity Vault / ProtoForge2 / EchoForge bootstrap readiness.

This script only writes reports under:
  ~/forge/memory/aiweb_bootstrap_boundary_v1/

It does not move, delete, import, execute, or modify project modules.
"""

from __future__ import annotations

import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_SUBDIR = Path("forge/memory/aiweb_bootstrap_boundary_v1")

RMC_MODULES = [
    "phase_state_parser",
    "ancestral_memory",
    "drift_arbitrator",
    "manifest_compiler",
    "output_renderer",
    "echo_gate",
    "rmc_orchestrator",
]

WORKING_RMC_FROM_S19 = {
    "ancestral_memory": "S19AF - expected working module",
    "manifest_compiler": "S19AH - expected working module",
    "output_renderer": "S19AI - expected working module",
    "rmc_orchestrator": "S19AK - expected working module",
}

MISSING_RMC_FROM_CLAUDE = {
    "phase_state_parser": "S19AE - required for phase parsing",
    "drift_arbitrator": "S19AG - required for drift arbitration",
    "echo_gate": "S19AJ - required for echo validation",
}

FORGE_AGENT_FILES = [
    "agents/forge/agent.py",
    "agents/forge/tools.py",
    "agents/forge/memory.py",
    "agents/forge/context_builder.py",
]

ROOT_CANDIDATES = {
    "forge": ["forge"],
    "aiweb": ["aiweb"],
    "identity_vault": ["identity-vault", "identity_vault", "aiweb/identity-vault"],
    "protoforge2": ["protoforge2", "ProtoForge2", "aiweb/protoforge2", "aiweb/projects/protoforge2"],
    "echoforge": ["echoforge", "EchoForge", "aiweb/echoforge", "aiweb/projects/echoforge"],
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "chroma_db",
    "patch_sandboxes",
    "rollback_registry",
    "proposed_patches",
    "logs",
    "backups",
    "dist",
    "build",
}


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def safe_exists(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False


def safe_is_dir(path: Path) -> bool:
    try:
        return path.is_dir()
    except OSError:
        return False


def safe_is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def rel(path: Path, home: Path) -> str:
    try:
        return str(path.resolve().relative_to(home.resolve()))
    except Exception:
        return str(path)


def find_first_existing(home: Path, candidates: list[str]) -> dict[str, Any]:
    hits = []
    for candidate in candidates:
        p = home / candidate
        if safe_exists(p):
            hits.append({"path": str(p), "relative_path": rel(p, home), "is_dir": safe_is_dir(p), "is_file": safe_is_file(p)})
    return {"present": bool(hits), "hits": hits, "candidates_checked": [str(home / c) for c in candidates]}


def read_json_safely(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        if not path.exists():
            return None, "missing"
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, f"read_error: {exc}"


def count_files_limited(root: Path, limit: int = 100000) -> dict[str, Any]:
    if not safe_is_dir(root):
        return {"present": False, "file_count_limited": 0, "dir_count_limited": 0, "limit_hit": False}
    file_count = 0
    dir_count = 0
    limit_hit = False
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        dir_count += len(dirs)
        file_count += len(files)
        if file_count + dir_count >= limit:
            limit_hit = True
            break
    return {"present": True, "file_count_limited": file_count, "dir_count_limited": dir_count, "limit_hit": limit_hit}


def scan_rmc_modules(home: Path) -> dict[str, Any]:
    locations = {
        "aiweb_runtime_wrappers": home / "aiweb/runtime_wrappers",
        "forge_rmc_shared": home / "forge/rmc_shared",
    }
    result: dict[str, Any] = {"locations": {}, "modules": {}, "summary": {}}
    for loc_name, loc_path in locations.items():
        result["locations"][loc_name] = {
            "path": str(loc_path),
            "present": safe_is_dir(loc_path),
        }

    for module in RMC_MODULES:
        module_hits = []
        for loc_name, loc_path in locations.items():
            p = loc_path / module
            if safe_exists(p):
                module_hits.append({
                    "location": loc_name,
                    "path": str(p),
                    "relative_path": rel(p, home),
                    "is_dir": safe_is_dir(p),
                    "is_file": safe_is_file(p),
                    "file_summary": count_files_limited(p, limit=5000) if safe_is_dir(p) else None,
                })
        result["modules"][module] = {
            "present": bool(module_hits),
            "hits": module_hits,
            "claude_status": "expected_working" if module in WORKING_RMC_FROM_S19 else "reported_missing_required",
            "note": WORKING_RMC_FROM_S19.get(module) or MISSING_RMC_FROM_CLAUDE.get(module) or "expected RMC module",
        }

    present = [m for m, info in result["modules"].items() if info["present"]]
    missing = [m for m, info in result["modules"].items() if not info["present"]]
    result["summary"] = {
        "expected_count": len(RMC_MODULES),
        "present_count": len(present),
        "missing_count": len(missing),
        "present": present,
        "missing": missing,
        "missing_required_from_claude": [m for m in MISSING_RMC_FROM_CLAUDE if m in missing],
    }
    return result


def search_for_module_dirs(home: Path, module_names: list[str]) -> dict[str, Any]:
    """Targeted search under known project roots. Read-only and skips heavy folders."""
    roots = [home / "forge", home / "aiweb", home / "identity-vault", home / "identity_vault"]
    hits: dict[str, list[dict[str, str]]] = {name: [] for name in module_names}
    target_set = set(module_names)

    for root in roots:
        if not safe_is_dir(root):
            continue
        for current_root, dirs, _files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for d in list(dirs):
                if d in target_set:
                    p = Path(current_root) / d
                    hits[d].append({"path": str(p), "relative_path": rel(p, home)})
    return {"searched_roots": [str(r) for r in roots if safe_is_dir(r)], "hits": hits}


def scan_forge(home: Path) -> dict[str, Any]:
    forge = home / "forge"
    registry_path = forge / "config/tool_registry.json"
    registry, registry_error = read_json_safely(registry_path)
    trust = None
    if isinstance(registry, dict):
        trust = registry.get("current_trust_level")

    agent_files = {}
    for f in FORGE_AGENT_FILES:
        p = forge / f
        agent_files[f] = {"present": safe_is_file(p), "path": str(p), "relative_path": rel(p, home)}

    expected_files = ["main.py", "config/tool_registry.json", "requirements.txt"]
    root_files = {}
    for f in expected_files:
        p = forge / f
        root_files[f] = {"present": safe_exists(p), "path": str(p), "relative_path": rel(p, home)}

    return {
        "root": str(forge),
        "present": safe_is_dir(forge),
        "root_files": root_files,
        "agent_framework_files": agent_files,
        "tool_registry": {
            "path": str(registry_path),
            "present": safe_is_file(registry_path),
            "read_error": registry_error,
            "current_trust_level": trust,
        },
        "file_summary": count_files_limited(forge, limit=100000),
    }


def scan_identity_vault(home: Path) -> dict[str, Any]:
    candidates = [home / "identity-vault", home / "identity_vault", home / "aiweb/identity-vault"]
    existing = [p for p in candidates if safe_is_dir(p)]
    results = []
    for root in existing:
        sensitive = []
        for name in [".env", ".env.local", ".env.production"]:
            p = root / name
            if safe_exists(p):
                sensitive.append({"path": str(p), "relative_path": rel(p, home), "warning": "do_not_package_or_share"})
        dbs = []
        for pattern in ["*.db", "data/*.db", "**/*.sqlite", "**/*.sqlite3"]:
            try:
                for p in root.glob(pattern):
                    if safe_is_file(p):
                        dbs.append({"path": str(p), "relative_path": rel(p, home)})
            except Exception:
                pass
        results.append({
            "root": str(root),
            "relative_path": rel(root, home),
            "package_json": safe_is_file(root / "package.json"),
            "node_modules_present": safe_is_dir(root / "node_modules"),
            "env_files_present": sensitive,
            "database_files_found": dbs[:50],
            "database_file_count_limited": len(dbs),
            "file_summary": count_files_limited(root, limit=50000),
        })
    return {"present": bool(existing), "candidates_checked": [str(c) for c in candidates], "instances": results}


def scan_wrong_standalone_agent(home: Path) -> dict[str, Any]:
    paths = [
        home / "aiweb/runtime_wrappers/gilligan_agent",
        home / "forge/rmc_shared/gilligan_agent",
    ]
    hits = []
    for p in paths:
        if safe_exists(p):
            hits.append({
                "path": str(p),
                "relative_path": rel(p, home),
                "present": True,
                "recommendation": "do_not_delete_until_backed_up_and_integrated; Claude marked standalone architecture as wrong",
                "file_summary": count_files_limited(p, limit=5000) if safe_is_dir(p) else None,
            })
    return {"present": bool(hits), "hits": hits}


def build_recommendations(scan: dict[str, Any]) -> list[str]:
    recs = []
    rmc_missing = scan.get("rmc", {}).get("summary", {}).get("missing", [])
    missing_required = scan.get("rmc", {}).get("summary", {}).get("missing_required_from_claude", [])
    if missing_required:
        recs.append("Do not integrate Gilligan personality yet. Rebuild or locate missing required RMC modules first: " + ", ".join(missing_required) + ".")
    elif rmc_missing:
        recs.append("Some RMC modules are still missing. Complete module inventory before wiring Forge tools.")
    else:
        recs.append("All expected RMC modules were found. Next safe step is a read-only Forge rmc_tools wrapper preflight.")

    if scan.get("standalone_gilligan_agent", {}).get("present"):
        recs.append("Standalone gilligan_agent exists. Do not delete yet. Freeze/copy it first, then retire after Forge-integrated path passes tests.")

    identity_instances = scan.get("identity_vault", {}).get("instances", [])
    if identity_instances:
        for inst in identity_instances:
            if inst.get("env_files_present"):
                recs.append("Identity Vault has .env-style files. Do not include them in future patch bundles; rotate secrets if any archive was shared outside your local machine.")
            if inst.get("node_modules_present"):
                recs.append("Identity Vault has node_modules. Do not package node_modules in future patch bundles.")
            if inst.get("database_file_count_limited", 0) > 1:
                recs.append("Identity Vault appears to have multiple DB files. Normalize to one canonical DB path before live integration.")
    else:
        recs.append("Identity Vault root not found in common locations. Confirm its actual path before adding Forge API calls.")

    recs.append("Keep first integration read-only: status/report commands before move/copy/delete/apply commands.")
    return recs


def write_markdown_report(report: dict[str, Any], md_path: Path) -> None:
    lines = []
    lines.append("# AI.Web Bootstrap Boundary Scan")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp_utc']}`")
    lines.append(f"Home: `{report['home']}`")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    for rec in report["recommendations"]:
        lines.append(f"- {rec}")
    lines.append("")
    lines.append("## Root Presence")
    lines.append("")
    for name, info in report["roots"].items():
        status = "FOUND" if info.get("present") else "MISSING"
        lines.append(f"- `{name}`: **{status}**")
        for hit in info.get("hits", []):
            lines.append(f"  - `{hit.get('relative_path')}`")
    lines.append("")
    lines.append("## RMC Module Inventory")
    lines.append("")
    rmc = report["rmc"]
    lines.append(f"Expected: `{rmc['summary']['expected_count']}` | Present: `{rmc['summary']['present_count']}` | Missing: `{rmc['summary']['missing_count']}`")
    lines.append("")
    for module, info in rmc["modules"].items():
        status = "FOUND" if info["present"] else "MISSING"
        lines.append(f"- `{module}`: **{status}** — {info['note']}")
        for hit in info.get("hits", []):
            lines.append(f"  - `{hit.get('relative_path')}`")
    lines.append("")
    lines.append("## Targeted Search Hits")
    lines.append("")
    for module, hits in report["targeted_module_search"]["hits"].items():
        lines.append(f"- `{module}`:")
        if not hits:
            lines.append("  - no extra hits found")
        for hit in hits:
            lines.append(f"  - `{hit['relative_path']}`")
    lines.append("")
    lines.append("## Forge Framework")
    lines.append("")
    forge = report["forge"]
    lines.append(f"Forge present: `{forge['present']}`")
    lines.append(f"Tool registry trust level: `{forge['tool_registry'].get('current_trust_level')}`")
    for f, info in forge["agent_framework_files"].items():
        lines.append(f"- `{f}`: `{info['present']}`")
    lines.append("")
    lines.append("## Standalone Gilligan Agent")
    lines.append("")
    if report["standalone_gilligan_agent"]["present"]:
        lines.append("Standalone Gilligan agent was found. Do not delete until backed up and retired through a patch.")
        for hit in report["standalone_gilligan_agent"]["hits"]:
            lines.append(f"- `{hit['relative_path']}`")
    else:
        lines.append("No standalone Gilligan agent found in common locations.")
    lines.append("")
    lines.append("## Identity Vault")
    lines.append("")
    if report["identity_vault"]["present"]:
        for inst in report["identity_vault"]["instances"]:
            lines.append(f"- Root: `{inst['relative_path']}`")
            lines.append(f"  - package.json: `{inst['package_json']}`")
            lines.append(f"  - node_modules present: `{inst['node_modules_present']}`")
            lines.append(f"  - env files: `{len(inst['env_files_present'])}`")
            lines.append(f"  - database files found: `{inst['database_file_count_limited']}`")
    else:
        lines.append("Identity Vault not found in common locations.")
    lines.append("")
    lines.append("## Next Safe Command")
    lines.append("")
    lines.append("Send this report back before moving modules or deleting anything.")
    lines.append("")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    home = Path.home()
    report_dir = home / REPORT_SUBDIR
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = now_stamp()
    json_path = report_dir / f"{stamp}_aiweb_bootstrap_scan.json"
    md_path = report_dir / f"{stamp}_aiweb_bootstrap_scan.md"

    roots = {name: find_first_existing(home, candidates) for name, candidates in ROOT_CANDIDATES.items()}

    report: dict[str, Any] = {
        "report_type": "AIWEB_BOOTSTRAP_BOUNDARY_SCAN_V1_PATCH206",
        "timestamp_utc": stamp,
        "home": str(home),
        "python": sys.version,
        "platform": platform.platform(),
        "write_scope": str(report_dir),
        "mode": "READ_ONLY_PROJECT_SCAN_REPORT_WRITE_ONLY",
        "roots": roots,
        "forge": scan_forge(home),
        "rmc": scan_rmc_modules(home),
        "targeted_module_search": search_for_module_dirs(home, RMC_MODULES + ["gilligan_agent"]),
        "standalone_gilligan_agent": scan_wrong_standalone_agent(home),
        "identity_vault": scan_identity_vault(home),
    }
    report["recommendations"] = build_recommendations(report)

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown_report(report, md_path)

    print("AI.Web Bootstrap Boundary Scan complete.")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print("")
    print("Top recommendations:")
    for rec in report["recommendations"]:
        print(f"- {rec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

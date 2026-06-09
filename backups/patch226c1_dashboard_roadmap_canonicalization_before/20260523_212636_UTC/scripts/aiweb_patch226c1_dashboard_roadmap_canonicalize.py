#!/usr/bin/env python3
"""
Patch 226C.1 — Forge Dashboard Roadmap Canonicalization

Purpose:
- Inventory the stale Forge dashboard roadmap panel state.
- Write a canonical AI.Web bootstrap roadmap manifest.
- Safely update the dashboard roadmap source if the known stale Patch 147 / S19AC block is found.

Boundaries:
- May write only under /home/nic/forge/config, /home/nic/forge/backups, and /home/nic/forge/memory.
- May modify a Forge dashboard roadmap source file only after backup and only if stale markers are found.
- Must not read .env secret values.
- Must not touch Identity Vault databases, RMC memory, AI.Web wrappers, agent memory, or tool registry trust.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
import py_compile
import re
import shutil
import stat
import sys
import traceback
from typing import Dict, List, Tuple, Any

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
CONFIG_DIR = FORGE_ROOT / "config"
MEMORY_ROOT = FORGE_ROOT / "memory" / "dashboard_roadmap_patch226c1_canonicalization_v1"
BACKUP_ROOT = FORGE_ROOT / "backups" / "patch226c1_dashboard_roadmap_canonicalization_before"
IDENTITY_ENV = HOME / "identity-vault" / ".env"
CANONICAL_DB = HOME / "identity-vault" / "data" / "identity_vault.db"
LEGACY_DB = HOME / "identity-vault" / "vault.db"
TOOL_REGISTRY = FORGE_ROOT / "config" / "tool_registry.json"

CANONICAL_MANIFEST_PATH = CONFIG_DIR / "dashboard_roadmap_canonical_aiweb_bootstrap_v1.json"

CURRENT_STAGE = {
    "stage_id": "S19AT",
    "title": "Identity Vault Profile Seed Preview / Template Repair Gate",
    "status": "ACTIVE",
    "patch": "Patch 226C",
}
NEXT_PATCH = {
    "patch": "Patch 226D",
    "title": "Identity Vault Template Repair Preview / No-Write JSON Repair Review",
    "stage_id": "S19AU",
}

CANONICAL_ENTRIES = [
    {"id": "S19AC", "status": "DONE", "title": "Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only"},
    {"id": "S19AD", "status": "DONE", "title": "Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt"},
    {"id": "S19AE", "status": "DONE", "title": "RMC Integration Freeze / No-Move Snapshot"},
    {"id": "S19AF", "status": "DONE", "title": "RMC Missing Module Install / Phase Parser, Drift Arbitrator, Echo Gate"},
    {"id": "S19AG", "status": "DONE", "title": "Forge RMC Read-Only Wrapper"},
    {"id": "S19AH", "status": "DONE", "title": "Forge RMC Runtime Preview Check"},
    {"id": "S19AI", "status": "DONE", "title": "Identity Vault Boundary Scan / Hygiene"},
    {"id": "S19AJ", "status": "DONE", "title": "Identity Vault Readiness Reconcile"},
    {"id": "S19AK", "status": "DONE", "title": "Identity Vault Read-Only Adapter"},
    {"id": "S19AL", "status": "DONE", "title": "Identity Vault Drift Auto-Confirm Safety"},
    {"id": "S19AM", "status": "DONE", "title": "Identity Vault DB Canonical Reconcile"},
    {"id": "S19AN", "status": "DONE", "title": "AI.Web Service Contracts Apply"},
    {"id": "S19AO", "status": "DONE", "title": "AI.Web Service Contracts Verify"},
    {"id": "S19AP", "status": "DONE", "title": "Forge AI.Web Read-Only Connector Commands"},
    {"id": "S19AQ", "status": "DONE", "title": "Identity Vault Operational Schema Alignment"},
    {"id": "S19AR", "status": "DONE", "title": "Identity Vault Schema Migration Apply"},
    {"id": "S19AS", "status": "DONE", "title": "Legacy Profile Migration Preview / Preserve Legacy user789"},
    {"id": "S19AT", "status": "ACTIVE", "title": "Identity Vault Profile Seed Preview / Template Repair Gate"},
    {"id": "S19AU", "status": "NEXT", "title": "Identity Vault Template Repair Preview"},
    {"id": "S19AV", "status": "FUTURE", "title": "Apply Repaired Identity Vault Templates"},
    {"id": "S19AW", "status": "FUTURE", "title": "Verify Repaired Identity Vault Templates"},
    {"id": "S19AX", "status": "FUTURE", "title": "Write Inactive Draft Identity Vault Profiles"},
    {"id": "S19AY", "status": "FUTURE", "title": "Verify Inactive Draft Identity Vault Profiles"},
    {"id": "S19AZ", "status": "FUTURE", "title": "Upgrade Full Profile Read-Only Adapter"},
    {"id": "S19BA", "status": "FUTURE", "title": "RMC Namespace Scaffold Preview"},
    {"id": "S19BB", "status": "FUTURE", "title": "RMC Namespace Scaffold Apply / Empty Namespaces Only"},
    {"id": "S19BC", "status": "FUTURE", "title": "Bootstrap Handshake Dry-Run v2 / Inactive Profile Respected"},
    {"id": "S19BD", "status": "FUTURE", "title": "Agent Activation Preflight Command"},
    {"id": "S19BE", "status": "FUTURE", "title": "Activate Gilligan as Governed Profile"},
    {"id": "S19BF", "status": "FUTURE", "title": "Gilligan Governed Handshake"},
    {"id": "S19BG", "status": "FUTURE", "title": "RMC Test Receipt Write"},
    {"id": "S19BH", "status": "FUTURE", "title": "Athena Activation and Governed Handshake"},
    {"id": "S19BI", "status": "FUTURE", "title": "Neo Activation and Governed Handshake"},
    {"id": "S19BJ", "status": "FUTURE", "title": "ProtoForge2 Discovery Scan"},
    {"id": "S19BK", "status": "FUTURE", "title": "ProtoForge2 Read-Only Connector"},
    {"id": "S19BL", "status": "FUTURE", "title": "ProtoForge2 Controlled Simulation Handshake"},
    {"id": "S19BM", "status": "FUTURE", "title": "EchoForge Discovery Scan"},
    {"id": "S19BN", "status": "FUTURE", "title": "EchoForge Read-Only Connector"},
    {"id": "S19BO", "status": "FUTURE", "title": "EchoForge Build-Intention Preview"},
    {"id": "S19BP", "status": "FUTURE", "title": "Full EchoForge → Forge → ProtoForge2 → RMC Approval Loop"},
]

EXCLUDE_DIR_NAMES = {
    ".venv", "venv", "node_modules", "__pycache__", ".git",
    "backups", "memory", "logs", ".mypy_cache", ".pytest_cache",
}

MARKERS = [
    "forge-dashboard-roadmap-status",
    "forge-dashboard-roadmap-list",
    "FORGE_DASHBOARD_ROADMAP_PANEL_READY",
    "Dashboard Roadmap Panel",
    "S19AC",
    "Patch 147",
]


def now_stamp() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def iso_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_metadata(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(stat.S_IMODE(st.st_mode)),
        "sha256": sha256_path(path) if path.is_file() else None,
    }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def iter_candidate_files(root: Path) -> List[Path]:
    candidates: List[Path] = []
    if not root.exists():
        return candidates
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]
        pdir = Path(dirpath)
        for name in filenames:
            path = pdir / name
            if path.suffix.lower() not in {".py", ".json", ".md", ".txt", ".toml", ".yaml", ".yml"}:
                continue
            try:
                if path.stat().st_size > 10_000_000:
                    continue
                text = read_text(path)
            except Exception:
                continue
            score = sum(1 for marker in MARKERS if marker in text)
            if score:
                candidates.append(path)
    return candidates


def canonical_manifest() -> Dict[str, Any]:
    return {
        "schema": "aiweb.dashboard_roadmap.canonical.v1",
        "created_by_patch": "Patch 226C.1",
        "created_at_utc": iso_now(),
        "purpose": "Canonical AI.Web bootstrap roadmap overlay after RMC, Identity Vault, service contracts, and read-only connector work advanced beyond stale Patch 147/S19AC dashboard state.",
        "current": CURRENT_STAGE,
        "next_patch": NEXT_PATCH,
        "entries": CANONICAL_ENTRIES,
        "boundaries": {
            "authority_layer": "Forge",
            "memory_layer": "RMC",
            "agent_home_layer": "Identity Vault",
            "execution_runtime_substrate": "ProtoForge2",
            "creation_simulation_request_layer": "EchoForge",
        },
        "rules": [
            "Connect by service contracts, not tangled imports.",
            "No live agent activation before inactive draft profiles and activation preflight pass.",
            "No RMC memory writes before governed handshake and receipt gate pass.",
            "No EchoForge live build without Forge patch proposal, ProtoForge2 simulation, and human approval.",
        ],
    }


def format_entries_for_report(entries: List[Dict[str, str]]) -> str:
    lines = []
    for e in entries:
        lines.append(f"  {e['id']:<5} {e['status']:<8} {e['title']}")
    return "\n".join(lines)


def replacement_block() -> str:
    return format_entries_for_report(CANONICAL_ENTRIES)


def patch_text(text: str) -> Tuple[str, List[str]]:
    changes: List[str] = []
    new = text

    replacements = {
        "Dashboard Roadmap Panel Status — Patch 147": "Dashboard Roadmap Panel Status — Patch 226C.1",
        "Dashboard Roadmap Panel List — Patch 147": "Dashboard Roadmap Panel List — Patch 226C.1",
        "Current    : S19AC — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only": "Current    : S19AT — Identity Vault Profile Seed Preview / Template Repair Gate",
        "Next patch : Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt": "Next patch : Patch 226D — Identity Vault Template Repair Preview / No-Write JSON Repair Review",
        "S19AC ACTIVE   Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only": "S19AC DONE     Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only",
        "S19AD NEXT     Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt": "S19AD DONE     Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt",
    }
    for old, repl in replacements.items():
        if old in new:
            new = new.replace(old, repl)
            changes.append(f"literal_replace::{old[:72]}")

    # If the plain-text roadmap block is present and new canonical entries are not, insert after S19AD.
    if "S19AE DONE     RMC Integration Freeze / No-Move Snapshot" not in new:
        pattern = re.compile(r"(?P<line>\s*S19AD\s+DONE\s+Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt)(?P<trail>\n)")
        m = pattern.search(new)
        if m:
            insert_lines = []
            for e in CANONICAL_ENTRIES:
                if e["id"] in {"S19AC", "S19AD"}:
                    continue
                insert_lines.append(f"  {e['id']:<5} {e['status']:<8} {e['title']}")
            new = new[:m.end()] + "\n".join(insert_lines) + "\n" + new[m.end():]
            changes.append("insert_canonical_s19ae_forward_plaintext_block")

    # If dashboard source uses compact dict/list strings, update known stale labels where possible.
    compact_replacements = {
        '"current": "S19AC"': '"current": "S19AT"',
        "'current': 'S19AC'": "'current': 'S19AT'",
        '"next_patch": "Patch 184"': '"next_patch": "Patch 226D"',
        "'next_patch': 'Patch 184'": "'next_patch': 'Patch 226D'",
        '"Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only"': '"Identity Vault Profile Seed Preview / Template Repair Gate"',
        "'Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only'": "'Identity Vault Profile Seed Preview / Template Repair Gate'",
    }
    for old, repl in compact_replacements.items():
        if old in new:
            new = new.replace(old, repl)
            changes.append(f"compact_replace::{old}")

    return new, changes


def backup_file(path: Path, stamp: str) -> Path:
    rel = path.relative_to(FORGE_ROOT)
    dest = BACKUP_ROOT / stamp / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    return dest


def compile_if_python(path: Path) -> Dict[str, Any]:
    if path.suffix != ".py":
        return {"attempted": False, "ok": True}
    try:
        py_compile.compile(str(path), doraise=True)
        return {"attempted": True, "ok": True}
    except Exception as exc:
        return {"attempted": True, "ok": False, "error": repr(exc), "traceback": traceback.format_exc()[-2000:]}


def restore_backup(target: Path, backup: Path) -> None:
    shutil.copy2(backup, target)


def main() -> int:
    stamp = now_stamp()
    run_dir = MEMORY_ROOT / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    before_env = stat_metadata(IDENTITY_ENV)
    before_canonical_db = stat_metadata(CANONICAL_DB)
    before_legacy_db = stat_metadata(LEGACY_DB)
    before_registry = stat_metadata(TOOL_REGISTRY)

    report: Dict[str, Any] = {
        "timestamp": stamp,
        "boundary": "dashboard roadmap canonicalization; no Identity Vault/RMC DB/memory writes; no agent activation",
        "current_before_from_user_terminal": {
            "panel_patch": "Patch 147",
            "current": "S19AC — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only",
            "next_patch": "Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt",
        },
        "canonical_current": CURRENT_STAGE,
        "canonical_next_patch": NEXT_PATCH,
        "canonical_entries": CANONICAL_ENTRIES,
        "candidate_files": [],
        "changed_files": [],
        "backups": [],
        "compile_checks": [],
        "manifest_path": str(CANONICAL_MANIFEST_PATH),
        "findings": [],
        "safety": {},
    }

    manifest = canonical_manifest()
    before_manifest = stat_metadata(CANONICAL_MANIFEST_PATH)
    write_text(CANONICAL_MANIFEST_PATH, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    after_manifest = stat_metadata(CANONICAL_MANIFEST_PATH)
    report["manifest_written"] = True
    report["manifest_before"] = before_manifest
    report["manifest_after"] = after_manifest

    candidates = iter_candidate_files(FORGE_ROOT)
    scored_candidates = []
    for path in candidates:
        text = read_text(path)
        score = sum(1 for marker in MARKERS if marker in text)
        scored_candidates.append({
            "path": str(path),
            "score": score,
            "sha16": (sha256_path(path) or "")[:16],
            "markers": [m for m in MARKERS if m in text],
        })
    scored_candidates.sort(key=lambda x: (-x["score"], x["path"]))
    report["candidate_files"] = scored_candidates[:25]

    # Prefer files that contain the dashboard command names/status markers.
    target_paths: List[Path] = []
    for item in scored_candidates:
        p = Path(item["path"])
        markers = set(item["markers"])
        if {"forge-dashboard-roadmap-status", "forge-dashboard-roadmap-list"} & markers or "FORGE_DASHBOARD_ROADMAP_PANEL_READY" in markers:
            target_paths.append(p)
    # Add a fallback if only S19AC/Patch 147 file found and it looks likely.
    if not target_paths and scored_candidates:
        p = Path(scored_candidates[0]["path"])
        if scored_candidates[0]["score"] >= 2:
            target_paths.append(p)

    changed_any = False
    for path in target_paths[:3]:
        before_text = read_text(path)
        after_text, changes = patch_text(before_text)
        if after_text == before_text:
            report["compile_checks"].append({"path": str(path), "attempted": False, "ok": True, "note": "no text changes matched"})
            continue
        backup = backup_file(path, stamp)
        report["backups"].append({"source": str(path), "backup": str(backup)})
        before_hash = sha256_path(path)
        write_text(path, after_text)
        compile_result = compile_if_python(path)
        compile_result["path"] = str(path)
        report["compile_checks"].append(compile_result)
        if not compile_result.get("ok"):
            restore_backup(path, backup)
            report["changed_files"].append({
                "path": str(path),
                "changed": False,
                "restored": True,
                "reason": "compile failed after roadmap edit",
                "changes_attempted": changes,
            })
            continue
        after_hash = sha256_path(path)
        report["changed_files"].append({
            "path": str(path),
            "changed": True,
            "restored": False,
            "before_sha16": (before_hash or "")[:16],
            "after_sha16": (after_hash or "")[:16],
            "changes": changes,
        })
        changed_any = True

    after_env = stat_metadata(IDENTITY_ENV)
    after_canonical_db = stat_metadata(CANONICAL_DB)
    after_legacy_db = stat_metadata(LEGACY_DB)
    after_registry = stat_metadata(TOOL_REGISTRY)

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before_env == after_env,
        "canonical_db_sha_unchanged": before_canonical_db.get("sha256") == after_canonical_db.get("sha256"),
        "legacy_db_sha_unchanged": before_legacy_db.get("sha256") == after_legacy_db.get("sha256"),
        "tool_registry_sha_unchanged": before_registry.get("sha256") == after_registry.get("sha256"),
        "identity_vault_db_write_performed": False,
        "rmc_memory_write_performed": False,
        "agent_identity_activation_performed": False,
    }
    report["safety"] = safety

    if changed_any:
        report["findings"].append({"level": "INFO", "code": "ROADMAP_SOURCE_UPDATED", "message": "At least one Forge dashboard roadmap source file was backed up and updated."})
    else:
        report["findings"].append({"level": "WARN", "code": "ROADMAP_SOURCE_NOT_UPDATED", "message": "Canonical manifest was written, but no roadmap source file matched safe update patterns."})
    report["findings"].append({"level": "INFO", "code": "CANONICAL_MANIFEST_WRITTEN", "message": str(CANONICAL_MANIFEST_PATH)})

    safety_ok = all(safety.values())
    compile_ok = all(item.get("ok", False) for item in report["compile_checks"]) if report["compile_checks"] else True
    verdict = "PASS" if changed_any and safety_ok and compile_ok else ("WARN" if safety_ok and compile_ok else "FAIL")
    report["verdict"] = verdict

    md = []
    md.append("# Forge Dashboard Roadmap Patch 226C.1 Canonicalization\n")
    md.append(f"Timestamp: `{stamp}`")
    md.append(f"Verdict: **{verdict}**\n")
    md.append("## Boundary")
    md.append("- This patch canonicalizes the dashboard roadmap state after the AI.Web bootstrap work moved beyond stale Patch 147/S19AC tracking.")
    md.append("- It may write a canonical roadmap manifest under Forge config and reports under Forge memory.")
    md.append("- It may update a Forge dashboard roadmap source file only after backup and only if stale roadmap markers are found.")
    md.append("- It does not write Identity Vault databases, RMC memory, `.env`, agent memory, AI.Web wrappers, or the Forge tool registry.\n")
    md.append("## Inventory From Current Dashboard Output")
    md.append("- panel patch: `Patch 147`")
    md.append("- stale current: `S19AC — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only`")
    md.append("- stale next patch: `Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt`\n")
    md.append("## Canonical Roadmap State")
    md.append(f"- current: `{CURRENT_STAGE['stage_id']} — {CURRENT_STAGE['title']}`")
    md.append(f"- next patch: `{NEXT_PATCH['patch']} — {NEXT_PATCH['title']}`")
    md.append(f"- canonical manifest: `{CANONICAL_MANIFEST_PATH}`\n")
    md.append("## Canonical AI.Web Runtime Entries")
    md.append("```text")
    md.append(format_entries_for_report(CANONICAL_ENTRIES))
    md.append("```\n")
    md.append("## Candidate Files")
    if scored_candidates:
        for item in scored_candidates[:10]:
            md.append(f"- `{item['path']}` score=`{item['score']}` markers=`{', '.join(item['markers'])}`")
    else:
        md.append("- none found")
    md.append("")
    md.append("## Changed Files")
    if report["changed_files"]:
        for item in report["changed_files"]:
            md.append(f"- `{item['path']}` changed=`{item['changed']}` restored=`{item.get('restored', False)}` changes=`{len(item.get('changes', []))}`")
    else:
        md.append("- none")
    md.append("")
    md.append("## Backups")
    if report["backups"]:
        for item in report["backups"]:
            md.append(f"- `{item['source']}` → `{item['backup']}`")
    else:
        md.append("- none")
    md.append("")
    md.append("## Compile Checks")
    if report["compile_checks"]:
        for item in report["compile_checks"]:
            md.append(f"- `{item.get('path')}` attempted=`{item.get('attempted')}` ok=`{item.get('ok')}`")
    else:
        md.append("- no source file compile checks were needed")
    md.append("")
    md.append("## Safety Checks")
    for key, value in safety.items():
        md.append(f"- `{key}`: `{value}`")
    md.append("")
    md.append("## Findings")
    for finding in report["findings"]:
        md.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    md.append("")
    md.append("## Next Safe Step")
    md.append("Run `forge-dashboard-roadmap-status` and `forge-dashboard-roadmap-list` inside Forge. If the command output updates, proceed to Patch 226D Identity Vault Template Repair Preview. If the command output is still stale, use this report to patch the exact located dashboard source in the next apply patch.")

    report_path = run_dir / f"{stamp}_dashboard_roadmap_patch226c1_canonicalization.json"
    md_path = run_dir / f"{stamp}_dashboard_roadmap_patch226c1_canonicalization.md"
    latest_json = MEMORY_ROOT / "latest_dashboard_roadmap_patch226c1_canonicalization.json"
    latest_md = MEMORY_ROOT / "latest_dashboard_roadmap_patch226c1_canonicalization.md"
    write_text(report_path, json.dumps(report, indent=2, sort_keys=True) + "\n")
    write_text(md_path, "\n".join(md) + "\n")
    shutil.copy2(report_path, latest_json)
    shutil.copy2(md_path, latest_md)

    print("Forge Dashboard Roadmap Patch 226C.1 canonicalization complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Manifest: {CANONICAL_MANIFEST_PATH}")
    print(f"Verdict: {verdict}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

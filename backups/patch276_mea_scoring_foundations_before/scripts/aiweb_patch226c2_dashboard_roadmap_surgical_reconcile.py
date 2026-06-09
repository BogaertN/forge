#!/usr/bin/env python3
"""
Patch 226C.2 — Forge Dashboard Roadmap Surgical Reconcile

Purpose:
  Correct the Forge dashboard/build roadmap source after Patch 226C.1 and the
  built-in forge-roadmap-* commands proved insufficient to update Current/Next.

Boundary:
  - Modifies only /home/nic/forge/main.py after backup.
  - Writes reports only under /home/nic/forge/memory/dashboard_roadmap_patch226c2_surgical_reconcile_v1/.
  - Does not touch Identity Vault databases, .env, RMC memory, AI.Web wrappers,
    agent memory, or tool_registry.json.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
MAIN_PY = FORGE_ROOT / "main.py"
TOOL_REGISTRY = FORGE_ROOT / "config" / "tool_registry.json"
IDENTITY_ROOT = HOME / "identity-vault"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
ENV_FILE = IDENTITY_ROOT / ".env"
REPORT_ROOT = FORGE_ROOT / "memory" / "dashboard_roadmap_patch226c2_surgical_reconcile_v1"
BACKUP_ROOT = FORGE_ROOT / "backups" / "patch226c2_dashboard_roadmap_surgical_reconcile_before"

CANONICAL_CURRENT = "S19AT — Identity Vault Profile Seed Preview / Template Repair Gate"
CANONICAL_NEXT = "Patch 226D — Identity Vault Template Repair Preview / No-Write JSON Repair Review"

DASHBOARD_LINES = [
    ("S19AC", "DONE", "Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only"),
    ("S19AD", "DONE", "Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt"),
    ("S19AE", "DONE", "RMC Integration Freeze / No-Move Snapshot"),
    ("S19AF", "DONE", "RMC Missing Module Install / Phase Parser, Drift Arbitrator, Echo Gate"),
    ("S19AG", "DONE", "Forge RMC Read-Only Wrapper"),
    ("S19AH", "DONE", "Forge RMC Runtime Preview Check"),
    ("S19AI", "DONE", "Identity Vault Boundary Scan / Hygiene"),
    ("S19AJ", "DONE", "Identity Vault Readiness Reconcile"),
    ("S19AK", "DONE", "Identity Vault Read-Only Adapter"),
    ("S19AL", "DONE", "Identity Vault Drift Auto-Confirm Safety"),
    ("S19AM", "DONE", "Identity Vault DB Canonical Reconcile"),
    ("S19AN", "DONE", "AI.Web Service Contracts Apply"),
    ("S19AO", "DONE", "AI.Web Service Contracts Verify"),
    ("S19AP", "DONE", "Forge AI.Web Read-Only Connector Commands"),
    ("S19AQ", "DONE", "Identity Vault Operational Schema Alignment"),
    ("S19AR", "DONE", "Identity Vault Schema Migration Apply"),
    ("S19AS", "DONE", "Legacy Profile Migration Preview / Preserve Legacy user789"),
    ("S19AT", "ACTIVE", "Identity Vault Profile Seed Preview / Template Repair Gate"),
    ("S19AU", "NEXT", "Identity Vault Template Repair Preview"),
    ("S19AV", "FUTURE", "Apply Repaired Identity Vault Templates"),
    ("S19AW", "FUTURE", "Verify Repaired Identity Vault Templates"),
    ("S19AX", "FUTURE", "Write Inactive Draft Identity Vault Profiles"),
    ("S19AY", "FUTURE", "Verify Inactive Draft Identity Vault Profiles"),
    ("S19AZ", "FUTURE", "Upgrade Full Profile Read-Only Adapter"),
    ("S19BA", "FUTURE", "RMC Namespace Scaffold Preview"),
    ("S19BB", "FUTURE", "RMC Namespace Scaffold Apply / Empty Namespaces Only"),
    ("S19BC", "FUTURE", "Bootstrap Handshake Dry-Run v2 / Inactive Profile Respected"),
    ("S19BD", "FUTURE", "Agent Activation Preflight Command"),
    ("S19BE", "FUTURE", "Activate Gilligan as Governed Profile"),
    ("S19BF", "FUTURE", "Gilligan Governed Handshake"),
    ("S19BG", "FUTURE", "RMC Test Receipt Write"),
    ("S19BH", "FUTURE", "Athena Activation and Governed Handshake"),
    ("S19BI", "FUTURE", "Neo Activation and Governed Handshake"),
    ("S19BJ", "FUTURE", "ProtoForge2 Discovery Scan"),
    ("S19BK", "FUTURE", "ProtoForge2 Read-Only Connector"),
    ("S19BL", "FUTURE", "ProtoForge2 Controlled Simulation Handshake"),
    ("S19BM", "FUTURE", "EchoForge Discovery Scan"),
    ("S19BN", "FUTURE", "EchoForge Read-Only Connector"),
    ("S19BO", "FUTURE", "EchoForge Build-Intention Preview"),
    ("S19BP", "FUTURE", "Full EchoForge to Forge to ProtoForge2 to RMC Approval Loop"),
]


def now_stamp() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_metadata(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(stat.S_IMODE(st.st_mode)),
    }


def copy_backup(src: Path, backup_dir: Path) -> Path:
    rel = src.relative_to(FORGE_ROOT) if src.is_relative_to(FORGE_ROOT) else src.name
    dst = backup_dir / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def replace_all_patterns(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    out = text

    replacements = {
        "Dashboard Roadmap Panel Status — Patch 147": "Dashboard Roadmap Panel Status — Patch 226C.2",
        "Dashboard Roadmap Panel Status — Patch 226C.1": "Dashboard Roadmap Panel Status — Patch 226C.2",
        "Dashboard Roadmap Panel List — Patch 147": "Dashboard Roadmap Panel List — Patch 226C.2",
        "Dashboard Roadmap Panel List — Patch 226C.1": "Dashboard Roadmap Panel List — Patch 226C.2",
        "Dashboard Roadmap Panel Build — Patch 147": "Dashboard Roadmap Panel Build — Patch 226C.2",
        "Forge Roadmap Status — Build Sequence / Patch 146": "Forge Roadmap Status — Build Sequence / Patch 226C.2",
        "Current    : S19AC — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only": f"Current    : {CANONICAL_CURRENT}",
        "Current    : S19AC — Identity Vault Profile Seed Preview / Template Repair Gate": f"Current    : {CANONICAL_CURRENT}",
        "Current      : S19AC — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only": f"Current      : {CANONICAL_CURRENT}",
        "Current : S19AC — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only": f"Current : {CANONICAL_CURRENT}",
        "Current : S19AC — Identity Vault Profile Seed Preview / Template Repair Gate": f"Current : {CANONICAL_CURRENT}",
        "Next patch : Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt": f"Next patch : {CANONICAL_NEXT}",
        "Next         : Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt": f"Next         : {CANONICAL_NEXT}",
        "Next    : Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt": f"Next    : {CANONICAL_NEXT}",
    }

    for old, new in replacements.items():
        count = out.count(old)
        if count:
            out = out.replace(old, new)
            changes.append(f"literal_replace:{old[:60]} count={count}")

    # Dashboard list format: two leading spaces, ID, two spaces, STATUS, spaces, title
    dashboard_block = "\n".join(
        f"  {sid} {status:<8} {title}" for sid, status, title in DASHBOARD_LINES
    )
    # Build sequence / roadmap status format: four spaces, ID [STATUS] title
    bracket_block = "\n".join(
        f"    {sid} [{status}] {title}" for sid, status, title in DASHBOARD_LINES
    )

    # Replace dashboard list region from S19AC through S19AD or existing inserted range.
    out2, n = re.subn(
        r"(?m)^  S19AC\s+.*(?:\n  S19A[D-Z]\s+.*|\n  S19B[A-P]\s+.*)*",
        dashboard_block,
        out,
        count=1,
    )
    if n:
        out = out2
        changes.append("regex_replace:dashboard_list_S19AC_forward")

    # Replace roadmap status region from S19AC through S19AD or existing inserted range.
    out2, n = re.subn(
        r"(?m)^    S19AC\s+\[.*(?:\n    S19A[D-Z]\s+\[.*|\n    S19B[A-P]\s+\[.*)*",
        bracket_block,
        out,
        count=1,
    )
    if n:
        out = out2
        changes.append("regex_replace:roadmap_status_S19AC_forward")

    return out, changes


def write_report(report: dict, run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    latest_md = REPORT_ROOT / "latest_dashboard_roadmap_patch226c2_surgical_reconcile.md"
    latest_json = REPORT_ROOT / "latest_dashboard_roadmap_patch226c2_surgical_reconcile.json"
    json_path = run_dir / f"{report['timestamp']}_dashboard_roadmap_patch226c2_surgical_reconcile.json"
    md_path = run_dir / f"{report['timestamp']}_dashboard_roadmap_patch226c2_surgical_reconcile.md"

    md = []
    md.append("# Forge Dashboard Roadmap Patch 226C.2 Surgical Reconcile\n")
    md.append(f"Timestamp: `{report['timestamp']}`")
    md.append(f"Verdict: **{report['verdict']}**\n")
    md.append("## Boundary")
    md.append("- Modifies only `/home/nic/forge/main.py` after backup.")
    md.append("- Writes reports only under Forge memory.")
    md.append("- Does not write Identity Vault databases, RMC memory, `.env`, agent memory, AI.Web wrappers, or the Forge tool registry.\n")
    md.append("## Target State")
    md.append(f"- Current: `{CANONICAL_CURRENT}`")
    md.append(f"- Next patch: `{CANONICAL_NEXT}`")
    md.append("- S19AC through S19AS: `DONE`")
    md.append("- S19AT: `ACTIVE`")
    md.append("- S19AU: `NEXT`")
    md.append("- S19AV through S19BP: `FUTURE`\n")
    md.append("## Files")
    md.append(f"- main.py exists: `{report['main_exists']}`")
    md.append(f"- backup: `{report.get('backup_path')}`")
    md.append(f"- changed: `{report['changed']}`")
    md.append(f"- changes detected: `{len(report['changes'])}`")
    for change in report["changes"]:
        md.append(f"  - `{change}`")
    md.append("")
    md.append("## Compile Check")
    md.append(f"- attempted: `{report['compile']['attempted']}`")
    md.append(f"- ok: `{report['compile']['ok']}`")
    md.append(f"- returncode: `{report['compile']['returncode']}`")
    if report['compile'].get('stderr_tail'):
        md.append("```text")
        md.append(report['compile']['stderr_tail'])
        md.append("```")
    md.append("")
    md.append("## Static Verification")
    for k, v in report["static_verification"].items():
        md.append(f"- `{k}`: `{v}`")
    md.append("")
    md.append("## Safety Checks")
    for k, v in report["safety"].items():
        md.append(f"- `{k}`: `{v}`")
    md.append("")
    md.append("## Findings")
    for finding in report["findings"]:
        md.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    md.append("")
    md.append("## Next Safe Step")
    md.append("Run Forge and check `forge-dashboard-roadmap-status`, `forge-dashboard-roadmap-list`, and `forge-roadmap-status`. If any output is stale, restore from the backup listed above and stop.")
    md_text = "\n".join(md) + "\n"

    for path in (json_path, latest_json):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    for path in (md_path, latest_md):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md_text, encoding="utf-8")


def main() -> int:
    timestamp = now_stamp()
    run_dir = REPORT_ROOT / timestamp
    backup_dir = BACKUP_ROOT / timestamp
    report = {
        "timestamp": timestamp,
        "verdict": "FAIL",
        "main_exists": MAIN_PY.exists(),
        "backup_path": None,
        "changed": False,
        "changes": [],
        "compile": {"attempted": False, "ok": False, "returncode": None},
        "static_verification": {},
        "safety": {},
        "findings": [],
    }

    before_hashes = {
        "main": sha256(MAIN_PY),
        "tool_registry": sha256(TOOL_REGISTRY),
        "canonical_db": sha256(CANONICAL_DB),
        "legacy_db": sha256(LEGACY_DB),
    }
    before_stats = {"env": stat_metadata(ENV_FILE)}

    try:
        if not MAIN_PY.exists():
            report["findings"].append({"level": "FAIL", "code": "MAIN_PY_MISSING", "message": str(MAIN_PY)})
            return 1

        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = copy_backup(MAIN_PY, backup_dir)
        report["backup_path"] = str(backup_path)

        original = MAIN_PY.read_text(encoding="utf-8")
        patched, changes = replace_all_patterns(original)
        report["changes"] = changes
        report["changed"] = patched != original

        if not changes or patched == original:
            report["findings"].append({"level": "FAIL", "code": "NO_SOURCE_CHANGES", "message": "No roadmap source markers were changed; stop before proceeding."})
            return 1

        MAIN_PY.write_text(patched, encoding="utf-8")

        compile_proc = subprocess.run([sys.executable, "-m", "py_compile", str(MAIN_PY)], text=True, capture_output=True)
        report["compile"] = {
            "attempted": True,
            "ok": compile_proc.returncode == 0,
            "returncode": compile_proc.returncode,
            "stdout_tail": compile_proc.stdout[-2000:],
            "stderr_tail": compile_proc.stderr[-4000:],
        }
        if compile_proc.returncode != 0:
            shutil.copy2(backup_path, MAIN_PY)
            report["findings"].append({"level": "FAIL", "code": "COMPILE_FAILED_RESTORED", "message": "main.py failed compile and was restored from backup."})
            return 1

        after = MAIN_PY.read_text(encoding="utf-8")
        static = {
            "canonical_current_present": CANONICAL_CURRENT in after,
            "canonical_next_present": CANONICAL_NEXT in after,
            "s19ac_done_present": "S19AC DONE" in after or "S19AC [DONE]" in after,
            "s19at_active_present": "S19AT ACTIVE" in after or "S19AT [ACTIVE]" in after,
            "s19au_next_present": "S19AU NEXT" in after or "S19AU [NEXT]" in after,
            "s19bp_future_present": "S19BP FUTURE" in after or "S19BP [FUTURE]" in after,
            "patch_label_226c2_present": "Patch 226C.2" in after,
        }
        report["static_verification"] = static

        after_hashes = {
            "main": sha256(MAIN_PY),
            "tool_registry": sha256(TOOL_REGISTRY),
            "canonical_db": sha256(CANONICAL_DB),
            "legacy_db": sha256(LEGACY_DB),
        }
        after_stats = {"env": stat_metadata(ENV_FILE)}
        safety = {
            "tool_registry_sha_unchanged": before_hashes["tool_registry"] == after_hashes["tool_registry"],
            "canonical_db_sha_unchanged": before_hashes["canonical_db"] == after_hashes["canonical_db"],
            "legacy_db_sha_unchanged": before_hashes["legacy_db"] == after_hashes["legacy_db"],
            "env_stat_unchanged": before_stats["env"] == after_stats["env"],
            "identity_vault_db_write_performed": before_hashes["canonical_db"] != after_hashes["canonical_db"] or before_hashes["legacy_db"] != after_hashes["legacy_db"],
            "forge_tool_registry_modified": before_hashes["tool_registry"] != after_hashes["tool_registry"],
            "main_py_modified": before_hashes["main"] != after_hashes["main"],
        }
        report["safety"] = safety

        if all(static.values()) and safety["tool_registry_sha_unchanged"] and safety["canonical_db_sha_unchanged"] and safety["legacy_db_sha_unchanged"] and safety["env_stat_unchanged"]:
            report["verdict"] = "PASS"
            report["findings"].append({"level": "INFO", "code": "ROADMAP_SOURCE_SURGICALLY_RECONCILED", "message": "main.py contains canonical roadmap current/next and S19AT/S19AU/S19BP markers."})
            return 0
        else:
            report["verdict"] = "FAIL"
            report["findings"].append({"level": "FAIL", "code": "STATIC_OR_SAFETY_VERIFICATION_FAILED", "message": "Static verification or safety checks failed. Review before running Forge."})
            return 1
    finally:
        # Ensure safety is populated even on early returns.
        if not report.get("safety"):
            after_hashes = {
                "tool_registry": sha256(TOOL_REGISTRY),
                "canonical_db": sha256(CANONICAL_DB),
                "legacy_db": sha256(LEGACY_DB),
            }
            after_stats = {"env": stat_metadata(ENV_FILE)}
            report["safety"] = {
                "tool_registry_sha_unchanged": before_hashes["tool_registry"] == after_hashes["tool_registry"],
                "canonical_db_sha_unchanged": before_hashes["canonical_db"] == after_hashes["canonical_db"],
                "legacy_db_sha_unchanged": before_hashes["legacy_db"] == after_hashes["legacy_db"],
                "env_stat_unchanged": before_stats["env"] == after_stats["env"],
            }
        write_report(report, run_dir)
        print("Forge Dashboard Roadmap Patch 226C.2 surgical reconcile complete.")
        print(f"Run directory: {run_dir}")
        print(f"Report: {REPORT_ROOT / 'latest_dashboard_roadmap_patch226c2_surgical_reconcile.md'}")
        print(f"Verdict: {report['verdict']}")


if __name__ == "__main__":
    raise SystemExit(main())

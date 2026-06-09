# identity_vault_patch218_verify.py — Verify Forge Identity Vault read-only adapter
# Purpose: verify adapter import, contract validation, DB read-only access, and no mutation evidence.

from __future__ import annotations

import datetime as _dt
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

FORGE_ROOT = Path.home() / "forge"
ADAPTER_PATH = FORGE_ROOT / "agents" / "forge" / "identity_vault_adapter.py"
IDENTITY_ROOT = Path.home() / "identity-vault"
CONTRACT_PATH = IDENTITY_ROOT / "service_contracts" / "identity_vault_readonly_service_contract.draft.json"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
ENV_PATH = IDENTITY_ROOT / ".env"
OUT_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch218_readonly_adapter_v1"


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_snapshot(paths: List[Path]) -> Dict[str, Dict[str, Any]]:
    snap: Dict[str, Dict[str, Any]] = {}
    for path in paths:
        if path.exists():
            st = path.stat()
            snap[str(path)] = {
                "exists": True,
                "size": st.st_size,
                "mtime_ns": st.st_mtime_ns,
                "sha256": sha256_file(path) if path.suffix in {".db", ".json"} else None,
            }
        else:
            snap[str(path)] = {"exists": False}
    return snap


def load_adapter_module():
    spec = importlib.util.spec_from_file_location("forge_identity_vault_adapter_patch218", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to create module spec for Identity Vault adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_reports(report: Dict[str, Any], run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    ts = report["timestamp"]
    json_path = run_dir / f"{ts}_identity_vault_patch218_readonly_adapter.json"
    md_path = run_dir / f"{ts}_identity_vault_patch218_readonly_adapter.md"
    latest_json = OUT_ROOT / "latest_identity_vault_patch218_readonly_adapter.json"
    latest_md = OUT_ROOT / "latest_identity_vault_patch218_readonly_adapter.md"

    json_text = json.dumps(report, indent=2, sort_keys=True)
    json_path.write_text(json_text + "\n", encoding="utf-8")
    latest_json.write_text(json_text + "\n", encoding="utf-8")

    lines: List[str] = []
    lines.append("# Identity Vault Patch 218 Read-Only Adapter Verification")
    lines.append("")
    lines.append(f"Timestamp: `{ts}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    for item in report["boundary_notes"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Adapter Checks")
    for key, value in report["adapter_checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Contract Summary")
    contract = report["adapter_status"].get("contract", {})
    for key, value in contract.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Package Metadata")
    package = report["adapter_status"].get("package", {})
    for key, value in package.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Database Read-Only Summary")
    database = report["adapter_status"].get("database", {})
    lines.append(f"- path: `{database.get('path')}`")
    lines.append(f"- opened_readonly: `{database.get('opened_readonly')}`")
    lines.append(f"- tables: `{', '.join(database.get('tables', []))}`")
    for table, count in database.get("row_counts", {}).items():
        lines.append(f"  - `{table}` rows: `{count}`")
    lines.append("")
    lines.append("## Identity Metadata Preview")
    preview = report["adapter_status"].get("identity_metadata_preview", {})
    for table, value in preview.items():
        lines.append(f"- `{table}` ok=`{value.get('ok')}` safe_columns=`{value.get('safe_columns')}` returned=`{value.get('row_count_returned')}`")
    lines.append("")
    lines.append("## No-Mutation Check")
    for key, value in report["no_mutation_check"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Findings")
    for finding in report["findings"]:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("Create a Forge-side registration readiness scan for Identity Vault read-only preview functions. Do not activate agent identities yet.")
    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")


def main() -> int:
    ts = _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")
    run_dir = OUT_ROOT / ts
    before = stat_snapshot([CONTRACT_PATH, CANONICAL_DB, LEGACY_DB, ENV_PATH])
    findings: List[Dict[str, str]] = []
    adapter_checks: Dict[str, Any] = {
        "adapter_exists": ADAPTER_PATH.exists(),
        "contract_exists": CONTRACT_PATH.exists(),
        "canonical_db_exists": CANONICAL_DB.exists(),
    }
    adapter_status: Dict[str, Any] = {}
    import_ok = False
    status_ok = False
    env_content_read = False
    db_write_performed = False
    identity_activation_performed = False

    try:
        module = load_adapter_module()
        import_ok = True
        adapter_checks["import_ok"] = True
        adapter_checks["read_only_constant"] = bool(getattr(module, "READ_ONLY", False))
        adapter_checks["adapter_version"] = getattr(module, "ADAPTER_VERSION", "missing")
        adapter_status = module.get_identity_vault_status()
        status_ok = bool(adapter_status.get("ok"))
        env_content_read = bool(adapter_status.get("env_secret_values_read"))
        db_write_performed = bool(adapter_status.get("database_write_performed"))
        identity_activation_performed = bool(adapter_status.get("agent_identity_activation_performed"))
    except Exception as exc:  # report full type but not noisy traceback
        adapter_checks["import_or_status_error"] = f"{type(exc).__name__}: {exc}"
        findings.append({"level": "ERROR", "code": "IV_ADAPTER_VERIFY_EXCEPTION", "message": str(exc)})

    after = stat_snapshot([CONTRACT_PATH, CANONICAL_DB, LEGACY_DB, ENV_PATH])
    no_mutation = before == after
    no_mutation_check = {
        "contract_db_env_legacy_snapshots_unchanged": no_mutation,
        "env_secret_values_read": env_content_read,
        "database_write_performed": db_write_performed,
        "agent_identity_activation_performed": identity_activation_performed,
    }

    if import_ok and status_ok:
        findings.append({"level": "INFO", "code": "IV_READONLY_ADAPTER_OK", "message": "Adapter imported and returned contract-bound read-only status."})
    if no_mutation:
        findings.append({"level": "INFO", "code": "IV_NO_MUTATION_EVIDENCE", "message": "Contract, databases, legacy DB, and .env metadata/hash snapshots were unchanged."})
    if env_content_read:
        findings.append({"level": "ERROR", "code": "IV_ENV_READ_FORBIDDEN", "message": ".env secret values appear to have been read."})
    if db_write_performed:
        findings.append({"level": "ERROR", "code": "IV_DB_WRITE_FORBIDDEN", "message": "Adapter reported a database write."})
    if identity_activation_performed:
        findings.append({"level": "ERROR", "code": "IV_IDENTITY_ACTIVATION_FORBIDDEN", "message": "Adapter reported identity activation."})

    verdict = "PASS" if import_ok and status_ok and no_mutation and not env_content_read and not db_write_performed and not identity_activation_performed else "FAIL"

    report: Dict[str, Any] = {
        "timestamp": ts,
        "verdict": verdict,
        "boundary_notes": [
            "This verification imports Forge's Identity Vault adapter only.",
            "The adapter is read-only and unregistered in Forge's tool surface.",
            "No .env secret values are read.",
            "No Identity Vault database writes are performed.",
            "No agent identity activation is performed.",
        ],
        "paths": {
            "adapter": str(ADAPTER_PATH),
            "contract": str(CONTRACT_PATH),
            "canonical_db": str(CANONICAL_DB),
            "legacy_db": str(LEGACY_DB),
        },
        "adapter_checks": adapter_checks,
        "adapter_status": adapter_status,
        "no_mutation_check": no_mutation_check,
        "before_snapshot": before,
        "after_snapshot": after,
        "findings": findings,
    }
    write_reports(report, run_dir)
    print("Identity Vault Patch 218 read-only adapter verification complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {OUT_ROOT / 'latest_identity_vault_patch218_readonly_adapter.md'}")
    print(f"JSON report: {OUT_ROOT / 'latest_identity_vault_patch218_readonly_adapter.json'}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

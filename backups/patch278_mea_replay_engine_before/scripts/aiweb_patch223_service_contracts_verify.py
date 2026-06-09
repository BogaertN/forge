#!/usr/bin/env python3
# identity: aiweb_patch223_service_contracts_verify.py
# purpose: Verify the five AI.Web service contract draft files before read-only connector commands are added.
# boundary: Read-only against AI.Web/Forge/Identity Vault/RMC service files except for writing this report under Forge memory.

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple


PATCH_ID = "patch223_aiweb_service_contracts_verify"
REPORT_DIR_NAME = "aiweb_patch223_service_contracts_verify_v1"

REQUIRED_CONTRACTS = [
    "forge.contract.json",
    "rmc.contract.json",
    "identity_vault.contract.json",
    "protoforge2.contract.json",
    "echoforge.contract.json",
]

REQUIRED_FIELDS = [
    "name",
    "role",
    "allowed_reads",
    "allowed_writes",
    "forbidden_writes",
    "api_or_cli_commands_exposed",
    "audit_log_path",
    "test_command",
    "startup_command",
    "shutdown_command",
    "health_check_command",
    "owner_authority",
]

LIST_FIELDS = {
    "allowed_reads",
    "allowed_writes",
    "forbidden_writes",
    "api_or_cli_commands_exposed",
}

EXPECTED_ROLE_KEYWORDS = {
    "forge.contract.json": ["verify", "govern", "forge"],
    "rmc.contract.json": ["memory", "rmc", "manifest", "echo"],
    "identity_vault.contract.json": ["identity", "permissions", "agent"],
    "protoforge2.contract.json": ["execute", "simulate", "runtime", "protoforge"],
    "echoforge.contract.json": ["request", "tools", "simulation", "echoforge"],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_read_json(path: Path) -> Tuple[bool, Dict[str, Any], str]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False, {}, "json root is not an object"
        return True, data, ""
    except Exception as exc:
        return False, {}, f"{type(exc).__name__}: {exc}"


def value_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return True  # empty list is allowed for allowed_writes in read-only/planned services
    return True


def validate_contract(filename: str, path: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "filename": filename,
        "path": str(path),
        "exists": path.exists(),
        "json_ok": False,
        "missing_fields": [],
        "empty_required_fields": [],
        "list_field_type_errors": [],
        "role_keyword_hint_ok": False,
        "sha_before": None,
        "sha_after": None,
        "unchanged": None,
        "ok": False,
        "error": "",
        "summary": {},
    }

    if not path.exists():
        result["error"] = "missing contract file"
        return result

    before = sha256_file(path)
    result["sha_before"] = before

    json_ok, data, error = safe_read_json(path)
    result["json_ok"] = json_ok
    if not json_ok:
        result["error"] = error
        result["sha_after"] = sha256_file(path)
        result["unchanged"] = result["sha_after"] == before
        return result

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    empty = [field for field in REQUIRED_FIELDS if field in data and not value_present(data.get(field))]
    type_errors = [
        field for field in LIST_FIELDS
        if field in data and not isinstance(data.get(field), list)
    ]

    role_blob = f"{data.get('name','')} {data.get('role','')}".lower()
    role_keywords = EXPECTED_ROLE_KEYWORDS.get(filename, [])
    role_keyword_hint_ok = any(keyword in role_blob for keyword in role_keywords)

    after = sha256_file(path)
    result.update({
        "missing_fields": missing,
        "empty_required_fields": empty,
        "list_field_type_errors": type_errors,
        "role_keyword_hint_ok": role_keyword_hint_ok,
        "sha_after": after,
        "unchanged": after == before,
        "summary": {
            "name": data.get("name"),
            "role": data.get("role"),
            "allowed_reads_count": len(data.get("allowed_reads", [])) if isinstance(data.get("allowed_reads"), list) else None,
            "allowed_writes_count": len(data.get("allowed_writes", [])) if isinstance(data.get("allowed_writes"), list) else None,
            "forbidden_writes_count": len(data.get("forbidden_writes", [])) if isinstance(data.get("forbidden_writes"), list) else None,
            "commands_count": len(data.get("api_or_cli_commands_exposed", [])) if isinstance(data.get("api_or_cli_commands_exposed"), list) else None,
            "audit_log_path": data.get("audit_log_path"),
            "test_command": data.get("test_command"),
            "startup_command": data.get("startup_command"),
            "shutdown_command": data.get("shutdown_command"),
            "health_check_command": data.get("health_check_command"),
            "owner_authority": data.get("owner_authority"),
        }
    })

    result["ok"] = (
        result["exists"]
        and result["json_ok"]
        and not missing
        and not empty
        and not type_errors
        and bool(role_keyword_hint_ok)
        and result["unchanged"] is True
    )
    return result


def path_exists_summary(home: Path) -> Dict[str, Any]:
    forge_root = home / "forge"
    aiweb_root = home / "aiweb"
    iv_root = home / "identity-vault"
    return {
        "forge_root": str(forge_root),
        "forge_root_exists": forge_root.exists(),
        "aiweb_root": str(aiweb_root),
        "aiweb_root_exists": aiweb_root.exists(),
        "identity_vault_root": str(iv_root),
        "identity_vault_root_exists": iv_root.exists(),
        "rmc_wrappers_root": str(aiweb_root / "runtime_wrappers"),
        "rmc_wrappers_root_exists": (aiweb_root / "runtime_wrappers").exists(),
        "identity_vault_adapter_exists": (forge_root / "agents/forge/identity_vault_adapter.py").exists(),
        "rmc_tools_exists": (forge_root / "agents/forge/rmc_tools.py").exists(),
        "protoforge2_candidates": [
            {"path": str(home / "protoforge2"), "exists": (home / "protoforge2").exists()},
            {"path": str(aiweb_root / "protoforge2"), "exists": (aiweb_root / "protoforge2").exists()},
            {"path": str(aiweb_root / "runtime_wrappers/protoforge2"), "exists": (aiweb_root / "runtime_wrappers/protoforge2").exists()},
        ],
        "echoforge_candidates": [
            {"path": str(home / "echoforge"), "exists": (home / "echoforge").exists()},
            {"path": str(aiweb_root / "echoforge"), "exists": (aiweb_root / "echoforge").exists()},
            {"path": str(aiweb_root / "runtime_wrappers/echoforge"), "exists": (aiweb_root / "runtime_wrappers/echoforge").exists()},
        ],
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# AI.Web Patch 223 Service Contracts Verify")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This patch verifies the five AI.Web service contract draft files only.")
    lines.append("- It does not register Forge connector commands.")
    lines.append("- It does not activate agent identities.")
    lines.append("- It does not write Identity Vault databases, RMC memory, or Forge registry.")
    lines.append("- It does not read `.env` secret values.")
    lines.append("")
    lines.append("## Contract Root")
    lines.append(f"- `{report['contract_root']}`")
    lines.append(f"- exists: `{report['contract_root_exists']}`")
    lines.append("")
    lines.append("## Required Fields")
    for field in REQUIRED_FIELDS:
        lines.append(f"- `{field}`")
    lines.append("")
    lines.append("## Contract Validation")
    for item in report["contracts"]:
        status = "PASS" if item["ok"] else "FAIL"
        lines.append(f"- `{item['filename']}`: **{status}**")
        lines.append(f"  - exists: `{item['exists']}` json_ok: `{item['json_ok']}` unchanged: `{item['unchanged']}`")
        lines.append(f"  - role keyword hint ok: `{item['role_keyword_hint_ok']}`")
        if item["missing_fields"]:
            lines.append(f"  - missing fields: `{', '.join(item['missing_fields'])}`")
        if item["empty_required_fields"]:
            lines.append(f"  - empty fields: `{', '.join(item['empty_required_fields'])}`")
        if item["list_field_type_errors"]:
            lines.append(f"  - list field type errors: `{', '.join(item['list_field_type_errors'])}`")
        if item["error"]:
            lines.append(f"  - error: `{item['error']}`")
        summary = item.get("summary", {})
        if summary:
            lines.append(f"  - name: `{summary.get('name')}`")
            lines.append(f"  - allowed_reads: `{summary.get('allowed_reads_count')}` allowed_writes: `{summary.get('allowed_writes_count')}` forbidden_writes: `{summary.get('forbidden_writes_count')}` commands: `{summary.get('commands_count')}`")
            lines.append(f"  - audit_log_path: `{summary.get('audit_log_path')}`")
            lines.append(f"  - test_command: `{summary.get('test_command')}`")
            lines.append(f"  - startup_command: `{summary.get('startup_command')}`")
            lines.append(f"  - shutdown_command: `{summary.get('shutdown_command')}`")
            lines.append(f"  - health_check_command: `{summary.get('health_check_command')}`")
            lines.append(f"  - owner_authority: `{summary.get('owner_authority')}`")
    lines.append("")
    lines.append("## Boundary Path Summary")
    ps = report["path_summary"]
    lines.append(f"- Forge root exists: `{ps['forge_root_exists']}` — `{ps['forge_root']}`")
    lines.append(f"- AI.Web root exists: `{ps['aiweb_root_exists']}` — `{ps['aiweb_root']}`")
    lines.append(f"- Identity Vault root exists: `{ps['identity_vault_root_exists']}` — `{ps['identity_vault_root']}`")
    lines.append(f"- RMC wrappers root exists: `{ps['rmc_wrappers_root_exists']}` — `{ps['rmc_wrappers_root']}`")
    lines.append(f"- Forge RMC tools file exists: `{ps['rmc_tools_exists']}`")
    lines.append(f"- Forge Identity Vault adapter exists: `{ps['identity_vault_adapter_exists']}`")
    lines.append("")
    lines.append("## ProtoForge2 / EchoForge Placeholder Status")
    lines.append("- These services may still be planned roots. Missing roots are acceptable at contract-verification stage.")
    lines.append("- ProtoForge2 candidates:")
    for candidate in ps["protoforge2_candidates"]:
        lines.append(f"  - `{candidate['path']}` exists=`{candidate['exists']}`")
    lines.append("- EchoForge candidates:")
    for candidate in ps["echoforge_candidates"]:
        lines.append(f"  - `{candidate['path']}` exists=`{candidate['exists']}`")
    lines.append("")
    lines.append("## Findings")
    for finding in report["findings"]:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    if report["verdict"] == "PASS":
        lines.append("Create the Forge read-only connector command patch for `forge-rmc-status`, `forge-rmc-test-status`, `forge-identity-status`, `forge-agent-list`, `forge-agent-show <agent_id>`, and `forge-system-boundary-map`. No memory writes, app creation, or agent mutation.")
    else:
        lines.append("Fix failed contract validation before adding Forge read-only connector commands.")
    return "\n".join(lines) + "\n"


def main() -> int:
    home = Path.home()
    forge_root = home / "forge"
    aiweb_root = home / "aiweb"
    contract_root = aiweb_root / "service_contracts"
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    run_dir = forge_root / "memory" / REPORT_DIR_NAME / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    contracts = [validate_contract(name, contract_root / name) for name in REQUIRED_CONTRACTS]

    findings: List[Dict[str, str]] = []
    if not contract_root.exists():
        findings.append({"level": "FAIL", "code": "AIWEB_CONTRACT_ROOT_MISSING", "message": "The AI.Web service_contracts directory is missing."})

    failed = [c["filename"] for c in contracts if not c["ok"]]
    if failed:
        findings.append({"level": "FAIL", "code": "AIWEB_SERVICE_CONTRACT_VALIDATION_FAILED", "message": "One or more service contracts failed validation: " + ", ".join(failed)})
    else:
        findings.append({"level": "INFO", "code": "AIWEB_SERVICE_CONTRACTS_VERIFIED", "message": "All five service contracts loaded, validated, and remained unchanged during verification."})

    ps = path_exists_summary(home)
    if not any(c["exists"] for c in ps["protoforge2_candidates"]):
        findings.append({"level": "INFO", "code": "PROTOFORGE2_ROOT_NOT_PRESENT_YET", "message": "ProtoForge2 root is not present yet; contract is a planned boundary placeholder."})
    if not any(c["exists"] for c in ps["echoforge_candidates"]):
        findings.append({"level": "INFO", "code": "ECHOFORGE_ROOT_NOT_PRESENT_YET", "message": "EchoForge root is not present yet; contract is a planned boundary placeholder."})

    verdict = "PASS" if contract_root.exists() and not failed else "FAIL"

    report: Dict[str, Any] = {
        "patch_id": PATCH_ID,
        "timestamp": ts,
        "verdict": verdict,
        "contract_root": str(contract_root),
        "contract_root_exists": contract_root.exists(),
        "required_contracts": REQUIRED_CONTRACTS,
        "required_fields": REQUIRED_FIELDS,
        "contracts": contracts,
        "path_summary": ps,
        "findings": findings,
        "mutations": {
            "forge_registry_modified": False,
            "identity_vault_db_write_performed": False,
            "rmc_memory_write_performed": False,
            "agent_identity_activation_performed": False,
            "env_secret_values_read": False,
        }
    }

    json_path = run_dir / f"{ts}_aiweb_patch223_service_contracts_verify.json"
    md_path = run_dir / f"{ts}_aiweb_patch223_service_contracts_verify.md"
    latest_json = forge_root / "memory" / REPORT_DIR_NAME / "latest_aiweb_patch223_service_contracts_verify.json"
    latest_md = forge_root / "memory" / REPORT_DIR_NAME / "latest_aiweb_patch223_service_contracts_verify.md"

    json_text = json.dumps(report, indent=2, sort_keys=True)
    md_text = render_markdown(report)

    json_path.write_text(json_text + "\n", encoding="utf-8")
    md_path.write_text(md_text, encoding="utf-8")
    latest_json.write_text(json_text + "\n", encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    print("AI.Web Patch 223 service contracts verify complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

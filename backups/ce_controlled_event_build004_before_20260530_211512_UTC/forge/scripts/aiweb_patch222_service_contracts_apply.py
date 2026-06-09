#!/usr/bin/env python3
# identity: aiweb_patch222_service_contracts_apply.py
# purpose: Create and verify AI.Web bootstrap service contract files before any connector wiring.

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "patch222_aiweb_service_contracts"
VERSION = "0.1.0-contract-draft"
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

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
AIWEB_ROOT = HOME / "aiweb"
IDENTITY_VAULT_ROOT = HOME / "identity-vault"
CONTRACT_ROOT = AIWEB_ROOT / "service_contracts"
FORGE_MEMORY_ROOT = FORGE_ROOT / "memory" / "aiweb_patch222_service_contracts_v1"
BACKUP_ROOT = FORGE_ROOT / "backups" / "patch222_aiweb_service_contracts_before"

CONTRACT_PATHS = {
    "forge": CONTRACT_ROOT / "forge.contract.json",
    "rmc": CONTRACT_ROOT / "rmc.contract.json",
    "identity_vault": CONTRACT_ROOT / "identity_vault.contract.json",
    "protoforge2": CONTRACT_ROOT / "protoforge2.contract.json",
    "echoforge": CONTRACT_ROOT / "echoforge.contract.json",
}


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def command_exists(path: Path) -> bool:
    return path.exists()


def contract_base(name: str, role: str, owner: str) -> Dict[str, Any]:
    return {
        "name": name,
        "version": VERSION,
        "status": "DRAFT_BOUNDARY_CONTRACT_NOT_CONNECTOR",
        "created_by_patch": PATCH_ID,
        "created_at_utc": None,
        "role": role,
        "allowed_reads": [],
        "allowed_writes": [],
        "forbidden_reads": [
            "secret values from .env files",
            "private keys, API keys, JWT secrets, passwords, raw tokens",
            "private agent memory payloads except through approved RMC boundary"
        ],
        "forbidden_writes": [],
        "api_or_cli_commands_exposed": [],
        "audit_log_path": "",
        "test_command": "",
        "startup_command": "",
        "shutdown_command": "",
        "health_check_command": "",
        "owner_authority": owner,
        "integration_rules": [
            "This contract defines boundary intent only; it does not activate connectors by itself.",
            "No agent identity activation is permitted from this contract file alone.",
            "All writes must pass through Forge approval, backup, and verification gates.",
            "No service may bypass Forge to mutate another service.",
            "Read-only connector commands must be proven before write-capable commands are considered."
        ],
    }


def build_contracts(ts: str) -> Dict[str, Dict[str, Any]]:
    forge = contract_base(
        "forge",
        "Governing and verification layer for AI.Web. Forge owns patch proposal, sandboxing, verification, rollback records, command-surface checks, and audit receipts.",
        "Nic Bogaert; Forge approval gates"
    )
    forge.update({
        "created_at_utc": ts,
        "allowed_reads": [
            "/home/nic/aiweb/service_contracts/*.contract.json",
            "/home/nic/forge/config/tool_registry.json",
            "/home/nic/forge/logs/forge_audit.log metadata",
            "/home/nic/forge/memory/* reports and receipts",
            "RMC status through approved read-only wrapper",
            "Identity Vault metadata through approved read-only adapter"
        ],
        "allowed_writes": [
            "/home/nic/forge/memory/* reports and receipts",
            "/home/nic/forge/backups/* backups",
            "/home/nic/forge/proposed_patches/*",
            "/home/nic/forge/apply_plans/*",
            "/home/nic/forge/rollback_registry/*",
            "/home/nic/forge/logs/forge_audit.log through append-only Forge logic",
            "/home/nic/aiweb/service_contracts/*.contract.json through approved contract patches only"
        ],
        "forbidden_writes": [
            "/home/nic/identity-vault/.env",
            "/home/nic/identity-vault/node_modules",
            "/home/nic/identity-vault/*.db direct mutation",
            "/home/nic/identity-vault/data/*.db direct mutation",
            "RMC memory writes unless routed through future approved RMC write contract",
            "agent identity state mutation before explicit activation gate",
            "EchoForge tool creation without patch proposal and sandbox verification"
        ],
        "api_or_cli_commands_exposed": [
            "forge-command-surface",
            "forge-version",
            "audit",
            "patch-propose",
            "patch-preflight",
            "patch-apply",
            "patch-verify",
            "rollback-restore",
            "future: forge-system-boundary-map",
            "future: forge-rmc-status",
            "future: forge-identity-status"
        ],
        "audit_log_path": "/home/nic/forge/logs/forge_audit.log",
        "test_command": "cd /home/nic/forge && source .venv/bin/activate && python main.py # then run forge-command-surface and forge-version",
        "startup_command": "cd /home/nic/forge && source .venv/bin/activate && python main.py",
        "shutdown_command": "exit from Forge CLI",
        "health_check_command": "forge-command-surface && forge-version"
    })

    rmc = contract_base(
        "rmc",
        "Shared and agent-scoped recursive memory/meaning layer. RMC parses phase state, checks drift, compiles manifests, renders previews, and validates echo under Forge governance.",
        "Forge governs access; Nic approves memory write capability"
    )
    rmc.update({
        "created_at_utc": ts,
        "allowed_reads": [
            "/home/nic/aiweb/runtime_wrappers/phase_parser metadata",
            "/home/nic/aiweb/runtime_wrappers/drift_detection metadata",
            "/home/nic/aiweb/runtime_wrappers/manifest_compiler metadata",
            "/home/nic/aiweb/runtime_wrappers/output_renderer metadata",
            "/home/nic/aiweb/runtime_wrappers/echo_validator metadata",
            "future shared RMC memory namespaces through approved contracts"
        ],
        "allowed_writes": [
            "none during read-only bootstrap",
            "future: test receipts only under Forge-approved RMC write contract"
        ],
        "forbidden_writes": [
            "live shared RMC memory before write contract",
            "agent private memory before identity activation gate",
            "Identity Vault database files",
            ".env files",
            "Forge tool registry"
        ],
        "api_or_cli_commands_exposed": [
            "rmc_phase_parse_preview",
            "rmc_drift_check_preview",
            "rmc_echo_validate_preview",
            "rmc_pipeline_preview",
            "future: forge-rmc-status",
            "future: forge-rmc-test-status"
        ],
        "audit_log_path": "/home/nic/forge/logs/forge_audit.log and /home/nic/forge/memory/rmc_* reports",
        "test_command": "cd /home/nic/forge && source .venv/bin/activate && python scripts/rmc_patch213_forge_runtime_preview_check.py",
        "startup_command": "imported as Python runtime wrappers by Forge; no independent daemon in this bootstrap stage",
        "shutdown_command": "not applicable; no independent daemon in this bootstrap stage",
        "health_check_command": "python /home/nic/forge/scripts/rmc_patch213_forge_runtime_preview_check.py"
    })

    iv = contract_base(
        "identity_vault",
        "Agent identity, permissions, profile metadata, and RMC namespace pointers. Identity Vault is not an agent runtime and not the shared memory store.",
        "Forge governs access; Nic approves identity activation"
    )
    iv.update({
        "created_at_utc": ts,
        "allowed_reads": [
            "/home/nic/identity-vault/package.json metadata",
            "/home/nic/identity-vault/service_contracts/identity_vault_readonly_service_contract.draft.json",
            "/home/nic/identity-vault/data/identity_vault.db schema and safe metadata through read-only adapter",
            "agent profile metadata after explicit adapter approval",
            "identity-to-RMC namespace pointers after explicit adapter approval"
        ],
        "allowed_writes": [
            "none during read-only bootstrap"
        ],
        "forbidden_reads": [
            "secret values from /home/nic/identity-vault/.env",
            "raw tokens, private keys, JWT secrets, API keys, passwords",
            "full private memory payloads unless routed through approved RMC boundary"
        ],
        "forbidden_writes": [
            "/home/nic/identity-vault/.env",
            "/home/nic/identity-vault/node_modules",
            "/home/nic/identity-vault/data/identity_vault.db",
            "/home/nic/identity-vault/vault.db",
            "agent identity state before explicit activation gate",
            "RMC memory",
            "Forge tool registry"
        ],
        "api_or_cli_commands_exposed": [
            "future: forge-identity-status",
            "future: forge-agent-list",
            "future: forge-agent-show <agent_id>"
        ],
        "audit_log_path": "/home/nic/forge/logs/forge_audit.log and /home/nic/forge/memory/identity_vault_* reports",
        "test_command": "cd /home/nic/forge && source .venv/bin/activate && python scripts/identity_vault_patch218_verify.py",
        "startup_command": "Identity Vault application startup is not required for read-only Forge metadata adapter",
        "shutdown_command": "not applicable for read-only adapter",
        "health_check_command": "python /home/nic/forge/scripts/identity_vault_patch218_verify.py"
    })

    proto = contract_base(
        "protoforge2",
        "Future execution and simulation substrate. ProtoForge2 runs controlled tests/simulations when Forge approves a plan. It is a lab bench, not an authority layer.",
        "Forge governs execution; Nic approves live effects"
    )
    proto.update({
        "created_at_utc": ts,
        "allowed_reads": [
            "/home/nic/aiweb/service_contracts/*.contract.json",
            "Forge-approved sandbox inputs",
            "Forge-approved test fixtures",
            "future EchoForge simulation requests routed by Forge"
        ],
        "allowed_writes": [
            "future: sandbox-only execution receipts",
            "future: simulation output under Forge-approved sandbox paths"
        ],
        "forbidden_writes": [
            "live /home/nic/aiweb source files without Forge patch approval",
            "Identity Vault databases",
            "RMC live memory",
            "Forge registry",
            ".env files",
            "agent identity state"
        ],
        "api_or_cli_commands_exposed": [
            "future: protoforge2-status",
            "future: protoforge2-run-sandbox",
            "future: protoforge2-test-report"
        ],
        "audit_log_path": "/home/nic/forge/logs/forge_audit.log and future /home/nic/forge/memory/protoforge2_* reports",
        "test_command": "future: Forge-approved ProtoForge2 smoke test",
        "startup_command": "future: start through Forge-controlled sandbox command only",
        "shutdown_command": "future: stop through Forge-controlled sandbox command only",
        "health_check_command": "future: protoforge2-status"
    })

    echo = contract_base(
        "echoforge",
        "Future creation/request layer for tools, simulations, and applications. EchoForge requests builds; Forge proposes, sandboxes, verifies, and applies.",
        "Forge governs creation; Nic approves live application"
    )
    echo.update({
        "created_at_utc": ts,
        "allowed_reads": [
            "/home/nic/aiweb/service_contracts/*.contract.json",
            "Forge-approved build requirements",
            "RMC preview summaries through Forge read-only tools",
            "Identity Vault requesting-agent metadata through Forge adapter"
        ],
        "allowed_writes": [
            "future: build intention receipts under Forge-approved path only",
            "future: draft proposals under Forge-approved proposed_patches path only"
        ],
        "forbidden_writes": [
            "direct tool installation",
            "direct live app creation",
            "Identity Vault databases",
            "RMC memory direct writes",
            "Forge registry direct writes",
            ".env files",
            "agent identity state"
        ],
        "api_or_cli_commands_exposed": [
            "future: echoforge-status",
            "future: echoforge-build-intention",
            "future: echoforge-simulation-request"
        ],
        "audit_log_path": "/home/nic/forge/logs/forge_audit.log and future /home/nic/forge/memory/echoforge_* reports",
        "test_command": "future: Forge-approved EchoForge intention dry-run",
        "startup_command": "future: start only through Forge-controlled command",
        "shutdown_command": "future: stop only through Forge-controlled command",
        "health_check_command": "future: echoforge-status"
    })

    return {
        "forge": forge,
        "rmc": rmc,
        "identity_vault": iv,
        "protoforge2": proto,
        "echoforge": echo,
    }


def validate_contract(path: Path) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    if not path.exists():
        return False, ["missing file"]
    try:
        data = read_json(path)
    except Exception as exc:
        return False, [f"json parse error: {exc}"]
    for field in REQUIRED_FIELDS:
        if field not in data:
            issues.append(f"missing required field: {field}")
    if data.get("allowed_writes") is None:
        issues.append("allowed_writes is null")
    if data.get("forbidden_writes") is None:
        issues.append("forbidden_writes is null")
    if not data.get("owner_authority"):
        issues.append("owner_authority is empty")
    if data.get("status") != "DRAFT_BOUNDARY_CONTRACT_NOT_CONNECTOR":
        issues.append("unexpected status")
    return not issues, issues


def main() -> int:
    ts = utc_stamp()
    run_dir = FORGE_MEMORY_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    backup_dir = BACKUP_ROOT / ts
    backup_dir.mkdir(parents=True, exist_ok=True)

    report: Dict[str, Any] = {
        "timestamp": ts,
        "patch_id": PATCH_ID,
        "boundary": {
            "creates_contract_files_only": True,
            "does_not_register_tools": True,
            "does_not_activate_agent_identities": True,
            "does_not_write_databases": True,
            "does_not_read_env_secret_values": True,
            "does_not_modify_rmc_memory": True,
        },
        "roots": {
            "forge_root": str(FORGE_ROOT),
            "aiweb_root": str(AIWEB_ROOT),
            "identity_vault_root": str(IDENTITY_VAULT_ROOT),
            "contract_root": str(CONTRACT_ROOT),
        },
        "preflight": {},
        "backups": {},
        "writes": {},
        "validations": {},
        "findings": [],
    }

    if not AIWEB_ROOT.exists():
        report["findings"].append({"level": "FAIL", "code": "AIWEB_ROOT_MISSING", "message": str(AIWEB_ROOT)})
    if not FORGE_ROOT.exists():
        report["findings"].append({"level": "FAIL", "code": "FORGE_ROOT_MISSING", "message": str(FORGE_ROOT)})

    CONTRACT_ROOT.mkdir(parents=True, exist_ok=True)

    before_hashes = {}
    for name, path in CONTRACT_PATHS.items():
        before_hashes[name] = sha256_file(path)
        if path.exists():
            dest = backup_dir / path.name
            shutil.copy2(path, dest)
            report["backups"][name] = str(dest)
        else:
            report["backups"][name] = "SKIPPED_MISSING"

    contracts = build_contracts(ts)
    for name, contract in contracts.items():
        path = CONTRACT_PATHS[name]
        write_json(path, contract)
        report["writes"][name] = {
            "path": str(path),
            "before_sha256": before_hashes.get(name),
            "after_sha256": sha256_file(path),
        }

    all_ok = True
    for name, path in CONTRACT_PATHS.items():
        ok, issues = validate_contract(path)
        report["validations"][name] = {
            "path": str(path),
            "ok": ok,
            "issues": issues,
            "required_fields_present": [] if not path.exists() else [f for f in REQUIRED_FIELDS if f in read_json(path)],
        }
        all_ok = all_ok and ok

    # Boundary sanity: this patch should not create connector command files or mutate registries.
    tool_registry = FORGE_ROOT / "config" / "tool_registry.json"
    report["preflight"]["tool_registry_exists"] = tool_registry.exists()
    report["preflight"]["tool_registry_sha256"] = sha256_file(tool_registry)

    # Minimal source root presence for future services.
    report["preflight"]["rmc_wrappers_exist"] = (AIWEB_ROOT / "runtime_wrappers").exists()
    report["preflight"]["identity_vault_contract_exists"] = (IDENTITY_VAULT_ROOT / "service_contracts" / "identity_vault_readonly_service_contract.draft.json").exists()
    report["preflight"]["protoforge2_root_exists"] = (HOME / "protoforge2").exists()
    report["preflight"]["echoforge_root_exists"] = (HOME / "echoforge").exists()

    if all_ok:
        report["findings"].append({"level": "INFO", "code": "AIWEB_SERVICE_CONTRACTS_WRITTEN", "message": "Five service contract draft files were written and validated."})
    else:
        report["findings"].append({"level": "FAIL", "code": "AIWEB_SERVICE_CONTRACT_VALIDATION_FAILED", "message": "One or more required fields missing or invalid."})

    verdict = "PASS" if all_ok and not any(f["level"] == "FAIL" for f in report["findings"]) else "FAIL"
    report["verdict"] = verdict

    json_path = run_dir / f"{ts}_aiweb_patch222_service_contracts.json"
    write_json(json_path, report)
    latest_json = FORGE_MEMORY_ROOT / "latest_aiweb_patch222_service_contracts.json"
    write_json(latest_json, report)

    md_lines = [
        "# AI.Web Patch 222 Service Contracts Apply",
        "",
        f"Timestamp: `{ts}`",
        f"Verdict: **{verdict}**",
        "",
        "## Boundary",
        "- This patch creates the five AI.Web service contract draft files only.",
        "- It does not register Forge connector commands.",
        "- It does not activate agent identities.",
        "- It does not write Identity Vault databases, RMC memory, or Forge registry.",
        "- It does not read `.env` secret values.",
        "",
        "## Contract Root",
        f"- `{CONTRACT_ROOT}`",
        "",
        "## Files Written",
    ]
    for name, info in report["writes"].items():
        md_lines.append(f"- `{Path(info['path']).name}` after_sha256=`{info['after_sha256']}`")

    md_lines.extend([
        "",
        "## Required Contract Fields",
    ])
    for f in REQUIRED_FIELDS:
        md_lines.append(f"- `{f}`")

    md_lines.extend([
        "",
        "## Validation",
    ])
    for name, v in report["validations"].items():
        md_lines.append(f"- `{Path(v['path']).name}`: **{'PASS' if v['ok'] else 'FAIL'}**")
        if v["issues"]:
            for issue in v["issues"]:
                md_lines.append(f"  - {issue}")

    md_lines.extend([
        "",
        "## Preflight Notes",
        f"- RMC wrappers exist: `{report['preflight']['rmc_wrappers_exist']}`",
        f"- Identity Vault draft contract exists: `{report['preflight']['identity_vault_contract_exists']}`",
        f"- ProtoForge2 root exists: `{report['preflight']['protoforge2_root_exists']}`",
        f"- EchoForge root exists: `{report['preflight']['echoforge_root_exists']}`",
        "",
        "## Findings",
    ])
    for finding in report["findings"]:
        md_lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")

    md_lines.extend([
        "",
        "## Next Safe Step",
        "Run a service-contract verification scan, then add Forge read-only connector commands only after the contracts are verified.",
    ])

    md_text = "\n".join(md_lines) + "\n"
    md_path = run_dir / f"{ts}_aiweb_patch222_service_contracts.md"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md = FORGE_MEMORY_ROOT / "latest_aiweb_patch222_service_contracts.md"
    latest_md.write_text(md_text, encoding="utf-8")

    print("AI.Web Patch 222 service contracts apply complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

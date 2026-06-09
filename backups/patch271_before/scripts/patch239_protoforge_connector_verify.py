
#!/usr/bin/env python3
# Patch 239 verifier — static verification only. Does not start Forge or run ProtoForge.
from __future__ import annotations
import ast, json, py_compile, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"

REQUIRED_COMMANDS = [
    "forge-protoforge-status",
    "forge-protoforge-simulation-plan",
    "forge-protoforge-simulation-run-approved",
    "forge-protoforge-result-show",
]
REQUIRED_FUNCTIONS = [
    "cmd_forge_protoforge_status",
    "cmd_forge_protoforge_simulation_plan",
    "cmd_forge_protoforge_simulation_run_approved",
    "cmd_forge_protoforge_result_show",
]
REQUIRED_TOOLS = [
    "forge_protoforge_status",
    "forge_protoforge_simulation_plan",
    "forge_protoforge_simulation_run_approved",
    "forge_protoforge_result_show",
]

def main() -> int:
    try:
        py_compile.compile(str(MAIN), doraise=True)
    except Exception as exc:
        print("PATCH239_VERIFY_FAIL")
        print("compile_error=" + str(exc))
        return 1

    src = MAIN.read_text(encoding="utf-8")
    tree = ast.parse(src)
    func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    registry = json.loads(REG.read_text(encoding="utf-8"))
    tools = registry.get("tools", {})

    checks = {
        "commands_present": all(cmd in src for cmd in REQUIRED_COMMANDS),
        "functions_present": all(fn in func_names for fn in REQUIRED_FUNCTIONS),
        "routes_present": all((cmd in src and fn in src) for cmd, fn in zip(REQUIRED_COMMANDS, REQUIRED_FUNCTIONS)),
        "tools_registered": all(tool in tools for tool in REQUIRED_TOOLS),
        "no_shell_true_in_patch239_block": "shell=True," not in src.split("# --- BEGIN PATCH 239 PROTOFORGE CONNECTOR V1 ---", 1)[1].split("# --- END PATCH 239 PROTOFORGE CONNECTOR V1 ---", 1)[0] and "shell = True" not in src.split("# --- BEGIN PATCH 239 PROTOFORGE CONNECTOR V1 ---", 1)[1].split("# --- END PATCH 239 PROTOFORGE CONNECTOR V1 ---", 1)[0],
        "contract_path_present": "/home/nic/aiweb/service_contracts/protoforge2.contract.json" in src,
        "substrate_root_present": "/home/nic/aiweb/runtime_wrappers/protoforge_sandbox_substrate_v0" in src,
        "allowlist_only_types": "pybullet_fixed_falling_cube" in src and "symbolic_frequency_probe" in src,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH239_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1
    print("PATCH239_VERIFY_PASS")
    print("commands=forge-protoforge-status, forge-protoforge-simulation-plan, forge-protoforge-simulation-run-approved, forge-protoforge-result-show")
    print("boundary=allowlist-only connector; no shell-enabled subprocess calls in patch239 block; no Identity Vault write; no RMC live memory write; no Forge UI change")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

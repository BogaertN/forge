#!/usr/bin/env python3
"""Patch 263S1 verifier — lifecycle boundary proof correction.

This verifier is read-only. It never calls restart, shutdown, shell, Identity
Vault writes, RMC memory writes, Chroma writes, or LLM routes.
"""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"

checks: list[tuple[str, bool, str]] = []

def check(name: str, ok: bool, detail: str = "") -> None:
    checks.append((name, bool(ok), detail))

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""

main_text = read(MAIN)
check("main_exists", MAIN.exists(), str(MAIN))
try:
    ast.parse(main_text)
    check("main_ast_ok", True)
except Exception as exc:
    check("main_ast_ok", False, str(exc))

# The bug this patch fixes: manifest/status/logs must not falsely imply that
# the lifecycle system lacks preview-first and exact-token gates.
check("s1_comment_present", "Patch 263S1 correction" in main_text)
check("global_preview_gate_field_present", "preview_before_confirm_required_for_confirming_actions" in main_text)
check("global_token_gate_field_present", "exact_confirmation_token_required_for_confirming_actions" in main_text)
check("per_action_preview_field_present", "this_action_requires_preview_before_confirm" in main_text)
check("per_action_token_field_present", "this_action_requires_exact_confirmation_token" in main_text)
check("legacy_preview_field_preserved", '"requires_preview_before_confirm": True' in main_text)
check("legacy_token_field_preserved", '"requires_exact_confirmation_token": True' in main_text)
check("mode_manifest_s1", "aiweb_os_lifecycle_manifest_patch263S1" in main_text)
check("mode_status_s1", "aiweb_os_lifecycle_status_patch263S1" in main_text)
check("mode_logs_s1", "aiweb_os_lifecycle_logs_patch263S1" in main_text)
check("mode_preview_s1", "aiweb_os_lifecycle_preview_patch263S1" in main_text)
check("mode_confirm_s1", "aiweb_os_lifecycle_confirm_patch263S1" in main_text)

# Preserve Patch 263S route surface and safety constraints.
for route in [
    "/api/aiweb-os/lifecycle-manifest",
    "/api/aiweb-os/status",
    "/api/aiweb-os/logs",
    "/api/aiweb-os/exit-window-preview",
    "/api/aiweb-os/exit-window-confirm",
    "/api/aiweb-os/restart-preview",
    "/api/aiweb-os/restart-confirm",
    "/api/aiweb-os/shutdown-preview",
    "/api/aiweb-os/shutdown-confirm",
]:
    check(f"route_preserved:{route}", route in main_text)

check("no_aiweb_shell_route", "/api/aiweb-os/shell" not in main_text)
check("no_aiweb_command_route", "/api/aiweb-os/command" not in main_text)
check("browser_shell_false", '"browser_executes_shell": False' in main_text)
check("browser_arbitrary_command_false", '"browser_executes_arbitrary_command": False' in main_text)
check("identity_write_false", '"identity_vault_write": False' in main_text)
check("rmc_write_false", '"rmc_live_memory_write": False' in main_text)
check("chroma_write_false", '"chroma_write": False' in main_text)
check("llm_call_false", '"llm_call": False' in main_text)

# Preserve recent RMC/deep stack routes.
for route in [
    "/api/rmc/deep-dry-run",
    "/api/rmc/deep-pipeline-preflight",
    "/api/rmc/resurrection-preview",
    "/api/rmc/protoforge2-drift-preview",
    "/api/rmc/containment-router",
    "/api/rmc/chi-correction-preview",
]:
    check(f"rmc_route_preserved:{route}", route in main_text)

# Safe pure function check when full Forge tree is present.
try:
    spec = importlib.util.spec_from_file_location("forge_main_patch263s1_verify", MAIN)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    manifest = module._p263s_lifecycle_manifest_v1()
    status_boundary = module._p263s_lifecycle_boundary("status")
    manifest_boundary = manifest.get("boundary", {})
    restart_preview = module._p263s_preview_payload("restart")
    refused = module._p263s_confirm_payload("restart", "/api/aiweb-os/restart-confirm?token=WRONG")

    for label, boundary in [("manifest", manifest_boundary), ("status", status_boundary)]:
        check(f"{label}_global_preview_gate_true", boundary.get("preview_before_confirm_required_for_confirming_actions") is True)
        check(f"{label}_global_token_gate_true", boundary.get("exact_confirmation_token_required_for_confirming_actions") is True)
        check(f"{label}_legacy_preview_true", boundary.get("requires_preview_before_confirm") is True)
        check(f"{label}_legacy_token_true", boundary.get("requires_exact_confirmation_token") is True)
        check(f"{label}_browser_shell_false", boundary.get("browser_executes_shell") is False)
        check(f"{label}_arbitrary_command_false", boundary.get("browser_executes_arbitrary_command") is False)

    restart_boundary = restart_preview.get("boundary", {})
    check("restart_this_action_preview_true", restart_boundary.get("this_action_requires_preview_before_confirm") is True)
    check("restart_this_action_token_true", restart_boundary.get("this_action_requires_exact_confirmation_token") is True)
    check("status_this_action_preview_false", status_boundary.get("this_action_requires_preview_before_confirm") is False)
    check("status_this_action_token_false", status_boundary.get("this_action_requires_exact_confirmation_token") is False)
    check("wrong_token_still_refused", refused.get("status") == "REFUSED" and refused.get("executed") is False)
except ModuleNotFoundError as exc:
    check("safe_import_checks_skipped_without_full_forge_tree", True, str(exc))
except Exception as exc:
    check("safe_import_checks", False, str(exc))

passed = sum(1 for _, ok, _ in checks if ok)
failed = len(checks) - passed
print(f"PATCH 263S1 VERIFIER  Total:{len(checks)} Passed:{passed} Failed:{failed}")
for name, ok, detail in checks:
    mark = "✓ [PASS]" if ok else "✗ [FAIL]"
    suffix = f" — {detail}" if detail else ""
    print(f"  {mark} {name}{suffix}")
if failed:
    print("RESULT: PATCH_263S1_VERIFY_FAILED")
    raise SystemExit(1)
print("RESULT: PATCH_263S1_VERIFY_OK")

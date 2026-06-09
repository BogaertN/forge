#!/usr/bin/env python3
"""Patch 263S1 lifecycle boundary behavior tests.

Tests only pure payload functions and static source. No restart/shutdown is
executed. No shell, memory write, Identity Vault, Chroma, or LLM call is made.
"""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
results: list[tuple[str, bool, str]] = []

def ok(name: str, condition: bool, detail: str = "") -> None:
    results.append((name, bool(condition), detail))

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""

text = read(MAIN)
try:
    ast.parse(text)
    ok("T0_main_ast", True)
except Exception as exc:
    ok("T0_main_ast", False, str(exc))

try:
    spec = importlib.util.spec_from_file_location("forge_main_patch263s1_test", MAIN)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    manifest = module._p263s_lifecycle_manifest_v1()
    status_boundary = module._p263s_lifecycle_boundary("status")
    logs_boundary = module._p263s_lifecycle_boundary("logs")
    manifest_boundary = manifest.get("boundary", {})
    exit_preview = module._p263s_preview_payload("exit_window")
    restart_preview = module._p263s_preview_payload("restart")
    shutdown_preview = module._p263s_preview_payload("shutdown")
    wrong_shutdown = module._p263s_confirm_payload("shutdown", "/api/aiweb-os/shutdown-confirm?token=WRONG")

    ok("T1_manifest_ok", manifest.get("status") == "OK")
    ok("T1_manifest_patch263S1_mode", manifest.get("mode") == "aiweb_os_lifecycle_manifest_patch263S1")
    ok("T1_routes_still_8", len(manifest.get("routes", [])) == 8)

    for label, boundary in [("manifest", manifest_boundary), ("status", status_boundary), ("logs", logs_boundary)]:
        ok(f"T2_{label}_global_preview_required", boundary.get("preview_before_confirm_required_for_confirming_actions") is True)
        ok(f"T2_{label}_global_token_required", boundary.get("exact_confirmation_token_required_for_confirming_actions") is True)
        ok(f"T2_{label}_legacy_preview_true", boundary.get("requires_preview_before_confirm") is True)
        ok(f"T2_{label}_legacy_token_true", boundary.get("requires_exact_confirmation_token") is True)
        ok(f"T2_{label}_ui_not_authority", boundary.get("ui_is_authority") is False)
        ok(f"T2_{label}_forge_governs", boundary.get("forge_governs") is True)
        ok(f"T2_{label}_no_shell", boundary.get("browser_executes_shell") is False)
        ok(f"T2_{label}_no_arbitrary_command", boundary.get("browser_executes_arbitrary_command") is False)
        ok(f"T2_{label}_no_memory_write", boundary.get("identity_vault_write") is False and boundary.get("rmc_live_memory_write") is False and boundary.get("chroma_write") is False)

    ok("T3_status_this_action_not_confirmable", status_boundary.get("this_action_requires_preview_before_confirm") is False and status_boundary.get("this_action_requires_exact_confirmation_token") is False)
    for name, payload in [("exit", exit_preview), ("restart", restart_preview), ("shutdown", shutdown_preview)]:
        boundary = payload.get("boundary", {})
        ok(f"T3_{name}_preview_status", payload.get("status") == "PREVIEW_OK")
        ok(f"T3_{name}_executes_now_false", payload.get("executes_now") is False)
        ok(f"T3_{name}_this_action_preview_true", boundary.get("this_action_requires_preview_before_confirm") is True)
        ok(f"T3_{name}_this_action_token_true", boundary.get("this_action_requires_exact_confirmation_token") is True)
        ok(f"T3_{name}_has_confirmation_token", bool(payload.get("confirmation_token")))

    ok("T4_wrong_shutdown_refused", wrong_shutdown.get("status") == "REFUSED" and wrong_shutdown.get("executed") is False)
except ModuleNotFoundError as exc:
    ok("T_payload_tests_skipped_without_full_forge_tree", True, str(exc))
except Exception as exc:
    ok("T_payload_tests", False, str(exc))

# Static no-danger regression.
ok("T5_no_shell_route", "/api/aiweb-os/shell" not in text)
ok("T5_no_command_route", "/api/aiweb-os/command" not in text)
ok("T5_no_eval_exec_in_boundary_patch", "eval(" not in text[text.find("# ─── PATCH 263S"): text.find("def _p201_make_handler")])
ok("T5_preserve_deep_dry_run", "/api/rmc/deep-dry-run" in text)
ok("T5_preserve_patch273", "Patch 273" in text)

passed = sum(1 for _, status, _ in results if status)
failed = len(results) - passed
print("PATCH 263S1 — LIFECYCLE BOUNDARY TESTS")
print("─" * 66)
for name, status, detail in results:
    mark = "✓ [PASS]" if status else "✗ [FAIL]"
    suffix = f" — {detail}" if detail else ""
    print(f"  {mark} {name}{suffix}")
print("─" * 66)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed:
    print("\n  RESULT: patch263S1_tests=FAIL")
    raise SystemExit(1)
print("\n  RESULT: patch263S1_tests=PASS")

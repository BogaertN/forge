#!/usr/bin/env python3
"""Behavior/static tests for Patch 262J1R-Preflight-C12R — Promotion HTTP route repair."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
FAILS = []

def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"[PASS] {name}{(' :: ' + detail) if detail else ''}")
    else:
        print(f"[FAIL] {name}{(' :: ' + detail) if detail else ''}")
        FAILS.append(name)

def main() -> int:
    src = MAIN.read_text(encoding="utf-8")
    check("main_exists", MAIN.exists(), str(MAIN))
    check("promotion_adapter_exists", "def _p262q_rmc_promotion_path_v1" in src)
    for route in [
        "/api/rmc/promotion-path/status",
        "/api/rmc/promotion-path/preview",
        "/api/rmc/promotion-path/promote",
    ]:
        check(f"route_literal_present_{route.rsplit('/',1)[-1]}", route in src)
    dispatcher_pattern = re.compile(
        r"elif\s+_p249_req_path\s+in\s+\([^)]*?/api/rmc/promotion-path/status[^)]*?/api/rmc/promotion-path/preview[^)]*?/api/rmc/promotion-path/promote[^)]*?\):\s*\n\s*body\s*=\s*_j\.dumps\(_p262q_rmc_promotion_path_v1\(self\.path\)\)",
        re.DOTALL,
    )
    check("dispatcher_routes_to_promotion_adapter", bool(dispatcher_pattern.search(src)))
    status_pos = src.find('"/api/rmc/promotion-path/status"')
    forge_pos = src.find('elif self.path == "/api/forge/status"')
    check("promotion_routes_before_forge_status_fallback", status_pos != -1 and forge_pos != -1 and status_pos < forge_pos)
    check("approval_token_still_required", "APPROVE_RMC_PROMOTION" in src)
    # Make sure the promote route did not bypass the adapter directly into commit-only code.
    route_block_start = src.find('elif _p249_req_path in (\n                "/api/rmc/promotion-path/status"')
    route_block = src[route_block_start:route_block_start + 700] if route_block_start != -1 else ""
    check("dispatcher_uses_single_adapter_not_direct_commit", "_p262q_rmc_promotion_commit_kernel" not in route_block and "_p262q_rmc_promotion_path_v1" in route_block)
    check("no_bad_archive_refs", "__pycache__" not in route_block and ".pyc" not in route_block)
    if FAILS:
        print(f"RESULT: promotion_route_C12R_behavior_tests_pass=False failed={len(FAILS)}")
        return 1
    print("RESULT: promotion_route_C12R_behavior_tests_pass=True")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

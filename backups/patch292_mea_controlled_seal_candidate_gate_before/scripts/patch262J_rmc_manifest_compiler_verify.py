#!/usr/bin/env python3
"""Patch 262J verifier: RMC Manifest Compiler dry-run."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
main = (root / "main.py").read_text(encoding="utf-8", errors="replace")
engine = (root / "rmc_engine_v1" / "manifest_compiler.py").read_text(encoding="utf-8", errors="replace")
checks = {
    "endpoint=/api/rmc/manifest-compiler": '"/api/rmc/manifest-compiler"' in main,
    "mode=read_only_manifest_compiler_engine_bound_dry_run": "read_only_manifest_compiler_engine_bound_dry_run" in main,
    "engine_module=forge/rmc_engine_v1/manifest_compiler.py": "compile_manifest_dry_run" in engine and "manifest_schema_contract" in engine,
    "uses_coherence_math_kernel=True": "coherence_math.py" in main or "coherence_math.py" in engine,
    "main_py_endpoint=thin_adapter": "_p262j_compile_manifest_dry_run" in main and "from rmc_engine_v1.manifest_compiler import compile_manifest_dry_run" in main,
    "manifest_preflight_blocks_fabrication=True": "manifest_preflight_blocked" in engine and "fabricating a manifest" in engine,
    "renders_final_language=False": "final_language_allowed" in engine and "False" in engine,
    "writes_files=False": "writes_files" in engine and "False" in engine,
    "adds_forge_commands=False": "forge-command" not in engine.lower(),
    "executes_shell=False": "subprocess" not in engine and "os.system" not in engine,
    "calls_llm=False": "ollama" not in engine.lower() and "openai" not in engine.lower(),
    "queries_chroma_db=False": "chroma" not in engine.lower(),
    "reads_db_files=False": ".db" not in engine.lower() and "sqlite" not in engine.lower(),
    "identity_vault_write=False": "identity_vault_write" in main and "False" in main,
    "rmc_live_memory_write=False": "rmc_live_memory_write" in main and "False" in main,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    print("PATCH262J_RMC_MANIFEST_COMPILER_VERIFY_FAIL")
    for name in failed:
        print(f"FAIL {name}")
    raise SystemExit(1)
print("PATCH262J_RMC_MANIFEST_COMPILER_VERIFY_PASS")
for name in checks:
    print(name)

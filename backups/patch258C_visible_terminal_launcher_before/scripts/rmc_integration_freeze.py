#!/usr/bin/env python3
"""Patch 207 - RMC Integration Freeze + Evidence Collector.

Read-only with respect to live AI.Web / Forge / Identity Vault source trees.
It copies evidence snapshots into Forge memory, computes hashes, compiles Python files,
and optionally runs pytest when tests are present.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
AIWEB_ROOT = HOME / "aiweb"
IDENTITY_ROOT = HOME / "identity-vault"
MEMORY_ROOT = FORGE_ROOT / "memory" / "rmc_integration_freeze_v1"

RMC_MODULES = [
    "phase_state_parser",
    "ancestral_memory",
    "drift_arbitrator",
    "manifest_compiler",
    "output_renderer",
    "echo_gate",
    "rmc_orchestrator",
]

EXPECTED_PRESENT = {
    "phase_state_parser": "S19AE - MISSING in Patch 206 scan; required for phase parsing",
    "ancestral_memory": "S19AF - present; shared memory substrate",
    "drift_arbitrator": "S19AG - MISSING in Patch 206 scan; required for drift arbitration",
    "manifest_compiler": "S19AH - present; manifest compilation",
    "output_renderer": "S19AI - present; output rendering",
    "echo_gate": "S19AJ - MISSING in Patch 206 scan; required for echo validation",
    "rmc_orchestrator": "S19AK - present; RMC coordination",
}

SKIP_DIRS = {"__pycache__", ".pytest_cache", ".git", "node_modules", ".venv", "venv"}


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(HOME))
    except ValueError:
        return str(path)


def safe_copytree(src: Path, dst: Path) -> None:
    def ignore(_directory: str, names: List[str]) -> set[str]:
        return {n for n in names if n in SKIP_DIRS or n.endswith(".pyc")}

    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=ignore)


def walk_files(root: Path) -> List[Path]:
    if not root.exists():
        return []
    out: List[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        cur = Path(current)
        for name in files:
            if name.endswith(".pyc"):
                continue
            out.append(cur / name)
    return sorted(out)


def inspect_tree(root: Path) -> Dict[str, Any]:
    files = walk_files(root)
    py_files = [p for p in files if p.suffix == ".py"]
    test_files = [p for p in py_files if p.name.startswith("test_") or "test" in p.parts]
    total_bytes = sum(p.stat().st_size for p in files if p.exists())
    sample = [rel(p) for p in files[:40]]
    hashes = []
    for p in files[:200]:
        try:
            hashes.append({"path": rel(p), "sha256": sha256_file(p), "bytes": p.stat().st_size})
        except Exception as exc:  # pragma: no cover - evidence collection only
            hashes.append({"path": rel(p), "error": str(exc)})
    return {
        "exists": root.exists(),
        "path": rel(root),
        "file_count": len(files),
        "py_file_count": len(py_files),
        "test_file_count": len(test_files),
        "total_bytes": total_bytes,
        "sample_files": sample,
        "hashes_first_200_files": hashes,
    }


def run_cmd(cmd: List[str], cwd: Path | None = None, timeout: int = 60) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "cmd": cmd,
            "cwd": rel(cwd) if cwd else None,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "cmd": cmd,
            "cwd": rel(cwd) if cwd else None,
            "timeout": timeout,
            "returncode": None,
            "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
            "error": "timeout",
        }
    except Exception as exc:  # pragma: no cover - defensive collector
        return {"cmd": cmd, "cwd": rel(cwd) if cwd else None, "error": str(exc), "returncode": None}


def compile_python_tree(root: Path) -> Dict[str, Any]:
    if not root.exists():
        return {"skipped": True, "reason": "missing"}
    py_files = [str(p) for p in walk_files(root) if p.suffix == ".py"]
    if not py_files:
        return {"skipped": True, "reason": "no_python_files"}
    return run_cmd([sys.executable, "-m", "py_compile", *py_files], cwd=HOME, timeout=120)


def pytest_tree(root: Path) -> Dict[str, Any]:
    if not root.exists():
        return {"skipped": True, "reason": "missing"}
    test_candidates = [p for p in walk_files(root) if p.suffix == ".py" and (p.name.startswith("test_") or "/tests/" in str(p))]
    if not test_candidates:
        return {"skipped": True, "reason": "no_test_files_detected"}
    return run_cmd([sys.executable, "-m", "pytest", str(root)], cwd=HOME, timeout=180)


def find_sensitive_files(root: Path) -> List[str]:
    if not root.exists():
        return []
    hits = []
    sensitive_names = {".env", ".npmrc", ".pypirc", "id_rsa", "id_ed25519"}
    for p in walk_files(root):
        name = p.name.lower()
        if p.name in sensitive_names or name.endswith(".env") or ".env." in name:
            hits.append(rel(p))
        if name.endswith((".db", ".sqlite", ".sqlite3")):
            hits.append(rel(p))
    return sorted(set(hits))


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# RMC Integration Freeze Report")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Snapshot root: `{report['snapshot_root']}`")
    lines.append("")
    lines.append("## Verdict")
    for item in report["verdict"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## RMC Module State")
    for name, entry in report["rmc_modules"].items():
        status = "FOUND" if entry["source_exists"] else "MISSING"
        lines.append(f"- `{name}`: **{status}** — {entry['note']}")
        if entry["source_exists"]:
            lines.append(f"  - source: `{entry['source_path']}`")
            lines.append(f"  - snapshot: `{entry['snapshot_path']}`")
            lines.append(f"  - files: `{entry['tree']['file_count']}`, python: `{entry['tree']['py_file_count']}`, tests: `{entry['tree']['test_file_count']}`")
            comp = entry.get("compile", {})
            if comp.get("skipped"):
                lines.append(f"  - compile: skipped ({comp.get('reason')})")
            else:
                lines.append(f"  - compile returncode: `{comp.get('returncode')}`")
            py = entry.get("pytest", {})
            if py.get("skipped"):
                lines.append(f"  - pytest: skipped ({py.get('reason')})")
            else:
                lines.append(f"  - pytest returncode: `{py.get('returncode')}`")
    lines.append("")
    lines.append("## Standalone Gilligan Freeze")
    g = report["standalone_gilligan"]
    if g["source_exists"]:
        lines.append("- Standalone `gilligan_agent` was found and copied into the freeze snapshot.")
        lines.append(f"- source: `{g['source_path']}`")
        lines.append(f"- snapshot: `{g['snapshot_path']}`")
        lines.append("- Do not delete it yet. Retire it only after Forge-integrated RMC passes.")
    else:
        lines.append("- Standalone `gilligan_agent` was not found.")
    lines.append("")
    lines.append("## Forge Framework")
    for k, v in report["forge_framework"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Identity Vault Hygiene")
    ih = report["identity_vault_hygiene"]
    lines.append(f"- root exists: `{ih['root_exists']}`")
    lines.append(f"- node_modules present: `{ih['node_modules_present']}`")
    lines.append(f"- sensitive/db file hits: `{len(ih['sensitive_or_db_hits'])}`")
    for hit in ih["sensitive_or_db_hits"][:30]:
        lines.append(f"  - `{hit}`")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("Rebuild the three missing RMC modules into a staging path, not directly into live Forge wiring:")
    lines.append("")
    lines.append("`phase_state_parser`, `drift_arbitrator`, `echo_gate`")
    lines.append("")
    lines.append("Then run module tests and only after that create Forge RMC tool wrappers.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    stamp = utc_stamp()
    run_root = MEMORY_ROOT / stamp
    snapshots = run_root / "snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)

    verdict = [
        "Freeze complete before any module movement or deletion.",
        "Do not wire Gilligan into Forge until phase_state_parser, drift_arbitrator, and echo_gate exist and pass compile/tests.",
        "Keep integration read-only/staged until service contracts and RMC tool wrappers are verified.",
    ]

    report: Dict[str, Any] = {
        "timestamp": stamp,
        "home": str(HOME),
        "snapshot_root": rel(run_root),
        "verdict": verdict,
        "rmc_modules": {},
        "standalone_gilligan": {},
        "forge_framework": {},
        "identity_vault_hygiene": {},
    }

    wrappers = AIWEB_ROOT / "runtime_wrappers"
    for name in RMC_MODULES:
        src = wrappers / name
        dst = snapshots / "rmc_modules" / name
        entry: Dict[str, Any] = {
            "note": EXPECTED_PRESENT[name],
            "source_exists": src.exists(),
            "source_path": rel(src),
            "snapshot_path": rel(dst),
        }
        if src.exists():
            safe_copytree(src, dst)
            entry["tree"] = inspect_tree(src)
            entry["snapshot_tree"] = inspect_tree(dst)
            entry["compile"] = compile_python_tree(src)
            entry["pytest"] = pytest_tree(src)
        report["rmc_modules"][name] = entry

    g_src = wrappers / "gilligan_agent"
    g_dst = snapshots / "retired_candidates" / "gilligan_agent"
    g_entry: Dict[str, Any] = {
        "source_exists": g_src.exists(),
        "source_path": rel(g_src),
        "snapshot_path": rel(g_dst),
    }
    if g_src.exists():
        safe_copytree(g_src, g_dst)
        g_entry["tree"] = inspect_tree(g_src)
        g_entry["snapshot_tree"] = inspect_tree(g_dst)
        g_entry["compile"] = compile_python_tree(g_src)
        g_entry["pytest"] = pytest_tree(g_src)
    report["standalone_gilligan"] = g_entry

    for path in [
        FORGE_ROOT / "agents" / "forge" / "agent.py",
        FORGE_ROOT / "agents" / "forge" / "tools.py",
        FORGE_ROOT / "agents" / "forge" / "memory.py",
        FORGE_ROOT / "agents" / "forge" / "context_builder.py",
        FORGE_ROOT / "config" / "tool_registry.json",
    ]:
        report["forge_framework"][rel(path)] = path.exists()

    report["identity_vault_hygiene"] = {
        "root_exists": IDENTITY_ROOT.exists(),
        "node_modules_present": (IDENTITY_ROOT / "node_modules").exists(),
        "sensitive_or_db_hits": find_sensitive_files(IDENTITY_ROOT),
    }

    json_path = run_root / f"{stamp}_rmc_integration_freeze.json"
    md_path = run_root / f"{stamp}_rmc_integration_freeze.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")

    latest_json = MEMORY_ROOT / "latest_rmc_integration_freeze.json"
    latest_md = MEMORY_ROOT / "latest_rmc_integration_freeze.md"
    latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
    latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")

    print("RMC Integration Freeze complete.")
    print(f"Run directory: {run_root}")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print("\nTop rule: do not move/delete/wire modules until this report is reviewed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

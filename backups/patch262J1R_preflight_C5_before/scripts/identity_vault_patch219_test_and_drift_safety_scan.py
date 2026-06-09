#!/usr/bin/env python3
"""
Patch 219 — Identity Vault Testability + Drift Safety Scan
Read-only scan for the remaining Identity Vault normalization gates:
1) DB layer testability/export readiness.
2) Canonical DB path reference hygiene.
3) utils/drift.js unsafe auto-confirm / recursive feedback behavior.

This script writes reports under Forge memory only. It does not modify Identity Vault.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FORGE_ROOT = Path.home() / "forge"
IV_ROOT = Path.home() / "identity-vault"
CONTRACT_PATH = IV_ROOT / "service_contracts" / "identity_vault_readonly_service_contract.draft.json"
MEMORY_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch219_test_and_drift_safety_scan_v1"

RISK_PATTERNS = [
    ("AUTO_CONFIRM_TERM", re.compile(r"auto[_-]?confirm|autoconfirm|auto\s+confirm", re.I)),
    ("CONFIRM_TRUE", re.compile(r"confirm(?:ed|ation)?\s*[:=]\s*true", re.I)),
    ("APPROVE_TRUE", re.compile(r"approv(?:e|ed|al)\s*[:=]\s*true", re.I)),
    ("AUTO_APPROVE", re.compile(r"auto[_-]?approve|auto\s+approve", re.I)),
    ("RECURSIVE_FEEDBACK", re.compile(r"recursive\s+feedback|feedback\s+loop|recursion", re.I)),
    ("BYPASS_CONFIRM", re.compile(r"bypass.*confirm|skip.*confirm|confirm.*bypass", re.I)),
    ("RETURN_TRUE_NEAR_CONFIRM", re.compile(r"confirm[\s\S]{0,120}return\s+true|return\s+true[\s\S]{0,120}confirm", re.I)),
]

CANONICAL_DB_PATTERNS = [
    ("legacy_root_vault_db", re.compile(r"(?<![\w/.-])vault\.db(?![\w.-])")),
    ("canonical_data_identity_vault_db", re.compile(r"data[/\\]identity_vault\.db|identity_vault\.db")),
    ("database_env_reference", re.compile(r"DATABASE_URL|DATABASE_PATH|IDENTITY_VAULT_DB|DB_PATH|process\.env", re.I)),
]

CODE_EXTS = {".js", ".mjs", ".cjs", ".ts", ".json"}
SKIP_DIRS = {"node_modules", ".git", "coverage", "dist", "build", ".next", "logs", "backups"}


def utc_ts() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def read_text(path: Path, max_bytes: int = 2_000_000) -> Optional[str]:
    try:
        if not path.exists() or not path.is_file():
            return None
        data = path.read_bytes()[:max_bytes]
        return data.decode("utf-8", errors="replace")
    except Exception:
        return None


def load_json(path: Path) -> Tuple[bool, Any, Optional[str]]:
    txt = read_text(path)
    if txt is None:
        return False, None, "file missing or unreadable"
    try:
        return True, json.loads(txt), None
    except Exception as e:
        return False, None, str(e)


def run_cmd(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 20) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return {
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
            "ok": proc.returncode == 0,
        }
    except FileNotFoundError as e:
        return {"cmd": cmd, "returncode": None, "stdout_tail": "", "stderr_tail": str(e), "ok": False, "not_found": True}
    except subprocess.TimeoutExpired as e:
        return {"cmd": cmd, "returncode": None, "stdout_tail": e.stdout or "", "stderr_tail": "timeout", "ok": False, "timeout": True}
    except Exception as e:
        return {"cmd": cmd, "returncode": None, "stdout_tail": "", "stderr_tail": repr(e), "ok": False}


def iter_source_files(root: Path) -> List[Path]:
    files: List[Path] = []
    if not root.exists():
        return files
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        base = Path(dirpath)
        for name in filenames:
            p = base / name
            if p.suffix in CODE_EXTS:
                files.append(p)
    return files


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(Path.home()))
    except Exception:
        return str(path)


def line_hits(path: Path, patterns: List[Tuple[str, re.Pattern[str]]], context: int = 0) -> List[Dict[str, Any]]:
    txt = read_text(path)
    hits: List[Dict[str, Any]] = []
    if txt is None:
        return hits
    lines = txt.splitlines()
    for idx, line in enumerate(lines, start=1):
        for code, pat in patterns:
            if pat.search(line):
                item: Dict[str, Any] = {
                    "code": code,
                    "file": rel(path),
                    "line": idx,
                    "text": line.strip()[:240],
                }
                if context:
                    start = max(1, idx - context)
                    end = min(len(lines), idx + context)
                    item["context"] = [f"{n}: {lines[n-1].strip()[:240]}" for n in range(start, end + 1)]
                hits.append(item)
    return hits


def scan_db_layer() -> Dict[str, Any]:
    db_js = IV_ROOT / "db.js"
    txt = read_text(db_js) or ""
    export_hits = []
    export_patterns = [
        ("module_exports", r"module\.exports"),
        ("exports_dot", r"exports\."),
        ("export_default", r"export\s+default"),
        ("export_named", r"export\s+(?:async\s+)?(?:function|const|class|\{)"),
    ]
    for name, pat in export_patterns:
        if re.search(pat, txt):
            export_hits.append(name)
    function_like = sorted(set(re.findall(r"(?:function\s+|const\s+|let\s+|var\s+)([A-Za-z_$][\w$]*)", txt)))[:100]
    key_terms = {
        "uses_sqlite3": bool(re.search(r"sqlite3|better-sqlite3", txt, re.I)),
        "mentions_legacy_vault_db": "vault.db" in txt,
        "mentions_canonical_identity_vault_db": "identity_vault.db" in txt,
        "mentions_data_directory": "data" in txt,
        "mentions_env": "process.env" in txt,
        "has_module_exports": "module.exports" in txt,
        "has_named_exports": bool(re.search(r"exports\.|export\s+", txt)),
    }
    node_check = run_cmd(["node", "--check", str(db_js)], cwd=IV_ROOT) if db_js.exists() else {"ok": False, "stderr_tail": "db.js missing"}
    return {
        "db_js_exists": db_js.exists(),
        "db_js_path": str(db_js),
        "export_hits": export_hits,
        "function_like_names": function_like,
        "key_terms": key_terms,
        "node_check": node_check,
        "testability_ready_static": db_js.exists() and bool(export_hits) and key_terms["uses_sqlite3"],
    }


def scan_tests() -> Dict[str, Any]:
    tests_root = IV_ROOT / "tests"
    test_files: List[Path] = []
    if tests_root.exists():
        for p in tests_root.rglob("*"):
            if p.is_file() and p.suffix in {".js", ".mjs", ".cjs", ".ts"}:
                test_files.append(p)
    package_ok, package, package_err = load_json(IV_ROOT / "package.json")
    scripts = package.get("scripts", {}) if package_ok and isinstance(package, dict) else {}
    test_scripts = {k: v for k, v in scripts.items() if "test" in k.lower() or k in {"lint", "type-check", "validate"}}
    sample_checks = []
    for p in test_files[:20]:
        sample_checks.append({"file": rel(p), "node_check": run_cmd(["node", "--check", str(p)], cwd=IV_ROOT)})
    return {
        "tests_root_exists": tests_root.exists(),
        "test_file_count": len(test_files),
        "test_files_sample": [rel(p) for p in test_files[:50]],
        "package_json_loaded": package_ok,
        "package_json_error": package_err,
        "test_scripts": test_scripts,
        "sample_node_checks": sample_checks,
    }


def scan_drift_safety() -> Dict[str, Any]:
    drift = IV_ROOT / "utils" / "drift.js"
    txt = read_text(drift) or ""
    hits = line_hits(drift, RISK_PATTERNS, context=2)
    node_check = run_cmd(["node", "--check", str(drift)], cwd=IV_ROOT) if drift.exists() else {"ok": False, "stderr_tail": "utils/drift.js missing"}
    risk_codes = sorted(set(h["code"] for h in hits))
    # High-risk if any explicit auto-confirm/approve or bypass pattern appears.
    high_risk_codes = {"AUTO_CONFIRM_TERM", "CONFIRM_TRUE", "AUTO_APPROVE", "BYPASS_CONFIRM", "RETURN_TRUE_NEAR_CONFIRM"}
    high_risk_hits = [h for h in hits if h["code"] in high_risk_codes]
    return {
        "drift_js_exists": drift.exists(),
        "drift_js_path": str(drift),
        "node_check": node_check,
        "risk_hit_count": len(hits),
        "risk_codes": risk_codes,
        "high_risk_hit_count": len(high_risk_hits),
        "hits": hits[:200],
        "requires_patch": bool(high_risk_hits),
    }


def scan_db_path_references() -> Dict[str, Any]:
    files = iter_source_files(IV_ROOT)
    hits: List[Dict[str, Any]] = []
    for p in files:
        if p.name == "package-lock.json":
            continue
        hits.extend(line_hits(p, CANONICAL_DB_PATTERNS, context=0))
    # Summarize by code and file.
    by_code: Dict[str, int] = {}
    by_file: Dict[str, int] = {}
    for h in hits:
        by_code[h["code"]] = by_code.get(h["code"], 0) + 1
        by_file[h["file"]] = by_file.get(h["file"], 0) + 1
    return {
        "scanned_file_count": len(files),
        "hit_count": len(hits),
        "by_code": by_code,
        "files_with_hits": dict(sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0]))[:50]),
        "hits_sample": hits[:100],
        "legacy_vault_db_reference_count": by_code.get("legacy_root_vault_db", 0),
        "canonical_reference_count": by_code.get("canonical_data_identity_vault_db", 0),
    }


def scan_contract() -> Dict[str, Any]:
    ok, data, err = load_json(CONTRACT_PATH)
    if not ok:
        return {"exists": CONTRACT_PATH.exists(), "loaded": False, "error": err}
    required = ["service", "controlled_by", "canonical_database_path", "allowed_reads", "allowed_writes", "forbidden_reads", "forbidden_writes", "future_adapter_rules", "status"]
    missing = [k for k in required if k not in data]
    return {
        "exists": True,
        "loaded": True,
        "missing": missing,
        "status": data.get("status"),
        "controlled_by": data.get("controlled_by"),
        "allowed_writes_empty": data.get("allowed_writes") == [],
        "canonical_database_path": data.get("canonical_database_path"),
        "ready": not missing and data.get("controlled_by") == "Forge" and data.get("allowed_writes") == [],
    }


def make_report(data: Dict[str, Any]) -> str:
    findings = data["findings"]
    lines: List[str] = []
    lines.append("# Identity Vault Patch 219 Testability + Drift Safety Scan")
    lines.append("")
    lines.append(f"Timestamp: `{data['timestamp']}`")
    lines.append(f"Verdict: **{data['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This scan is read-only except for writing reports under Forge memory.")
    lines.append("- It does not modify Identity Vault code, databases, .env, node_modules, Forge registry, RMC memory, or agent identity activation state.")
    lines.append("- It does not read .env secret values.")
    lines.append("")
    lines.append("## Contract / Adapter Baseline")
    c = data["contract"]
    lines.append(f"- contract loaded: `{c.get('loaded')}`")
    lines.append(f"- contract ready: `{c.get('ready')}`")
    lines.append(f"- status: `{c.get('status')}`")
    lines.append(f"- canonical DB: `{c.get('canonical_database_path')}`")
    lines.append(f"- allowed writes empty: `{c.get('allowed_writes_empty')}`")
    lines.append("")
    lines.append("## DB Layer Testability Scan")
    db = data["db_layer"]
    lines.append(f"- `db.js` exists: `{db.get('db_js_exists')}`")
    lines.append(f"- static testability ready: `{db.get('testability_ready_static')}`")
    lines.append(f"- export hits: `{', '.join(db.get('export_hits') or []) or 'none'}`")
    lines.append(f"- key terms: `{db.get('key_terms')}`")
    node = db.get("node_check", {})
    lines.append(f"- node syntax check ok: `{node.get('ok')}` returncode=`{node.get('returncode')}`")
    if node.get("stderr_tail"):
        lines.append("```text")
        lines.append(str(node.get("stderr_tail"))[:1000])
        lines.append("```")
    lines.append("")
    lines.append("## Test Inventory")
    tests = data["tests"]
    lines.append(f"- tests root exists: `{tests.get('tests_root_exists')}`")
    lines.append(f"- test file count: `{tests.get('test_file_count')}`")
    lines.append(f"- test-related package scripts: `{tests.get('test_scripts')}`")
    lines.append("- test file sample:")
    for f in tests.get("test_files_sample", [])[:25]:
        lines.append(f"  - `{f}`")
    if not tests.get("test_files_sample"):
        lines.append("  - none found")
    lines.append("")
    lines.append("## Canonical DB Path Reference Scan")
    refs = data["db_path_references"]
    lines.append(f"- scanned source files: `{refs.get('scanned_file_count')}`")
    lines.append(f"- total DB path hits: `{refs.get('hit_count')}`")
    lines.append(f"- legacy `vault.db` references: `{refs.get('legacy_vault_db_reference_count')}`")
    lines.append(f"- canonical `identity_vault.db` references: `{refs.get('canonical_reference_count')}`")
    lines.append(f"- hits by code: `{refs.get('by_code')}`")
    if refs.get("files_with_hits"):
        lines.append("- files with DB path/env references:")
        for f, n in refs.get("files_with_hits", {}).items():
            lines.append(f"  - `{f}`: `{n}`")
    lines.append("")
    lines.append("## Drift Safety Scan")
    drift = data["drift_safety"]
    lines.append(f"- `utils/drift.js` exists: `{drift.get('drift_js_exists')}`")
    lines.append(f"- node syntax check ok: `{drift.get('node_check', {}).get('ok')}` returncode=`{drift.get('node_check', {}).get('returncode')}`")
    lines.append(f"- risk hit count: `{drift.get('risk_hit_count')}`")
    lines.append(f"- high-risk hit count: `{drift.get('high_risk_hit_count')}`")
    lines.append(f"- risk codes: `{', '.join(drift.get('risk_codes') or []) or 'none'}`")
    lines.append(f"- requires safety patch: `{drift.get('requires_patch')}`")
    if drift.get("hits"):
        lines.append("- drift risk sample:")
        for h in drift.get("hits", [])[:30]:
            lines.append(f"  - `{h['code']}` `{h['file']}:{h['line']}` — `{h['text']}`")
    lines.append("")
    lines.append("## Findings")
    for item in findings:
        lines.append(f"- **{item['level']}** `{item['code']}` — {item['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    if data["verdict"] == "PASS":
        lines.append("Proceed to a narrow patch that prepares Identity Vault read-only preview tool registration, or continue normalization with a focused DB/test export patch if needed.")
    else:
        lines.append("Create a focused normalization patch plan before any adapter tool registration: fix DB testability/export issues and/or disable unsafe drift auto-confirm behavior. Do not activate agent identities.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ts = utc_ts()
    run_dir = MEMORY_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    data: Dict[str, Any] = {
        "timestamp": ts,
        "identity_vault_root": str(IV_ROOT),
        "contract": scan_contract(),
        "db_layer": scan_db_layer(),
        "tests": scan_tests(),
        "db_path_references": scan_db_path_references(),
        "drift_safety": scan_drift_safety(),
        "no_mutation_claim": {
            "env_secret_values_read": False,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "forge_registry_modified": False,
        },
    }

    findings: List[Dict[str, str]] = []
    if not IV_ROOT.exists():
        findings.append({"level": "FAIL", "code": "IV_ROOT_MISSING", "message": "Identity Vault root was not found."})
    if not data["contract"].get("ready"):
        findings.append({"level": "WARN", "code": "IV_CONTRACT_NOT_READY", "message": "Read-only service contract is not ready."})
    if not data["db_layer"].get("testability_ready_static"):
        findings.append({"level": "WARN", "code": "IV_DB_LAYER_TESTABILITY_WEAK", "message": "db.js may not expose a clean testable interface or sqlite usage was not detected."})
    if data["db_path_references"].get("legacy_vault_db_reference_count", 0) > 0:
        findings.append({"level": "WARN", "code": "IV_LEGACY_DB_REFERENCES", "message": "Code still references root-level vault.db; canonical path should be data/identity_vault.db unless migration review says otherwise."})
    if data["drift_safety"].get("requires_patch"):
        findings.append({"level": "WARN", "code": "IV_DRIFT_AUTO_CONFIRM_RISK", "message": "utils/drift.js contains high-risk confirmation/auto-approval patterns that should be disabled or gated."})
    if data["tests"].get("test_file_count", 0) == 0:
        findings.append({"level": "WARN", "code": "IV_TEST_FILES_NOT_FOUND", "message": "No test files were found under tests/."})
    if data["tests"].get("test_file_count", 0) > 0:
        findings.append({"level": "INFO", "code": "IV_TEST_FILES_PRESENT", "message": "Test files exist and can be used after the DB layer is normalized."})
    if data["drift_safety"].get("drift_js_exists") and not data["drift_safety"].get("requires_patch"):
        findings.append({"level": "INFO", "code": "IV_DRIFT_NO_HIGH_RISK_AUTO_CONFIRM", "message": "No high-risk auto-confirm pattern was found by this static scan."})

    # This is a scan, so WARN is acceptable and expected if remaining normalization work exists.
    verdict = "FAIL" if any(f["level"] == "FAIL" for f in findings) else ("WARN" if any(f["level"] == "WARN" for f in findings) else "PASS")
    data["findings"] = findings
    data["verdict"] = verdict

    json_path = run_dir / f"{ts}_identity_vault_patch219_test_and_drift_safety_scan.json"
    md_path = run_dir / f"{ts}_identity_vault_patch219_test_and_drift_safety_scan.md"
    latest_json = MEMORY_ROOT / "latest_identity_vault_patch219_test_and_drift_safety_scan.json"
    latest_md = MEMORY_ROOT / "latest_identity_vault_patch219_test_and_drift_safety_scan.md"

    json_text = json.dumps(data, indent=2, sort_keys=True)
    md_text = make_report(data)
    json_path.write_text(json_text + "\n", encoding="utf-8")
    md_path.write_text(md_text, encoding="utf-8")
    latest_json.write_text(json_text + "\n", encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    print("Identity Vault Patch 219 testability + drift safety scan complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

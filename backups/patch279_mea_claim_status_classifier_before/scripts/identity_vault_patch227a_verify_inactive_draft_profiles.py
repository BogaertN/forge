#!/usr/bin/env python3
"""
Patch 227A — Identity Vault inactive draft profile verification.

Read-only verifier for Patch 227. Verifies that nic_bogaert, gilligan.local,
athena.local, and neo.local exist in the canonical Identity Vault database as
inactive draft profiles. Writes reports only under Forge memory.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sqlite3
import stat
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
IDENTITY_ROOT = HOME / "identity-vault"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
TOOL_REGISTRY = FORGE_ROOT / "config" / "tool_registry.json"
ENV_PATH = IDENTITY_ROOT / ".env"
RMC_CANDIDATE_ROOTS = [
    HOME / "aiweb" / "rmc",
    HOME / "aiweb" / "memory" / "rmc",
    HOME / "forge" / "memory" / "rmc",
]
REPORT_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch227a_inactive_profile_verify_v1"

EXPECTED_USER_ID = "nic_bogaert"
EXPECTED_AGENTS = {
    "gilligan.local": "rmc/agents/gilligan.local",
    "athena.local": "rmc/agents/athena.local",
    "neo.local": "rmc/agents/neo.local",
}


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def iso_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_meta(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(stat.S_IMODE(st.st_mode)),
    }


def open_ro_sqlite(path: Path) -> Tuple[Optional[sqlite3.Connection], Dict[str, Any]]:
    info: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "opened_readonly": False, "ok": False, "error": None}
    if not path.exists():
        info["error"] = "missing"
        return None, info
    try:
        uri = f"file:{path}?mode=ro&immutable=1"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        info["opened_readonly"] = True
        info["ok"] = True
        return conn, info
    except Exception as exc:  # pragma: no cover - diagnostic path
        info["error"] = repr(exc)
        return None, info


def table_names(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [r[0] for r in rows]


def row_counts(conn: sqlite3.Connection) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for name in table_names(conn):
        try:
            counts[name] = int(conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0])
        except Exception:
            counts[name] = -1
    return counts


def fetch_one_by(conn: sqlite3.Connection, table: str, column: str, value: str) -> Optional[Dict[str, Any]]:
    row = conn.execute(f'SELECT * FROM "{table}" WHERE "{column}" = ? LIMIT 1', (value,)).fetchone()
    if row is None:
        return None
    return dict(row)


def parse_json_field(raw: Any) -> Tuple[bool, Optional[Any], Optional[str]]:
    if raw is None:
        return False, None, "missing"
    if isinstance(raw, (dict, list)):
        return True, raw, None
    try:
        return True, json.loads(str(raw)), None
    except Exception as exc:
        return False, None, repr(exc)


def hash_candidates(raw: str, parsed: Any) -> Dict[str, str]:
    candidates: Dict[str, str] = {}
    raw_text = raw if isinstance(raw, str) else str(raw)
    candidates["sha256_raw"] = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    try:
        candidates["sha256_sorted_compact"] = hashlib.sha256(
            json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        candidates["sha256_sorted_pretty"] = hashlib.sha256(
            json.dumps(parsed, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
    except Exception:
        pass
    return candidates


def verify_hash(row: Dict[str, Any]) -> Dict[str, Any]:
    raw = row.get("operational_profile_json")
    stored = row.get("profile_hash")
    ok_json, parsed, err = parse_json_field(raw)
    out: Dict[str, Any] = {
        "json_ok": ok_json,
        "json_error": err,
        "stored_hash": stored,
        "hash_ok": False,
        "matched_method": None,
        "hash16": str(stored)[:16] if stored else None,
    }
    if not ok_json or parsed is None or not stored:
        return out
    candidates = hash_candidates(str(raw), parsed)
    for method, value in candidates.items():
        if value == stored:
            out["hash_ok"] = True
            out["matched_method"] = method
            break
    out["profile_keys"] = sorted(list(parsed.keys())) if isinstance(parsed, dict) else []
    return out


def pointer_only(ns: Any) -> bool:
    if not isinstance(ns, str) or not ns:
        return False
    if ns.startswith("/") or ".." in ns or "://" in ns or ns.startswith("~"):
        return False
    return ns.startswith("rmc/agents/")


def namespace_paths_for(ns: str) -> List[str]:
    rel = Path(ns)
    return [str(root / rel.relative_to("rmc")) if ns.startswith("rmc/") else str(root / rel) for root in RMC_CANDIDATE_ROOTS]


def namespace_exists_any(ns: str) -> bool:
    return any(Path(p).exists() for p in namespace_paths_for(ns))


def bool_int(v: Any) -> int:
    try:
        return int(v)
    except Exception:
        return 999


def verify_user(conn: sqlite3.Connection) -> Dict[str, Any]:
    row = fetch_one_by(conn, "user_profiles", "user_id", EXPECTED_USER_ID)
    out: Dict[str, Any] = {"user_id": EXPECTED_USER_ID, "exists": row is not None, "ok": False}
    if row is None:
        out["missing_reason"] = "row_not_found"
        return out
    hash_info = verify_hash(row)
    out.update({
        "canonical_name": row.get("canonical_name"),
        "is_active": bool_int(row.get("is_active")),
        "profile_schema_version": row.get("profile_schema_version"),
        "hash": hash_info,
        "json_ok": hash_info.get("json_ok", False),
        "hash_ok": hash_info.get("hash_ok", False),
    })
    out["ok"] = bool(out["exists"] and out["is_active"] == 0 and out["json_ok"] and out["hash_ok"])
    return out


def verify_agent(conn: sqlite3.Connection, agent_id: str, expected_ns: str) -> Dict[str, Any]:
    row = fetch_one_by(conn, "agent_profiles", "agent_id", agent_id)
    out: Dict[str, Any] = {"agent_id": agent_id, "exists": row is not None, "ok": False}
    if row is None:
        out["missing_reason"] = "row_not_found"
        return out
    hash_info = verify_hash(row)
    ns = row.get("rmc_namespace")
    ns_paths = namespace_paths_for(str(ns)) if isinstance(ns, str) else []
    ns_exists = namespace_exists_any(str(ns)) if isinstance(ns, str) else False
    out.update({
        "canonical_name": row.get("canonical_name"),
        "role": row.get("role"),
        "activation_state": row.get("activation_state"),
        "is_active": bool_int(row.get("is_active")),
        "rmc_namespace": ns,
        "expected_namespace": expected_ns,
        "namespace_pointer_only": pointer_only(ns),
        "namespace_matches_expected": ns == expected_ns,
        "namespace_candidate_paths": ns_paths,
        "namespace_directory_exists": ns_exists,
        "profile_schema_version": row.get("profile_schema_version"),
        "hash": hash_info,
        "json_ok": hash_info.get("json_ok", False),
        "hash_ok": hash_info.get("hash_ok", False),
    })
    out["ok"] = bool(
        out["exists"]
        and out["activation_state"] == "inactive_draft"
        and out["is_active"] == 0
        and out["namespace_pointer_only"]
        and out["namespace_matches_expected"]
        and not out["namespace_directory_exists"]
        and out["json_ok"]
        and out["hash_ok"]
    )
    return out


def write_reports(run_dir: Path, report: Dict[str, Any]) -> Tuple[Path, Path]:
    run_dir.mkdir(parents=True, exist_ok=True)
    stamp = report["timestamp"]
    json_path = run_dir / f"{stamp}_identity_vault_patch227a_inactive_profile_verify.json"
    md_path = run_dir / f"{stamp}_identity_vault_patch227a_inactive_profile_verify.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    latest_json = REPORT_ROOT / "latest_identity_vault_patch227a_inactive_profile_verify.json"
    latest_md = REPORT_ROOT / "latest_identity_vault_patch227a_inactive_profile_verify.md"
    latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
    latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    return md_path, json_path


def render_markdown(r: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Identity Vault Patch 227A Inactive Draft Profile Verification")
    lines.append("")
    lines.append(f"Timestamp: `{r['timestamp']}`")
    lines.append(f"Verdict: **{r['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This patch independently verifies inactive draft profile rows seeded by Patch 227.")
    lines.append("- It writes reports only under Forge memory.")
    lines.append("- It does not write Identity Vault databases, create or activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.")
    lines.append("")
    lines.append("## Canonical Database")
    c = r["canonical"]
    lines.append(f"- path: `{c.get('path')}` opened_readonly=`{c.get('opened_readonly')}` ok=`{c.get('ok')}`")
    lines.append(f"- rows: `{c.get('row_counts')}`")
    lines.append("")
    lines.append("## User Profile Verification")
    u = r["user_verification"]
    lines.append(f"- user `{u.get('user_id')}` exists=`{u.get('exists')}` is_active=`{u.get('is_active')}` json_ok=`{u.get('json_ok')}` hash_ok=`{u.get('hash_ok')}` ok=`{u.get('ok')}`")
    lines.append("")
    lines.append("## Agent Profile Verification")
    for a in r["agent_verification"]:
        lines.append(
            f"- agent `{a.get('agent_id')}` exists=`{a.get('exists')}` activation_state=`{a.get('activation_state')}` "
            f"is_active=`{a.get('is_active')}` rmc_namespace=`{a.get('rmc_namespace')}` pointer_only=`{a.get('namespace_pointer_only')}` "
            f"namespace_exists=`{a.get('namespace_directory_exists')}` json_ok=`{a.get('json_ok')}` hash_ok=`{a.get('hash_ok')}` ok=`{a.get('ok')}`"
        )
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in r["safety"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    for f in r["findings"]:
        lines.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    if r["verdict"] == "PASS":
        lines.append("Manually test `forge-agent-list` and `forge-agent-show gilligan.local`, then proceed to Patch 228 full profile read-only adapter upgrade.")
    else:
        lines.append("Do not proceed to adapter upgrade. Review failed verification details first.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ts = utc_stamp()
    run_dir = REPORT_ROOT / ts
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    before = {
        "env_stat": stat_meta(ENV_PATH),
        "canonical_db_sha": sha256_file(CANONICAL_DB),
        "legacy_db_sha": sha256_file(LEGACY_DB),
        "tool_registry_sha": sha256_file(TOOL_REGISTRY),
        "rmc_existing_paths": sorted([str(p) for root in RMC_CANDIDATE_ROOTS if root.exists() for p in root.rglob("*") if p.exists()])[:2000],
    }

    conn, canonical_info = open_ro_sqlite(CANONICAL_DB)
    legacy_conn, legacy_info = open_ro_sqlite(LEGACY_DB)
    report: Dict[str, Any] = {
        "timestamp": ts,
        "generated_at_utc": iso_now(),
        "boundary": "read-only verification; reports only; no identity activation",
        "canonical": canonical_info,
        "legacy": legacy_info,
        "user_verification": {},
        "agent_verification": [],
        "safety": {},
        "findings": [],
        "verdict": "FAIL",
    }

    if conn is not None:
        report["canonical"]["tables"] = table_names(conn)
        report["canonical"]["row_counts"] = row_counts(conn)
        report["user_verification"] = verify_user(conn)
        report["agent_verification"] = [verify_agent(conn, aid, ns) for aid, ns in EXPECTED_AGENTS.items()]
        conn.close()
    if legacy_conn is not None:
        report["legacy"]["tables"] = table_names(legacy_conn)
        report["legacy"]["row_counts"] = row_counts(legacy_conn)
        legacy_conn.close()

    after = {
        "env_stat": stat_meta(ENV_PATH),
        "canonical_db_sha": sha256_file(CANONICAL_DB),
        "legacy_db_sha": sha256_file(LEGACY_DB),
        "tool_registry_sha": sha256_file(TOOL_REGISTRY),
        "rmc_existing_paths": sorted([str(p) for root in RMC_CANDIDATE_ROOTS if root.exists() for p in root.rglob("*") if p.exists()])[:2000],
    }

    agent_checks = report.get("agent_verification", [])
    user_ok = bool(report.get("user_verification", {}).get("ok"))
    agents_ok = all(bool(a.get("ok")) for a in agent_checks) and len(agent_checks) == 3
    no_namespaces_written = before["rmc_existing_paths"] == after["rmc_existing_paths"]
    row_counts = report.get("canonical", {}).get("row_counts", {})
    rows_expected = row_counts.get("agent_profiles") == 3 and row_counts.get("user_profiles") == 1

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env_stat"] == after["env_stat"],
        "canonical_db_sha_unchanged_during_verify": before["canonical_db_sha"] == after["canonical_db_sha"],
        "legacy_db_sha_unchanged_during_verify": before["legacy_db_sha"] == after["legacy_db_sha"],
        "tool_registry_sha_unchanged": before["tool_registry_sha"] == after["tool_registry_sha"],
        "identity_vault_database_write_performed": False,
        "profiles_created_by_verifier": False,
        "agent_identity_activation_performed": False,
        "all_seeded_profiles_inactive": user_ok and agents_ok,
        "rmc_memory_write_performed": False,
        "rmc_fingerprints_unchanged": no_namespaces_written,
        "forge_tool_registry_modified": False,
        "row_counts_expected": rows_expected,
    }
    report["safety"] = safety

    if user_ok:
        report["findings"].append({"level": "INFO", "code": "IV_USER_PROFILE_INACTIVE_OK", "message": "nic_bogaert exists as an inactive user profile with valid operational JSON and hash."})
    else:
        report["findings"].append({"level": "FAIL", "code": "IV_USER_PROFILE_VERIFY_FAILED", "message": "nic_bogaert is missing or failed inactive/hash/JSON checks."})
    if agents_ok:
        report["findings"].append({"level": "INFO", "code": "IV_AGENT_PROFILES_INACTIVE_OK", "message": "Gilligan, Athena, and Neo exist as inactive draft profiles with valid JSON, hashes, and RMC namespace pointers."})
    else:
        report["findings"].append({"level": "FAIL", "code": "IV_AGENT_PROFILE_VERIFY_FAILED", "message": "One or more agent profiles failed inactive/hash/namespace checks."})
    if no_namespaces_written:
        report["findings"].append({"level": "INFO", "code": "IV_NO_RMC_NAMESPACE_WRITES", "message": "RMC namespace paths were not created or modified by this verifier."})
    else:
        report["findings"].append({"level": "FAIL", "code": "IV_RMC_FINGERPRINT_CHANGED", "message": "RMC path fingerprint changed during verification."})

    safety_ok = all(bool(v) for v in safety.values())
    if safety_ok:
        report["findings"].append({"level": "INFO", "code": "IV_NO_MUTATION_VERIFY_OK", "message": "Verification was read-only; DB hashes, .env metadata, RMC fingerprints, and registry stayed unchanged."})
    else:
        report["findings"].append({"level": "FAIL", "code": "IV_NO_MUTATION_VERIFY_FAILED", "message": "One or more no-mutation checks failed."})

    report["verdict"] = "PASS" if (canonical_info.get("ok") and user_ok and agents_ok and safety_ok) else "FAIL"

    md_path, json_path = write_reports(run_dir, report)
    print("Identity Vault Patch 227A inactive draft profile verification complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {REPORT_ROOT / 'latest_identity_vault_patch227a_inactive_profile_verify.md'}")
    print(f"JSON report: {REPORT_ROOT / 'latest_identity_vault_patch227a_inactive_profile_verify.json'}")
    print(f"Verdict: {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

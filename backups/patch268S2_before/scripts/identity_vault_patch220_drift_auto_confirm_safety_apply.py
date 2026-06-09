#!/usr/bin/env python3
# identity_vault_patch220_drift_auto_confirm_safety_apply.py
# Purpose: Disable unsafe Identity Vault recursive drift auto-confirm behavior.
# Boundary: This patch modifies only identity-vault/utils/drift.js after backup.
# It does not read .env secret values, write databases, register tools, or activate agent identities.

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any

FORGE_ROOT = Path.home() / "forge"
IV_ROOT = Path.home() / "identity-vault"
DRIFT_PATH = IV_ROOT / "utils" / "drift.js"
OUT_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch220_drift_auto_confirm_safety_v1"
BACKUP_ROOT = FORGE_ROOT / "backups" / "patch220_identity_vault_drift_auto_confirm_before"

PATCH_NAME = "patch220_identity_vault_drift_auto_confirm_safety_apply"
SAFE_ENV_FLAG = "IDENTITY_VAULT_ALLOW_DRIFT_AUTO_CONFIRM"
SAFE_ENV_TOKEN = "IDENTITY_VAULT_DRIFT_APPROVAL_TOKEN"
SAFE_ENV_TOKEN_VALUE = "MANUAL_REVIEW_APPROVED"


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(cmd: List[str], cwd: Path | None = None) -> Dict[str, Any]:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"cmd": cmd, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


def detect_risk(text: str) -> Dict[str, Any]:
    # High-risk means auto-confirm is forced by unconditional true, or the exact old pattern survives.
    lines = text.splitlines()
    hits = []
    for idx, line in enumerate(lines, start=1):
        low = line.lower()
        if "auto_confirm" in low or "auto-confirm" in low or "recursive feedback" in low or "confirm" in low:
            risk = "INFO"
            if "|| true" in line or "&& true" in line or re.search(r"\bconst\s+confirm\s*=\s*true\b", line):
                risk = "HIGH"
            elif "auto_confirm" in low:
                risk = "MEDIUM"
            hits.append({"line": idx, "risk": risk, "text": line.strip()[:240]})
    return {
        "risk_hit_count": len(hits),
        "high_risk_hit_count": sum(1 for h in hits if h["risk"] == "HIGH"),
        "hits": hits[:20],
        "forced_true_present": "|| true" in text or "&& true" in text or bool(re.search(r"\bconst\s+confirm\s*=\s*true\b", text)),
        "legacy_auto_confirm_env_present": "AUTO_CONFIRM" in text,
        "safe_env_flag_present": SAFE_ENV_FLAG in text,
        "safe_env_token_present": SAFE_ENV_TOKEN in text,
    }


def apply_patch(text: str) -> tuple[str, List[str]]:
    changes: List[str] = []
    original = text

    # Exact high-risk line seen in Patch 219:
    exact_old = "const confirm = process.env.AUTO_CONFIRM === 'true' || true; // Safety: Opt-in auto"
    exact_new = (
        f"const confirm = process.env.{SAFE_ENV_FLAG} === 'true' "
        f"&& process.env.{SAFE_ENV_TOKEN} === '{SAFE_ENV_TOKEN_VALUE}'; "
        "// Safety: explicit opt-in only; never auto-confirm by default"
    )
    if exact_old in text:
        text = text.replace(exact_old, exact_new)
        changes.append("Replaced exact unsafe AUTO_CONFIRM || true confirmation line.")

    # More general but still narrow repair for any const confirm assignment that contains "|| true".
    pattern = re.compile(r"^(\s*const\s+confirm\s*=\s*)(.*\|\|\s*true\s*;.*)$", re.MULTILINE)
    def repl(match: re.Match) -> str:
        changes.append("Replaced a const confirm assignment containing unconditional || true.")
        indent = match.group(1)
        prefix_ws = re.match(r"^(\s*)", match.group(0)).group(1)
        return (
            f"{prefix_ws}const confirm = process.env.{SAFE_ENV_FLAG} === 'true' "
            f"&& process.env.{SAFE_ENV_TOKEN} === '{SAFE_ENV_TOKEN_VALUE}'; "
            "// Safety: explicit opt-in only; never auto-confirm by default"
        )
    text = pattern.sub(repl, text)

    # If the file has recursive feedback but no clear safe marker, add a tiny comment marker near the top.
    if "Recursive feedback" in text or "recursive feedback" in text:
        marker = "// PATCH220 SAFETY: recursive drift feedback must never auto-confirm without explicit operator approval."
        if marker not in text:
            lines = text.splitlines()
            insert_at = 1 if lines and lines[0].startswith("//") else 0
            lines.insert(insert_at, marker)
            text = "\n".join(lines) + ("\n" if original.endswith("\n") else "")
            changes.append("Added Patch 220 safety marker comment.")

    return text, changes


def main() -> int:
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    run_dir = OUT_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    report: Dict[str, Any] = {
        "patch": PATCH_NAME,
        "timestamp": ts,
        "boundary": {
            "modifies": ["identity-vault/utils/drift.js"],
            "does_not_modify": [
                "Identity Vault databases",
                ".env",
                "node_modules",
                "Forge registry",
                "RMC memory",
                "AI.Web wrappers",
                "agent identity activation state",
            ],
            "env_secret_values_read": False,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
        },
        "paths": {
            "identity_vault_root": str(IV_ROOT),
            "drift_js": str(DRIFT_PATH),
            "backup_root": str(BACKUP_ROOT / ts),
        },
        "checks": {},
        "findings": [],
    }

    if not DRIFT_PATH.exists():
        report["verdict"] = "FAIL"
        report["findings"].append({"level": "FAIL", "code": "IV_DRIFT_JS_MISSING", "message": f"{DRIFT_PATH} does not exist."})
        return finish(report, run_dir)

    before_hash = sha256_file(DRIFT_PATH)
    before_text = DRIFT_PATH.read_text(encoding="utf-8", errors="replace")
    before_risk = detect_risk(before_text)

    backup_dir = BACKUP_ROOT / ts
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DRIFT_PATH, backup_dir / "drift.js")

    after_text, changes = apply_patch(before_text)
    changed = after_text != before_text
    if changed:
        DRIFT_PATH.write_text(after_text, encoding="utf-8")

    after_hash = sha256_file(DRIFT_PATH)
    after_text_read = DRIFT_PATH.read_text(encoding="utf-8", errors="replace")
    after_risk = detect_risk(after_text_read)

    node_syntax = run(["node", "--check", str(DRIFT_PATH)], cwd=IV_ROOT)

    report["checks"].update({
        "drift_js_exists": True,
        "backup_created": (backup_dir / "drift.js").exists(),
        "before_sha256": before_hash,
        "after_sha256": after_hash,
        "changed": changed,
        "changes": changes,
        "before_risk": before_risk,
        "after_risk": after_risk,
        "node_syntax_ok": node_syntax["returncode"] == 0,
        "node_syntax_returncode": node_syntax["returncode"],
        "node_syntax_stderr_tail": node_syntax["stderr"][-1000:],
        "safe_env_flag": SAFE_ENV_FLAG,
        "safe_env_token": SAFE_ENV_TOKEN,
        "safe_env_token_value_required": SAFE_ENV_TOKEN_VALUE,
    })

    if node_syntax["returncode"] != 0:
        # Restore on syntax failure.
        shutil.copy2(backup_dir / "drift.js", DRIFT_PATH)
        report["verdict"] = "FAIL"
        report["findings"].append({"level": "FAIL", "code": "IV_DRIFT_JS_SYNTAX_FAIL_RESTORED", "message": "node --check failed; original drift.js restored from backup."})
        report["checks"]["restored_after_syntax_failure"] = True
        report["checks"]["restored_sha256"] = sha256_file(DRIFT_PATH)
    elif after_risk["forced_true_present"] or after_risk["high_risk_hit_count"] > 0:
        report["verdict"] = "WARN"
        report["findings"].append({"level": "WARN", "code": "IV_DRIFT_AUTO_CONFIRM_HIGH_RISK_REMAINS", "message": "A forced true confirmation pattern remains in utils/drift.js."})
    elif changed:
        report["verdict"] = "PASS"
        report["findings"].append({"level": "INFO", "code": "IV_DRIFT_AUTO_CONFIRM_DISABLED", "message": "Unsafe recursive drift auto-confirm pattern was replaced with explicit two-factor environment gating."})
    else:
        report["verdict"] = "PASS"
        report["findings"].append({"level": "INFO", "code": "IV_DRIFT_AUTO_CONFIRM_ALREADY_SAFE", "message": "No forced auto-confirm pattern was present; no file change was needed."})

    report["findings"].append({"level": "INFO", "code": "IV_DRIFT_SAFETY_GATE", "message": f"Auto-confirm now requires {SAFE_ENV_FLAG}=true and {SAFE_ENV_TOKEN}={SAFE_ENV_TOKEN_VALUE} if the code path is used."})

    return finish(report, run_dir)


def finish(report: Dict[str, Any], run_dir: Path) -> int:
    json_path = run_dir / f"{report['timestamp']}_identity_vault_patch220_drift_auto_confirm_safety.json"
    md_path = run_dir / f"{report['timestamp']}_identity_vault_patch220_drift_auto_confirm_safety.md"
    latest_json = OUT_ROOT / "latest_identity_vault_patch220_drift_auto_confirm_safety.json"
    latest_md = OUT_ROOT / "latest_identity_vault_patch220_drift_auto_confirm_safety.md"

    write_text(json_path, json.dumps(report, indent=2, sort_keys=True))
    write_text(latest_json, json.dumps(report, indent=2, sort_keys=True))

    md = render_md(report)
    write_text(md_path, md)
    write_text(latest_md, md)

    print("Identity Vault Patch 220 drift auto-confirm safety apply complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {report.get('verdict', 'UNKNOWN')}")
    return 0 if report.get("verdict") in {"PASS", "WARN"} else 1


def render_md(report: Dict[str, Any]) -> str:
    c = report.get("checks", {})
    lines: List[str] = []
    lines.append("# Identity Vault Patch 220 Drift Auto-Confirm Safety Apply")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report.get('verdict', 'UNKNOWN')}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This patch modifies only `identity-vault/utils/drift.js`, and only after backup.")
    lines.append("- It does not modify Identity Vault databases, `.env`, `node_modules`, Forge registry, RMC memory, AI.Web wrappers, or agent identity activation state.")
    lines.append("- It does not read `.env` secret values.")
    lines.append("")
    lines.append("## Backup")
    lines.append(f"- backup root: `{report['paths'].get('backup_root')}`")
    lines.append(f"- backup created: `{c.get('backup_created')}`")
    lines.append("")
    lines.append("## Change Summary")
    lines.append(f"- changed: `{c.get('changed')}`")
    lines.append(f"- before sha256: `{c.get('before_sha256')}`")
    lines.append(f"- after sha256: `{c.get('after_sha256')}`")
    for change in c.get("changes", []):
        lines.append(f"- {change}")
    if not c.get("changes"):
        lines.append("- No code change was needed.")
    lines.append("")
    lines.append("## Drift Safety Result")
    before = c.get("before_risk", {})
    after = c.get("after_risk", {})
    lines.append(f"- forced true before: `{before.get('forced_true_present')}`")
    lines.append(f"- forced true after: `{after.get('forced_true_present')}`")
    lines.append(f"- high-risk hits before: `{before.get('high_risk_hit_count')}`")
    lines.append(f"- high-risk hits after: `{after.get('high_risk_hit_count')}`")
    lines.append(f"- legacy `AUTO_CONFIRM` reference after: `{after.get('legacy_auto_confirm_env_present')}`")
    lines.append(f"- safe env flag present after: `{after.get('safe_env_flag_present')}`")
    lines.append(f"- safe env token present after: `{after.get('safe_env_token_present')}`")
    lines.append("")
    lines.append("## Syntax Check")
    lines.append(f"- `node --check utils/drift.js`: `{c.get('node_syntax_ok')}` returncode=`{c.get('node_syntax_returncode')}`")
    if c.get("node_syntax_stderr_tail"):
        lines.append("```text")
        lines.append(c.get("node_syntax_stderr_tail"))
        lines.append("```")
    lines.append("")
    lines.append("## Required Manual Override Gate")
    lines.append(f"- `{c.get('safe_env_flag')}` must equal `true`")
    lines.append(f"- `{c.get('safe_env_token')}` must equal `{c.get('safe_env_token_value_required')}`")
    lines.append("- Without both, recursive drift feedback must not auto-confirm.")
    lines.append("")
    lines.append("## Findings")
    for f in report.get("findings", []):
        lines.append(f"- **{f.get('level')}** `{f.get('code')}` — {f.get('message')}")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("Run a follow-up scan for DB canonical path/testability. Then create AI.Web service contract files before any broader connector registration.")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

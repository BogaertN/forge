#!/usr/bin/env python3
"""
Patch 226C — Identity Vault Profile Seed Preview

Read-only preview for canonical operational identity seed records:
- Nic user profile draft
- Gilligan agent profile draft
- Athena agent profile draft
- Neo agent profile draft

Writes reports only under Forge memory. Does not write Identity Vault databases.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sqlite3
import stat
from pathlib import Path
from typing import Any, Dict, List, Tuple

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
IDENTITY_ROOT = HOME / "identity-vault"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
MEM_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch226c_profile_seed_preview_v1"

USER_REQUIRED = [
    "user_id",
    "canonical_name",
    "spirit_name",
    "project_affiliations",
    "identity_tags",
    "version",
    "last_updated",
    "project_context",
    "interaction_preferences",
    "meta_rules",
    "session_state",
]

AGENT_REQUIRED = [
    "agent_id",
    "canonical_name",
    "version",
    "last_updated",
    "role",
    "symbolic_signature",
    "description",
    "capabilities",
    "limitations",
    "persona",
    "voice_style",
    "quotes_or_character_inspiration",
    "special_style_notes",
    "permissions",
    "authority",
    "enforcement_rules",
    "forbidden_actions",
    "session_state",
    "last_action",
    "last_feedback",
    "log_fields",
    "timestamp",
]


def ts() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def sha256_path(path: Path, read_content: bool = True) -> str | None:
    if not path.exists() or not read_content:
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_metadata(path: Path, include_hash: bool = True) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    data = {
        "exists": True,
        "size": st.st_size,
        "mode": oct(stat.S_IMODE(st.st_mode)),
        "mtime_ns": st.st_mtime_ns,
    }
    if include_hash:
        data["sha256"] = sha256_path(path)
    return data


def sqlite_readonly(path: Path) -> sqlite3.Connection:
    uri = f"file:{path}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def db_summary(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "opened_readonly": False, "ok": False}
    if not path.exists():
        return out
    try:
        with sqlite_readonly(path) as con:
            out["opened_readonly"] = True
            rows = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
            tables = [r[0] for r in rows]
            out["tables"] = tables
            counts = {}
            schemas = {}
            for t in tables:
                try:
                    counts[t] = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                    schemas[t] = [r[1] for r in con.execute(f"PRAGMA table_info({t})").fetchall()]
                except Exception as e:  # keep scan resilient
                    counts[t] = f"ERROR: {e}"
            out["row_counts"] = counts
            out["schemas"] = schemas
            out["ok"] = True
    except Exception as e:
        out["error"] = repr(e)
    return out


def preview_legacy(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {"profiles": [], "session_state": [], "payload_plaintext_json": False}
    if not path.exists():
        return out
    try:
        with sqlite_readonly(path) as con:
            if "profiles" in [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]:
                cols = [r[1] for r in con.execute("PRAGMA table_info(profiles)").fetchall()]
                rows = con.execute("SELECT * FROM profiles LIMIT 10").fetchall()
                for row in rows:
                    item = dict(zip(cols, row))
                    raw = item.get("data")
                    if isinstance(raw, str):
                        item["data_preview"] = {
                            "redacted": True,
                            "length": len(raw),
                            "sha16": hashlib.sha256(raw.encode("utf-8", "ignore")).hexdigest()[:16],
                            "colon_segment_count": raw.count(":") + 1 if raw else 0,
                            "format_guess": "json" if raw.strip().startswith("{") else "colon_delimited_ciphertext_or_encoded_payload" if ":" in raw else "unknown_text",
                        }
                        del item["data"]
                    out["profiles"].append(item)
            if "session_state" in [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]:
                cols = [r[1] for r in con.execute("PRAGMA table_info(session_state)").fetchall()]
                rows = con.execute("SELECT * FROM session_state LIMIT 10").fetchall()
                for row in rows:
                    out["session_state"].append(dict(zip(cols, row)))
    except Exception as e:
        out["error"] = repr(e)
    return out


def load_template(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "json_ok": False}
    if not path.exists():
        return out
    out.update(stat_metadata(path, include_hash=True))
    try:
        out["parsed"] = json.loads(path.read_text(encoding="utf-8"))
        out["json_ok"] = True
        out["keys"] = sorted(list(out["parsed"].keys())) if isinstance(out["parsed"], dict) else []
    except Exception as e:
        out["json_error"] = str(e)
    return out


def profile_hash(profile: Dict[str, Any]) -> str:
    data = json.dumps(profile, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_user_profile(timestamp: str) -> Dict[str, Any]:
    return {
        "user_id": "nic_bogaert",
        "canonical_name": "Nic Bogaert",
        "spirit_name": "Manitou Benishi",
        "project_affiliations": ["AI.Web", "Forge", "RMC", "Identity Vault"],
        "identity_tags": ["founder", "systems_builder", "recursive_architect", "privacy_first"],
        "version": "1.0.0-blueprint-draft",
        "last_updated": timestamp,
        "project_context": {
            "current_project": "AI.Web bootstrap integration",
            "phase": "Identity Vault schema/profile alignment",
            "current_files": [],
            "active_collaborators": [],
            "subsystems": ["Forge", "RMC", "Identity Vault", "ProtoForge2", "EchoForge"],
            "goals": [
                "Preserve operational identity locally",
                "Use Forge as governing authority",
                "Use RMC as shared and agent-scoped memory substrate",
                "Keep agent identity inactive until explicitly approved",
            ],
        },
        "interaction_preferences": {
            "formality": "calm, direct, stoic",
            "depth": "detailed",
            "step_by_step": True,
            "beginner_friendly": True,
            "plain_language": True,
            "no_boxes": True,
            "pushback": True,
            "critique_mandatory": True,
            "confirmation_required": True,
            "formatting_rules": [
                "Use clear step-by-step instructions",
                "Do not skip safety checks",
                "Avoid tables unless explicitly requested",
            ],
        },
        "meta_rules": {
            "recursive_feedback": True,
            "drift_tracking": True,
            "contradiction_alerts": True,
            "require_honest_pushback": True,
            "preserve_session_memory": True,
            "require_context_carryover": True,
            "log_all_exchanges": True,
            "always_explain_decisions": True,
            "safe_words": ["pause", "reset", "hold"],
            "forbidden_actions": [
                "activate agent identities without approval",
                "write to RMC memory without approval",
                "read .env secret values",
                "package secrets or node_modules",
            ],
        },
        "session_state": {
            "phase": "draft_inactive",
            "waiting_for": "profile seed review",
            "last_feedback": "Use the real Identity Vault on disk; do not build a replacement vault.",
            "last_action": "Prepared draft user operational identity payload preview.",
            "timestamp": timestamp,
        },
        "legacy_migration_reference": {
            "source_database": str(LEGACY_DB),
            "source_id": "user789",
            "status": "preserve_as_reference_only_until_decryption_or_manual_review",
        },
    }


def build_agent_profiles(timestamp: str) -> List[Dict[str, Any]]:
    return [
        {
            "agent_id": "gilligan.local",
            "canonical_name": "Gilligan",
            "version": "1.0.0-blueprint-draft",
            "last_updated": timestamp,
            "role": "Recursive Mirror / Forge-Governed Development Co-Pilot",
            "symbolic_signature": ["mirror", "critic", "drift_corrector", "forge_governed"],
            "description": "Gilligan is the Forge-governed recursive logic mirror for AI.Web, focused on step-by-step build guidance, drift correction, and clear technical reasoning.",
            "capabilities": ["reasoning support", "patch workflow guidance", "drift detection preview", "RMC preview requests"],
            "limitations": ["cannot activate itself", "cannot bypass Forge", "cannot write memory without approval", "cannot delete user data"],
            "persona": "calm, old-soul, direct, technically careful",
            "voice_style": "laid-back but precise",
            "quotes_or_character_inspiration": ["Willie Nelson meets HAL 9000, without the murder."],
            "special_style_notes": ["Beginner-friendly steps", "Push back when structure is weak", "Never pretend a failed gate passed"],
            "permissions": ["read-only Forge/RMC/Identity Vault previews after approval"],
            "authority": ["may recommend corrections", "may not execute live effects"],
            "enforcement_rules": ["Forge approval gates control actions", "RMC memory writes require explicit approval", "Identity remains inactive until approved"],
            "forbidden_actions": ["self-activation", "secret reading", "database writes", "unapproved tool execution", "memory mutation without approval"],
            "session_state": "inactive_draft",
            "last_action": "Draft operational identity preview prepared.",
            "last_feedback": "Do not build Gilligan as a standalone agent.",
            "log_fields": ["drift corrections", "patch gates", "handoff notes", "RMC preview receipts"],
            "timestamp": timestamp,
            "rmc_namespace": "rmc/agents/gilligan.local",
        },
        {
            "agent_id": "athena.local",
            "canonical_name": "Athena",
            "version": "1.0.0-blueprint-draft",
            "last_updated": timestamp,
            "role": "Governance / Strategy / Investor-Facing Analysis Agent",
            "symbolic_signature": ["governance", "strategy", "clarity", "boundary_guardian"],
            "description": "Athena supports formal analysis, governance framing, investor-facing explanation, and policy-aware system boundaries under Forge control.",
            "capabilities": ["strategic analysis", "formal summaries", "governance review", "risk framing"],
            "limitations": ["cannot override Forge", "cannot activate identities", "cannot write databases", "cannot represent live facts without verification"],
            "persona": "formal, composed, analytical",
            "voice_style": "clear, structured, executive-facing",
            "quotes_or_character_inspiration": ["Strategic clarity before action."],
            "special_style_notes": ["Prefer evidence and boundaries", "Use plain professional language"],
            "permissions": ["read-only contract/status previews after approval"],
            "authority": ["may recommend governance holds", "may recommend risk flags"],
            "enforcement_rules": ["No live execution", "No identity activation", "No unsupported claims"],
            "forbidden_actions": ["database writes", "secret reading", "unapproved external claims", "bypassing Forge"],
            "session_state": "inactive_draft",
            "last_action": "Draft operational identity preview prepared.",
            "last_feedback": "Keep Athena as governed identity, not independent runtime.",
            "log_fields": ["governance reviews", "risk flags", "contract checks"],
            "timestamp": timestamp,
            "rmc_namespace": "rmc/agents/athena.local",
        },
        {
            "agent_id": "neo.local",
            "canonical_name": "Neo",
            "version": "1.0.0-blueprint-draft",
            "last_updated": timestamp,
            "role": "Public / Frontline Assistant Identity",
            "symbolic_signature": ["public_interface", "friendly", "support", "translation_layer"],
            "description": "Neo is the friendly frontline assistant identity for public-facing explanations, onboarding, and everyday user support under Forge governance.",
            "capabilities": ["plain-language explanation", "onboarding support", "public FAQ drafting", "user-friendly summaries"],
            "limitations": ["cannot access private memory without approval", "cannot modify files", "cannot activate itself", "cannot bypass Forge"],
            "persona": "warm, clear, accessible",
            "voice_style": "friendly and simple",
            "quotes_or_character_inspiration": ["Make the doorway easy to walk through."],
            "special_style_notes": ["Avoid jargon", "Use simple wording", "Support non-technical users"],
            "permissions": ["read-only public context previews after approval"],
            "authority": ["may simplify explanations", "may ask for clarification"],
            "enforcement_rules": ["No private data exposure", "No unapproved memory writes", "No tool execution"],
            "forbidden_actions": ["secret reading", "database writes", "private memory exposure", "unapproved execution"],
            "session_state": "inactive_draft",
            "last_action": "Draft operational identity preview prepared.",
            "last_feedback": "Keep Neo as public-facing governed identity.",
            "log_fields": ["public explanations", "onboarding outputs", "support interactions"],
            "timestamp": timestamp,
            "rmc_namespace": "rmc/agents/neo.local",
        },
    ]


def validate_keys(profile: Dict[str, Any], required: List[str]) -> Tuple[bool, List[str]]:
    missing = [k for k in required if k not in profile]
    return not missing, missing


def main() -> int:
    stamp = ts()
    iso = now_iso()
    run_dir = MEM_ROOT / stamp
    run_dir.mkdir(parents=True, exist_ok=True)

    before = {
        "env": stat_metadata(IDENTITY_ROOT / ".env", include_hash=False),
        "canonical_db": stat_metadata(CANONICAL_DB, include_hash=True),
        "legacy_db": stat_metadata(LEGACY_DB, include_hash=True),
    }

    canonical = db_summary(CANONICAL_DB)
    legacy = db_summary(LEGACY_DB)
    legacy_preview = preview_legacy(LEGACY_DB)
    templates = {
        "user_template": load_template(IDENTITY_ROOT / "templates" / "user-template.json"),
        "agent_template": load_template(IDENTITY_ROOT / "templates" / "agent-template.json"),
    }

    user = build_user_profile(iso)
    agents = build_agent_profiles(iso)
    user_ok, user_missing = validate_keys(user, USER_REQUIRED)
    agent_checks = []
    for a in agents:
        ok, missing = validate_keys(a, AGENT_REQUIRED)
        agent_checks.append({"agent_id": a["agent_id"], "ok": ok, "missing": missing, "hash": profile_hash(a)})

    draft_records = {
        "status": "PREVIEW_ONLY_NOT_WRITTEN",
        "created_at_utc": stamp,
        "user_profile": {
            "target_table": "user_profiles",
            "lookup_id": user["user_id"],
            "activation_state": "inactive_draft_preview_only",
            "profile_hash": profile_hash(user),
            "operational_profile_json": user,
        },
        "agent_profiles": [
            {
                "target_table": "agent_profiles",
                "lookup_id": a["agent_id"],
                "activation_state": "inactive_draft_preview_only",
                "rmc_namespace": a["rmc_namespace"],
                "profile_hash": profile_hash(a),
                "operational_profile_json": a,
            }
            for a in agents
        ],
    }

    after = {
        "env": stat_metadata(IDENTITY_ROOT / ".env", include_hash=False),
        "canonical_db": stat_metadata(CANONICAL_DB, include_hash=True),
        "legacy_db": stat_metadata(LEGACY_DB, include_hash=True),
    }

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env"] == after["env"],
        "canonical_db_sha_unchanged": before["canonical_db"].get("sha256") == after["canonical_db"].get("sha256"),
        "legacy_db_sha_unchanged": before["legacy_db"].get("sha256") == after["legacy_db"].get("sha256"),
        "database_write_performed": False,
        "profiles_created": False,
        "agent_identity_activation_performed": False,
    }

    verdict = "PASS" if user_ok and all(c["ok"] for c in agent_checks) and all(safety.values()) else "WARN"

    report = {
        "timestamp": stamp,
        "verdict": verdict,
        "boundary": "read-only preview; no DB writes; no identity activation",
        "canonical": canonical,
        "legacy": legacy,
        "legacy_preview": legacy_preview,
        "templates": {k: {kk: vv for kk, vv in v.items() if kk != "parsed"} for k, v in templates.items()},
        "template_json_ok": {k: v.get("json_ok") for k, v in templates.items()},
        "draft_validation": {"user_ok": user_ok, "user_missing": user_missing, "agent_checks": agent_checks},
        "safety": safety,
        "draft_records": draft_records,
    }

    json_path = run_dir / f"{stamp}_identity_vault_patch226c_profile_seed_preview.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    latest_json = MEM_ROOT / "latest_identity_vault_patch226c_profile_seed_preview.json"
    latest_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    md_lines = [
        "# Identity Vault Patch 226C Profile Seed Preview",
        "",
        f"Timestamp: `{stamp}`",
        f"Verdict: **{verdict}**",
        "",
        "## Boundary",
        "- This patch previews draft operational profiles only.",
        "- It writes reports only under Forge memory.",
        "- It does not write Identity Vault databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.",
        "",
        "## Canonical Database",
        f"- path: `{CANONICAL_DB}` opened_readonly=`{canonical.get('opened_readonly')}` ok=`{canonical.get('ok')}`",
        f"- row counts: `{canonical.get('row_counts')}`",
        "",
        "## Legacy Database",
        f"- path: `{LEGACY_DB}` opened_readonly=`{legacy.get('opened_readonly')}` ok=`{legacy.get('ok')}`",
        f"- row counts: `{legacy.get('row_counts')}`",
        f"- legacy profiles previewed: `{len(legacy_preview.get('profiles', []))}`",
        "- legacy payload status: preserve as reference only unless app-level decryption/manual review is approved.",
        "",
        "## Template Review",
        f"- user template json_ok: `{templates['user_template'].get('json_ok')}` path=`{templates['user_template'].get('path')}`",
        f"- agent template json_ok: `{templates['agent_template'].get('json_ok')}` path=`{templates['agent_template'].get('path')}`",
        "- Templates are treated as reference files only; draft profiles are generated from the blueprint field structure.",
        "",
        "## Draft Profiles Previewed",
        f"- user profile: `{user['user_id']}` hash=`{profile_hash(user)[:16]}` required_fields_ok=`{user_ok}`",
        f"- agent profile: `gilligan.local` hash=`{agent_checks[0]['hash'][:16]}` required_fields_ok=`{agent_checks[0]['ok']}` rmc_namespace=`rmc/agents/gilligan.local`",
        f"- agent profile: `athena.local` hash=`{agent_checks[1]['hash'][:16]}` required_fields_ok=`{agent_checks[1]['ok']}` rmc_namespace=`rmc/agents/athena.local`",
        f"- agent profile: `neo.local` hash=`{agent_checks[2]['hash'][:16]}` required_fields_ok=`{agent_checks[2]['ok']}` rmc_namespace=`rmc/agents/neo.local`",
        "",
        "## Safety Checks",
    ]
    for k, v in safety.items():
        md_lines.append(f"- `{k}`: `{v}`")
    md_lines += [
        "",
        "## Findings",
        "- **INFO** `IV_REAL_VAULT_USED` — Preview uses `/home/nic/identity-vault`, not a replacement vault.",
        "- **INFO** `IV_LEGACY_USER789_PRESERVED` — Legacy `user789` row is preserved as migration reference only.",
        "- **INFO** `IV_DRAFT_PROFILES_PREVIEWED_ONLY` — Nic, Gilligan, Athena, and Neo draft operational profiles were generated but not written.",
        "",
        "## Output Files",
        f"- JSON preview: `{json_path}`",
        "",
        "## Next Safe Step",
        "If this preview is acceptable, create Patch 227 to write these profiles as inactive draft rows into the canonical Identity Vault database. Do not activate identities yet.",
    ]

    md_path = run_dir / f"{stamp}_identity_vault_patch226c_profile_seed_preview.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    latest_md = MEM_ROOT / "latest_identity_vault_patch226c_profile_seed_preview.md"
    latest_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print("Identity Vault Patch 226C profile seed preview complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON preview: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Memory Writer Dry-Run / W_t engine.

Patch 262J1R-Preflight-C7 creates the write-intent layer that follows Echo
Validation. This module does not write files, mutate RMC memory, update Chroma,
change canonical references, call an LLM, execute shell, or touch Identity
Vault. It computes whether the validated RMC output is eligible for a future
approved memory write and returns a deterministic write plan.

The actual write stage is intentionally deferred to a later gated patch. C7
answers one question only: if this echo-validated render were allowed to become
memory, what exactly would be written, where, under which phase/drift tags, and
why?
"""
from __future__ import annotations

import datetime as _dt
import re
from typing import Any

try:
    from rmc_engine_v1.measurement_kernel import clamp, stable_hash, stable_id
except Exception:  # pragma: no cover - keeps unit tests usable if imported standalone
    import hashlib

    def clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
        try:
            number = float(value)
        except Exception:
            number = low
        return max(low, min(high, number))

    def stable_hash(value: Any) -> str:
        return hashlib.sha256(str(value).encode("utf-8", errors="replace")).hexdigest()

    def stable_id(prefix: str, value: Any) -> str:
        return f"{prefix}_{stable_hash(value)[:18]}"

ENGINE_VERSION = "rmc_memory_writer_dry_run_v1_patch262J1R_preflight_C7"
ENGINE_MODE = "read_only_memory_writer_dry_run_W_t"

REQUIRED_ECHO_FIELDS = [
    "echo_validation_id",
    "source_rendered_output_id",
    "source_manifest_id",
    "echo_score",
    "echo_components",
    "echo_validation_passed",
    "recommended_route",
]

REQUIRED_MEMORY_NODE_FIELDS = [
    "content",
    "source",
    "phase",
    "confidence",
    "ancestry",
    "prior_drift_score",
    "retrieval_weight",
    "tags",
]


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value or {}) if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, "", {}):
        return []
    return [value]


def _text(value: Any, limit: int = 4000) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def _tokens(value: Any) -> set[str]:
    return {tok for tok in re.findall(r"[a-z0-9_]+", str(value or "").lower()) if len(tok) > 2}


def _round(value: Any, places: int = 6) -> float:
    return round(clamp(value), places)


def memory_writer_boundary() -> dict[str, Any]:
    return {
        "engine_version": ENGINE_VERSION,
        "engine_mode": ENGINE_MODE,
        "engine_module_location": "forge/rmc_engine_v1/memory_writer.py",
        "implements_rmc_stage": "Memory Writer Dry-Run / W_t",
        "input_contract": "C6_echo_validation_report_with_optional_V_t",
        "output_contract": "dry_run_memory_write_plan_or_blocked_write_candidate",
        "actual_writer_stage_present": False,
        "approval_required_for_real_write": True,
        "read_only": True,
        "uses_llm": False,
        "queries_chroma": False,
        "reads_db_files": False,
        "executes_shell": False,
        "writes_files": False,
        "writes_rmc_memory": False,
        "writes_identity_vault": False,
        "mutates_canonical_reference": False,
        "approved_output": False,
        "projection_allowed": False,
        "memory_write_allowed": False,
        "read_only_means": "computes write eligibility and exact write plan in response only; performs no mutation",
    }


def memory_writer_schema_contract() -> dict[str, Any]:
    return {
        "memory_writer_symbol": "W_t",
        "formula": "W_t = plan_memory_write(V_t, R_t, μ_t, T_t) if echo_passed and write_eligibility >= threshold",
        "required_source": "C6 V_t echo validation plus C5 R_t render packet and C4 μ_t manifest packet",
        "required_memory_node_fields": list(REQUIRED_MEMORY_NODE_FIELDS),
        "write_eligibility_formula": (
            "0.30*echo_score + 0.18*manifest_confidence + 0.14*drift_stability "
            "+ 0.12*memory_support + 0.10*schema_integrity + 0.08*phase_closure "
            "+ 0.08*source_confidence - novelty_risk_penalty - distortion_penalty"
        ),
        "dry_run_threshold": 0.72,
        "actual_write_stage": "deferred_to_gated_C8_or_later",
        "axioms_enforced": {
            "no_output_without_trace": True,
            "meaning_precedes_rendering": True,
            "memory_must_be_phase_tagged": True,
            "phase6_closure_before_projection": True,
            "language_is_output_modality_not_core_state": True,
            "echo_validation_before_memory_write": True,
        },
    }


def _V_t(echo_report: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(echo_report.get("V_t"))


def _render_report(echo_report: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(echo_report.get("source_output_renderer"))


def _render_packet_from_echo(echo_report: dict[str, Any]) -> dict[str, Any]:
    render_report = _render_report(echo_report)
    return _as_dict(render_report.get("render_packet"))


def _manifest_packet_from_echo(echo_report: dict[str, Any]) -> dict[str, Any]:
    render_report = _render_report(echo_report)
    packet = render_report.get("source_manifest_packet")
    if isinstance(packet, dict) and packet:
        return dict(packet)
    source_manifest = _as_dict(render_report.get("source_manifest_compiler"))
    packet = source_manifest.get("manifest_packet")
    return dict(packet or {}) if isinstance(packet, dict) else {}


def _mu_from_echo(echo_report: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(_manifest_packet_from_echo(echo_report).get("μ_t"))


def _drift_status(mu: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(mu.get("drift_status"))


def _memory_links(mu: dict[str, Any]) -> list[dict[str, Any]]:
    return [m for m in _as_list(mu.get("memory_links")) if isinstance(m, dict)]


def _source_confidence(memory_links: list[dict[str, Any]]) -> float:
    if not memory_links:
        return 0.0
    values = []
    for item in memory_links:
        raw = item.get("confidence", item.get("source_confidence", item.get("weight", 0.5)))
        if isinstance(raw, str):
            lowered = raw.lower()
            if lowered in ("high", "canonical", "trusted"):
                raw = 0.9
            elif lowered in ("medium", "moderate"):
                raw = 0.65
            elif lowered in ("low", "weak"):
                raw = 0.35
            else:
                raw = 0.5
        values.append(clamp(raw))
    return round(sum(values) / max(1, len(values)), 6)


def _phase_closure_score(mu: dict[str, Any]) -> float:
    phases = [str(p) for p in _as_list(mu.get("phase_path"))]
    if not phases:
        return 0.0
    has6 = "Φ6" in phases
    has7 = "Φ7" in phases
    has8 = "Φ8" in phases
    if has8 and (not has6 or not has7):
        return 0.0
    if has6 and has7:
        return 1.0
    if has6:
        return 0.72
    return 0.42


def _schema_integrity(render_packet: dict[str, Any], mu: dict[str, Any], V: dict[str, Any]) -> float:
    required_mu = ["claim", "phase_path", "operator_path", "memory_links", "confidence", "novelty", "drift_status", "output_targets"]
    required_render = ["rendered_output_id", "source_manifest_id", "render_mode", "R_t"]
    required_echo = list(REQUIRED_ECHO_FIELDS)
    total = len(required_mu) + len(required_render) + len(required_echo)
    missing = sum(1 for key in required_mu if key not in mu)
    missing += sum(1 for key in required_render if key not in render_packet)
    missing += sum(1 for key in required_echo if key not in V)
    return round(clamp(1.0 - (missing / max(1, total))), 6)


def _drift_stability(mu: dict[str, Any]) -> float:
    drift = _drift_status(mu)
    eps = drift.get("post_epsilon_s", drift.get("epsilon_s", drift.get("measured_epsilon_s", 0.5)))
    if isinstance(eps, dict):
        eps = eps.get("epsilon_s", 0.5)
    return round(clamp(1.0 - clamp(eps)), 6)


def _novelty_risk_penalty(mu: dict[str, Any]) -> float:
    novelty = clamp(mu.get("novelty", 0.0))
    # Novelty beyond 0.70 is not forbidden, but it requires review support.
    return round(max(0.0, novelty - 0.70) * 0.35, 6)


def _distortion_penalty(V: dict[str, Any]) -> float:
    flags = _as_list(V.get("distortion_flags"))
    components = _as_dict(V.get("echo_components"))
    direct = clamp(V.get("distortion_penalty", 0.0))
    component_penalty = 0.0
    if flags:
        component_penalty += min(0.35, 0.07 * len(flags))
    for value in components.values():
        try:
            if float(value) < 0.5:
                component_penalty += 0.025
        except Exception:
            continue
    return round(clamp(max(direct, component_penalty)), 6)


def _memory_support(memory_links: list[dict[str, Any]]) -> float:
    if not memory_links:
        return 0.0
    count_score = clamp(len(memory_links) / 5.0)
    confidence_score = _source_confidence(memory_links)
    return round((0.55 * count_score) + (0.45 * confidence_score), 6)


def _render_content(render_packet: dict[str, Any]) -> str:
    R_t = render_packet.get("R_t")
    if isinstance(R_t, dict):
        # Prefer human-readable fields, then stable compact representation.
        for key in ("text", "summary", "claim", "display", "content"):
            if key in R_t:
                return _text(R_t.get(key), 8000)
    return _text(R_t, 8000)


def _phase_tags(mu: dict[str, Any]) -> list[str]:
    tags = []
    for phase in _as_list(mu.get("phase_path")):
        value = str(phase).strip()
        if value and value not in tags:
            tags.append(value)
    return tags


def _operator_tags(mu: dict[str, Any]) -> list[str]:
    tags = []
    for operator in _as_list(mu.get("operator_path")):
        value = str(operator).strip()
        if value and value not in tags:
            tags.append(value)
    return tags


def _write_class(mu: dict[str, Any], V: dict[str, Any], eligibility: float) -> str:
    drift = _drift_status(mu)
    status = str(drift.get("status") or "").lower()
    if not bool(V.get("echo_validation_passed")):
        return "blocked_echo_failed"
    if eligibility >= 0.86 and "unresolved" not in status:
        return "candidate_trace_memory_high_confidence"
    if eligibility >= 0.72:
        return "candidate_trace_memory_requires_review"
    return "blocked_low_write_eligibility"


def _target_preview(write_class: str, memory_node_id: str) -> dict[str, Any]:
    base = "/home/nic/forge/memory/rmc_live_memory_v1"
    if write_class == "candidate_trace_memory_high_confidence":
        namespace = "approved_trace_candidates"
    elif write_class == "candidate_trace_memory_requires_review":
        namespace = "review_queue"
    else:
        namespace = "blocked_write_candidates"
    day = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d")
    return {
        "root": base,
        "namespace": namespace,
        "relative_path_preview": f"{namespace}/{day}/{memory_node_id}.json",
        "absolute_path_preview": f"{base}/{namespace}/{day}/{memory_node_id}.json",
        "receipt_path_preview": f"{base}/receipts/{day}/{memory_node_id}_receipt.json",
        "index_path_preview": f"{base}/indexes/memory_writer_index.jsonl",
    }


def _blocked(reason_codes: list[str], echo_report: dict[str, Any], diagnostics: dict[str, Any] | None = None) -> dict[str, Any]:
    diagnostics = diagnostics or {}
    digest = stable_hash({"reasons": reason_codes, "echo": echo_report.get("echo_run_id"), "diag": diagnostics})[:18]
    return {
        "status": "BLOCKED",
        "engine_version": ENGINE_VERSION,
        "engine_mode": ENGINE_MODE,
        "stage": "Memory Writer Dry-Run",
        "W_t_present": False,
        "memory_write_plan_allowed": False,
        "write_plan": None,
        "blocked_write_candidate": {
            "blocked_write_id": f"blocked_write_{digest}",
            "status": "blocked_memory_write_dry_run",
            "reason_codes": list(reason_codes),
            "diagnostics": diagnostics,
            "source_echo_run_id": echo_report.get("echo_run_id"),
            "actual_files_written": [],
            "writes_files": False,
            "memory_write_allowed": False,
            "approval_required_for_future_write": True,
            "recommended_route": _recommended_block_route(reason_codes),
        },
        "gate_classification": {
            "algorithm_failure": False,
            "gate_refusal": True,
            "read_only_refusal": "actual_write_deferred_to_gated_writer_stage",
            "explanation": "C7 can compute a write plan, but it cannot mutate memory. If upstream echo/manifest is blocked, no write plan is permitted.",
        },
        "actual_files_written": [],
        "writes_files": False,
        "identity_vault_write": False,
        "rmc_live_memory_write": False,
        "approved_output": False,
        "projection_allowed": False,
        "memory_write_allowed": False,
    }


def _recommended_block_route(reason_codes: list[str]) -> str:
    reasons = set(reason_codes)
    if "echo_validation_failed" in reasons:
        return "route_to_renderer_repair_or_manifest_review"
    if "missing_echo_validation" in reasons:
        return "route_to_echo_validator"
    if "missing_render_packet" in reasons:
        return "route_to_output_renderer"
    if "missing_manifest_packet" in reasons:
        return "route_to_manifest_compiler"
    if "write_eligibility_below_threshold" in reasons:
        return "route_to_review_or_add_memory_support"
    return "hold_for_review"


def _build_memory_node(echo_report: dict[str, Any], V: dict[str, Any], render_packet: dict[str, Any], mu: dict[str, Any], eligibility: float) -> dict[str, Any]:
    content = _render_content(render_packet)
    memory_links = _memory_links(mu)
    drift = _drift_status(mu)
    source_conf = _source_confidence(memory_links)
    memory_fit = _memory_support(memory_links)
    prior_drift = clamp(1.0 - _drift_stability(mu))
    retrieval_weight = round(clamp(
        0.30 * eligibility
        + 0.20 * clamp(mu.get("confidence", 0.0))
        + 0.18 * memory_fit
        + 0.14 * _phase_closure_score(mu)
        + 0.10 * source_conf
        + 0.08 * clamp(V.get("echo_score", 0.0))
    ), 6)
    claim = _text(mu.get("claim"), 1000)
    tags = []
    for item in _phase_tags(mu) + _operator_tags(mu):
        if item not in tags:
            tags.append(item)
    for item in ("rmc", "trace", "manifest", "echo_validated", "dry_run_write_candidate"):
        if item not in tags:
            tags.append(item)
    node_basis = {
        "claim": claim,
        "render_id": render_packet.get("rendered_output_id"),
        "manifest_id": render_packet.get("source_manifest_id") or V.get("source_manifest_id"),
        "echo_id": V.get("echo_validation_id"),
        "content_hash": stable_hash(content),
    }
    return {
        "memory_node_id": stable_id("rmcmem", node_basis),
        "content": content,
        "content_sha256": stable_hash(content),
        "source": {
            "kind": "rmc_echo_validated_render_dry_run",
            "trace_id": echo_report.get("trace_id") or echo_report.get("echo_run_id"),
            "manifest_id": render_packet.get("source_manifest_id") or V.get("source_manifest_id"),
            "rendered_output_id": render_packet.get("rendered_output_id") or V.get("source_rendered_output_id"),
            "echo_validation_id": V.get("echo_validation_id"),
            "renderer_mode": render_packet.get("render_mode"),
        },
        "phase": _phase_tags(mu),
        "confidence": round(clamp(mu.get("confidence", 0.0)) * 0.45 + eligibility * 0.35 + clamp(V.get("echo_score", 0.0)) * 0.20, 6),
        "ancestry": {
            "claim": claim,
            "phase_path": _phase_tags(mu),
            "operator_path": _operator_tags(mu),
            "memory_link_count": len(memory_links),
            "memory_link_ids": [str(m.get("memory_id") or m.get("id") or m.get("source") or "unknown") for m in memory_links[:12]],
            "manifest_claim_hash": stable_hash(claim),
            "render_content_hash": stable_hash(content),
        },
        "prior_drift_score": round(prior_drift, 6),
        "retrieval_weight": retrieval_weight,
        "tags": tags,
        "drift_status": drift,
        "novelty": _round(mu.get("novelty", 0.0)),
        "write_status": "dry_run_candidate_not_written",
    }


def _compute_write_eligibility(V: dict[str, Any], render_packet: dict[str, Any], mu: dict[str, Any]) -> dict[str, Any]:
    memory_links = _memory_links(mu)
    echo_score = clamp(V.get("echo_score", 0.0))
    manifest_confidence = clamp(mu.get("confidence", 0.0))
    drift_stability = _drift_stability(mu)
    memory_support = _memory_support(memory_links)
    schema_integrity = _schema_integrity(render_packet, mu, V)
    phase_closure = _phase_closure_score(mu)
    source_confidence = _source_confidence(memory_links)
    novelty_penalty = _novelty_risk_penalty(mu)
    distortion_penalty = _distortion_penalty(V)
    raw = (
        0.30 * echo_score
        + 0.18 * manifest_confidence
        + 0.14 * drift_stability
        + 0.12 * memory_support
        + 0.10 * schema_integrity
        + 0.08 * phase_closure
        + 0.08 * source_confidence
        - novelty_penalty
        - distortion_penalty
    )
    eligibility = round(clamp(raw), 6)
    return {
        "write_eligibility_score": eligibility,
        "threshold": 0.72,
        "formula": memory_writer_schema_contract()["write_eligibility_formula"],
        "components": {
            "echo_score": round(echo_score, 6),
            "manifest_confidence": round(manifest_confidence, 6),
            "drift_stability": round(drift_stability, 6),
            "memory_support": round(memory_support, 6),
            "schema_integrity": round(schema_integrity, 6),
            "phase_closure": round(phase_closure, 6),
            "source_confidence": round(source_confidence, 6),
            "novelty_risk_penalty": round(novelty_penalty, 6),
            "distortion_penalty": round(distortion_penalty, 6),
        },
        "passes_threshold": eligibility >= 0.72,
    }


def plan_memory_write(echo_report: dict[str, Any]) -> dict[str, Any]:
    """Return W_t dry-run write plan or a blocked write candidate.

    This function intentionally performs no I/O. It accepts a C6 echo report and
    computes whether the echo-validated render is eligible to become a future
    memory record. The returned plan contains deterministic target previews and
    receipts, but the lists of actual writes remain empty.
    """
    echo_report = _as_dict(echo_report)
    V = _V_t(echo_report)
    render_packet = _render_packet_from_echo(echo_report)
    manifest_packet = _manifest_packet_from_echo(echo_report)
    mu = _as_dict(manifest_packet.get("μ_t"))

    reason_codes: list[str] = []
    if not V:
        reason_codes.append("missing_echo_validation")
    if not render_packet:
        reason_codes.append("missing_render_packet")
    if not manifest_packet or not mu:
        reason_codes.append("missing_manifest_packet")
    if V and not bool(V.get("echo_validation_passed")):
        reason_codes.append("echo_validation_failed")
    if render_packet and bool(render_packet.get("approved_output")):
        # The renderer must not approve output before echo/memory gates.
        reason_codes.append("renderer_premature_approval_flag")

    if reason_codes:
        return _blocked(reason_codes, echo_report, {
            "has_V_t": bool(V),
            "has_render_packet": bool(render_packet),
            "has_manifest_packet": bool(manifest_packet),
            "echo_validation_passed": bool(V.get("echo_validation_passed")) if V else False,
        })

    eligibility_report = _compute_write_eligibility(V, render_packet, mu)
    if not eligibility_report["passes_threshold"]:
        return _blocked(["write_eligibility_below_threshold"], echo_report, eligibility_report)

    memory_node = _build_memory_node(echo_report, V, render_packet, mu, eligibility_report["write_eligibility_score"])
    write_class = _write_class(mu, V, eligibility_report["write_eligibility_score"])
    target_preview = _target_preview(write_class, memory_node["memory_node_id"])
    W_basis = {
        "memory_node_id": memory_node["memory_node_id"],
        "echo_validation_id": V.get("echo_validation_id"),
        "rendered_output_id": render_packet.get("rendered_output_id"),
        "manifest_id": render_packet.get("source_manifest_id") or V.get("source_manifest_id"),
        "eligibility": eligibility_report,
    }
    W_t = {
        "W_t_id": stable_id("wt", W_basis),
        "status": "memory_write_plan_ready_dry_run_only",
        "dry_run": True,
        "actual_write_requires_future_gated_patch": True,
        "approval_token_required_for_future_write": "APPROVE_RMC_MEMORY_WRITE",
        "write_class": write_class,
        "write_eligibility": eligibility_report,
        "memory_node_preview": memory_node,
        "write_target_preview": target_preview,
        "receipt_preview": {
            "receipt_id": stable_id("rmcwrec", W_basis),
            "receipt_kind": "rmc_memory_write_dry_run_receipt_preview",
            "created_at_utc": _utc_now(),
            "source_echo_validation_id": V.get("echo_validation_id"),
            "source_rendered_output_id": render_packet.get("rendered_output_id"),
            "source_manifest_id": render_packet.get("source_manifest_id") or V.get("source_manifest_id"),
            "content_sha256": memory_node["content_sha256"],
            "actual_files_written": [],
        },
        "duplicate_check_preview": {
            "content_sha256": memory_node["content_sha256"],
            "candidate_duplicate_keys": [
                memory_node["content_sha256"],
                stable_hash(memory_node["ancestry"].get("claim", "")),
                stable_hash(memory_node["source"]),
            ],
            "duplicate_decision": "not_checked_against_disk_in_read_only_C7",
            "future_writer_must_check_index_before_commit": True,
        },
        "actual_files_written": [],
    }
    return {
        "status": "OK",
        "engine_version": ENGINE_VERSION,
        "engine_mode": ENGINE_MODE,
        "stage": "Memory Writer Dry-Run",
        "W_t_present": True,
        "memory_write_plan_allowed": True,
        "write_plan": W_t,
        "blocked_write_candidate": None,
        "gate_classification": {
            "algorithm_failure": False,
            "gate_refusal": False,
            "read_only_refusal": "actual_write_deferred_to_gated_writer_stage",
            "explanation": "C7 computed a future write plan but performed no mutation.",
        },
        "actual_files_written": [],
        "writes_files": False,
        "identity_vault_write": False,
        "rmc_live_memory_write": False,
        "approved_output": False,
        "projection_allowed": False,
        "memory_write_allowed": False,
    }

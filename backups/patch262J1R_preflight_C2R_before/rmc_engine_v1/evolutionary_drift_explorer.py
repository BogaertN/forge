"""RMC Evolutionary Drift Explorer + Coherence Scorer v1.

Patch 262J1R-Preflight-C2 implements the next real RMC application stage
after Candidate Conclusion Generator.

This module consumes C_t candidate meaning states and produces:
    E_t — bounded evolutionary-drift exploration report.
    S_t — read-only coherence score set and selected candidate preview.

It does not render final language, approve projection, compile manifests,
write memory, mutate datasets, query Chroma, execute shell, call an LLM, or
touch Identity Vault.

Core law:
    Drift is not always error.
    Novelty is allowed only when drift remains bounded.
    A scored candidate is still not an approved output.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
from typing import Any

ENGINE_VERSION = "rmc_evolutionary_drift_explorer_v1_patch262J1R_preflight_C2"
ENGINE_MODE = "read_only_evolutionary_drift_and_coherence_scoring"
PHASES = [f"Φ{i}" for i in range(1, 10)]


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _sha(obj: Any) -> str:
    try:
        payload = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    except Exception:
        payload = str(obj)
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()


def _stable_id(prefix: str, obj: Any, n: int = 18) -> str:
    return f"{prefix}_{_sha(obj)[:n]}"


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        v = float(value)
    except Exception:
        v = 0.0
    return max(float(low), min(float(high), v))


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, "", {}):
        return []
    return [value]


def _phase_index(phase: Any) -> int | None:
    s = str(phase or "").strip()
    for idx in range(1, 10):
        if s == f"Φ{idx}" or s == str(idx) or f"Φ{idx}" in s:
            return idx
    return None


def _phase_path(candidate: dict[str, Any]) -> list[str]:
    path = []
    for p in _as_list(candidate.get("phase_path")):
        ps = str(p)
        if ps in PHASES and ps not in path:
            path.append(ps)
    target = str(candidate.get("phase_target") or "")
    if target in PHASES and target not in path:
        path.append(target)
    return path


def _candidate_id(candidate: dict[str, Any], index: int) -> str:
    return str(candidate.get("candidate_id") or _stable_id(f"ct_auto_{index:02d}", candidate))


def evolutionary_drift_boundary() -> dict[str, Any]:
    return {
        "engine_version": ENGINE_VERSION,
        "engine_mode": ENGINE_MODE,
        "engine_module_location": "forge/rmc_engine_v1/evolutionary_drift_explorer.py",
        "implements_rmc_stages": [
            "Evolutionary Drift Explorer / E_t",
            "Coherence Scorer / S_t",
        ],
        "input_contract": "candidate_conclusion_report_C_t",
        "output_contract": "bounded_drift_exploration_and_coherence_scores_not_final_language",
        "calls_llm": False,
        "queries_chroma": False,
        "reads_db_files": False,
        "executes_shell": False,
        "writes_files": False,
        "writes_rmc_memory": False,
        "writes_identity_vault": False,
        "mutates_canonical_reference": False,
        "renders_final_language": False,
        "approved_output": False,
        "projection_allowed": False,
        "memory_write_allowed": False,
        "manifest_allowed": False,
        "note": "C2 ranks candidate meaning states and marks bounded novelty. It cannot render, approve, project, write memory, or compile a manifest.",
    }


def _candidate_set(candidate_report: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = candidate_report.get("candidate_set") if isinstance(candidate_report, dict) else []
    if not isinstance(candidates, list):
        return []
    return [c for c in candidates if isinstance(c, dict)]


def _candidate_generation_blocked(candidate_report: dict[str, Any]) -> bool:
    status = candidate_report.get("candidate_generation_status") if isinstance(candidate_report, dict) else {}
    if isinstance(status, dict) and status.get("candidate_generation_allowed") is False:
        return True
    for c in _candidate_set(candidate_report):
        if str(c.get("candidate_kind") or "") == "containment_correction_route":
            return True
    return False


def _memory_fit(candidate: dict[str, Any]) -> float:
    support = candidate.get("memory_support") if isinstance(candidate, dict) else {}
    if not isinstance(support, dict):
        support = {}
    avg = _clamp(support.get("average_retrieval_weight"), 0.0, 1.0)
    linked = min(int(support.get("linked_memory_count") or 0), 8) / 8.0
    present = 1.0 if bool(support.get("memory_support_present")) else 0.0
    return _clamp((avg * 0.55) + (linked * 0.25) + (present * 0.20))


def _novelty_fit(novelty: float) -> float:
    novelty = _clamp(novelty)
    # Useful zone: enough novelty to evolve, not so much it loses trace.
    if novelty <= 0.05:
        return 0.35
    if novelty <= 0.65:
        return 0.65 + (novelty / 0.65) * 0.30
    if novelty <= 0.82:
        return 0.95 - ((novelty - 0.65) / 0.17) * 0.18
    return max(0.15, 0.55 - ((novelty - 0.82) / 0.18) * 0.40)


def _utility_fit(candidate: dict[str, Any]) -> float:
    kind = str(candidate.get("candidate_kind") or "")
    title = str(candidate.get("title") or "").lower()
    if kind in {"correction_candidate", "memory_anchored_candidate"}:
        return 0.86
    if kind in {"direct_trace_candidate", "projection_gate_candidate"}:
        return 0.72
    if kind in {"bounded_evolutionary_candidate"}:
        return 0.68
    if "correction" in title:
        return 0.82
    if "archive" in kind or "containment" in kind:
        return 0.42
    return 0.58


def _phase_validity(candidate: dict[str, Any]) -> dict[str, Any]:
    path = _phase_path(candidate)
    indexes = [i for i in (_phase_index(p) for p in path) if i is not None]
    warnings: list[dict[str, Any]] = []

    if 5 in indexes and 8 in indexes:
        if not (6 in indexes and 7 in indexes and indexes.index(6) < indexes.index(8) and indexes.index(7) < indexes.index(8)):
            warnings.append({
                "type": "phase_5_to_8_projection_skip",
                "severity": "critical",
                "rule": "Φ5 drift may not project to Φ8 before Φ6 correction and Φ7 naming.",
            })
    if 8 in indexes and not (6 in indexes and 7 in indexes):
        warnings.append({
            "type": "projection_without_correction_or_naming",
            "severity": "high",
            "rule": "Projection requires Φ6 correction and Φ7 naming first.",
        })
    if 7 in indexes and 6 not in indexes:
        warnings.append({
            "type": "naming_without_correction_context",
            "severity": "medium",
            "rule": "Naming should preserve correction context when drift or projection is active.",
        })
    has_decrease = any(indexes[i] > indexes[i + 1] and indexes[i + 1] not in {1, 6, 9} for i in range(len(indexes) - 1))
    if has_decrease:
        warnings.append({
            "type": "nonlinear_phase_return_requires_review",
            "severity": "medium",
            "rule": "Nonlinear phase return must be explicit correction, closure, or new loop initiation.",
        })

    if any(w.get("severity") == "critical" for w in warnings):
        score = 0.0
        status = "phase_invalid_projection_skip"
    elif any(w.get("severity") == "high" for w in warnings):
        score = 0.32
        status = "phase_requires_gate_repair"
    elif warnings:
        score = 0.68
        status = "phase_valid_with_review_warning"
    elif indexes:
        score = 0.92 if (not (8 in indexes) or (6 in indexes and 7 in indexes)) else 0.72
        status = "phase_valid"
    else:
        score = 0.45
        status = "phase_unknown"
    return {
        "phase_path": path,
        "phase_indexes": indexes,
        "phase_validity_score": round(_clamp(score), 3),
        "phase_validity_status": status,
        "phase_warnings": warnings,
    }


def _boundedness(candidate: dict[str, Any], phase_info: dict[str, Any]) -> dict[str, Any]:
    novelty = _clamp(candidate.get("novelty"))
    drift = _clamp(candidate.get("drift"))
    confidence = _clamp(candidate.get("confidence"))
    kind = str(candidate.get("candidate_kind") or "")
    target = str(candidate.get("phase_target") or "")
    path = phase_info.get("phase_path") or []

    threshold = 0.55
    if kind in {"projection_gate_candidate"} or target == "Φ8" or "Φ8" in path:
        threshold = 0.30
    if kind in {"correction_candidate", "archive_candidate"} or target == "Φ6":
        threshold = 0.72
    if kind == "bounded_evolutionary_candidate":
        threshold = 0.48

    novelty_status = "repetitive_or_low_novelty" if novelty <= 0.05 else "bounded_evolutionary_novelty"
    if novelty > 0.82:
        novelty_status = "excessive_novelty_requires_archive_or_research_review"

    bounded = (drift <= threshold) and (novelty <= 0.82) and phase_info.get("phase_validity_score", 0.0) > 0.0
    if not bool(candidate.get("allowed_to_continue_to_scoring", False)):
        bounded = False

    if bounded and novelty > 0.05:
        route = "bounded_evolutionary_drift_allowed_for_scoring"
    elif bounded:
        route = "low_novelty_trace_preserving_scoring"
    elif drift > threshold:
        route = "drift_exceeds_candidate_threshold_route_to_correction_or_archive"
    elif novelty > 0.82:
        route = "novelty_exceeds_bound_route_to_research_review"
    else:
        route = "candidate_not_scoreable"

    return {
        "novelty": round(novelty, 3),
        "drift": round(drift, 3),
        "confidence": round(confidence, 3),
        "drift_threshold": round(threshold, 3),
        "novelty_status": novelty_status,
        "bounded_evolutionary_drift": bool(bounded and novelty > 0.05),
        "bounded_for_scoring": bool(bounded),
        "recommended_route": route,
        "axiom_binding": {
            "drift_not_always_error": True,
            "novelty_requires_bounded_drift": True,
            "no_projection_without_correction_naming_manifest_echo": True,
        },
    }


def _exploration_branch(candidate: dict[str, Any], index: int) -> dict[str, Any]:
    cid = _candidate_id(candidate, index)
    phase_info = _phase_validity(candidate)
    bounded = _boundedness(candidate, phase_info)
    adjacency = []
    kind = str(candidate.get("candidate_kind") or "")
    if kind == "bounded_evolutionary_candidate":
        adjacency.extend(["adjacent_theory_branch", "requires_memory_comparison", "hypothesis_only"])
    if "correction" in kind or candidate.get("phase_target") == "Φ6":
        adjacency.extend(["correction_path", "drift_reduction_branch"])
    if "naming" in kind or candidate.get("phase_target") == "Φ7" or "Φ7" in (phase_info.get("phase_path") or []):
        adjacency.extend(["naming_candidate", "definition_boundary_needed"])
    if "projection" in kind or candidate.get("phase_target") == "Φ8" or "Φ8" in (phase_info.get("phase_path") or []):
        adjacency.extend(["projection_risk", "export_gate_required"])
    if not adjacency:
        adjacency.append("trace_preserving_branch")
    branch_id = _stable_id("et_branch", {"candidate_id": cid, "bounded": bounded, "phase": phase_info}, 18)
    return {
        "branch_id": branch_id,
        "candidate_id": cid,
        "candidate_kind": candidate.get("candidate_kind"),
        "phase_target": candidate.get("phase_target"),
        "adjacency_vectors": list(dict.fromkeys(adjacency)),
        "phase_analysis": phase_info,
        "boundedness": bounded,
        "branch_allowed_to_score": bool(bounded.get("bounded_for_scoring")),
        "branch_allowed_to_render": False,
        "branch_allowed_to_write_memory": False,
        "branch_allowed_to_project": False,
    }


def explore_evolutionary_drift(candidate_report: dict[str, Any], *, max_branches: int = 12) -> dict[str, Any]:
    """Create E_t, a bounded evolutionary-drift exploration report from C_t."""
    if not isinstance(candidate_report, dict):
        candidate_report = {}
    candidates = _candidate_set(candidate_report)
    blocked = _candidate_generation_blocked(candidate_report)
    candidate_set_id = str(candidate_report.get("candidate_set_id") or _stable_id("ct_set_unknown", candidate_report))
    trace_id = str(candidate_report.get("trace_id") or ((candidate_report.get("dry_run_trace") or {}).get("trace_id") if isinstance(candidate_report.get("dry_run_trace"), dict) else "") or _stable_id("trace_unknown", candidate_report))
    branches = []
    if not blocked:
        for idx, candidate in enumerate(candidates[: max(1, min(int(max_branches or 12), 24))], start=1):
            branches.append(_exploration_branch(candidate, idx))
    else:
        branches.append({
            "branch_id": _stable_id("et_branch_blocked", candidate_report, 18),
            "candidate_id": "circuit_breaker_containment_only",
            "candidate_kind": "containment_correction_route",
            "adjacency_vectors": ["containment", "correction_or_archive_only"],
            "boundedness": {
                "bounded_for_scoring": False,
                "recommended_route": "circuit_breaker_blocks_evolutionary_exploration",
                "axiom_binding": {"drift_not_always_error": True, "novelty_requires_bounded_drift": True},
            },
            "branch_allowed_to_score": False,
            "branch_allowed_to_render": False,
            "branch_allowed_to_write_memory": False,
            "branch_allowed_to_project": False,
        })

    allowed = [b for b in branches if b.get("branch_allowed_to_score")]
    E_id = _stable_id("et", {"candidate_set_id": candidate_set_id, "branches": [b.get("branch_id") for b in branches]})
    return {
        "status": "OK",
        "engine_version": ENGINE_VERSION,
        "engine_mode": ENGINE_MODE,
        "stage": "Evolutionary Drift Explorer",
        "candidate_set_id": candidate_set_id,
        "trace_id": trace_id,
        "E_t_present": True,
        "E_t": {
            "status": "IMPLEMENTED_READ_ONLY_IN_PATCH_C2",
            "exploration_id": E_id,
            "branch_count": len(branches),
            "bounded_branch_count": len(allowed),
            "exploration_allowed": bool(not blocked and allowed),
        },
        "exploration_id": E_id,
        "source_candidate_conclusion": candidate_report,
        "evolutionary_branches": branches,
        "exploration_summary": {
            "candidate_count": len(candidates),
            "branch_count": len(branches),
            "bounded_branch_count": len(allowed),
            "blocked_by_circuit_breaker_or_candidate_gate": bool(blocked),
            "projection_allowed": False,
            "final_language_allowed": False,
            "memory_write_allowed": False,
            "manifest_allowed": False,
        },
        "recommended_sequence": [
            "Use E_t to preserve bounded novelty as inspectable branches, not as truth.",
            "Next score candidates through S_t before Correction Engine or Naming Engine.",
            "Do not render, project, write memory, or compile a manifest from E_t directly.",
        ],
        "boundary": evolutionary_drift_boundary(),
    }


def _score_candidate(candidate: dict[str, Any], branch: dict[str, Any] | None, index: int) -> dict[str, Any]:
    cid = _candidate_id(candidate, index)
    phase_info = branch.get("phase_analysis") if isinstance(branch, dict) else _phase_validity(candidate)
    bounded = branch.get("boundedness") if isinstance(branch, dict) else _boundedness(candidate, phase_info)
    novelty = _clamp(candidate.get("novelty"))
    drift = _clamp(candidate.get("drift"))
    confidence = _clamp(candidate.get("confidence"))
    memory = _memory_fit(candidate)
    phase = _clamp((phase_info or {}).get("phase_validity_score"))
    drift_fit = 1.0 - drift
    novelty_score = _novelty_fit(novelty)
    utility = _utility_fit(candidate)
    bounded_ok = bool((bounded or {}).get("bounded_for_scoring")) and bool(candidate.get("allowed_to_continue_to_scoring", False))
    if not bounded_ok:
        coherence = 0.0
        status = "not_scoreable_due_to_unbounded_drift_or_gate"
    else:
        coherence = (
            memory * 0.22
            + phase * 0.22
            + drift_fit * 0.22
            + novelty_score * 0.16
            + utility * 0.12
            + confidence * 0.06
        )
        status = "coherence_candidate_ready_for_correction_or_naming" if coherence >= 0.58 else "coherence_candidate_requires_more_recall_or_correction"
    manifest_ready = False
    return {
        "candidate_id": cid,
        "candidate_kind": candidate.get("candidate_kind"),
        "title": candidate.get("title"),
        "score_components": {
            "memory_fit": round(memory, 3),
            "phase_validity": round(phase, 3),
            "drift_fit": round(drift_fit, 3),
            "novelty_fit": round(novelty_score, 3),
            "utility_fit": round(utility, 3),
            "candidate_confidence": round(confidence, 3),
        },
        "coherence_score": round(_clamp(coherence), 3),
        "coherence_status": status,
        "boundedness": bounded,
        "phase_analysis": phase_info,
        "selected_candidate_eligible": bool(bounded_ok and coherence >= 0.58),
        "allowed_to_continue_to_correction_engine": bool(bounded_ok and coherence >= 0.42),
        "allowed_to_continue_to_naming_engine": bool(bounded_ok and coherence >= 0.58 and "Φ6" in (_phase_path(candidate) or [])),
        "allowed_to_continue_to_manifest_compiler": manifest_ready,
        "renders_final_language": False,
        "projection_allowed": False,
        "memory_write_allowed": False,
        "approved_output": False,
        "rationale": "Score combines memory fit, phase validity, drift containment, novelty fit, utility, and candidate confidence. Manifest remains blocked until correction/naming/manifest stages exist.",
    }


def score_coherence(evolution_report: dict[str, Any]) -> dict[str, Any]:
    """Create S_t, read-only coherence scores from E_t."""
    if not isinstance(evolution_report, dict):
        evolution_report = {}
    candidate_report = evolution_report.get("source_candidate_conclusion") if isinstance(evolution_report.get("source_candidate_conclusion"), dict) else {}
    candidates = _candidate_set(candidate_report)
    branches = evolution_report.get("evolutionary_branches") if isinstance(evolution_report, dict) else []
    branches_by_candidate = {}
    if isinstance(branches, list):
        for branch in branches:
            if isinstance(branch, dict):
                branches_by_candidate[str(branch.get("candidate_id"))] = branch
    scores = []
    for idx, candidate in enumerate(candidates, start=1):
        cid = _candidate_id(candidate, idx)
        scores.append(_score_candidate(candidate, branches_by_candidate.get(cid), idx))
    scores.sort(key=lambda item: (item.get("selected_candidate_eligible") is True, item.get("coherence_score", 0.0)), reverse=True)
    selected = None
    for score in scores:
        if score.get("selected_candidate_eligible"):
            selected = score
            break
    if selected is None and scores:
        selected = scores[0]
    S_id = _stable_id("st", {"exploration_id": evolution_report.get("exploration_id"), "scores": [(s.get("candidate_id"), s.get("coherence_score")) for s in scores]})
    selected_candidate = None
    if selected:
        selected_id = selected.get("candidate_id")
        for idx, candidate in enumerate(candidates, start=1):
            if _candidate_id(candidate, idx) == selected_id:
                selected_candidate = candidate
                break
    return {
        "status": "OK",
        "engine_version": ENGINE_VERSION,
        "engine_mode": ENGINE_MODE,
        "stage": "Coherence Scorer",
        "trace_id": evolution_report.get("trace_id"),
        "candidate_set_id": evolution_report.get("candidate_set_id"),
        "exploration_id": evolution_report.get("exploration_id"),
        "S_t_present": True,
        "S_t": {
            "status": "IMPLEMENTED_READ_ONLY_IN_PATCH_C2",
            "score_set_id": S_id,
            "candidate_score_count": len(scores),
            "selected_candidate_id": (selected or {}).get("candidate_id"),
            "selected_coherence_score": (selected or {}).get("coherence_score"),
            "manifest_allowed": False,
            "projection_allowed": False,
            "memory_write_allowed": False,
        },
        "score_set_id": S_id,
        "source_evolutionary_drift": evolution_report,
        "candidate_scores": scores,
        "selected_scored_candidate_preview": selected,
        "selected_candidate_meaning_state_preview": selected_candidate,
        "coherence_summary": {
            "candidate_count": len(candidates),
            "scored_count": len(scores),
            "eligible_count": sum(1 for s in scores if s.get("selected_candidate_eligible")),
            "correction_engine_next": True,
            "naming_engine_next": True,
            "manifest_compiler_allowed": False,
            "renderer_allowed": False,
            "projection_allowed": False,
            "memory_write_allowed": False,
        },
        "recommended_sequence": [
            "Use S_t to choose the strongest candidate meaning state, not to render final language.",
            "Next stage should implement Correction Engine and Naming Engine before manifest compilation.",
            "Manifest, Renderer, Echo Validator, and Memory Writer remain blocked in C2.",
        ],
        "boundary": evolutionary_drift_boundary(),
        "writes_files": False,
        "identity_vault_write": False,
        "rmc_live_memory_write": False,
        "renders_final_language": False,
        "approved_output": False,
    }

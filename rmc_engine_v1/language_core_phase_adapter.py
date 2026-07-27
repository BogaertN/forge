"""LC-RMC-001 compatibility adapter for the existing RMC phase-report contract."""

from __future__ import annotations

import datetime
import hashlib
from typing import Any

from aiweb_language_core_bootstrap.deterministic_language_runtime import (
    interpret_source,
    runtime_authority_boundary,
)
from aiweb_language_core_bootstrap.deterministic_language_runtime.authority import (
    STATUS_AMBIGUOUS,
    STATUS_INTERPRETED,
)
from aiweb_language_core_bootstrap.deterministic_language_runtime.forge_profile import (
    action_profile,
)


ADAPTER_VERSION = "lc-rmc-001.rmc-phase-adapter.v1"
AMBIGUOUS_MEANING_HELD = "LC_RMC_001_AMBIGUOUS_MEANING_HELD"
NEGATED_ACTION_HELD = "LC_RMC_001_NEGATED_ACTION_HELD"

_PHASE_ROUTING = {
    "Φ3": "identify_direction",
    "Φ6": "correction_engine",
    "Φ8": "projection_gate",
}


def phase_adapter_boundary() -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "stable_entrypoint": "rmc_engine_v1.phase_parser.parse_phase",
        "delegates_to_deterministic_language_core": True,
        "legacy_heuristic_fallback": False,
        "phase_report_is_execution_authority": False,
        "phase_report_is_permission": False,
        "phase_report_is_output_authority": False,
        "phase_report_is_memory_write_authority": False,
        "calls_llm": False,
        "queries_chroma": False,
        "uses_embeddings": False,
        "uses_vector_store": False,
        "reads_files": False,
        "writes_files": False,
        "routes_tools": False,
        "executes_actions": False,
        "runtime_boundary": runtime_authority_boundary(),
    }


def _input_event(source_text: str, source_metadata: dict[str, Any]) -> dict[str, Any]:
    digest = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    return {
        "event_id": f"it_lc_rmc_001_{digest[:16]}",
        "x_t_raw_input_preview": source_text[:1200],
        "x_t_raw_input_sha256": digest,
        "x_t_raw_input_length": len(source_text),
        "c_t_context_source": source_metadata,
        "u_t_identity_context": {
            "operator_console": True,
            "forge_governs": True,
            "ui_is_authority": False,
            "language_interpretation_is_authority": False,
        },
        "tau_t_generated_at_utc": (
            datetime.datetime.now(datetime.UTC)
            .replace(microsecond=0)
            .isoformat()
        ),
        "dry_run": True,
        "source_immutable": True,
    }


def _drift_foundation_anchor() -> dict[str, Any]:
    return {
        "memory_drift_protoforge2_required": True,
        "memory_drift_py_required": True,
        "drift_taxonomy_required": [
            "syntactic",
            "semantic",
            "recursive",
            "catastrophic",
            "evolutionary",
            "resonant",
            "structural",
        ],
        "epsilon_s_required": "ε_s = (σ_res + D_score + |ΔΦ|) / n",
        "chi_t_correction_required": True,
        "circuit_breaker_required": True,
        "phase_skip_detection_required": True,
        "language_core_semantic_signature_required": True,
    }


def interpret_phase(
    source_text: str,
    source_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map a typed deterministic interpretation into the legacy phase shape."""

    if type(source_text) is not str:
        raise TypeError("source_text must be an exact str")
    if source_metadata is None:
        metadata: dict[str, Any] = {}
    elif type(source_metadata) is dict:
        metadata = dict(source_metadata)
    else:
        raise TypeError("source_metadata must be a dict or None")

    envelope = interpret_source(source_text, metadata)
    envelope_dict = envelope.to_dict()
    first_candidate = envelope.candidates[0] if envelope.candidates else None
    accepted = (
        envelope.status == STATUS_INTERPRETED
        and len(envelope.candidates) == 1
        and first_candidate is not None
        and not first_candidate.negated
    )
    input_event = _input_event(source_text, metadata)

    if accepted:
        first = first_candidate
        assert first is not None
        profile = action_profile(first.action_root_key)
        phase_primary = profile.phase_primary
        confidence = 0.88 if envelope.status == STATUS_AMBIGUOUS else 1.0
        phase_candidates = [
            {
                "phase": phase_primary,
                "index": int(phase_primary.replace("Φ", "")),
                "role": "Language Core-derived RMC phase compatibility candidate",
                "routing": _PHASE_ROUTING[phase_primary],
                "confidence": confidence,
                "evidence": [
                    f"language_core_action_root:{candidate.action_root_key}",
                    f"language_core_candidate:{candidate.candidate_id}",
                ],
                "linguistic_candidate_id": candidate.candidate_id,
                "selected_meaning": False,
            }
            for candidate in envelope.candidates
        ]
        routing = [
            _PHASE_ROUTING[phase_primary],
            "next_module:drift_analyzer",
        ]
        warnings = []
        if phase_primary == "Φ8":
            warnings.append(
                {
                    "type": "language_meaning_is_not_projection_authority",
                    "from": phase_primary,
                    "to": phase_primary,
                    "law": (
                        "report meaning does not authorize rendering, delivery, "
                        "publication, or output"
                    ),
                }
            )
        phase_state = {
            "phase_primary": phase_primary,
            "phase_primary_role": (
                "Language Core-derived compatibility phase; not selected meaning"
            ),
            "phase_secondary": [],
            "phase_path_hypothesis": [phase_primary],
            "confidence": confidence,
            "confidence_status": (
                "linguistic_ambiguity_preserved"
                if envelope.status == STATUS_AMBIGUOUS
                else "language_core_interpretation_complete"
            ),
            "token_boundary_mode": "lc_rmc_001_exact_source_spans",
            "phase_candidates": phase_candidates,
            "transition_warnings": warnings,
            "routing": routing,
            "projection_warning": (
                "Language interpretation never grants projection or delivery."
            ),
            "interpretation_status": envelope.status,
            "interpretation_complete": envelope.coverage_complete,
            "action_root_key": first.action_root_key,
            "action_root_id": first.action_root_id,
            "predicate_id": first.predicate_id,
            "predicate_frame_id": first.frame_id,
            "negated": first.negated,
            "semantic_signature": envelope.semantic_signature,
            "linguistic_candidate_count": len(envelope.candidates),
            "selected_meaning_created": False,
        }
        status = "OK"
        reason_code = None
    else:
        if envelope.status == STATUS_AMBIGUOUS:
            held_reason = AMBIGUOUS_MEANING_HELD
        elif first_candidate is not None and first_candidate.negated:
            held_reason = NEGATED_ACTION_HELD
        else:
            held_reason = envelope.refusal_code or "LC_RMC_001_UNRESOLVED"

        held_candidates = [
            {
                "phase": None,
                "index": None,
                "role": "unadmitted Language Core candidate held before RMC",
                "routing": "stop_before_rmc_meaning_admission",
                "confidence": 0.0,
                "evidence": [held_reason],
                "linguistic_candidate_id": candidate.candidate_id,
                "action_root_key": candidate.action_root_key,
                "negated": candidate.negated,
                "selected_meaning": False,
            }
            for candidate in envelope.candidates
        ]
        if not held_candidates:
            held_candidates = [
                {
                    "phase": None,
                    "index": None,
                    "role": "typed unresolved Language Core result",
                    "routing": "stop_before_rmc_meaning_admission",
                    "confidence": 0.0,
                    "evidence": [held_reason],
                    "linguistic_candidate_id": None,
                    "action_root_key": None,
                    "negated": False,
                    "selected_meaning": False,
                }
            ]
        phase_state = {
            "phase_primary": None,
            "phase_primary_role": "language_core_admission_held",
            "phase_secondary": [],
            "phase_path_hypothesis": [],
            "confidence": 0.0,
            "confidence_status": "language_core_admission_held",
            "token_boundary_mode": "lc_rmc_001_exact_source_spans",
            "phase_candidates": held_candidates,
            "transition_warnings": [
                {
                    "type": "language_core_admission_hold",
                    "from": None,
                    "to": None,
                    "law": (
                        "no RMC admission or heuristic fallback after a "
                        "Language Core hold"
                    ),
                }
            ],
            "routing": ["stop_before_rmc_meaning_admission"],
            "projection_warning": (
                "Unresolved language cannot proceed to projection or delivery."
            ),
            "interpretation_status": envelope.status,
            "interpretation_complete": False,
            "action_root_key": (
                first_candidate.action_root_key if first_candidate is not None else None
            ),
            "action_root_id": (
                first_candidate.action_root_id if first_candidate is not None else None
            ),
            "predicate_id": (
                first_candidate.predicate_id if first_candidate is not None else None
            ),
            "predicate_frame_id": (
                first_candidate.frame_id if first_candidate is not None else None
            ),
            "negated": (
                first_candidate.negated if first_candidate is not None else False
            ),
            "semantic_signature": envelope.semantic_signature,
            "linguistic_candidate_count": len(envelope.candidates),
            "selected_meaning_created": False,
        }
        status = "UNRESOLVED"
        reason_code = held_reason

    return {
        "status": status,
        "reason_code": reason_code,
        "input_event": input_event,
        "phase_state": phase_state,
        "language_core_interpretation": envelope_dict,
        "drift_foundation_anchor": _drift_foundation_anchor(),
        "engine_boundary": phase_adapter_boundary(),
        "language_core_admitted": accepted,
        "candidate_pipeline_eligible": accepted,
        "fallback_performed": False,
        "writes_files": False,
        "identity_vault_write": False,
        "rmc_live_memory_write": False,
        "approved_output": False,
        "permission_granted": False,
        "route_authorized": False,
        "tool_authorized": False,
        "execution_authorized": False,
        "delivery_authorized": False,
    }


__all__ = (
    "ADAPTER_VERSION",
    "AMBIGUOUS_MEANING_HELD",
    "NEGATED_ACTION_HELD",
    "interpret_phase",
    "phase_adapter_boundary",
)

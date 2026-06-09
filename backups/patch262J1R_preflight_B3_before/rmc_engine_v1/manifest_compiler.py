"""RMC manifest compiler kernel v1.

Patch 262J: side-effect-free Manifest Compiler dry-run.
Patch 262J1R-Preflight: adds manifest packet schema validation.

This module compiles an internal manifest packet from the math-bound coherence
response only. It performs no I/O, no shell execution, no model calls, no DB
reads, no memory writes, and no final language projection.

Changes in 262J1R-Preflight
-----------------------------
- Added _validate_manifest_packet() guard. The compiler now refuses to return
  a manifest_packet unless all 12 required schema sections are present. If any
  section is missing, it returns a schema_violation error instead of a partial
  manifest.
- Added manifest_compiler_boundary() for consistency with other engine modules.
"""

from __future__ import annotations

from typing import Any
import hashlib

ENGINE_VERSION = "rmc_manifest_compiler_kernel_v1_patch262J1R_preflight"

REQUIRED_MANIFEST_SECTIONS = [
    "manifest_id",
    "source_trace",
    "phase_path",
    "operator_path",
    "drift_status",
    "candidate_identity",
    "coherence_terms",
    "gates",
    "render_targets",
    "limitations",
    "echo_requirements",
    "memory_writeback_contract",
]


def _stable_digest(value: Any, size: int = 16) -> str:
    return hashlib.sha256(
        repr(value).encode("utf-8", errors="replace")
    ).hexdigest()[:size]


def _safe_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list:
    return value if isinstance(value, list) else []


# ── Public: boundary declaration ─────────────────────────────────────────────

def manifest_compiler_boundary() -> dict:
    return {
        "engine_version": ENGINE_VERSION,
        "manifest_kernel_location": "forge/rmc_engine_v1/manifest_compiler.py",
        "ui_owns_manifest_logic": False,
        "main_py_owns_manifest_logic": False,
        "engine_module_owns_manifest_logic": True,
        "side_effect_free": True,
        "calls_llm": False,
        "queries_chroma": False,
        "reads_db_files": False,
        "writes_files": False,
        "writes_rmc_memory": False,
        "writes_identity_vault": False,
        "schema_validation_active": True,
        "required_sections_count": len(REQUIRED_MANIFEST_SECTIONS),
    }


# ── Public: schema contract ───────────────────────────────────────────────────

def manifest_schema_contract() -> dict:
    """Schema contract for dry-run manifest packets.

    This is not the final public renderer. It is the internal meaning packet that
    future renderers and echo validators may consume after correction/naming.
    """
    return {
        "engine_version": ENGINE_VERSION,
        "manifest_kernel_location": "forge/rmc_engine_v1/manifest_compiler.py",
        "manifest_is_final_language": False,
        "manifest_is_memory_write": False,
        "required_sections": REQUIRED_MANIFEST_SECTIONS,
        "no_trace_no_approval": True,
        "no_projection_from_manifest_dry_run": True,
        "echo_validation_required_before_projection": True,
        "memory_write_requires_gate_and_receipt": True,
        "schema_validation_enforced": True,
    }


# ── Internal: schema validation ───────────────────────────────────────────────

def _validate_manifest_packet(packet: dict) -> list[str]:
    """Return a list of missing required section keys.

    An empty list means the packet is schema-valid. Any non-empty list
    means the compiler must refuse to return the packet.
    """
    return [
        section
        for section in REQUIRED_MANIFEST_SECTIONS
        if section not in packet
    ]


# ── Public: compile ───────────────────────────────────────────────────────────

def compile_manifest_dry_run(coherence_report: dict) -> dict:
    """Compile a dry-run manifest packet from a coherence-gated candidate.

    If the coherence gate does not allow manifest dry-run, this function returns
    a blocked preflight report instead of fabricating a manifest. That is the
    critical structural rule: the compiler must not pretend an uncorrected or
    unnamed candidate is manifest-ready.

    If the coherence gate allows compilation but the resulting packet fails schema
    validation (missing required sections), the compiler returns a schema_violation
    error. A partial manifest must not be returned.
    """
    coherence_report = _safe_dict(coherence_report)
    selected = _safe_dict(coherence_report.get("selected_scored_candidate_preview"))
    source_candidate = _safe_dict(coherence_report.get("source_candidate_conclusion"))
    source_drift = _safe_dict(source_candidate.get("source_drift_report"))
    source_phase = _safe_dict(source_drift.get("source_phase_parser"))

    manifest_gate = _safe_dict(selected.get("manifest_gate"))
    correction_gate = _safe_dict(selected.get("correction_gate"))
    naming_gate = _safe_dict(selected.get("naming_gate"))
    projection_gate = _safe_dict(selected.get("projection_gate"))
    cold_storage_gate = _safe_dict(selected.get("cold_storage_gate"))
    math_terms = _safe_dict(selected.get("math_terms"))
    score_components = _safe_dict(selected.get("score_components"))

    manifest_allowed = bool(manifest_gate.get("allowed"))
    blocked_reasons: list[str] = []

    if not selected:
        blocked_reasons.append("no selected scored candidate")
    if not bool(correction_gate.get("passed")):
        blocked_reasons.append("Φ6 correction gate has not passed")
    if not bool(naming_gate.get("passed")):
        blocked_reasons.append("Φ7 naming gate has not passed")
    if cold_storage_gate.get("route") != "active_stack_dry_run_candidate":
        blocked_reasons.append("candidate is not on active-stack route")
    if bool(projection_gate.get("allowed")):
        blocked_reasons.append("projection gate must remain blocked during dry-run")
    if not manifest_allowed:
        blocked_reasons.append("manifest_gate.allowed is false")

    source_trace = {
        "coherence_run_id": coherence_report.get("coherence_run_id"),
        "candidate_set_id": source_candidate.get("candidate_set_id"),
        "drift_report_id": source_drift.get("drift_report_id"),
        "input_event_id": _safe_dict(source_phase.get("input_event")).get("event_id"),
        "phase_parser_mode": source_phase.get("mode"),
        "drift_analyzer_mode": source_drift.get("mode"),
        "candidate_generator_mode": source_candidate.get("mode"),
        "coherence_gate_mode": coherence_report.get("mode"),
    }

    phase_state = _safe_dict(source_phase.get("phase_state"))
    drift_status = {
        "epsilon_s": _safe_dict(source_drift.get("epsilon_s")),
        "phase_drift": _safe_dict(source_drift.get("phase_drift")),
        "chi_t": _safe_dict(source_drift.get("chi_t")),
        "circuit_breaker": _safe_dict(source_drift.get("circuit_breaker")),
        "projection_status": source_drift.get("projection_status"),
    }

    dry_run_id = "manifest_dry_run_" + _stable_digest({
        "source_trace": source_trace,
        "selected": selected.get("candidate_id"),
        "coherence": selected.get("coherence_score"),
        "allowed": manifest_allowed,
        "blocked_reasons": blocked_reasons,
    })

    preflight = {
        "manifest_dry_run_id": dry_run_id,
        "manifest_compilation_allowed": manifest_allowed,
        "blocked_reasons": blocked_reasons,
        "required_before_manifest": [
            r for r in blocked_reasons
            if r != "projection gate must remain blocked during dry-run"
        ],
        "source_trace": source_trace,
        "selected_candidate_id": selected.get("candidate_id"),
        "selected_candidate_title": selected.get("title"),
        "coherence_score": selected.get("coherence_score"),
        "status": "manifest_preflight_blocked" if not manifest_allowed else "manifest_dry_run_compiled",
    }

    manifest_packet = None
    schema_violation: list[str] = []

    if manifest_allowed:
        candidate_packet: dict[str, Any] = {
            "manifest_id": dry_run_id,
            "manifest_kind": "internal_rmc_manifest_dry_run",
            "approved_output": False,
            "projection_allowed": False,
            "final_language_allowed": False,
            "memory_write_allowed": False,
            "source_trace": source_trace,
            "candidate_identity": {
                "candidate_id": selected.get("candidate_id"),
                "title": selected.get("title"),
                "candidate_type": selected.get("candidate_type"),
                "phase_target": selected.get("phase_target"),
                "drift_posture": selected.get("drift_posture"),
            },
            "phase_path": {
                "primary": phase_state.get("phase_primary"),
                "secondary": phase_state.get("phase_secondary"),
                "hypothesis": phase_state.get("phase_path_hypothesis"),
                "math_terms_phase_path": math_terms.get("phase_path"),
                "phase_skip_risk": math_terms.get("phase_skip_risk"),
            },
            "operator_path": [
                "InputEvent",
                "PhaseParser",
                "DriftAnalyzer",
                "CandidateConclusion",
                "CoherenceGate",
                "ManifestCompilerDryRun",
            ],
            "drift_status": drift_status,
            "coherence_terms": {
                "math_terms": math_terms,
                "score_components": score_components,
                "formal_math_binding": selected.get("formal_math_binding"),
                "math_kernel_location": selected.get("math_kernel_location"),
            },
            "gates": {
                "correction_gate": correction_gate,
                "naming_gate": naming_gate,
                "manifest_gate": manifest_gate,
                "projection_gate": projection_gate,
                "cold_storage_gate": cold_storage_gate,
            },
            "limitations": selected.get("required_limitations") or [],
            "render_targets": {
                "text": {"status": "disabled_until_echo_validator", "file_written": False},
                "json_packet": {"status": "preview_only", "file_written": False},
                "glyph": {"status": "disabled_until_echo_validator", "file_written": False},
                "cymatic_geometry": {
                    "status": "preview_only_existing_browser_layer",
                    "file_written": False,
                },
                "dashboard_state": {"status": "preview_only", "file_written": False},
                "memory_record": {"status": "disabled_until_writeback_gate", "file_written": False},
            },
            "echo_requirements": {
                "echo_validator_required": True,
                "round_trip_manifest_required": True,
                "semantic_drift_check_required": True,
                "render_fidelity_check_required": True,
                "next_patch": "Patch 262K — RMC Echo Validator Preview",
            },
            "memory_writeback_contract": {
                "memory_write_allowed": False,
                "requires_dry_run": True,
                "requires_approval_gate": True,
                "requires_receipt": True,
                "requires_rollback_or_suppression_path": True,
            },
        }

        # ── Schema validation guard ──────────────────────────────────────────
        # A manifest packet must contain all required sections. A partial packet
        # must not be returned. This guard fires here so it is engine-enforced,
        # not endpoint-enforced.
        schema_violation = _validate_manifest_packet(candidate_packet)
        if not schema_violation:
            manifest_packet = candidate_packet
        else:
            # Schema failure: return blocked preflight, no manifest_packet.
            preflight["status"] = "manifest_schema_violation"
            preflight["schema_violation"] = schema_violation
            manifest_allowed = False

    return {
        "engine_version": ENGINE_VERSION,
        "manifest_schema_contract": manifest_schema_contract(),
        "manifest_compiler_boundary": manifest_compiler_boundary(),
        "preflight": preflight,
        "manifest_packet": manifest_packet,
        "manifest_compilation_allowed": manifest_allowed and not schema_violation,
        "schema_validation_result": {
            "passed": not bool(schema_violation),
            "missing_sections": schema_violation,
            "required_sections_checked": REQUIRED_MANIFEST_SECTIONS,
        },
        "approved_output": False,
        "projection_allowed": False,
        "final_language_allowed": False,
        "memory_write_allowed": False,
        "writes_files": False,
        "identity_vault_write": False,
        "rmc_live_memory_write": False,
    }

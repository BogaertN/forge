"""RMC Phase Parser engine module v1.

Patch 262J1R-Preflight: extracted from forge/main.py _p262f_* functions.

This module is pure Python and side-effect free. It performs no I/O, no shell
execution, no model calls, no Chroma queries, no DB reads, and no memory writes.

The endpoint/UI must supply source_text and call this engine.
The engine must not call back into main.py or endpoint code.
That boundary is the point of this extraction.

Public API
----------
parse_phase(source_text, source_metadata=None) -> dict
    Build a phase_state object from input text. Returns the full phase_state
    dict as the endpoint returned it, minus the HTTP envelope. Called by the
    thin adapter in main.py.

phase_catalog() -> dict
    Read-only Φ1–Φ9 phase definitions.

phase_parser_boundary() -> dict
    Engine boundary declaration for this module.
"""

from __future__ import annotations

import re
import hashlib
import datetime
from typing import Any

ENGINE_VERSION = "rmc_phase_parser_engine_v1_patch262J1R_preflight"


# ── Public: boundary declaration ────────────────────────────────────────────

def phase_parser_boundary() -> dict:
    """Engine boundary declaration.

    Returns a machine-readable record of what this module does and does not do.
    Consumed by the thin adapter and surfaced in the endpoint response.
    """
    return {
        "engine_version": ENGINE_VERSION,
        "engine_module_location": "forge/rmc_engine_v1/phase_parser.py",
        "ui_owns_phase_logic": False,
        "main_py_owns_phase_logic": False,
        "engine_module_owns_phase_logic": True,
        "side_effect_free": True,
        "calls_llm": False,
        "queries_chroma": False,
        "reads_db_files": False,
        "writes_files": False,
        "writes_rmc_memory": False,
        "writes_identity_vault": False,
        "calls_main_py_functions": False,
        "source_text_supplied_by_adapter": True,
        "note": (
            "The adapter (main.py) resolves source_text from query params or the "
            "memory-object endpoint before calling this engine. The engine itself "
            "never touches main.py internals."
        ),
    }


# ── Public: phase catalog ────────────────────────────────────────────────────

def phase_catalog() -> dict:
    """Φ1–Φ9 phase definitions. Read-only."""
    return {
        "Φ1": {
            "index": 1,
            "role": "Initiation / seed",
            "routing": "establish_context",
            "keywords": ["start", "begin", "seed", "new", "first", "initiate",
                         "open", "create", "build"],
        },
        "Φ2": {
            "index": 2,
            "role": "Polarity / contrast",
            "routing": "identify_poles",
            "keywords": ["versus", "compare", "difference", "contrast",
                         "opposite", "polarity", "either", "or", "mirror"],
        },
        "Φ3": {
            "index": 3,
            "role": "Desire / vector",
            "routing": "identify_direction",
            "keywords": ["want", "need", "goal", "plan", "direction", "aim",
                         "path", "next", "ready"],
        },
        "Φ4": {
            "index": 4,
            "role": "Friction / constraint",
            "routing": "surface_constraint",
            "keywords": ["problem", "blocked", "issue", "bug", "fail", "error",
                         "constraint", "stuck", "why"],
        },
        "Φ5": {
            "index": 5,
            "role": "Entropy / drift",
            "routing": "drift_analyzer_required",
            "keywords": ["drift", "confused", "hallucination", "collapse",
                         "unstable", "wrong", "danger", "loop", "slip"],
        },
        "Φ6": {
            "index": 6,
            "role": "Correction / coherence return",
            "routing": "correction_engine",
            "keywords": ["correct", "fix", "repair", "realign", "verify",
                         "ground", "coherence", "return", "χ", "christ"],
        },
        "Φ7": {
            "index": 7,
            "role": "Naming / identity lock",
            "routing": "naming_engine",
            "keywords": ["name", "define", "definition", "classify", "label",
                         "identity", "schema", "contract", "codex"],
        },
        "Φ8": {
            "index": 8,
            "role": "Projection / outward expression",
            "routing": "projection_gate",
            "keywords": ["publish", "ship", "render", "export", "output",
                         "show", "public", "run", "launch", "deploy"],
        },
        "Φ9": {
            "index": 9,
            "role": "Closure / octave transition",
            "routing": "closure_or_archive",
            "keywords": ["finish", "complete", "close", "seal", "archive",
                         "handover", "done", "final", "octave"],
        },
    }


# ── Internal helpers ─────────────────────────────────────────────────────────

def _evidence_for_phase(text_lower: str, phase_key: str, entry: dict) -> list:
    evidence = []
    for kw in entry.get("keywords", []):
        if str(kw).lower() in text_lower:
            evidence.append(f"keyword:{kw}")
    idx = entry.get("index")
    for token in (f"φ{idx}", f"phi{idx}", f"phase {idx}",
                  f"phase_{idx}", f"u03a6{idx}"):
        if token.lower() in text_lower:
            evidence.append(f"explicit:{token}")
    return evidence[:12]


def _rank_phases(text: str) -> list:
    catalog = phase_catalog()
    text_lower = str(text or "").lower()
    token_count = max(1, len(re.findall(r"\w+", text_lower)))
    ranked = []
    for phase_key, entry in catalog.items():
        evidence = _evidence_for_phase(text_lower, phase_key, entry)
        explicit_weight = sum(3 for item in evidence if item.startswith("explicit:"))
        keyword_weight = sum(1 for item in evidence if item.startswith("keyword:"))
        base = explicit_weight + keyword_weight
        confidence = round(
            min(0.96, 0.08 + (base * 0.12)
                + min(0.18, len(evidence) / max(12, token_count))),
            3,
        ) if base else 0.03
        ranked.append({
            "phase": phase_key,
            "index": entry.get("index"),
            "role": entry.get("role"),
            "routing": entry.get("routing"),
            "confidence": confidence,
            "evidence": evidence,
        })
    ranked.sort(
        key=lambda item: (item.get("confidence", 0), len(item.get("evidence", []))),
        reverse=True,
    )
    if ranked and ranked[0].get("confidence", 0) <= 0.05:
        ranked[0]["confidence"] = 0.18
        ranked[0]["evidence"] = ["fallback:unclassified_input_treated_as_seed"]
    return ranked


def _phase_path_hypothesis(ranked: list) -> list:
    top = [item for item in ranked if item.get("confidence", 0) >= 0.12]
    if not top and ranked:
        top = [ranked[0]]
    ordered = sorted(top[:5], key=lambda item: item.get("index", 0))
    return [item.get("phase") for item in ordered]


def _transition_warnings(path: list) -> list:
    warnings = []
    nums: list[int] = []
    for phase in path:
        try:
            nums.append(int(str(phase).replace("Φ", "")))
        except Exception:
            pass
    for a, b in zip(nums, nums[1:]):
        if a == 5 and b >= 8:
            warnings.append({
                "type": "phase_skip_projection_risk",
                "from": f"Φ{a}",
                "to": f"Φ{b}",
                "law": "drift must pass correction/naming before projection",
            })
        elif b - a > 2:
            warnings.append({
                "type": "phase_skip_review",
                "from": f"Φ{a}",
                "to": f"Φ{b}",
                "law": "ordered phase transition expected unless explicitly marked exploratory",
            })
    return warnings


def _build_input_event(source_text: str, source_metadata: dict | None) -> dict:
    source_metadata = source_metadata or {}
    digest = (
        hashlib.sha256(source_text.encode("utf-8", errors="replace")).hexdigest()[:16]
        if source_text
        else "empty_input"
    )
    return {
        "event_id": f"it_preview_{digest}",
        "x_t_raw_input_preview": source_text[:1200],
        "c_t_context_source": source_metadata,
        "u_t_identity_context": {
            "operator_console": True,
            "forge_governs": True,
            "ui_is_authority": False,
        },
        "tau_t_generated_at_utc": (
            datetime.datetime.now(datetime.UTC)
            .replace(microsecond=0)
            .isoformat()
        ),
        "dry_run": True,
    }


def _build_routing(primary: dict, phase_path: list, warnings: list) -> list:
    routing = []
    if primary.get("routing"):
        routing.append(primary.get("routing"))
    if any(w.get("type") == "phase_skip_projection_risk" for w in warnings):
        routing.append("drift_analyzer_required_before_projection")
    if "Φ5" in phase_path:
        routing.append("drift_analyzer_required")
    if "Φ6" in phase_path:
        routing.append("correction_gate_candidate")
    if "Φ7" in phase_path:
        routing.append("naming_gate_candidate")
    routing.append("next_module:drift_analyzer")
    return routing


# ── Public: main engine function ─────────────────────────────────────────────

def parse_phase(source_text: str, source_metadata: dict | None = None) -> dict:
    """Parse phase state from source text.

    Parameters
    ----------
    source_text:
        The raw text to classify. The adapter is responsible for resolving
        this from query params, memory-object, or receipt. This engine does
        not fetch it.
    source_metadata:
        Optional dict describing how source_text was obtained (source_kind,
        selector, file, etc.). Passed through to the input_event record.

    Returns
    -------
    dict with keys: input_event, phase_state, drift_foundation_anchor,
    engine_boundary, and top-level boundary/mode flags.
    """
    source_text = str(source_text or "")
    ranked = _rank_phases(source_text)
    primary = ranked[0] if ranked else {}
    secondary = ranked[1:4] if len(ranked) > 1 else []
    phase_path = _phase_path_hypothesis(ranked)
    warnings = _transition_warnings(phase_path)
    routing = _build_routing(primary, phase_path, warnings)
    input_event = _build_input_event(source_text, source_metadata)

    phase_state = {
        "phase_primary": primary.get("phase"),
        "phase_primary_role": primary.get("role"),
        "phase_secondary": [item.get("phase") for item in secondary],
        "phase_path_hypothesis": phase_path,
        "confidence": primary.get("confidence", 0),
        "phase_candidates": ranked,
        "transition_warnings": warnings,
        "routing": routing,
        "projection_warning": (
            "Projection requires Φ6 correction and Φ7 naming before Φ8 export."
            if (primary.get("phase") == "Φ8" or any(warnings))
            else "No projection warning from parser dry-run."
        ),
    }

    drift_foundation_anchor = {
        "memory_drift_protoforge2_required": True,
        "memory_drift_py_required": True,
        "drift_taxonomy_required": [
            "syntactic", "semantic", "recursive", "catastrophic",
            "evolutionary", "resonant", "structural",
        ],
        "epsilon_s_required": "ε_s = (σ_res + D_score + |ΔΦ|) / n",
        "chi_t_correction_required": True,
        "circuit_breaker_required": True,
        "phase_skip_detection_required": True,
        "note": (
            "Drift Analyzer must implement against these anchors. "
            "Phase Parser does not perform drift analysis itself."
        ),
    }

    return {
        "input_event": input_event,
        "phase_state": phase_state,
        "drift_foundation_anchor": drift_foundation_anchor,
        "engine_boundary": phase_parser_boundary(),
        "writes_files": False,
        "identity_vault_write": False,
        "rmc_live_memory_write": False,
        "approved_output": False,
    }

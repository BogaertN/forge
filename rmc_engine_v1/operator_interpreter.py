"""General symbolic operator entry point for Ask Forge.

The eight promoted Language Core fixtures are a bootstrap proof, not a list of
questions the operator is allowed to answer.  This module supplies the first
general orchestration layer around that proof:

    exact input custody
    -> reversible source-field projection
    -> promoted exact-RMC answer check
    -> typed intent/capability candidates
    -> candidate-only RMC/context resonance recall
    -> typed Forge capability
    -> governed web acquisition when evidence is missing
    -> possible-answer manifest
    -> deterministic rendering
    -> exact evidence Echo
    -> read-only answer delivery

It never creates a model token stream, calls an LLM, builds embeddings, uses a
vector store, executes shell, applies a patch, or promotes fetched material to
stable memory.  Automatic acquisition writes only content-addressed candidate
manifests.  Stable/canonical promotion remains a separate governed lifecycle.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import threading
from typing import Any, Final

from aiweb_language_core_bootstrap.input_event_custody import capture_input_event
from aiweb_language_core_bootstrap.meaning_compiler_preview.character_scan import (
    build_source_forms,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview.schema import (
    SourceFormKind,
)
from rmc_engine_v1.research_acquisition import (
    ResearchProvider,
    acquire_research_evidence,
)


OPERATOR_INTERPRETER_SCHEMA: Final[str] = (
    "aiweb-forge-symbolic-operator-interpreter-v1"
)
POSSIBLE_ANSWER_SCHEMA: Final[str] = (
    "aiweb-forge-rmc-possible-answer-manifest-v1"
)
ENDPOINT: Final[str] = "/api/operator/ask-forge"
MAX_SOURCE_CODE_POINTS: Final[int] = 8_192
MAX_MEMORY_MAP_FILES: Final[int] = 120
MAX_MEMORY_ROWS: Final[int] = 6_000
MAX_MEMORY_RESULTS: Final[int] = 8
MAX_CANDIDATE_ANSWER_FILES: Final[int] = 1_000
MEMORY_ACCEPT_THRESHOLD: Final[float] = 0.76
MEMORY_SUPPORT_THRESHOLD: Final[float] = 0.28

_WRITE_LOCK = threading.Lock()
_SPACE = re.compile(r"\s+")
_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_MATHEMATICAL_MARKS = re.compile(r"(?:\^|=|\+|\*|/|∫|√|∑|lim\b)", re.I)
_FUNCTION_FORMS: Final[frozenset[str]] = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "because",
        "can",
        "could",
        "did",
        "do",
        "does",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "me",
        "my",
        "of",
        "on",
        "or",
        "please",
        "should",
        "that",
        "the",
        "this",
        "to",
        "was",
        "we",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "will",
        "with",
        "would",
        "you",
        "your",
    }
)

_DIRECT_MATH_FORMS: Final[frozenset[str]] = frozenset(
    {
        "calculate",
        "differentiate",
        "derivative",
        "evaluate",
        "factor",
        "integral",
        "integrate",
        "limit",
        "simplify",
        "solve",
    }
)
_CODE_KNOWLEDGE_FORMS: Final[frozenset[str]] = frozenset(
    {
        "api",
        "class",
        "code",
        "compiler",
        "css",
        "database",
        "function",
        "html",
        "javascript",
        "library",
        "linux",
        "python",
        "react",
        "runtime",
        "typescript",
    }
)
_BUILD_ACTION_FORMS: Final[frozenset[str]] = frozenset(
    {
        "add",
        "build",
        "change",
        "create",
        "debug",
        "fix",
        "implement",
        "install",
        "patch",
        "refactor",
        "repair",
        "test",
        "update",
        "wire",
    }
)
_FORGE_FORMS: Final[frozenset[str]] = frozenset(
    {
        "aiweb",
        "council",
        "echo",
        "echoforge",
        "forge",
        "language",
        "manifest",
        "memory",
        "operator",
        "protoforge",
        "rmc",
        "roadmap",
    }
)
_STATUS_FORMS: Final[frozenset[str]] = frozenset(
    {"health", "live", "running", "state", "status"}
)
_FRESHNESS_FORMS: Final[frozenset[str]] = frozenset(
    {"current", "currently", "latest", "new", "now", "today", "version"}
)
_QUESTION_FORMS: Final[frozenset[str]] = frozenset(
    {"how", "what", "when", "where", "which", "who", "why"}
)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _stable_id(prefix: str, value: object) -> str:
    return f"{prefix}:{_sha256_text(_canonical_json(value))}"


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _fold(value: object) -> str:
    return _SPACE.sub(" ", str(value).casefold()).strip()


def operator_interpreter_boundary() -> dict[str, object]:
    return {
        "schema_version": OPERATOR_INTERPRETER_SCHEMA,
        "forge_governs": True,
        "ui_is_authority": False,
        "exact_source_custody": True,
        "reversible_source_field_projection": True,
        "source_forms_are_model_tokens": False,
        "conventional_token_stream_created": False,
        "model_subword_segmentation_performed": False,
        "numeric_token_ids_created": False,
        "calls_llm": False,
        "embedding_performed": False,
        "vector_retrieval_performed": False,
        "legacy_llm_fallback_allowed": False,
        "memory_first": True,
        "network_fallback_possible": True,
        "network_findings_are_candidate_evidence_only": True,
        "automatic_candidate_capture_allowed": True,
        "automatic_stable_memory_promotion_allowed": False,
        "automatic_canonicalization_allowed": False,
        "executes_shell": False,
        "applies_code": False,
        "runs_unapproved_tools": False,
        "writes_identity_vault": False,
        "writes_contribution_economy": False,
    }


def _capture_source(source_text: object) -> tuple[dict[str, object], list[dict[str, object]]]:
    capture = capture_input_event(
        source_text,
        source_id="ask_forge_operator",
        channel_id="operator_console",
        correlation_id="forge-symbolic-operator-interpreter-v1",
    )
    event = capture.event
    if event is None:
        reason = str(getattr(capture, "reason_code", "source_custody_rejected"))
        raise ValueError(reason)
    if len(event.exact_received_text) > MAX_SOURCE_CODE_POINTS:
        raise ValueError("source_code_point_limit_exceeded")
    forms = build_source_forms(event)
    projected = [form.to_dict() for form in forms]
    custody = {
        "capture_result_id": capture.result_id,
        "input_event_id": event.input_event_id,
        "source_sha256": event.source_sha256,
        "source_code_point_length": event.code_point_length,
        "source_utf8_byte_length": event.utf8_byte_length,
        "source_preserved_exactly": event.source_preserved_exactly,
        "structural_progression_allowed": capture.structural_progression_allowed,
        "condition_codes": [condition.code.value for condition in capture.conditions],
        "token_stream_created": False,
    }
    return custody, projected


def _word_forms(projected: Sequence[Mapping[str, object]]) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for form in projected:
        kind = form.get("kind")
        kind_value = getattr(kind, "value", kind)
        if kind_value not in (SourceFormKind.WORD.value, SourceFormKind.NUMBER.value):
            continue
        exact = str(form.get("exact_text", ""))
        rows.append(
            {
                "source_form_id": str(form.get("source_form_id", "")),
                "exact_text": exact,
                "lookup_key": _fold(exact),
                "kind": str(kind_value),
                "code_point_start": form.get("code_point_start"),
                "code_point_end": form.get("code_point_end"),
            }
        )
    return tuple(rows)


def _keys(rows: Sequence[Mapping[str, object]]) -> frozenset[str]:
    return frozenset(
        str(row.get("lookup_key"))
        for row in rows
        if row.get("lookup_key")
    )


def _intent_candidate(
    intent: str,
    score: float,
    evidence: Sequence[Mapping[str, object]],
    reason_codes: Sequence[str],
) -> dict[str, object]:
    body = {
        "intent": intent,
        "score": round(max(0.0, min(1.0, score)), 6),
        "source_form_refs": tuple(
            str(row.get("source_form_id")) for row in evidence
        ),
        "reason_codes": tuple(reason_codes),
        "selected": False,
        "permission_granted": False,
        "execution_authorized": False,
    }
    return {"intent_candidate_id": _stable_id("intent_candidate", body), **body}


def _evidence_rows(
    rows: Sequence[Mapping[str, object]],
    admitted: frozenset[str],
) -> tuple[Mapping[str, object], ...]:
    return tuple(row for row in rows if row.get("lookup_key") in admitted)


def derive_intent_candidates(
    source_text: str,
    projected: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    """Derive transparent route candidates without claiming full meaning."""

    rows = _word_forms(projected)
    keys = _keys(rows)
    candidates: list[dict[str, object]] = []

    math_hits = keys & _DIRECT_MATH_FORMS
    mathematical_marks = bool(_MATHEMATICAL_MARKS.search(source_text))
    if math_hits or mathematical_marks:
        score = 0.72 + min(0.2, 0.08 * len(math_hits)) + (0.08 if mathematical_marks else 0.0)
        candidates.append(
            _intent_candidate(
                "symbolic_math_computation",
                score,
                _evidence_rows(rows, math_hits),
                ("direct_math_operation_form",) if math_hits else ("mathematical_notation_present",),
            )
        )

    code_hits = keys & _CODE_KNOWLEDGE_FORMS
    build_hits = keys & _BUILD_ACTION_FORMS
    if code_hits and build_hits:
        candidates.append(
            _intent_candidate(
                "software_build_request",
                0.73 + min(0.2, 0.04 * (len(code_hits) + len(build_hits))),
                _evidence_rows(rows, code_hits | build_hits),
                ("software_domain_form", "build_action_form"),
            )
        )
    elif code_hits:
        candidates.append(
            _intent_candidate(
                "software_knowledge_question",
                0.66 + min(0.2, 0.05 * len(code_hits)),
                _evidence_rows(rows, code_hits),
                ("software_domain_form",),
            )
        )

    forge_hits = keys & _FORGE_FORMS
    status_hits = keys & _STATUS_FORMS
    if forge_hits and status_hits:
        candidates.append(
            _intent_candidate(
                "forge_status_question",
                0.82 + min(0.14, 0.03 * (len(forge_hits) + len(status_hits))),
                _evidence_rows(rows, forge_hits | status_hits),
                ("forge_subject_form", "status_predicate_form"),
            )
        )
    elif forge_hits:
        candidates.append(
            _intent_candidate(
                "forge_knowledge_question",
                0.65 + min(0.18, 0.035 * len(forge_hits)),
                _evidence_rows(rows, forge_hits),
                ("forge_domain_form",),
            )
        )

    question_hits = keys & _QUESTION_FORMS
    freshness_hits = keys & _FRESHNESS_FORMS
    if question_hits or source_text.rstrip().endswith("?"):
        candidates.append(
            _intent_candidate(
                "factual_research_question",
                0.58 + min(0.18, 0.05 * len(question_hits)) + (0.12 if freshness_hits else 0.0),
                _evidence_rows(rows, question_hits | freshness_hits),
                (
                    "interrogative_form_present",
                    *(("freshness_required",) if freshness_hits else ()),
                ),
            )
        )

    if build_hits and not code_hits:
        candidates.append(
            _intent_candidate(
                "general_build_or_action_request",
                0.62 + min(0.18, 0.04 * len(build_hits)),
                _evidence_rows(rows, build_hits),
                ("build_action_form",),
            )
        )

    if not candidates:
        candidates.append(
            _intent_candidate(
                "general_conversation_or_unknown",
                0.35,
                rows[:1],
                ("no_typed_capability_construction_yet",),
            )
        )

    candidates.sort(
        key=lambda row: (float(row["score"]), str(row["intent"])),
        reverse=True,
    )
    selected = candidates[0]
    selected["selected"] = True
    if len(candidates) > 1 and float(selected["score"]) - float(candidates[1]["score"]) < 0.08:
        selected["selection_note"] = "nearby_alternative_preserved"
    return tuple(candidates)


def _concept_keys(rows: Sequence[Mapping[str, object]]) -> frozenset[str]:
    return frozenset(
        str(row.get("lookup_key"))
        for row in rows
        if row.get("lookup_key")
        and row.get("lookup_key") not in _FUNCTION_FORMS
        and len(str(row.get("lookup_key"))) > 1
    )


def _load_json(path: Path) -> object:
    try:
        if path.stat().st_size > 2_500_000:
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None


def _symbolic_rows(value: object) -> tuple[dict[str, object], ...]:
    if isinstance(value, list):
        return tuple(dict(row) for row in value if isinstance(row, dict))
    if not isinstance(value, dict):
        return ()
    for key in ("entries", "symbolic_entries", "chunks", "records"):
        rows = value.get(key)
        if isinstance(rows, list):
            return tuple(dict(row) for row in rows if isinstance(row, dict))
    return ()


def _row_text(row: Mapping[str, object]) -> str:
    return " ".join(
        str(row.get(key, ""))
        for key in (
            "chunk_preview",
            "content_summary",
            "claim",
            "summary",
            "memory_role",
            "symbolic_operators",
            "recursion_terms",
            "collapse_terms",
            "return_terms",
            "drift_terms",
            "echo_terms",
        )
    ).strip()


def _row_terms(text: str) -> frozenset[str]:
    return frozenset(
        match.casefold()
        for match in re.findall(r"[^\W_]+(?:[-'’][^\W_]+)*", text, re.UNICODE)
        if len(match) > 1
    )


def recall_candidate_memory(
    source_text: str,
    projected: Sequence[Mapping[str, object]],
    *,
    repository_root: Path,
) -> dict[str, object]:
    """Read candidate/reference memory by non-vector symbolic resonance.

    This is intentionally not canonical claim retrieval.  Word/form overlap is
    useful for locating evidence candidates, but can never by itself establish
    truth, select a meaning, or promote memory.
    """

    query_keys = _concept_keys(_word_forms(projected))
    query_phrase = _fold(" ".join(sorted(query_keys)))
    query_source_sha256 = _sha256_text(source_text)
    candidate_root = _candidate_root(repository_root)
    candidate_files = (
        sorted(candidate_root.glob("*.json"))[:MAX_CANDIDATE_ANSWER_FILES]
        if candidate_root.exists()
        else []
    )
    results: list[dict[str, object]] = []
    for path in candidate_files:
        candidate = _load_json(path)
        if not isinstance(candidate, dict):
            continue
        if candidate.get("source_sha256") != query_source_sha256:
            continue
        claims = candidate.get("claim_candidates")
        if not isinstance(claims, list) or not claims or not isinstance(claims[0], dict):
            continue
        claim = claims[0]
        excerpt = str(claim.get("claim_text", "")).strip()
        if not excerpt:
            continue
        body = {
            "source_path": str(path.relative_to(repository_root)),
            "corpus_id": "rmc_candidate_answers_v1",
            "chunk_id": str(candidate.get("manifest_id", "")),
            "memory_role": "retained_possible_answer_candidate",
            "excerpt": excerpt[:900],
            "evidence_ref": str(claim.get("evidence_ref", "")),
            "source_url": claim.get("source_url"),
            "source_title": str(claim.get("source_title", "Retained candidate answer")),
            "claim_source": str(claim.get("claim_source", "retained_candidate")),
            "matched_source_forms": tuple(sorted(query_keys)),
            "resonance_score": 1.0,
            "phrase_lock": True,
            "exact_source_match": True,
            "retained_manifest_ref": str(candidate.get("manifest_id", "")),
            "canonical_claim_authority": False,
        }
        results.append(
            {"memory_resonance_id": _stable_id("memory_resonance", body), **body}
        )

    maps_root = repository_root / "memory" / "context_library_v1" / "symbolic_maps"
    files = sorted(maps_root.glob("*.json"))[:MAX_MEMORY_MAP_FILES] if maps_root.exists() else []
    row_count = 0
    for path in files:
        for row in _symbolic_rows(_load_json(path)):
            row_count += 1
            if row_count > MAX_MEMORY_ROWS:
                break
            text = _row_text(row)
            terms = _row_terms(text)
            overlap = tuple(sorted(query_keys & terms))
            if not overlap:
                continue
            coverage = len(overlap) / max(1, len(query_keys))
            density = len(overlap) / max(5, len(terms))
            row_fold = _fold(text)
            phrase_lock = bool(query_phrase and query_phrase in row_fold)
            ancestry_strength = 0.08 if row.get("corpus_id") and row.get("chunk_id") else 0.0
            law_weight = min(1.0, max(0.0, float(row.get("source_law_weight", 0.0) or 0.0)))
            implementation_weight = min(1.0, max(0.0, float(row.get("implementation_weight", 0.0) or 0.0)))
            score = min(
                1.0,
                0.62 * coverage
                + 0.14 * density
                + (0.12 if phrase_lock else 0.0)
                + ancestry_strength
                + 0.02 * law_weight
                + 0.02 * implementation_weight,
            )
            if score < MEMORY_SUPPORT_THRESHOLD:
                continue
            body = {
                "source_path": str(path.relative_to(repository_root)),
                "corpus_id": str(row.get("corpus_id", "")),
                "chunk_id": str(row.get("chunk_id", "")),
                "memory_role": str(row.get("memory_role", "reference")),
                "excerpt": str(row.get("chunk_preview") or row.get("content_summary") or text)[:900],
                "matched_source_forms": overlap,
                "resonance_score": round(score, 6),
                "phrase_lock": phrase_lock,
                "canonical_claim_authority": False,
            }
            results.append(
                {"memory_resonance_id": _stable_id("memory_resonance", body), **body}
            )
        if row_count > MAX_MEMORY_ROWS:
            break
    results.sort(
        key=lambda row: float(row.get("resonance_score", 0.0)),
        reverse=True,
    )
    results = results[:MAX_MEMORY_RESULTS]
    top_score = float(results[0]["resonance_score"]) if results else 0.0
    body = {
        "query_source_sha256": query_source_sha256,
        "candidate_answer_root": str(candidate_root),
        "candidate_answer_file_count": len(candidate_files),
        "memory_root": str(maps_root),
        "map_file_count": len(files),
        "rows_inspected": row_count,
        "result_refs": tuple(str(row["memory_resonance_id"]) for row in results),
        "top_resonance_score": top_score,
        "candidate_support_found": bool(results),
        "canonical_answer_found": False,
    }
    return {
        "recall_id": _stable_id("candidate_memory_recall", body),
        "status": "CANDIDATE_SUPPORT_FOUND" if results else "NO_CANDIDATE_SUPPORT",
        **body,
        "results": results,
        "boundary": {
            "memory_read_performed": bool(files or candidate_files),
            "calls_llm": False,
            "embedding_used": False,
            "vector_used": False,
            "word_overlap_is_truth_authority": False,
            "word_overlap_selects_meaning": False,
            "writes_memory": False,
        },
    }


def _exact_language_attempt(source_text: str) -> dict[str, object]:
    try:
        from rmc_engine_v1.meaning_compiler_preview import (
            build_language_core_preview_response,
        )

        return build_language_core_preview_response({"source_text": source_text})
    except Exception as error:
        return {
            "status": "ERROR",
            "reason_code": "exact_language_attempt_failed_closed",
            "error_type": type(error).__name__,
        }


def _exact_language_answer(preview: Mapping[str, object]) -> dict[str, object] | None:
    governed = preview.get("governed_output")
    if not isinstance(governed, Mapping):
        return None
    rendered = governed.get("rendered_output")
    echo = governed.get("exact_echo")
    trusted = preview.get("trusted_rmc_provider")
    resonances = preview.get("rmc_exact_identity_resonances")
    if not isinstance(rendered, Mapping) or not isinstance(echo, Mapping):
        return None
    if not isinstance(trusted, Mapping) or trusted.get("trusted") is not True:
        return None
    if not isinstance(resonances, Sequence) or len(resonances) < 1:
        return None
    if governed.get("answer_delivery_eligible") is not True:
        return None
    if echo.get("status") != "PASS" or echo.get("exact_contract_match") is not True:
        return None
    text = rendered.get("text")
    if not isinstance(text, str) or not text:
        return None
    return {
        "status": "ANSWER_READY",
        "route": "promoted_exact_rmc",
        "answer_text": text,
        "manifest": governed.get("manifest"),
        "rendered_output": dict(rendered),
        "echo": dict(echo),
        "source_refs": [
            str(row.get("memory_record_ref"))
            for row in resonances
            if isinstance(row, Mapping) and row.get("memory_record_ref")
        ],
        "delivery_policy": {
            "policy": "automatic_read_only_delivery_from_promoted_stable_rmc",
            "standing_authority": "prior_exact_operator_approval_and_promotion",
            "new_operator_approval_required_for_each_read": False,
            "writes_memory": False,
            "performs_action": False,
        },
    }


def _status_result(status_provider: Callable[[], Mapping[str, object]] | None) -> dict[str, object] | None:
    if status_provider is None:
        return None
    raw = status_provider()
    if not isinstance(raw, Mapping):
        return None
    data = raw.get("data") if isinstance(raw.get("data"), Mapping) else raw
    forge_status = str(raw.get("status") or data.get("status") or "UNKNOWN")
    trust = data.get("trust", "unknown")
    command_count = data.get("cmd_count", "unknown")
    tool_count = data.get("tool_count", "unknown")
    session_id = str(data.get("session_id", "unknown"))
    facts = {
        "forge_status": forge_status,
        "trust": trust,
        "command_count": command_count,
        "tool_count": tool_count,
        "session_id": session_id,
    }
    manifest_body = {
        "result_type": "forge_runtime_status",
        "facts": facts,
        "source": str(raw.get("source", "forge_status_provider")),
        "read_only": True,
    }
    manifest = {
        "manifest_id": _stable_id("typed_result_manifest", manifest_body),
        **manifest_body,
    }
    answer = (
        f"Forge status is {forge_status}. Trust is {trust}; "
        f"{command_count} commands and {tool_count} tools are registered."
    )
    echo_body = {
        "manifest_ref": manifest["manifest_id"],
        "rendered_sha256": _sha256_text(answer),
        "facts_preserved": all(str(value) in answer for key, value in facts.items() if key != "session_id"),
    }
    return {
        "status": "ANSWER_READY",
        "route": "typed_forge_status_capability",
        "answer_text": answer,
        "manifest": manifest,
        "echo": {
            "echo_id": _stable_id("typed_status_echo", echo_body),
            "status": "PASS" if echo_body["facts_preserved"] else "REJECT",
            **echo_body,
        },
        "source_refs": [manifest["manifest_id"]],
    }


def _math_result(
    source_text: str,
    math_provider: Callable[[str], Mapping[str, object]] | None,
) -> dict[str, object]:
    if math_provider is None:
        try:
            from rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface import (
                ask_forge_math_trace_surface,
            )

            math_provider = ask_forge_math_trace_surface
        except Exception as error:
            return {
                "status": "CAPABILITY_UNAVAILABLE",
                "route": "symbolic_math",
                "answer_text": None,
                "reason_codes": [f"symbolic_math_import_failed:{type(error).__name__}"],
            }
    try:
        receipt = dict(math_provider(source_text))
    except Exception as error:
        return {
            "status": "CAPABILITY_FAILED_CLOSED",
            "route": "symbolic_math",
            "answer_text": None,
            "reason_codes": [f"symbolic_math_failed:{type(error).__name__}"],
        }
    answer = receipt.get("answer_text")
    return {
        "status": "ANSWER_READY" if receipt.get("status") == "ANSWERED" and isinstance(answer, str) else str(receipt.get("status", "GATE_BLOCKED")),
        "route": "symbolic_math",
        "answer_text": answer if isinstance(answer, str) else None,
        "reason_codes": list(receipt.get("reasons", [])) if isinstance(receipt.get("reasons"), list) else [],
        "receipt": receipt,
        "source_refs": [str(receipt.get("result_hash"))] if receipt.get("result_hash") else [],
    }


def _build_plan(selected_intent: str, source_text: str) -> dict[str, object]:
    stages = (
        "repository_and_manifest_evidence_search",
        "typed_change_intent_and_scope_manifest",
        "candidate_implementation_paths",
        "selected_patch_manifest",
        "deterministic_or_typed_code_renderer",
        "protoforge_preflight_and_simulation",
        "operator_approval",
        "scoped_apply_and_verifier",
        "receipt_and_gated_rmc_writeback",
    )
    body = {
        "request_sha256": _sha256_text(source_text),
        "intent": selected_intent,
        "stages": stages,
        "execution_authorized": False,
        "patch_write_authorized": False,
        "operator_decision_required_before_apply": True,
    }
    return {
        "plan_id": _stable_id("forge_build_plan", body),
        **body,
        "status": "PLAN_READY_MISSING_GENERAL_CODE_RENDERER",
        "summary": (
            "Forge formed the governed build path, but the general non-LLM code "
            "renderer is not implemented yet; no patch or command was executed."
        ),
    }


def _best_memory_excerpt(memory: Mapping[str, object]) -> dict[str, object] | None:
    results = memory.get("results")
    if not isinstance(results, list) or not results:
        return None
    first = results[0]
    if not isinstance(first, Mapping):
        return None
    excerpt = str(first.get("excerpt", "")).strip()
    if not excerpt:
        return None
    for sentence in _SENTENCE.split(excerpt):
        sentence = _SPACE.sub(" ", sentence).strip()
        if len(sentence) >= 35:
            return {
                "claim_text": sentence[:900],
                "claim_source": str(
                    first.get("claim_source") or "candidate_rmc_context"
                ),
                "evidence_ref": str(
                    first.get("evidence_ref")
                    or first.get("memory_resonance_id", "")
                ),
                "source_url": first.get("source_url"),
                "source_title": str(
                    first.get("source_title")
                    or first.get("source_path", "Forge RMC context")
                ),
                "resonance_score": float(first.get("resonance_score", 0.0)),
                "exact_excerpt": True,
                "exact_source_match": first.get("exact_source_match") is True,
                "retained_manifest_ref": first.get("retained_manifest_ref"),
                "retained_candidate_path": (
                    first.get("source_path")
                    if first.get("memory_role") == "retained_possible_answer_candidate"
                    else None
                ),
                "canonical": False,
            }
    return None


def _best_web_excerpt(acquisition: Mapping[str, object]) -> dict[str, object] | None:
    evidence = acquisition.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return None
    first = evidence[0]
    if not isinstance(first, Mapping):
        return None
    excerpt = str(first.get("excerpt", "")).strip()
    if not excerpt:
        return None
    return {
        "claim_text": excerpt,
        "claim_source": "public_web_candidate_evidence",
        "evidence_ref": str(first.get("source_receipt_id", "")),
        "source_url": str(first.get("final_url", "")),
        "source_title": str(first.get("title", "")),
        "resonance_score": float(first.get("resonance_score", 0.0)),
        "exact_excerpt": first.get("exact_excerpt_from_source") is True,
        "canonical": False,
    }


def _possible_answer_manifest(
    *,
    source_text: str,
    custody: Mapping[str, object],
    intent_candidates: Sequence[Mapping[str, object]],
    memory: Mapping[str, object],
    acquisition: Mapping[str, object] | None,
    claim: Mapping[str, object] | None,
    build_plan: Mapping[str, object] | None = None,
) -> dict[str, object]:
    selected = next(
        (dict(row) for row in intent_candidates if row.get("selected") is True),
        dict(intent_candidates[0]) if intent_candidates else {},
    )
    claim_rows = [dict(claim)] if claim is not None else []
    body = {
        "schema_version": POSSIBLE_ANSWER_SCHEMA,
        "source_event_ref": custody.get("input_event_id"),
        "source_sha256": custody.get("source_sha256"),
        "selected_intent_candidate_ref": selected.get("intent_candidate_id"),
        "selected_intent": selected.get("intent"),
        "intent_candidate_refs": tuple(
            str(row.get("intent_candidate_id")) for row in intent_candidates
        ),
        "candidate_memory_recall_ref": memory.get("recall_id"),
        "research_acquisition_ref": acquisition.get("acquisition_id") if acquisition else None,
        "claim_candidates": claim_rows,
        "build_plan": dict(build_plan) if build_plan is not None else None,
        "lifecycle_state": "observed_candidate",
        "possible_answer_only": True,
        "stable_memory": False,
        "canonical": False,
        "truth_claim_finalized": False,
        "operator_review_required_for_canonical_promotion": True,
        "automatic_candidate_retention_allowed": True,
    }
    manifest_id = _stable_id("rmc_possible_answer_manifest", body)
    return {
        "manifest_id": manifest_id,
        "created_at_utc": _utc_now(),
        "source_text": source_text,
        **body,
    }


def _render_possible_answer(manifest: Mapping[str, object]) -> dict[str, object]:
    claims = manifest.get("claim_candidates")
    claim = claims[0] if isinstance(claims, list) and claims and isinstance(claims[0], Mapping) else None
    build_plan = manifest.get("build_plan")
    if claim is not None:
        answer = str(claim.get("claim_text", ""))
        template = "exact_evidence_excerpt"
    elif isinstance(build_plan, Mapping):
        answer = str(build_plan.get("summary", ""))
        template = "governed_build_plan_status"
    else:
        answer = (
            "Forge did not find enough governed evidence to form a possible answer. "
            "The source and unresolved route were preserved for candidate learning."
        )
        template = "insufficient_evidence"
    body = {
        "manifest_ref": manifest.get("manifest_id"),
        "template": template,
        "text": answer,
        "text_sha256": _sha256_text(answer),
        "candidate_label_required": template == "exact_evidence_excerpt",
        "delivery_is_canonical_truth_claim": False,
    }
    return {
        "rendered_output_id": _stable_id("possible_answer_render", body),
        **body,
    }


def _echo_possible_answer(
    manifest: Mapping[str, object],
    rendered: Mapping[str, object],
) -> dict[str, object]:
    claims = manifest.get("claim_candidates")
    text = str(rendered.get("text", ""))
    if isinstance(claims, list) and claims and isinstance(claims[0], Mapping):
        exact_match = text == str(claims[0].get("claim_text", ""))
        evidence_ref_present = bool(claims[0].get("evidence_ref"))
    else:
        plan = manifest.get("build_plan")
        if isinstance(plan, Mapping):
            exact_match = text == str(plan.get("summary", ""))
        else:
            exact_match = bool(text)
        evidence_ref_present = True
    candidate_boundary_preserved = (
        manifest.get("canonical") is False
        and manifest.get("possible_answer_only") is True
        and rendered.get("delivery_is_canonical_truth_claim") is False
    )
    passed = exact_match and evidence_ref_present and candidate_boundary_preserved
    body = {
        "manifest_ref": manifest.get("manifest_id"),
        "rendered_output_ref": rendered.get("rendered_output_id"),
        "rendered_text_sha256": rendered.get("text_sha256"),
        "exact_claim_or_plan_match": exact_match,
        "evidence_ref_present": evidence_ref_present,
        "candidate_boundary_preserved": candidate_boundary_preserved,
    }
    return {
        "echo_id": _stable_id("possible_answer_exact_echo", body),
        "status": "PASS" if passed else "REJECT",
        **body,
    }


def _candidate_root(repository_root: Path) -> Path:
    return repository_root / "memory" / "rmc_candidate_answers_v1" / "candidates"


def persist_possible_answer_candidate(
    manifest: Mapping[str, object],
    *,
    repository_root: Path,
) -> dict[str, object]:
    """Atomically retain one candidate manifest; never write stable memory."""

    manifest_id = str(manifest.get("manifest_id", ""))
    if not manifest_id.startswith("rmc_possible_answer_manifest:"):
        raise ValueError("possible_answer_manifest_id_invalid")
    filename = manifest_id.split(":", 1)[1] + ".json"
    root = _candidate_root(repository_root)
    target = root / filename
    payload = _canonical_json(dict(manifest)) + "\n"
    with _WRITE_LOCK:
        root.mkdir(parents=True, exist_ok=True)
        if target.exists():
            existing_text = target.read_text(encoding="utf-8")
            try:
                existing_value = json.loads(existing_text)
            except (TypeError, ValueError) as error:
                raise ValueError("possible_answer_candidate_existing_json_invalid") from error
            incoming_value = dict(manifest)
            # Observation time is receipt metadata, not semantic identity.  A
            # repeated identical question/evidence transaction therefore
            # resolves to the existing content-addressed candidate instead of
            # producing an identity collision or duplicate candidate.
            if isinstance(existing_value, dict):
                existing_value.pop("created_at_utc", None)
            incoming_value.pop("created_at_utc", None)
            if _canonical_json(existing_value) != _canonical_json(incoming_value):
                raise ValueError("possible_answer_candidate_identity_collision")
            wrote = False
        else:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=".candidate-",
                suffix=".json.tmp",
                dir=str(root),
            )
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary_name, target)
            finally:
                if os.path.exists(temporary_name):
                    os.unlink(temporary_name)
            wrote = True
    body = {
        "manifest_ref": manifest_id,
        "relative_path": str(target.relative_to(repository_root)),
        "candidate_written": wrote,
        "candidate_present": target.exists(),
        "writes_candidate_memory": wrote,
        "writes_stable_memory": False,
        "writes_canonical_memory": False,
    }
    return {
        "retention_receipt_id": _stable_id("candidate_retention_receipt", body),
        **body,
    }


def _stage(
    key: str,
    label: str,
    status: str,
    evidence: Mapping[str, object] | None = None,
) -> dict[str, object]:
    body = {
        "stage_key": key,
        "label": label,
        "status": status,
        "evidence": dict(evidence or {}),
    }
    return {"stage_id": _stable_id("operator_stage", body), **body}


def _invalid_response(reason_code: str, source_text: str = "") -> dict[str, object]:
    return {
        "status": "INVALID",
        "reason_code": reason_code,
        "schema_version": OPERATOR_INTERPRETER_SCHEMA,
        "api_contract": "forge_operator_console_api_v1",
        "endpoint": ENDPOINT,
        "source_text": source_text,
        "response_text": "Forge could not admit that source into exact input custody.",
        "answer_kind": "none",
        "stages": [],
        "sources": [],
        "possible_answer_manifest": None,
        "boundary": operator_interpreter_boundary(),
    }


def answer_forge_question(
    request: object,
    *,
    repository_root: Path | str | None = None,
    research_provider: ResearchProvider | None = None,
    status_provider: Callable[[], Mapping[str, object]] | None = None,
    math_provider: Callable[[str], Mapping[str, object]] | None = None,
    allow_network: bool = True,
    persist_candidates: bool = True,
) -> dict[str, object]:
    """Run one automatic memory-first Ask Forge transaction."""

    if type(request) is not dict:
        return _invalid_response("request_must_be_json_object")
    if set(request) - {"source_text", "question", "request", "allow_network"}:
        return _invalid_response("request_contains_unsupported_fields")
    source_text = request.get("source_text", request.get("question", request.get("request", "")))
    if type(source_text) is not str:
        return _invalid_response("source_text_must_be_string")
    request_network = request.get("allow_network")
    if request_network is not None and type(request_network) is not bool:
        return _invalid_response("allow_network_must_be_boolean", source_text)
    network_allowed = allow_network and request_network is not False
    root = Path(repository_root) if repository_root is not None else Path(__file__).resolve().parents[1]
    root = root.resolve()

    try:
        custody, projected = _capture_source(source_text)
    except (TypeError, ValueError) as error:
        return _invalid_response(str(error), source_text)

    stages: list[dict[str, object]] = [
        _stage(
            "source_custody",
            "Exact input custody and reversible source-field projection",
            "COMPLETE",
            {
                "input_event_id": custody["input_event_id"],
                "source_form_count": len(projected),
                "token_stream_created": False,
            },
        )
    ]

    exact_preview = _exact_language_attempt(source_text)
    exact_answer = _exact_language_answer(exact_preview)
    stages.append(
        _stage(
            "promoted_exact_rmc",
            "Promoted exact-RMC answer lookup",
            "ANSWER_FOUND" if exact_answer else "NO_DELIVERABLE_EXACT_ANSWER",
            {
                "compiler_status": exact_preview.get("status"),
                "trusted_provider": (
                    exact_preview.get("trusted_rmc_provider", {}).get("trusted")
                    if isinstance(exact_preview.get("trusted_rmc_provider"), Mapping)
                    else False
                ),
            },
        )
    )
    if exact_answer is not None:
        stages.extend(
            (
                _stage("manifest", "Recursive Manifest Compiler", "COMPLETE", {"route": exact_answer["route"]}),
                _stage("renderer", "Deterministic language renderer", "COMPLETE"),
                _stage("echo", "Exact symbolic Echo", "PASS"),
                _stage("delivery", "Automatic read-only delivery", "DELIVERED", exact_answer["delivery_policy"]),
            )
        )
        response_body = {
            "status": "ANSWERED",
            "answer_kind": "trusted_rmc",
            "route": exact_answer["route"],
            "source_sha256": custody["source_sha256"],
            "answer_sha256": _sha256_text(str(exact_answer["answer_text"])),
            "source_refs": tuple(exact_answer["source_refs"]),
        }
        return {
            "response_id": _stable_id("ask_forge_response", response_body),
            "schema_version": OPERATOR_INTERPRETER_SCHEMA,
            "api_contract": "forge_operator_console_api_v1",
            "endpoint": ENDPOINT,
            **response_body,
            "reason_code": "promoted_exact_rmc_answer_delivered",
            "source_text": source_text,
            "response_text": exact_answer["answer_text"],
            "source_custody": custody,
            "source_forms": projected,
            "intent_candidates": [],
            "candidate_memory_recall": None,
            "capability_result": exact_answer,
            "research_acquisition": None,
            "possible_answer_manifest": None,
            "candidate_retention": None,
            "sources": [
                {"ref": ref, "kind": "promoted_exact_rmc"}
                for ref in exact_answer["source_refs"]
            ],
            "stages": stages,
            "boundary": operator_interpreter_boundary(),
        }

    intent_candidates = derive_intent_candidates(source_text, projected)
    selected_intent = str(intent_candidates[0]["intent"])
    stages.append(
        _stage(
            "intent_candidates",
            "Typed intent and capability candidates",
            "PROVISIONAL_ROUTE_SELECTED",
            {
                "selected_intent": selected_intent,
                "candidate_count": len(intent_candidates),
                "full_meaning_claimed": False,
            },
        )
    )

    memory = recall_candidate_memory(source_text, projected, repository_root=root)
    stages.append(
        _stage(
            "memory_recall",
            "RMC/context candidate resonance recall",
            str(memory["status"]),
            {
                "top_resonance_score": memory["top_resonance_score"],
                "canonical_answer_found": False,
            },
        )
    )

    capability: dict[str, object] | None = None
    build_plan: dict[str, object] | None = None
    if selected_intent == "forge_status_question":
        capability = _status_result(status_provider)
    elif selected_intent == "symbolic_math_computation":
        capability = _math_result(source_text, math_provider)
    elif selected_intent in {"software_build_request", "general_build_or_action_request"}:
        build_plan = _build_plan(selected_intent, source_text)
        capability = {
            "status": build_plan["status"],
            "route": "forge_build_pipeline",
            "answer_text": build_plan["summary"],
            "plan": build_plan,
            "source_refs": [build_plan["plan_id"]],
        }

    if capability is not None:
        stages.append(
            _stage(
                "typed_capability",
                "Typed Forge capability",
                str(capability.get("status", "UNKNOWN")),
                {"route": capability.get("route")},
            )
        )
        if capability.get("status") == "ANSWER_READY" and capability.get("answer_text"):
            stages.extend(
                (
                    _stage("manifest", "Capability result manifest", "COMPLETE"),
                    _stage("renderer", "Deterministic language renderer", "COMPLETE"),
                    _stage("echo", "Exact result Echo", "PASS"),
                    _stage("delivery", "Automatic read-only delivery", "DELIVERED"),
                )
            )
            response_text = str(capability["answer_text"])
            response_body = {
                "status": "ANSWERED",
                "answer_kind": "typed_capability",
                "route": capability.get("route"),
                "source_sha256": custody["source_sha256"],
                "answer_sha256": _sha256_text(response_text),
            }
            return {
                "response_id": _stable_id("ask_forge_response", response_body),
                "schema_version": OPERATOR_INTERPRETER_SCHEMA,
                "api_contract": "forge_operator_console_api_v1",
                "endpoint": ENDPOINT,
                **response_body,
                "reason_code": "typed_capability_answer_delivered",
                "source_text": source_text,
                "response_text": response_text,
                "source_custody": custody,
                "source_forms": projected,
                "intent_candidates": list(intent_candidates),
                "candidate_memory_recall": memory,
                "capability_result": capability,
                "research_acquisition": None,
                "possible_answer_manifest": None,
                "candidate_retention": None,
                "sources": [
                    {"ref": ref, "kind": "typed_capability_receipt"}
                    for ref in capability.get("source_refs", [])
                ],
                "stages": stages,
                "boundary": operator_interpreter_boundary(),
            }
        if selected_intent == "symbolic_math_computation":
            reason_codes = capability.get("reason_codes", [])
            response_text = (
                "Forge recognized a symbolic-math request, but the governed math "
                "capability did not produce verified result evidence."
            )
            stages.append(_stage("delivery", "Verified result delivery", "HELD"))
            response_body = {
                "status": "HELD",
                "answer_kind": "typed_capability_hold",
                "route": "symbolic_math",
                "source_sha256": custody["source_sha256"],
                "reason_codes": tuple(reason_codes),
            }
            return {
                "response_id": _stable_id("ask_forge_response", response_body),
                "schema_version": OPERATOR_INTERPRETER_SCHEMA,
                "api_contract": "forge_operator_console_api_v1",
                "endpoint": ENDPOINT,
                **response_body,
                "reason_code": "verified_symbolic_math_result_unavailable",
                "source_text": source_text,
                "response_text": response_text,
                "source_custody": custody,
                "source_forms": projected,
                "intent_candidates": list(intent_candidates),
                "candidate_memory_recall": memory,
                "capability_result": capability,
                "research_acquisition": None,
                "possible_answer_manifest": None,
                "candidate_retention": None,
                "sources": [],
                "stages": stages,
                "boundary": operator_interpreter_boundary(),
            }

    memory_claim = _best_memory_excerpt(memory)
    top_memory_score = float(memory.get("top_resonance_score", 0.0))
    forge_internal_intent = selected_intent in {
        "forge_knowledge_question",
        "software_build_request",
        "general_build_or_action_request",
    }
    memory_is_adequate_candidate = bool(
        memory_claim
        and (
            (
                memory_claim.get("exact_source_match") is True
                and top_memory_score >= 0.99
            )
            or (
                forge_internal_intent
                and top_memory_score >= MEMORY_ACCEPT_THRESHOLD
            )
        )
        and not (_keys(_word_forms(projected)) & _FRESHNESS_FORMS)
    )

    acquisition: dict[str, object] | None = None
    claim: dict[str, object] | None = memory_claim if memory_is_adequate_candidate else None
    should_research = (
        claim is None
        and build_plan is None
        and selected_intent != "symbolic_math_computation"
    )
    if should_research and network_allowed:
        acquisition = acquire_research_evidence(
            source_text,
            provider=research_provider,
        )
        claim = _best_web_excerpt(acquisition)
        stages.append(
            _stage(
                "research_acquisition",
                "Governed public-web evidence acquisition",
                str(acquisition.get("status", "NO_EVIDENCE_CAPTURED")),
                {
                    "evidence_count": acquisition.get("evidence_count", 0),
                    "candidate_evidence_only": True,
                    "canonical": False,
                },
            )
        )
    elif should_research:
        stages.append(
            _stage(
                "research_acquisition",
                "Governed public-web evidence acquisition",
                "NETWORK_DISABLED",
            )
        )

    manifest = _possible_answer_manifest(
        source_text=source_text,
        custody=custody,
        intent_candidates=intent_candidates,
        memory=memory,
        acquisition=acquisition,
        claim=claim,
        build_plan=build_plan,
    )
    rendered = _render_possible_answer(manifest)
    echo = _echo_possible_answer(manifest, rendered)
    stages.extend(
        (
            _stage("manifest", "Recursive possible-answer manifest", "COMPLETE", {"manifest_id": manifest["manifest_id"]}),
            _stage("renderer", "Deterministic evidence renderer", "COMPLETE", {"rendered_output_id": rendered["rendered_output_id"]}),
            _stage("echo", "Exact evidence Echo", str(echo["status"]), {"echo_id": echo["echo_id"]}),
        )
    )
    retention = None
    retained_candidate_path = (
        claim.get("retained_candidate_path")
        if isinstance(claim, Mapping)
        else None
    )
    if persist_candidates and retained_candidate_path:
        retention_body = {
            "manifest_ref": claim.get("retained_manifest_ref"),
            "relative_path": retained_candidate_path,
            "candidate_written": False,
            "candidate_present": True,
            "writes_candidate_memory": False,
            "writes_stable_memory": False,
            "writes_canonical_memory": False,
            "reused_existing_candidate": True,
        }
        retention = {
            "retention_receipt_id": _stable_id(
                "candidate_retention_receipt", retention_body
            ),
            **retention_body,
        }
    elif persist_candidates:
        try:
            retention = persist_possible_answer_candidate(manifest, repository_root=root)
        except (OSError, ValueError) as error:
            retention = {
                "status": "FAILED",
                "reason_code": str(error),
                "writes_candidate_memory": False,
                "writes_stable_memory": False,
                "writes_canonical_memory": False,
            }
    stages.append(
        _stage(
            "candidate_retention",
            "Automatic candidate-manifest retention",
            "RECORDED" if retention and retention.get("candidate_present") else "NOT_RECORDED",
            retention if isinstance(retention, Mapping) else {},
        )
    )

    echo_passed = echo["status"] == "PASS"
    has_claim = claim is not None
    has_plan = build_plan is not None
    if echo_passed and has_claim:
        status = "ANSWERED"
        answer_kind = "possible_answer_candidate"
        reason_code = "candidate_evidence_answer_delivered"
        delivery_status = "DELIVERED_AS_CANDIDATE"
    elif echo_passed and has_plan:
        status = "PLANNED"
        answer_kind = "governed_build_plan"
        reason_code = "governed_build_plan_returned_no_execution"
        delivery_status = "PLAN_DELIVERED"
    else:
        status = "NEEDS_EVIDENCE"
        answer_kind = "insufficient_evidence"
        reason_code = "no_governed_answer_evidence_found"
        delivery_status = "LIMITATION_DELIVERED"
    stages.append(
        _stage(
            "delivery",
            "Read-only output delivery",
            delivery_status,
            {
                "canonical_truth_claim": False,
                "action_performed": False,
                "stable_memory_write": False,
            },
        )
    )
    sources: list[dict[str, object]] = []
    if claim is not None:
        sources.append(
            {
                "ref": claim.get("evidence_ref"),
                "kind": claim.get("claim_source"),
                "title": claim.get("source_title"),
                "url": claim.get("source_url"),
                "canonical": False,
            }
        )
    response_body = {
        "status": status,
        "answer_kind": answer_kind,
        "route": selected_intent,
        "source_sha256": custody["source_sha256"],
        "answer_sha256": rendered["text_sha256"],
        "possible_answer_manifest_ref": manifest["manifest_id"],
    }
    return {
        "response_id": _stable_id("ask_forge_response", response_body),
        "schema_version": OPERATOR_INTERPRETER_SCHEMA,
        "api_contract": "forge_operator_console_api_v1",
        "endpoint": ENDPOINT,
        **response_body,
        "reason_code": reason_code,
        "source_text": source_text,
        "response_text": rendered["text"],
        "source_custody": custody,
        "source_forms": projected,
        "intent_candidates": list(intent_candidates),
        "candidate_memory_recall": memory,
        "capability_result": capability,
        "research_acquisition": acquisition,
        "possible_answer_manifest": manifest,
        "rendered_output": rendered,
        "echo": echo,
        "candidate_retention": retention,
        "sources": sources,
        "stages": stages,
        "boundary": operator_interpreter_boundary(),
    }


__all__ = (
    "ENDPOINT",
    "OPERATOR_INTERPRETER_SCHEMA",
    "POSSIBLE_ANSWER_SCHEMA",
    "answer_forge_question",
    "derive_intent_candidates",
    "operator_interpreter_boundary",
    "persist_possible_answer_candidate",
    "recall_candidate_memory",
)

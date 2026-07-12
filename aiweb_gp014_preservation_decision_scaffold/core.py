from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Tuple

SCHEMA_VERSION = "aiweb-gp014-preservation-decision-scaffold-v1"
SCOPE_STATUS = "gp014_preservation_wrapper_decision_boundary_scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"
BASE_HEAD = "cf2d5dc94113a857d0ffd53dd4710534df1aa55e"
BASE_PARENT = "3b640f380b8633ce93143d178dcbee143503f03d"
SOURCE_AUTHORITY_PACKET_SHA256 = "2703699eeab34ac5340cc2e69416a8c05b851c9090ea023559e57f1c78e11cc5"
GP014_IDENTITY = "LANG-EXPR-001 / GP-014"
GP014_STATUS = "preserved_protected_unsuperseded"
GP014_RELATIONSHIP = "referenced_only"
GP014_WRAPPER_DECISION = "no_wrapper_at_slice18"
GP014_IMPORT_DECISION = "no_import"
GP014_CALL_DECISION = "no_call"
GP014_MODIFICATION_DECISION = "no_modification"
GP014_SUPERSESSION_DECISION = "no_supersession"
GP014_PROMOTION_DECISION = "no_promotion"
GP015_STATUS = "failed_not_repaired"
SLICE17_STATUS = "expression_boundary_not_gp014_wrapper"

GP014_PROTECTED_PATH_HASHES: Tuple[Tuple[str, str], ...] = (
    (
        "rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py",
        "431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473",
    ),
    (
        "rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py",
        "f1f2486504bb987d705efee70d775c1549d3597f5153d30e87cbf11f38bedf1a",
    ),
    (
        "rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json",
        "e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e",
    ),
    (
        "scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py",
        "d047b3ca07c13e4e29ab55f9aa8fb357ee87a1a7d649ea2b23f68f30b75af3be",
    ),
    (
        "scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py",
        "c84800156011727cd49f743b722502c60f555c109859ff79aa399cb32ae4d797",
    ),
)

GP015_PROTECTED_PATH_HASHES: Tuple[Tuple[str, str], ...] = (
    (
        "rmc_engine_v1/general_pipeline/gp015_ask_forge_trace_surface.py",
        "9449cdac60047d6d9dd4522e0d4128b72dd86485db225c21203dfd234ba53453",
    ),
)

RELATED_RENDERER_EVIDENCE_PATHS: Tuple[str, ...] = (
    "rmc_engine_v1/renderer/__init__.py",
    "rmc_engine_v1/renderer/mea_render_gate.py",
    "rmc_engine_v1/renderer/semantic_lexicon.py",
    "rmc_engine_v1/renderer/grammar_templates.py",
    "rmc_engine_v1/renderer/surface_realizer.py",
    "rmc_engine_v1/renderer/renderer.py",
    "rmc_engine_v1/renderer/echo_validator.py",
)

REQUIRED_DECISION_LAWS: Tuple[str, ...] = (
    "gp014_is_not_general_language",
    "gp014_is_not_concept_authority",
    "gp014_is_not_predicate_authority",
    "gp014_is_not_source_authority",
    "gp014_is_not_selected_meaning_authority",
    "gp014_is_not_full_rmc_authority",
    "gp014_is_not_renderer_authority",
    "gp014_is_not_delivery_authority",
    "gp014_is_not_echo_authority",
    "gp014_is_not_output_approval",
    "gp014_is_not_production_integration",
    "gp014_is_not_superseded_without_future_formal_supersession_path",
    "gp014_must_not_be_imported_by_slice18",
    "gp014_must_not_be_called_by_slice18",
    "gp014_must_not_be_wrapped_by_slice18",
    "gp014_must_not_broaden_slice17_expression_boundary",
    "gp014_must_remain_byte_protected_during_slice18",
)

FALSE_ONLY_AUTHORITY_FIELDS: Tuple[str, ...] = (
    "general_language_authority",
    "concept_authority",
    "predicate_authority",
    "source_authority",
    "selected_meaning_authority",
    "full_rmc_authority",
    "renderer_authority",
    "output_approval",
    "delivery_authority",
    "execution_authority",
    "runtime_authority",
    "echo_authority",
    "production_authority",
    "route_authority",
    "ui_authority",
    "memory_authority",
    "corpus_authority",
    "external_truth_authority",
    "model_authority",
    "vector_authority",
    "retrieval_authority",
    "training_authority",
    "gp014_modification",
    "gp014_import",
    "gp014_call",
    "gp014_wrapper_created",
    "gp014_supersession",
    "gp014_promotion",
    "gp015_repair",
    "release_authority",
)

REJECTED_GP014_ACTIONS: Tuple[str, ...] = (
    "wrap_gp014_at_slice18",
    "import_gp014_at_slice18",
    "call_gp014_at_slice18",
    "modify_gp014_at_slice18",
    "supersede_gp014_at_slice18",
    "promote_gp014_to_general_language_authority",
    "promote_gp014_to_concept_authority",
    "promote_gp014_to_predicate_authority",
    "promote_gp014_to_source_authority",
    "promote_gp014_to_selected_meaning_authority",
    "promote_gp014_to_full_rmc_authority",
    "promote_gp014_to_renderer_authority",
    "promote_gp014_to_delivery_authority",
    "promote_gp014_to_runtime_authority",
    "repair_gp015_as_part_of_slice18",
)

FORBIDDEN_IMPORT_ROOTS: Tuple[str, ...] = (
    "openai",
    "anthropic",
    "chromadb",
    "langchain",
    "faiss",
    "sklearn",
    "sentence_transformers",
    "transformers",
    "torch",
    "tensorflow",
    "requests",
    "httpx",
    "urllib",
    "socket",
    "sqlite3",
    "ollama",
    "llama_cpp",
)

FORBIDDEN_IMPORT_PREFIXES: Tuple[str, ...] = (
    "rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer",
    "rmc_engine_v1.general_pipeline.symbolic_math_operator_language_realizer",
    "rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface",
    "rmc_engine_v1.renderer",
    "rmc_engine_v1.llm_renderer",
    "rmc_engine_v1.chroma_connector",
    "aiweb_output_expression_boundary_scaffold",
)


@dataclass(frozen=True)
class ValidationIssue:
    field: str
    reason: str
    severity: str = "error"


@dataclass(frozen=True)
class ValidationReport:
    schema_version: str
    ok: bool
    issues: Tuple[ValidationIssue, ...] = ()


def issue(field: str, reason: str, severity: str = "error") -> ValidationIssue:
    return ValidationIssue(field=field, reason=reason, severity=severity)


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, tuple):
        return [_canonicalize(item) for item in value]
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(_canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_decision_id(prefix: str, *parts: Any) -> str:
    body = {"prefix": prefix, "parts": [_canonicalize(part) for part in parts]}
    digest = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def sha256_file(path: str | Path) -> str:
    target = Path(path)
    h = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def tuple_of_text(value: object, *, allow_empty: bool = False) -> bool:
    if not isinstance(value, tuple):
        return False
    if not allow_empty and not value:
        return False
    return all(nonempty_text(item) for item in value)


def tuple_of_path_hashes(value: object, *, allow_empty: bool = False) -> bool:
    if not isinstance(value, tuple):
        return False
    if not allow_empty and not value:
        return False
    for item in value:
        if not isinstance(item, tuple) or len(item) != 2:
            return False
        path, digest = item
        if not nonempty_text(path) or not isinstance(digest, str):
            return False
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            return False
    return True


def unique_tuple(value: Tuple[str, ...]) -> bool:
    return len(set(value)) == len(value)


def check_false_only(record: object, fields: Tuple[str, ...], issues: list[ValidationIssue]) -> None:
    for field in fields:
        if getattr(record, field, None) is not False:
            issues.append(issue(field, "must_be_false_boundary_field"))


def authority_false_defaults() -> dict[str, bool]:
    return {field: False for field in FALSE_ONLY_AUTHORITY_FIELDS}


def gp014_decision_scope_record() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "scope_status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "base_head": BASE_HEAD,
        "base_parent": BASE_PARENT,
        "source_authority_packet_sha256": SOURCE_AUTHORITY_PACKET_SHA256,
        "gp014_identity": GP014_IDENTITY,
        "gp014_status": GP014_STATUS,
        "gp014_relationship": GP014_RELATIONSHIP,
        "gp014_wrapper_decision": GP014_WRAPPER_DECISION,
        "gp014_import_decision": GP014_IMPORT_DECISION,
        "gp014_call_decision": GP014_CALL_DECISION,
        "gp014_modification_decision": GP014_MODIFICATION_DECISION,
        "gp014_supersession_decision": GP014_SUPERSESSION_DECISION,
        "gp014_promotion_decision": GP014_PROMOTION_DECISION,
        "gp015_status": GP015_STATUS,
        "slice17_status": SLICE17_STATUS,
        "required_decision_laws": REQUIRED_DECISION_LAWS,
        "rejected_gp014_actions": REJECTED_GP014_ACTIONS,
        "gp014_protected_path_hashes": GP014_PROTECTED_PATH_HASHES,
        "gp015_protected_path_hashes": GP015_PROTECTED_PATH_HASHES,
        "related_renderer_evidence_paths": RELATED_RENDERER_EVIDENCE_PATHS,
    }
    record.update(authority_false_defaults())
    return record

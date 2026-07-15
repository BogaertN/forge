"""Static legacy and separate-domain isolation catalog for Slice 36B0.

This module contains names only. It does not import, inspect, call, or probe any
listed surface.
"""

from __future__ import annotations

from ..schema import stable_record_id
from .schema import (
    CONTRACT_SCHEMA_VERSION,
    CONTRACT_SPEC_ID,
    CONTRACT_SPEC_VERSION,
    LEGACY_ISOLATION_SCHEMA_ID,
    LegacyIsolationCatalog,
    LegacyIsolationRecord,
    LegacySurfaceCategory,
    LegacySurfaceDisposition,
)


_SURFACES = (
    (
        "rmc_engine_v1.phase_parser",
        LegacySurfaceCategory.WITHDRAWN_LEGACY_LANGUAGE,
        LegacySurfaceDisposition.ISOLATED_NO_IMPORT_OR_CALL,
        "legacy_keyword_phase_parser_not_language_authority",
        False,
    ),
    (
        "rmc_engine_v1.resonance_lexicon",
        LegacySurfaceCategory.WITHDRAWN_LEGACY_LANGUAGE,
        LegacySurfaceDisposition.ISOLATED_NO_IMPORT_OR_CALL,
        "legacy_normalizing_weighted_lexicon_not_language_authority",
        False,
    ),
    (
        "rmc_engine_v1.candidate_generator",
        LegacySurfaceCategory.WITHDRAWN_LEGACY_LANGUAGE,
        LegacySurfaceDisposition.ISOLATED_NO_IMPORT_OR_CALL,
        "legacy_candidate_generator_not_language_authority",
        False,
    ),
    (
        "rmc_engine_v1.manifest_compiler",
        LegacySurfaceCategory.WITHDRAWN_LEGACY_LANGUAGE,
        LegacySurfaceDisposition.ISOLATED_NO_IMPORT_OR_CALL,
        "legacy_manifest_compiler_not_new_language_authority",
        False,
    ),
    (
        "rmc_engine_v1.rmc_pipeline",
        LegacySurfaceCategory.WITHDRAWN_LEGACY_LANGUAGE,
        LegacySurfaceDisposition.ISOLATED_NO_IMPORT_OR_CALL,
        "legacy_pipeline_not_new_language_authority",
        False,
    ),
    (
        "rmc_engine_v1.llm_renderer",
        LegacySurfaceCategory.PROHIBITED_DEPENDENCY,
        LegacySurfaceDisposition.PROHIBITED_NO_IMPORT_OR_CALL,
        "llm_dependency_prohibited_from_language_core",
        False,
    ),
    (
        "rmc_engine_v1.chroma_connector",
        LegacySurfaceCategory.PROHIBITED_DEPENDENCY,
        LegacySurfaceDisposition.PROHIBITED_NO_IMPORT_OR_CALL,
        "vector_retrieval_dependency_prohibited_from_language_core",
        False,
    ),
    (
        "rmc_engine_v1.mea.operator_engine",
        LegacySurfaceCategory.SEPARATE_DOMAIN_NOT_LANGUAGE_AUTHORITY,
        LegacySurfaceDisposition.SEPARATE_DOMAIN_NO_SUBSTITUTION,
        "mea_problem_manifest_operator_engine_cannot_substitute_for_language_operator_kernel",
        True,
    ),
    (
        "rmc_engine_v1.mea.operator_registry",
        LegacySurfaceCategory.SEPARATE_DOMAIN_NOT_LANGUAGE_AUTHORITY,
        LegacySurfaceDisposition.SEPARATE_DOMAIN_NO_SUBSTITUTION,
        "mea_problem_manifest_registry_cannot_substitute_for_language_operator_registry",
        True,
    ),
    (
        "rmc_engine_v1.mea.fbsc_operator_crosswalk",
        LegacySurfaceCategory.SEPARATE_DOMAIN_NOT_LANGUAGE_AUTHORITY,
        LegacySurfaceDisposition.SEPARATE_DOMAIN_NO_SUBSTITUTION,
        "mea_crosswalk_is_not_language_operator_execution_authority",
        True,
    ),
    (
        "rmc_engine_v1.phase_codex",
        LegacySurfaceCategory.REFERENCE_ONLY_NOT_RUNTIME_AUTHORITY,
        LegacySurfaceDisposition.STATIC_REFERENCE_ONLY,
        "legacy_phase_codex_requires_later_re_admission_before_use",
        True,
    ),
    (
        "rmc_engine_v1.reference.operator_phrase_lexicon_v1.jsonl",
        LegacySurfaceCategory.REFERENCE_ONLY_NOT_RUNTIME_AUTHORITY,
        LegacySurfaceDisposition.STATIC_REFERENCE_ONLY,
        "phrase_lexicon_is_not_operator_binding_authority",
        True,
    ),
    (
        "rmc_engine_v1.reference.word_loop_seed_lexicon_v1.jsonl",
        LegacySurfaceCategory.REFERENCE_ONLY_NOT_RUNTIME_AUTHORITY,
        LegacySurfaceDisposition.STATIC_REFERENCE_ONLY,
        "word_loop_lexicon_is_not_source_field_or_meaning_authority",
        True,
    ),
    (
        "rmc_engine_v1.reference.letter_phase_map_v1.json",
        LegacySurfaceCategory.REFERENCE_ONLY_NOT_RUNTIME_AUTHORITY,
        LegacySurfaceDisposition.STATIC_REFERENCE_ONLY,
        "letter_phase_map_is_not_phase_assignment_authority",
        True,
    ),
)


def _record(
    *,
    surface_path: str,
    category: LegacySurfaceCategory,
    disposition: LegacySurfaceDisposition,
    reason_code: str,
    static_reference_allowed: bool,
) -> LegacyIsolationRecord:
    body = {
        "surface_path": surface_path,
        "category": category,
        "disposition": disposition,
        "reason_code": reason_code,
        "static_reference_allowed": static_reference_allowed,
        "import_allowed": False,
        "call_allowed": False,
        "language_authority_allowed": False,
        "semantic_authority_allowed": False,
        "runtime_substitution_allowed": False,
        "contract_spec_id": CONTRACT_SPEC_ID,
        "contract_spec_version": CONTRACT_SPEC_VERSION,
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "isolation_schema_id": LEGACY_ISOLATION_SCHEMA_ID,
    }
    return LegacyIsolationRecord(
        isolation_id=stable_record_id("legacy_operator_isolation", body),
        **body,
    )


def build_default_legacy_isolation_catalog() -> LegacyIsolationCatalog:
    records = tuple(
        _record(
            surface_path=row[0],
            category=row[1],
            disposition=row[2],
            reason_code=row[3],
            static_reference_allowed=row[4],
        )
        for row in _SURFACES
    )
    body = {
        "records": records,
        "legacy_imports_allowed": False,
        "legacy_calls_allowed": False,
        "legacy_language_authority_allowed": False,
        "mea_substitution_allowed": False,
        "static_reference_only": True,
        "contract_spec_id": CONTRACT_SPEC_ID,
        "contract_spec_version": CONTRACT_SPEC_VERSION,
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "isolation_schema_id": LEGACY_ISOLATION_SCHEMA_ID,
    }
    return LegacyIsolationCatalog(
        catalog_id=stable_record_id("legacy_operator_isolation_catalog", body),
        **body,
    )


def isolation_record_for_surface(
    surface_path: object,
    catalog: LegacyIsolationCatalog | None = None,
) -> LegacyIsolationRecord | None:
    if type(surface_path) is not str:
        return None
    selected = catalog or build_default_legacy_isolation_catalog()
    return next(
        (item for item in selected.records if item.surface_path == surface_path),
        None,
    )

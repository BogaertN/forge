"""Binding authority for Slice 47 GP-014 status decision and Phase D closeout."""
from __future__ import annotations
from typing import Final

SLICE47_SCHEMA_VERSION: Final[str] = "aiweb-slice47-gp014-status-decision-v1"
SLICE47_SPEC_ID: Final[str] = "canonical-roadmap:slice47"
SLICE47_SPEC_VERSION: Final[str] = "v1.0.0"
SLICE47_COMMIT_SUBJECT: Final[str] = 'Slice 47 GP-014 status decision and Phase D closeout'

ACCEPTED_PARENT_HEAD: Final[str] = '0af2e034f061dfdbb86868090a6db2424131b999'
ACCEPTED_PARENT_PARENT: Final[str] = '00df51e4b2fe14e437291c5228159820dd1cf139'
ACCEPTED_PARENT_TREE: Final[str] = 'f7dd3b4ec061f28f8076d62b06e49f8cead32938'
ACCEPTED_PARENT_SUBJECT: Final[str] = 'Slice 46 GP-014 equivalence and regression proof'

SOURCE_AUTHORITY_PACKET_SHA256: Final[str] = 'a72b79f05aee69ed5c49e26f2b373756ee2a482ec498ff610e597f96c0f983d8'
SLICE44_SOURCE_AUTHORITY_PACKET_SHA256: Final[str] = 'd753137824f30b608729113d0d0d31cd2e80ed124eb2f9e2f8f956c431f8dcac'
SLICE46_ACCEPTANCE_ARCHIVE_SHA256: Final[str] = 'c0e5c8e4a782745c1000b787a4dbfc05697337b25eb8348afbc5a5b844d66ebf'

SLICE18_COMMIT: Final[str] = "7046051567b5d82c98811f64b2413e746da70a97"
SLICE45_COMMIT: Final[str] = "00df51e4b2fe14e437291c5228159820dd1cf139"
SLICE46_COMMIT: Final[str] = ACCEPTED_PARENT_HEAD

LAWFUL_STATUS_OUTCOMES: Final[tuple[str, ...]] = (
    "preserved_as_unchanged_bounded_lane",
    "wrapped_behind_general_interface",
    "refactored_under_equivalence_proof",
    "replaced_under_full_dedicated_proof",
    "superseded_under_dedicated_supersession_cycle",
)
SELECTED_STATUS_OUTCOME: Final[str] = "preserved_as_unchanged_bounded_lane"
REJECTED_STATUS_OUTCOMES: Final[tuple[str, ...]] = tuple(
    value for value in LAWFUL_STATUS_OUTCOMES if value != SELECTED_STATUS_OUTCOME
)

GP014_BUILD_ID: Final[str] = "LANG-EXPR-001-GP-014-RMC-OPERATOR-GUIDED-GENERATIVE-LANGUAGE-REALIZER"
GP014_STATUS: Final[str] = "protected_unchanged_bounded_lane_unsuperseded"
ADAPTER_STATUS: Final[str] = "separate_disabled_unregistered_bounded_adapter"
EQUIVALENCE_STATUS: Final[str] = "accepted_within_slice46_scope"
PHASE_D_STATUS: Final[str] = "complete_with_gp014_preserved"
NEXT_LAWFUL_SLICE: Final[str] = "Slice 48 — Local Runtime Service Boundary"

GP014_PROTECTED_SOURCE: Final[tuple[tuple[str, str], ...]] = (
    ("rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py", "431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473"),
    ("rmc_engine_v1/general_pipeline/symbolic_math_language_vertical_slice.py", "protected_by_slice46_predecessor_manifest"),
    ("rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py", "protected_by_slice46_predecessor_manifest"),
    ("rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json", "e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e"),
)

PHASE_D_SLICES: Final[tuple[str, ...]] = (
    "Slice 44 — GP-014 source and regression authority packet",
    "Slice 45 — bounded GP-014 adapter boundary",
    "Slice 46 — GP-014 equivalence and regression proof",
    "Slice 47 — GP-014 status decision",
)

FUTURE_CHANGE_REQUIRES: Final[tuple[str, ...]] = (
    "fresh_exact_source_authority_packet",
    "explicit_decision_owner_authorization",
    "dedicated_behavior_and_inherited_acceptance",
    "protected_predecessor_hash_verification",
    "rollback_and_recovery_proof",
    "returned_real_repository_evidence_before_staging_or_commit",
)
SUPERSESSION_REQUIRES: Final[tuple[str, ...]] = (
    "separate_dedicated_supersession_cycle",
    "full_dedicated_supersession_proof",
    "explicit_supersession_acceptance",
)

PROHIBITED_AUTHORITY_FIELDS: Final[tuple[str, ...]] = (
    "gp014_modified", "gp014_refactored", "gp014_replaced", "gp014_superseded",
    "gp015_used", "general_language_authority", "concept_authority",
    "predicate_authority", "selected_meaning_authority", "truth_authority",
    "evidence_authority", "permission_authority", "route_authority",
    "api_authority", "ui_authority", "network_authority",
    "filesystem_write_authority", "memory_authority", "resource_authority",
    "tool_authority", "action_authority", "delivery_authority",
    "release_authority", "production_authority",
)

__all__ = tuple(name for name in globals() if not name.startswith("_"))

"""Authority separation record for Slice 21.

Read-only inspection may make already-governed records visible for review.
It must never become acceptance, runtime authority, proof, delivery,
tool routing, memory authority, external-resource admission, or UI authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Final

_AUTHORITY_LAYERS: Final[tuple[str, ...]] = (
    "record_custody_layer",
    "inspection_visibility_layer",
    "runtime_authority_layer",
    "acceptance_authority_layer",
    "delivery_action_tool_layer",
    "memory_authority_layer",
    "ui_evidence_view_layer",
)

_DENIED_COLLAPSES: Final[tuple[tuple[str, str], ...]] = (
    ("inspection_visibility_layer", "runtime_authority_layer"),
    ("inspection_visibility_layer", "acceptance_authority_layer"),
    ("inspection_visibility_layer", "delivery_action_tool_layer"),
    ("inspection_visibility_layer", "memory_authority_layer"),
    ("inspection_visibility_layer", "ui_evidence_view_layer_as_proof"),
    ("api_availability", "acceptance_authority_layer"),
    ("ui_visibility", "proof_authority"),
)


@dataclass(frozen=True, slots=True)
class AuthoritySeparationRecord:
    authority_layers: tuple[str, ...]
    denied_collapses: tuple[tuple[str, str], ...]
    read_only_inspection_required: bool
    mutation_forbidden: bool
    acceptance_creation_forbidden: bool
    accepted_scope_widening_forbidden: bool
    candidate_promotion_forbidden: bool
    memory_write_forbidden: bool
    tool_routing_forbidden: bool
    tool_invocation_forbidden: bool
    delivery_forbidden: bool
    action_execution_forbidden: bool
    external_resource_admission_forbidden: bool
    model_vector_retrieval_rag_authority_forbidden: bool
    ui_authority_forbidden: bool
    this_scaffold_grants_runtime_authority: bool
    this_scaffold_grants_acceptance_authority: bool
    this_scaffold_grants_permission: bool
    this_scaffold_registers_routes: bool
    this_scaffold_modifies_config: bool
    this_scaffold_integrates_ui: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_authority_separation_record() -> AuthoritySeparationRecord:
    return AuthoritySeparationRecord(
        authority_layers=_AUTHORITY_LAYERS,
        denied_collapses=_DENIED_COLLAPSES,
        read_only_inspection_required=True,
        mutation_forbidden=True,
        acceptance_creation_forbidden=True,
        accepted_scope_widening_forbidden=True,
        candidate_promotion_forbidden=True,
        memory_write_forbidden=True,
        tool_routing_forbidden=True,
        tool_invocation_forbidden=True,
        delivery_forbidden=True,
        action_execution_forbidden=True,
        external_resource_admission_forbidden=True,
        model_vector_retrieval_rag_authority_forbidden=True,
        ui_authority_forbidden=True,
        this_scaffold_grants_runtime_authority=False,
        this_scaffold_grants_acceptance_authority=False,
        this_scaffold_grants_permission=False,
        this_scaffold_registers_routes=False,
        this_scaffold_modifies_config=False,
        this_scaffold_integrates_ui=False,
    )

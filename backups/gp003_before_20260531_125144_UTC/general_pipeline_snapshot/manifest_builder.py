"""General Learning-to-Answer Pipeline — MEA manifest builder (Build GP-001).

Builds a genuine MEA ProblemManifest (the engine's own dataclass) from a
parsed question plus the governed source procedure that authorises the domain.

This is the bridge from "question understood" to "problem state the engine can
reason about and seal." It uses the real ProblemManifest contract so the result
is a first-class engine citizen, not a parallel structure.
"""

from __future__ import annotations

from typing import Optional

from rmc_engine_v1.mea.manifest_schema import (
    ProblemManifest,
    MemoryRef,
    ClaimStatus,
    OutputPermission,
    canonical_hash as manifest_canonical_hash,
)

from .contracts import ParsedQuestion, SemanticSource, fraction_to_text


def build_problem_manifest(
    parsed: ParsedQuestion,
    source: SemanticSource,
) -> ProblemManifest:
    """Construct an unsolved MEA ProblemManifest for a parsed question.

    The manifest starts at full proof_debt and UNCLASSIFIED claim status: it is
    an open problem, not a result. The governed source procedure for the domain
    is recorded as memory_ancestry so the eventual seal can prove the relation's
    origin. allowed_tools names the exact-arithmetic permission only.
    """
    procedure = source.procedure_for_domain(parsed.domain)
    if procedure is None:
        raise ValueError(
            f"no governed procedure for domain {parsed.domain!r}; "
            f"source does not authorise this kind of problem"
        )

    known_facts = []
    for role, value in sorted(parsed.quantities.items()):
        known_facts.append(f"{role} = {fraction_to_text(value)}")
    for key, value in sorted(parsed.metadata.items()):
        known_facts.append(f"{key} = {value}")
    known_facts.append(f"governed_relation = {procedure.relation_text}")

    problem_id = canonical_problem_id(parsed)

    ancestry = [
        MemoryRef(
            memory_key=procedure.procedure_id,
            source=procedure.source_ref,
            relevance=1.0,
            evidence_tier="governed_source_procedure",
        )
    ]

    manifest = ProblemManifest(
        problem_id=problem_id,
        goal=f"Resolve the unknown for a {parsed.domain} question and verify it by exact arithmetic.",
        known_facts=known_facts,
        unknowns=["target_value"],
        constraints=[
            "use only exact arithmetic permitted by the governed relation",
            "answer must satisfy the original problem statement under substitution",
        ],
        success_conditions=["unknown resolved", "result verified by exact substitution"],
        failure_conditions=["verification fails", "relation not supported by source"],
        proof_debt=1.0,
        memory_ancestry=ancestry,
        goal_ancestry=[f"domain:{parsed.domain}", f"source:{source.source_id}"],
        claim_status=ClaimStatus.UNCLASSIFIED.value,
        output_permissions=OutputPermission.SEALED.value,
        allowed_tools=["exact_arithmetic"],
    )
    return manifest


def canonical_problem_id(parsed: ParsedQuestion) -> str:
    return "gp_" + manifest_canonical_hash_safe(parsed)[:24]


def manifest_canonical_hash_safe(parsed: ParsedQuestion) -> str:
    # Hash the parsed question payload (stable) for a deterministic problem id.
    from .contracts import canonical_hash as _ch
    return _ch(parsed.to_dict())


__all__ = ["build_problem_manifest", "canonical_problem_id"]

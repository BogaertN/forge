"""Exact accepted-scope record builder."""

from __future__ import annotations

from dataclasses import dataclass

from .authority import ACCEPTED_SCOPE_SENTENCE, SLICE24_HARD_BOUNDARY

@dataclass(frozen=True)
class AcceptedScopeRecord:
    scope_id: str
    accepted: bool
    accepted_sentence: str
    required_command_count: int
    passed_command_count: int
    external_context_passed: bool
    source_guard_passed: bool
    exact_only: bool
    hard_boundary: tuple[str, ...]
    rejected_claims: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "scope_id": self.scope_id,
            "accepted": self.accepted,
            "accepted_sentence": self.accepted_sentence,
            "required_command_count": self.required_command_count,
            "passed_command_count": self.passed_command_count,
            "external_context_passed": self.external_context_passed,
            "source_guard_passed": self.source_guard_passed,
            "exact_only": self.exact_only,
            "hard_boundary": list(self.hard_boundary),
            "rejected_claims": list(self.rejected_claims),
        }


def build_scope_record(required_command_count: int, passed_command_count: int, external_context_passed: bool, source_guard_passed: bool) -> AcceptedScopeRecord:
    accepted = (
        required_command_count > 0
        and required_command_count == passed_command_count
        and external_context_passed
        and source_guard_passed
    )
    return AcceptedScopeRecord(
        scope_id="slice24-accepted-scope:exact-required-proof-set",
        accepted=accepted,
        accepted_sentence=ACCEPTED_SCOPE_SENTENCE if accepted else "No accepted scope beyond recorded partial evidence because the required proof set did not fully pass.",
        required_command_count=required_command_count,
        passed_command_count=passed_command_count,
        external_context_passed=external_context_passed,
        source_guard_passed=source_guard_passed,
        exact_only=True,
        hard_boundary=SLICE24_HARD_BOUNDARY,
        rejected_claims=(
            "general_language_competence_not_accepted",
            "live_runtime_authority_not_accepted",
            "public_capability_not_accepted",
            "memory_delivery_action_not_accepted",
        ),
    )

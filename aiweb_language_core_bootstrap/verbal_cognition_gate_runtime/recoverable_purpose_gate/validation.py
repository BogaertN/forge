"""Fail-closed validation for Slice 40F recoverable-purpose evaluation."""
from __future__ import annotations

import re
from typing import Iterable

from ..governed_lifecycle import GateLifecycleStage, validate_governance_bundle
from ..schema import VerbalCognitionGateFamily
from ..predicate_frame_version_custody import (
    invalid_predicate_frame_version_fields,
)
from .identity import (
    expected_result_digest,
    with_expected_assertion_id,
    with_expected_evaluation_input_id,
    with_expected_finding_id,
    with_expected_observation_id,
    with_expected_profile_id,
)
from .schema import *


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _issue(path, code, detail):
    return RecoverablePurposeValidationIssue(path, code, detail)


def _ordered(
    items: Iterable[RecoverablePurposeValidationIssue],
) -> RecoverablePurposeValidationReport:
    return RecoverablePurposeValidationReport(
        tuple(
            sorted(
                items,
                key=lambda item: (
                    item.path,
                    item.code.value,
                    item.detail,
                ),
            )
        )
    )


def _text(value, path, issues):
    if (
        not isinstance(value, str)
        or not value
        or _IDENTIFIER.fullmatch(value) is None
    ):
        issues.append(
            _issue(
                path,
                RecoverablePurposeValidationCode.INVALID_IDENTIFIER,
                "controlled identifier required",
            )
        )


def _tuple(value, path, issues, allow_empty=True):
    if not isinstance(value, tuple) or (not allow_empty and not value):
        issues.append(
            _issue(
                path,
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "tuple of controlled identifiers required",
            )
        )
        return
    try:
        if len(set(value)) != len(value):
            issues.append(
                _issue(
                    path,
                    RecoverablePurposeValidationCode.DUPLICATE_ID,
                    "duplicate tuple value",
                )
            )
    except TypeError:
        issues.append(
            _issue(
                path,
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "hashable identifier tuple required",
            )
        )
    for index, item in enumerate(value):
        _text(item, f"{path}[{index}]", issues)


def _identity(actual, expected, field, path, issues):
    if getattr(actual, field) != getattr(expected, field):
        issues.append(
            _issue(
                path,
                RecoverablePurposeValidationCode.IDENTITY_MISMATCH,
                "deterministic identity mismatch",
            )
        )


def _false_flags(value, names, prefix, issues, code):
    for name in names:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"{prefix}.{name}",
                    code,
                    "must be false",
                )
            )


def validate_profile(value: object) -> RecoverablePurposeValidationReport:
    issues = []
    if not isinstance(value, RecoverablePurposeGateRuntimeProfile):
        return _ordered(
            (
                _issue(
                    "profile",
                    RecoverablePurposeValidationCode.TYPE_MISMATCH,
                    "RecoverablePurposeGateRuntimeProfile required",
                ),
            )
        )
    for name in ("profile_id", "profile_key", "gate_profile_ref"):
        _text(getattr(value, name), f"profile.{name}", issues)
    if (
        value.profile_version != SLICE40F_PROFILE_VERSION
        or value.gate_profile_version != "v1.0.0"
    ):
        issues.append(
            _issue(
                "profile.profile_version",
                RecoverablePurposeValidationCode.INVALID_VERSION,
                "only v1.0.0 admitted",
            )
        )
    if value.schema_version != SLICE40F_SCHEMA_VERSION:
        issues.append(
            _issue(
                "profile.schema_version",
                RecoverablePurposeValidationCode.INVALID_VERSION,
                "Slice 40F schema required",
            )
        )
    _tuple(
        value.governing_authority_refs,
        "profile.governing_authority_refs",
        issues,
        False,
    )
    if value.permitted_distinction_kinds != tuple(PurportDistinctionKind):
        issues.append(
            _issue(
                "profile.permitted_distinction_kinds",
                RecoverablePurposeValidationCode.CROSS_RECORD_MISMATCH,
                "all and only Slice 40F distinctions required",
            )
        )
    required_true = (
        "exact_candidate_records_required",
        "approved_discourse_ancestry_only",
        "authorized_reference_state_only",
        "exact_active_context_only",
    )
    for name in required_true:
        if getattr(value, name) is not True:
            issues.append(
                _issue(
                    f"profile.{name}",
                    RecoverablePurposeValidationCode.EXACT_PURPOSE_AUTHORITY_REQUIRED,
                    "must be true",
                )
            )
    _false_flags(
        value,
        (
            "hidden_intent_inference_allowed",
            "assistant_intuition_allowed",
            "psychological_inference_allowed",
            "emotional_interpretation_allowed",
            "raw_text_only_inference_allowed",
        ),
        "profile",
        issues,
        RecoverablePurposeValidationCode.HIDDEN_INTENT_PROHIBITED,
    )
    _false_flags(
        value,
        ("capability_existence_inference_allowed",),
        "profile",
        issues,
        RecoverablePurposeValidationCode.CAPABILITY_INFERENCE_PROHIBITED,
    )
    _false_flags(
        value,
        ("prior_conversation_habit_allowed",),
        "profile",
        issues,
        RecoverablePurposeValidationCode.CONVERSATION_HABIT_PROHIBITED,
    )
    _false_flags(
        value,
        (
            "purpose_conflation_allowed",
            "automatic_purpose_collapse_allowed",
        ),
        "profile",
        issues,
        RecoverablePurposeValidationCode.AUTOMATIC_COLLAPSE_PROHIBITED,
    )
    _false_flags(
        value,
        (
            "gate_composition_allowed",
            "selected_meaning_allowed",
            "route_tool_action_allowed",
        ),
        "profile",
        issues,
        RecoverablePurposeValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
    )
    _identity(
        value,
        with_expected_profile_id(value),
        "profile_id",
        "profile.profile_id",
        issues,
    )
    return _ordered(issues)


def validate_assertion(value: object) -> RecoverablePurposeValidationReport:
    issues = []
    if not isinstance(value, RecoverablePurposeAssertion):
        return _ordered(
            (
                _issue(
                    "assertion",
                    RecoverablePurposeValidationCode.TYPE_MISMATCH,
                    "RecoverablePurposeAssertion required",
                ),
            )
        )
    for name in (
        "assertion_id",
        "candidate_input_ref",
        "predicate_id",
        "frame_id",
        "assertion_key",
    ):
        _text(getattr(value, name), f"assertion.{name}", issues)
    for name in invalid_predicate_frame_version_fields(
        predicate_id=value.predicate_id,
        predicate_version=value.predicate_version,
        frame_id=value.frame_id,
        frame_version=value.frame_version,
    ):
        issues.append(
            _issue(
                f"assertion.{name}",
                RecoverablePurposeValidationCode.INVALID_VERSION,
                "exact legacy or registry-custodied predicate/frame version required",
            )
        )
    if not isinstance(value.distinction_kind, PurportDistinctionKind):
        issues.append(
            _issue(
                "assertion.distinction_kind",
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "PurportDistinctionKind required",
            )
        )
    if not isinstance(value.represented_act, CommunicativeActKind):
        issues.append(
            _issue(
                "assertion.represented_act",
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "CommunicativeActKind required",
            )
        )
    if not isinstance(value.prohibited_conflation_act, CommunicativeActKind):
        issues.append(
            _issue(
                "assertion.prohibited_conflation_act",
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "CommunicativeActKind required",
            )
        )
    if (
        isinstance(value.distinction_kind, PurportDistinctionKind)
        and isinstance(value.represented_act, CommunicativeActKind)
        and isinstance(value.prohibited_conflation_act, CommunicativeActKind)
    ):
        expected_pair = PURPORT_DISTINCTION_PAIRS[value.distinction_kind]
        if (
            value.represented_act not in expected_pair
            or value.prohibited_conflation_act not in expected_pair
            or value.represented_act is value.prohibited_conflation_act
        ):
            issues.append(
                _issue(
                    "assertion.represented_act",
                    RecoverablePurposeValidationCode.DISTINCTION_CONFLATION_PROHIBITED,
                    "exact distinction pair required",
                )
            )
    for name in (
        "candidate_record_refs",
        "purpose_support_refs",
        "authority_refs",
    ):
        _tuple(getattr(value, name), f"assertion.{name}", issues, False)
    for name in (
        "discourse_ancestry_refs",
        "authorized_reference_state_refs",
        "active_context_refs",
    ):
        _tuple(getattr(value, name), f"assertion.{name}", issues, True)
    if value.exact_candidate_records is not True or value.explicit_purpose_only is not True:
        issues.append(
            _issue(
                "assertion.exact_candidate_records",
                RecoverablePurposeValidationCode.EXACT_PURPOSE_AUTHORITY_REQUIRED,
                "explicit exact candidate purpose support required",
            )
        )
    context_pairs = (
        (
            "discourse_ancestry_refs",
            "discourse_ancestry_authorized",
        ),
        (
            "authorized_reference_state_refs",
            "reference_state_authorized",
        ),
        (
            "active_context_refs",
            "active_context_authorized",
        ),
    )
    for refs_name, flag_name in context_pairs:
        refs = getattr(value, refs_name)
        flag = getattr(value, flag_name)
        if refs and flag is not True:
            issues.append(
                _issue(
                    f"assertion.{flag_name}",
                    RecoverablePurposeValidationCode.UNAUTHORIZED_CONTEXT_PROHIBITED,
                    "context refs require exact authority",
                )
            )
        if not refs and flag is not False:
            issues.append(
                _issue(
                    f"assertion.{flag_name}",
                    RecoverablePurposeValidationCode.CROSS_RECORD_MISMATCH,
                    "authority flag must reflect ref presence",
                )
            )
    if value.schema_version != SLICE40F_SCHEMA_VERSION:
        issues.append(
            _issue(
                "assertion.schema_version",
                RecoverablePurposeValidationCode.INVALID_VERSION,
                "Slice 40F schema required",
            )
        )
    _identity(
        value,
        with_expected_assertion_id(value),
        "assertion_id",
        "assertion.assertion_id",
        issues,
    )
    return _ordered(issues)


def validate_observation(value: object) -> RecoverablePurposeValidationReport:
    issues = []
    if not isinstance(value, RecoverablePurposeObservation):
        return _ordered(
            (
                _issue(
                    "observation",
                    RecoverablePurposeValidationCode.TYPE_MISMATCH,
                    "RecoverablePurposeObservation required",
                ),
            )
        )
    for name in (
        "observation_id",
        "assertion_ref",
        "candidate_input_ref",
    ):
        _text(getattr(value, name), f"observation.{name}", issues)
    if not isinstance(value.authority_state, RecoverablePurposeAuthorityState):
        issues.append(
            _issue(
                "observation.authority_state",
                RecoverablePurposeValidationCode.AUTHORITY_STATE_INVALID,
                "closed authority state required",
            )
        )
    if not isinstance(value.purpose_judgment, RecoverablePurposeJudgment):
        issues.append(
            _issue(
                "observation.purpose_judgment",
                RecoverablePurposeValidationCode.JUDGMENT_INVALID,
                "closed purpose judgment required",
            )
        )
    for name in (
        "supporting_refs",
        "missing_authority_refs",
        "conflicting_refs",
        "trace_refs",
        "provenance_refs",
    ):
        _tuple(
            getattr(value, name),
            f"observation.{name}",
            issues,
            name in (
                "supporting_refs",
                "missing_authority_refs",
                "conflicting_refs",
            ),
        )
    if (
        isinstance(value.authority_state, RecoverablePurposeAuthorityState)
        and isinstance(value.purpose_judgment, RecoverablePurposeJudgment)
    ):
        if value.authority_state is RecoverablePurposeAuthorityState.ADMITTED:
            if value.purpose_judgment not in (
                RecoverablePurposeJudgment.RECOVERABLE,
                RecoverablePurposeJudgment.UNRECOVERABLE,
            ):
                issues.append(
                    _issue(
                        "observation.purpose_judgment",
                        RecoverablePurposeValidationCode.JUDGMENT_INVALID,
                        "admitted authority requires recoverable or unrecoverable",
                    )
                )
        elif value.purpose_judgment is not RecoverablePurposeJudgment.NOT_EVALUATED:
            issues.append(
                _issue(
                    "observation.purpose_judgment",
                    RecoverablePurposeValidationCode.JUDGMENT_INVALID,
                    "non-admitted authority must remain not_evaluated",
                )
            )
        if (
            value.purpose_judgment is RecoverablePurposeJudgment.RECOVERABLE
            and not value.supporting_refs
        ):
            issues.append(
                _issue(
                    "observation.supporting_refs",
                    RecoverablePurposeValidationCode.EXACT_PURPOSE_AUTHORITY_REQUIRED,
                    "recoverable judgment requires support",
                )
            )
        if (
            value.purpose_judgment is RecoverablePurposeJudgment.UNRECOVERABLE
            and not (value.missing_authority_refs or value.conflicting_refs)
        ):
            issues.append(
                _issue(
                    "observation.missing_authority_refs",
                    RecoverablePurposeValidationCode.EXACT_PURPOSE_AUTHORITY_REQUIRED,
                    "unrecoverable judgment requires missing or conflicting authority",
                )
            )
        if (
            value.authority_state is RecoverablePurposeAuthorityState.ABSENT
            and not value.missing_authority_refs
        ):
            issues.append(
                _issue(
                    "observation.missing_authority_refs",
                    RecoverablePurposeValidationCode.EXACT_PURPOSE_AUTHORITY_REQUIRED,
                    "absent authority must be identified",
                )
            )
        if (
            value.authority_state
            in (
                RecoverablePurposeAuthorityState.CONFLICTED,
                RecoverablePurposeAuthorityState.AMBIGUOUS,
            )
            and not value.conflicting_refs
        ):
            issues.append(
                _issue(
                    "observation.conflicting_refs",
                    RecoverablePurposeValidationCode.EXACT_PURPOSE_AUTHORITY_REQUIRED,
                    "conflicted or ambiguous state requires exact conflict refs",
                )
            )
    if value.schema_version != SLICE40F_SCHEMA_VERSION:
        issues.append(
            _issue(
                "observation.schema_version",
                RecoverablePurposeValidationCode.INVALID_VERSION,
                "Slice 40F schema required",
            )
        )
    _identity(
        value,
        with_expected_observation_id(value),
        "observation_id",
        "observation.observation_id",
        issues,
    )
    return _ordered(issues)


def validate_evaluation_input(
    value: object,
) -> RecoverablePurposeValidationReport:
    issues = []
    if not isinstance(value, RecoverablePurposeEvaluationInput):
        return _ordered(
            (
                _issue(
                    "evaluation_input",
                    RecoverablePurposeValidationCode.TYPE_MISMATCH,
                    "RecoverablePurposeEvaluationInput required",
                ),
            )
        )
    for name in (
        "evaluation_input_id",
        "candidate_input_ref",
        "predicate_id",
        "frame_id",
    ):
        _text(getattr(value, name), f"evaluation_input.{name}", issues)
    for name in invalid_predicate_frame_version_fields(
        predicate_id=value.predicate_id,
        predicate_version=value.predicate_version,
        frame_id=value.frame_id,
        frame_version=value.frame_version,
    ):
        issues.append(
            _issue(
                f"evaluation_input.{name}",
                RecoverablePurposeValidationCode.INVALID_VERSION,
                "exact legacy or registry-custodied predicate/frame version required",
            )
        )

    try:
        governance = validate_governance_bundle(value.governance_bundle)
        if not governance.ok:
            issues.append(
                _issue(
                    "evaluation_input.governance_bundle",
                    RecoverablePurposeValidationCode.GOVERNANCE_INVALID,
                    "governance bundle invalid",
                )
            )
        review = value.governance_bundle.review_record
        if (
            review.identity.gate_family
            is not VerbalCognitionGateFamily.RECOVERABLE_PURPOSE
        ):
            issues.append(
                _issue(
                    "evaluation_input.governance_bundle.review_record.identity.gate_family",
                    RecoverablePurposeValidationCode.RECOVERABLE_PURPOSE_FAMILY_REQUIRED,
                    "recoverable-purpose family required",
                )
            )
        if (
            not value.governance_bundle.validation_complete
            or not any(
                record.stage is GateLifecycleStage.RECORD_SEALED
                for record in value.governance_bundle.lifecycle_records
            )
        ):
            issues.append(
                _issue(
                    "evaluation_input.governance_bundle",
                    RecoverablePurposeValidationCode.SEALED_GOVERNANCE_REQUIRED,
                    "sealed governance required",
                )
            )
        if (
            review.candidate_input.candidate_input_ref_id
            != value.candidate_input_ref
        ):
            issues.append(
                _issue(
                    "evaluation_input.candidate_input_ref",
                    RecoverablePurposeValidationCode.CROSS_RECORD_MISMATCH,
                    "candidate reference mismatch",
                )
            )
        if (
            review.profile.profile_id
            != value.runtime_profile.gate_profile_ref
            or review.profile.profile_version
            != value.runtime_profile.gate_profile_version
        ):
            issues.append(
                _issue(
                    "evaluation_input.runtime_profile",
                    RecoverablePurposeValidationCode.CROSS_RECORD_MISMATCH,
                    "gate profile mismatch",
                )
            )
    except Exception:
        issues.append(
            _issue(
                "evaluation_input.governance_bundle",
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "governance shape required",
            )
        )

    issues.extend(validate_profile(value.runtime_profile).issues)
    if not isinstance(value.assertions, tuple) or not value.assertions:
        issues.append(
            _issue(
                "evaluation_input.assertions",
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "non-empty assertion tuple required",
            )
        )
    if not isinstance(value.observations, tuple) or not value.observations:
        issues.append(
            _issue(
                "evaluation_input.observations",
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "non-empty observation tuple required",
            )
        )

    assertion_ids = []
    distinction_keys = []
    observation_refs = []
    if isinstance(value.assertions, tuple):
        for index, assertion in enumerate(value.assertions):
            issues.extend(validate_assertion(assertion).issues)
            if isinstance(assertion, RecoverablePurposeAssertion):
                assertion_ids.append(assertion.assertion_id)
                distinction_keys.append(
                    (
                        assertion.distinction_kind,
                        assertion.represented_act,
                    )
                )
                for field_name in (
                    "candidate_input_ref",
                    "predicate_id",
                    "predicate_version",
                    "frame_id",
                    "frame_version",
                ):
                    if getattr(assertion, field_name) != getattr(
                        value,
                        field_name,
                    ):
                        issues.append(
                            _issue(
                                f"evaluation_input.assertions[{index}].{field_name}",
                                RecoverablePurposeValidationCode.CROSS_RECORD_MISMATCH,
                                "input mismatch",
                            )
                        )
                for ref in assertion.candidate_record_refs:
                    if ref not in value.candidate_record_refs:
                        issues.append(
                            _issue(
                                f"evaluation_input.assertions[{index}].candidate_record_refs",
                                RecoverablePurposeValidationCode.REFERENCE_NOT_FOUND,
                                "candidate record not in evaluation custody",
                            )
                        )
                for refs_name in (
                    "discourse_ancestry_refs",
                    "authorized_reference_state_refs",
                    "active_context_refs",
                ):
                    allowed = getattr(value, refs_name)
                    for ref in getattr(assertion, refs_name):
                        if ref not in allowed:
                            issues.append(
                                _issue(
                                    f"evaluation_input.assertions[{index}].{refs_name}",
                                    RecoverablePurposeValidationCode.REFERENCE_NOT_FOUND,
                                    "context ref not in evaluation custody",
                                )
                            )
    if len(set(assertion_ids)) != len(assertion_ids):
        issues.append(
            _issue(
                "evaluation_input.assertions",
                RecoverablePurposeValidationCode.DUPLICATE_ID,
                "duplicate assertion identity",
            )
        )
    if len(set(distinction_keys)) != len(distinction_keys):
        issues.append(
            _issue(
                "evaluation_input.assertions",
                RecoverablePurposeValidationCode.DUPLICATE_ID,
                "duplicate distinction/act assertion",
            )
        )

    if isinstance(value.observations, tuple):
        for index, observation in enumerate(value.observations):
            issues.extend(validate_observation(observation).issues)
            if isinstance(observation, RecoverablePurposeObservation):
                observation_refs.append(observation.assertion_ref)
                if observation.candidate_input_ref != value.candidate_input_ref:
                    issues.append(
                        _issue(
                            f"evaluation_input.observations[{index}].candidate_input_ref",
                            RecoverablePurposeValidationCode.CROSS_RECORD_MISMATCH,
                            "candidate reference mismatch",
                        )
                    )
                if observation.assertion_ref not in assertion_ids:
                    issues.append(
                        _issue(
                            f"evaluation_input.observations[{index}].assertion_ref",
                            RecoverablePurposeValidationCode.REFERENCE_NOT_FOUND,
                            "assertion not found",
                        )
                    )
    if len(set(observation_refs)) != len(observation_refs):
        issues.append(
            _issue(
                "evaluation_input.observations",
                RecoverablePurposeValidationCode.DUPLICATE_ID,
                "duplicate observation for assertion",
            )
        )
    if sorted(assertion_ids) != sorted(observation_refs):
        issues.append(
            _issue(
                "evaluation_input.observations",
                RecoverablePurposeValidationCode.COUNT_MISMATCH,
                "exactly one observation per assertion required",
            )
        )

    for name in (
        "candidate_record_refs",
        "trace_refs",
        "provenance_refs",
        "limitation_refs",
    ):
        _tuple(
            getattr(value, name),
            f"evaluation_input.{name}",
            issues,
            False,
        )
    for name in (
        "discourse_ancestry_refs",
        "authorized_reference_state_refs",
        "active_context_refs",
    ):
        _tuple(
            getattr(value, name),
            f"evaluation_input.{name}",
            issues,
            True,
        )

    _false_flags(
        value,
        (
            "hidden_intent_inference_used",
            "assistant_intuition_used",
            "psychological_inference_used",
            "emotional_interpretation_used",
            "raw_text_only_inference_used",
        ),
        "evaluation_input",
        issues,
        RecoverablePurposeValidationCode.HIDDEN_INTENT_PROHIBITED,
    )
    _false_flags(
        value,
        ("capability_existence_inference_used",),
        "evaluation_input",
        issues,
        RecoverablePurposeValidationCode.CAPABILITY_INFERENCE_PROHIBITED,
    )
    _false_flags(
        value,
        ("prior_conversation_habit_used",),
        "evaluation_input",
        issues,
        RecoverablePurposeValidationCode.CONVERSATION_HABIT_PROHIBITED,
    )
    _false_flags(
        value,
        (
            "purpose_conflation_used",
            "automatic_purpose_collapse_used",
        ),
        "evaluation_input",
        issues,
        RecoverablePurposeValidationCode.AUTOMATIC_COLLAPSE_PROHIBITED,
    )
    _false_flags(
        value,
        ("unauthorized_context_used",),
        "evaluation_input",
        issues,
        RecoverablePurposeValidationCode.UNAUTHORIZED_CONTEXT_PROHIBITED,
    )
    _false_flags(
        value,
        ("candidate_structure_mutated",),
        "evaluation_input",
        issues,
        RecoverablePurposeValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
    )
    if value.raw_text_supplied is not False:
        issues.append(
            _issue(
                "evaluation_input.raw_text_supplied",
                RecoverablePurposeValidationCode.HIDDEN_INTENT_PROHIBITED,
                "raw text is not purpose authority",
            )
        )
    if value.schema_version != SLICE40F_SCHEMA_VERSION:
        issues.append(
            _issue(
                "evaluation_input.schema_version",
                RecoverablePurposeValidationCode.INVALID_VERSION,
                "Slice 40F schema required",
            )
        )
    _identity(
        value,
        with_expected_evaluation_input_id(value),
        "evaluation_input_id",
        "evaluation_input.evaluation_input_id",
        issues,
    )
    return _ordered(issues)


def validate_finding(value: object) -> RecoverablePurposeValidationReport:
    issues = []
    if not isinstance(value, RecoverablePurposeFinding):
        return _ordered(
            (
                _issue(
                    "finding",
                    RecoverablePurposeValidationCode.TYPE_MISMATCH,
                    "RecoverablePurposeFinding required",
                ),
            )
        )
    for name in ("finding_id", "evaluation_input_ref"):
        _text(getattr(value, name), f"finding.{name}", issues)
    if value.assertion_ref is not None:
        _text(value.assertion_ref, "finding.assertion_ref", issues)
    if not isinstance(value.finding_kind, RecoverablePurposeFindingKind):
        issues.append(
            _issue(
                "finding.finding_kind",
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "RecoverablePurposeFindingKind required",
            )
        )
    for name in (
        "supporting_refs",
        "missing_authority_refs",
        "conflicting_refs",
        "trace_refs",
        "provenance_refs",
        "reason_refs",
    ):
        _tuple(
            getattr(value, name),
            f"finding.{name}",
            issues,
            name in (
                "supporting_refs",
                "missing_authority_refs",
                "conflicting_refs",
            ),
        )
    if value.schema_version != SLICE40F_SCHEMA_VERSION:
        issues.append(
            _issue(
                "finding.schema_version",
                RecoverablePurposeValidationCode.INVALID_VERSION,
                "Slice 40F schema required",
            )
        )
    _identity(
        value,
        with_expected_finding_id(value),
        "finding_id",
        "finding.finding_id",
        issues,
    )
    return _ordered(issues)


def validate_result(value: object) -> RecoverablePurposeValidationReport:
    issues = []
    if not isinstance(value, RecoverablePurposeGateResult):
        return _ordered(
            (
                _issue(
                    "result",
                    RecoverablePurposeValidationCode.TYPE_MISMATCH,
                    "RecoverablePurposeGateResult required",
                ),
            )
        )
    for name in (
        "result_id",
        "evaluation_input_ref",
        "review_record_id",
        "gate_id",
        "gate_profile_id",
        "candidate_input_ref",
        "predicate_id",
        "frame_id",
    ):
        _text(getattr(value, name), f"result.{name}", issues)
    for name in invalid_predicate_frame_version_fields(
        predicate_id=value.predicate_id,
        predicate_version=value.predicate_version,
        frame_id=value.frame_id,
        frame_version=value.frame_version,
    ):
        issues.append(
            _issue(
                f"result.{name}",
                RecoverablePurposeValidationCode.INVALID_VERSION,
                "exact legacy or registry-custodied predicate/frame version required",
            )
        )
    if not isinstance(value.overall_state, RecoverablePurposeOverallState):
        issues.append(
            _issue(
                "result.overall_state",
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "RecoverablePurposeOverallState required",
            )
        )
    if not isinstance(value.findings, tuple) or not value.findings:
        issues.append(
            _issue(
                "result.findings",
                RecoverablePurposeValidationCode.TYPE_MISMATCH,
                "non-empty findings required",
            )
        )
    else:
        for finding in value.findings:
            issues.extend(validate_finding(finding).issues)
            if (
                isinstance(finding, RecoverablePurposeFinding)
                and finding.evaluation_input_ref != value.evaluation_input_ref
            ):
                issues.append(
                    _issue(
                        "result.findings",
                        RecoverablePurposeValidationCode.CROSS_RECORD_MISMATCH,
                        "finding input mismatch",
                    )
                )
    counts = (
        value.recoverable_count,
        value.unrecoverable_count,
        value.ambiguous_count,
        value.unsupported_count,
        value.conflicted_count,
        value.indeterminate_count,
    )
    if (
        any(type(item) is not int or item < 0 for item in counts)
        or type(value.assertion_count) is not int
        or value.assertion_count < 1
        or sum(counts) != value.assertion_count
    ):
        issues.append(
            _issue(
                "result.assertion_count",
                RecoverablePurposeValidationCode.COUNT_MISMATCH,
                "non-negative counts must sum to assertion_count",
            )
        )
    expected_state = None
    if value.conflicted_count:
        expected_state = RecoverablePurposeOverallState.CONFLICTED
    elif value.unsupported_count:
        expected_state = RecoverablePurposeOverallState.UNSUPPORTED
    elif value.ambiguous_count:
        expected_state = RecoverablePurposeOverallState.AMBIGUOUS
    elif value.indeterminate_count:
        expected_state = RecoverablePurposeOverallState.INDETERMINATE
    elif value.unrecoverable_count:
        expected_state = RecoverablePurposeOverallState.UNRECOVERABLE
    elif value.recoverable_count == value.assertion_count:
        expected_state = RecoverablePurposeOverallState.RECOVERABLE
    if expected_state is not value.overall_state:
        issues.append(
            _issue(
                "result.overall_state",
                RecoverablePurposeValidationCode.CROSS_RECORD_MISMATCH,
                "overall state does not match counts",
            )
        )
    if value.deterministic is not True or value.exact_purpose_authority_preserved is not True:
        issues.append(
            _issue(
                "result.exact_purpose_authority_preserved",
                RecoverablePurposeValidationCode.EXACT_PURPOSE_AUTHORITY_REQUIRED,
                "deterministic exact authority must be preserved",
            )
        )
    _false_flags(
        value,
        (
            "candidate_structure_mutated",
            "hidden_intent_inference_used",
            "capability_existence_inference_used",
            "prior_conversation_habit_used",
            "assistant_intuition_used",
            "psychological_inference_used",
            "emotional_interpretation_used",
            "raw_text_only_inference_used",
            "purpose_conflation_used",
            "automatic_purpose_collapse_used",
            "unauthorized_context_used",
            "clarification_required_created",
            "rejection_created",
            "refusal_relevant_created",
            "blocked_progression_created",
            "composed_gate_outcome_created",
            "candidate_disposition_created",
            "selected_meaning_created",
            "truth_determined",
            "evidence_validated",
            "permission_granted",
            "execution_authorized",
            "capability_availability_created",
            "route_created",
            "tool_invoked",
            "action_performed",
            "memory_accessed",
            "memory_written",
            "rendered",
            "delivered",
            "external_resource_loaded",
            "language_model_used",
            "embedding_used",
            "vector_used",
            "rag_used",
            "semantic_similarity_used",
        ),
        "result",
        issues,
        RecoverablePurposeValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
    )
    if (
        not isinstance(value.canonical_digest, str)
        or _SHA256.fullmatch(value.canonical_digest) is None
        or value.canonical_digest != expected_result_digest(value)
    ):
        issues.append(
            _issue(
                "result.canonical_digest",
                RecoverablePurposeValidationCode.INVALID_SHA256,
                "canonical digest mismatch",
            )
        )
    if (
        value.result_id
        != f"recoverable_purpose_result:sha256:{value.canonical_digest}"
    ):
        issues.append(
            _issue(
                "result.result_id",
                RecoverablePurposeValidationCode.IDENTITY_MISMATCH,
                "result identity mismatch",
            )
        )
    if value.digest_algorithm != DIGEST_ALGORITHM:
        issues.append(
            _issue(
                "result.digest_algorithm",
                RecoverablePurposeValidationCode.CROSS_RECORD_MISMATCH,
                "sha256 required",
            )
        )
    if value.schema_version != SLICE40F_SCHEMA_VERSION:
        issues.append(
            _issue(
                "result.schema_version",
                RecoverablePurposeValidationCode.INVALID_VERSION,
                "Slice 40F schema required",
            )
        )
    return _ordered(issues)


def assert_valid_evaluation_input(
    value: RecoverablePurposeEvaluationInput,
) -> RecoverablePurposeEvaluationInput:
    report = validate_evaluation_input(value)
    if not report.ok:
        raise RecoverablePurposeValidationError(report)
    return value


def assert_valid_result(
    value: RecoverablePurposeGateResult,
) -> RecoverablePurposeGateResult:
    report = validate_result(value)
    if not report.ok:
        raise RecoverablePurposeValidationError(report)
    return value

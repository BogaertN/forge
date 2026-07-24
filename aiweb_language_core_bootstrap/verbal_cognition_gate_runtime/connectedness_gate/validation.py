"""Fail-closed validation for Slice 40E connectedness evaluation."""
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
    return ConnectednessValidationIssue(path, code, detail)


def _ordered(
    items: Iterable[ConnectednessValidationIssue],
) -> ConnectednessValidationReport:
    return ConnectednessValidationReport(
        tuple(sorted(items, key=lambda item: (item.path, item.code.value, item.detail)))
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
                ConnectednessValidationCode.INVALID_IDENTIFIER,
                "controlled identifier required",
            )
        )


def _tuple(value, path, issues, allow_empty=True):
    if not isinstance(value, tuple) or (not allow_empty and not value):
        issues.append(
            _issue(
                path,
                ConnectednessValidationCode.TYPE_MISMATCH,
                "tuple of identifiers required",
            )
        )
        return
    if len(set(value)) != len(value):
        issues.append(
            _issue(
                path,
                ConnectednessValidationCode.DUPLICATE_ID,
                "duplicate tuple value",
            )
        )
    for index, item in enumerate(value):
        _text(item, f"{path}[{index}]", issues)


def _identity(actual, expected, field, path, issues):
    if getattr(actual, field) != getattr(expected, field):
        issues.append(
            _issue(
                path,
                ConnectednessValidationCode.IDENTITY_MISMATCH,
                "deterministic identity mismatch",
            )
        )


def validate_profile(value: object) -> ConnectednessValidationReport:
    issues = []
    if not isinstance(value, ConnectednessGateRuntimeProfile):
        return _ordered(
            (
                _issue(
                    "profile",
                    ConnectednessValidationCode.TYPE_MISMATCH,
                    "ConnectednessGateRuntimeProfile required",
                ),
            )
        )
    for name in ("profile_id", "profile_key", "gate_profile_ref"):
        _text(getattr(value, name), f"profile.{name}", issues)
    if (
        value.profile_version != SLICE40E_PROFILE_VERSION
        or value.gate_profile_version != "v1.0.0"
    ):
        issues.append(
            _issue(
                "profile.profile_version",
                ConnectednessValidationCode.INVALID_VERSION,
                "only v1.0.0 admitted",
            )
        )
    if value.schema_version != SLICE40E_SCHEMA_VERSION:
        issues.append(
            _issue(
                "profile.schema_version",
                ConnectednessValidationCode.INVALID_VERSION,
                "Slice 40E schema required",
            )
        )
    _tuple(
        value.governing_authority_refs,
        "profile.governing_authority_refs",
        issues,
        False,
    )
    if value.permitted_assertion_kinds != tuple(ConnectednessAssertionKind):
        issues.append(
            _issue(
                "profile.permitted_assertion_kinds",
                ConnectednessValidationCode.CROSS_RECORD_MISMATCH,
                "all and only Slice 40E assertion kinds required",
            )
        )
    if value.exact_admitted_connections_only is not True:
        issues.append(
            _issue(
                "profile.exact_admitted_connections_only",
                ConnectednessValidationCode.EXACT_CONNECTION_AUTHORITY_REQUIRED,
                "must be true",
            )
        )
    cooccurrence_flags = (
        "cooccurrence_connection_allowed",
        "same_expression_connection_allowed",
        "same_manifest_connection_allowed",
    )
    transitive_flags = ("implicit_transitivity_allowed",)
    rewrite_flags = (
        "source_gap_bridge_allowed",
        "ancestry_gap_bridge_allowed",
        "scope_rewrite_allowed",
        "attachment_reassignment_allowed",
        "operator_trail_rewrite_allowed",
        "predicate_frame_rewire_allowed",
        "candidate_lineage_merge_allowed",
    )
    downstream_flags = (
        "raw_text_inspection_allowed",
        "similarity_fallback_allowed",
        "hidden_model_judgment_allowed",
        "gate_composition_allowed",
        "selected_meaning_allowed",
        "route_tool_action_allowed",
    )
    for name in cooccurrence_flags:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"profile.{name}",
                    ConnectednessValidationCode.CO_OCCURRENCE_AUTHORITY_PROHIBITED,
                    "must be false",
                )
            )
    for name in transitive_flags:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"profile.{name}",
                    ConnectednessValidationCode.INVENTED_TRANSITIVITY_PROHIBITED,
                    "must be false",
                )
            )
    for name in rewrite_flags:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"profile.{name}",
                    ConnectednessValidationCode.REWRITE_PROHIBITED,
                    "must be false",
                )
            )
    for name in downstream_flags:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"profile.{name}",
                    ConnectednessValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                    "must be false",
                )
            )
    _identity(
        value,
        with_expected_profile_id(value),
        "profile_id",
        "profile.profile_id",
        issues,
    )
    return _ordered(issues)


def validate_assertion(value: object) -> ConnectednessValidationReport:
    issues = []
    if not isinstance(value, ConnectednessAssertion):
        return _ordered(
            (
                _issue(
                    "assertion",
                    ConnectednessValidationCode.TYPE_MISMATCH,
                    "ConnectednessAssertion required",
                ),
            )
        )
    for name in (
        "assertion_id",
        "candidate_input_ref",
        "predicate_id",
        "frame_id",
        "assertion_key",
        "left_record_ref",
        "right_record_ref",
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
                ConnectednessValidationCode.INVALID_VERSION,
                "exact legacy or registry-custodied predicate/frame version required",
            )
        )
    if not isinstance(value.assertion_kind, ConnectednessAssertionKind):
        issues.append(
            _issue(
                "assertion.assertion_kind",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "ConnectednessAssertionKind required",
            )
        )
    for name in (
        "connection_basis_refs",
        "assertion_source_refs",
        "authority_refs",
    ):
        _tuple(getattr(value, name), f"assertion.{name}", issues, False)
    if value.left_record_ref == value.right_record_ref:
        issues.append(
            _issue(
                "assertion.right_record_ref",
                ConnectednessValidationCode.CROSS_RECORD_MISMATCH,
                "connectedness requires two distinct record references",
            )
        )
    if value.exact_admitted_connection is not True:
        issues.append(
            _issue(
                "assertion.exact_admitted_connection",
                ConnectednessValidationCode.EXACT_CONNECTION_AUTHORITY_REQUIRED,
                "must be true",
            )
        )
    for name in ("same_expression_only", "same_manifest_only"):
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"assertion.{name}",
                    ConnectednessValidationCode.CO_OCCURRENCE_AUTHORITY_PROHIBITED,
                    "co-occurrence alone cannot establish connection",
                )
            )
    if value.implicit_transitive_only is not False:
        issues.append(
            _issue(
                "assertion.implicit_transitive_only",
                ConnectednessValidationCode.INVENTED_TRANSITIVITY_PROHIBITED,
                "implicit transitivity cannot establish connection",
            )
        )
    if value.schema_version != SLICE40E_SCHEMA_VERSION:
        issues.append(
            _issue(
                "assertion.schema_version",
                ConnectednessValidationCode.INVALID_VERSION,
                "Slice 40E schema required",
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


def validate_observation(value: object) -> ConnectednessValidationReport:
    issues = []
    if not isinstance(value, ConnectednessObservation):
        return _ordered(
            (
                _issue(
                    "observation",
                    ConnectednessValidationCode.TYPE_MISMATCH,
                    "ConnectednessObservation required",
                ),
            )
        )
    for name in ("observation_id", "assertion_ref", "candidate_input_ref"):
        _text(getattr(value, name), f"observation.{name}", issues)
    if not isinstance(value.authority_state, ConnectednessAuthorityState):
        issues.append(
            _issue(
                "observation.authority_state",
                ConnectednessValidationCode.AUTHORITY_STATE_INVALID,
                "ConnectednessAuthorityState required",
            )
        )
    if not isinstance(value.connection_judgment, ConnectednessJudgment):
        issues.append(
            _issue(
                "observation.connection_judgment",
                ConnectednessValidationCode.JUDGMENT_INVALID,
                "ConnectednessJudgment required",
            )
        )
    if isinstance(value.authority_state, ConnectednessAuthorityState) and isinstance(
        value.connection_judgment,
        ConnectednessJudgment,
    ):
        if (
            value.authority_state is ConnectednessAuthorityState.ADMITTED
            and value.connection_judgment is ConnectednessJudgment.NOT_EVALUATED
        ):
            issues.append(
                _issue(
                    "observation.connection_judgment",
                    ConnectednessValidationCode.JUDGMENT_INVALID,
                    "admitted authority requires an exact judgment",
                )
            )
        if (
            value.authority_state is not ConnectednessAuthorityState.ADMITTED
            and value.connection_judgment is not ConnectednessJudgment.NOT_EVALUATED
        ):
            issues.append(
                _issue(
                    "observation.connection_judgment",
                    ConnectednessValidationCode.JUDGMENT_INVALID,
                    "non-admitted authority cannot carry a connection judgment",
                )
            )
        if (
            value.authority_state is ConnectednessAuthorityState.ADMITTED
            and value.connection_judgment is ConnectednessJudgment.CONNECTED
            and not value.supporting_refs
        ):
            issues.append(
                _issue(
                    "observation.supporting_refs",
                    ConnectednessValidationCode.EXACT_CONNECTION_AUTHORITY_REQUIRED,
                    "connected judgment requires supporting references",
                )
            )
        if (
            value.authority_state is ConnectednessAuthorityState.ADMITTED
            and value.connection_judgment is ConnectednessJudgment.DISCONNECTED
            and not value.disconnection_refs
        ):
            issues.append(
                _issue(
                    "observation.disconnection_refs",
                    ConnectednessValidationCode.EXACT_CONNECTION_AUTHORITY_REQUIRED,
                    "disconnected judgment requires disconnection references",
                )
            )
    for name in (
        "supporting_refs",
        "disconnection_refs",
        "trace_refs",
        "provenance_refs",
    ):
        _tuple(
            getattr(value, name),
            f"observation.{name}",
            issues,
            name in ("supporting_refs", "disconnection_refs"),
        )
    if value.schema_version != SLICE40E_SCHEMA_VERSION:
        issues.append(
            _issue(
                "observation.schema_version",
                ConnectednessValidationCode.INVALID_VERSION,
                "Slice 40E schema required",
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
) -> ConnectednessValidationReport:
    issues = []
    if not isinstance(value, ConnectednessEvaluationInput):
        return _ordered(
            (
                _issue(
                    "evaluation_input",
                    ConnectednessValidationCode.TYPE_MISMATCH,
                    "ConnectednessEvaluationInput required",
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
                ConnectednessValidationCode.INVALID_VERSION,
                "exact legacy or registry-custodied predicate/frame version required",
            )
        )

    governance = validate_governance_bundle(value.governance_bundle)
    if not governance.ok:
        issues.append(
            _issue(
                "evaluation_input.governance_bundle",
                ConnectednessValidationCode.GOVERNANCE_INVALID,
                "governance bundle invalid",
            )
        )
    try:
        review = value.governance_bundle.review_record
        if review.identity.gate_family is not VerbalCognitionGateFamily.CONNECTEDNESS:
            issues.append(
                _issue(
                    "evaluation_input.governance_bundle.review_record.identity.gate_family",
                    ConnectednessValidationCode.CONNECTEDNESS_FAMILY_REQUIRED,
                    "connectedness family required",
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
                    ConnectednessValidationCode.SEALED_GOVERNANCE_REQUIRED,
                    "sealed governance required",
                )
            )
        if review.candidate_input.candidate_input_ref_id != value.candidate_input_ref:
            issues.append(
                _issue(
                    "evaluation_input.candidate_input_ref",
                    ConnectednessValidationCode.CROSS_RECORD_MISMATCH,
                    "candidate reference mismatch",
                )
            )
        if (
            review.profile.profile_id != value.runtime_profile.gate_profile_ref
            or review.profile.profile_version
            != value.runtime_profile.gate_profile_version
        ):
            issues.append(
                _issue(
                    "evaluation_input.runtime_profile",
                    ConnectednessValidationCode.CROSS_RECORD_MISMATCH,
                    "gate profile mismatch",
                )
            )
    except Exception:
        issues.append(
            _issue(
                "evaluation_input.governance_bundle",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "governance shape required",
            )
        )

    issues.extend(validate_profile(value.runtime_profile).issues)
    if not isinstance(value.assertions, tuple) or not value.assertions:
        issues.append(
            _issue(
                "evaluation_input.assertions",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "non-empty tuple required",
            )
        )
    if not isinstance(value.observations, tuple) or not value.observations:
        issues.append(
            _issue(
                "evaluation_input.observations",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "non-empty tuple required",
            )
        )

    assertion_ids = []
    pair_keys = []
    observation_refs = []
    if isinstance(value.assertions, tuple):
        for index, assertion in enumerate(value.assertions):
            issues.extend(validate_assertion(assertion).issues)
            if isinstance(assertion, ConnectednessAssertion):
                assertion_ids.append(assertion.assertion_id)
                pair_keys.append(
                    (
                        assertion.assertion_kind,
                        assertion.left_record_ref,
                        assertion.right_record_ref,
                    )
                )
                for field_name in (
                    "candidate_input_ref",
                    "predicate_id",
                    "predicate_version",
                    "frame_id",
                    "frame_version",
                ):
                    if getattr(assertion, field_name) != getattr(value, field_name):
                        issues.append(
                            _issue(
                                f"evaluation_input.assertions[{index}].{field_name}",
                                ConnectednessValidationCode.CROSS_RECORD_MISMATCH,
                                "input mismatch",
                            )
                        )
    if len(set(assertion_ids)) != len(assertion_ids):
        issues.append(
            _issue(
                "evaluation_input.assertions",
                ConnectednessValidationCode.DUPLICATE_ID,
                "duplicate assertion",
            )
        )
    if len(set(pair_keys)) != len(pair_keys):
        issues.append(
            _issue(
                "evaluation_input.assertions",
                ConnectednessValidationCode.DUPLICATE_ID,
                "duplicate connection pair for assertion kind",
            )
        )

    if isinstance(value.observations, tuple):
        for index, observation in enumerate(value.observations):
            issues.extend(validate_observation(observation).issues)
            if isinstance(observation, ConnectednessObservation):
                observation_refs.append(observation.assertion_ref)
                if observation.candidate_input_ref != value.candidate_input_ref:
                    issues.append(
                        _issue(
                            f"evaluation_input.observations[{index}].candidate_input_ref",
                            ConnectednessValidationCode.CROSS_RECORD_MISMATCH,
                            "candidate mismatch",
                        )
                    )
                if observation.assertion_ref not in assertion_ids:
                    issues.append(
                        _issue(
                            f"evaluation_input.observations[{index}].assertion_ref",
                            ConnectednessValidationCode.REFERENCE_NOT_FOUND,
                            "assertion not found",
                        )
                    )
    if len(set(observation_refs)) != len(observation_refs):
        issues.append(
            _issue(
                "evaluation_input.observations",
                ConnectednessValidationCode.DUPLICATE_ID,
                "duplicate observation assertion",
            )
        )
    if set(observation_refs) != set(assertion_ids):
        issues.append(
            _issue(
                "evaluation_input.observations",
                ConnectednessValidationCode.COUNT_MISMATCH,
                "exactly one observation per assertion required",
            )
        )

    for name in ("trace_refs", "provenance_refs", "limitation_refs"):
        _tuple(getattr(value, name), f"evaluation_input.{name}", issues, False)

    cooccurrence_flags = (
        "cooccurrence_only_connection_used",
        "same_expression_only_connection_used",
        "same_manifest_only_connection_used",
    )
    rewrite_flags = (
        "source_gap_bridged",
        "ancestry_gap_bridged",
        "scope_rewritten",
        "attachment_reassigned",
        "operator_trail_rewritten",
        "predicate_frame_rewired",
        "candidate_lineage_merged",
    )
    for name in cooccurrence_flags:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"evaluation_input.{name}",
                    ConnectednessValidationCode.CO_OCCURRENCE_AUTHORITY_PROHIBITED,
                    "must be false",
                )
            )
    if value.implicit_transitive_connection_used is not False:
        issues.append(
            _issue(
                "evaluation_input.implicit_transitive_connection_used",
                ConnectednessValidationCode.INVENTED_TRANSITIVITY_PROHIBITED,
                "must be false",
            )
        )
    for name in rewrite_flags:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"evaluation_input.{name}",
                    ConnectednessValidationCode.REWRITE_PROHIBITED,
                    "must be false",
                )
            )
    for name in (
        "raw_text_supplied",
        "similarity_fallback_used",
        "hidden_model_judgment_used",
    ):
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"evaluation_input.{name}",
                    ConnectednessValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                    "must be false",
                )
            )
    if value.schema_version != SLICE40E_SCHEMA_VERSION:
        issues.append(
            _issue(
                "evaluation_input.schema_version",
                ConnectednessValidationCode.INVALID_VERSION,
                "Slice 40E schema required",
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


def validate_finding(value: object) -> ConnectednessValidationReport:
    issues = []
    if not isinstance(value, ConnectednessFinding):
        return _ordered(
            (
                _issue(
                    "finding",
                    ConnectednessValidationCode.TYPE_MISMATCH,
                    "ConnectednessFinding required",
                ),
            )
        )
    for name in ("finding_id", "evaluation_input_ref"):
        _text(getattr(value, name), f"finding.{name}", issues)
    if value.assertion_ref is not None:
        _text(value.assertion_ref, "finding.assertion_ref", issues)
    if not isinstance(value.finding_kind, ConnectednessFindingKind):
        issues.append(
            _issue(
                "finding.finding_kind",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "ConnectednessFindingKind required",
            )
        )
    if value.assertion_kind is not None and not isinstance(
        value.assertion_kind,
        ConnectednessAssertionKind,
    ):
        issues.append(
            _issue(
                "finding.assertion_kind",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "ConnectednessAssertionKind required",
            )
        )
    if not isinstance(value.authority_state, ConnectednessAuthorityState):
        issues.append(
            _issue(
                "finding.authority_state",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "ConnectednessAuthorityState required",
            )
        )
    if not isinstance(value.connection_judgment, ConnectednessJudgment):
        issues.append(
            _issue(
                "finding.connection_judgment",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "ConnectednessJudgment required",
            )
        )
    for name in (
        "supporting_refs",
        "disconnection_refs",
        "trace_refs",
        "provenance_refs",
        "reason_refs",
    ):
        _tuple(
            getattr(value, name),
            f"finding.{name}",
            issues,
            name in ("supporting_refs", "disconnection_refs"),
        )
    if value.schema_version != SLICE40E_SCHEMA_VERSION:
        issues.append(
            _issue(
                "finding.schema_version",
                ConnectednessValidationCode.INVALID_VERSION,
                "Slice 40E schema required",
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


def validate_result(value: object) -> ConnectednessValidationReport:
    issues = []
    if not isinstance(value, ConnectednessGateResult):
        return _ordered(
            (
                _issue(
                    "result",
                    ConnectednessValidationCode.TYPE_MISMATCH,
                    "ConnectednessGateResult required",
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
                ConnectednessValidationCode.INVALID_VERSION,
                "exact legacy or registry-custodied predicate/frame version required",
            )
        )
    if not isinstance(value.overall_state, ConnectednessOverallState):
        issues.append(
            _issue(
                "result.overall_state",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "ConnectednessOverallState required",
            )
        )
    if not isinstance(value.findings, tuple) or not value.findings:
        issues.append(
            _issue(
                "result.findings",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "non-empty tuple required",
            )
        )
    if isinstance(value.findings, tuple):
        for finding in value.findings:
            issues.extend(validate_finding(finding).issues)
        finding_ids = [
            finding.finding_id
            for finding in value.findings
            if isinstance(finding, ConnectednessFinding)
        ]
        if len(set(finding_ids)) != len(finding_ids):
            issues.append(
                _issue(
                    "result.findings",
                    ConnectednessValidationCode.DUPLICATE_ID,
                    "duplicate finding",
                )
            )

    counts = (
        value.connected_count,
        value.disconnected_count,
        value.ambiguous_count,
        value.unsupported_count,
        value.conflicted_count,
        value.indeterminate_count,
    )
    if (
        any(type(count) is not int or count < 0 for count in counts)
        or type(value.assertion_count) is not int
        or value.assertion_count < 1
    ):
        issues.append(
            _issue(
                "result.counts",
                ConnectednessValidationCode.TYPE_MISMATCH,
                "non-negative integer counts required",
            )
        )
    elif sum(counts) != value.assertion_count:
        issues.append(
            _issue(
                "result.counts",
                ConnectednessValidationCode.COUNT_MISMATCH,
                "counts must equal assertion count",
            )
        )
    else:
        if value.conflicted_count:
            expected_overall = ConnectednessOverallState.CONFLICTED
        elif value.unsupported_count:
            expected_overall = ConnectednessOverallState.UNSUPPORTED
        elif value.ambiguous_count:
            expected_overall = ConnectednessOverallState.AMBIGUOUS
        elif value.indeterminate_count:
            expected_overall = ConnectednessOverallState.INDETERMINATE
        elif value.disconnected_count:
            expected_overall = ConnectednessOverallState.DISCONNECTED
        else:
            expected_overall = ConnectednessOverallState.CONNECTED
        if value.overall_state is not expected_overall:
            issues.append(
                _issue(
                    "result.overall_state",
                    ConnectednessValidationCode.CROSS_RECORD_MISMATCH,
                    "overall state does not match deterministic count precedence",
                )
            )
        if isinstance(value.findings, tuple):
            per_assertion = [
                finding
                for finding in value.findings
                if isinstance(finding, ConnectednessFinding)
                and finding.assertion_ref is not None
            ]
            summary = [
                finding
                for finding in value.findings
                if isinstance(finding, ConnectednessFinding)
                and finding.assertion_ref is None
            ]
            if (
                len(per_assertion) != value.assertion_count
                or len({finding.assertion_ref for finding in per_assertion})
                != value.assertion_count
            ):
                issues.append(
                    _issue(
                        "result.findings",
                        ConnectednessValidationCode.COUNT_MISMATCH,
                        "exactly one finding per assertion required",
                    )
                )
            expected_summary = (
                1 if expected_overall is ConnectednessOverallState.CONNECTED else 0
            )
            if len(summary) != expected_summary or any(
                finding.finding_kind
                is not ConnectednessFindingKind.ALL_ASSERTIONS_CONNECTED
                for finding in summary
            ):
                issues.append(
                    _issue(
                        "result.findings",
                        ConnectednessValidationCode.CROSS_RECORD_MISMATCH,
                        "connected summary presence mismatch",
                    )
                )
            kind_counts = {
                ConnectednessFindingKind.CONNECTED_ASSERTION: value.connected_count,
                ConnectednessFindingKind.DISCONNECTED_ASSERTION: value.disconnected_count,
                ConnectednessFindingKind.AMBIGUOUS_ASSERTION: value.ambiguous_count,
                ConnectednessFindingKind.UNSUPPORTED_ASSERTION: value.unsupported_count,
                ConnectednessFindingKind.CONFLICTED_ASSERTION: value.conflicted_count,
                ConnectednessFindingKind.INDETERMINATE_AUTHORITY_ABSENT: value.indeterminate_count,
            }
            for kind, expected_count in kind_counts.items():
                observed_count = sum(
                    finding.finding_kind is kind
                    for finding in per_assertion
                )
                if observed_count != expected_count:
                    issues.append(
                        _issue(
                            "result.findings",
                            ConnectednessValidationCode.COUNT_MISMATCH,
                            f"finding count mismatch for {kind.value}",
                        )
                    )

    if (
        value.deterministic is not True
        or value.exact_connection_authority_preserved is not True
    ):
        issues.append(
            _issue(
                "result.determinism",
                ConnectednessValidationCode.EXACT_CONNECTION_AUTHORITY_REQUIRED,
                "deterministic exact connection authority required",
            )
        )

    cooccurrence_flags = (
        "cooccurrence_only_connection_used",
        "same_expression_only_connection_used",
        "same_manifest_only_connection_used",
    )
    rewrite_flags = (
        "candidate_structure_mutated",
        "source_gap_bridged",
        "ancestry_gap_bridged",
        "scope_rewritten",
        "attachment_reassigned",
        "operator_trail_rewritten",
        "predicate_frame_rewired",
        "candidate_lineage_merged",
    )
    downstream_flags = (
        "similarity_fallback_used",
        "hidden_model_judgment_used",
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
        "route_created",
        "tool_invoked",
        "action_performed",
        "memory_accessed",
        "rendered",
        "delivered",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "vector_used",
        "rag_used",
        "semantic_similarity_used",
    )
    for name in cooccurrence_flags:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"result.{name}",
                    ConnectednessValidationCode.CO_OCCURRENCE_AUTHORITY_PROHIBITED,
                    "must be false",
                )
            )
    if value.implicit_transitive_connection_used is not False:
        issues.append(
            _issue(
                "result.implicit_transitive_connection_used",
                ConnectednessValidationCode.INVENTED_TRANSITIVITY_PROHIBITED,
                "must be false",
            )
        )
    for name in rewrite_flags:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"result.{name}",
                    ConnectednessValidationCode.REWRITE_PROHIBITED,
                    "must be false",
                )
            )
    for name in downstream_flags:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"result.{name}",
                    ConnectednessValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                    "must be false",
                )
            )

    if (
        value.digest_algorithm != DIGEST_ALGORITHM
        or _SHA256.fullmatch(value.canonical_digest) is None
    ):
        issues.append(
            _issue(
                "result.canonical_digest",
                ConnectednessValidationCode.INVALID_SHA256,
                "sha256 required",
            )
        )
    elif value.canonical_digest != expected_result_digest(value):
        issues.append(
            _issue(
                "result.canonical_digest",
                ConnectednessValidationCode.IDENTITY_MISMATCH,
                "result digest mismatch",
            )
        )
    if value.result_id != f"connectedness_result:sha256:{value.canonical_digest}":
        issues.append(
            _issue(
                "result.result_id",
                ConnectednessValidationCode.IDENTITY_MISMATCH,
                "result id mismatch",
            )
        )
    if value.schema_version != SLICE40E_SCHEMA_VERSION:
        issues.append(
            _issue(
                "result.schema_version",
                ConnectednessValidationCode.INVALID_VERSION,
                "Slice 40E schema required",
            )
        )
    return _ordered(issues)


def assert_valid_evaluation_input(
    value: ConnectednessEvaluationInput,
) -> ConnectednessEvaluationInput:
    report = validate_evaluation_input(value)
    if not report.ok:
        raise ConnectednessValidationError(report)
    return value


def assert_valid_result(
    value: ConnectednessGateResult,
) -> ConnectednessGateResult:
    report = validate_result(value)
    if not report.ok:
        raise ConnectednessValidationError(report)
    return value

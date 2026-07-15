#!/usr/bin/env python3
"""Behavior tests for Slice 35D MSM-v1 canonical serialization."""

from __future__ import annotations

from dataclasses import replace
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = "aiweb_language_core_bootstrap.meaning_structure_manifest"
SERIALIZATION_MODULE = f"{PACKAGE}.serialization"
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

EXPECTED_EXPORTS = (
    "CANONICAL_FORMAT_ID",
    "CANONICAL_FORMAT_VERSION",
    "SERIALIZATION_SPEC_ID",
    "SERIALIZATION_SPEC_VERSION",
    "CanonicalSerializationError",
    "SerializationErrorCode",
    "canonical_manifest_sha256",
    "deserialize_manifest",
    "serialize_manifest",
)
EXPECTED_ROOT_EXPORTS = (
    "AUTHORITY_DOCUMENT",
    "CandidateMeaningRecord",
    "DeliveryContainmentKind",
    "DeliveryContainmentLinkRecord",
    "ExpressionLinkRecord",
    "ExternalAuthorityKind",
    "ExternalAuthorityReferenceRecord",
    "GovernedOutwardMeaningRecord",
    "GovernedResultReferenceRecord",
    "LineageOriginKind",
    "LineageRootRecord",
    "MeaningStructureManifestV1",
    "NonSelectionOutcomeKind",
    "NonSelectionOutcomeRecord",
    "PACKAGE_ID",
    "PACKAGE_NAME",
    "SCHEMA_ABBREVIATION",
    "SCHEMA_ID",
    "SCHEMA_NAME",
    "SCHEMA_VERSION",
    "SelectedGovernedMeaningRecord",
    "SemanticDirection",
    "SemanticLifecycleState",
    "SemanticPreservationClass",
    "SemanticRecordKind",
    "SemanticTransitionKind",
    "SemanticTransitionTraceRecord",
    "ValidationLinkRecord",
)
GOLDEN_SHA256 = "ef5924972982ad631f9a1e802b729c41ea029f497dcc2e2d9708ef64b468d058"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def import_probe(statement: str) -> None:
    with tempfile.TemporaryDirectory(prefix="aiweb_slice35d_import_") as tmp:
        before = tuple(sorted(Path(tmp).iterdir()))
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPATH"] = str(REPO)
        completed = subprocess.run(
            [sys.executable, "-B", "-c", statement],
            cwd=tmp,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        after = tuple(sorted(Path(tmp).iterdir()))
        require(
            completed.returncode == 0,
            f"import probe failed: {statement!r}\n{completed.stderr}",
        )
        require(before == after, "import created files or runtime state")


def make_authority(package, record_id, external_ref, authority_kind):
    return package.ExternalAuthorityReferenceRecord(
        record_id=record_id,
        lineage_id="lineage-001",
        authority_kind=authority_kind,
        external_object_ref=external_ref,
        semantic_relevance=f"bounds_{record_id}",
    )


def make_manifest(package, lifecycle):
    preservation = (
        package.SemanticPreservationClass.NEGATION,
        package.SemanticPreservationClass.UNCERTAINTY_AND_CLAIM_STRENGTH,
        package.SemanticPreservationClass.NON_LLM_PROVENANCE,
    )
    root = package.LineageRootRecord(
        lineage_id="lineage-001",
        origin_kind=package.LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION,
        origin_ref="source-event-001",
        direction=package.SemanticDirection.INWARD,
    )
    candidate = package.CandidateMeaningRecord(
        record_id="candidate-001",
        lineage_id=root.lineage_id,
        source_expression_ref=root.origin_ref,
        communicative_act="request_to_explain",
        concept_refs=("concept-001", "concept-002"),
        relation_refs=("relation-001",),
        meaning_modifiers=("bounded_scope", "not_yet_verified"),
        ambiguity_reasons=(),
        unresolved_referents=(),
        authority_sensitive_implications=("meaning_not_action",),
        preservation_classes=preservation,
    )
    authorities = (
        make_authority(
            package,
            "authority-gate",
            "gate-receipt-001",
            package.ExternalAuthorityKind.MANIFEST_CONTRACT,
        ),
        make_authority(
            package,
            "authority-result",
            "result-receipt-001",
            package.ExternalAuthorityKind.INVOCATION_EXECUTION_OR_VERIFICATION_RECEIPT,
        ),
        make_authority(
            package,
            "authority-outward",
            "outward-authority-001",
            package.ExternalAuthorityKind.MANIFEST_CONTRACT,
        ),
        make_authority(
            package,
            "authority-render",
            "render-candidate-001",
            package.ExternalAuthorityKind.RENDER_PREVIEW_OR_OUTPUT_OBJECT,
        ),
        make_authority(
            package,
            "authority-echo",
            "echo-receipt-001",
            package.ExternalAuthorityKind.RMC_ECHO_VALIDATOR_RECEIPT,
        ),
        make_authority(
            package,
            "authority-delivery",
            "delivery-receipt-001",
            package.ExternalAuthorityKind.DELIVERY_OR_CONTAINMENT_RECEIPT,
        ),
        make_authority(
            package,
            "authority-unresolved",
            "gate-unresolved-001",
            package.ExternalAuthorityKind.MANIFEST_CONTRACT,
        ),
    )
    unresolved = package.NonSelectionOutcomeRecord(
        record_id="outcome-unresolved-001",
        lineage_id=root.lineage_id,
        outcome_kind=package.NonSelectionOutcomeKind.UNRESOLVED,
        candidate_refs=(candidate.record_id,),
        reasons=("material_alternative_remains",),
        required_clarifications=(),
        external_authority_refs=("authority-unresolved",),
    )
    manifest = package.MeaningStructureManifestV1(
        manifest_id="msm-001",
        lineage_root=root,
        candidate_meanings=(candidate,),
        non_selection_outcomes=(unresolved,),
        selected_governed_meanings=(),
        governed_result_references=(),
        governed_outward_meanings=(),
        expression_links=(),
        validation_links=(),
        delivery_or_containment_links=(),
        external_authority_references=authorities,
        semantic_transition_traces=(),
    )
    selected = package.SelectedGovernedMeaningRecord(
        record_id="selected-001",
        lineage_id=root.lineage_id,
        selected_candidate_ref=candidate.record_id,
        selection_authority_ref="gate-receipt-001",
        communicative_act=candidate.communicative_act,
        concept_refs=candidate.concept_refs,
        relation_refs=candidate.relation_refs,
        meaning_modifiers=candidate.meaning_modifiers,
        inherited_limitations=("explanation_only",),
        authority_sensitive_distinctions=("selected_not_authorized",),
        preservation_classes=preservation,
    )
    step1 = lifecycle.append_lifecycle_successor(
        manifest,
        trace_record_id="trace-001",
        from_record_ref=candidate.record_id,
        successor=selected,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="deterministic_gate_selected_candidate",
        authority_reference_ref="authority-gate",
    )
    result = package.GovernedResultReferenceRecord(
        record_id="result-001",
        lineage_id=root.lineage_id,
        selected_meaning_ref=selected.record_id,
        external_authority_ref="authority-result",
        semantic_relevance="bounded_external_result",
    )
    step2 = lifecycle.append_lifecycle_successor(
        step1.manifest,
        trace_record_id="trace-002",
        from_record_ref=selected.record_id,
        successor=result,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="external_result_became_semantically_relevant",
        authority_reference_ref="authority-result",
    )
    outward = package.GovernedOutwardMeaningRecord(
        record_id="outward-001",
        lineage_id=root.lineage_id,
        outward_basis_refs=(result.record_id, "authority-outward"),
        prior_selected_meaning_ref=selected.record_id,
        permitted_claims=("the bounded result exists — Δ",),
        required_qualifications=("within external receipt scope",),
        prohibited_enlargements=("general success",),
        external_dependency_refs=("authority-outward",),
        preservation_classes=preservation,
    )
    step3 = lifecycle.append_lifecycle_successor(
        step2.manifest,
        trace_record_id="trace-003",
        from_record_ref=result.record_id,
        successor=outward,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="outward_meaning_bounded_by_result",
        authority_reference_ref="authority-outward",
    )
    expression = package.ExpressionLinkRecord(
        record_id="expression-001",
        lineage_id=root.lineage_id,
        governed_outward_meaning_ref=outward.record_id,
        expression_candidate_ref="render-candidate-001",
    )
    step4 = lifecycle.append_lifecycle_successor(
        step3.manifest,
        trace_record_id="trace-004",
        from_record_ref=outward.record_id,
        successor=expression,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="deterministic_surface_candidate_linked",
        authority_reference_ref="authority-render",
    )
    validation = package.ValidationLinkRecord(
        record_id="validation-001",
        lineage_id=root.lineage_id,
        expression_link_ref=expression.record_id,
        external_validation_receipt_ref="echo-receipt-001",
        external_validation_disposition="accepted_within_scope",
    )
    step5 = lifecycle.append_lifecycle_successor(
        step4.manifest,
        trace_record_id="trace-005",
        from_record_ref=expression.record_id,
        successor=validation,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="external_echo_receipt_linked",
        authority_reference_ref="authority-echo",
    )
    delivery = package.DeliveryContainmentLinkRecord(
        record_id="delivery-001",
        lineage_id=root.lineage_id,
        prior_link_ref=validation.record_id,
        disposition=package.DeliveryContainmentKind.DELIVERY_LINKED,
        external_receipt_ref="delivery-receipt-001",
    )
    step6 = lifecycle.append_lifecycle_successor(
        step5.manifest,
        trace_record_id="trace-006",
        from_record_ref=validation.record_id,
        successor=delivery,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="separate_delivery_receipt_linked",
        authority_reference_ref="authority-delivery",
    )
    return step6.manifest


def canonical_json(value) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def expect_error(serialization, code, payload) -> None:
    try:
        serialization.deserialize_manifest(payload)
    except serialization.CanonicalSerializationError as error:
        require(error.code is code, f"expected {code.value}, got {error.code.value}: {error}")
    else:
        raise AssertionError(f"expected {code.value}")


def main() -> int:
    import_probe(f"import {SERIALIZATION_MODULE}")
    import_probe(f"from {SERIALIZATION_MODULE} import *")

    package = importlib.import_module(PACKAGE)
    lifecycle = importlib.import_module(f"{PACKAGE}.lifecycle")
    validation = importlib.import_module(f"{PACKAGE}.validation")
    serialization = importlib.import_module(SERIALIZATION_MODULE)

    require(serialization.__all__ == EXPECTED_EXPORTS, "serialization __all__ mismatch")
    star: dict[str, object] = {}
    exec(f"from {SERIALIZATION_MODULE} import *", star, star)
    star_names = tuple(sorted(name for name in star if name != "__builtins__"))
    require(star_names == tuple(sorted(EXPECTED_EXPORTS)), "star import mismatch")
    for name in EXPECTED_EXPORTS:
        require(star[name] is getattr(serialization, name), f"export identity mismatch: {name}")

    require(package.__all__ == EXPECTED_ROOT_EXPORTS, "root package exports changed")
    require("serialize_manifest" not in package.__all__, "root export surface expanded")
    require(not any("migrat" in name.lower() for name in serialization.__all__), "migration export present")
    require(not any("upgrade" in name.lower() for name in serialization.__all__), "upgrade export present")

    manifest = make_manifest(package, lifecycle)
    require(validation.validate_manifest(manifest).ok, "fixture manifest invalid")

    payload1 = serialization.serialize_manifest(manifest)
    payload2 = serialization.serialize_manifest(manifest)
    require(type(payload1) is bytes, "serializer did not return bytes")
    require(payload1 == payload2, "serialization is not deterministic")
    require(payload1 == payload1.strip(), "canonical payload contains surrounding whitespace")
    payload1.decode("ascii")

    decoded_bytes = serialization.deserialize_manifest(payload1)
    decoded_text = serialization.deserialize_manifest(payload1.decode("ascii"))
    require(decoded_bytes == manifest, "byte round-trip mismatch")
    require(decoded_text == manifest, "text round-trip mismatch")
    require(hash(decoded_bytes) == hash(manifest), "round-trip hash mismatch")
    require(serialization.serialize_manifest(decoded_bytes) == payload1, "round-trip bytes changed")

    digest = serialization.canonical_manifest_sha256(manifest)
    require(digest == serialization.canonical_manifest_sha256(decoded_bytes), "digest changed")
    require(len(digest) == 64 and all(char in "0123456789abcdef" for char in digest), "digest format invalid")
    if GOLDEN_SHA256 != "TO_BE_FILLED":
        require(digest == GOLDEN_SHA256, f"golden digest drift: {digest}")

    parsed = json.loads(payload1)
    require(canonical_json(parsed) == payload1, "payload is not canonical JSON")
    require(parsed["canonical_format"] == serialization.CANONICAL_FORMAT_ID, "format id missing")
    require(parsed["canonical_format_version"] == serialization.CANONICAL_FORMAT_VERSION, "format version missing")
    require(parsed["schema_version"] == package.SCHEMA_VERSION, "envelope schema version missing")
    require(parsed["manifest"]["schema_version"] == package.SCHEMA_VERSION, "manifest schema version missing")
    require(parsed["manifest"]["record_kind"] == "meaning_structure_manifest", "manifest kind missing")
    require(len(parsed["manifest"]["semantic_transition_traces"]) == 6, "trace serialization incomplete")
    require(len(parsed["manifest"]["external_authority_references"]) == 7, "authority serialization incomplete")
    require(len(parsed["manifest"]["non_selection_outcomes"]) == 1, "non-selection serialization incomplete")
    require(b"\\u0394" in payload1, "non-ASCII text was not escaped canonically")

    code = serialization.SerializationErrorCode
    expect_error(serialization, code.PAYLOAD_TYPE_INVALID, bytearray(payload1))
    expect_error(serialization, code.PAYLOAD_UTF8_INVALID, b"\xff")
    expect_error(serialization, code.JSON_INVALID, b"{")
    expect_error(
        serialization,
        code.DUPLICATE_KEY,
        b'{"canonical_format":"a","canonical_format":"b"}',
    )
    expect_error(serialization, code.NON_CANONICAL_PAYLOAD, b"\xef\xbb\xbf" + payload1)
    pretty = json.dumps(parsed, ensure_ascii=True, sort_keys=True, indent=2).encode("ascii")
    expect_error(serialization, code.NON_CANONICAL_PAYLOAD, pretty)
    expect_error(serialization, code.NON_CANONICAL_PAYLOAD, payload1 + b"\n")

    mutated = json.loads(payload1)
    mutated["canonical_format"] = "unknown-format"
    expect_error(serialization, code.CANONICAL_FORMAT_UNSUPPORTED, canonical_json(mutated))

    mutated = json.loads(payload1)
    mutated["canonical_format_version"] = "2"
    expect_error(serialization, code.CANONICAL_FORMAT_VERSION_UNSUPPORTED, canonical_json(mutated))

    mutated = json.loads(payload1)
    mutated["package_id"] = "other-package"
    expect_error(serialization, code.PACKAGE_ID_INCOMPATIBLE, canonical_json(mutated))

    mutated = json.loads(payload1)
    mutated["schema_id"] = "other-schema"
    expect_error(serialization, code.SCHEMA_ID_INCOMPATIBLE, canonical_json(mutated))

    mutated = json.loads(payload1)
    mutated["schema_version"] = "MSM-v2"
    expect_error(serialization, code.SCHEMA_VERSION_UNSUPPORTED, canonical_json(mutated))

    mutated = json.loads(payload1)
    mutated["manifest"]["schema_version"] = "MSM-v0"
    expect_error(serialization, code.SCHEMA_VERSION_UNSUPPORTED, canonical_json(mutated))

    mutated = json.loads(payload1)
    mutated["unexpected"] = "field"
    expect_error(serialization, code.UNKNOWN_FIELD, canonical_json(mutated))

    mutated = json.loads(payload1)
    del mutated["schema_id"]
    expect_error(serialization, code.MISSING_FIELD, canonical_json(mutated))

    mutated = json.loads(payload1)
    mutated["manifest"]["candidate_meanings"][0]["preservation_classes"][0] = "not-a-class"
    expect_error(serialization, code.ENUM_VALUE_UNKNOWN, canonical_json(mutated))

    mutated = json.loads(payload1)
    mutated["manifest"]["candidate_meanings"] = {}
    expect_error(serialization, code.ARRAY_REQUIRED, canonical_json(mutated))

    mutated = json.loads(payload1)
    mutated["manifest"]["candidate_meanings"][0]["lifecycle_state"] = "unsupported"
    expect_error(serialization, code.FIXED_VALUE_MISMATCH, canonical_json(mutated))

    mutated = json.loads(payload1)
    mutated["manifest"]["candidate_meanings"][0]["source_expression_ref"] = "other-source"
    expect_error(serialization, code.MANIFEST_VALIDATION_FAILED, canonical_json(mutated))

    mutated = json.loads(payload1)
    first_trace = mutated["manifest"]["semantic_transition_traces"][0]
    first_trace["from_record_ref"] = "candidate-001"
    first_trace["to_record_ref"] = "delivery-001"
    first_trace["from_state"] = "candidate_meaning"
    first_trace["to_state"] = "delivery_linked"
    first_trace["transition_kind"] = "ancestry"
    first_trace["authority_reference_ref"] = "authority-delivery"
    expect_error(serialization, code.LIFECYCLE_HISTORY_INVALID, canonical_json(mutated))

    invalid_manifest = replace(manifest, manifest_id=" invalid ")
    try:
        serialization.serialize_manifest(invalid_manifest)
    except serialization.CanonicalSerializationError as error:
        require(error.code is code.MANIFEST_VALIDATION_FAILED, "invalid serializer error code")
    else:
        raise AssertionError("invalid manifest serialized")

    print("SLICE 35D BEHAVIOR TEST: PASS")
    print(f"serialization_module={SERIALIZATION_MODULE}")
    print(f"serialization_exports={len(serialization.__all__)}")
    print(f"canonical_bytes={len(payload1)}")
    print(f"canonical_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

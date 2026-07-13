"""Static accepted-component registry for the isolated bootstrap boundary.

Slice 30 registers source identities only. It does not import or load any
accepted component package.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .schema import (
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    issue,
    require_false,
    require_non_empty_text,
    stable_record_id,
)

REGISTRY_STATE = "registered_not_loaded"

_COMPONENT_SPECS: tuple[
    tuple[str, str, str, int, str],
    ...,
] = (
    (
        "Slice 7",
        "aiweb_meaning_law_trace_scaffold",
        "c8ca2f959815d9d4f4b947b635dcd499ce54f30562d204f99aa86e8384568e38",
        4,
        "Meaning-object and law-trace record boundary; no truth or runtime authority.",
    ),
    (
        "Slice 8",
        "aiweb_concept_boundary_scaffold",
        "28843077cf64aeb7f6f455eb6cec313f35ab5004c803ed03a02824f43357de01",
        4,
        "Concept and relation boundary; concepts are not evidence or selected meaning.",
    ),
    (
        "Slice 9",
        "aiweb_predicate_role_boundary_scaffold",
        "88feda8338f8b7927ad041886fe1ca99bd211fdc7ea261faf69b2b5333e8faf3",
        6,
        "Predicate, role, speech-act and effect boundary; frames are not execution.",
    ),
    (
        "Slice 10",
        "aiweb_verbal_cognition_gate_boundary_scaffold",
        "308385c90974885c5b13b2422f7df1d9253db35717bef80a1e4cd3e9b10b51f5",
        6,
        "Gate-state record boundary; gate output is not routing or action.",
    ),
    (
        "Slice 11",
        "aiweb_candidate_meaning_boundary_scaffold",
        "3eda1f92198049b1c71ab59878a79587995d29e8508ca5f8780aabaa6dcb7656",
        7,
        "Source custody and candidate-meaning boundary; candidate is not selected meaning.",
    ),
    (
        "Slice 12",
        "aiweb_ambiguity_clarification_boundary_scaffold",
        "290936f9ffeba047d06a61e32135f580505e6937597cd052dde6ee03d2b29b1f",
        6,
        "Ambiguity, unknown, unsupported, deferred and clarification states.",
    ),
    (
        "Slice 13",
        "aiweb_requirements_traceability_scaffold",
        "0c7872dc5456b807af37fb64260f99d76a94ad4e003be952dc562309f0b8ded9",
        7,
        "Requirement-to-test traceability records only.",
    ),
    (
        "Slice 14",
        "aiweb_external_resource_quarantine_scaffold",
        "cf22c2744ac28d6af6305b47d7c95ca0b9ae2005c0f4727b7e80fca23fb594fe",
        9,
        "External-resource quarantine and refusal; no resource is admitted.",
    ),
    (
        "Slice 15",
        "aiweb_corpus_evidence_memory_trace_scaffold",
        "76b7e6d15043b6ce64553b87371d2734ab5e8312133d2b569ae21cfa611cfd47",
        11,
        "Corpus, evidence, memory and trace separation; no persistent authority.",
    ),
    (
        "Slice 16",
        "aiweb_selected_meaning_boundary_scaffold",
        "06950bcdd18bda2be35d9d404ebd15de4248c4fabfc8133367e8057411f42153",
        9,
        "Selected-meaning custody boundary; selection is not truth.",
    ),
    (
        "Slice 17",
        "aiweb_output_expression_boundary_scaffold",
        "6f5d65a97630d14ba2e590bbc219e754fea8ae7698ee01ce2db17be0e65003a1",
        9,
        "Expression-source and preview boundary; expression is not delivery.",
    ),
    (
        "Slice 18",
        "aiweb_gp014_preservation_decision_scaffold",
        "dfeb9a016bde775cda62a0835972a3c99f7f86f2dc6eb6780c3641063044fdca",
        6,
        "GP-014 preservation decision records only; no import, call or wrapper.",
    ),
    (
        "Slice 19",
        "aiweb_rmc_echo_boundary_scaffold",
        "edf319c1b5044fdf67404a4a129e3d0114658f5aedc6d6d05b4c18323b9da7b3",
        6,
        "Deterministic Echo validation and non-authority boundary.",
    ),
    (
        "Slice 20",
        "aiweb_delivery_action_tool_routing_boundary_scaffold",
        "bec6e6f1fe84f1641a8d8d2bda93d7fbe2445d8abf312af644610f6d29777a98",
        6,
        "Delivery, action and tool-routing refusal boundary.",
    ),
    (
        "Slice 21",
        "aiweb_read_only_inspection_surface_scaffold",
        "a8639119735f89852ca2ec5d750cfb442a06fdccc1e3a58d0b91d69a6765c42c",
        6,
        "Read-only inspection boundary; inspection is not runtime authority.",
    ),
)

_EXPECTED_COMPONENTS_BY_NAME = {
    package_name: (
        slice_ref,
        package_name,
        package_digest,
        file_count,
        accepted_scope,
    )
    for (
        slice_ref,
        package_name,
        package_digest,
        file_count,
        accepted_scope,
    ) in _COMPONENT_SPECS
}

PROHIBITED_RUNTIME_COMPONENTS = (
    "aiweb_end_to_end_dry_run_harness_scaffold",
    "aiweb_full_regression_acceptance_bundle_scaffold",
)


@dataclass(frozen=True, slots=True)
class ComponentRegistrationRecord:
    component_registration_id: str
    slice_ref: str
    package_name: str
    package_digest: str
    file_count: int
    accepted_scope: str
    registry_state: str
    runtime_import_authorized: bool
    component_loaded: bool
    schema_version: str = SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("component_registration_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "bootstrap_component",
            self.canonical_body(),
        )


@dataclass(frozen=True, slots=True)
class ComponentRegistryRecord:
    registry_id: str
    components: tuple[ComponentRegistrationRecord, ...]
    registry_state: str
    component_count: int
    components_loaded: bool
    dynamic_discovery_allowed: bool
    schema_version: str = SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        return {
            "components": tuple(
                component.canonical_body()
                | {
                    "component_registration_id":
                        component.component_registration_id
                }
                for component in self.components
            ),
            "registry_state": self.registry_state,
            "component_count": self.component_count,
            "components_loaded": self.components_loaded,
            "dynamic_discovery_allowed": self.dynamic_discovery_allowed,
            "schema_version": self.schema_version,
        }

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_registry", self.canonical_body())


def build_component_registration_record(
    *,
    slice_ref: str,
    package_name: str,
    package_digest: str,
    file_count: int,
    accepted_scope: str,
) -> ComponentRegistrationRecord:
    body = {
        "slice_ref": slice_ref,
        "package_name": package_name,
        "package_digest": package_digest,
        "file_count": file_count,
        "accepted_scope": accepted_scope,
        "registry_state": REGISTRY_STATE,
        "runtime_import_authorized": False,
        "component_loaded": False,
        "schema_version": SCHEMA_VERSION,
    }
    return ComponentRegistrationRecord(
        component_registration_id=stable_record_id(
            "bootstrap_component",
            body,
        ),
        **body,
    )


def build_component_registry_record() -> ComponentRegistryRecord:
    components = tuple(
        build_component_registration_record(
            slice_ref=slice_ref,
            package_name=package_name,
            package_digest=package_digest,
            file_count=file_count,
            accepted_scope=accepted_scope,
        )
        for (
            slice_ref,
            package_name,
            package_digest,
            file_count,
            accepted_scope,
        ) in _COMPONENT_SPECS
    )
    body = {
        "components": tuple(
            component.canonical_body()
            | {
                "component_registration_id":
                    component.component_registration_id
            }
            for component in components
        ),
        "registry_state": REGISTRY_STATE,
        "component_count": len(components),
        "components_loaded": False,
        "dynamic_discovery_allowed": False,
        "schema_version": SCHEMA_VERSION,
    }
    return ComponentRegistryRecord(
        registry_id=stable_record_id("bootstrap_registry", body),
        components=components,
        registry_state=REGISTRY_STATE,
        component_count=len(components),
        components_loaded=False,
        dynamic_discovery_allowed=False,
        schema_version=SCHEMA_VERSION,
    )


def validate_component_registration_record(
    record: ComponentRegistrationRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    require_non_empty_text(
        field="slice_ref",
        value=record.slice_ref,
        issues=issues,
    )
    require_non_empty_text(
        field="package_name",
        value=record.package_name,
        issues=issues,
    )
    require_non_empty_text(
        field="accepted_scope",
        value=record.accepted_scope,
        issues=issues,
    )

    if record.schema_version != SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.registry_state != REGISTRY_STATE:
        issues.append(issue("registry_state", "unsupported_registry_state"))
    if not isinstance(record.file_count, int) or record.file_count <= 0:
        issues.append(issue("file_count", "required_positive_integer"))
    if (
        not isinstance(record.package_digest, str)
        or len(record.package_digest) != 64
        or any(char not in "0123456789abcdef" for char in record.package_digest)
    ):
        issues.append(issue("package_digest", "invalid_sha256"))
    if record.package_name in PROHIBITED_RUNTIME_COMPONENTS:
        issues.append(issue("package_name", "evidence_component_not_runtime_component"))
    if record.package_name.startswith(
        ("main", "agents.forge", "rmc_engine_v1", "forge.rmc_engine_v1")
    ):
        issues.append(issue("package_name", "prohibited_runtime_prefix"))

    if record.package_name not in _EXPECTED_COMPONENTS_BY_NAME:
        issues.append(issue("package_name", "unrecognized_component"))
    else:
        expected = _EXPECTED_COMPONENTS_BY_NAME[record.package_name]
        (
            expected_slice_ref,
            expected_package_name,
            expected_package_digest,
            expected_file_count,
            expected_accepted_scope,
        ) = expected
        if record.slice_ref != expected_slice_ref:
            issues.append(issue("slice_ref", "component_identity_mismatch"))
        if record.package_name != expected_package_name:
            issues.append(issue("package_name", "component_identity_mismatch"))
        if record.package_digest != expected_package_digest:
            issues.append(issue("package_digest", "component_identity_mismatch"))
        if record.file_count != expected_file_count:
            issues.append(issue("file_count", "component_identity_mismatch"))
        if record.accepted_scope != expected_accepted_scope:
            issues.append(issue("accepted_scope", "component_identity_mismatch"))

    require_false(
        field="runtime_import_authorized",
        value=record.runtime_import_authorized,
        issues=issues,
    )
    require_false(
        field="component_loaded",
        value=record.component_loaded,
        issues=issues,
    )
    if record.component_registration_id != record.expected_id():
        issues.append(
            issue(
                "component_registration_id",
                "stable_identifier_mismatch",
            )
        )

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_component_registry_record(
    record: ComponentRegistryRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if record.schema_version != SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.registry_state != REGISTRY_STATE:
        issues.append(issue("registry_state", "unsupported_registry_state"))
    if record.component_count != len(_COMPONENT_SPECS):
        issues.append(issue("component_count", "unexpected_component_count"))
    if record.component_count != len(record.components):
        issues.append(issue("component_count", "component_count_mismatch"))
    require_false(
        field="components_loaded",
        value=record.components_loaded,
        issues=issues,
    )
    require_false(
        field="dynamic_discovery_allowed",
        value=record.dynamic_discovery_allowed,
        issues=issues,
    )

    package_names = tuple(
        component.package_name for component in record.components
    )
    expected_names = tuple(spec[1] for spec in _COMPONENT_SPECS)
    if package_names != expected_names:
        issues.append(issue("components", "component_set_or_order_mismatch"))
    if len(package_names) != len(set(package_names)):
        issues.append(issue("components", "duplicate_component"))

    actual_component_identities = tuple(
        (
            component.slice_ref,
            component.package_name,
            component.package_digest,
            component.file_count,
            component.accepted_scope,
        )
        for component in record.components
    )
    if actual_component_identities != _COMPONENT_SPECS:
        issues.append(
            issue(
                "components",
                "component_identity_set_or_order_mismatch",
            )
        )

    for component in record.components:
        report = validate_component_registration_record(component)
        for component_issue in report.issues:
            issues.append(
                issue(
                    f"components.{component.package_name}.{component_issue.field}",
                    component_issue.code,
                    component_issue.detail,
                )
            )

    if record.registry_id != record.expected_id():
        issues.append(issue("registry_id", "stable_identifier_mismatch"))

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )

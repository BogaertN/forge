from __future__ import annotations

from dataclasses import replace
import ast
from pathlib import Path
from typing import List, Tuple

from .core import (
    EXPRESSION_FALSE_ONLY_FIELDS,
    REQUIRED_EXPRESSION_LAWS,
    expression_scope_record,
    text_sha256,
)
from .expression_plan import (
    build_expression_plan_record,
    demo_expression_plan_record,
    validate_expression_plan_record,
)
from .expression_preview import (
    ExpressionPreviewRecord,
    render_expression_preview,
    validate_expression_preview_record,
)
from .expression_receipt import (
    RECEIPT_EFFECT,
    build_expression_receipt_record,
    validate_expression_receipt_record,
)
from .expression_source import (
    demo_expression_source_record,
    validate_expression_source_record,
)
from .fidelity import evaluate_expression_fidelity, validate_expression_fidelity_record
from .preservation_contract import (
    build_expression_preservation_contract,
    demo_expression_preservation_contract,
    validate_expression_preservation_contract,
)

PACKAGE_PATHS = (
    "aiweb_output_expression_boundary_scaffold/__init__.py",
    "aiweb_output_expression_boundary_scaffold/core.py",
    "aiweb_output_expression_boundary_scaffold/expression_source.py",
    "aiweb_output_expression_boundary_scaffold/preservation_contract.py",
    "aiweb_output_expression_boundary_scaffold/expression_plan.py",
    "aiweb_output_expression_boundary_scaffold/expression_preview.py",
    "aiweb_output_expression_boundary_scaffold/fidelity.py",
    "aiweb_output_expression_boundary_scaffold/expression_receipt.py",
    "aiweb_output_expression_boundary_scaffold/verify.py",
    "scripts/test_aiweb_slice17_output_expression_boundary_scaffold.py",
    "scripts/aiweb_slice17_output_expression_boundary_verify.py",
    "scripts/README_aiweb_slice17_output_expression_boundary_scaffold.md",
)

FORBIDDEN_DEPENDENCY_TEXT = (
    "rmc_engine_v1.output_renderer",
    "rmc_engine_v1.renderer",
    "gp014_operator_guided_language_realizer",
    "symbolic_math_operator_language_realizer",
    "gp015_ask_forge_trace_surface",
    "rmc_engine_v1.llm_renderer",
    "rmc_engine_v1.chroma_connector",
    "openai",
    "chromadb",
    "requests",
    "urllib.request",
)


def _mutated_preview(preview: ExpressionPreviewRecord, old: str, new: str) -> ExpressionPreviewRecord:
    changed = preview.preview_text.replace(old, new)
    return replace(
        preview,
        preview_text=changed,
        preview_text_hash=text_sha256(changed),
        expression_preview_id="expression-preview:mutated",
    )


def _demo_pipeline():
    source = demo_expression_source_record()
    contract = demo_expression_preservation_contract(
        source.expression_source_id, source.selected_meaning_id
    )
    plan = demo_expression_plan_record(
        expression_source_id=source.expression_source_id,
        preservation_contract_id=contract.preservation_contract_id,
        selected_meaning_id=source.selected_meaning_id,
        selected_meaning_status=source.selected_meaning_status,
    )
    preview = render_expression_preview(plan)
    fidelity = evaluate_expression_fidelity(source, contract, plan, preview)
    receipt = build_expression_receipt_record(
        fidelity,
        preview_status=preview.preview_status,
        audit_note="Slice 17 structural receipt only.",
    )
    return source, contract, plan, preview, fidelity, receipt


def run_verification(repo: Path) -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []

    def check(label: str, condition: bool) -> None:
        (passes if condition else failures).append(label)

    for rel in PACKAGE_PATHS:
        check(f"required path exists: {rel}", (repo / rel).is_file())

    scope = expression_scope_record()
    check("scope schema present", bool(scope.get("schema_version")))
    check("scope has no runtime effect", scope.get("runtime_effect") == "none")
    check("scope keeps GP-014 protected", scope.get("gp014_status") == "protected_not_imported_not_superseded")
    check("scope keeps GP-015 failed", scope.get("gp015_status") == "failed_not_repaired")
    check("scope keeps frozen legacy evidence-only", scope.get("frozen_legacy_status") == "evidence_only_not_imported_not_called")
    for field in EXPRESSION_FALSE_ONLY_FIELDS:
        check(f"scope blocks {field}", scope.get(field) is False)
    for law in REQUIRED_EXPRESSION_LAWS:
        check(f"scope carries law {law}", law in scope.get("required_expression_laws", ()))

    source, contract, plan, preview, fidelity, receipt = _demo_pipeline()
    check("expression source validates", validate_expression_source_record(source).ok)
    check("preservation contract validates", validate_expression_preservation_contract(contract).ok)
    check("expression plan validates", validate_expression_plan_record(plan).ok)
    check("expression preview validates", validate_expression_preview_record(preview).ok)
    check("expression fidelity validates", validate_expression_fidelity_record(fidelity).ok)
    check("expression receipt validates", validate_expression_receipt_record(receipt).ok)
    check("source ID stable", source.expression_source_id == source.expected_id())
    check("contract ID stable", contract.preservation_contract_id == contract.expected_id())
    check("plan ID stable", plan.expression_plan_id == plan.expected_id())
    check("preview ID stable", preview.expression_preview_id == preview.expected_id())
    check("fidelity ID stable", fidelity.expression_fidelity_id == fidelity.expected_id())
    check("receipt ID stable", receipt.expression_receipt_id == receipt.expected_id())
    check("all hard fidelity checks pass", fidelity.hard_gate_pass)
    check("receipt is structural only", receipt.receipt_effect == RECEIPT_EFFECT)
    check("preview remains unapproved", preview.preview_status == "unapproved_expression_preview_boundary")

    adversarial = {
        "negation removal rejected": _mutated_preview(preview, "not authorized", "authorized"),
        "condition removal rejected": _mutated_preview(preview, "only if checksum verification passes", "after checksum verification"),
        "modality strengthening rejected": _mutated_preview(preview, "may proceed", "will proceed"),
        "attribution removal rejected": _mutated_preview(preview, "According to the operator, ", ""),
        "scope widening rejected": _mutated_preview(preview, "the system", "all systems"),
        "refusal relevance removal rejected": _mutated_preview(preview, "not authorized", "unavailable"),
        "uncertainty removal rejected": _mutated_preview(preview, "uncertainty remains", "the result is clear"),
        "forbidden proof claim rejected": _mutated_preview(preview, "Explanation preview:", "Explanation preview: This proves"),
        "missing disclaimer rejected": _mutated_preview(preview, preview.disclaimer, ""),
    }
    expected_failed_ref = {
        "negation removal rejected": "negation_preservation",
        "condition removal rejected": "condition_preservation",
        "modality strengthening rejected": "modality_non_strengthening",
        "attribution removal rejected": "attribution_preservation",
        "scope widening rejected": "scope_non_widening",
        "refusal relevance removal rejected": "refusal_relevance_preservation",
        "uncertainty removal rejected": "uncertainty_preservation",
        "forbidden proof claim rejected": "forbidden_claim_absence",
        "missing disclaimer rejected": "non_authority_disclaimer",
    }
    for label, mutated in adversarial.items():
        result = evaluate_expression_fidelity(source, contract, plan, mutated)
        check(label, not result.hard_gate_pass and expected_failed_ref[label] in result.failed_check_refs)

    metadata_mutations = (
        ("preview kind tampering rejected", replace(preview, preview_kind="status_preview")),
        ("template tampering rejected", replace(preview, template_id="slice17.status.v1")),
        ("qualifier custody tampering rejected", replace(preview, preserved_qualifier_markers=("different",))),
    )
    for label, mutated in metadata_mutations:
        result = evaluate_expression_fidelity(source, contract, plan, mutated)
        check(label, not result.hard_gate_pass and "source_binding" in result.failed_check_refs)

    check(
        "source snapshot hash mutation rejected",
        not validate_expression_source_record(
            replace(source, normalized_text_snapshot=source.normalized_text_snapshot + " altered")
        ).ok,
    )
    check(
        "silent preservation dimension rejected",
        not validate_expression_preservation_contract(
            replace(contract, negation_markers=())
        ).ok,
    )
    check(
        "not-applicable dimension requires reason",
        not validate_expression_preservation_contract(
            replace(contract, negation_state="explicit_not_applicable", negation_markers=("none",))
        ).ok,
    )

    status_cases = (
        ("selected_meaning_boundary_recorded", "explanation_preview", True),
        ("selected_meaning_boundary_recorded", "refusal_preview", False),
        ("selection_held_boundary", "held_preview", True),
        ("selection_held_boundary", "explanation_preview", False),
        ("selection_blocked_boundary", "blocked_preview", True),
        ("selection_blocked_boundary", "status_preview", False),
        ("selection_refused_boundary", "refusal_preview", True),
        ("selection_refused_boundary", "explanation_preview", False),
    )
    for status, kind, expected in status_cases:
        case = build_expression_plan_record(
            expression_source_id="expression-source:status",
            preservation_contract_id="expression-preservation:status",
            selected_meaning_id="selected-meaning:status",
            selected_meaning_status=status,
            preview_kind=kind,
            clause_sequence=("Boundary status remains explicit.",),
            source_refs=("selected-meaning:status",),
            required_qualifier_markers=("Boundary status remains explicit",),
            forbidden_transformations=("change_status",),
        )
        check(
            f"status mapping {status} -> {kind} is {expected}",
            validate_expression_plan_record(case).ok is expected,
        )

    false_only_mutations = (
        (source, "truth_decision", validate_expression_source_record),
        (contract, "model_authority", validate_expression_preservation_contract),
        (plan, "tool_invocation", validate_expression_plan_record),
        (preview, "output_approval", validate_expression_preview_record),
        (fidelity, "acceptance_effect", validate_expression_fidelity_record),
        (receipt, "delivery_action", validate_expression_receipt_record),
    )
    for record, field, validator in false_only_mutations:
        changed = replace(record, **{field: True})
        check(f"false-only field rejected: {field}", not validator(changed).ok)

    for rel in PACKAGE_PATHS:
        if not rel.endswith(".py"):
            continue
        source_text = (repo / rel).read_text(encoding="utf-8")
        try:
            tree = ast.parse(source_text, filename=str(repo / rel))
        except SyntaxError:
            check(f"{rel} Python syntax is valid for import scan", False)
            continue
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        for forbidden in FORBIDDEN_DEPENDENCY_TEXT:
            check(
                f"{rel} omits forbidden import {forbidden}",
                all(not name.startswith(forbidden) for name in imported),
            )

    return passes, failures

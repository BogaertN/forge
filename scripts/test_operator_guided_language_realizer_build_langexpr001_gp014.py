#!/usr/bin/env python3
"""LANG-EXPR-001 / GP-014 behavior verification: operator-guided expression remains Echo-governed."""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
if str(FORGE) not in sys.path:
    sys.path.insert(0, str(FORGE))

from rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer import activate
from rmc_engine_v1.general_pipeline.symbolic_math_language_vertical_slice import answer_symbolic_math_language_request
from rmc_engine_v1.general_pipeline.symbolic_math_operator_language_realizer import operator_guided_language_realizer_boundary

checks = []
def check(name, condition):
    checks.append((name, bool(condition)))
    if not condition:
        print(f"FAIL: {name}")

state = activate()
check("GP-014 activation active", state["active"] is True and "LANG-EXPR-001-GP-014" in state["build_id"])
check("GP-014 extends existing GP-013 delivery spine", state["extends_installed_gp013_actual_echo_vertical_slice"] is True)
check("GP-014 cannot grant delivery", state["delivery_authority_added"] is False)
check("GP-014 requires actual Echo", state["actual_echo_delivery_required"] is True)
check("GP-014 does not add UI route", state["adds_route_or_ui"] is False)
check("GP-014 uses no corpus LLM memory or economy", not any(state[key] for key in ("corpus_ingestion_added", "calls_llm", "writes_memory", "writes_identity_vault", "writes_contribution_economy", "mints_ct", "writes_ledgers")))

boundary = operator_guided_language_realizer_boundary()
check("bounded expression lexicon is not a corpus", boundary["expression_lexicon_authority_class"] == "BOUNDED_VERSIONED_EXPRESSION_LEXICON_NOT_CORPUS")
check("operator-guided layer covers existing eight families", boundary["supported_operation_family_count"] == 8)
check("operator-guided layer uses finite generative means", boundary["finite_means_generate_multiple_surface_candidates"] is True)
check("operator-guided layer builds hierarchical clause trees", boundary["hierarchical_clause_tree_generated"] is True)
check("operator-guided layer uses FBSC crosswalk read-only", boundary["uses_fbsc_operator_crosswalk_read_only"] is True)
check("operator-guided layer computes candidate scores from installed measurement kernel", boundary["uses_installed_measurement_kernel"] is True and boundary["candidate_scores_are_computed_not_lexicon_awarded"] is True)
check("operator-guided layer does not activate MEA preview operator engine", boundary["activates_preview_mea_operator_engine"] is False)
check("operator-guided layer does not use historical preview renderer", boundary["uses_historical_renderer_preview_lane"] is False)
check("operator-guided layer cannot self-authorize", boundary["actual_echo_invoked_here"] is False and boundary["delivery_authority_created_here"] is False)

# One end-to-end non-fixture path proves selected language still reaches real Echo delivery.
result = answer_symbolic_math_language_request("Differentiate x^3 + 4*x with respect to x.")
check("end-to-end result delivered", result.status == "ANSWERED")
trace = result.trace
receipt = trace["expression_realization_receipt"]
check("trace carries realization receipt hash", len(trace["expression_realization_receipt_hash"]) == 64)
check("realizer generated multiple candidate sentences", len(receipt["candidates"]) >= 3 and receipt["accepted_candidate_count"] >= 3)
check("selected expression text equals rendered text", receipt["selected_text"] == trace["rendered_text"] == result.answer_text)
check("realizer has no Echo authority", receipt["actual_echo_invoked"] is False and receipt["delivery_authorized"] is False)
check("selected candidate is pending Echo only", receipt["render_preview_only_until_echo"] is True)
check("selected language preserves exact result", trace["solution"]["answer_text"] in receipt["selected_text"])
check("selected language preserves source expression", "x^3 + 4*x" in receipt["selected_text"])
check("selected language preserves verification strength text", trace["solution"]["verification_text"] in receipt["selected_text"])
check("actual Echo approves selected candidate", trace["echo"]["approved_output"] is True)
check("actual DeliveryAuthorizationReceiptV2 remains final", trace["delivery_authorization_v2"]["delivery_status"] == "ECHO_APPROVED_DELIVERY_AUTHORIZED")
check("required operator path is recorded", [row["glyph"] for row in receipt["operator_path"]] == ["⧙", "⟁", "ΔΦ", "⧧", "⧀"])
check("operators do not assert delivery", all(row["authorizes_delivery"] is False for row in receipt["operator_path"]))
check("phase transition metrics authorize legal externalization order", receipt["phase_transition_metrics"]["phase_path_legal"] is True and receipt["phase_transition_metrics"]["phase_path"] == ["Φ6", "Φ7", "Φ8"])
check("phase externalization binds naming before projection", [row["normalized_phase_id"] for row in receipt["phase_externalization_path"]] == ["Φ6", "Φ7", "Φ8"])
check("every candidate carries hierarchical clause tree", all(len(row["clause_tree"]) == 4 for row in receipt["candidates"]))
check("candidate receipts carry real measured readings", all(row["measurement_readings"]["uses_installed_measurement_kernel"] is True and "semantic_distance" in row["measurement_readings"] and "drift_severity_D_score" in row["measurement_readings"] and "symbolic_epsilon_s" in row["measurement_readings"] for row in receipt["candidates"]))
check("FBSC operators execute traceable measurement roles", all(all(glyph in row["operator_measurements"] for glyph in ["⧙", "⟁", "ΔΦ", "⧧", "⧀"]) for row in receipt["candidates"]))
check("lexical selection has a published computed formula", receipt["scoring_formula"].startswith("0.34*meaning_fidelity"))
check("every accepted candidate locks required atoms", all(all(row["hard_gate_checks"].values()) for row in receipt["candidates"] if not row["rejected_reasons"]))
check("candidate selection is traceable", any(row["candidate_hash"] == receipt["selected_candidate_hash"] for row in receipt["candidates"]))
check("selected candidate is highest deterministic lawful score", receipt["selected_candidate_hash"] == sorted([row for row in receipt["candidates"] if not row["rejected_reasons"]], key=lambda row: (-row["final_score"], row["surface_template_id"], row["candidate_hash"]))[0]["candidate_hash"])

# Existing compilation refusal still prevents downstream language generation.
refused = answer_symbolic_math_language_request("Factor x^2 - 9 and publish it.")
check("unsafe widened request remains refused", refused.status == "REFUSED_UNLEARNED")
check("refused request receives no expression candidate or delivery", "expression_realization_receipt" not in refused.trace and "delivery_authorization_v2" not in refused.trace)

attestation = {
    "build_id": state["build_id"],
    "status": "LANG_EXPR001_GP014_OPERATOR_GUIDED_EXPRESSION_ATTESTED_PENDING_ACTUAL_ECHO_THEN_DELIVERED",
    "renderer_boundary": boundary,
    "differentiation_expression_receipt_hash": trace["expression_realization_receipt_hash"],
    "differentiation_delivery_authorization_v2_hash": trace["delivery_authorization_v2_hash"],
    "realizer_delivery_authority": False,
    "actual_echo_delivery_required": True,
    "corpus_used": False,
    "llm_used": False,
    "writes_memory": False,
    "writes_identity_vault": False,
    "writes_contribution_economy": False,
    "mints_ct": False,
    "writes_ledgers": False,
}
path = os.environ.get("LANG_EXPR001_GP014_ATTESTATION_OUTPUT", "").strip()
if path:
    Path(path).write_text(json.dumps(attestation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    check("attestation evidence output created", Path(path).is_file())

passed = sum(1 for _, ok in checks if ok)
print(f"RESULT: LANG-EXPR-001-GP-014-OPERATOR-GUIDED-GENERATIVE-LANGUAGE-REALIZER_BEHAVIOR {'PASS' if passed == len(checks) else 'FAIL'}  Total:{len(checks)} Passed:{passed} Failed:{len(checks)-passed}")
raise SystemExit(0 if passed == len(checks) else 1)

#!/usr/bin/env python3
"""LANG-EXPR-001 / GP-014 structural/governance verification."""
from __future__ import annotations
import json
import sys
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
if str(FORGE) not in sys.path:
    sys.path.insert(0, str(FORGE))

from rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer import activate
from rmc_engine_v1.general_pipeline.symbolic_math_operator_language_realizer import operator_guided_language_realizer_boundary

checks=[]
def check(name, condition):
    checks.append((name, bool(condition)))
    if not condition:
        print(f"FAIL: {name}")

required=(
    "rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py",
    "rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py",
    "rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json",
    "scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py",
    "scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py",
    "scripts/README_operator_guided_language_realizer_build_langexpr001_gp014.md",
    "scripts/MEA_OPERATOR_GUIDED_LANGUAGE_REALIZER_BUILD_LANGEXPR001_GP014_DELIVERY_MANIFEST.json",
)
for rel in required:
    check(f"required payload file installed: {rel}", (FORGE/rel).is_file())

state=activate(); boundary=operator_guided_language_realizer_boundary()
check("activation identifies GP-014", state["active"] is True and state["build_id"].startswith("LANG-EXPR-001-GP-014"))
check("extends actual GP-013 path", state["extends_installed_gp013_actual_echo_vertical_slice"] is True)
check("actual Echo still required", state["actual_echo_delivery_required"] is True)
check("renderer cannot authorize delivery", state["delivery_authority_added"] is False and boundary["delivery_authority_created_here"] is False)
check("lexicon is bounded and not corpus", boundary["expression_lexicon_authority_class"] == "BOUNDED_VERSIONED_EXPRESSION_LEXICON_NOT_CORPUS")
check("generation uses multiple candidates", boundary["finite_means_generate_multiple_surface_candidates"] is True)
check("generation uses FBSC crosswalk only read-only", boundary["uses_fbsc_operator_crosswalk_read_only"] is True)
check("generation uses installed real measurement kernel", boundary["uses_installed_measurement_kernel"] is True and boundary["candidate_scores_are_computed_not_lexicon_awarded"] is True)
check("measured features include drift and semantic distance", "drift_severity_D_score" in boundary["measured_candidate_features"] and "meaning_semantic_distance" in boundary["measured_candidate_features"])
check("phase path carries verified correction then naming then projection", boundary["phase_externalization_sequence"] == ["Φ6", "Φ7", "Φ8"])
check("old preview path not promoted", boundary["uses_historical_renderer_preview_lane"] is False and boundary["activates_preview_mea_operator_engine"] is False)
check("no added UI/API route in this slice", state["adds_route_or_ui"] is False)
check("no corpus/LLM/persistence/economy authority", not any(state[key] for key in ("corpus_ingestion_added","calls_llm","writes_memory","writes_identity_vault","writes_contribution_economy","mints_ct","writes_ledgers")))

lex = json.loads((FORGE/"rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json").read_text(encoding="utf-8"))
check("versioned lexicon authority declares not corpus", lex["authority_class"] == "BOUNDED_VERSIONED_EXPRESSION_LEXICON_NOT_CORPUS")
check("lexicon covers exactly installed language slice", set(lex["operation_families"]) == {"simplification","expansion","factoring","trigonometric_simplification","trigonometric_expansion","differentiation","integration","limits"})
check("each operation has finite alternatives", all(len(row["templates"]) >= 3 for row in lex["operation_families"].values()))
check("lexicon supplies phrases but cannot pre-award candidate scores", all(not any("score" in template for template in row["templates"]) for row in lex["operation_families"].values()) and lex["selection_authority"].startswith("SCORES_COMPUTED"))
check("lexicon operator roles preserve five renderer controls", [row["glyph"] for row in lex["operator_roles"]] == ["⧙","⟁","ΔΦ","⧧","⧀"])

realizer=(FORGE/"rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py").read_text(encoding="utf-8")
delivery=(FORGE/"rmc_engine_v1/general_pipeline/symbolic_math_rmc_delivery.py").read_text(encoding="utf-8")
vertical=(FORGE/"rmc_engine_v1/general_pipeline/symbolic_math_language_vertical_slice.py").read_text(encoding="utf-8")
check("realizer consumes actual FBSC crosswalk", "from rmc_engine_v1.mea.fbsc_operator_crosswalk import binding_for_glyph, phase_binding" in realizer)
check("realizer consumes installed RMC measurement kernel", "from rmc_engine_v1.measurement_kernel import" in realizer and "drift_severity_score" in realizer and "semantic_distance" in realizer and "symbolic_epsilon" in realizer)
check("realizer has no lexicon-awarded smoothness scores", "base_score" not in realizer and "preferred_length" not in realizer)
check("realizer does not import preview operator engine", "mea.operator_engine" not in realizer)
check("realizer does not import historical renderer preview lane", "rmc_engine_v1.renderer" not in realizer)
check("delivery invokes operator-guided realization", "realize_operator_guided_symbolic_math_expression(meaning, contract)" in delivery)
execution_body = vertical[vertical.index("def answer_symbolic_math_language_request"):]
check("vertical trace captures expression receipt before Echo", execution_body.index("expression_realization =") < execution_body.index("validate_symbolic_math_echo_v2") and "expression_realization_receipt_hash" in execution_body)
check("delivery retains actual Echo function", "validate_and_approve_v2(meaning, rendered_text, contract)" in delivery)
check("vertical retains final DeliveryAuthorizationReceiptV2 step", execution_body.index("validate_symbolic_math_echo_v2") < execution_body.index("finalize_echo_delivery"))

combined="\n".join([realizer, delivery, vertical])
for token in ("eval(", "exec(", "sympify", "parse_expr", "requests.", "os.system", "sqlite3.connect", "chromadb", "ECHO_STYLE_SYMBOLIC_DELIVERY_AUTHORIZED"):
    check(f"production language upgrade excludes prohibited token {token!r}", token not in combined)
check("realizer source does not call LLM", "llm_renderer" not in realizer and "calls_llm\": True" not in realizer)
check("realizer source contains no write authority", ".write_text(" not in realizer and ".write_bytes(" not in realizer)

passed=sum(1 for _, ok in checks if ok)
print(f"RESULT: LANG-EXPR-001-GP-014-OPERATOR-GUIDED-GENERATIVE-LANGUAGE-REALIZER_VERIFY {'PASS' if passed==len(checks) else 'FAIL'}  Total:{len(checks)} Passed:{passed} Failed:{len(checks)-passed}")
raise SystemExit(0 if passed==len(checks) else 1)

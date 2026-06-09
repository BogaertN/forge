"""RMC engine v1 package.

Patch 262J1R-Preflight-A: phase_parser extracted from main.py.

Module registry
---------------
phase_parser       — Φ1–Φ9 phase classification (extracted this patch)
coherence_math     — formal math kernel / coherence scorer (Patch 262I2, kernel fix this patch)
manifest_compiler  — manifest dry-run compiler (Patch 262J, schema validation this patch)

NOT YET EXTRACTED (planned next patches)
-----------------------------------------
drift_engine       — Patch 262J1R-Preflight-B (real drift engine from design docs)
candidate_generator — Patch 262J1R-Preflight-C

Authorship law
--------------
UI does not own the math.
main.py does not own the math.
rmc_engine_v1 owns the math.
main.py is a thin governed adapter.
"""

ENGINE_PACKAGE_VERSION = "rmc_engine_v1_patch262J1R_preflight_A"

MODULE_REGISTRY = {
    "phase_parser": {
        "module": "rmc_engine_v1.phase_parser",
        "public_api": ["parse_phase", "phase_catalog", "phase_parser_boundary"],
        "extracted_patch": "262J1R-Preflight-A",
        "side_effect_free": True,
        "status": "extracted",
    },
    "coherence_math": {
        "module": "rmc_engine_v1.coherence_math",
        "public_api": [
            "score_candidate", "gate_thresholds", "extract_math_terms",
            "formal_math_binding", "clamp", "phase_num",
        ],
        "extracted_patch": "262I2",
        "updated_patch": "262J1R-Preflight-A",
        "update_note": "circuit_breaker now forces coherence_score=0.0; clamp/phase_num exported",
        "side_effect_free": True,
        "status": "extracted",
    },
    "manifest_compiler": {
        "module": "rmc_engine_v1.manifest_compiler",
        "public_api": [
            "compile_manifest_dry_run", "manifest_schema_contract",
            "manifest_compiler_boundary",
        ],
        "extracted_patch": "262J",
        "updated_patch": "262J1R-Preflight-A",
        "update_note": "schema validation guard added",
        "side_effect_free": True,
        "status": "extracted",
    },
}

PLANNED_EXTRACTIONS = {
    "drift_engine": {
        "planned_patch": "262J1R-Preflight-B",
        "note": "Real drift engine from design docs (Section 5.4, Appendix C, Section 6.3)",
        "design_sources": [
            "The Recursive Manifest Compiler - Section 05.4 Drift Analyzer",
            "The Recursive Manifest Compiler - Appendix C Drift Taxonomy",
            "The Recursive Manifest Compiler - Section 06.3 Drift Functional",
        ],
    },
    "candidate_generator": {
        "planned_patch": "262J1R-Preflight-C",
        "source_functions": ["_p262h_build_candidate_set", "_p262h_make_candidate",
                             "_p262h_candidate_status"],
    },
}

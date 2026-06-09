"""RMC engine v1 package.

Patch 262J1R-Preflight-B: drift_engine extracted and rebuilt from design docs.

Module registry
---------------
phase_parser       — extracted Patch 262J1R-Preflight-A (no change this patch)
drift_engine       — NEW this patch: structural analysis, real epsilon_s computation
coherence_math     — extracted Patch 262I2, kernel fix Patch 262J1R-Preflight-A
manifest_compiler  — extracted Patch 262J, schema validation Patch 262J1R-Preflight-A

NOT YET EXTRACTED
-----------------
candidate_generator — Patch 262J1R-Preflight-C (next)
"""

ENGINE_PACKAGE_VERSION = "rmc_engine_v1_patch262J1R_preflight_B1"

MODULE_REGISTRY = {
    "phase_parser": {
        "module": "rmc_engine_v1.phase_parser",
        "extracted_patch": "262J1R-Preflight-A",
        "status": "extracted",
        "side_effect_free": True,
    },
    "drift_engine": {
        "module": "rmc_engine_v1.drift_engine",
        "extracted_patch": "262J1R-Preflight-B",
        "status": "extracted",
        "scoring_mode": "structural_contract_drift_analysis",
        "synthetic_taxonomy_mode": False,
        "side_effect_free": True,
        "design_sources": [
            "RMC Section 05.4 Drift Analyzer",
            "RMC Appendix C Drift Taxonomy",
            "RMC Section 06.3 Drift Functional",
        ],
    },
    "coherence_math": {
        "module": "rmc_engine_v1.coherence_math",
        "extracted_patch": "262I2",
        "updated_patch": "262J1R-Preflight-A",
        "status": "extracted",
        "side_effect_free": True,
    },
    "manifest_compiler": {
        "module": "rmc_engine_v1.manifest_compiler",
        "extracted_patch": "262J",
        "updated_patch": "262J1R-Preflight-A",
        "status": "extracted",
        "side_effect_free": True,
    },
}

PLANNED_EXTRACTIONS = {
    "candidate_generator": {"planned_patch": "262J1R-Preflight-C"},
    "containment_routing": {"planned_patch": "262J1R"},
}

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
resonance_lexicon — Patch 262J1R-Preflight-B2 (gold reference foundation)
candidate_generator — Patch 262J1R-Preflight-C (after B2 verifies)
"""

ENGINE_PACKAGE_VERSION = "rmc_engine_v1_patch262J1R_preflight_B3"

MODULE_REGISTRY = {
    "phase_codex": {
        "module": "rmc_engine_v1.phase_codex",
        "extracted_patch": "262J1R-Preflight-B3",
        "status": "extracted",
        "engine_mode": "read_only_phase_codex_binding",
        "side_effect_free": True,
        "authority": "FBSC Phase Glyph Codex v2.5 / Rosetta Stone",
    },
    "phase_parser": {
        "module": "rmc_engine_v1.phase_parser",
        "extracted_patch": "262J1R-Preflight-A",
        "status": "extracted",
        "side_effect_free": True,
    },

    "resonance_lexicon": {
        "module": "rmc_engine_v1.resonance_lexicon",
        "extracted_patch": "262J1R-Preflight-B2",
        "updated_patch": "262J1R-Preflight-B3",
        "status": "extracted",
        "engine_mode": "read_only_resonance_lexicon_dry_run",
        "side_effect_free": True,
        "authority_hierarchy": [
            "letter_resonance_weak_signal",
            "word_loop_medium_signal",
            "phrase_operator_strong_signal",
            "sentence_transition_and_manifest_trace_final_authority",
        ],
    },
    "drift_engine": {
        "module": "rmc_engine_v1.drift_engine",
        "extracted_patch": "262J1R-Preflight-B",
        "updated_patch": "262J1R-Preflight-B2",
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

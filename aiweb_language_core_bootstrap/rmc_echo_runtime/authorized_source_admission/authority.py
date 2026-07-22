"""Slice 43C exact accepted-source authority constants.

These constants bind admission to the single accepted, deterministic,
fixture-only Slice 42 ancestry proven at the accepted Slice 43B parent.
They grant no comparison, drift, disposition, delivery, model, route,
memory, tool, action, or GP-014 authority.
"""

from __future__ import annotations

SLICE43C_ACCEPTED_PARENT_HEAD = "42db0a12fd0b09dbe002fe652d869987dd955ed6"
SLICE43C_ACCEPTED_PARENT_TREE = "bd734175783e413fab30084f686d80fde9e76b29"
SLICE43C_ACCEPTED_PARENT_SUBJECT = (
    "Slice 43B deterministic validation identity versioning lifecycle"
)
SLICE43C_COMMIT_SUBJECT = (
    "Slice 43C authorized meaning and proposed-expression admission"
)

SLICE43C_SCHEMA_VERSION = (
    "aiweb-slice43c-authorized-meaning-proposed-expression-admission-v1"
)
SLICE43C_PROFILE_VERSION = (
    "aiweb-slice43c-exact-slice42-source-admission-profile-v1"
)
SLICE43C_SPEC_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"
REQUESTED_OPERATION = (
    "admit-exact-authorized-meaning-and-proposed-expression"
)

SUPPORTED_SOURCE_SCHEMA_VERSIONS = (
    ("slice41e", "aiweb-language-core-slice41e-msm-selected-meaning-integration-v1"),
    ("slice42c", "aiweb-slice42c-authorized-meaning-admission-expression-eligibility-v1"),
    ("slice42d", "aiweb-slice42d-preservation-obligation-projection-v1"),
    ("slice42e", "aiweb-slice42e-controlled-expression-plan-construction-v1"),
    ("slice42f", "aiweb-slice42f-deterministic-surface-realization-v1"),
    ("slice42g", "aiweb-language-core-slice42g-msm-outward-expression-integration-v1"),
    ("slice42h", "aiweb-slice42h-disabled-outward-expression-closeout-v1"),
    ("msm", "MSM-v1"),
    ("slice43a", "aiweb-slice43a-rmc-echo-core-schema-v1"),
    ("slice43b", "aiweb-slice43b-rmc-echo-governance-v1"),
)

EXACT_ACCEPTED_IDS = (
    ("slice42h_fixture", "slice42h_outward_expression_closeout_fixture:a6656abf2995c83ad00b7975ec3eea260a9bd6930cd0a75459abf1b73bce56f2"),
    ("slice42h_result", "slice42h_disabled_outward_expression_closeout_result:107e9914332219bb299f72f4904eb1d3aa0c748e4fb14dba7d611229967a3f9e"),
    ("slice42h_acceptance", "slice42_acceptance_record:4478ef7310eb45518e9ea62e2e5ed7265023db47b8bdb9a682e1ea891dc0b7f2"),
    ("slice42g_input", "slice42g_integration_input:819e7def452b942afa7823425ac3806558c054c5ecfdb14e103a8fff1c1c0039"),
    ("slice42g_result", "slice42g_msm_outward_expression_integration_result:c28a9228c95963fb7bb8ce888635f362a990040e2b3a36890d7bb6e89fc66cce"),
    ("slice42g_receipt", "slice42g_msm_outward_expression_receipt:f465c649d10a0a7c961936860cf7e883999e00d76dad6bef7948c5379831145c"),
    ("source_manifest", "meaning_structure_manifest_slice41e_successor:33d102c251bc2f74747c47abe11d7ec7b5ae1b0365bd5f54b69ca597f8878183"),
    ("successor_manifest", "meaning_structure_manifest_slice42g_successor:1967fb50851d52772478cdb0a09d1db75a2df848915c554492ec8049e6cb0ab0"),
    ("selected_meaning", "slice41e_integrated_selected_governed_meaning:f4477d332130847fbb16ee281c5dcf8a2d43e470245a2b913f8601a76bfa3c8f"),
    ("selected_candidate", "msm_candidate_record:demo"),
    ("governed_outward_meaning", "slice42g_integrated_governed_outward_meaning:ad7a691427b39263f273981aa5b8e5b49ec7ae0b44cb3f76f3b510c3e9645c95"),
    ("expression_link", "slice42g_integrated_expression_link:b6172f4915b3c5f4a3a749b72dd79793949252acd8ba7940f009584aee2b41f7"),
    ("expression_candidate", "unvalidated-expression-candidate:9aaebbab660e5449b65abe6933eb56d85be3ad52e145de36a11f2e472a27d105"),
    ("slice42f_input", "surface-realization-input:d96bd5fa5f96fa91234a4ade936428b41d1cfc0181a18702f37fc96b52c1980a"),
    ("slice42f_result", "surface-realization-result:d60f92e3a145fb9839a788241f6f59afcd6c916027c16f176110aa63bdcf69a4"),
    ("slice42f_receipt", "surface-realization-receipt:df50b7efbd0d7e1818703dbdacb38d24fc203b03ecf205e270726a6097b7be86"),
    ("slice42f_trace", "surface-realization-trace:d35c1cd4ecd3168d17ac994a405423e0954db043e01cb4e98f81d64f3403a665"),
    ("slice42e_plan", "controlled_expression_plan:eadb6a2b8ff3963f82933a81f451acaff7fc1a82cfc8ffc675d8cedd1f51ad2c"),
    ("slice42d_obligation", "expression_obligation_package:df01b7bd18a10b7822955b591eb1339330370d6c110f02cfc851a25ab3334a1c"),
    ("slice42c_result", "expression_eligibility_result:5f73de040aded455bffc5a109e58916f287c218c8aea2c0af1b7d1dc91087e3d"),
    ("selected_content_proof", "selected_meaning_content_proof:0e1764bec2b22ac40a1fc9727d4d0ac53ea491393ada5f8656f38eefaefc1bb0"),
    ("selection_authority_reference", "slice41e_selection_authority_reference:1ca18baa297493997721dd7ec2c7d93d92c6ec9c5dc9cafd6e20c30417da3c44"),
    ("outward_authority_reference", "slice42g_surface_realization_authority_reference:375d389516998288b8eb9dec2b5c5c51a2c45f4f5200004fa6c439c916d336fa"),
    ("selected_to_outward_trace", "slice42g_selected_to_outward_transition:cdafcf1caf73458b4a3faf5a469f5169b011058432739e73ef2c7ab418fed117"),
    ("outward_to_expression_trace", "slice42g_outward_to_expression_transition:6abfc22cea9c55304b8af95cf7c18ec5354bf1605906e608ce8ed2f00cbe4d6b"),
)
EXACT_ACCEPTED_ID_MAP = dict(EXACT_ACCEPTED_IDS)

EXACT_SOURCE_MANIFEST_SHA256 = (
    "ca83428e682d3521348160ef34bd6e1aae0f08eab63c1eb063247cf58dab36d6"
)
EXACT_SUCCESSOR_MANIFEST_SHA256 = (
    "90e6617745dd09bdeda854a5980d1c6e7cac052356493dde14697e399075b26c"
)
EXACT_REALIZED_TEXT_SHA256 = (
    "6c6a1179184d0c833db4b7d326380740be063c24adbadfc3a9713bc9dca59875"
)

PERMANENT_AUTHORITY_ZERO = (
    "meaning-preservation comparison is deferred to Slice 43D",
    "validation finding creation is deferred to Slice 43D",
    "drift classification and materiality are deferred to Slice 43E",
    "PASSED, REJECTED and CONTAINED disposition execution is deferred to Slice 43F",
    "Echo rejection and containment issuance is deferred to Slice 43F",
    "MSM-v1 validation-link integration is deferred to Slice 43G",
    "bootstrap integration and Slice 43 closeout are deferred to Slice 43H",
    "delivery, route, API, network, filesystem, memory, tool and action authority are absent",
    "LLM, EchoForge, embedding, vector, RAG, similarity, neural parser and hidden classifier authority are absent",
    "GP-014 is not superseded",
)

REQUIRED_ADMISSION_COMPONENTS = (
    "selected_governed_meaning",
    "governed_outward_meaning",
    "realized_expression_candidate",
    "msm_v1_expression_link",
    "slice42_trace_and_custody_references",
)

REQUIRED_REJECTION_CATEGORIES = (
    "raw_text_without_accepted_ancestry",
    "orphan_expression",
    "recomputed_or_fabricated_identity",
    "unsupported_version",
    "missing_required_link",
    "already_delivered_candidate",
    "unauthorized_candidate",
    "inconsistent_accepted_ancestry",
)

__all__ = tuple(name for name in globals() if name.isupper())

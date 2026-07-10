#!/usr/bin/env python3
"""Behavior tests for the frozen legacy RMC call-site containment correction."""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.manifest_compiler import compile_manifest  # noqa: E402
from rmc_engine_v1.output_renderer import render_manifest, renderer_boundary  # noqa: E402
from rmc_engine_v1.memory_recaller import recall_memory, build_trace_spine, memory_recaller_boundary  # noqa: E402
from rmc_engine_v1 import MODULE_REGISTRY, FROZEN_LEGACY_EVIDENCE  # noqa: E402

PASS_MARKER = "PASS - FROZEN LEGACY CALL-SITE CONTAINMENT BEHAVIOR TEST"
FROZEN = {
    "rmc_engine_v1/llm_renderer.py": "855bb683801e034487c997fd6dfeb51b8fd376f4d287fddb3e33b83bca99d2ac",
    "rmc_engine_v1/chroma_connector.py": "6554fe9188e676d4b79d4ba15f0a723574a64defc8bef4e0363ed165c83eed91",
}
RETIRED = {
    "scripts/test_rmc_chroma_connector_C15.py": "RETIRED - C15 CHROMA BEHAVIOR TEST BLOCKED",
    "scripts/test_rmc_llm_renderer_C16.py": "RETIRED - C16 LLM RENDERER BEHAVIOR TEST BLOCKED",
    "scripts/patch262J1R_preflight_C15_verify.py": "RETIRED - C15 CHROMA VERIFIER BLOCKED",
    "scripts/patch262J1R_preflight_C16_verify.py": "RETIRED - C16 LLM RENDERER VERIFIER BLOCKED",
}


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"FAIL - {name}" + (f": {detail}" if detail else ""))
    print(f"PASS - {name}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _literal_text(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return ""


def assert_no_frozen_import_or_dynamic_load(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = {"rmc_engine_v1.llm_renderer", "rmc_engine_v1.chroma_connector"}
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in forbidden:
                    violations.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "") in forbidden:
                violations.append(f"from {node.module} import ...")
        elif isinstance(node, ast.Call):
            target = ""
            if isinstance(node.func, ast.Name):
                target = node.func.id
            elif isinstance(node.func, ast.Attribute):
                target = node.func.attr
            if target in {"__import__", "import_module"} and node.args:
                literal = _literal_text(node.args[0])
                if literal in forbidden:
                    violations.append(f"dynamic import {literal}")
    check(
        f"no frozen import or dynamic load: {path.relative_to(ROOT)}",
        not violations,
        "; ".join(violations),
    )


def strong_c3r(claim: str = "Compile the corrected and named trace into a pre-language manifest object before any rendering.") -> dict:
    return {
        "status": "OK",
        "trace_id": "rmctrace_test_render_strong",
        "run_id": "c3run_test_render_strong",
        "score_set_id": "st_test_render_strong",
        "candidate_set_id": "ct_set_test_render_strong",
        "selected_candidate_id": "ct_test_render_strong",
        "chi_t_present": True,
        "N_t_present": True,
        "chi_t": {
            "chi_t_id": "chi_test_render_strong",
            "status": "correction_passes_stable_for_naming_dry_run",
            "correction_allowed": True,
            "candidate_id": "ct_test_render_strong",
            "candidate_validity_score": 0.78,
            "projection_gated_score": 0.0,
            "measured_inputs": {
                "epsilon_s": 0.22,
                "D_score": 0.34,
                "sigma_res": 0.09,
                "semantic_distance": 0.31,
                "memory_fit": 0.78,
                "novelty_delta": 0.24,
                "source_confidence": 0.91,
            },
            "quality_calibration": {
                "candidate_validity_score": 0.78,
                "projection_gated_score": 0.0,
                "novelty_budget": 0.55,
                "support_pressure": 0.18,
                "components": {
                    "memory_fit": 0.78,
                    "semantic_distance": 0.31,
                    "novelty_delta": 0.24,
                    "source_confidence": 0.91,
                    "epsilon_s": 0.22,
                    "D_score": 0.34,
                    "phase_validity": 0.92,
                },
            },
            "phase_repair": {
                "repaired_phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
                "repaired_phase_metrics": {
                    "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
                    "phase_indexes": [5, 6, 7, 8],
                    "transition_deltas": [0.125, 0.125, 0.125],
                    "average_delta_phi": 0.125,
                    "max_delta_phi": 0.125,
                    "phase_path_legal": True,
                    "phase_warnings": [],
                    "phase_validity_score": 0.92,
                },
            },
            "correction_math": {
                "post_correction_estimate": {
                    "sigma_res": 0.09,
                    "D_score": 0.24,
                    "delta_phi": 0.125,
                    "epsilon_s": 0.151667,
                    "formula": "post_epsilon_s = (sigma_res + corrected_D_score + corrected_delta_phi) / 3",
                }
            },
            "route_consistency": {
                "recommended_route": "route_to_naming_engine",
                "chi_t_action": "route_to_naming_engine",
                "route_consistent": True,
            },
        },
        "N_t": {
            "N_t_id": "nt_test_render_strong",
            "status": "naming_candidate_stable_internal_only",
            "naming_allowed": True,
            "stable_naming": True,
            "candidate_id": "ct_test_render_strong",
            "proposed_name": "Drift-Corrected Rendering Trace",
            "machine_name": "drift_corrected_rendering_trace",
            "definition": claim,
            "phase_role": "Φ7 naming after Φ6 correction",
            "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
            "allowed_use": ["internal_trace_label", "future_manifest_input_after_correction_and_coherence_validation"],
            "forbidden_use": ["public_projection", "memory_write_as_truth"],
            "memory_tag_preview": "rmc/name/drift_corrected_rendering_trace",
            "naming_confidence_report": {
                "naming_confidence": 0.79,
                "components": {
                    "candidate_validity_score": 0.78,
                    "post_stability": 0.848333,
                    "memory_fit": 0.78,
                    "semantic_distance": 0.31,
                    "novelty_delta": 0.24,
                    "source_confidence": 0.91,
                    "phase_validity": 0.92,
                },
            },
        },
        "source_coherence_scorer": {
            "trace_id": "rmctrace_test_render_strong",
            "candidate_set_id": "ct_set_test_render_strong",
            "score_set_id": "st_test_render_strong",
            "selected_candidate_meaning_state_preview": {
                "candidate_id": "ct_test_render_strong",
                "title": "Strong Render Manifest Candidate",
                "candidate": claim,
                "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
                "memory_links": [
                    {
                        "memory_id": "m_manifest_rendering_definition",
                        "source_kind": "reference_document",
                        "source_path": "RMC Section 3.7 Rendering",
                        "memory_role": "render_schema_source",
                        "phase_tags": ["Φ7", "Φ8"],
                        "confidence": 0.96,
                        "retrieval_weight": 0.88,
                    }
                ],
            },
            "selected_scored_candidate_preview": {
                "candidate_id": "ct_test_render_strong",
                "coherence_score": 0.74,
            },
        },
    }

def main() -> int:
    check("target repository exists", ROOT.is_dir())
    for rel, expected in FROZEN.items():
        check(f"frozen hash unchanged: {rel}", sha256(ROOT / rel) == expected)

    live_paths = [
        ROOT / "main.py",
        ROOT / "rmc_engine_v1" / "__init__.py",
        ROOT / "rmc_engine_v1" / "output_renderer.py",
        ROOT / "rmc_engine_v1" / "memory_recaller.py",
        ROOT / "rmc_engine_v1" / "frozen_legacy_boundary.py",
        *[ROOT / rel for rel in RETIRED],
    ]
    for path in live_paths:
        check(f"required path exists: {path.relative_to(ROOT)}", path.is_file())
        assert_no_frozen_import_or_dynamic_load(path)

    manifest = compile_manifest(strong_c3r())
    check("strong manifest compiles", manifest.get("status") == "OK")
    rendered = render_manifest(manifest)
    check("deterministic render succeeds", rendered.get("status") == "OK")
    check("deterministic render produces R_t", rendered.get("R_t_present") is True)
    check("deterministic render used no LLM", rendered.get("llm_renderer_used") is False)
    check("deterministic render performed no fallback", rendered.get("fallback_performed") is False)
    check("renderer reports LLM unavailable", renderer_boundary().get("optional_llm_renderer_available") is False)

    blocked_llm_requests = [
        {"llm_renderer_enabled": True},
        {"llm_renderer_enabled": "yes"},
        {"model_endpoint": "http://127.0.0.1:11434/api/generate"},
        {"model": "withdrawn-model"},
        {"llm_timeout_seconds": 3},
        {"llm_client": object()},
    ]
    for kwargs in blocked_llm_requests:
        result = render_manifest(manifest, **kwargs)
        label = next(iter(kwargs))
        check(f"LLM request blocked: {label}", result.get("status") == "BLOCKED")
        check(f"LLM request has no R_t: {label}", result.get("R_t_present") is False)
        check(f"LLM request has no fallback: {label}", result.get("fallback_performed") is False)
        decision = result.get("legacy_llm_request") or {}
        check(f"LLM decision explicit: {label}", decision.get("reason_code") == "FROZEN_LEGACY_LLM_REQUEST_PROHIBITED")
        check(f"LLM call false: {label}", decision.get("calls_llm") is False and decision.get("calls_model") is False)

    saved_backend = os.environ.pop("RMC_MEMORY_RETRIEVAL_BACKEND", None)
    saved_collection = os.environ.pop("RMC_CHROMA_COLLECTION", None)
    saved_limit = os.environ.pop("RMC_CHROMA_LIMIT", None)
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "forge"
            receipt = root / "memory" / "context_library_v1" / "receipts" / "receipt_001.json"
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.write_text(json.dumps({
                "memory_id": "memory_filesystem_001",
                "text": "Grace correction precedes naming and projection.",
                "memory_role": "test_context",
                "phase_tags": ["Φ6", "Φ7"],
                "source_kind": "context_receipt",
            }), encoding="utf-8")

            default_recall = recall_memory("grace correction naming", {}, root=root)
            check("default recall succeeds", default_recall.get("status") == "OK")
            check("default backend is filesystem", default_recall.get("memory_state", {}).get("retrieval_backend_effective") == "filesystem")
            check("default recall performs no fallback", default_recall.get("fallback_performed") is False)
            check("filesystem memory can be recalled", default_recall.get("memory_state", {}).get("active_memory_count", 0) >= 1)
            check("vector similarity not advertised", "vector_similarity" not in default_recall.get("memory_state", {}).get("retrieval_dimensions", []))

            for alias in ["filesystem", "files", "fs", "local", "local_filesystem", ""]:
                result = recall_memory("grace correction", {"retrieval_backend": alias}, root=root)
                check(f"filesystem alias accepted: {alias!r}", result.get("status") == "OK")
                check(f"filesystem alias effective: {alias!r}", result.get("memory_state", {}).get("retrieval_backend_effective") == "filesystem")

            for backend in ["chroma", "hybrid", "auto", "vector", "semantic", "embedding", "rag", "unknown"]:
                result = recall_memory("grace correction", {"retrieval_backend": backend}, root=root)
                check(f"prohibited backend blocked: {backend}", result.get("status") == "BLOCKED")
                check(f"prohibited backend no fallback: {backend}", result.get("fallback_performed") is False)
                check(f"prohibited backend active count zero: {backend}", result.get("memory_state", {}).get("active_memory_count") == 0)

            for control in [
                {"chroma_collection": "legacy"},
                {"collection_name": "legacy"},
                {"chroma_limit": 2},
            ]:
                result = recall_memory("grace correction", control, root=root)
                label = next(iter(control))
                check(f"prohibited vector control blocked: {label}", result.get("status") == "BLOCKED")
                check(f"prohibited vector control no fallback: {label}", result.get("fallback_performed") is False)

            trace = build_trace_spine("grace correction", {"retrieval_backend": "chroma"}, root=root)
            check("blocked trace spine remains blocked", trace.get("status") == "BLOCKED")
            check("blocked trace spine does not render", trace.get("trace_spine_readiness", {}).get("rendering_allowed") is False)
    finally:
        if saved_backend is not None:
            os.environ["RMC_MEMORY_RETRIEVAL_BACKEND"] = saved_backend
        if saved_collection is not None:
            os.environ["RMC_CHROMA_COLLECTION"] = saved_collection
        if saved_limit is not None:
            os.environ["RMC_CHROMA_LIMIT"] = saved_limit

    check("registry removes live LLM capability", "llm_renderer" not in MODULE_REGISTRY)
    check("registry removes live Chroma capability", "chroma_connector" not in MODULE_REGISTRY)
    check("historical evidence declares LLM frozen", FROZEN_LEGACY_EVIDENCE["rmc_engine_v1/llm_renderer.py"]["runtime_authorized"] is False)
    check("historical evidence declares Chroma frozen", FROZEN_LEGACY_EVIDENCE["rmc_engine_v1/chroma_connector.py"]["runtime_authorized"] is False)

    forbidden_old_markers = [
        "PASS - RMC CHROMA CONNECTOR C15 TESTS",
        "PASS - RMC LLM RENDERER C16 TESTS",
        "PASS - PATCH262J1R PREFLIGHT C15 VERIFIER",
        "PASS - PATCH262J1R PREFLIGHT C16 VERIFIER",
    ]
    for rel, marker in RETIRED.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        check(f"retired marker present: {rel}", marker in text)
        check(f"retired script has no frozen module path: {rel}", "rmc_engine_v1.llm_renderer" not in text and "rmc_engine_v1.chroma_connector" not in text)
        check(f"retired script cannot emit old success marker: {rel}", not any(old in text for old in forbidden_old_markers))
        proc = subprocess.run([sys.executable, str(path)], cwd=str(ROOT), capture_output=True, text=True, check=False)
        check(f"retired script exits non-success: {rel}", proc.returncode == 78, f"returncode={proc.returncode}")
        check(f"retired script emits retirement marker: {rel}", marker in proc.stdout)

    main_text = (ROOT / "main.py").read_text(encoding="utf-8")
    check("main has static legacy route helper", 'legacy_route_record("legacy_llm_renderer"' in main_text and 'legacy_route_record("legacy_chroma_connector"' in main_text)
    check("main legacy routes use HTTP Gone helper", "_gone(" in main_text)
    check("main does not import frozen modules", "from rmc_engine_v1.llm_renderer" not in main_text and "from rmc_engine_v1.chroma_connector" not in main_text)

    memory_boundary = memory_recaller_boundary()
    check("memory boundary filesystem-only", memory_boundary.get("supported_retrieval_backends") == ["filesystem"])
    check("memory boundary no Chroma", memory_boundary.get("queries_chroma") is False)
    check("memory boundary no vector store", memory_boundary.get("queries_vector_store") is False)

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

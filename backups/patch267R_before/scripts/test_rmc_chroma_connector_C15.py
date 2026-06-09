#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C15 Chroma integration boundary."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.chroma_connector import (  # noqa: E402
    DEFAULT_CHROMA_COLLECTION,
    ENGINE_VERSION,
    chroma_connector_boundary,
    chroma_memory_status,
    normalize_retrieval_backend,
    query_chroma_memory,
)
from rmc_engine_v1.memory_recaller import recall_memory, build_trace_spine, memory_recaller_boundary  # noqa: E402


def _assert(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"[FAIL] {name} {detail}".rstrip())
    print(f"[PASS] {name}")


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class FakeCollection:
    def query(self, query_texts, n_results, include):
        assert query_texts
        assert "documents" in include
        return {
            "ids": [["chunk_alpha", "chunk_beta"][:n_results]],
            "documents": [[
                "Grace correction must happen before naming and projection in the RMC trace.",
                "Stable memory retrieval links phase tags and operator paths for echo validation.",
            ][:n_results]],
            "metadatas": [[
                {
                    "rpmc_phase_tags": ["Φ6", "Φ7", "Φ8"],
                    "memory_role": "chroma_phase_law_chunk",
                    "source_path": "context/chunks/chunk_alpha.txt",
                    "corpus_id": "corpus_chroma_test",
                    "sha256_16": "abc123def4567890",
                },
                {
                    "phase_path": "Φ7 Φ8",
                    "role": "echo_validation_chunk",
                    "source_file": "context/chunks/chunk_beta.txt",
                },
            ][:n_results]],
            "distances": [[0.12, 0.38][:n_results]],
        }


class FakeClient:
    def __init__(self, path):
        self.path = path

    def get_collection(self, name):
        assert name == DEFAULT_CHROMA_COLLECTION
        return FakeCollection()


def main() -> int:
    _assert("engine_version_C15", ENGINE_VERSION.endswith("C15"))
    _assert("backend_normalize_filesystem", normalize_retrieval_backend("files") == "filesystem")
    _assert("backend_normalize_hybrid", normalize_retrieval_backend("both") == "hybrid")
    _assert("backend_invalid_falls_back", normalize_retrieval_backend("dangerous") == "filesystem")
    boundary = chroma_connector_boundary(collection_name=DEFAULT_CHROMA_COLLECTION)
    _assert("boundary_read_only", boundary.get("writes_files") is False and boundary.get("writes_chroma") is False)
    _assert("boundary_no_llm_shell", boundary.get("calls_llm") is False and boundary.get("executes_shell") is False)
    _assert("boundary_query_only_when_requested", boundary.get("queries_chroma_only_when_requested") is True)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "forge"
        chroma_path = root / "memory" / "context_library_v1" / "chroma_db"
        status_missing = chroma_memory_status(root=root)
        _assert("status_missing_path_ok", status_missing.get("status") == "OK")
        _assert("status_connector_not_available_without_path", status_missing.get("connector_available_for_query") is False)

        skipped = query_chroma_memory("correction before projection", root=root, client_factory=lambda p: FakeClient(p))
        _assert("missing_path_skips_without_query", skipped.get("status") == "SKIPPED" and skipped.get("reason_code") == "approved_chroma_path_missing")
        _assert("missing_path_no_write", skipped.get("writes_files") is False)

        chroma_path.mkdir(parents=True)
        queried = query_chroma_memory(
            "correction before naming projection",
            root=root,
            collection_name=DEFAULT_CHROMA_COLLECTION,
            limit=2,
            client_factory=lambda p: FakeClient(p),
        )
        _assert("fake_chroma_query_ok", queried.get("status") == "OK")
        nodes = queried.get("memory_nodes") or []
        _assert("fake_chroma_returns_nodes", len(nodes) == 2)
        _assert("node_source_kind_chroma", nodes[0].get("source_kind") == "chroma_context_chunk")
        _assert("node_phase_tags_extracted", "Φ6" in (nodes[0].get("phase_tags") or []))
        _assert("node_vector_similarity_present", nodes[0].get("vector_similarity", 0) > 0)
        _assert("query_no_write", queried.get("writes_files") is False and queried.get("writes_chroma") is False)

        # Add a filesystem JSON node to prove default recall still works and does not require Chroma.
        receipt = root / "memory" / "context_library_v1" / "receipts" / "receipt_001.json"
        _write_json(receipt, {
            "receipt_id": "receipt_001",
            "filename": "Filesystem Context.txt",
            "collection": "aiweb_context_chunks_v1",
            "verification_ok": True,
            "rpmc_phase_tags": ["Φ6", "Φ7"],
        })
        fs_report = recall_memory("correct projection before naming", {"source_kind": "test", "retrieval_backend": "filesystem"}, root=root, limit=5)
        _assert("filesystem_default_ok", fs_report.get("status") == "OK")
        _assert("filesystem_backend_effective", fs_report.get("memory_state", {}).get("retrieval_backend_effective") == "filesystem")
        _assert("filesystem_no_chroma_nodes", fs_report.get("memory_state", {}).get("chroma_nodes_collected") == 0)
        _assert("filesystem_active_nodes", fs_report.get("memory_state", {}).get("active_memory_count", 0) >= 1)

        # Monkeypatch the module function used by memory_recaller to prove hybrid merge without real chromadb.
        import rmc_engine_v1.memory_recaller as mr  # noqa: E402
        original_query = mr.query_chroma_memory
        try:
            mr.query_chroma_memory = lambda *args, **kwargs: queried
            hybrid = recall_memory("correct projection before naming", {"source_kind": "test", "retrieval_backend": "hybrid"}, root=root, limit=5)
        finally:
            mr.query_chroma_memory = original_query
        _assert("hybrid_recall_ok", hybrid.get("status") == "OK")
        _assert("hybrid_effective", hybrid.get("memory_state", {}).get("retrieval_backend_effective") == "hybrid")
        _assert("hybrid_chroma_nodes_collected", hybrid.get("memory_state", {}).get("chroma_nodes_collected") == 2)
        _assert("hybrid_active_has_vector_dimension", "vector_similarity" in hybrid.get("memory_state", {}).get("retrieval_dimensions", []))
        _assert("hybrid_no_memory_write", hybrid.get("boundary", {}).get("writes_files") is False and hybrid.get("boundary", {}).get("writes_rmc_memory") is False)

        trace = build_trace_spine("correct projection before naming", {"source_kind": "test", "retrieval_backend": "filesystem"}, root=root, limit=5)
        _assert("trace_spine_still_ok", trace.get("status") == "OK" and bool(trace.get("symbolic_trace", {}).get("M_t")))
        _assert("trace_spine_no_render", trace.get("trace_spine_readiness", {}).get("rendering_allowed") is False)

    mem_boundary = memory_recaller_boundary()
    _assert("memory_boundary_reports_supported_backends", "hybrid" in mem_boundary.get("supported_retrieval_backends", []))
    _assert("memory_boundary_default_filesystem", mem_boundary.get("retrieval_backend_default") == "filesystem")
    print("RESULT: chroma_connector_C15_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

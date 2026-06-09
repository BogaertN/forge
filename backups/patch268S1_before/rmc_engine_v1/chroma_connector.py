"""RMC Chroma Connector v1.

Patch 262J1R-Preflight-C15 adds a read-only Chroma retrieval boundary for the
RMC Memory Recaller. This module is intentionally small and explicit:

* It never writes to Chroma.
* It never creates a Chroma database path.
* It never mutates canonical references, Identity Vault, RMC live memory, or
  dataset JSON.
* It only queries an already-existing, approved context-library Chroma path.
* If Chroma is unavailable, it returns a structured SKIPPED report and the
  Memory Recaller falls back to its existing file-system retrieval path.

The goal is not to replace RMC memory with a vector database. The goal is to
allow the Memory Recaller to pull additional read-only context chunks from the
approved context library when the connector is deliberately activated.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import importlib
import json
import os
import re
from pathlib import Path
from typing import Any, Callable

ENGINE_VERSION = "rmc_chroma_connector_v1_patch262J1R_preflight_C15"
ENGINE_MODE = "read_only_chroma_context_retrieval_boundary"
DEFAULT_FORGE_ROOT = Path("/home/nic/forge")
DEFAULT_CHROMA_COLLECTION = "aiweb_context_chunks_v1"
APPROVED_CHROMA_RELATIVE_PATH = Path("memory/context_library_v1/chroma_db")
SUPPORTED_RETRIEVAL_BACKENDS = ("filesystem", "chroma", "hybrid", "auto")


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _forge_root(root: str | Path | None = None) -> Path:
    if root is not None:
        return Path(root).expanduser().resolve()
    env_root = os.environ.get("FORGE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return DEFAULT_FORGE_ROOT


def _sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _stable_id(prefix: str, text: str) -> str:
    return f"{prefix}_{_sha256_text(text)[:18]}"


def normalize_retrieval_backend(value: Any) -> str:
    backend = str(value or "filesystem").strip().lower().replace("-", "_")
    aliases = {
        "file": "filesystem",
        "files": "filesystem",
        "json": "filesystem",
        "local": "filesystem",
        "vector": "chroma",
        "vectors": "chroma",
        "chroma_db": "chroma",
        "both": "hybrid",
        "merge": "hybrid",
    }
    backend = aliases.get(backend, backend)
    if backend not in SUPPORTED_RETRIEVAL_BACKENDS:
        return "filesystem"
    return backend


def approved_chroma_path(root: str | Path | None = None) -> Path:
    return (_forge_root(root) / APPROVED_CHROMA_RELATIVE_PATH).resolve()


def _path_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False


def _phase_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        raw = value
    elif isinstance(value, tuple):
        raw = list(value)
    elif isinstance(value, dict):
        raw = list(value.keys())
    else:
        raw = re.split(r"[,;|\s]+", str(value))
    out: list[str] = []
    for item in raw:
        text = str(item).strip().replace("Phi", "Φ").replace("phi", "Φ")
        m = re.search(r"(?:Φ|phase[_\s-]?)([1-9])", text, re.I)
        if m:
            text = f"Φ{m.group(1)}"
        if text in {f"Φ{i}" for i in range(1, 10)} and text not in out:
            out.append(text)
    return out


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def chroma_connector_boundary(root: str | Path | None = None, collection_name: str = DEFAULT_CHROMA_COLLECTION) -> dict[str, Any]:
    chroma_path = approved_chroma_path(root)
    return {
        "engine_version": ENGINE_VERSION,
        "engine_mode": ENGINE_MODE,
        "engine_module_location": "forge/rmc_engine_v1/chroma_connector.py",
        "implements_rmc_stage": "Optional Chroma Context Retrieval for Memory Recaller / M_t",
        "approved_chroma_path": str(chroma_path),
        "approved_collection_name": str(collection_name or DEFAULT_CHROMA_COLLECTION),
        "retrieval_backends": list(SUPPORTED_RETRIEVAL_BACKENDS),
        "queries_chroma_only_when_requested": True,
        "creates_chroma_path": False,
        "writes_chroma": False,
        "writes_files": False,
        "writes_rmc_memory": False,
        "writes_identity_vault": False,
        "calls_llm": False,
        "executes_shell": False,
        "mutates_canonical_reference": False,
        "read_only": True,
        "note": "Chroma is an optional read-only retrieval source. File-system recall remains available and is the default.",
    }


def _import_chromadb() -> tuple[Any | None, str | None]:
    try:
        return importlib.import_module("chromadb"), None
    except Exception as exc:
        return None, f"chromadb_not_available:{type(exc).__name__}"


def chroma_memory_status(root: str | Path | None = None, collection_name: str = DEFAULT_CHROMA_COLLECTION) -> dict[str, Any]:
    root_path = _forge_root(root)
    chroma_path = approved_chroma_path(root_path)
    approved_parent = (root_path / APPROVED_CHROMA_RELATIVE_PATH).resolve()
    path_guard_ok = _path_within(chroma_path, approved_parent) or chroma_path == approved_parent
    chromadb_module, import_error = _import_chromadb()
    path_exists = chroma_path.exists() and chroma_path.is_dir()
    return {
        "status": "OK",
        "engine_version": ENGINE_VERSION,
        "engine_mode": "read_only_chroma_status_C15",
        "stage": "Chroma Connector Status",
        "created_at_utc": _utc_now(),
        "collection_name": str(collection_name or DEFAULT_CHROMA_COLLECTION),
        "chroma_path": str(chroma_path),
        "chroma_path_exists": bool(path_exists),
        "chroma_path_guard_ok": bool(path_guard_ok),
        "chromadb_import_available": chromadb_module is not None,
        "chromadb_import_error": import_error,
        "connector_available_for_query": bool(path_exists and path_guard_ok and chromadb_module is not None),
        "fallback_available": True,
        "fallback_backend": "filesystem",
        "boundary": chroma_connector_boundary(root_path, collection_name),
        "writes_files": False,
        "writes_chroma": False,
        "memory_write_allowed": False,
        "identity_vault_write": False,
        "calls_llm": False,
        "executes_shell": False,
    }


def _extract_nested_rows(result: dict[str, Any], key: str) -> list[Any]:
    value = result.get(key)
    if not value:
        return []
    if isinstance(value, list) and value and isinstance(value[0], list):
        return value[0]
    if isinstance(value, list):
        return value
    return []


def _node_from_chroma_row(
    *,
    collection_name: str,
    chroma_id: str,
    document: str,
    metadata: dict[str, Any],
    distance: float | None,
    rank: int,
) -> dict[str, Any]:
    metadata = metadata or {}
    doc = str(document or "")
    phase_tags = _phase_list(
        metadata.get("rpmc_phase_tags") or
        metadata.get("phase_tags") or
        metadata.get("phase_path") or
        metadata.get("phase")
    )
    if distance is None:
        vector_similarity = 0.0
    else:
        # Chroma distance values are backend-specific; clamp a useful similarity
        # hint for ranking without claiming it is universal truth.
        vector_similarity = max(0.0, min(1.0, 1.0 - _coerce_float(distance, 1.0)))
    source = (
        metadata.get("source") or metadata.get("filename") or metadata.get("source_file") or
        metadata.get("document_id") or metadata.get("corpus_id") or "chroma_context_chunk"
    )
    return {
        "memory_id": _stable_id("mem_chroma", f"{collection_name}:{chroma_id}:{rank}"),
        "source_kind": "chroma_context_chunk",
        "source_path": str(metadata.get("source_path") or metadata.get("relative_path") or "chroma://" + collection_name + "/" + str(chroma_id)),
        "content_summary": doc[:900],
        "source": str(source),
        "phase_tags": phase_tags,
        "confidence": "chroma_retrieved",
        "ancestry": {
            "collection": collection_name,
            "chroma_id": str(chroma_id),
            "rank": rank,
            "distance": distance,
            "document_id": metadata.get("document_id") or metadata.get("id") or "",
            "corpus_id": metadata.get("corpus_id") or "",
            "sha256_16": metadata.get("sha256_16") or metadata.get("sha256") or "",
        },
        "prior_drift_score": _coerce_float(metadata.get("prior_drift_score") or metadata.get("epsilon_s") or 0.0),
        "memory_role": str(metadata.get("memory_role") or metadata.get("role") or "chroma_context_chunk"),
        "chroma_distance": distance,
        "vector_similarity": round(vector_similarity, 4),
        "retrieval_backend": "chroma",
    }


def query_chroma_memory(
    source_text: str,
    phase_report: dict[str, Any] | None = None,
    root: str | Path | None = None,
    limit: int = 8,
    collection_name: str = DEFAULT_CHROMA_COLLECTION,
    client_factory: Callable[[str], Any] | None = None,
) -> dict[str, Any]:
    """Read-only query against the approved context-library Chroma collection.

    ``client_factory`` exists for deterministic unit tests. In live Forge, this
    function imports ``chromadb`` dynamically only after the approved path exists.
    """
    del phase_report  # phase features are already encoded in metadata/ranking upstream.
    root_path = _forge_root(root)
    chroma_path = approved_chroma_path(root_path)
    approved_parent = (root_path / APPROVED_CHROMA_RELATIVE_PATH).resolve()
    if not (chroma_path == approved_parent or _path_within(chroma_path, approved_parent)):
        return {
            "status": "REFUSED",
            "reason_code": "chroma_path_outside_approved_context_library",
            "memory_nodes": [],
            "boundary": chroma_connector_boundary(root_path, collection_name),
            "queries_chroma": False,
            "writes_files": False,
        }
    if not chroma_path.exists() or not chroma_path.is_dir():
        return {
            "status": "SKIPPED",
            "reason_code": "approved_chroma_path_missing",
            "chroma_path": str(chroma_path),
            "memory_nodes": [],
            "boundary": chroma_connector_boundary(root_path, collection_name),
            "queries_chroma": False,
            "writes_files": False,
        }
    try:
        n_results = max(1, min(int(limit or 8), 50))
    except Exception:
        n_results = 8
    try:
        if client_factory is not None:
            client = client_factory(str(chroma_path))
        else:
            chromadb_module, import_error = _import_chromadb()
            if chromadb_module is None:
                return {
                    "status": "SKIPPED",
                    "reason_code": "chromadb_import_unavailable",
                    "import_error": import_error,
                    "chroma_path": str(chroma_path),
                    "memory_nodes": [],
                    "boundary": chroma_connector_boundary(root_path, collection_name),
                    "queries_chroma": False,
                    "writes_files": False,
                }
            client = chromadb_module.PersistentClient(path=str(chroma_path))
        collection = client.get_collection(name=str(collection_name or DEFAULT_CHROMA_COLLECTION))
        query = collection.query(
            query_texts=[str(source_text or "")[:4000]],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        return {
            "status": "SKIPPED",
            "reason_code": "chroma_query_unavailable",
            "error_type": type(exc).__name__,
            "error_preview": str(exc)[:240],
            "chroma_path": str(chroma_path),
            "collection_name": str(collection_name or DEFAULT_CHROMA_COLLECTION),
            "memory_nodes": [],
            "boundary": chroma_connector_boundary(root_path, collection_name),
            "queries_chroma": True,
            "writes_files": False,
        }

    docs = _extract_nested_rows(query, "documents")
    metas = _extract_nested_rows(query, "metadatas")
    ids = _extract_nested_rows(query, "ids")
    distances = _extract_nested_rows(query, "distances")
    nodes: list[dict[str, Any]] = []
    for idx, doc in enumerate(docs[:n_results]):
        meta = metas[idx] if idx < len(metas) and isinstance(metas[idx], dict) else {}
        chroma_id = str(ids[idx] if idx < len(ids) else meta.get("id") or f"rank_{idx}")
        distance = distances[idx] if idx < len(distances) else None
        nodes.append(_node_from_chroma_row(
            collection_name=str(collection_name or DEFAULT_CHROMA_COLLECTION),
            chroma_id=chroma_id,
            document=str(doc or ""),
            metadata=meta,
            distance=distance,
            rank=idx + 1,
        ))
    return {
        "status": "OK",
        "engine_version": ENGINE_VERSION,
        "engine_mode": "read_only_chroma_query_C15",
        "stage": "Chroma Context Retrieval",
        "query_id": _stable_id("chromaquery", str(source_text) + str(collection_name) + str(n_results)),
        "collection_name": str(collection_name or DEFAULT_CHROMA_COLLECTION),
        "chroma_path": str(chroma_path),
        "requested_results": n_results,
        "returned_results": len(nodes),
        "memory_nodes": nodes,
        "boundary": chroma_connector_boundary(root_path, collection_name),
        "queries_chroma": True,
        "writes_files": False,
        "writes_chroma": False,
        "memory_write_allowed": False,
        "identity_vault_write": False,
        "calls_llm": False,
        "executes_shell": False,
    }

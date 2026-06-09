"""
Forge knowledge_base.py
Local vector knowledge base using ChromaDB and nomic-embed-text via Ollama.

Flow for forge add <path>:
  1. scan_for_indexing(path)  → returns preview of what will/won't be indexed
  2. User approves
  3. index_path(path, project_name) → chunks, embeds, stores, updates manifest

search_knowledge_base(query) is a read-only tool available after indexing.
"""

import os
import json
import hashlib
import datetime
import requests
from pathlib import Path
from typing import Optional

import chromadb

from .permissions import (
    is_path_allowed,
    is_filetype_allowed,
    is_path_blocked,
    get_filetype_policy,
)

FORGE_ROOT    = Path(__file__).resolve().parents[2]
MEMORY_DIR    = FORGE_ROOT / "memory"
KB_DIR        = MEMORY_DIR / "chroma_db"
KB_MANIFEST   = MEMORY_DIR / "forge_kb_manifest.json"

OLLAMA_EMBED_URL = "http://127.0.0.1:11434/api/embed"
EMBED_MODEL      = "nomic-embed-text"
COLLECTION_NAME  = "forge_kb"

CHUNK_SIZE    = 1800   # characters per chunk
CHUNK_OVERLAP = 150    # overlap between chunks


# ─── CHUNKING ────────────────────────────────────────────────────────────────

def _chunk_text(text: str, filepath: str) -> list[str]:
    """
    Split file content into overlapping chunks for embedding.
    Python files are split at function/class boundaries when possible.
    All other files are split at paragraph or fixed-size boundaries.
    Returns a list of chunk strings.
    """
    if not text.strip():
        return []

    ext = Path(filepath).suffix.lower()

    if ext == ".py":
        return _chunk_python(text)
    else:
        return _chunk_generic(text)


def _chunk_python(text: str) -> list[str]:
    """
    Split Python source by top-level def/class blocks.
    Falls back to generic chunking if file is too flat.
    """
    lines = text.splitlines(keepends=True)
    chunks = []
    current = []
    current_size = 0

    for line in lines:
        # New top-level def/class starts a new chunk
        if (line.startswith("def ") or line.startswith("class ") or
                line.startswith("async def ")):
            if current and current_size > 100:
                chunks.append("".join(current))
                current = []
                current_size = 0

        current.append(line)
        current_size += len(line)

        # Force-split if chunk is very large
        if current_size >= CHUNK_SIZE:
            chunks.append("".join(current))
            # Keep the last line as overlap start
            current = [line]
            current_size = len(line)

    if current:
        chunks.append("".join(current))

    # If we ended up with one giant chunk, fall back to generic
    if len(chunks) == 1 and len(chunks[0]) > CHUNK_SIZE * 2:
        return _chunk_generic(text)

    return [c for c in chunks if c.strip()]


def _chunk_generic(text: str) -> list[str]:
    """
    Split text into overlapping fixed-size chunks.
    Tries to split at paragraph boundaries (double newlines) first.
    """
    # Try paragraph-based splitting
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > CHUNK_SIZE:
            if current.strip():
                chunks.append(current.strip())
            # Start new chunk with overlap from end of previous
            overlap = current[-CHUNK_OVERLAP:] if len(current) > CHUNK_OVERLAP else current
            current = overlap + "\n\n" + para
        else:
            current = current + "\n\n" + para if current else para

    if current.strip():
        chunks.append(current.strip())

    # If paragraph splitting gave too-large chunks, force split by character
    final = []
    for chunk in chunks:
        if len(chunk) <= CHUNK_SIZE * 1.5:
            final.append(chunk)
        else:
            for i in range(0, len(chunk), CHUNK_SIZE - CHUNK_OVERLAP):
                part = chunk[i:i + CHUNK_SIZE]
                if part.strip():
                    final.append(part)

    return final if final else [text[:CHUNK_SIZE]]


# ─── EMBEDDING ───────────────────────────────────────────────────────────────

def _embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of text strings using nomic-embed-text via Ollama.
    Returns a list of embedding vectors.
    Raises RuntimeError if Ollama is unreachable or model is missing.
    """
    if not texts:
        return []

    try:
        response = requests.post(
            OLLAMA_EMBED_URL,
            json={"model": EMBED_MODEL, "input": texts},
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        embeddings = data.get("embeddings", [])
        if not embeddings:
            raise RuntimeError(
                f"Ollama returned no embeddings. Response: {data}"
            )
        return embeddings
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot reach Ollama at http://127.0.0.1:11434. "
            "Is Ollama running? Run: systemctl status ollama"
        )
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise RuntimeError(
                f"Embedding model '{EMBED_MODEL}' not found. "
                f"Pull it with: ollama pull {EMBED_MODEL}"
            )
        raise RuntimeError(f"Ollama embedding error: {e}")


def check_embed_model_available() -> tuple[bool, str]:
    """Check whether nomic-embed-text is available in Ollama."""
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=10)
        response.raise_for_status()
        models = [m["name"] for m in response.json().get("models", [])]
        if any(EMBED_MODEL in m for m in models):
            return True, f"{EMBED_MODEL} is available."
        return False, (
            f"{EMBED_MODEL} is not installed. Pull it with:\n"
            f"  ollama pull {EMBED_MODEL}"
        )
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach Ollama. Is it running?"


# ─── CHROMADB CLIENT ─────────────────────────────────────────────────────────

def _get_collection() -> chromadb.Collection:
    """Return (or create) the persistent ChromaDB collection."""
    KB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(KB_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Forge local knowledge base"}
    )


# ─── MANIFEST ────────────────────────────────────────────────────────────────

def _load_manifest() -> dict:
    if not KB_MANIFEST.exists():
        return {"_comment": "Forge knowledge base manifest.", "entries": []}
    content = KB_MANIFEST.read_text().strip()
    if not content:
        return {"_comment": "Forge knowledge base manifest.", "entries": []}
    with open(KB_MANIFEST, "r") as f:
        return json.load(f)


def _save_manifest(data: dict):
    with open(KB_MANIFEST, "w") as f:
        json.dump(data, f, indent=2)


def _file_hash(filepath: str) -> str:
    """SHA-256 of file contents, first 16 chars."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()[:16]


def _is_already_indexed(filepath: str, current_hash: str) -> bool:
    """Return True if this exact file version is already in the manifest."""
    manifest = _load_manifest()
    for entry in manifest.get("entries", []):
        if entry.get("path") == filepath and entry.get("hash") == current_hash:
            return True
    return False


def _add_manifest_entry(entry: dict):
    manifest = _load_manifest()
    # Remove old entry for this path if it exists (re-indexing updated file)
    manifest["entries"] = [
        e for e in manifest.get("entries", [])
        if e.get("path") != entry["path"]
    ]
    manifest["entries"].append(entry)
    _save_manifest(manifest)


# ─── SCAN (PRE-INDEXING PREVIEW) ─────────────────────────────────────────────

class ScanResult:
    """Result of a pre-indexing scan. Shown to user for approval."""

    def __init__(self):
        self.will_index:   list[str] = []   # paths that will be indexed
        self.will_skip:    list[tuple[str, str]] = []  # (path, reason)
        self.already_current: list[str] = []  # indexed and unchanged

    def summary(self) -> str:
        lines = []

        if self.already_current:
            lines.append(f"\n  Already indexed and current ({len(self.already_current)} files):")
            for p in self.already_current[:10]:
                lines.append(f"    ✓ {p}")
            if len(self.already_current) > 10:
                lines.append(f"    ... and {len(self.already_current)-10} more")

        if self.will_index:
            lines.append(f"\n  Will be indexed ({len(self.will_index)} files):")
            for p in self.will_index[:30]:
                lines.append(f"    + {p}")
            if len(self.will_index) > 30:
                lines.append(f"    ... and {len(self.will_index)-30} more")

        if self.will_skip:
            lines.append(f"\n  Will be excluded ({len(self.will_skip)} files):")
            for p, reason in self.will_skip[:15]:
                lines.append(f"    ✗ {os.path.basename(p)}  ({reason})")
            if len(self.will_skip) > 15:
                lines.append(f"    ... and {len(self.will_skip)-15} more")

        lines.append(f"\n  Total to index now: {len(self.will_index)} files")
        return "\n".join(lines)

    def is_empty(self) -> bool:
        return len(self.will_index) == 0


def scan_for_indexing(path: str) -> ScanResult:
    """
    Walk a path and classify every file as: will_index, will_skip, or already_current.
    Does not embed anything. Returns a ScanResult for user review.
    """
    path = os.path.expanduser(path)
    result = ScanResult()

    # Check path is allowed
    allowed, reason = is_path_allowed(path)
    if not allowed:
        result.will_skip.append((path, reason))
        return result

    blocked_dir_names = {
        "node_modules", "__pycache__", ".git", ".venv", ".env",
        "dist", "build", ".idea", ".vscode", "migrations",
        ".mypy_cache", ".pytest_cache", "htmlcov", "coverage"
    }

    def _walk(current: str):
        try:
            entries = sorted(os.scandir(current), key=lambda e: (not e.is_dir(), e.name))
        except PermissionError:
            return

        for entry in entries:
            name = entry.name

            if entry.is_dir():
                if name.startswith(".") or name.lower() in blocked_dir_names:
                    result.will_skip.append((entry.path, f"directory excluded: {name}"))
                    continue
                allowed, reason = is_path_allowed(entry.path)
                if not allowed:
                    result.will_skip.append((entry.path, reason))
                    continue
                _walk(entry.path)

            else:
                blocked, reason = is_path_blocked(entry.path)
                if blocked:
                    result.will_skip.append((entry.path, reason))
                    continue

                allowed_type, reason = is_filetype_allowed(entry.path)
                if not allowed_type:
                    result.will_skip.append((entry.path, reason))
                    continue

                # Check size
                policy = get_filetype_policy()
                max_kb = policy.get("max_file_size_kb", 512)
                size_kb = entry.stat().st_size / 1024
                if size_kb > max_kb:
                    result.will_skip.append((entry.path, f"file too large: {size_kb:.0f}KB > {max_kb}KB"))
                    continue

                # Check if already indexed and current
                try:
                    fhash = _file_hash(entry.path)
                    if _is_already_indexed(entry.path, fhash):
                        result.already_current.append(entry.path)
                        continue
                except OSError:
                    result.will_skip.append((entry.path, "cannot read file"))
                    continue

                result.will_index.append(entry.path)

    if os.path.isfile(path):
        blocked, reason = is_path_blocked(path)
        if blocked:
            result.will_skip.append((path, reason))
        else:
            allowed_type, reason = is_filetype_allowed(path)
            if not allowed_type:
                result.will_skip.append((path, reason))
            else:
                try:
                    fhash = _file_hash(path)
                    if _is_already_indexed(path, fhash):
                        result.already_current.append(path)
                    else:
                        result.will_index.append(path)
                except OSError:
                    result.will_skip.append((path, "cannot read file"))
    else:
        _walk(path)

    return result


# ─── INDEXING ────────────────────────────────────────────────────────────────

class IndexingProgress:
    """Tracks and reports indexing progress to the terminal."""

    def __init__(self, total: int):
        self.total     = total
        self.done      = 0
        self.errors    = 0
        self.chunks_total = 0

    def update(self, filepath: str, chunks: int, error: str = ""):
        self.done += 1
        if error:
            self.errors += 1
            print(f"    ✗ [{self.done}/{self.total}] {os.path.basename(filepath)} — {error}")
        else:
            self.chunks_total += chunks
            print(f"    + [{self.done}/{self.total}] {os.path.basename(filepath)} ({chunks} chunks)")

    def summary(self) -> str:
        return (
            f"  Indexed {self.done - self.errors} files, "
            f"{self.chunks_total} total chunks. "
            f"{self.errors} errors."
        )


def index_path(
    path: str,
    project_name: str,
    files_to_index: list[str]
) -> tuple[int, int]:
    """
    Index the approved file list into ChromaDB.
    Returns (files_indexed, chunks_created).

    Each file is:
      1. Read
      2. Chunked
      3. Embedded via nomic-embed-text
      4. Stored in ChromaDB
      5. Recorded in forge_kb_manifest.json
    """
    collection = _get_collection()
    progress   = IndexingProgress(len(files_to_index))

    for filepath in files_to_index:
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            progress.update(filepath, 0, str(e))
            continue

        chunks = _chunk_text(content, filepath)
        if not chunks:
            progress.update(filepath, 0, "empty file, skipped")
            continue

        # Embed all chunks for this file
        try:
            embeddings = _embed_texts(chunks)
        except RuntimeError as e:
            progress.update(filepath, 0, f"embedding failed: {e}")
            continue

        if len(embeddings) != len(chunks):
            progress.update(filepath, 0, f"embedding count mismatch: {len(embeddings)} vs {len(chunks)}")
            continue

        # Generate chunk IDs: sha256(filepath)[:8] + chunk index
        file_id_prefix = hashlib.sha256(filepath.encode()).hexdigest()[:8]
        chunk_ids = [f"{file_id_prefix}_c{i}" for i in range(len(chunks))]

        # Remove old chunks for this file (re-indexing case)
        try:
            existing = collection.get(where={"source": filepath})
            if existing["ids"]:
                collection.delete(ids=existing["ids"])
        except Exception:
            pass  # First time indexing this file

        # Store in ChromaDB
        try:
            collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=[
                    {
                        "source":    filepath,
                        "project":   project_name,
                        "chunk_idx": i,
                        "ext":       Path(filepath).suffix.lower(),
                    }
                    for i in range(len(chunks))
                ]
            )
        except Exception as e:
            progress.update(filepath, 0, f"chromadb error: {e}")
            continue

        # Record in manifest
        fhash = _file_hash(filepath)
        _add_manifest_entry({
            "path":            filepath,
            "project":         project_name,
            "hash":            fhash,
            "indexed_at":      datetime.datetime.now().isoformat(timespec="seconds"),
            "embedding_model": EMBED_MODEL,
            "chunk_count":     len(chunks),
            "file_type":       Path(filepath).suffix.lower(),
            "size_kb":         round(os.path.getsize(filepath) / 1024, 2),
        })

        progress.update(filepath, len(chunks))

    files_indexed = progress.done - progress.errors
    print(f"\n  {progress.summary()}")
    return files_indexed, progress.chunks_total


# ─── SEARCH ──────────────────────────────────────────────────────────────────

def search_knowledge_base(
    query: str,
    n_results: int = 5,
    project_filter: Optional[str] = None
) -> dict:
    """
    Semantic search against the local knowledge base.
    Returns top N matching chunks with source file and relevance.
    """
    if not KB_DIR.exists():
        return {
            "ok": False,
            "error": "Knowledge base has not been initialized. Run 'forge add <path>' first."
        }

    collection = _get_collection()
    if collection.count() == 0:
        return {
            "ok": False,
            "error": "Knowledge base is empty. Run 'forge add <path>' to index a project."
        }

    # Embed the query
    try:
        query_embeddings = _embed_texts([query])
    except RuntimeError as e:
        return {"ok": False, "error": f"Embedding query failed: {e}"}

    where = {"project": project_filter} if project_filter else None

    try:
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=min(n_results, collection.count()),
            where=where,
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        return {"ok": False, "error": f"ChromaDB query failed: {e}"}

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return {"ok": True, "data": f"No results found in knowledge base for: '{query}'"}

    lines = [f"Knowledge base results for '{query}' ({len(documents)} matches):\n"]
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        source   = meta.get("source", "unknown")
        project  = meta.get("project", "")
        relevance = max(0.0, 1.0 - dist)  # convert distance to 0-1 relevance score
        lines.append(f"── Result {i+1}  [{relevance:.0%} relevant]  {source}")
        # Show a preview of the chunk (first 400 chars)
        preview = doc[:400].replace("\n", " ").strip()
        if len(doc) > 400:
            preview += " ..."
        lines.append(f"   {preview}")
        lines.append("")

    return {"ok": True, "data": "\n".join(lines)}


def get_kb_stats() -> str:
    """Return a summary of what is currently in the knowledge base."""
    manifest = _load_manifest()
    entries  = manifest.get("entries", [])

    if not entries:
        return "Knowledge base is empty. Run 'forge add <path>' to index a project."

    projects: dict[str, list] = {}
    for entry in entries:
        p = entry.get("project", "unknown")
        projects.setdefault(p, []).append(entry)

    lines = [f"Knowledge base: {len(entries)} files indexed across {len(projects)} project(s)"]
    for proj, proj_entries in sorted(projects.items()):
        total_chunks = sum(e.get("chunk_count", 0) for e in proj_entries)
        lines.append(f"  {proj}: {len(proj_entries)} files, {total_chunks} chunks")

    if KB_DIR.exists():
        collection = _get_collection()
        lines.append(f"  ChromaDB total vectors: {collection.count()}")

    return "\n".join(lines)

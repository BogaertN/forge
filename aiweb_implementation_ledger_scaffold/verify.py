"""
Slice 5R1 verifier helpers for Implementation Ledger continuity scaffolding.
"""

from __future__ import annotations

import py_compile
from pathlib import Path
from typing import List, Sequence, Tuple

REQUIRED_FILES = (
    "aiweb_implementation_ledger_scaffold/__init__.py",
    "aiweb_implementation_ledger_scaffold/ledger.py",
    "aiweb_implementation_ledger_scaffold/cycle.py",
    "aiweb_implementation_ledger_scaffold/verify.py",
    "scripts/test_aiweb_slice05_implementation_ledger_scaffold.py",
    "scripts/aiweb_slice05_implementation_ledger_verify.py",
    "scripts/README_aiweb_slice05_implementation_ledger_scaffold.md",
)

ALLOWED_STATUS_PATH_PREFIXES = (
    "aiweb_implementation_ledger_scaffold/",
    "scripts/README_aiweb_slice05_implementation_ledger_scaffold.md",
    "scripts/aiweb_slice05_implementation_ledger_verify.py",
    "scripts/test_aiweb_slice05_implementation_ledger_scaffold.py",
)

FORBIDDEN_IMPORT_TERMS = (
    "openai",
    "ollama",
    "chromadb",
    "langchain",
    "llama",
    "faiss",
    "sentence_transformers",
    "transformers",
    "torch",
    "tensorflow",
    "requests",
    "httpx",
    "urllib",
    "socket",
)

_FORBIDDEN_AUTHORITY_PARTS = (
    ("production", " ready"),
    ("production", "-ready"),
    ("release", " authorized"),
    ("public delivery", " authorized"),
    ("gp-014", " superseded"),
    ("gp014", " superseded"),
    ("gp-014", " replaced"),
    ("gp015", " repaired"),
    ("gp-015", " repaired"),
    ("gp015r1", " installed"),
    ("gp-015r1", " installed"),
    ("llm authority", " enabled"),
    ("vector authority", " enabled"),
    ("memory authority", " enabled"),
)

def forbidden_authority_terms() -> Tuple[str, ...]:
    return tuple("".join(parts) for parts in _FORBIDDEN_AUTHORITY_PARTS)

def compile_python_file(path: Path) -> Tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, f"python syntax valid: {path}"
    except Exception as exc:  # pragma: no cover - verifier diagnostic path
        return False, f"python syntax invalid: {path}: {exc}"

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def has_forbidden_imports(path: Path) -> Tuple[bool, str]:
    text = read_text(path).lower()
    active_lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        active_lines.append(line)
    joined = "\n".join(active_lines)
    hits = [term for term in FORBIDDEN_IMPORT_TERMS if f"import {term}" in joined or f"from {term}" in joined]
    if hits:
        return False, f"forbidden active model/network import terms in {path}: {', '.join(sorted(hits))}"
    return True, f"no forbidden active model/network imports: {path}"

def has_forbidden_authority_phrases(path: Path) -> Tuple[bool, str]:
    text = read_text(path).lower()
    hits = [term for term in forbidden_authority_terms() if term in text]
    if hits:
        return False, f"forbidden authority phrase in {path}: {', '.join(sorted(hits))}"
    return True, f"no forbidden authority phrases: {path}"

def git_status_is_slice05_only(repo: Path, status_lines: Sequence[str]) -> Tuple[bool, str]:
    unexpected: List[str] = []
    for line in status_lines:
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 else line.strip()
        if not any(path.startswith(prefix) for prefix in ALLOWED_STATUS_PATH_PREFIXES):
            unexpected.append(line)
    if unexpected:
        return False, "git status contains out-of-scope paths: " + " | ".join(unexpected)
    return True, "git status contains only Slice 5 scaffold paths"

def required_files_exist(repo: Path) -> Tuple[bool, List[str]]:
    messages: List[str] = []
    ok = True
    for rel in REQUIRED_FILES:
        exists = (repo / rel).is_file()
        ok = ok and exists
        messages.append(("required file exists: " if exists else "required file missing: ") + rel)
    return ok, messages

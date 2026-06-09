"""
Forge document_adapters.py
Level 4.8 — Document Adapter Registry.

Provides a registry of read adapters for common document formats.
Detection is lazy (at call time) so it reflects the active Python environment —
whether that is the Forge venv, system Python, or another environment.

SECURITY CONSTRAINTS:
  No subprocess. No shell. No package install. No document writes.
  Adapters only extract text from files. They do not store or index anything.
"""

from __future__ import annotations
import hashlib
import sys
from pathlib import Path
from typing import Optional

PREVIEW_MAX_CHARS = 4_000
PDF_MAX_PAGES     = 5       # limit PDF extraction to first N pages


# ─── FORMAT REGISTRY ──────────────────────────────────────────────────────────

# Plain text formats: no library needed, read as UTF-8
PLAIN_TEXT_EXTENSIONS = {
    ".txt", ".md", ".json", ".csv", ".py", ".log",
    ".toml", ".yaml", ".yml", ".tex", ".rst", ".sh",
    ".js", ".ts", ".html", ".css", ".sql",
}

# Library-backed formats
LIBRARY_FORMATS = {
    ".docx": {
        "library":      "python-docx",
        "import_check": "from docx import Document",
        "install_hint": "pip install python-docx",
        "description":  "Microsoft Word (Open XML)",
    },
    ".pdf": {
        "library":      "pdfplumber (or pypdf)",
        "import_check": "import pdfplumber",
        "install_hint": "pip install pdfplumber",
        "description":  "Portable Document Format",
    },
}

# Future / unsupported formats
FUTURE_FORMATS = {
    ".doc":  "Legacy Word (binary) — not supported",
    ".rtf":  "Rich Text Format — not supported",
    ".odt":  "OpenDocument Text — not supported",
    ".xlsx": "Excel — not supported",
    ".pptx": "PowerPoint — not supported",
    ".epub": "eBook — not supported",
}


# ─── LIBRARY DETECTION ───────────────────────────────────────────────────────

def _check_library(import_check: str) -> bool:
    """Try to import a library and return True if available."""
    try:
        exec(import_check, {})
        return True
    except ImportError:
        return False


def get_adapter_status() -> dict[str, dict]:
    """
    Return the current status of all format adapters, detecting library
    availability in the currently active Python environment.
    """
    status: dict[str, dict] = {}

    # Plain text — always available
    for ext in sorted(PLAIN_TEXT_EXTENSIONS):
        status[ext] = {
            "extension":       ext,
            "read_supported":  True,
            "write_supported": False,
            "library":         "built-in (UTF-8 read)",
            "status":          "available",
            "notes":           "plain text, no library required",
        }

    # Library-backed formats
    for ext, info in sorted(LIBRARY_FORMATS.items()):
        available = _check_library(info["import_check"])
        status[ext] = {
            "extension":       ext,
            "read_supported":  available,
            "write_supported": False,
            "library":         info["library"],
            "status":          "available" if available else "missing",
            "notes":           "" if available else f"Install with: {info['install_hint']}",
            "description":     info["description"],
        }

    # Future formats
    for ext, desc in sorted(FUTURE_FORMATS.items()):
        status[ext] = {
            "extension":       ext,
            "read_supported":  False,
            "write_supported": False,
            "library":         "none",
            "status":          "future",
            "notes":           desc,
        }

    return status


# ─── TEXT EXTRACTION ──────────────────────────────────────────────────────────

class ExtractionResult:
    def __init__(self, text: str = "", error: str = "", unsupported: bool = False):
        self.text        = text
        self.error       = error
        self.unsupported = unsupported

    @property
    def ok(self) -> bool:
        return not self.error and not self.unsupported


def extract_text(path: Path, max_chars: int = PREVIEW_MAX_CHARS) -> ExtractionResult:
    """
    Extract up to max_chars of text from a file.
    Returns an ExtractionResult with text, error, or unsupported flag.

    Never writes anything. Never installs anything. Never calls subprocess.
    If a library is missing, returns ExtractionResult with unsupported=True.
    """
    suffix = path.suffix.lower()

    # ── Plain text family ───────────────────────────────────────────────────
    if suffix in PLAIN_TEXT_EXTENSIONS:
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            return ExtractionResult(text=content[:max_chars])
        except OSError as e:
            return ExtractionResult(error=f"Read error: {e}")

    # ── DOCX ────────────────────────────────────────────────────────────────
    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError:
            return ExtractionResult(
                unsupported=True,
                error=(
                    "python-docx is not installed in the active Python environment.\n"
                    f"  Python: {sys.executable}\n"
                    "  To fix: activate the Forge venv and run:\n"
                    "    pip install python-docx"
                )
            )
        try:
            doc = Document(str(path))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs)
            return ExtractionResult(text=text[:max_chars])
        except Exception as e:
            return ExtractionResult(error=f"docx extraction failed: {e}")

    # ── PDF ─────────────────────────────────────────────────────────────────
    if suffix == ".pdf":
        # Try pdfplumber first
        try:
            import pdfplumber
            with pdfplumber.open(str(path)) as pdf:
                pages = []
                for i, page in enumerate(pdf.pages):
                    if i >= PDF_MAX_PAGES:
                        break
                    t = page.extract_text()
                    if t:
                        pages.append(t)
            text = "\n".join(pages)
            return ExtractionResult(text=text[:max_chars])
        except ImportError:
            pass  # fall through to pypdf
        except Exception as e:
            return ExtractionResult(error=f"pdfplumber extraction failed: {e}")

        # Try pypdf as fallback
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            pages = []
            for i, page in enumerate(reader.pages):
                if i >= PDF_MAX_PAGES:
                    break
                t = page.extract_text()
                if t:
                    pages.append(t)
            text = "\n".join(pages)
            return ExtractionResult(text=text[:max_chars])
        except ImportError:
            return ExtractionResult(
                unsupported=True,
                error=(
                    "No PDF library found in the active Python environment.\n"
                    f"  Python: {sys.executable}\n"
                    "  To fix: activate the Forge venv and run:\n"
                    "    pip install pdfplumber"
                )
            )
        except Exception as e:
            return ExtractionResult(error=f"pypdf extraction failed: {e}")

    # ── Unsupported ──────────────────────────────────────────────────────────
    future_note = FUTURE_FORMATS.get(suffix, "")
    return ExtractionResult(
        unsupported=True,
        error=f"Unsupported format: {suffix}" + (f" — {future_note}" if future_note else "")
    )


# ─── CORPUS PREVIEW BACKEND ───────────────────────────────────────────────────

def corpus_preview(
    item: dict,
    corpus_root: Path,
    session_id: str,
) -> tuple[str, str, str]:
    """
    Shared backend for corpus-preview and doc-preview.
    Validates path, checks SHA-256, extracts text.

    Returns (text, error_msg, audit_tool) where:
      text      — extracted preview text (may be empty on error)
      error_msg — non-empty if something went wrong
      audit_tool — the audit entry name to write
    """
    abs_path_str = item.get("absolute_path", "").strip()
    if not abs_path_str:
        abs_path_str = str(corpus_root / item.get("relative_path", ""))

    abs_path = Path(abs_path_str)

    # Path must be inside corpus root
    try:
        abs_path.relative_to(corpus_root)
    except ValueError:
        return "", f"Path escapes corpus root: {abs_path}", "DOC_PREVIEW_REFUSED"

    if not abs_path.exists():
        return "", f"File not found on disk: {abs_path}", "DOC_PREVIEW_REFUSED"

    # SHA-256 integrity check
    expected_sha = str(item.get("sha256_16", "")).strip()
    if expected_sha:
        try:
            actual_sha = hashlib.sha256(abs_path.read_bytes()).hexdigest()[:16]
        except OSError as e:
            return "", f"Cannot read file for hash check: {e}", "DOC_PREVIEW_REFUSED"

        if actual_sha != expected_sha:
            return (
                "",
                f"SHA-256 mismatch — expected {expected_sha}, got {actual_sha}. "
                "File may have changed since manifest was created.",
                "DOC_PREVIEW_HASH_MISMATCH"
            )
    else:
        actual_sha = "unknown"

    # Extract text via adapter
    result = extract_text(abs_path)

    if result.unsupported:
        return "", result.error, "DOC_PREVIEW_UNSUPPORTED"
    if result.error:
        return "", result.error, "DOC_PREVIEW_REFUSED"

    return result.text, "", "DOC_PREVIEWED"

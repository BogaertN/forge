"""Deterministic scanner primitives for Slice 6."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from .catalog import UnsafePhrase, assembled_unsafe_catalog, scanner_scope_record


EXCLUDED_DIR_NAMES = {
    ".git",
    "node_modules",
    "target",
    "dist",
    "build",
    ".next",
    "coverage",
    ".pytest_cache",
    ".venv",
    "venv",
    "backups",
    "backup",
    "memory",
    "logs",
    "runtime",
    "__pycache__",
}


TEXT_SUFFIXES = {
    ".py",
    ".pyw",
    ".txt",
    ".md",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".rs",
    ".sh",
    ".cfg",
    ".ini",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    category: str
    matched: str
    context: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ScanReport:
    schema_version: str
    scanner_only: bool
    scanned_files: int
    finding_count: int
    findings: List[Finding]

    @property
    def passed(self) -> bool:
        return self.finding_count == 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "scanner_only": self.scanner_only,
            "scanned_files": self.scanned_files,
            "finding_count": self.finding_count,
            "passed": self.passed,
            "findings": [item.to_dict() for item in self.findings],
        }


def _line_context(line_text: str) -> str:
    clean = " ".join(line_text.strip().split())
    if len(clean) <= 160:
        return clean
    return clean[:157] + "..."


def scan_text(text: str, *, path_label: str = "<text>", rules: Optional[Sequence[UnsafePhrase]] = None) -> ScanReport:
    active_rules = list(rules if rules is not None else assembled_unsafe_catalog())
    findings: List[Finding] = []
    for line_number, line_text in enumerate(text.splitlines(), start=1):
        lowered = line_text.lower()
        for rule in active_rules:
            phrase = rule.phrase
            if phrase.lower() in lowered:
                findings.append(
                    Finding(
                        path=path_label,
                        line=line_number,
                        category=rule.category,
                        matched=phrase,
                        context=_line_context(line_text),
                    )
                )
    scope = scanner_scope_record()
    return ScanReport(
        schema_version=str(scope["schema_version"]),
        scanner_only=bool(scope["scanner_only"]),
        scanned_files=1,
        finding_count=len(findings),
        findings=findings,
    )


def _is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in path.parts)


def iter_scannable_files(root: Path) -> List[Path]:
    root = root.resolve()
    files: List[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if _is_excluded(path.relative_to(root)):
            continue
        if path.suffix in TEXT_SUFFIXES:
            files.append(path)
    return sorted(files)


def scan_file(path: Path, *, rules: Optional[Sequence[UnsafePhrase]] = None) -> ScanReport:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    return scan_text(text, path_label=str(path), rules=rules)


def scan_paths(paths: Iterable[Path], *, rules: Optional[Sequence[UnsafePhrase]] = None) -> ScanReport:
    active_rules = list(rules if rules is not None else assembled_unsafe_catalog())
    all_findings: List[Finding] = []
    scanned = 0
    for path in sorted(Path(p) for p in paths):
        if path.is_dir():
            candidates = iter_scannable_files(path)
        elif path.is_file():
            candidates = [path]
        else:
            candidates = []
        for candidate in candidates:
            report = scan_file(candidate, rules=active_rules)
            scanned += report.scanned_files
            all_findings.extend(report.findings)
    scope = scanner_scope_record()
    return ScanReport(
        schema_version=str(scope["schema_version"]),
        scanner_only=bool(scope["scanner_only"]),
        scanned_files=scanned,
        finding_count=len(all_findings),
        findings=all_findings,
    )

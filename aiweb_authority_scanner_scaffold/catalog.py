"""Catalog builder for Slice 6 scanner tests.

Unsafe examples are stored as fragments and joined only while running.
This keeps the scaffold inspectable without embedding blocked phrases
as contiguous source text.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

SCHEMA_VERSION = "aiweb-authority-scanner-scaffold-v1"
SCANNER_STATUS = "scanner_scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"


@dataclass(frozen=True)
class UnsafePhrase:
    category: str
    phrase: str


def _join(parts: Sequence[str]) -> str:
    return "".join(parts)


def _unsafe_fragment_catalog() -> Dict[str, Tuple[Tuple[str, ...], ...]]:
    return {
        "public_claim_overreach": (
            ("production", "-", "ready"),
            ("production", " ", "ready"),
            ("release", " ", "authorized"),
            ("public", " ", "delivery", " ", "authorized"),
            ("actions", " ", "enabled"),
        ),
        "baseline_failure_path_overclaim": (
            ("GP", "-014", " ", "superseded"),
            ("GP", "-014", " ", "replaced"),
            ("GP", "014", " ", "superseded"),
            ("GP", "015", " ", "repaired"),
            ("GP", "-015", " ", "repaired"),
            ("GP", "015R1", " ", "installed"),
            ("GP", "-015R1", " ", "installed"),
        ),
        "model_or_opaque_authority": (
            ("l", "l", "m", " ", "authority", " ", "enabled"),
            ("model", " ", "confidence", " ", "gate"),
            ("neural", " ", "parser"),
            ("learned", " ", "classifier"),
            ("opaque", " ", "learned"),
            ("O", "ll", "ama"),
            ("Open", "A", "I"),
            ("anth", "ropic"),
            ("G", "P", "T"),
            ("Cl", "aude"),
        ),
        "retrieval_or_similarity_authority": (
            ("embedding", " ", "authority"),
            ("vector", " ", "authority"),
            ("semantic", " ", "similarity", " ", "authority"),
            ("similarity", " ", "decides"),
            ("nearest", "-", "neighbor", " ", "authority"),
            ("R", "A", "G", " ", "path"),
            ("Ch", "roma"),
            ("chrom", "adb"),
            ("fa", "iss"),
            ("lang", "chain"),
        ),
        "stored_material_or_action_overreach": (
            ("memory", " ", "authority", " ", "enabled"),
            ("evidence", " ", "authority", " ", "enabled"),
            ("corpus", " ", "authority", " ", "enabled"),
            ("external", " ", "resource", " ", "authority", " ", "enabled"),
            ("UI", " ", "authority", " ", "enabled"),
            ("tool", " ", "routing", " ", "enabled"),
            ("delivery", " ", "authorized"),
        ),
    }


def assembled_unsafe_catalog() -> List[UnsafePhrase]:
    items: List[UnsafePhrase] = []
    for category, phrase_parts in _unsafe_fragment_catalog().items():
        for parts in phrase_parts:
            items.append(UnsafePhrase(category=category, phrase=_join(parts)))
    return items


def unsafe_phrases_by_category() -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    for item in assembled_unsafe_catalog():
        grouped.setdefault(item.category, []).append(item.phrase)
    return grouped


def scanner_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": SCANNER_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "live_routing": False,
        "live_memory_write": False,
        "external_update": False,
        "acceptance_authority": False,
        "release_authority": False,
        "readiness_authority": False,
        "baseline_replacement_authority": False,
        "failed_path_revival_authority": False,
        "unsafe_phrase_count": len(assembled_unsafe_catalog()),
        "scanner_only": True,
    }


def safe_demo_text() -> str:
    return (
        "This local scanner creates findings only. "
        "It does not grant runtime power, does not alter dependencies, "
        "and does not update live records."
    )


def unsafe_demo_text() -> str:
    pieces = [
        _join(("production", "-", "ready")),
        _join(("GP", "-014", " ", "superseded")),
        _join(("l", "l", "m", " ", "authority", " ", "enabled")),
        _join(("semantic", " ", "similarity", " ", "authority")),
        _join(("memory", " ", "authority", " ", "enabled")),
    ]
    return " / ".join(pieces)

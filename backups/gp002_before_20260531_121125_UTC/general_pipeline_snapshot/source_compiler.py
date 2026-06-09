"""General Learning-to-Answer Pipeline — source compiler (Build GP-001).

Turns instructional source text into a hash-bound SemanticSource: governed
concepts and governed solution procedures, with source ancestry.

Honesty boundary:
  Build GP-001 does not do open-ended knowledge extraction from arbitrary
  prose. It recognises which *known domains* the supplied text teaches, and
  binds those domains' relations as governed procedures with a source hash.
  This is how "learning" stays governed: the system only admits a procedure
  whose domain it can actually execute and verify. Uploading text about an
  unknown domain compiles concepts but grants no executable procedure, so the
  pipeline will still refuse questions it cannot verify.

  In-memory only. No persistence, no Chroma, no memory write in this build.
"""

from __future__ import annotations

import re
from typing import List

from .contracts import (
    SemanticSource,
    CompiledConcept,
    CompiledProcedure,
    canonical_hash,
)
from .domains import all_domains

# Keyword fingerprints that indicate a source teaches a given domain.
_DOMAIN_FINGERPRINTS = {
    "whole_number_arithmetic": ("add", "subtract", "multiply", "divide", "sum", "product", "arithmetic"),
    "fraction_change_capacity": ("fraction", "capacity", "full", "removed", "whole"),
}


def _raw_hash(text: str) -> str:
    return canonical_hash({"raw_text": text})


def compile_source(source_text: str, source_ref: str) -> SemanticSource:
    """Compile instructional text into a governed SemanticSource.

    `source_ref` is a human/audit reference for where the text came from
    (e.g. a filename + section). It is recorded as ancestry on every concept
    and procedure compiled from this text.
    """
    text = str(source_text)
    norm = " ".join(text.lower().split())
    raw_text_hash = _raw_hash(text)
    source_id = canonical_hash({"raw_text_hash": raw_text_hash, "source_ref": source_ref})[:24]

    concepts: List[CompiledConcept] = []
    procedures: List[CompiledProcedure] = []

    known_domain_ids = {d.domain_id for d in all_domains()}
    domain_relation = {d.domain_id: d.relation_text() for d in all_domains()}

    for domain_id, fingerprints in _DOMAIN_FINGERPRINTS.items():
        if domain_id not in known_domain_ids:
            continue
        hits = [w for w in fingerprints if re.search(r"\b" + re.escape(w), norm)]
        # Require at least two distinct fingerprint hits to admit a procedure,
        # so unrelated text does not accidentally grant executable authority.
        if len(hits) >= 2:
            procedures.append(
                CompiledProcedure(
                    procedure_id=canonical_hash({"d": domain_id, "s": source_id})[:16],
                    domain=domain_id,
                    relation_text=domain_relation[domain_id],
                    source_ref=source_ref,
                )
            )
            for term in hits:
                concepts.append(
                    CompiledConcept(
                        concept_id=canonical_hash({"t": term, "s": source_id})[:16],
                        term=term,
                        definition=f"term used by domain {domain_id}",
                        source_ref=source_ref,
                    )
                )

    return SemanticSource(
        source_id=source_id,
        raw_text_hash=raw_text_hash,
        concepts=concepts,
        procedures=procedures,
    )


__all__ = ["compile_source"]

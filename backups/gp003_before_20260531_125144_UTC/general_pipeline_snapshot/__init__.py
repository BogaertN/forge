"""General Learning-to-Answer Pipeline (Build GP-001).

The first real, non-fixture vertical slice of the architecture:

    learn from instructional text  ->  build an MEA problem manifest
    ->  execute exact domain math  ->  governed gate  ->  seal
    ->  compile RMC meaning        ->  generatively render language
    ->  Echo-approve the faithful answer  ->  return it

Build GP-001 ships two learned domains (whole-number arithmetic and the
fraction-change-capacity family) and refuses any question it has not learned,
rather than guessing. Capability grows by adding domains in `domains.py`; the
engine never changes.

Boundaries: in-memory only. No route, no UI, no LLM, no memory write, no
Chroma, no Identity Vault, no CT/ledger activity. It does not modify any
Build 005-010 file.
"""

from .contracts import (
    GENERAL_PIPELINE_BUILD_ID,
    GENERAL_PIPELINE_SCHEMA_VERSION,
    SemanticSource,
    ParsedQuestion,
    ExactSolution,
    MeaningManifest,
)
from .pipeline import (
    PipelineResult,
    learn,
    answer_question,
    learn_and_answer,
)
from .domains import all_domains, match_domain

__all__ = [
    "GENERAL_PIPELINE_BUILD_ID",
    "GENERAL_PIPELINE_SCHEMA_VERSION",
    "SemanticSource",
    "ParsedQuestion",
    "ExactSolution",
    "MeaningManifest",
    "PipelineResult",
    "learn",
    "answer_question",
    "learn_and_answer",
    "all_domains",
    "match_domain",
]

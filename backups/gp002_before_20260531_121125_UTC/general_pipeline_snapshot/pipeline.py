"""General Learning-to-Answer Pipeline — orchestrator (Build GP-001).

Wires the full motion the architecture was designed for, for the domains the
system has actually learned:

  instructional source text
    -> compile governed semantic source            (source_compiler)
  user question
    -> match a learned domain                       (domains.match_domain)
    -> parse into typed quantities                  (domain.parse)
    -> build a real MEA ProblemManifest             (manifest_builder)
    -> execute exact arithmetic + verify            (domain.execute)
    -> governed gate decides if it may seal         (governed_gate.evaluate_gate)
    -> seal manifest to RESOLVED / RENDER_ALLOWED   (governed_gate.apply_seal)
    -> compile RMC meaning manifest                 (meaning_and_renderer.compile_meaning)
    -> generatively render natural language         (meaning_and_renderer.render)
    -> Echo approves the faithful rendering         (echo_approval.validate_and_approve)
    -> return the approved answer

Honesty boundary (Build GP-001):
  - If no learned domain matches the question, the pipeline REFUSES with a clear
    message. It never guesses an answer to an unrecognised question.
  - If the governed gate fails, no answer is delivered.
  - If Echo rejects the rendering, no answer is delivered.
  - In-memory only: no route, no UI, no memory write, no Chroma, no Identity
    Vault, no CT/ledger activity.

Return value is a structured PipelineResult with the answer (when approved) and
the full audited trace of every stage, each hashed for replay/inspection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from rmc_engine_v1.mea.manifest_schema import (
    ProblemManifest,
    canonical_hash as manifest_hash,
    to_dict as manifest_to_dict,
)

from .contracts import (
    SemanticSource,
    canonical_hash,
    GENERAL_PIPELINE_BUILD_ID,
    GENERAL_PIPELINE_SCHEMA_VERSION,
)
from .domains import match_domain
from .source_compiler import compile_source
from .manifest_builder import build_problem_manifest
from .governed_gate import evaluate_gate, apply_seal
from .meaning_and_renderer import compile_meaning, render
from .echo_approval import validate_and_approve


@dataclass
class PipelineResult:
    status: str  # "ANSWERED" | "REFUSED_UNLEARNED" | "GATE_BLOCKED" | "ECHO_REJECTED"
    question: str
    answer_text: Optional[str] = None
    domain: Optional[str] = None
    trace: Dict[str, Any] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "build_id": GENERAL_PIPELINE_BUILD_ID,
            "schema_version": GENERAL_PIPELINE_SCHEMA_VERSION,
            "status": self.status,
            "question": self.question,
            "answer_text": self.answer_text,
            "domain": self.domain,
            "trace": self.trace,
            "reasons": list(self.reasons),
        }

    def result_hash(self) -> str:
        # Deterministic content hash: exclude wall-clock timestamps that the
        # engine stamps into manifests (created_at/updated_at), so identical
        # inputs produce an identical hash across runs.
        payload = self.to_dict()
        trace = dict(payload.get("trace", {}))
        for key in ("open_manifest", "sealed_manifest"):
            man = trace.get(key)
            if isinstance(man, dict):
                man = {k: v for k, v in man.items() if k not in ("created_at", "updated_at")}
                trace[key] = man
        payload["trace"] = trace
        return canonical_hash(payload)


def learn(source_text: str, source_ref: str) -> SemanticSource:
    """Public entry point for the learning stage."""
    return compile_source(source_text, source_ref)


def answer_question(question: str, source: SemanticSource) -> PipelineResult:
    """Run the full pipeline for one question against a compiled source."""
    domain = match_domain(question)
    if domain is None:
        return PipelineResult(
            status="REFUSED_UNLEARNED",
            question=question,
            reasons=[
                "no learned domain recognises this question; "
                "the system refuses rather than guessing"
            ],
        )

    if not source.supports_domain(domain.domain_id):
        return PipelineResult(
            status="REFUSED_UNLEARNED",
            question=question,
            domain=domain.domain_id,
            reasons=[
                f"question matches domain {domain.domain_id!r} but the compiled "
                f"source does not authorise it; upload instructional text for this domain first"
            ],
        )

    parsed = domain.parse(question)
    if parsed is None:  # pragma: no cover - match implies parse
        return PipelineResult(
            status="REFUSED_UNLEARNED",
            question=question,
            domain=domain.domain_id,
            reasons=["domain matched but parsing failed"],
        )

    manifest = build_problem_manifest(parsed, source)
    solution = domain.execute(parsed)
    gate = evaluate_gate(manifest, solution, source)

    trace: Dict[str, Any] = {
        "parsed_question": parsed.to_dict(),
        "open_manifest_hash": manifest_hash(manifest),
        "open_manifest": manifest_to_dict(manifest),
        "solution": solution.to_dict(),
        "gate": gate.to_dict(),
        "gate_hash": gate.gate_hash(),
    }

    if not gate.passed:
        return PipelineResult(
            status="GATE_BLOCKED",
            question=question,
            domain=domain.domain_id,
            trace=trace,
            reasons=gate.reasons,
        )

    sealed = apply_seal(manifest, solution)
    source_ref = source.procedure_for_domain(domain.domain_id).source_ref
    meaning = compile_meaning(sealed, parsed, solution, source_ref)
    rendered = render(meaning)
    echo = validate_and_approve(meaning, rendered)

    trace.update({
        "sealed_manifest_hash": manifest_hash(sealed),
        "sealed_manifest": manifest_to_dict(sealed),
        "meaning_manifest": meaning.to_dict(),
        "meaning_hash": meaning.meaning_hash(),
        "rendered_text": rendered,
        "echo": echo.to_dict(),
        "echo_hash": echo.echo_hash(),
    })

    if not echo.approved_output:
        return PipelineResult(
            status="ECHO_REJECTED",
            question=question,
            domain=domain.domain_id,
            trace=trace,
            reasons=echo.failure_reasons,
        )

    return PipelineResult(
        status="ANSWERED",
        question=question,
        answer_text=echo.approved_text,
        domain=domain.domain_id,
        trace=trace,
    )


def learn_and_answer(source_text: str, source_ref: str, question: str) -> PipelineResult:
    """Convenience: compile a source then answer one question against it."""
    source = learn(source_text, source_ref)
    return answer_question(question, source)


__all__ = [
    "PipelineResult",
    "learn",
    "answer_question",
    "learn_and_answer",
    "GENERAL_PIPELINE_BUILD_ID",
    "GENERAL_PIPELINE_SCHEMA_VERSION",
]

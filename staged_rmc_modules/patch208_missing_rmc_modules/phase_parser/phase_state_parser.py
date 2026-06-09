"""
Phase State Parser — RMC Module 1 (S19AE rebuild)

Maps situated input text into the Φ1-Φ9 recursive phase state space.
This module is intentionally stdlib-only and inspectable.

Primary runtime import expected by the existing orchestrator:
    from phase_parser.phase_state_parser import PhaseStateParser

Compatibility aliases are staged separately for the logical architecture name:
    phase_state_parser.phase_state_parser
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Tuple


PHASES: Dict[int, Dict[str, str]] = {
    1: {"token": "initiation_pulse", "name": "Initiation Pulse", "role": "new loop / seed"},
    2: {"token": "polarity", "name": "Polarity", "role": "contrast / opposition"},
    3: {"token": "desire", "name": "Desire", "role": "goal / vector"},
    4: {"token": "friction", "name": "Friction", "role": "constraint / obstacle"},
    5: {"token": "entropy", "name": "Entropy", "role": "drift / instability"},
    6: {"token": "grace", "name": "Grace", "role": "correction / return"},
    7: {"token": "naming", "name": "Naming", "role": "definition / identity lock"},
    8: {"token": "power", "name": "Power", "role": "projection / implementation"},
    9: {"token": "recursive_evolution", "name": "Recursive Evolution", "role": "closure / next octave"},
}

TOKEN_TO_PHASE = {v["token"]: k for k, v in PHASES.items()}


@dataclass
class PhaseCue:
    phase: int
    cue: str
    weight: float
    reason: str

    def to_dict(self) -> Dict:
        return {
            "phase": self.phase,
            "phase_token": PHASES[self.phase]["token"],
            "phase_name": PHASES[self.phase]["name"],
            "cue": self.cue,
            "weight": self.weight,
            "reason": self.reason,
        }


@dataclass
class PhaseState:
    phase_id: int
    confidence: float
    cues: List[PhaseCue] = field(default_factory=list)
    secondary_phases: List[int] = field(default_factory=list)
    phase_path_hypothesis: List[int] = field(default_factory=list)
    routing: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        meta = PHASES[self.phase_id]
        return {
            # Legacy key used by existing S19AK orchestrator.
            "phase": meta["token"],
            # Numeric keys used by the compiler-facing architecture.
            "phase_id": self.phase_id,
            "phase_number": self.phase_id,
            "phase_name": meta["name"],
            "phase_role": meta["role"],
            "confidence": round(max(0.0, min(1.0, self.confidence)), 4),
            "secondary_phases": self.secondary_phases,
            "phase_path_hypothesis": self.phase_path_hypothesis,
            "routing": self.routing,
            "warnings": self.warnings,
            "cues": [cue.to_dict() for cue in self.cues],
            "timestamp": self.timestamp,
        }


class PhaseStateParser:
    """
    Rule-assisted parser for the Φ1-Φ9 RMC state space.

    The first implementation is intentionally explicit rather than clever:
    text cues, command intent, punctuation, and projection/correction language
    all vote toward a phase. Later versions can replace the cue scorer without
    changing the returned object shape.
    """

    CUE_TABLE: Dict[int, List[Tuple[str, float, str]]] = {
        1: [
            (r"\b(start|begin|new|first|seed|initiate|bootstrap|open)\b", 1.0, "new loop cue"),
            (r"\bidea|thought|question\b", 0.45, "seed concept cue"),
        ],
        2: [
            (r"\b(vs|versus|compare|difference|opposite|contrast|between|both sides)\b", 1.0, "polarity cue"),
            (r"\bor\b", 0.3, "choice cue"),
        ],
        3: [
            (r"\b(want|need|trying|goal|plan|build|make|create|help me|let's)\b", 0.9, "goal/vector cue"),
            (r"\?\s*$", 0.45, "question seeking direction"),
        ],
        4: [
            (r"\b(problem|issue|stuck|blocked|error|fail|missing|can't|cannot|wrong|bug)\b", 1.0, "constraint/friction cue"),
            (r"\bbut\b", 0.35, "resistance cue"),
        ],
        5: [
            (r"\b(confused|drift|spiral|collapse|chaos|unstable|hallucinat|lost|tangled|mess)\b", 1.0, "entropy/drift cue"),
            (r"\bmaybe.*maybe|i don't know|not sure\b", 0.6, "uncertainty cue"),
        ],
        6: [
            (r"\b(fix|repair|correct|ground|realign|rebuild|restore|clean up|verify|audit|check)\b", 1.0, "correction cue"),
            (r"\bdo it correctly|needs to be perfect|properly\b", 0.9, "quality correction cue"),
        ],
        7: [
            (r"\b(name|define|definition|call it|classify|label|identity|manifest)\b", 1.0, "naming cue"),
            (r"\bis called\b", 0.6, "declaration cue"),
        ],
        8: [
            (r"\b(project|publish|deploy|send|execute|implement|install|run|apply|wire|integrate|launch)\b", 1.0, "projection cue"),
            (r"\bnow\b", 0.25, "execution urgency cue"),
        ],
        9: [
            (r"\b(final|finish|complete|close|seal|archive|handover|summary|next octave|wrap up)\b", 1.0, "closure cue"),
            (r"\bfrom here|moving forward|next step\b", 0.55, "transition cue"),
        ],
    }

    ROUTING_BY_PHASE = {
        1: ["memory_recaller", "candidate_generator"],
        2: ["memory_recaller", "candidate_generator"],
        3: ["memory_recaller", "candidate_generator"],
        4: ["memory_recaller", "drift_analyzer", "correction_engine"],
        5: ["drift_analyzer", "correction_engine"],
        6: ["drift_analyzer", "correction_engine", "naming_engine"],
        7: ["memory_recaller", "naming_engine"],
        8: ["drift_analyzer", "projection_gate", "output_renderer"],
        9: ["echo_validator", "memory_writer"],
    }

    def parse(self, input_text: str, context: Dict | None = None) -> Dict:
        state = self.parse_state(input_text, context=context)
        return state.to_dict()

    def parse_state(self, input_text: str, context: Dict | None = None) -> PhaseState:
        text = input_text or ""
        context = context or {}
        scores: Dict[int, float] = {phase: 0.0 for phase in PHASES}
        cues: List[PhaseCue] = []
        lower = text.lower()

        for phase, patterns in self.CUE_TABLE.items():
            for pattern, weight, reason in patterns:
                if re.search(pattern, lower, flags=re.IGNORECASE):
                    scores[phase] += weight
                    cues.append(PhaseCue(phase=phase, cue=pattern, weight=weight, reason=reason))

        # Empty or tiny input remains initiation unless it is malformed enough for drift.
        if not lower.strip():
            scores[1] += 1.0
            cues.append(PhaseCue(1, "<empty>", 1.0, "empty input starts/no-ops a loop"))

        # Explicit phase tokens/notation override weak language cues.
        explicit = self._detect_explicit_phase(lower)
        if explicit:
            scores[explicit] += 2.0
            cues.append(PhaseCue(explicit, f"explicit_phase_{explicit}", 2.0, "explicit phase notation"))

        # Context can bias the parser without owning the result.
        prior_phase = self._coerce_phase(context.get("prior_phase"))
        if prior_phase:
            # Staying near the prior phase is a weak stabilizer.
            scores[prior_phase] += 0.15
            if prior_phase < 9:
                scores[prior_phase + 1] += 0.1
            elif prior_phase == 9:
                scores[1] += 0.1

        # Default if no meaningful cue appears.
        if max(scores.values()) <= 0:
            scores[1] = 0.4
            cues.append(PhaseCue(1, "default", 0.4, "default initiation for unclassified input"))

        phase_id = max(scores.items(), key=lambda item: (item[1], -item[0]))[0]
        total = sum(scores.values()) or 1.0
        confidence = scores[phase_id] / total
        # Keep confidence practical for simple cue parses.
        confidence = max(0.35, min(0.95, confidence))

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        secondary = [p for p, score in ranked[1:4] if score > 0]
        path = self._infer_path(prior_phase, phase_id, secondary)
        warnings = self._warnings_for_path(path, phase_id)

        return PhaseState(
            phase_id=phase_id,
            confidence=confidence,
            cues=cues,
            secondary_phases=secondary,
            phase_path_hypothesis=path,
            routing=self.ROUTING_BY_PHASE.get(phase_id, []),
            warnings=warnings,
        )

    def _detect_explicit_phase(self, text: str) -> int | None:
        match = re.search(r"(?:φ|phi|phase)\s*([1-9])", text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
        for token, phase in TOKEN_TO_PHASE.items():
            if token in text:
                return phase
        return None

    def _coerce_phase(self, value) -> int | None:
        if value is None:
            return None
        if isinstance(value, int) and 1 <= value <= 9:
            return value
        if isinstance(value, str):
            v = value.strip().lower()
            if v.isdigit() and 1 <= int(v) <= 9:
                return int(v)
            return TOKEN_TO_PHASE.get(v)
        return None

    def _infer_path(self, prior_phase: int | None, phase_id: int, secondary: List[int]) -> List[int]:
        if prior_phase and prior_phase != phase_id:
            return [prior_phase, phase_id]
        if 5 in secondary and phase_id in (6, 7, 8):
            return [5, phase_id]
        if phase_id == 8 and 6 not in secondary and 7 not in secondary:
            return [phase_id]
        return [phase_id]

    def _warnings_for_path(self, path: List[int], phase_id: int) -> List[str]:
        warnings: List[str] = []
        if len(path) >= 2 and path[-2:] in ([5, 8], [4, 8]):
            warnings.append("projection_attempt_from_uncorrected_drift_or_friction")
        if phase_id == 8 and not any(p in path for p in (6, 7)):
            warnings.append("projection_requires_prior_correction_and_naming")
        return warnings


if __name__ == "__main__":
    parser = PhaseStateParser()
    for sample in [
        "start the new RMC rebuild",
        "this is wrong and needs to be corrected",
        "ship it now",
        "define the echo gate",
        "final handover summary",
    ]:
        print(sample)
        print(parser.parse(sample))

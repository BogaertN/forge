"""
Drift Detection Runtime — RMC Module 3
Detects three types of drift before they corrupt output.

Syntactic drift  — malformed, broken, or structurally invalid statements
Semantic drift   — meaning of a concept is shifting across the conversation
Recursive drift  — phase is being skipped (Luciferian skip) or looping

A DriftEvent is raised when drift is detected. The system can then
decide to correct, flag, or block the output before it propagates.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field


# ── DRIFT EVENT ────────────────────────────────────────────────────

@dataclass
class DriftEvent:
    drift_type: str          # "syntactic" | "semantic" | "recursive"
    severity: float          # 0.0 (low) to 1.0 (critical)
    description: str
    signal: str              # what triggered it
    phase: int               # phase where drift was detected
    correctable: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            'drift_type': self.drift_type,
            'severity': self.severity,
            'description': self.description,
            'signal': self.signal,
            'phase': self.phase,
            'correctable': self.correctable,
            'timestamp': self.timestamp,
        }


# ── SYNTACTIC DRIFT ────────────────────────────────────────────────

class SyntacticDriftDetector:
    """
    Detects structurally malformed or broken statements.
    Examples: incomplete sentences, broken logic, contradictory structure.
    """

    def detect(self, text: str, phase: int) -> List[DriftEvent]:
        events = []

        # Incomplete sentence — ends abruptly without punctuation or completion
        if text.strip() and not re.search(r'[.!?:)\]"\'…]$', text.strip()):
            if len(text.split()) >= 3:
                events.append(DriftEvent(
                    drift_type="syntactic",
                    severity=0.3,
                    description="Statement appears incomplete — no terminal punctuation",
                    signal=text[-20:],
                    phase=phase,
                    correctable=True
                ))

        # Contradiction markers — "but" immediately contradicting itself
        if re.search(r'\b(yes\s+but\s+no|no\s+but\s+yes|true\s+but\s+false)\b', text, re.IGNORECASE):
            events.append(DriftEvent(
                drift_type="syntactic",
                severity=0.6,
                description="Direct contradiction detected in statement",
                signal=re.search(r'\b(yes\s+but\s+no|no\s+but\s+yes|true\s+but\s+false)\b',
                                  text, re.IGNORECASE).group(),
                phase=phase,
                correctable=True
            ))

        # Excessive hedging — meaning dissolves into uncertainty
        hedge_count = len(re.findall(
            r'\b(maybe|perhaps|possibly|might|could|sort\s+of|kind\s+of|somewhat)\b',
            text, re.IGNORECASE))
        if hedge_count >= 3:
            events.append(DriftEvent(
                drift_type="syntactic",
                severity=0.4,
                description=f"Excessive hedging ({hedge_count} qualifiers) — meaning unclear",
                signal=f"{hedge_count} hedge words",
                phase=phase,
                correctable=True
            ))

        # Repetition — same phrase repeated (sign of loop)
        words = text.lower().split()
        if len(words) > 6:
            for i in range(len(words) - 3):
                phrase = ' '.join(words[i:i+3])
                rest = ' '.join(words[i+3:])
                if phrase in rest:
                    events.append(DriftEvent(
                        drift_type="syntactic",
                        severity=0.5,
                        description="Phrase repetition detected — possible loop",
                        signal=phrase,
                        phase=phase,
                        correctable=True
                    ))
                    break

        return events


# ── SEMANTIC DRIFT ─────────────────────────────────────────────────

class SemanticDriftDetector:
    """
    Detects when the meaning of key concepts shifts across a conversation.
    Tracks term definitions and flags when the same term is used differently.
    """

    def __init__(self):
        self.term_registry: Dict[str, List[str]] = {}

    def register_term(self, term: str, definition: str):
        """Register how a term is being used"""
        term_lower = term.lower()
        if term_lower not in self.term_registry:
            self.term_registry[term_lower] = []
        self.term_registry[term_lower].append(definition)

    def detect(self, text: str, phase: int) -> List[DriftEvent]:
        events = []

        # Detect scope shift signals
        scope_shifts = re.findall(
            r'\b(actually|in\s+fact|what\s+I\s+meant|to\s+clarify|'
            r'I\s+mean|rather|instead|correction)\b',
            text, re.IGNORECASE)
        if len(scope_shifts) >= 2:
            events.append(DriftEvent(
                drift_type="semantic",
                severity=0.5,
                description="Multiple meaning corrections in one statement — semantic instability",
                signal=', '.join(scope_shifts[:3]),
                phase=phase,
                correctable=True
            ))

        # Detect conflicting certainty levels in same statement
        certain = len(re.findall(r'\b(definitely|certainly|always|never|must|will)\b',
                                  text, re.IGNORECASE))
        uncertain = len(re.findall(r'\b(maybe|sometimes|might|could|possibly|perhaps)\b',
                                    text, re.IGNORECASE))
        if certain >= 1 and uncertain >= 2:
            events.append(DriftEvent(
                drift_type="semantic",
                severity=0.4,
                description="Conflicting certainty levels — statement is semantically unstable",
                signal=f"{certain} certain + {uncertain} uncertain markers",
                phase=phase,
                correctable=True
            ))

        # Detect concept redefinition mid-statement
        if re.search(r'\b(now\s+means?|redefin\w+|no\s+longer\s+means?|'
                     r'has\s+changed\s+to|used\s+to\s+mean)\b', text, re.IGNORECASE):
            events.append(DriftEvent(
                drift_type="semantic",
                severity=0.7,
                description="Concept redefinition detected mid-conversation",
                signal="redefinition marker",
                phase=phase,
                correctable=True
            ))

        return events


# ── RECURSIVE DRIFT ────────────────────────────────────────────────

class RecursiveDriftDetector:
    """
    Detects phase skipping (Luciferian skips) and stuck loops.
    Works with the phase history to identify invalid transitions
    and phases that are cycling without progress.
    """

    FORBIDDEN = {
        1: [8, 9],
        2: [8, 9],
        3: [7, 9],
        4: [8, 9],
        5: [7, 8, 9],
    }

    def detect(self, current_phase: int, phase_history: List[int]) -> List[DriftEvent]:
        events = []

        if not phase_history:
            return events

        previous_phase = phase_history[-1]

        # Luciferian skip — forbidden phase jump
        if previous_phase in self.FORBIDDEN:
            if current_phase in self.FORBIDDEN[previous_phase]:
                events.append(DriftEvent(
                    drift_type="recursive",
                    severity=0.9,
                    description=f"Luciferian skip: Phase {previous_phase} → {current_phase} "
                                f"bypasses required intermediate phases",
                    signal=f"{previous_phase}→{current_phase}",
                    phase=current_phase,
                    correctable=True
                ))

        # Stuck loop — same phase repeating too many times
        if len(phase_history) >= 4:
            recent = phase_history[-4:]
            if len(set(recent)) == 1:
                stuck_phase = recent[0]
                events.append(DriftEvent(
                    drift_type="recursive",
                    severity=0.6,
                    description=f"Phase {stuck_phase} has repeated 4+ times — system may be stuck",
                    signal=f"phase {stuck_phase} x{len(recent)}",
                    phase=current_phase,
                    correctable=True
                ))

        # Entropy without Grace — Phase 5 appearing without Phase 6 following
        if len(phase_history) >= 3:
            if phase_history[-3] == 5 and phase_history[-2] == 5 and current_phase == 5:
                events.append(DriftEvent(
                    drift_type="recursive",
                    severity=0.8,
                    description="System in sustained Entropy (Phase 5) — Grace (Phase 6) required",
                    signal="phase 5 x3",
                    phase=current_phase,
                    correctable=True
                ))

        # Rapid cycling — bouncing between two phases
        if len(phase_history) >= 6:
            recent6 = phase_history[-6:]
            unique = set(recent6)
            if len(unique) == 2:
                events.append(DriftEvent(
                    drift_type="recursive",
                    severity=0.5,
                    description=f"Rapid cycling between phases {sorted(unique)} — no forward progress",
                    signal=f"alternating {sorted(unique)}",
                    phase=current_phase,
                    correctable=True
                ))

        return events


# ── DRIFT ARBITRATOR ───────────────────────────────────────────────

class DriftArbitrator:
    """
    Runs all three detectors and produces a combined drift report.
    Decides whether to ALLOW, WARN, or BLOCK based on severity.
    """

    BLOCK_THRESHOLD = 0.85
    WARN_THRESHOLD  = 0.4

    def __init__(self):
        self.syntactic  = SyntacticDriftDetector()
        self.semantic   = SemanticDriftDetector()
        self.recursive  = RecursiveDriftDetector()

    def evaluate(self, text: str, current_phase: int,
                 phase_history: Optional[List[int]] = None) -> Dict:
        """
        Evaluate text for all drift types.
        Returns a report with verdict: ALLOW | WARN | BLOCK
        """
        all_events: List[DriftEvent] = []

        all_events.extend(self.syntactic.detect(text, current_phase))
        all_events.extend(self.semantic.detect(text, current_phase))
        if phase_history:
            all_events.extend(self.recursive.detect(current_phase, phase_history))

        max_severity = max((e.severity for e in all_events), default=0.0)

        if max_severity >= self.BLOCK_THRESHOLD:
            verdict = "BLOCK"
        elif max_severity >= self.WARN_THRESHOLD:
            verdict = "WARN"
        else:
            verdict = "ALLOW"

        return {
            'verdict': verdict,
            'max_severity': max_severity,
            'event_count': len(all_events),
            'events': [e.to_dict() for e in all_events],
            'phase': current_phase,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }


if __name__ == "__main__":
    print("=== Drift Detection Runtime — Quick Test ===\n")

    arb = DriftArbitrator()

    tests = [
        ("This is a clean, well-formed statement.", 3, [], "ALLOW"),
        ("Maybe perhaps it could possibly sort of be somewhat true", 3, [], "WARN"),
        ("yes but no that is true but false", 2, [], "WARN"),
        ("I want to build", 3, [1, 2], "ALLOW"),          # valid Phase 3, low sev note only
        ("Let's ship it now", 8, [1, 2], "BLOCK"),        # Luciferian skip 2→8
        ("Let's build it", 8, [7], "ALLOW"),              # valid 7→8
    ]

    for text, phase, history, expected in tests:
        result = arb.evaluate(text, phase, history)
        verdict = result['verdict']
        status = "✅" if verdict == expected else "❌"
        print(f"{status} [{verdict:5s}] Phase {phase} | {text[:45]}")
        if result['events']:
            for e in result['events']:
                print(f"       ↳ {e['drift_type']:10s} | sev {e['severity']:.1f} | {e['description'][:55]}")
    print()

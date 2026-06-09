"""
Manifest Compiler — RMC Module 4
The core of the Recursive Manifest Compiler.

Takes input from all three prior modules and produces a Manifest —
a traceable symbolic object that exists BEFORE any language is rendered.

Pipeline:
    PhaseState   (from Module 1)
    MemoryRecord (from Module 2)
    DriftReport  (from Module 3)
         ↓
    CandidatePaths  — possible meaning paths given the above
         ↓
    CoherenceCheck  — validates each candidate against phase + drift rules
         ↓
    Manifest        — the selected, validated, traceable meaning object
         ↓
    (output rendering happens AFTER this — Module 5)

The manifest is the audit-bearing object. The sentence is one projection of it.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from typing import Tuple


# ── CANDIDATE PATH ─────────────────────────────────────────────────

@dataclass
class CandidatePath:
    """A possible meaning path — what the system might conclude"""
    id: str
    description: str        # What this path claims
    phase: int              # Phase this path belongs to
    confidence: float       # How confident we are (0.0-1.0)
    novelty: float          # How new/different this is (0.0-1.0)
    memory_ids: List[str]   # Memory records that support this path
    drift_clean: bool       # Did drift detection pass for this path?

    def is_viable(self) -> bool:
        """A path is viable if it's drift-clean and has reasonable confidence"""
        return self.drift_clean and self.confidence >= 0.3


# ── MANIFEST ───────────────────────────────────────────────────────

@dataclass
class Manifest:
    """
    The traceable symbolic object produced before language rendering.
    Everything that goes into the output must be traceable to this manifest.
    """
    id: str
    conclusion: str                 # The selected meaning
    phase: int                      # Phase this manifest belongs to
    phase_name: str
    confidence: float               # Confidence in the conclusion
    novelty: float                  # How novel this conclusion is
    memory_ids: List[str]           # Memory records used
    drift_verdict: str              # ALLOW | WARN | BLOCK
    drift_events: List[Dict]        # All drift events detected
    candidate_count: int            # How many paths were evaluated
    selected_path_id: str           # Which candidate was chosen
    phase_history: List[int]        # Phase history at time of compilation
    projection_status: str          # READY | HELD | BLOCKED
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    claim_type: str = "assertion"   # assertion | question | instruction | observation
    output_modalities: List[str] = field(default_factory=lambda: ["language"])

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'conclusion': self.conclusion,
            'phase': self.phase,
            'phase_name': self.phase_name,
            'confidence': self.confidence,
            'novelty': self.novelty,
            'memory_ids': self.memory_ids,
            'drift_verdict': self.drift_verdict,
            'drift_events': self.drift_events,
            'candidate_count': self.candidate_count,
            'selected_path_id': self.selected_path_id,
            'phase_history': self.phase_history,
            'projection_status': self.projection_status,
            'timestamp': self.timestamp,
            'claim_type': self.claim_type,
            'output_modalities': self.output_modalities,
        }

    def is_ready(self) -> bool:
        return self.projection_status == "READY"

    def is_blocked(self) -> bool:
        return self.projection_status == "BLOCKED"


# ── CANDIDATE PATH GENERATOR ───────────────────────────────────────

class CandidatePathGenerator:
    """
    Generates candidate meaning paths from phase state and memory.
    Bounded novelty — paths may differ from memory but must stay
    within phase-valid limits.
    """

    def generate(self, input_text: str, phase: int,
                 memory_records: List[Dict],
                 drift_verdict: str) -> List[CandidatePath]:
        """Generate candidate paths from input and context"""
        candidates = []

        # Path 1: Direct — take the input at face value
        # Phase 9 and questions get novelty boost — evolution IS the novel move
        base_novelty = 0.6 if phase == 9 else (0.5 if input_text.strip().endswith('?') else 0.1)
        direct = CandidatePath(
            id=str(uuid.uuid4())[:8],
            description=input_text.strip(),
            phase=phase,
            confidence=0.8,
            novelty=base_novelty,
            memory_ids=[],
            drift_clean=(drift_verdict != "BLOCK")
        )
        candidates.append(direct)

        # Path 2: Memory-grounded — if we have relevant memories, use them
        if memory_records:
            top_memory = memory_records[0]
            memory_grounded = CandidatePath(
                id=str(uuid.uuid4())[:8],
                description=f"{input_text.strip()} [grounded in: {top_memory.get('content', '')[:60]}]",
                phase=phase,
                confidence=min(1.0, 0.7 + top_memory.get('confidence', 0.5) * 0.2),
                novelty=0.2,
                memory_ids=[top_memory.get('id', '')] if top_memory.get('id') else [],
                drift_clean=(drift_verdict != "BLOCK")
            )
            candidates.append(memory_grounded)

        # Path 3: Conservative — lower confidence, acknowledges uncertainty
        # Only generated when drift is present
        if drift_verdict in ("WARN", "BLOCK"):
            conservative = CandidatePath(
                id=str(uuid.uuid4())[:8],
                description=f"[uncertain] {input_text.strip()}",
                phase=phase,
                confidence=0.4,
                novelty=0.0,
                memory_ids=[],
                drift_clean=True   # Conservative path is always drift-clean
            )
            candidates.append(conservative)

        return candidates


# ── COHERENCE VALIDATOR ────────────────────────────────────────────

class CoherenceValidator:
    """
    Validates candidate paths before they become manifests.
    Checks phase validity, confidence thresholds, and drift cleanliness.
    """

    MIN_CONFIDENCE = 0.3
    MIN_NOVELTY_FOR_EVOLUTION = 0.5  # Phase 9 needs meaningful novelty

    def validate(self, candidate: CandidatePath,
                 phase_history: List[int]) -> Tuple[bool, str]:
        """
        Returns (is_valid: bool, reason: str)
        """
        # Must be drift-clean
        if not candidate.drift_clean:
            return False, "Drift detected — path is not clean"

        # Must meet minimum confidence
        if candidate.confidence < self.MIN_CONFIDENCE:
            return False, f"Confidence {candidate.confidence:.2f} below minimum {self.MIN_CONFIDENCE}"

        # Phase 9 (Evolution) requires meaningful novelty
        if candidate.phase == 9 and candidate.novelty < self.MIN_NOVELTY_FOR_EVOLUTION:
            return False, "Phase 9 (Evolution) requires novelty >= 0.5"

        return True, "valid"

    def select_best(self, candidates: List[CandidatePath],
                    phase_history: List[int]) -> Optional[CandidatePath]:
        """Select the best viable candidate"""
        viable = []
        for c in candidates:
            valid, _ = self.validate(c, phase_history)
            if valid:
                viable.append(c)

        if not viable:
            return None

        # Score = confidence * (1 + novelty * 0.2)
        # Slight bonus for novelty, but confidence dominates
        viable.sort(key=lambda c: c.confidence * (1 + c.novelty * 0.2), reverse=True)
        return viable[0]


# Workaround for type hint without importing typing in dataclass


# ── MANIFEST COMPILER ──────────────────────────────────────────────

class ManifestCompiler:
    """
    The core RMC compiler.
    Takes phase state, memory, and drift report — produces a Manifest.
    """

    def __init__(self):
        self.generator = CandidatePathGenerator()
        self.validator = CoherenceValidator()

    def compile(self,
                input_text: str,
                phase_state: Dict,
                memory_records: List[Dict],
                drift_report: Dict,
                phase_history: Optional[List[int]] = None) -> Manifest:
        """
        Compile a manifest from all available inputs.

        Args:
            input_text:     Raw input from the user/system
            phase_state:    Output from PhaseStateParser.parse()
            memory_records: Output from AncestralMemory.retrieve() (as dicts)
            drift_report:   Output from DriftArbitrator.evaluate()
            phase_history:  List of previous phase numbers

        Returns:
            Manifest — the traceable symbolic object
        """
        phase = phase_state.get('phase', 1)
        phase_name = phase_state.get('phase_name', 'Unknown')
        drift_verdict = drift_report.get('verdict', 'ALLOW')
        drift_events = drift_report.get('events', [])
        history = phase_history or []

        # Generate candidate paths
        candidates = self.generator.generate(
            input_text, phase, memory_records, drift_verdict
        )

        # Select best candidate
        best = self.validator.select_best(candidates, history)

        # Determine projection status
        if drift_verdict == "BLOCK":
            projection_status = "BLOCKED"
        elif best is None:
            projection_status = "HELD"
        elif drift_verdict == "WARN":
            projection_status = "READY"   # WARN still allows, just flagged
        else:
            projection_status = "READY"

        # Build conclusion
        if best is not None:
            conclusion = best.description
            confidence = best.confidence
            novelty = best.novelty
            selected_id = best.id
            memory_ids = best.memory_ids
        else:
            # Fallback — no viable path found
            conclusion = f"[no viable path] {input_text.strip()}"
            confidence = 0.0
            novelty = 0.0
            selected_id = "none"
            memory_ids = []

        # Infer claim type from phase
        claim_type = self._infer_claim_type(phase, input_text)

        return Manifest(
            id=str(uuid.uuid4())[:8],
            conclusion=conclusion,
            phase=phase,
            phase_name=phase_name,
            confidence=confidence,
            novelty=novelty,
            memory_ids=memory_ids,
            drift_verdict=drift_verdict,
            drift_events=drift_events,
            candidate_count=len(candidates),
            selected_path_id=selected_id,
            phase_history=list(history),
            projection_status=projection_status,
            claim_type=claim_type,
        )

    def _infer_claim_type(self, phase: int, text: str) -> str:
        """Infer claim type from phase and text"""
        text_lower = text.lower().strip()
        if text_lower.endswith('?') or text_lower.startswith(('what', 'how', 'why', 'when', 'where', 'who')):
            return "question"
        if phase == 8:
            return "instruction"
        if phase in (1, 9):
            return "observation"
        return "assertion"


if __name__ == "__main__":
    print("=== Manifest Compiler — Quick Test ===\n")

    compiler = ManifestCompiler()

    # Simulate inputs from prior modules
    phase_state = {'phase': 3, 'phase_name': 'Desire', 'confidence': 0.9}
    memory_records = [
        {'id': 'abc123', 'content': 'User previously built a Python app', 'confidence': 0.85}
    ]
    drift_report_clean = {'verdict': 'ALLOW', 'events': [], 'max_severity': 0.0}
    drift_report_warn  = {'verdict': 'WARN',  'events': [{'drift_type': 'syntactic', 'severity': 0.4, 'description': 'Incomplete', 'signal': '...', 'phase': 3, 'correctable': True, 'timestamp': ''}], 'max_severity': 0.4}
    drift_report_block = {'verdict': 'BLOCK', 'events': [{'drift_type': 'recursive', 'severity': 0.9, 'description': 'Luciferian skip', 'signal': '1→8', 'phase': 8, 'correctable': True, 'timestamp': ''}], 'max_severity': 0.9}

    tests = [
        ("I want to build a web application", phase_state, memory_records, drift_report_clean, [1,2], "READY"),
        ("maybe I want to build something",   phase_state, [],             drift_report_warn,  [1,2], "READY"),
        ("ship it now",                        {'phase': 8, 'phase_name': 'Power'}, [], drift_report_block, [1,2], "BLOCKED"),
    ]

    for text, ps, mem, dr, history, expected_status in tests:
        m = compiler.compile(text, ps, mem, dr, history)
        status = "✅" if m.projection_status == expected_status else "❌"
        print(f"{status} [{m.projection_status:7s}] Phase {m.phase} | drift={m.drift_verdict:5s} | {text[:40]}")
        print(f"   Manifest [{m.id}] confidence={m.confidence:.2f} candidates={m.candidate_count} claim={m.claim_type}")
        print(f"   Conclusion: {m.conclusion[:70]}")
        print()

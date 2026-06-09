"""
Phase-State Parser — RMC Module 1 (v1.1)
Parses input into phase-state representations using the 9-phase framework.
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone


class PhaseStateParser:
    def __init__(self, forge_audit_callback=None):
        self.forge_audit = forge_audit_callback
        self.phase_detector = PhaseDetector()
        self.phase_validator = PhaseValidator()

    def parse(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if not input_text or not input_text.strip():
            return self._error_state("Empty input")
        phase, confidence, signals = self.phase_detector.detect(input_text)
        transition_valid = True
        if context and 'previous_phase' in context:
            transition_valid = self.phase_validator.validate_transition(
                context['previous_phase'], phase)
        phase_state = {
            'phase': phase,
            'phase_name': self._get_phase_name(phase),
            'confidence': confidence,
            'signals': signals,
            'transition_valid': transition_valid,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'input_snippet': input_text[:100] + ('...' if len(input_text) > 100 else '')
        }
        if self.forge_audit:
            self.forge_audit(phase, confidence, phase_state['input_snippet'])
        return phase_state

    def _get_phase_name(self, phase: int) -> str:
        names = {
            1: "Initiation Pulse", 2: "Polarity", 3: "Desire",
            4: "Friction",         5: "Entropy",  6: "Grace",
            7: "Naming",           8: "Power",    9: "Recursive Evolution"
        }
        return names.get(phase, "Unknown")

    def _error_state(self, error_msg: str) -> Dict:
        return {
            'phase': 0, 'phase_name': 'Error', 'confidence': 0.0,
            'signals': [], 'transition_valid': False,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'input_snippet': f"Error: {error_msg}", 'error': error_msg
        }


class PhaseDetector:
    def __init__(self):
        # Each phase has (phase_number, patterns, weight)
        # Weight > 1 means these signals count more — used to break ties
        self.all_patterns = [
            (1, [r'\b(start|begin|initial|first|new|fresh|launch)\b',
                 r'\b(what\s+is|tell\s+me|explain|introduce)\b',
                 r'\b(hello|hi|hey)\b'], 1),
            (2, [r'\b(versus|vs\.?|compared?\s+to|different|contrast)\b',
                 r'\b(either|or|which|choose|option)\b',
                 r'\b(pros?\s+and\s+cons?|advantage|disadvantage)\b'], 1),
            (3, [r'\b(want|need|wish|hope|goal|aim|intend)\b',
                 r'\b(should|would\s+like|prefer)\b',
                 r'\b(looking\s+for|seeking|trying\s+to)\b',
                 r'\b(how\s+can\s+I|help\s+me)\b'], 1),
            (4, [r'\b(problem|difficult|hard|stuck|blocked|can\'?t)\b',
                 r'\b(error|fail|broke|wrong|bug|crash)\b',
                 r'\b(but|however|although|despite|struggle)\b'], 1),
            (5, [r'\b(confus|overwhelm|chaos|mess|disorder|collapse)\b',
                 r'\b(lost|drift|uncertain|unclear|ambiguous)\b',
                 r'\b(don\'?t\s+know|no\s+idea|unsure)\b'], 1),
            # Phase 6 has weight 2 — correction words beat friction words
            (6, [r'\b(fix|correct|repair|restore|recover|heal)\b',
                 r'\b(reset|restart|try\s+again|retry)\b',
                 r'\b(adjust|refine|tune|calibrate|patch)\b'], 2),
            # Phase 7 matches "call", "called", "calling" etc.
            (7, [r'\b(defin\w*|nam\w+|call\w*|label\w*|identif\w*|specif\w*)\b',
                 r'\b(exact|precise|specific|particular)\b',
                 r'\b(finaliz\w*|lock\w*|seal\w*|commit\w*|decid\w*)\b',
                 r'\b(is\s+called|refers?\s+to|known\s+as|defined\s+as)\b'], 1),
            (8, [r'\b(create|build|make|produce|generate|construct)\b',
                 r'\b(execute|run|perform|implement|deploy)\b',
                 r'\b(show|display|present|demonstrate)\b'], 1),
            (9, [r'\b(complete|finish|done|end|conclude)\b',
                 r'\b(next|continue|again|repeat|iterate|cycle)\b',
                 r'\b(what\'?s\s+next|then\s+what|and\s+then)\b'], 1),
        ]

    def detect(self, input_text: str) -> Tuple[int, float, List[str]]:
        text_lower = input_text.lower()
        phase_scores = {}
        phase_signals = {}

        for phase_num, patterns, weight in self.all_patterns:
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                if found:
                    matches.extend(found)
            if matches:
                phase_scores[phase_num] = len(matches) * weight
                phase_signals[phase_num] = matches

        if not phase_scores:
            return 1, 0.3, ["default_initiation"]

        max_phase = max(phase_scores, key=phase_scores.get)
        max_score = phase_scores[max_phase]
        total_matches = sum(phase_scores.values())
        confidence = min(1.0, max_score / total_matches if total_matches > 0 else 0.3)
        if len(phase_scores) == 1:
            confidence = min(1.0, confidence + 0.2)
        return max_phase, confidence, phase_signals[max_phase]


class PhaseValidator:
    def __init__(self):
        self.valid_transitions = {
            1: [1, 2, 3], 2: [2, 3, 4], 3: [3, 4, 8],
            4: [4, 5, 6], 5: [5, 6],    6: [6, 7, 3],
            7: [7, 8],    8: [8, 9, 4], 9: [9, 1],
        }
        self.forbidden_transitions = {
            1: [8, 9], 2: [8, 9], 3: [7, 9],
            4: [8, 9], 5: [7, 8, 9],
        }

    def validate_transition(self, from_phase: int, to_phase: int) -> bool:
        if from_phase == to_phase:
            return True
        if from_phase in self.forbidden_transitions:
            if to_phase in self.forbidden_transitions[from_phase]:
                return False
        return True

    def get_valid_next_phases(self, current_phase: int) -> List[int]:
        return self.valid_transitions.get(current_phase, [])


def parse_phase(input_text: str, forge_audit_callback=None) -> Dict:
    parser = PhaseStateParser(forge_audit_callback)
    return parser.parse(input_text)


if __name__ == "__main__":
    print("=== Phase-State Parser v1.1 — Quick Test ===\n")
    parser = PhaseStateParser()
    tests = [
        ("Hello, starting a new project",        1),
        ("Should I use Python or JavaScript?",   2),
        ("I want to build a web application",    3),
        ("I'm stuck on this error",              4),
        ("Everything is confusing and unclear",  5),
        ("Let me fix this issue",                6),
        ("This is called the phase parser",      7),
        ("Let's build it now",                   8),
        ("Done! What's next?",                   9),
    ]
    passed = 0
    for text, expected in tests:
        r = parser.parse(text)
        status = "✅" if r['phase'] == expected else "❌"
        if r['phase'] == expected:
            passed += 1
        print(f"{status} Phase {r['phase']} ({r['phase_name']:20s}) | expected {expected} | {text}")
    print(f"\n{passed}/9 correct")

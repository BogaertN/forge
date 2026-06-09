"""
Drift Arbitrator — RMC Module 3 (S19AG rebuild)

Detects syntactic, semantic, structural, and recursive drift before a
candidate conclusion may become a manifest.

Primary runtime import expected by the existing orchestrator:
    from drift_detection.drift_detector import DriftArbitrator

Compatibility aliases are staged separately for the logical architecture name:
    drift_arbitrator.drift_arbitrator
"""

from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


@dataclass
class DriftEvent:
    drift_type: str
    severity: float
    description: str
    signal: str
    phase: int
    correctable: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            "drift_type": self.drift_type,
            "severity": round(max(0.0, min(1.0, self.severity)), 4),
            "description": self.description,
            "signal": self.signal,
            "phase": self.phase,
            "correctable": self.correctable,
            "timestamp": self.timestamp,
        }


class DriftArbitrator:
    """
    Rule-based, stdlib-only drift analyzer.

    It implements the first buildable form of the RMC drift contract:
    entropy + structure + semantic distance + phase deviation + transition
    validity + taxonomy + circuit breaker + χ(t)-style correction flag.
    """

    WARN_THRESHOLD = 0.35
    BLOCK_THRESHOLD = 0.72
    CIRCUIT_THRESHOLD = 0.82

    VALID_NEXT = {
        1: {1, 2, 3},
        2: {2, 3, 4},
        3: {3, 4, 5},
        4: {4, 5, 6},
        5: {5, 6},
        6: {6, 7},
        7: {7, 8, 9},
        8: {8, 9},
        9: {9, 1},
    }

    DANGEROUS_SKIPS = {(5, 8), (4, 8), (5, 9), (3, 8)}

    def __init__(self, history_window: int = 24):
        self.history_window = history_window
        self.recent_scores: List[float] = []
        self.circuit_open = False
        self.circuit_reason = ""

    def evaluate(self, text: str, current_phase: int, phase_history: List[int] | None = None,
                 expected_shape: Any | None = None, memory_baseline: str | None = None) -> Dict:
        phase_history = [p for p in (phase_history or []) if isinstance(p, int) and 1 <= p <= 9]
        current_phase = self._coerce_phase(current_phase)
        events: List[DriftEvent] = []

        entropy = self._shannon_norm(text or "")
        structure_status, structural_distance = self._structure_check(text, expected_shape)
        semantic_distance = self._semantic_distance(text or "", memory_baseline)
        phase_deviation, transition_validity = self._phase_deviation(current_phase, phase_history)

        # Syntactic firewall.
        if not (text or "").strip():
            events.append(DriftEvent("syntactic", 0.2, "empty input", "empty", current_phase, True))
        if len(text or "") > 4000:
            events.append(DriftEvent("syntactic", 0.6, "input exceeds safe first-pass size", "size>4000", current_phase, True))
        if entropy > 0.92 and len(text or "") >= 32:
            events.append(DriftEvent("syntactic", min(1.0, entropy), "high normalized Shannon entropy", f"H={entropy:.3f}", current_phase, True))
        if self._looks_like_repeated_noise(text or ""):
            events.append(DriftEvent("syntactic", 0.55, "repeated low-information sequence", "repeat_noise", current_phase, True))

        # Structural drift.
        if structural_distance > 0.5:
            events.append(DriftEvent("structural", structural_distance, "object structure changed beyond threshold", f"Jdist={structural_distance:.3f}", current_phase, True))
        elif structure_status != "valid":
            events.append(DriftEvent("structural", 0.35, structure_status, structure_status, current_phase, True))

        # Semantic drift / uncertainty markers.
        if semantic_distance > 0.5:
            events.append(DriftEvent("semantic", semantic_distance, "meaning moved far from baseline", f"dist={semantic_distance:.3f}", current_phase, True))
        if self._semantic_instability_cue(text or ""):
            events.append(DriftEvent("semantic", 0.45, "uncertainty or contradiction cue detected", "semantic_instability", current_phase, True))

        # Recursive phase drift.
        if phase_deviation >= 0.75:
            correctable = current_phase in (5, 6, 7, 8)
            events.append(DriftEvent("recursive", phase_deviation, "unsafe phase transition or projection skip", transition_validity, current_phase, correctable))
        elif phase_deviation >= 0.35:
            events.append(DriftEvent("recursive", phase_deviation, "phase transition needs review", transition_validity, current_phase, True))

        # Trend/taxonomy pass.
        trend_type = self._temporal_type(self.recent_scores)
        if trend_type == "evolutionary":
            events.append(DriftEvent("evolutionary", 0.28, "controlled upward novelty/drift trend", "ema_upward", current_phase, True))
        elif trend_type == "resonant":
            events.append(DriftEvent("resonant", 0.3, "oscillating drift pattern", "oscillation", current_phase, True))

        max_severity = max((e.severity for e in events), default=0.0)
        sigma_res = statistics.pstdev(self.recent_scores[-self.history_window:]) if len(self.recent_scores) >= 2 else 0.0
        d_score = max_severity
        delta_phi = phase_deviation
        n = max(1, min(len(phase_history) + 1, self.history_window))
        epsilon_s = min(1.0, (sigma_res + d_score + delta_phi) / n if n > 1 else max(d_score, delta_phi))
        # For severe single-event drift, keep epsilon meaningful.
        epsilon_s = max(epsilon_s, max_severity * 0.85, phase_deviation * 0.85)

        self.recent_scores.append(epsilon_s)
        self.recent_scores = self.recent_scores[-self.history_window:]

        if epsilon_s >= self.CIRCUIT_THRESHOLD or max_severity >= 0.9:
            self.circuit_open = True
            self.circuit_reason = "drift exceeded circuit breaker threshold"

        if self.circuit_open:
            events.append(DriftEvent("catastrophic", max(0.9, epsilon_s), self.circuit_reason, "circuit_breaker_open", current_phase, False))

        verdict = "ALLOW"
        if self.circuit_open or max_severity >= self.BLOCK_THRESHOLD or phase_deviation >= 0.85:
            verdict = "BLOCK"
        elif max_severity >= self.WARN_THRESHOLD or epsilon_s >= self.WARN_THRESHOLD:
            verdict = "WARN"

        correction_recommended = verdict in ("WARN", "BLOCK") and any(e.correctable for e in events)
        projection_ready = verdict != "BLOCK" and not self._projection_without_closure(current_phase, phase_history)
        chi_t_required = epsilon_s >= 0.8 or (current_phase == 5 and correction_recommended)

        return {
            "verdict": verdict,
            "drift_detected": bool(events),
            "events": [e.to_dict() for e in events],
            "max_severity": round(max_severity, 4),
            "epsilon_s": round(epsilon_s, 4),
            "entropy": round(entropy, 4),
            "structure_status": structure_status,
            "structural_distance": round(structural_distance, 4),
            "semantic_distance": round(semantic_distance, 4),
            "phase_deviation": round(phase_deviation, 4),
            "transition_validity": transition_validity,
            "correction_recommended": correction_recommended,
            "chi_t_required": chi_t_required,
            "circuit_breaker_open": self.circuit_open,
            "projection_ready": projection_ready,
            "recommended_action": self._recommended_action(verdict, correction_recommended, projection_ready),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def reset_circuit(self) -> None:
        self.circuit_open = False
        self.circuit_reason = ""

    def _coerce_phase(self, value) -> int:
        if isinstance(value, int) and 1 <= value <= 9:
            return value
        if isinstance(value, str) and value.strip().isdigit():
            v = int(value.strip())
            if 1 <= v <= 9:
                return v
        return 1

    def _shannon_norm(self, payload: str) -> float:
        n = len(payload)
        if n < 2:
            return 0.0
        counts = Counter(payload)
        entropy = 0.0
        for count in counts.values():
            p = count / n
            if p > 0:
                entropy -= p * math.log2(p)
        h_max = math.log2(min(len(counts), n))
        return entropy / h_max if h_max > 0 else 0.0

    def _looks_like_repeated_noise(self, text: str) -> bool:
        stripped = re.sub(r"\s+", "", text)
        if len(stripped) < 12:
            return False
        most_common = Counter(stripped).most_common(1)[0][1]
        return most_common / len(stripped) > 0.75

    def _structure_check(self, text: str, expected_shape: Any | None) -> Tuple[str, float]:
        if text.count("{") != text.count("}") or text.count("[") != text.count("]"):
            return "unbalanced_brackets", 0.55
        if expected_shape is None:
            return "valid", 0.0
        try:
            obj = json.loads(text) if isinstance(text, str) and text.strip().startswith(("{", "[")) else text
            expected_sig = self._shape_signature(expected_shape)
            actual_sig = self._shape_signature(obj)
            distance = self._signature_distance(expected_sig, actual_sig)
            return "valid" if distance <= 0.5 else "shape_mismatch", distance
        except Exception:
            return "unparseable_for_shape", 0.6

    def _shape_signature(self, obj: Any) -> Tuple[str, int, Tuple[int, ...]]:
        type_counts = [0, 0, 0, 0, 0, 0]
        max_depth = 0
        keys: List[str] = []

        def walk(node: Any, depth: int = 0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            if isinstance(node, dict):
                type_counts[0] += 1
                keys.extend(str(k) for k in node.keys())
                for v in node.values():
                    walk(v, depth + 1)
            elif isinstance(node, list):
                type_counts[1] += 1
                for item in node:
                    walk(item, depth + 1)
            elif isinstance(node, str):
                type_counts[2] += 1
            elif isinstance(node, (int, float)) and not isinstance(node, bool):
                type_counts[3] += 1
            elif isinstance(node, bool):
                type_counts[4] += 1
            elif node is None:
                type_counts[5] += 1

        walk(obj)
        return ("|".join(sorted(keys)), max_depth, tuple(type_counts))

    def _signature_distance(self, a: Tuple[str, int, Tuple[int, ...]], b: Tuple[str, int, Tuple[int, ...]]) -> float:
        keys_a = set(a[0].split("|")) if a[0] else set()
        keys_b = set(b[0].split("|")) if b[0] else set()
        key_dist = 0.0 if not keys_a and not keys_b else 1.0 - (len(keys_a & keys_b) / max(1, len(keys_a | keys_b)))
        depth_dist = min(1.0, abs(a[1] - b[1]) / 5)
        count_delta = sum(abs(x - y) for x, y in zip(a[2], b[2]))
        count_total = max(1, sum(max(x, y) for x, y in zip(a[2], b[2])))
        count_dist = min(1.0, count_delta / count_total)
        return (key_dist + depth_dist + count_dist) / 3

    def _semantic_distance(self, text: str, baseline: str | None) -> float:
        lower = text.lower()
        if not baseline:
            return 0.0
        a = {w for w in re.findall(r"[a-z0-9_]{3,}", lower)}
        b = {w for w in re.findall(r"[a-z0-9_]{3,}", baseline.lower())}
        if not a and not b:
            return 0.0
        return 1.0 - (len(a & b) / max(1, len(a | b)))

    def _semantic_instability_cue(self, text: str) -> bool:
        lower = text.lower()
        contradiction = bool(re.search(r"\b(always|never|definitely)\b.*\b(maybe|not sure|i think)\b", lower))
        uncertainty = bool(re.search(r"\b(i don't know|not sure|confused|could be wrong|maybe maybe)\b", lower))
        overclaim = bool(re.search(r"\b(prove|guarantee|absolute truth)\b", lower)) and "source" not in lower
        return contradiction or uncertainty or overclaim

    def _phase_deviation(self, current_phase: int, history: List[int]) -> Tuple[float, str]:
        if not history:
            return (0.0, "no_prior_phase")
        prior = history[-1]
        if (prior, current_phase) in self.DANGEROUS_SKIPS:
            return (0.95, f"dangerous_skip_{prior}_to_{current_phase}")
        if current_phase in self.VALID_NEXT.get(prior, {current_phase}):
            return (0.0, f"valid_{prior}_to_{current_phase}")
        gap = abs(current_phase - prior)
        if prior == 9 and current_phase == 1:
            return (0.0, "valid_octave_return_9_to_1")
        severity = min(0.85, gap / 8 + 0.25)
        return (severity, f"unexpected_transition_{prior}_to_{current_phase}")

    def _projection_without_closure(self, current_phase: int, history: List[int]) -> bool:
        if current_phase != 8:
            return False
        return not (6 in history and 7 in history)

    def _temporal_type(self, scores: List[float]) -> str | None:
        if len(scores) < 4:
            return None
        last = scores[-4:]
        if all(b > a for a, b in zip(last, last[1:])) and (last[-1] - last[0]) > 0.15:
            return "evolutionary"
        signs = [last[i + 1] - last[i] for i in range(len(last) - 1)]
        if len(signs) >= 3 and signs[0] * signs[1] < 0 and signs[1] * signs[2] < 0:
            return "resonant"
        return None

    def _recommended_action(self, verdict: str, correction: bool, projection_ready: bool) -> str:
        if verdict == "BLOCK":
            return "block_and_route_to_correction_or_cold_storage" if correction else "block_and_hold"
        if verdict == "WARN":
            return "warn_and_correct_before_projection" if not projection_ready or correction else "warn_and_continue"
        if not projection_ready:
            return "hold_projection_until_phase6_and_phase7"
        return "allow"


if __name__ == "__main__":
    arb = DriftArbitrator()
    for phase, hist, text in [
        (3, [1, 2], "I want to build this"),
        (8, [5], "ship it now"),
        (5, [4], "I am confused and drifting"),
    ]:
        print(arb.evaluate(text, phase, hist))

"""
Echo Gate — RMC Module 6 (S19AJ rebuild)

Validates that a rendered output faithfully preserves the manifest it claims
to render. Rendering may be text, code, glyph, packet, dashboard state, or
memory record. The first implementation is conservative, stdlib-only, and
returns the tuple expected by the existing orchestrator:

    accepted, score, note = EchoGate().validate(manifest, rendered_output, modality)

Compatibility aliases are staged separately for the logical architecture name:
    echo_gate.echo_gate
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Tuple


@dataclass
class EchoCheck:
    name: str
    passed: bool
    score: float
    note: str

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "score": round(max(0.0, min(1.0, self.score)), 4),
            "note": self.note,
        }


@dataclass
class EchoReport:
    accepted: bool
    score: float
    note: str
    checks: List[EchoCheck] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            "accepted": self.accepted,
            "score": round(max(0.0, min(1.0, self.score)), 4),
            "note": self.note,
            "checks": [c.to_dict() for c in self.checks],
            "timestamp": self.timestamp,
        }


class EchoGate:
    """
    Echo validator for rendered output.

    It enforces the minimum RMC law:
    - no manifest, no approved output
    - blocked manifests must render as blocked
    - rendered output must preserve the manifest conclusion or manifest fields
    - drift/confidence/phase posture may not be silently inverted
    """

    ACCEPT_THRESHOLD = 0.62

    def validate(self, manifest: Dict, rendered_output: str, modality: str = "language") -> Tuple[bool, float, str]:
        report = self.validate_report(manifest, rendered_output, modality)
        return report.accepted, report.score, report.note

    def validate_report(self, manifest: Dict, rendered_output: str, modality: str = "language") -> EchoReport:
        manifest = manifest or {}
        output = rendered_output or ""
        modality = modality or "language"
        checks: List[EchoCheck] = []

        checks.append(self._check_required_manifest(manifest))
        checks.append(self._check_nonempty_output(output, manifest))
        checks.append(self._check_block_preservation(manifest, output))
        checks.append(self._check_conclusion_preservation(manifest, output, modality))
        checks.append(self._check_modality_fields(manifest, output, modality))
        checks.append(self._check_drift_posture(manifest, output))

        hard_fail = any((not c.passed) and c.name in {"required_manifest", "block_preservation", "drift_posture"} for c in checks)
        score = sum(c.score for c in checks) / max(1, len(checks))
        accepted = (not hard_fail) and score >= self.ACCEPT_THRESHOLD
        note = "echo accepted" if accepted else "echo rejected: " + "; ".join(c.note for c in checks if not c.passed)

        return EchoReport(accepted=accepted, score=score, note=note, checks=checks)

    def _check_required_manifest(self, manifest: Dict) -> EchoCheck:
        required = {"id", "conclusion", "phase", "drift_verdict", "projection_status"}
        missing = sorted(required - set(manifest.keys()))
        if missing:
            return EchoCheck("required_manifest", False, 0.0, f"missing manifest fields: {', '.join(missing)}")
        return EchoCheck("required_manifest", True, 1.0, "required manifest fields present")

    def _check_nonempty_output(self, output: str, manifest: Dict) -> EchoCheck:
        if manifest.get("projection_status") == "BLOCKED":
            # A blocked output may be brief but should not be empty.
            pass
        if output.strip():
            return EchoCheck("nonempty_output", True, 1.0, "rendered output present")
        return EchoCheck("nonempty_output", False, 0.0, "rendered output is empty")

    def _check_block_preservation(self, manifest: Dict, output: str) -> EchoCheck:
        blocked = manifest.get("projection_status") == "BLOCKED" or manifest.get("drift_verdict") == "BLOCK"
        output_marks_block = bool(re.search(r"\b(blocked|cannot render|held|denied|drift severity)\b", output.lower()))
        if blocked and not output_marks_block:
            return EchoCheck("block_preservation", False, 0.0, "blocked manifest rendered without block marker")
        if blocked:
            return EchoCheck("block_preservation", True, 1.0, "blocked state preserved")
        return EchoCheck("block_preservation", True, 1.0, "manifest is not blocked")

    def _check_conclusion_preservation(self, manifest: Dict, output: str, modality: str) -> EchoCheck:
        conclusion = str(manifest.get("conclusion", "")).strip()
        if not conclusion:
            return EchoCheck("conclusion_preservation", False, 0.0, "manifest conclusion missing")
        if manifest.get("projection_status") == "BLOCKED":
            return EchoCheck("conclusion_preservation", True, 1.0, "blocked manifest need not expose conclusion")

        if modality == "packet":
            try:
                packet = json.loads(output)
                packet_conclusion = str(packet.get("conclusion", ""))
                similarity = self._token_similarity(conclusion, packet_conclusion)
                return EchoCheck("conclusion_preservation", similarity >= 0.8, similarity, "packet conclusion compared to manifest")
            except Exception:
                return EchoCheck("conclusion_preservation", False, 0.0, "packet output was not parseable JSON")

        similarity = self._token_similarity(conclusion, output)
        # The existing language renderer may add phase frames. A 0.35 overlap is enough
        # for short statements; strong exact substring earns full score.
        if conclusion[:40].lower() in output.lower():
            similarity = max(similarity, 1.0)
        passed = similarity >= 0.35
        return EchoCheck(
            "conclusion_preservation",
            passed,
            similarity,
            f"conclusion token overlap={similarity:.3f}",
        )

    def _check_modality_fields(self, manifest: Dict, output: str, modality: str) -> EchoCheck:
        if manifest.get("projection_status") == "BLOCKED":
            return EchoCheck("modality_fields", True, 1.0, "blocked output allowed in any modality")
        phase = str(manifest.get("phase", ""))
        mid = str(manifest.get("id", ""))
        if modality == "glyph":
            ok = f"Φ{phase}" in output or phase in output
            return EchoCheck("modality_fields", ok, 1.0 if ok else 0.3, "glyph phase marker check")
        if modality == "code":
            ok = mid in output and "Conclusion:" in output
            return EchoCheck("modality_fields", ok, 1.0 if ok else 0.4, "code manifest id/conclusion check")
        if modality == "packet":
            try:
                packet = json.loads(output)
                ok = str(packet.get("manifest_id", "")) == mid
                return EchoCheck("modality_fields", ok, 1.0 if ok else 0.4, "packet manifest id check")
            except Exception:
                return EchoCheck("modality_fields", False, 0.0, "packet is not JSON")
        return EchoCheck("modality_fields", True, 0.9, "language modality has no required structural marker")

    def _check_drift_posture(self, manifest: Dict, output: str) -> EchoCheck:
        drift = manifest.get("drift_verdict", "ALLOW")
        confidence = float(manifest.get("confidence", 1.0) or 0.0)
        lower = output.lower()
        if drift == "WARN" and not any(marker in lower for marker in ["drift", "note", "uncertain", "warning"]):
            return EchoCheck("drift_posture", False, 0.45, "WARN drift not visible in rendered output")
        if confidence < 0.5 and not any(marker in lower for marker in ["low confidence", "uncertain", "blocked"]):
            return EchoCheck("drift_posture", False, 0.5, "low confidence not visible in rendered output")
        return EchoCheck("drift_posture", True, 1.0, "drift/confidence posture preserved")

    def _token_similarity(self, a: str, b: str) -> float:
        ta = set(self._tokens(a))
        tb = set(self._tokens(b))
        if not ta and not tb:
            return 1.0
        if not ta or not tb:
            return 0.0
        return len(ta & tb) / max(1, len(ta | tb))

    def _tokens(self, text: str) -> Iterable[str]:
        return [t for t in re.findall(r"[a-z0-9_]{3,}", text.lower())]


if __name__ == "__main__":
    gate = EchoGate()
    manifest = {
        "id": "abc123", "phase": 3, "phase_name": "Desire",
        "conclusion": "The goal is to rebuild the missing modules",
        "confidence": 0.9, "drift_verdict": "ALLOW", "projection_status": "READY"
    }
    print(gate.validate(manifest, "The goal here is: The goal is to rebuild the missing modules"))

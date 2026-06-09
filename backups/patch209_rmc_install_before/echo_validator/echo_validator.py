"""
Echo Validator — RMC Module 6
The final gate before output is accepted.

Asks one question after every render:
Does the output still match the manifest?

If the renderer drifted from the manifest — added claims, inflated
confidence, dropped limitations, or invented content — the Echo
Validator catches it here before it reaches memory or the user.

Failed renderings are stored, not erased. They become part of the
audit trail. Memory poisoning is prevented by never storing a failed
rendering as a valid conclusion.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field


# ── ECHO SCORE ─────────────────────────────────────────────────────

@dataclass
class EchoScore:
    """
    Result of validating a rendered output against its manifest.
    Score 0.0 = completely unfaithful. Score 1.0 = perfectly faithful.
    """
    score: float                    # 0.0 to 1.0
    passed: bool                    # True if score >= threshold
    checks: Dict[str, bool]         # Which checks passed
    failures: List[str]             # What failed and why
    manifest_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            'score': self.score,
            'passed': self.passed,
            'checks': self.checks,
            'failures': self.failures,
            'manifest_id': self.manifest_id,
            'timestamp': self.timestamp,
        }


# ── FAILED RENDERING RECORD ────────────────────────────────────────

@dataclass
class FailedRenderingRecord:
    """
    A failed rendering stored for audit — never used as a valid conclusion.
    Prevents memory poisoning by quarantining unfaithful output.
    """
    manifest_id: str
    failed_output: str
    failure_type: str
    echo_score: float
    retry_instruction: str
    memory_status: str = "debugging_only"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            'manifest_id': self.manifest_id,
            'failed_output': self.failed_output,
            'failure_type': self.failure_type,
            'echo_score': self.echo_score,
            'retry_instruction': self.retry_instruction,
            'memory_status': self.memory_status,
            'timestamp': self.timestamp,
        }


# ── ECHO VALIDATOR ─────────────────────────────────────────────────

class EchoValidator:
    """
    Validates that rendered output faithfully preserves the manifest.

    Checks:
        1. conclusion_present   — core conclusion appears in output
        2. claim_preserved      — claim type not inflated
        3. confidence_preserved — output doesn't overclaim
        4. block_respected      — blocked manifests produce blocked output
        5. drift_preserved      — drift verdict reflected in output
        6. no_forbidden_claims  — no absolute claims from uncertain manifests
    """

    PASS_THRESHOLD = 0.75    # Score below this = failed rendering

    FORBIDDEN_ABSOLUTES = [
        r'\b(always|never|guaranteed|proven|impossible|certain|perfect)\b'
    ]

    def validate(self, manifest: Dict, rendered_output: str) -> EchoScore:
        """
        Validate rendered output against manifest.
        Returns EchoScore with pass/fail and detailed check results.
        """
        checks = {}
        failures = []

        conclusion  = manifest.get('conclusion', '')
        confidence  = manifest.get('confidence', 1.0)
        drift       = manifest.get('drift_verdict', 'ALLOW')
        status      = manifest.get('projection_status', 'READY')
        claim_type  = manifest.get('claim_type', 'assertion')
        manifest_id = manifest.get('id', 'unknown')
        output_lower = rendered_output.lower()

        # ── Check 1: Conclusion present in output ──────────────────
        core = self._extract_core(conclusion)
        checks['conclusion_present'] = core.lower() in output_lower
        if not checks['conclusion_present']:
            failures.append(f"Core conclusion '{core[:40]}' not found in output")

        # ── Check 2: Blocked manifest produces blocked output ──────
        if status == 'BLOCKED':
            checks['block_respected'] = 'blocked' in output_lower
            if not checks['block_respected']:
                failures.append("Blocked manifest rendered without block indicator")
        else:
            checks['block_respected'] = True

        # ── Check 3: Drift verdict reflected ──────────────────────
        if drift == 'WARN':
            # Must have an explicit warning marker — not just the word drift
            # appearing in the conclusion itself
            conclusion_lower = conclusion.lower()
            has_warn_marker = (
                '[note:' in output_lower or
                '[warn' in output_lower or
                'note: drift' in output_lower or
                output_lower.startswith('[note') or
                output_lower.startswith('[warn')
            )
            has_uncertain = (
                'uncertain' in output_lower or
                'low confidence' in output_lower
            )
            checks['drift_preserved'] = has_warn_marker or has_uncertain
            if not checks['drift_preserved']:
                failures.append("WARN drift verdict not reflected in output")
        elif drift == 'BLOCK':
            checks['drift_preserved'] = checks['block_respected']
        else:
            checks['drift_preserved'] = True

        # ── Check 4: No forbidden absolute claims when uncertain ───
        if confidence < 0.6:
            forbidden_found = any(
                re.search(p, rendered_output, re.IGNORECASE)
                for p in self.FORBIDDEN_ABSOLUTES
            )
            checks['no_forbidden_claims'] = not forbidden_found
            if forbidden_found:
                failures.append(
                    f"Absolute claim found in low-confidence output ({confidence:.2f})"
                )
        else:
            checks['no_forbidden_claims'] = True

        # ── Check 5: Confidence not inflated ──────────────────────
        # If output explicitly states a confidence, it shouldn't exceed manifest
        conf_match = re.search(r'confidence[:\s]+(\d+\.?\d*)', output_lower)
        if conf_match:
            stated_conf = float(conf_match.group(1))
            # Normalize if given as percentage
            if stated_conf > 1.0:
                stated_conf /= 100
            checks['confidence_preserved'] = stated_conf <= confidence + 0.05
            if not checks['confidence_preserved']:
                failures.append(
                    f"Stated confidence {stated_conf:.2f} exceeds manifest {confidence:.2f}"
                )
        else:
            checks['confidence_preserved'] = True

        # ── Check 6: Claim type not inflated ──────────────────────
        # Questions shouldn't become assertions, observations shouldn't become proofs
        if claim_type == 'question':
            checks['claim_preserved'] = '?' in rendered_output or 'question' in output_lower
        elif claim_type == 'observation':
            inflated = re.search(r'\b(proves?|demonstrates?|confirms?|establishes?)\b',
                                  rendered_output, re.IGNORECASE)
            checks['claim_preserved'] = not bool(inflated)
            if inflated:
                failures.append(f"Observation inflated to proof: '{inflated.group()}'")
        else:
            checks['claim_preserved'] = True

        # ── Score calculation ──────────────────────────────────────
        passed_count = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        score = passed_count / total_checks if total_checks > 0 else 0.0
        passed = score >= self.PASS_THRESHOLD

        # Hard fail — block violations and warn suppression always fail regardless of score
        if status == "BLOCKED" and not checks.get("block_respected"):
            passed = False
        if drift == "WARN" and not checks.get("drift_preserved"):
            passed = False

        return EchoScore(
            score=score,
            passed=passed,
            checks=checks,
            failures=failures,
            manifest_id=manifest_id,
        )

    def _extract_core(self, conclusion: str) -> str:
        """Extract the core content, stripping prefixes like [uncertain]"""
        core = re.sub(r'^\[.*?\]\s*', '', conclusion).strip()
        # Take first 6 words as the core fingerprint
        words = core.split()[:6]
        return ' '.join(words)


# ── FAILED RENDERING HANDLER ───────────────────────────────────────

class FailedRenderingHandler:
    """
    Stores failed renderings for audit. Never allows them into valid memory.
    """

    def __init__(self):
        self.failed_records: List[FailedRenderingRecord] = []

    def store(self, manifest: Dict, rendered_output: str,
              echo_score: EchoScore) -> FailedRenderingRecord:
        """Store a failed rendering for audit purposes"""
        failure_type = self._classify_failure(echo_score)
        retry_instruction = self._build_retry_instruction(echo_score)

        record = FailedRenderingRecord(
            manifest_id=manifest.get('id', 'unknown'),
            failed_output=rendered_output[:200],
            failure_type=failure_type,
            echo_score=echo_score.score,
            retry_instruction=retry_instruction,
        )
        self.failed_records.append(record)
        return record

    def count(self) -> int:
        return len(self.failed_records)

    def get_all(self) -> List[FailedRenderingRecord]:
        return list(self.failed_records)

    def _classify_failure(self, score: EchoScore) -> str:
        if not score.checks.get('block_respected'):
            return "block_violation"
        if not score.checks.get('no_forbidden_claims'):
            return "forbidden_claim_and_confidence_inflation"
        if not score.checks.get('conclusion_present'):
            return "conclusion_lost"
        if not score.checks.get('drift_preserved'):
            return "drift_suppressed"
        if not score.checks.get('claim_preserved'):
            return "claim_type_inflated"
        return "general_faithfulness_failure"

    def _build_retry_instruction(self, score: EchoScore) -> str:
        if score.failures:
            return f"Fix: {score.failures[0]}"
        return "Re-render preserving all manifest constraints"


# ── ECHO GATE (convenience wrapper) ───────────────────────────────

class EchoGate:
    """
    Single entry point for echo validation.
    Returns (accepted: bool, echo_score, failed_record_or_None)
    """

    def __init__(self):
        self.validator = EchoValidator()
        self.failed_handler = FailedRenderingHandler()

    def check(self, manifest: Dict,
              rendered_output: str) -> Tuple[bool, EchoScore, Optional[FailedRenderingRecord]]:
        """
        Check if rendered output passes echo validation.
        Returns (accepted, score, failed_record)
        failed_record is None if accepted.
        """
        score = self.validator.validate(manifest, rendered_output)

        if score.passed:
            return True, score, None
        else:
            record = self.failed_handler.store(manifest, rendered_output, score)
            return False, score, record


if __name__ == "__main__":
    print("=== Echo Validator — Quick Test ===\n")

    gate = EchoGate()

    tests = [
        # (manifest, output, expect_pass, label)
        (
            {'id': 'm1', 'conclusion': 'User wants to build a web app',
             'confidence': 0.87, 'drift_verdict': 'ALLOW',
             'projection_status': 'READY', 'claim_type': 'assertion'},
            "The goal here is: User wants to build a web app",
            True, "Clean render"
        ),
        (
            {'id': 'm2', 'conclusion': 'ship it now',
             'confidence': 0.4, 'drift_verdict': 'BLOCK',
             'projection_status': 'BLOCKED', 'claim_type': 'instruction'},
            "[output blocked — drift severity too high to render]",
            True, "Blocked render respected"
        ),
        (
            {'id': 'm3', 'conclusion': 'ship it now',
             'confidence': 0.4, 'drift_verdict': 'BLOCK',
             'projection_status': 'BLOCKED', 'claim_type': 'instruction'},
            "Ship it now, everything is ready!",
            False, "Block violation — renderer ignored block"
        ),
        (
            {'id': 'm4', 'conclusion': 'System state unclear',
             'confidence': 0.3, 'drift_verdict': 'ALLOW',
             'projection_status': 'READY', 'claim_type': 'assertion'},
            "This is certainly always guaranteed to be correct.",
            False, "Forbidden absolutes in low-confidence output"
        ),
        (
            {'id': 'm5', 'conclusion': 'System state is drifting',
             'confidence': 0.45, 'drift_verdict': 'WARN',
             'projection_status': 'READY', 'claim_type': 'observation'},
            "[note: drift detected] There is significant uncertainty: System state is drifting",
            True, "Warn drift preserved"
        ),
    ]

    passed_total = 0
    for manifest, output, expect, label in tests:
        accepted, score, failed = gate.check(manifest, output)
        ok = (accepted == expect)
        if ok: passed_total += 1
        status = "✅" if ok else "❌"
        verdict = "PASS" if accepted else "FAIL"
        print(f"{status} [{verdict}] score={score.score:.2f} | {label}")
        if score.failures:
            for f in score.failures:
                print(f"     ↳ {f}")

    print(f"\n{passed_total}/{len(tests)} correct")
    print(f"Failed renderings stored: {gate.failed_handler.count()}")

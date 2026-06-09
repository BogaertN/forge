import unittest
from echo_validator import EchoGate

BASE_MANIFEST = {
    "id": "abc123",
    "phase": 3,
    "phase_name": "Desire",
    "conclusion": "The goal is to rebuild the missing modules",
    "confidence": 0.9,
    "drift_verdict": "ALLOW",
    "projection_status": "READY",
    "claim_type": "assertion",
}

class TestEchoGate(unittest.TestCase):
    def setUp(self):
        self.g = EchoGate()

    def test_accepts_faithful_language(self):
        accepted, score, note = self.g.validate(BASE_MANIFEST, "The goal here is: The goal is to rebuild the missing modules")
        self.assertTrue(accepted)
        self.assertGreaterEqual(score, 0.62)

    def test_rejects_missing_manifest_fields(self):
        accepted, score, note = self.g.validate({"id": "x"}, "something")
        self.assertFalse(accepted)

    def test_blocked_manifest_requires_blocked_output(self):
        m = dict(BASE_MANIFEST, drift_verdict="BLOCK", projection_status="BLOCKED")
        accepted, score, note = self.g.validate(m, "Ship it now")
        self.assertFalse(accepted)

    def test_blocked_manifest_accepts_blocked_output(self):
        m = dict(BASE_MANIFEST, drift_verdict="BLOCK", projection_status="BLOCKED")
        accepted, score, note = self.g.validate(m, "[output blocked — drift severity too high to render]")
        self.assertTrue(accepted)

    def test_warn_drift_must_be_visible(self):
        m = dict(BASE_MANIFEST, drift_verdict="WARN")
        accepted, score, note = self.g.validate(m, "The goal is to rebuild the missing modules")
        self.assertFalse(accepted)
        accepted2, _, _ = self.g.validate(m, "[note: drift detected] The goal is to rebuild the missing modules")
        self.assertTrue(accepted2)

    def test_packet_validation(self):
        packet = '{"rmc_packet": true, "manifest_id": "abc123", "conclusion": "The goal is to rebuild the missing modules"}'
        accepted, score, note = self.g.validate(BASE_MANIFEST, packet, modality="packet")
        self.assertTrue(accepted)

    def test_glyph_validation_checks_phase(self):
        accepted, score, note = self.g.validate(BASE_MANIFEST, "Φ3→ The goal is to rebuild the missing modules", modality="glyph")
        self.assertTrue(accepted)

if __name__ == "__main__":
    unittest.main(verbosity=2)

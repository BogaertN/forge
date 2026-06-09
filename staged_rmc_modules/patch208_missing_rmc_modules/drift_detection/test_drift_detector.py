import unittest
from drift_detector import DriftArbitrator

class TestDriftArbitrator(unittest.TestCase):
    def setUp(self):
        self.d = DriftArbitrator()

    def test_clean_transition_allows(self):
        r = self.d.evaluate("I want to build this", 3, [1, 2])
        self.assertEqual(r["verdict"], "ALLOW")
        self.assertFalse(r["circuit_breaker_open"])

    def test_dangerous_skip_blocks(self):
        r = self.d.evaluate("ship it now", 8, [5])
        self.assertEqual(r["verdict"], "BLOCK")
        self.assertTrue(any(e["drift_type"] == "recursive" for e in r["events"]))

    def test_unbalanced_brackets_warns_or_blocks(self):
        r = self.d.evaluate('{"broken": [1, 2}', 4, [3])
        self.assertIn(r["verdict"], ("WARN", "BLOCK"))
        self.assertTrue(any(e["drift_type"] == "structural" for e in r["events"]))

    def test_semantic_distance(self):
        r = self.d.evaluate("octopus memory lattice", 3, [2], memory_baseline="truck repair schedule")
        self.assertGreaterEqual(r["semantic_distance"], 0.5)
        self.assertTrue(any(e["drift_type"] == "semantic" for e in r["events"]))

    def test_repeated_noise_detects(self):
        r = self.d.evaluate("aaaaaaaaaaaaaaaaaaaaaaaa", 5, [4])
        self.assertTrue(r["drift_detected"])

    def test_report_has_required_fields(self):
        r = self.d.evaluate("fix this", 6, [5])
        for key in ["verdict", "events", "epsilon_s", "phase_deviation", "recommended_action", "projection_ready"]:
            self.assertIn(key, r)

    def test_projection_without_closure_not_ready(self):
        r = self.d.evaluate("deploy this", 8, [3, 4])
        self.assertFalse(r["projection_ready"])

    def test_phase_6_after_5_is_valid(self):
        r = self.d.evaluate("correct and restore it", 6, [5])
        self.assertNotEqual(r["verdict"], "BLOCK")

if __name__ == "__main__":
    unittest.main(verbosity=2)

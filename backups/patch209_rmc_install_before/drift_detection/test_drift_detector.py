"""
Test Suite — Drift Detection Runtime (RMC Module 3)
"""
import unittest, sys
from drift_detector import (
    SyntacticDriftDetector, SemanticDriftDetector,
    RecursiveDriftDetector, DriftArbitrator, DriftEvent
)


class TestDriftEvent(unittest.TestCase):
    def test_to_dict_keys(self):
        e = DriftEvent("syntactic", 0.5, "desc", "signal", 3)
        d = e.to_dict()
        for k in ['drift_type','severity','description','signal','phase','correctable','timestamp']:
            self.assertIn(k, d)

    def test_severity_stored(self):
        e = DriftEvent("semantic", 0.7, "d", "s", 4)
        self.assertEqual(e.severity, 0.7)

    def test_timestamp_utc(self):
        e = DriftEvent("recursive", 0.9, "d", "s", 5)
        self.assertIn("+00:00", e.timestamp)


class TestSyntacticDrift(unittest.TestCase):
    def setUp(self): self.d = SyntacticDriftDetector()

    def test_clean_sentence_no_events(self):
        events = self.d.detect("This is a clean, well-formed statement.", 3)
        self.assertEqual(len(events), 0)

    def test_contradiction_detected(self):
        events = self.d.detect("yes but no that is wrong", 2)
        types = [e.drift_type for e in events]
        self.assertIn("syntactic", types)
        sev = max(e.severity for e in events)
        self.assertGreaterEqual(sev, 0.6)

    def test_excessive_hedging_detected(self):
        events = self.d.detect("maybe perhaps it could possibly sort of work", 3)
        descs = [e.description for e in events]
        self.assertTrue(any("hedging" in d for d in descs))

    def test_repetition_detected(self):
        events = self.d.detect("the system needs the system needs to restart", 4)
        descs = [e.description for e in events]
        self.assertTrue(any("repetition" in d.lower() for d in descs))

    def test_all_events_are_syntactic(self):
        events = self.d.detect("yes but no maybe perhaps possibly", 2)
        for e in events:
            self.assertEqual(e.drift_type, "syntactic")


class TestSemanticDrift(unittest.TestCase):
    def setUp(self): self.d = SemanticDriftDetector()

    def test_clean_sentence_no_events(self):
        events = self.d.detect("The system processes requests correctly.", 7)
        self.assertEqual(len(events), 0)

    def test_redefinition_detected(self):
        events = self.d.detect("This now means something completely different", 5)
        descs = [e.description for e in events]
        self.assertTrue(any("redefin" in d.lower() for d in descs))

    def test_conflicting_certainty_detected(self):
        events = self.d.detect("This will definitely work but maybe possibly not", 3)
        descs = [e.description for e in events]
        self.assertTrue(any("certainty" in d.lower() for d in descs))

    def test_multiple_corrections_detected(self):
        events = self.d.detect("Actually I mean to clarify what I meant was", 4)
        descs = [e.description for e in events]
        self.assertTrue(any("correction" in d.lower() or "instab" in d.lower() for d in descs))

    def test_all_events_are_semantic(self):
        events = self.d.detect("This now means something different actually I mean", 3)
        for e in events:
            self.assertEqual(e.drift_type, "semantic")


class TestRecursiveDrift(unittest.TestCase):
    def setUp(self): self.d = RecursiveDriftDetector()

    def test_no_history_no_events(self):
        events = self.d.detect(3, [])
        self.assertEqual(len(events), 0)

    def test_luciferian_skip_1_to_8(self):
        events = self.d.detect(8, [1])
        self.assertTrue(any(e.severity >= 0.9 for e in events))

    def test_luciferian_skip_2_to_9(self):
        events = self.d.detect(9, [2])
        self.assertTrue(any("skip" in e.description.lower() for e in events))

    def test_luciferian_skip_5_to_8(self):
        events = self.d.detect(8, [5])
        self.assertTrue(any(e.severity >= 0.9 for e in events))

    def test_valid_transition_no_skip_event(self):
        events = self.d.detect(8, [7])
        skip_events = [e for e in events if "skip" in e.description.lower()]
        self.assertEqual(len(skip_events), 0)

    def test_stuck_loop_detected(self):
        events = self.d.detect(4, [4, 4, 4, 4])
        descs = [e.description for e in events]
        self.assertTrue(any("stuck" in d.lower() or "repeat" in d.lower() for d in descs))

    def test_sustained_entropy_detected(self):
        events = self.d.detect(5, [5, 5, 5])
        descs = [e.description for e in events]
        self.assertTrue(any("entropy" in d.lower() or "grace" in d.lower() for d in descs))

    def test_rapid_cycling_detected(self):
        events = self.d.detect(3, [3, 4, 3, 4, 3, 4])
        descs = [e.description for e in events]
        self.assertTrue(any("cycl" in d.lower() for d in descs))

    def test_all_events_are_recursive(self):
        events = self.d.detect(8, [1])
        for e in events:
            self.assertEqual(e.drift_type, "recursive")


class TestDriftArbitrator(unittest.TestCase):
    def setUp(self): self.arb = DriftArbitrator()

    def test_clean_text_allow(self):
        r = self.arb.evaluate("This is a clean statement.", 3, [1, 2])
        self.assertEqual(r['verdict'], "ALLOW")

    def test_luciferian_skip_blocked(self):
        r = self.arb.evaluate("Let's ship it now", 8, [1, 2])
        self.assertEqual(r['verdict'], "BLOCK")

    def test_hedging_warns(self):
        r = self.arb.evaluate("maybe perhaps it could possibly sort of work", 3, [])
        self.assertEqual(r['verdict'], "WARN")

    def test_valid_transition_allow(self):
        r = self.arb.evaluate("Let's build it.", 8, [7])
        self.assertEqual(r['verdict'], "ALLOW")

    def test_result_has_required_keys(self):
        r = self.arb.evaluate("test", 1, [])
        for k in ['verdict','max_severity','event_count','events','phase','timestamp']:
            self.assertIn(k, r)

    def test_max_severity_is_float(self):
        r = self.arb.evaluate("test", 1, [])
        self.assertIsInstance(r['max_severity'], float)

    def test_events_is_list(self):
        r = self.arb.evaluate("test", 1, [])
        self.assertIsInstance(r['events'], list)

    def test_block_threshold(self):
        # Luciferian skip = 0.9 severity, must BLOCK
        r = self.arb.evaluate("go", 8, [1])
        self.assertEqual(r['verdict'], "BLOCK")

    def test_no_history_still_works(self):
        r = self.arb.evaluate("Hello world.", 1, None)
        self.assertIn(r['verdict'], ["ALLOW", "WARN", "BLOCK"])


if __name__ == "__main__":
    print("=" * 60)
    print("DRIFT DETECTION RUNTIME — TEST SUITE")
    print("RMC Module 3 | S19AG")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestDriftEvent, TestSyntacticDrift, TestSemanticDrift,
                TestRecursiveDrift, TestDriftArbitrator]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print()
    print("=" * 60)
    print(f"{'✅ ALL TESTS PASSED' if result.wasSuccessful() else '❌ FAILURES DETECTED'}")
    print("=" * 60)
    sys.exit(0 if result.wasSuccessful() else 1)

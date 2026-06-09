"""
Test Suite — Phase-State Parser (RMC Module 1)
"""
import unittest, sys
from phase_state_parser import PhaseStateParser, PhaseDetector, PhaseValidator, parse_phase


class TestPhaseDetector(unittest.TestCase):
    def setUp(self): self.d = PhaseDetector()

    def test_phase_1(self): self.assertEqual(self.d.detect("Hello, starting a new project")[0], 1)
    def test_phase_2(self): self.assertEqual(self.d.detect("Should I use Python or JavaScript?")[0], 2)
    def test_phase_3(self): self.assertEqual(self.d.detect("I want to build a web application")[0], 3)
    def test_phase_4(self): self.assertEqual(self.d.detect("I'm stuck on this error")[0], 4)
    def test_phase_5(self): self.assertEqual(self.d.detect("Everything is confusing and unclear")[0], 5)
    def test_phase_6(self): self.assertEqual(self.d.detect("Let me fix this issue")[0], 6)
    def test_phase_7(self): self.assertEqual(self.d.detect("This is called the phase parser")[0], 7)
    def test_phase_8(self): self.assertEqual(self.d.detect("Let's build it now")[0], 8)
    def test_phase_9(self): self.assertEqual(self.d.detect("Done! What's next?")[0], 9)
    def test_empty_defaults_to_1(self): self.assertEqual(self.d.detect("")[0], 1)
    def test_confidence_is_float(self): self.assertIsInstance(self.d.detect("hello")[1], float)
    def test_signals_is_list(self): self.assertIsInstance(self.d.detect("hello")[2], list)


class TestPhaseValidator(unittest.TestCase):
    def setUp(self): self.v = PhaseValidator()

    def test_same_phase_always_valid(self):
        for p in range(1, 10):
            self.assertTrue(self.v.validate_transition(p, p))

    def test_valid_forward_chain(self):
        for a, b in [(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(9,1)]:
            self.assertTrue(self.v.validate_transition(a, b), f"{a}→{b} should be valid")

    def test_luciferian_skips_blocked(self):
        for a, b in [(1,8),(1,9),(2,8),(2,9),(5,8),(5,9)]:
            self.assertFalse(self.v.validate_transition(a, b), f"{a}→{b} should be blocked")

    def test_get_valid_next_phases_returns_list(self):
        self.assertIsInstance(self.v.get_valid_next_phases(1), list)

    def test_phase_5_must_go_through_grace(self):
        self.assertFalse(self.v.validate_transition(5, 7))
        self.assertFalse(self.v.validate_transition(5, 8))
        self.assertTrue(self.v.validate_transition(5, 6))


class TestPhaseStateParser(unittest.TestCase):
    def setUp(self): self.p = PhaseStateParser()

    def test_returns_dict(self):
        r = self.p.parse("Hello")
        self.assertIsInstance(r, dict)

    def test_required_keys(self):
        r = self.p.parse("Hello")
        for key in ['phase','phase_name','confidence','signals','transition_valid','timestamp','input_snippet']:
            self.assertIn(key, r)

    def test_empty_input_returns_error(self):
        r = self.p.parse("")
        self.assertIn('error', r)
        self.assertEqual(r['phase'], 0)

    def test_whitespace_input_returns_error(self):
        r = self.p.parse("   ")
        self.assertIn('error', r)

    def test_valid_transition_with_context(self):
        r = self.p.parse("Let me fix this", context={'previous_phase': 4})
        self.assertTrue(r['transition_valid'])

    def test_invalid_transition_flagged(self):
        r = self.p.parse("Let's build it now", context={'previous_phase': 1})
        if r['phase'] == 8:
            self.assertFalse(r['transition_valid'])

    def test_snippet_truncated(self):
        r = self.p.parse("A" * 200)
        self.assertTrue(r['input_snippet'].endswith('...'))
        self.assertLessEqual(len(r['input_snippet']), 104)

    def test_audit_callback_called(self):
        log = []
        p = PhaseStateParser(forge_audit_callback=lambda ph, cf, sn: log.append(ph))
        p.parse("Hello world")
        self.assertEqual(len(log), 1)

    def test_no_timestamp_deprecation(self):
        r = self.p.parse("test")
        self.assertIn("+00:00", r["timestamp"])


class TestConvenience(unittest.TestCase):
    def test_parse_phase_function(self):
        r = parse_phase("Let's start")
        self.assertIn('phase', r)
        self.assertIsInstance(r['phase'], int)


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE-STATE PARSER — TEST SUITE")
    print("RMC Module 1 | S19AE")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestPhaseDetector, TestPhaseValidator, TestPhaseStateParser, TestConvenience]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print()
    print("=" * 60)
    print(f"{'✅ ALL TESTS PASSED' if result.wasSuccessful() else '❌ FAILURES DETECTED'}")
    print("=" * 60)
    sys.exit(0 if result.wasSuccessful() else 1)

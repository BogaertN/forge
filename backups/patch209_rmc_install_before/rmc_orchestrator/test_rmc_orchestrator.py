"""
Test Suite — RMC Pipeline Orchestrator (S19AK)
"""
import unittest, sys, os

BASE = os.path.expanduser("~/aiweb/runtime_wrappers")
for mod in ["phase_parser","ancestral_memory","drift_detection",
            "manifest_compiler","output_renderer","echo_validator","rmc_orchestrator"]:
    sys.path.insert(0, os.path.join(BASE, mod))

from rmc_orchestrator import RMCOrchestrator, RMCResult


class TestRMCResult(unittest.TestCase):
    def setUp(self):
        self.rmc = RMCOrchestrator()
        self.result = self.rmc.process("Hello, starting a new project")

    def test_returns_rmc_result(self):
        self.assertIsInstance(self.result, RMCResult)

    def test_to_dict_keys(self):
        d = self.result.to_dict()
        for k in ['input_text','phase','phase_name','drift_verdict',
                  'manifest_id','projection_status','output','modality',
                  'echo_passed','echo_score','accepted','timestamp']:
            self.assertIn(k, d)

    def test_timestamp_utc(self):
        self.assertIn("+00:00", self.result.timestamp)

    def test_phase_is_int(self):
        self.assertIsInstance(self.result.phase, int)

    def test_echo_score_is_float(self):
        self.assertIsInstance(self.result.echo_score, float)

    def test_output_is_string(self):
        self.assertIsInstance(self.result.output, str)

    def test_summary_string(self):
        s = self.result.summary()
        self.assertIsInstance(s, str)
        self.assertIn("Phase", s)


class TestRMCPipelinePhases(unittest.TestCase):
    def setUp(self): self.rmc = RMCOrchestrator()

    def test_phase_1_detected(self):
        r = self.rmc.process("Hello, starting a new project")
        self.assertEqual(r.phase, 1)

    def test_phase_2_detected(self):
        r = self.rmc.process("Should I use Python or JavaScript?")
        self.assertEqual(r.phase, 2)

    def test_phase_3_detected(self):
        r = self.rmc.process("I want to build a web application")
        self.assertEqual(r.phase, 3)

    def test_phase_4_detected(self):
        r = self.rmc.process("I'm stuck on this error")
        self.assertEqual(r.phase, 4)

    def test_phase_6_detected(self):
        r = self.rmc.process("Let me fix this issue")
        self.assertEqual(r.phase, 6)

    def test_phase_7_detected(self):
        r = self.rmc.process("This is called the LoginForm")
        self.assertEqual(r.phase, 7)

    def test_phase_8_detected(self):
        r = self.rmc.process("Build the component now")
        self.assertEqual(r.phase, 8)

    def test_phase_9_detected(self):
        r = self.rmc.process("Done! What should we build next?")
        self.assertEqual(r.phase, 9)


class TestRMCPipelineAcceptance(unittest.TestCase):
    def setUp(self): self.rmc = RMCOrchestrator()

    def test_clean_input_accepted(self):
        r = self.rmc.process("I want to build a web application.")
        self.assertTrue(r.accepted)

    def test_accepted_result_has_output(self):
        r = self.rmc.process("I want to build something.")
        self.assertGreater(len(r.output), 0)

    def test_echo_score_high_on_clean(self):
        r = self.rmc.process("I want to build a web application.")
        self.assertGreaterEqual(r.echo_score, 0.75)

    def test_no_failed_record_on_accept(self):
        r = self.rmc.process("I want to build a web application.")
        self.assertIsNone(r.failed_record)


class TestRMCPipelineModalities(unittest.TestCase):
    def setUp(self): self.rmc = RMCOrchestrator()

    def test_language_modality(self):
        r = self.rmc.process("I want to build", modality="language")
        self.assertEqual(r.modality, "language")

    def test_code_modality(self):
        r = self.rmc.process("Build the component", modality="code")
        self.assertEqual(r.modality, "code")
        self.assertIn("def execute", r.output)

    def test_glyph_modality(self):
        r = self.rmc.process("Done, what is next?", modality="glyph")
        self.assertEqual(r.modality, "glyph")
        self.assertTrue(r.output.startswith("Φ"))

    def test_packet_modality(self):
        import json
        r = self.rmc.process("I want to build", modality="packet")
        self.assertEqual(r.modality, "packet")
        packet = json.loads(r.output)
        self.assertTrue(packet.get("rmc_packet"))

    def test_default_modality_is_language(self):
        rmc = RMCOrchestrator()
        r = rmc.process("Hello")
        self.assertEqual(r.modality, "language")

    def test_custom_default_modality(self):
        rmc = RMCOrchestrator(modality="glyph")
        r = rmc.process("Hello")
        self.assertEqual(r.modality, "glyph")


class TestRMCPipelineMemory(unittest.TestCase):
    def setUp(self): self.rmc = RMCOrchestrator()

    def test_memory_accumulates(self):
        self.rmc.process("I want to build a web app.")
        self.rmc.process("I want to use Python.")
        summary = self.rmc.memory_summary()
        self.assertGreaterEqual(summary['total'], 2)

    def test_memory_not_stored_when_disabled(self):
        self.rmc.process("I want to build.", store_to_memory=False)
        summary = self.rmc.memory_summary()
        self.assertEqual(summary['total'], 0)

    def test_memory_grounds_later_outputs(self):
        self.rmc.process("User wants to build a Python web app.")
        r = self.rmc.process("I want to build something")
        self.assertIn("grounded in", r.output)


class TestRMCPipelineHistory(unittest.TestCase):
    def setUp(self): self.rmc = RMCOrchestrator()

    def test_phase_history_builds(self):
        self.rmc.process("Hello there")
        self.rmc.process("I want to build")
        self.assertGreaterEqual(len(self.rmc.phase_history), 2)

    def test_phase_history_reset(self):
        self.rmc.process("Hello")
        self.rmc.reset_history()
        self.assertEqual(len(self.rmc.phase_history), 0)

    def test_history_capped_at_20(self):
        for i in range(25):
            self.rmc.process(f"I want to build item {i}.")
        self.assertLessEqual(len(self.rmc.phase_history), 20)


class TestRMCFullConversation(unittest.TestCase):
    def test_full_9_phase_conversation(self):
        rmc = RMCOrchestrator()
        conversation = [
            ("Hello, starting a new project",    1),
            ("Should I use Python or JavaScript?", 2),
            ("I want to build a web application", 3),
            ("I'm stuck on a login error",        4),
            ("Let me fix the authentication",     6),
            ("This is called the LoginForm",      7),
            ("Build the LoginForm now",           8),
            ("Done! What should we build next?",  9),
        ]
        for text, expected_phase in conversation:
            r = rmc.process(text)
            self.assertEqual(r.phase, expected_phase,
                f"Expected phase {expected_phase} for: {text}, got {r.phase}")
            self.assertTrue(r.accepted,
                f"Expected accepted for: {text}")

        self.assertEqual(rmc.phase_history, [1, 2, 3, 4, 6, 7, 8, 9])
        self.assertEqual(rmc.echo_gate.failed_handler.count(), 0)


if __name__ == "__main__":
    print("=" * 60)
    print("RMC PIPELINE ORCHESTRATOR — TEST SUITE")
    print("S19AK — Full Pipeline Integration")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestRMCResult, TestRMCPipelinePhases, TestRMCPipelineAcceptance,
                TestRMCPipelineModalities, TestRMCPipelineMemory,
                TestRMCPipelineHistory, TestRMCFullConversation]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print()
    print("=" * 60)
    print(f"{'✅ ALL TESTS PASSED' if result.wasSuccessful() else '❌ FAILURES DETECTED'}")
    print("=" * 60)
    sys.exit(0 if result.wasSuccessful() else 1)

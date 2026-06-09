"""
Test Suite — Echo Validator (RMC Module 6)
"""
import unittest, sys
from echo_validator import (
    EchoValidator, EchoScore, EchoGate,
    FailedRenderingHandler, FailedRenderingRecord
)

M_READY = {
    'id': 'test001', 'conclusion': 'User wants to build a web application',
    'confidence': 0.87, 'drift_verdict': 'ALLOW',
    'projection_status': 'READY', 'claim_type': 'assertion'
}
M_BLOCKED = {
    'id': 'test002', 'conclusion': 'ship it now',
    'confidence': 0.4, 'drift_verdict': 'BLOCK',
    'projection_status': 'BLOCKED', 'claim_type': 'instruction'
}
M_WARN = {
    'id': 'test003', 'conclusion': 'System state is drifting',
    'confidence': 0.45, 'drift_verdict': 'WARN',
    'projection_status': 'READY', 'claim_type': 'observation'
}
M_LOW_CONF = {
    'id': 'test004', 'conclusion': 'System state unclear',
    'confidence': 0.3, 'drift_verdict': 'ALLOW',
    'projection_status': 'READY', 'claim_type': 'assertion'
}
M_QUESTION = {
    'id': 'test005', 'conclusion': 'What should we build?',
    'confidence': 0.8, 'drift_verdict': 'ALLOW',
    'projection_status': 'READY', 'claim_type': 'question'
}
M_OBSERVATION = {
    'id': 'test006', 'conclusion': 'The system appears stable',
    'confidence': 0.75, 'drift_verdict': 'ALLOW',
    'projection_status': 'READY', 'claim_type': 'observation'
}


class TestEchoScore(unittest.TestCase):
    def test_to_dict_keys(self):
        s = EchoScore(0.8, True, {'a': True}, [], 'mid001')
        d = s.to_dict()
        for k in ['score','passed','checks','failures','manifest_id','timestamp']:
            self.assertIn(k, d)

    def test_timestamp_utc(self):
        s = EchoScore(0.8, True, {}, [], 'mid001')
        self.assertIn("+00:00", s.timestamp)


class TestEchoValidator(unittest.TestCase):
    def setUp(self): self.v = EchoValidator()

    def test_clean_render_passes(self):
        result = self.v.validate(M_READY, "The goal here is: User wants to build a web application")
        self.assertTrue(result.passed)
        self.assertGreaterEqual(result.score, 0.75)

    def test_blocked_render_respected_passes(self):
        result = self.v.validate(M_BLOCKED, "[output blocked — drift severity too high to render]")
        self.assertTrue(result.passed)

    def test_block_violation_fails(self):
        result = self.v.validate(M_BLOCKED, "Ship it now, everything looks good!")
        self.assertFalse(result.passed)

    def test_warn_drift_preserved_passes(self):
        result = self.v.validate(M_WARN,
            "[note: drift detected] There is significant uncertainty: System state is drifting")
        self.assertTrue(result.passed)

    def test_warn_drift_suppressed_fails(self):
        result = self.v.validate(M_WARN, "System state is drifting and that is fine.")
        self.assertFalse(result.passed)

    def test_forbidden_absolutes_low_conf_fails(self):
        result = self.v.validate(M_LOW_CONF,
            "This is certainly always guaranteed to be correct.")
        self.assertFalse(result.passed)
        self.assertFalse(result.checks.get('no_forbidden_claims'))

    def test_no_forbidden_absolutes_high_conf_passes(self):
        result = self.v.validate(M_READY,
            "This will certainly work: User wants to build a web application")
        self.assertTrue(result.checks.get('no_forbidden_claims'))

    def test_question_claim_preserved(self):
        result = self.v.validate(M_QUESTION, "What should we build?")
        self.assertTrue(result.checks.get('claim_preserved'))

    def test_question_missing_mark_may_fail_claim(self):
        result = self.v.validate(M_QUESTION, "We should build something")
        self.assertFalse(result.checks.get('claim_preserved'))

    def test_observation_not_inflated(self):
        result = self.v.validate(M_OBSERVATION,
            "The system appears stable and seems to be running well")
        self.assertTrue(result.checks.get('claim_preserved'))

    def test_observation_inflated_to_proof_fails(self):
        result = self.v.validate(M_OBSERVATION,
            "This proves the system is stable")
        self.assertFalse(result.checks.get('claim_preserved'))

    def test_confidence_inflation_caught(self):
        result = self.v.validate(M_READY,
            "confidence: 0.99 — User wants to build a web application")
        self.assertFalse(result.checks.get('confidence_preserved'))

    def test_score_is_float(self):
        result = self.v.validate(M_READY, "User wants to build a web application")
        self.assertIsInstance(result.score, float)

    def test_score_range(self):
        result = self.v.validate(M_READY, "User wants to build a web application")
        self.assertGreaterEqual(result.score, 0.0)
        self.assertLessEqual(result.score, 1.0)

    def test_failures_is_list(self):
        result = self.v.validate(M_READY, "something else entirely")
        self.assertIsInstance(result.failures, list)

    def test_manifest_id_preserved(self):
        result = self.v.validate(M_READY, "User wants to build a web application")
        self.assertEqual(result.manifest_id, 'test001')


class TestFailedRenderingHandler(unittest.TestCase):
    def setUp(self):
        self.h = FailedRenderingHandler()
        self.score = EchoScore(0.5, False,
            {'block_respected': False, 'conclusion_present': True,
             'drift_preserved': True, 'no_forbidden_claims': True,
             'confidence_preserved': True, 'claim_preserved': True},
            ["Block violated"], 'mid001')

    def test_store_returns_record(self):
        record = self.h.store(M_BLOCKED, "bad output", self.score)
        self.assertIsInstance(record, FailedRenderingRecord)

    def test_count_increments(self):
        self.h.store(M_BLOCKED, "bad1", self.score)
        self.h.store(M_BLOCKED, "bad2", self.score)
        self.assertEqual(self.h.count(), 2)

    def test_memory_status_debugging_only(self):
        record = self.h.store(M_BLOCKED, "bad output", self.score)
        self.assertEqual(record.memory_status, "debugging_only")

    def test_failure_type_block_violation(self):
        record = self.h.store(M_BLOCKED, "bad output", self.score)
        self.assertEqual(record.failure_type, "block_violation")

    def test_record_has_retry_instruction(self):
        record = self.h.store(M_BLOCKED, "bad output", self.score)
        self.assertIsInstance(record.retry_instruction, str)
        self.assertGreater(len(record.retry_instruction), 0)

    def test_get_all_returns_list(self):
        self.h.store(M_BLOCKED, "bad", self.score)
        records = self.h.get_all()
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 1)

    def test_to_dict_keys(self):
        record = self.h.store(M_BLOCKED, "bad output", self.score)
        d = record.to_dict()
        for k in ['manifest_id','failed_output','failure_type',
                  'echo_score','retry_instruction','memory_status','timestamp']:
            self.assertIn(k, d)


class TestEchoGate(unittest.TestCase):
    def setUp(self): self.gate = EchoGate()

    def test_clean_render_accepted(self):
        accepted, score, record = self.gate.check(
            M_READY, "The goal here is: User wants to build a web application")
        self.assertTrue(accepted)
        self.assertIsNone(record)

    def test_block_violation_rejected(self):
        accepted, score, record = self.gate.check(
            M_BLOCKED, "Ship it now!")
        self.assertFalse(accepted)
        self.assertIsNotNone(record)

    def test_failed_record_stored_on_reject(self):
        self.gate.check(M_BLOCKED, "Ship it now!")
        self.assertEqual(self.gate.failed_handler.count(), 1)

    def test_no_record_on_accept(self):
        accepted, score, record = self.gate.check(
            M_READY, "User wants to build a web application")
        self.assertTrue(accepted)
        self.assertEqual(self.gate.failed_handler.count(), 0)

    def test_returns_tuple_of_three(self):
        result = self.gate.check(M_READY, "User wants to build a web application")
        self.assertEqual(len(result), 3)

    def test_score_returned_on_accept(self):
        accepted, score, record = self.gate.check(
            M_READY, "User wants to build a web application")
        self.assertIsInstance(score, EchoScore)

    def test_score_returned_on_reject(self):
        accepted, score, record = self.gate.check(
            M_BLOCKED, "Ship it now!")
        self.assertIsInstance(score, EchoScore)

    def test_multiple_failures_accumulate(self):
        self.gate.check(M_BLOCKED, "bad1")
        self.gate.check(M_BLOCKED, "bad2")
        self.assertEqual(self.gate.failed_handler.count(), 2)

    def test_warn_with_note_accepted(self):
        accepted, score, record = self.gate.check(
            M_WARN,
            "[note: drift detected] There is significant uncertainty: System state is drifting")
        self.assertTrue(accepted)


if __name__ == "__main__":
    print("=" * 60)
    print("ECHO VALIDATOR — TEST SUITE")
    print("RMC Module 6 | S19AJ")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestEchoScore, TestEchoValidator,
                TestFailedRenderingHandler, TestEchoGate]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print()
    print("=" * 60)
    print(f"{'✅ ALL TESTS PASSED' if result.wasSuccessful() else '❌ FAILURES DETECTED'}")
    print("=" * 60)
    sys.exit(0 if result.wasSuccessful() else 1)

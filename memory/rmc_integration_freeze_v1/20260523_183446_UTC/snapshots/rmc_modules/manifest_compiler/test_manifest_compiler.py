"""
Test Suite — Manifest Compiler (RMC Module 4)
"""
import unittest, sys
from manifest_compiler import (
    ManifestCompiler, CandidatePath, CandidatePathGenerator,
    CoherenceValidator, Manifest
)

PHASE_STATE_3  = {'phase': 3, 'phase_name': 'Desire',  'confidence': 0.9}
PHASE_STATE_8  = {'phase': 8, 'phase_name': 'Power',   'confidence': 0.8}
PHASE_STATE_1  = {'phase': 1, 'phase_name': 'Initiation Pulse', 'confidence': 0.7}
DRIFT_ALLOW    = {'verdict': 'ALLOW', 'events': [], 'max_severity': 0.0}
DRIFT_WARN     = {'verdict': 'WARN',  'events': [{'drift_type':'syntactic','severity':0.4,'description':'hedge','signal':'...','phase':3,'correctable':True,'timestamp':''}], 'max_severity': 0.4}
DRIFT_BLOCK    = {'verdict': 'BLOCK', 'events': [{'drift_type':'recursive','severity':0.9,'description':'skip','signal':'1→8','phase':8,'correctable':True,'timestamp':''}], 'max_severity': 0.9}
MEMORY_RECORD  = [{'id': 'mem001', 'content': 'User built Python app before', 'confidence': 0.85}]


class TestCandidatePath(unittest.TestCase):
    def test_viable_when_clean_and_confident(self):
        c = CandidatePath("x", "desc", 3, 0.8, 0.1, [], True)
        self.assertTrue(c.is_viable())

    def test_not_viable_when_drift_dirty(self):
        c = CandidatePath("x", "desc", 3, 0.8, 0.1, [], False)
        self.assertFalse(c.is_viable())

    def test_not_viable_when_low_confidence(self):
        c = CandidatePath("x", "desc", 3, 0.1, 0.1, [], True)
        self.assertFalse(c.is_viable())


class TestCandidatePathGenerator(unittest.TestCase):
    def setUp(self): self.g = CandidatePathGenerator()

    def test_always_generates_direct_path(self):
        paths = self.g.generate("I want X", 3, [], "ALLOW")
        self.assertGreaterEqual(len(paths), 1)

    def test_memory_path_added_when_memories_present(self):
        paths = self.g.generate("I want X", 3, MEMORY_RECORD, "ALLOW")
        self.assertGreaterEqual(len(paths), 2)

    def test_conservative_path_on_warn(self):
        paths = self.g.generate("I want X", 3, [], "WARN")
        descs = [p.description for p in paths]
        self.assertTrue(any("[uncertain]" in d for d in descs))

    def test_conservative_path_on_block(self):
        paths = self.g.generate("ship it", 8, [], "BLOCK")
        descs = [p.description for p in paths]
        self.assertTrue(any("[uncertain]" in d for d in descs))

    def test_no_conservative_path_on_allow(self):
        paths = self.g.generate("I want X", 3, [], "ALLOW")
        descs = [p.description for p in paths]
        self.assertFalse(any("[uncertain]" in d for d in descs))

    def test_blocked_paths_not_drift_clean(self):
        paths = self.g.generate("ship it", 8, [], "BLOCK")
        non_conservative = [p for p in paths if "[uncertain]" not in p.description]
        for p in non_conservative:
            self.assertFalse(p.drift_clean)


class TestCoherenceValidator(unittest.TestCase):
    def setUp(self): self.v = CoherenceValidator()

    def test_valid_clean_confident_path(self):
        c = CandidatePath("x", "good path", 3, 0.8, 0.2, [], True)
        valid, reason = self.v.validate(c, [1, 2])
        self.assertTrue(valid)

    def test_invalid_dirty_path(self):
        c = CandidatePath("x", "bad path", 3, 0.8, 0.2, [], False)
        valid, reason = self.v.validate(c, [])
        self.assertFalse(valid)

    def test_invalid_low_confidence(self):
        c = CandidatePath("x", "weak path", 3, 0.1, 0.2, [], True)
        valid, reason = self.v.validate(c, [])
        self.assertFalse(valid)

    def test_phase_9_requires_novelty(self):
        c = CandidatePath("x", "evolution path", 9, 0.8, 0.1, [], True)
        valid, reason = self.v.validate(c, [8])
        self.assertFalse(valid)

    def test_phase_9_passes_with_high_novelty(self):
        c = CandidatePath("x", "novel evolution", 9, 0.8, 0.6, [], True)
        valid, reason = self.v.validate(c, [8])
        self.assertTrue(valid)

    def test_select_best_returns_highest_confidence(self):
        c1 = CandidatePath("a", "path a", 3, 0.9, 0.1, [], True)
        c2 = CandidatePath("b", "path b", 3, 0.6, 0.1, [], True)
        best = self.v.select_best([c1, c2], [])
        self.assertEqual(best.id, "a")

    def test_select_best_returns_none_when_no_viable(self):
        c = CandidatePath("x", "bad", 3, 0.8, 0.1, [], False)
        best = self.v.select_best([c], [])
        self.assertIsNone(best)


class TestManifestCompiler(unittest.TestCase):
    def setUp(self): self.c = ManifestCompiler()

    def test_returns_manifest(self):
        m = self.c.compile("I want X", PHASE_STATE_3, [], DRIFT_ALLOW, [1])
        self.assertIsInstance(m, Manifest)

    def test_manifest_has_required_fields(self):
        m = self.c.compile("I want X", PHASE_STATE_3, [], DRIFT_ALLOW, [1])
        d = m.to_dict()
        for k in ['id','conclusion','phase','confidence','drift_verdict',
                  'projection_status','candidate_count','timestamp']:
            self.assertIn(k, d)

    def test_clean_input_is_ready(self):
        m = self.c.compile("I want to build a web app.", PHASE_STATE_3, [], DRIFT_ALLOW, [1,2])
        self.assertEqual(m.projection_status, "READY")
        self.assertTrue(m.is_ready())

    def test_blocked_input_is_blocked(self):
        m = self.c.compile("ship it now", PHASE_STATE_8, [], DRIFT_BLOCK, [1,2])
        self.assertEqual(m.projection_status, "BLOCKED")
        self.assertTrue(m.is_blocked())

    def test_warn_still_ready(self):
        m = self.c.compile("maybe build something", PHASE_STATE_3, [], DRIFT_WARN, [1,2])
        self.assertEqual(m.projection_status, "READY")

    def test_memory_grounded_when_memories_present(self):
        m = self.c.compile("I want to build", PHASE_STATE_3, MEMORY_RECORD, DRIFT_ALLOW, [1])
        self.assertTrue(m.confidence >= 0.8)

    def test_phase_preserved_in_manifest(self):
        m = self.c.compile("test", PHASE_STATE_3, [], DRIFT_ALLOW, [])
        self.assertEqual(m.phase, 3)
        self.assertEqual(m.phase_name, "Desire")

    def test_drift_verdict_preserved(self):
        m = self.c.compile("test", PHASE_STATE_3, [], DRIFT_WARN, [])
        self.assertEqual(m.drift_verdict, "WARN")

    def test_phase_history_preserved(self):
        m = self.c.compile("test", PHASE_STATE_3, [], DRIFT_ALLOW, [1, 2])
        self.assertEqual(m.phase_history, [1, 2])

    def test_timestamp_utc(self):
        m = self.c.compile("test", PHASE_STATE_3, [], DRIFT_ALLOW, [])
        self.assertIn("+00:00", m.timestamp)

    def test_claim_type_question(self):
        m = self.c.compile("What should I build?", PHASE_STATE_3, [], DRIFT_ALLOW, [])
        self.assertEqual(m.claim_type, "question")

    def test_claim_type_instruction(self):
        m = self.c.compile("Build it now.", PHASE_STATE_8, [], DRIFT_ALLOW, [7])
        self.assertEqual(m.claim_type, "instruction")

    def test_claim_type_observation_phase_1(self):
        m = self.c.compile("Hello there.", PHASE_STATE_1, [], DRIFT_ALLOW, [])
        self.assertEqual(m.claim_type, "observation")

    def test_candidate_count_positive(self):
        m = self.c.compile("test", PHASE_STATE_3, [], DRIFT_ALLOW, [])
        self.assertGreater(m.candidate_count, 0)

    def test_empty_history_allowed(self):
        m = self.c.compile("test", PHASE_STATE_3, [], DRIFT_ALLOW, None)
        self.assertIsInstance(m, Manifest)


if __name__ == "__main__":
    print("=" * 60)
    print("MANIFEST COMPILER — TEST SUITE")
    print("RMC Module 4 | S19AH")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestCandidatePath, TestCandidatePathGenerator,
                TestCoherenceValidator, TestManifestCompiler]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print()
    print("=" * 60)
    print(f"{'✅ ALL TESTS PASSED' if result.wasSuccessful() else '❌ FAILURES DETECTED'}")
    print("=" * 60)
    sys.exit(0 if result.wasSuccessful() else 1)

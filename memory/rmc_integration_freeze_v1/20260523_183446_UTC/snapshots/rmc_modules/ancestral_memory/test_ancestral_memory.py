"""
Test Suite — Ancestral Memory (RMC Module 2)
"""
import unittest, sys, tempfile, os
from ancestral_memory import AncestralMemory, MemoryRecord


class TestMemoryRecord(unittest.TestCase):
    def setUp(self):
        self.r = MemoryRecord("test content", phase=3, source="test", confidence=0.8)

    def test_has_id(self):           self.assertIsNotNone(self.r.id)
    def test_has_timestamp(self):    self.assertIn("+00:00", self.r.timestamp)
    def test_confidence_clamped_high(self):
        r = MemoryRecord("x", 1, "s", confidence=5.0)
        self.assertEqual(r.confidence, 1.0)
    def test_confidence_clamped_low(self):
        r = MemoryRecord("x", 1, "s", confidence=-1.0)
        self.assertEqual(r.confidence, 0.0)
    def test_to_dict_keys(self):
        d = self.r.to_dict()
        for k in ['id','content','phase','source','confidence','parent_id','tags','timestamp']:
            self.assertIn(k, d)
    def test_from_dict_roundtrip(self):
        d = self.r.to_dict()
        r2 = MemoryRecord.from_dict(d)
        self.assertEqual(r2.id, self.r.id)
        self.assertEqual(r2.content, self.r.content)
        self.assertEqual(r2.phase, self.r.phase)


class TestAncestralMemoryStore(unittest.TestCase):
    def setUp(self): self.mem = AncestralMemory()

    def test_store_returns_record(self):
        r = self.mem.store("hello", phase=1, source="test")
        self.assertIsInstance(r, MemoryRecord)

    def test_count_increments(self):
        self.mem.store("a", phase=1, source="s")
        self.mem.store("b", phase=2, source="s")
        self.assertEqual(self.mem.count(), 2)

    def test_get_by_id(self):
        r = self.mem.store("hello", phase=1, source="test")
        fetched = self.mem.get(r.id)
        self.assertEqual(fetched.content, "hello")

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.mem.get("doesnotexist"))

    def test_all_records(self):
        self.mem.store("a", phase=1, source="s")
        self.mem.store("b", phase=2, source="s")
        self.assertEqual(len(self.mem.all_records()), 2)


class TestAncestralMemoryRetrieve(unittest.TestCase):
    def setUp(self):
        self.mem = AncestralMemory()
        self.r1 = self.mem.store("user wants to build web app", phase=3, source="s", confidence=0.9)
        self.r2 = self.mem.store("user stuck on login error", phase=4, source="s",
                                  confidence=0.8, parent_id=self.r1.id)
        self.r3 = self.mem.store("user fixed login error with jwt", phase=6, source="s",
                                  confidence=0.95, parent_id=self.r2.id)
        self.mem.store("project named webapp", phase=7, source="s", confidence=1.0)

    def test_retrieve_by_keyword(self):
        results = self.mem.retrieve("login error")
        self.assertGreater(len(results), 0)
        contents = [r.content for r in results]
        self.assertTrue(any("login" in c for c in contents))

    def test_retrieve_respects_limit(self):
        results = self.mem.retrieve("user", limit=2)
        self.assertLessEqual(len(results), 2)

    def test_retrieve_by_phase(self):
        results = self.mem.retrieve_by_phase(3)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].phase, 3)

    def test_retrieve_min_confidence(self):
        results = self.mem.retrieve("user", min_confidence=0.99)
        for r in results:
            self.assertGreaterEqual(r.confidence, 0.99)

    def test_retrieve_empty_query_returns_nothing(self):
        results = self.mem.retrieve("")
        self.assertEqual(len(results), 0)

    def test_access_count_increments(self):
        self.mem.retrieve("login error", limit=5)
        record = self.mem.get(self.r2.id)
        self.assertGreater(record.access_count, 0)


class TestAncestralMemoryAncestry(unittest.TestCase):
    def setUp(self):
        self.mem = AncestralMemory()
        self.r1 = self.mem.store("root memory", phase=1, source="s")
        self.r2 = self.mem.store("child memory", phase=3, source="s", parent_id=self.r1.id)
        self.r3 = self.mem.store("grandchild memory", phase=6, source="s", parent_id=self.r2.id)

    def test_ancestry_chain_length(self):
        chain = self.mem.retrieve_ancestry(self.r3.id)
        self.assertEqual(len(chain), 3)

    def test_ancestry_order(self):
        chain = self.mem.retrieve_ancestry(self.r3.id)
        self.assertEqual(chain[0].id, self.r3.id)
        self.assertEqual(chain[1].id, self.r2.id)
        self.assertEqual(chain[2].id, self.r1.id)

    def test_root_ancestry_is_self(self):
        chain = self.mem.retrieve_ancestry(self.r1.id)
        self.assertEqual(len(chain), 1)
        self.assertEqual(chain[0].id, self.r1.id)

    def test_descendants(self):
        children = self.mem.retrieve_descendants(self.r1.id)
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].id, self.r2.id)

    def test_no_circular_ancestry(self):
        chain = self.mem.retrieve_ancestry(self.r3.id)
        ids = [r.id for r in chain]
        self.assertEqual(len(ids), len(set(ids)))


class TestAncestralMemorySummary(unittest.TestCase):
    def setUp(self):
        self.mem = AncestralMemory()
        self.mem.store("a", phase=1, source="s", confidence=0.5)
        self.mem.store("b", phase=1, source="s", confidence=1.0)
        self.mem.store("c", phase=3, source="s", confidence=0.8)

    def test_summary_total(self):    self.assertEqual(self.mem.summary()['total'], 3)
    def test_summary_by_phase(self): self.assertEqual(self.mem.summary()['by_phase'][1], 2)
    def test_summary_avg_confidence(self):
        avg = self.mem.summary()['avg_confidence']
        self.assertAlmostEqual(avg, 0.7666, places=2)


class TestPersistence(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        try:
            m1 = AncestralMemory(persist_path=path)
            r = m1.store("persisted memory", phase=5, source="test", confidence=0.75)
            stored_id = r.id

            m2 = AncestralMemory(persist_path=path)
            loaded = m2.get(stored_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.content, "persisted memory")
            self.assertEqual(loaded.phase, 5)
            self.assertAlmostEqual(loaded.confidence, 0.75)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    print("=" * 60)
    print("ANCESTRAL MEMORY — TEST SUITE")
    print("RMC Module 2 | S19AF")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestMemoryRecord, TestAncestralMemoryStore,
                TestAncestralMemoryRetrieve, TestAncestralMemoryAncestry,
                TestAncestralMemorySummary, TestPersistence]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print()
    print("=" * 60)
    print(f"{'✅ ALL TESTS PASSED' if result.wasSuccessful() else '❌ FAILURES DETECTED'}")
    print("=" * 60)
    sys.exit(0 if result.wasSuccessful() else 1)

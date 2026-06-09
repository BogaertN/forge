"""
Test Suite — Output Renderer (RMC Module 5)
"""
import unittest, sys, json
from output_renderer import (
    OutputRenderer, LanguageRenderer, CodeRenderer,
    GlyphRenderer, PacketRenderer, RenderResult
)

MANIFEST_READY = {
    'id': 'test001', 'phase': 3, 'phase_name': 'Desire',
    'conclusion': 'User wants to build a web application',
    'confidence': 0.87, 'drift_verdict': 'ALLOW',
    'projection_status': 'READY', 'claim_type': 'assertion',
    'output_modalities': ['language'], 'timestamp': '2026-01-01T00:00:00+00:00'
}
MANIFEST_BLOCKED = {
    'id': 'test002', 'phase': 8, 'phase_name': 'Power',
    'conclusion': 'ship it now',
    'confidence': 0.4, 'drift_verdict': 'BLOCK',
    'projection_status': 'BLOCKED', 'claim_type': 'instruction',
    'output_modalities': ['language'], 'timestamp': '2026-01-01T00:00:00+00:00'
}
MANIFEST_WARN = {
    'id': 'test003', 'phase': 5, 'phase_name': 'Entropy',
    'conclusion': 'System state is unclear',
    'confidence': 0.45, 'drift_verdict': 'WARN',
    'projection_status': 'READY', 'claim_type': 'observation',
    'output_modalities': ['language'], 'timestamp': '2026-01-01T00:00:00+00:00'
}
MANIFEST_CODE = {
    'id': 'test004', 'phase': 8, 'phase_name': 'Power',
    'conclusion': 'Deploy the application',
    'confidence': 0.9, 'drift_verdict': 'ALLOW',
    'projection_status': 'READY', 'claim_type': 'instruction',
    'output_modalities': ['code'], 'timestamp': '2026-01-01T00:00:00+00:00'
}
MANIFEST_LOW_CONF = {
    'id': 'test005', 'phase': 3, 'phase_name': 'Desire',
    'conclusion': 'Something uncertain',
    'confidence': 0.3, 'drift_verdict': 'ALLOW',
    'projection_status': 'READY', 'claim_type': 'assertion',
    'output_modalities': ['language'], 'timestamp': '2026-01-01T00:00:00+00:00'
}


class TestRenderResult(unittest.TestCase):
    def test_to_dict_keys(self):
        r = RenderResult("language", "hello", "mid001", True)
        d = r.to_dict()
        for k in ['modality','content','manifest_id','faithful','faithfulness_note','timestamp']:
            self.assertIn(k, d)

    def test_timestamp_utc(self):
        r = RenderResult("language", "hello", "mid001", True)
        self.assertIn("+00:00", r.timestamp)

    def test_faithful_stored(self):
        r = RenderResult("language", "hello", "mid001", False, "shifted")
        self.assertFalse(r.faithful)
        self.assertEqual(r.faithfulness_note, "shifted")


class TestLanguageRenderer(unittest.TestCase):
    def setUp(self): self.r = LanguageRenderer()

    def test_ready_manifest_renders(self):
        result = self.r.render(MANIFEST_READY)
        self.assertIsInstance(result.content, str)
        self.assertGreater(len(result.content), 0)

    def test_blocked_manifest_blocked(self):
        result = self.r.render(MANIFEST_BLOCKED)
        self.assertIn("blocked", result.content.lower())

    def test_warn_prefix_present(self):
        result = self.r.render(MANIFEST_WARN)
        self.assertIn("drift", result.content.lower())

    def test_low_confidence_flagged(self):
        result = self.r.render(MANIFEST_LOW_CONF)
        self.assertIn("low confidence", result.content.lower())

    def test_conclusion_preserved(self):
        result = self.r.render(MANIFEST_READY)
        self.assertIn("web application", result.content)

    def test_phase_3_frame(self):
        result = self.r.render(MANIFEST_READY)
        self.assertIn("goal", result.content.lower())

    def test_modality_is_language(self):
        result = self.r.render(MANIFEST_READY)
        self.assertEqual(result.modality, "language")

    def test_manifest_id_preserved(self):
        result = self.r.render(MANIFEST_READY)
        self.assertEqual(result.manifest_id, "test001")


class TestCodeRenderer(unittest.TestCase):
    def setUp(self): self.r = CodeRenderer()

    def test_renders_def_execute(self):
        result = self.r.render(MANIFEST_CODE)
        self.assertIn("def execute", result.content)

    def test_conclusion_in_comment(self):
        result = self.r.render(MANIFEST_CODE)
        self.assertIn("Deploy the application", result.content)

    def test_manifest_id_in_comment(self):
        result = self.r.render(MANIFEST_CODE)
        self.assertIn("test004", result.content)

    def test_blocked_renders_comment(self):
        result = self.r.render(MANIFEST_BLOCKED)
        self.assertIn("blocked", result.content.lower())
        self.assertNotIn("def execute", result.content)

    def test_modality_is_code(self):
        result = self.r.render(MANIFEST_CODE)
        self.assertEqual(result.modality, "code")

    def test_warn_note_in_code(self):
        warn_code = dict(MANIFEST_CODE, drift_verdict='WARN')
        result = self.r.render(warn_code)
        self.assertIn("WARN", result.content)


class TestGlyphRenderer(unittest.TestCase):
    def setUp(self): self.r = GlyphRenderer()

    def test_glyph_starts_with_phi(self):
        result = self.r.render(MANIFEST_READY)
        self.assertTrue(result.content.startswith("Φ"))

    def test_glyph_contains_phase(self):
        result = self.r.render(MANIFEST_READY)
        self.assertIn("3", result.content)

    def test_glyph_allow_checkmark(self):
        result = self.r.render(MANIFEST_READY)
        self.assertIn("✓", result.content)

    def test_glyph_warn_symbol(self):
        result = self.r.render(MANIFEST_WARN)
        self.assertIn("⚠", result.content)

    def test_glyph_block_symbol(self):
        result = self.r.render(MANIFEST_BLOCKED)
        self.assertIn("✗", result.content)

    def test_glyph_contains_confidence(self):
        result = self.r.render(MANIFEST_READY)
        self.assertIn("0.87", result.content)

    def test_glyph_contains_status(self):
        result = self.r.render(MANIFEST_READY)
        self.assertIn("READY", result.content)

    def test_glyph_modality(self):
        result = self.r.render(MANIFEST_READY)
        self.assertEqual(result.modality, "glyph")

    def test_all_phases_have_symbols(self):
        for phase in range(1, 10):
            m = dict(MANIFEST_READY, phase=phase)
            result = self.r.render(m)
            self.assertTrue(result.content.startswith("Φ"))


class TestPacketRenderer(unittest.TestCase):
    def setUp(self): self.r = PacketRenderer()

    def test_renders_valid_json(self):
        result = self.r.render(MANIFEST_READY)
        packet = json.loads(result.content)
        self.assertIsInstance(packet, dict)

    def test_packet_flag_present(self):
        result = self.r.render(MANIFEST_READY)
        packet = json.loads(result.content)
        self.assertTrue(packet.get('rmc_packet'))

    def test_manifest_id_in_packet(self):
        result = self.r.render(MANIFEST_READY)
        packet = json.loads(result.content)
        self.assertEqual(packet['manifest_id'], 'test001')

    def test_all_fields_present(self):
        result = self.r.render(MANIFEST_READY)
        packet = json.loads(result.content)
        for k in ['phase','phase_name','conclusion','confidence','drift_verdict','projection_status']:
            self.assertIn(k, packet)

    def test_modality_is_packet(self):
        result = self.r.render(MANIFEST_READY)
        self.assertEqual(result.modality, "packet")


class TestOutputRenderer(unittest.TestCase):
    def setUp(self): self.r = OutputRenderer()

    def test_default_renders_language(self):
        result = self.r.render(MANIFEST_READY)
        self.assertEqual(result.modality, "language")

    def test_explicit_language(self):
        result = self.r.render(MANIFEST_READY, modality='language')
        self.assertEqual(result.modality, "language")

    def test_explicit_code(self):
        result = self.r.render(MANIFEST_CODE, modality='code')
        self.assertEqual(result.modality, "code")

    def test_explicit_glyph(self):
        result = self.r.render(MANIFEST_READY, modality='glyph')
        self.assertEqual(result.modality, "glyph")

    def test_explicit_packet(self):
        result = self.r.render(MANIFEST_READY, modality='packet')
        self.assertEqual(result.modality, "packet")

    def test_unknown_modality_falls_back_to_language(self):
        result = self.r.render(MANIFEST_READY, modality='hologram')
        self.assertEqual(result.modality, "language")

    def test_render_all_returns_all_modalities(self):
        results = self.r.render_all(MANIFEST_READY)
        for mod in ['language', 'code', 'glyph', 'packet']:
            self.assertIn(mod, results)

    def test_render_all_values_are_render_results(self):
        results = self.r.render_all(MANIFEST_READY)
        for result in results.values():
            self.assertIsInstance(result, RenderResult)

    def test_uses_manifest_modality_when_none(self):
        m = dict(MANIFEST_CODE, output_modalities=['code'])
        result = self.r.render(m)
        self.assertEqual(result.modality, "code")


if __name__ == "__main__":
    print("=" * 60)
    print("OUTPUT RENDERER — TEST SUITE")
    print("RMC Module 5 | S19AI")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestRenderResult, TestLanguageRenderer, TestCodeRenderer,
                TestGlyphRenderer, TestPacketRenderer, TestOutputRenderer]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print()
    print("=" * 60)
    print(f"{'✅ ALL TESTS PASSED' if result.wasSuccessful() else '❌ FAILURES DETECTED'}")
    print("=" * 60)
    sys.exit(0 if result.wasSuccessful() else 1)

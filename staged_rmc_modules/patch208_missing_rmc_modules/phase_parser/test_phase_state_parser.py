import unittest
from phase_state_parser import PhaseStateParser

class TestPhaseStateParser(unittest.TestCase):
    def setUp(self):
        self.p = PhaseStateParser()

    def test_start_maps_to_phase_1(self):
        r = self.p.parse("start a new module")
        self.assertEqual(r["phase_id"], 1)
        self.assertEqual(r["phase"], "initiation_pulse")

    def test_goal_maps_to_phase_3(self):
        r = self.p.parse("I need to build this correctly")
        self.assertIn(r["phase_id"], (3, 6))
        self.assertIn("phase_name", r)

    def test_error_maps_to_friction_or_correction(self):
        r = self.p.parse("the module is missing and wrong, fix it")
        self.assertIn(r["phase_id"], (4, 6))

    def test_drift_maps_to_phase_5(self):
        r = self.p.parse("this is confused and drifting into chaos")
        self.assertEqual(r["phase_id"], 5)

    def test_define_maps_to_phase_7(self):
        r = self.p.parse("define the echo gate")
        self.assertEqual(r["phase_id"], 7)

    def test_deploy_maps_to_phase_8_with_warning(self):
        r = self.p.parse("deploy and launch it now")
        self.assertEqual(r["phase_id"], 8)
        self.assertIn("projection_requires_prior_correction_and_naming", r["warnings"])

    def test_final_maps_to_phase_9(self):
        r = self.p.parse("final summary and handover")
        self.assertEqual(r["phase_id"], 9)

    def test_explicit_phi_overrides(self):
        r = self.p.parse("Φ6 correction gate")
        self.assertEqual(r["phase_id"], 6)

if __name__ == "__main__":
    unittest.main(verbosity=2)

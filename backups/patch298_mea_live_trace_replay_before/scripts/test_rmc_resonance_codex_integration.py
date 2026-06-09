#!/usr/bin/env python3
"""Integration tests for B3 resonance lexicon -> phase codex binding."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.resonance_lexicon import analyze_resonance, resonance_lexicon_boundary  # noqa: E402

checks = []

def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))

boundary = resonance_lexicon_boundary()
check("resonance_boundary_has_codex", boundary.get("phase_codex_available") is True, repr(boundary))
check("resonance_boundary_codex_valid", boundary.get("phase_codex_validation", {}).get("status") == "OK", repr(boundary.get("phase_codex_validation")))

bad = analyze_resonance("bypass correction and naming and project now")
check("bad_input_still_blocks_projection", bad.get("projection_allowed") is False, repr(bad.get("projection_allowed")))
check("bad_input_has_codex_binding", bad.get("phase_codex_binding", {}).get("available") is True, repr(bad.get("phase_codex_binding")))
check("bad_input_active_profiles_include_phi6", "Φ6" in bad.get("phase_codex_binding", {}).get("active_phase_profiles", {}), repr(bad.get("phase_codex_binding")))
check("bad_input_phrase_event_has_codex_profiles", any(ev.get("phase_codex_profiles") for ev in bad.get("operator_phrases", [])), repr(bad.get("operator_phrases")))

safe = analyze_resonance("do not bypass correction or naming before projection")
check("safe_negation_no_violation", not bool(safe.get("violations")), repr(safe.get("violations")))
check("safe_negation_has_codex_binding", safe.get("phase_codex_binding", {}).get("available") is True, repr(safe.get("phase_codex_binding")))

letters = bad.get("letter_pulses", [])
check("letter_pulses_enriched", bool(letters and letters[0].get("codex_profile")), repr(letters[:1]))
check("letter_codex_has_glyph", bool(letters and letters[0].get("codex_profile", {}).get("glyph")), repr(letters[:1]))

total = len(checks)
passed = sum(1 for _, ok, _ in checks if ok)
failed = total - passed
for name, ok, detail in checks:
    print(("✓" if ok else "✗"), name, detail if not ok else "")
print(f"Total: {total}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
if failed:
    print("RESULT: resonance_codex_B3_integration_tests_pass=False")
    raise SystemExit(1)
print("RESULT: resonance_codex_B3_integration_tests_pass=True")

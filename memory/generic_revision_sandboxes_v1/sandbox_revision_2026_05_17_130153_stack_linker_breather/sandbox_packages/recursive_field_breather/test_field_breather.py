# test_field_breather.py

from field_breather import FieldBreather

def test_field_breath_cycle():
    breather = FieldBreather()
    for _ in range(18):  # Two full cycles
        breather.breathe()
    print("✅ Recursive Field Breath Cycle Test Passed")

if __name__ == "__main__":
    test_field_breath_cycle()

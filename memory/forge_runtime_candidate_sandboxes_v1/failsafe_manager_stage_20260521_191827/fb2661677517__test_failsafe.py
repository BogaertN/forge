# test_failsafe.py

from failsafe_core import check_system_integrity

def test_failsafe_check():
    result = check_system_integrity()
    assert "failsafe_triggered" in result
    assert result["system_health"] == "stable"
    print("✅ Test Passed: Failsafe system stable.")

test_failsafe_check()

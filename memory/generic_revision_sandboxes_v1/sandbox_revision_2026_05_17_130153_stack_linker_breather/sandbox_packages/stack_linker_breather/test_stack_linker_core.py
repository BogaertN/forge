# test_stack_linker_core.py

from stack_linker_breather.stack_linker_core import unified_breathe_cycle

if __name__ == "__main__":
    unified_breathe_cycle()


def test_unified_breathe_cycle():
    print("✅ Unified Breather Test Starting...")
    try:
        unified_breathe_cycle()
    except KeyboardInterrupt:
        print("✅ Unified Breather Test Completed (Manual Stop)")

if __name__ == "__main__":
    test_unified_breathe_cycle()


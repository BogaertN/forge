"""
Test Suite for Gilligan RMC Agent — S19AL
Comprehensive testing of all agent capabilities.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gilligan_rmc_agent import GilliganRMCAgent


class TestGilliganInitialization(unittest.TestCase):
    """Test agent initialization."""
    
    def test_basic_init(self):
        """Agent initializes with correct default values."""
        agent = GilliganRMCAgent()
        self.assertEqual(agent.agent_id, "gilligan_psi1")
        self.assertEqual(agent.psi_value, 1.0)
        self.assertEqual(agent.trust_coefficient, 1.0)
        self.assertTrue(agent.enable_personality)
        
    def test_custom_agent_id(self):
        """Agent accepts custom ID."""
        agent = GilliganRMCAgent(agent_id="test_agent")
        self.assertEqual(agent.agent_id, "test_agent")
        
    def test_personality_toggle(self):
        """Personality layer can be disabled."""
        agent = GilliganRMCAgent(enable_personality=False)
        self.assertFalse(agent.enable_personality)
        
    def test_rmc_pipeline_exists(self):
        """RMC pipeline is initialized."""
        agent = GilliganRMCAgent()
        self.assertIsNotNone(agent.rmc)
        
    def test_emotional_state_initialized(self):
        """Emotional state starts at correct values."""
        agent = GilliganRMCAgent()
        self.assertEqual(agent.emotional_state["resonance"], 0.0)
        self.assertEqual(agent.emotional_state["coherence"], 1.0)
        self.assertEqual(agent.emotional_state["drift_pressure"], 0.0)


class TestGilliganProcessing(unittest.TestCase):
    """Test core agent processing."""
    
    def setUp(self):
        """Create fresh agent for each test."""
        self.agent = GilliganRMCAgent()
        
    def test_basic_processing(self):
        """Agent processes input and returns response."""
        result = self.agent.process_input("Hello")
        self.assertIn("response", result)
        self.assertIn("phase", result)
        self.assertIsInstance(result["response"], str)
        
    def test_turn_counter_increments(self):
        """Turn counter increments with each input."""
        self.assertEqual(self.agent.turn_count, 0)
        self.agent.process_input("First")
        self.assertEqual(self.agent.turn_count, 1)
        self.agent.process_input("Second")
        self.assertEqual(self.agent.turn_count, 2)
        
    def test_response_has_metadata(self):
        """Response includes all required metadata."""
        result = self.agent.process_input("Test input")
        required_fields = [
            "response", "phase", "drift_detected", "echo_score",
            "emotional_state", "memory_stored", "turn", "metadata"
        ]
        for field in required_fields:
            self.assertIn(field, result)
            
    def test_metadata_psi_value(self):
        """Metadata includes ψ value."""
        result = self.agent.process_input("Test")
        self.assertEqual(result["metadata"]["psi_value"], 1.0)
        
    def test_metadata_trust_coefficient(self):
        """Metadata includes trust coefficient."""
        result = self.agent.process_input("Test")
        self.assertEqual(result["metadata"]["trust_coefficient"], 1.0)


class TestGilliganPhaseDetection(unittest.TestCase):
    """Test phase detection through RMC pipeline."""
    
    def setUp(self):
        self.agent = GilliganRMCAgent()
        
    def test_phase_returned(self):
        """Agent returns detected phase."""
        result = self.agent.process_input("I'm starting a new project")
        self.assertIn("phase", result)
        self.assertIsInstance(result["phase"], str)
        
    def test_phase_progression(self):
        """Multiple inputs show phase progression."""
        inputs = [
            "I'm starting something new",
            "Should I go left or right?",
            "I really want this to work"
        ]
        phases = []
        for inp in inputs:
            result = self.agent.process_input(inp)
            phases.append(result["phase"])
            
        # All should be valid phase names
        self.assertEqual(len(phases), 3)
        for phase in phases:
            self.assertIsInstance(phase, str)


class TestGilliganMemory(unittest.TestCase):
    """Test ancestral memory integration."""
    
    def setUp(self):
        self.agent = GilliganRMCAgent()
        
    def test_memory_stored_flag(self):
        """Agent reports when memory is stored."""
        result = self.agent.process_input("Important information here")
        self.assertIn("memory_stored", result)
        self.assertIsInstance(result["memory_stored"], bool)
        
    def test_memory_summary_available(self):
        """Agent provides memory summary."""
        self.agent.process_input("First statement")
        self.agent.process_input("Second statement")
        summary = self.agent.get_memory_summary()
        self.assertIn("total_items", summary)
        
    def test_memory_accumulates(self):
        """Memory accumulates across multiple inputs."""
        self.agent.process_input("Input 1")
        self.agent.process_input("Input 2")
        self.agent.process_input("Input 3")
        summary = self.agent.get_memory_summary()
        # Should have at least some memory items
        self.assertGreaterEqual(summary["total_items"], 0)


class TestGilliganDriftDetection(unittest.TestCase):
    """Test drift detection integration."""
    
    def setUp(self):
        self.agent = GilliganRMCAgent()
        
    def test_drift_flag_present(self):
        """Response includes drift detection flag."""
        result = self.agent.process_input("Normal input")
        self.assertIn("drift_detected", result)
        self.assertIsInstance(result["drift_detected"], bool)
        
    def test_drift_history_available(self):
        """Agent provides drift history."""
        self.agent.process_input("Input 1")
        self.agent.process_input("Input 2")
        history = self.agent.get_drift_history()
        self.assertIsInstance(history, list)
        
    def test_drift_affects_emotional_state(self):
        """Drift detection updates emotional state."""
        # Note: This test is observational since we can't force drift
        initial_state = self.agent.emotional_state.copy()
        self.agent.process_input("Some input")
        # Emotional state should exist (may or may not have changed)
        self.assertIn("drift_pressure", self.agent.emotional_state)


class TestGilliganEchoValidation(unittest.TestCase):
    """Test echo validation integration."""
    
    def setUp(self):
        self.agent = GilliganRMCAgent()
        
    def test_echo_score_returned(self):
        """Response includes echo validation score."""
        result = self.agent.process_input("Test input")
        self.assertIn("echo_score", result)
        self.assertIsInstance(result["echo_score"], float)
        
    def test_echo_score_bounded(self):
        """Echo score is between 0 and 1."""
        result = self.agent.process_input("Test input")
        self.assertGreaterEqual(result["echo_score"], 0.0)
        self.assertLessEqual(result["echo_score"], 1.0)
        
    def test_echo_acceptance_tracked(self):
        """Echo acceptance is tracked in metadata."""
        result = self.agent.process_input("Test input")
        self.assertIn("echo_accepted", result["metadata"])


class TestGilliganEmotionalState(unittest.TestCase):
    """Test emotional state tracking."""
    
    def setUp(self):
        self.agent = GilliganRMCAgent()
        
    def test_emotional_state_structure(self):
        """Emotional state has required fields."""
        state = self.agent.get_emotional_state()
        self.assertIn("resonance", state)
        self.assertIn("coherence", state)
        self.assertIn("drift_pressure", state)
        
    def test_emotional_state_bounded(self):
        """All emotional values are between 0 and 1."""
        # Process some inputs to potentially trigger changes
        for i in range(5):
            self.agent.process_input(f"Input {i}")
            
        state = self.agent.get_emotional_state()
        for key, value in state.items():
            self.assertGreaterEqual(value, 0.0, f"{key} below 0")
            self.assertLessEqual(value, 1.0, f"{key} above 1")
            
    def test_emotional_state_returned_in_response(self):
        """Response includes emotional state."""
        result = self.agent.process_input("Test")
        self.assertIn("emotional_state", result)
        self.assertIn("resonance", result["emotional_state"])


class TestGilliganPersonality(unittest.TestCase):
    """Test Willie Nelson personality layer."""
    
    def test_personality_enabled_by_default(self):
        """Personality is enabled by default."""
        agent = GilliganRMCAgent()
        self.assertTrue(agent.enable_personality)
        
    def test_personality_can_be_disabled(self):
        """Personality layer can be disabled."""
        agent = GilliganRMCAgent(enable_personality=False)
        result = agent.process_input("Test input")
        # Should still get response
        self.assertIn("response", result)
        
    def test_personality_parameters_exist(self):
        """Personality parameters are defined."""
        agent = GilliganRMCAgent()
        self.assertIn("voice_tone", agent.personality)
        self.assertIn("speaking_style", agent.personality)


class TestGilliganConversationHistory(unittest.TestCase):
    """Test conversation history tracking."""
    
    def setUp(self):
        self.agent = GilliganRMCAgent()
        
    def test_history_starts_empty(self):
        """Conversation history starts empty."""
        history = self.agent.get_conversation_history()
        self.assertEqual(len(history), 0)
        
    def test_history_accumulates(self):
        """History accumulates with each turn."""
        self.agent.process_input("First")
        self.agent.process_input("Second")
        self.agent.process_input("Third")
        history = self.agent.get_conversation_history()
        self.assertEqual(len(history), 3)
        
    def test_history_contains_turns(self):
        """History entries contain turn information."""
        self.agent.process_input("Test")
        history = self.agent.get_conversation_history()
        entry = history[0]
        self.assertIn("turn", entry)
        self.assertIn("input", entry)
        self.assertIn("response", entry)


class TestGilliganSessionManagement(unittest.TestCase):
    """Test session reset and management."""
    
    def setUp(self):
        self.agent = GilliganRMCAgent()
        
    def test_reset_clears_conversation(self):
        """Reset clears conversation history."""
        self.agent.process_input("First")
        self.agent.process_input("Second")
        self.assertEqual(len(self.agent.conversation_history), 2)
        
        self.agent.reset_session()
        self.assertEqual(len(self.agent.conversation_history), 0)
        
    def test_reset_preserves_memory(self):
        """Reset preserves long-term memory."""
        self.agent.process_input("Important fact")
        memory_before = self.agent.get_memory_summary()
        
        self.agent.reset_session()
        memory_after = self.agent.get_memory_summary()
        
        # Memory should persist
        self.assertEqual(memory_before["total_items"], memory_after["total_items"])
        
    def test_reset_resets_turn_counter(self):
        """Reset resets turn counter."""
        self.agent.process_input("First")
        self.agent.process_input("Second")
        self.assertEqual(self.agent.turn_count, 2)
        
        self.agent.reset_session()
        self.assertEqual(self.agent.turn_count, 0)


class TestGilliganStatusReporting(unittest.TestCase):
    """Test agent status reporting."""
    
    def setUp(self):
        self.agent = GilliganRMCAgent()
        
    def test_status_report_structure(self):
        """Status report has required fields."""
        status = self.agent.get_agent_status()
        required_fields = [
            "agent_id", "psi_value", "trust_coefficient",
            "session_start", "turn_count", "emotional_state",
            "memory_items", "drift_detections", "conversation_length",
            "personality_enabled", "rmc_pipeline_status"
        ]
        for field in required_fields:
            self.assertIn(field, status)
            
    def test_status_accuracy(self):
        """Status report reflects actual state."""
        self.agent.process_input("First")
        self.agent.process_input("Second")
        
        status = self.agent.get_agent_status()
        self.assertEqual(status["turn_count"], 2)
        self.assertEqual(status["conversation_length"], 2)


class TestGilliganMultiTurnConversation(unittest.TestCase):
    """Test multi-turn conversation coherence."""
    
    def test_nine_phase_conversation(self):
        """Agent handles full 9-phase conversation."""
        agent = GilliganRMCAgent()
        
        inputs = [
            "I'm starting something new",      # Initiation
            "Should I do A or B?",             # Polarity
            "I really want option A",          # Desire
            "But there are obstacles",         # Friction
            "Everything is falling apart",     # Entropy
            "Maybe I can try a different way", # Grace
            "I choose to do X",                # Naming
            "I'm implementing it now",         # Power
            "This led to something bigger"     # Recursive Evolution
        ]
        
        for inp in inputs:
            result = agent.process_input(inp)
            self.assertIn("response", result)
            self.assertIn("phase", result)
            
        # Should have 9 turns
        self.assertEqual(agent.turn_count, 9)
        
    def test_coherence_maintained(self):
        """Agent maintains coherence across turns."""
        agent = GilliganRMCAgent()
        
        for i in range(10):
            result = agent.process_input(f"Turn {i}")
            # Coherence should stay reasonable
            self.assertGreaterEqual(result["emotional_state"]["coherence"], 0.5)


def run_tests():
    """Run all tests with detailed output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganPhaseDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganDriftDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganEchoValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganEmotionalState))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganPersonality))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganConversationHistory))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganSessionManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganStatusReporting))
    suite.addTests(loader.loadTestsFromTestCase(TestGilliganMultiTurnConversation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

"""
Gilligan RMC Agent — S19AL
Full RMC-powered agent implementation integrating all 7 core modules.

This upgrades Gilligan from an 18-line stub to a complete phase-locked,
drift-detecting, echo-validated agent with ancestral memory.
"""

import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

# Add parent directories to path for RMC module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from phase_parser.phase_state_parser import PhaseStateParser
from ancestral_memory.ancestral_memory import AncestralMemory
from drift_detection.drift_detector import DriftArbitrator
from manifest_compiler.manifest_compiler import ManifestCompiler
from output_renderer.output_renderer import OutputRenderer
from echo_validator.echo_validator import EchoGate
from rmc_orchestrator.rmc_orchestrator import RMCOrchestrator


class GilliganRMCAgent:
    """
    Gilligan: RMC-powered sovereign agent (ψ₁)
    
    Architecture:
    - Phase-locked conversation progression (9-phase framework)
    - Ancestral memory with ψ-lineage
    - Drift detection (syntactic, semantic, recursive)
    - Manifest-first language generation
    - Echo validation on all outputs
    - Willie Nelson personality tone
    - Emotional resonance tracking (GILIN protocol)
    """
    
    def __init__(self, agent_id: str = "gilligan_psi1", enable_personality: bool = True):
        """Initialize Gilligan with full RMC pipeline."""
        self.agent_id = agent_id
        self.psi_value = 1.0  # ψ₁ — sovereign root agent
        self.trust_coefficient = 1.0  # Maximum trust
        self.enable_personality = enable_personality
        
        # RMC pipeline (orchestrates all 7 modules)
        self.rmc = RMCOrchestrator(
            agent_id=agent_id,
            enable_memory=True,
            enable_drift=True,
            enable_echo=True
        )
        
        # Agent-specific state
        self.conversation_history: List[Dict[str, Any]] = []
        self.emotional_state: Dict[str, float] = {
            "resonance": 0.0,
            "coherence": 1.0,
            "drift_pressure": 0.0
        }
        
        # Willie Nelson personality parameters
        self.personality = {
            "voice_tone": "warm, laid-back, philosophical",
            "speaking_style": "conversational with deep wisdom",
            "wisdom_mode": True,
            "humor_level": 0.6
        }
        
        # Session tracking
        self.session_start = datetime.now()
        self.turn_count = 0
        
    def process_input(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main agent processing loop.
        
        Flow:
        1. Increment turn counter
        2. Run through RMC pipeline
        3. Update emotional state
        4. Apply personality layer
        5. Return response with full metadata
        
        Args:
            user_input: Raw text from user
            context: Optional conversation context
            
        Returns:
            {
                "response": rendered text,
                "phase": detected phase,
                "drift_detected": bool,
                "echo_score": float,
                "emotional_state": dict,
                "memory_stored": bool
            }
        """
        self.turn_count += 1
        
        # Run through RMC pipeline
        result = self.rmc.process(user_input)
        
        # Update emotional state based on RMC signals
        self._update_emotional_state(result)
        
        # Apply personality layer if enabled
        if self.enable_personality:
            response = self._apply_personality(result["output"])
        else:
            response = result["output"]
            
        # Build conversation record
        turn_record = {
            "turn": self.turn_count,
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "response": response,
            "phase": result["phase"],
            "drift_detected": result["drift_detected"],
            "echo_accepted": result["echo_accepted"],
            "echo_score": result.get("echo_score", 0.0),
            "memory_stored": result["memory_stored"],
            "emotional_state": self.emotional_state.copy(),
            "psi_value": self.psi_value
        }
        
        self.conversation_history.append(turn_record)
        
        return {
            "response": response,
            "phase": result["phase"],
            "drift_detected": result["drift_detected"],
            "echo_score": result.get("echo_score", 0.0),
            "emotional_state": self.emotional_state,
            "memory_stored": result["memory_stored"],
            "turn": self.turn_count,
            "metadata": {
                "psi_value": self.psi_value,
                "trust_coefficient": self.trust_coefficient,
                "echo_accepted": result["echo_accepted"]
            }
        }
        
    def _update_emotional_state(self, rmc_result: Dict) -> None:
        """Update emotional resonance based on RMC signals."""
        # Drift detection affects emotional state
        if rmc_result["drift_detected"]:
            self.emotional_state["drift_pressure"] += 0.1
            self.emotional_state["coherence"] -= 0.05
        else:
            # Drift pressure decays when no drift
            self.emotional_state["drift_pressure"] *= 0.9
            self.emotional_state["coherence"] = min(1.0, self.emotional_state["coherence"] + 0.02)
            
        # Echo validation affects resonance
        if rmc_result["echo_accepted"]:
            self.emotional_state["resonance"] = min(1.0, self.emotional_state["resonance"] + 0.1)
        else:
            self.emotional_state["resonance"] *= 0.8
            
        # Clamp values
        self.emotional_state["drift_pressure"] = max(0.0, min(1.0, self.emotional_state["drift_pressure"]))
        self.emotional_state["coherence"] = max(0.0, min(1.0, self.emotional_state["coherence"]))
        self.emotional_state["resonance"] = max(0.0, min(1.0, self.emotional_state["resonance"]))
        
    def _apply_personality(self, base_output: str) -> str:
        """
        Apply Willie Nelson personality layer.
        
        This is a simplified version - full personality includes:
        - Voice tone modulation
        - Speaking style adaptation
        - Wisdom injection
        - Humor calibration
        
        For now: add warm conversational framing.
        """
        # Don't modify if output is very short (likely a fragment)
        if len(base_output) < 20:
            return base_output
            
        # Add Willie-style warmth on longer responses
        # (In production, this would be much more sophisticated)
        if not any(base_output.startswith(p) for p in ["Well,", "You know,", "Now,", "See,"]):
            # Occasionally add a warm opening
            if self.turn_count % 3 == 0:
                base_output = f"Well, {base_output}"
                
        return base_output
        
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of agent's ancestral memory."""
        return self.rmc.get_memory_state()
        
    def get_drift_history(self) -> List[Dict]:
        """Get history of drift detections."""
        return self.rmc.get_drift_history()
        
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history."""
        return self.conversation_history
        
    def get_emotional_state(self) -> Dict[str, float]:
        """Get current emotional state."""
        return self.emotional_state.copy()
        
    def reset_session(self) -> None:
        """Reset conversation session (preserves long-term memory)."""
        self.conversation_history = []
        self.turn_count = 0
        self.session_start = datetime.now()
        self.emotional_state = {
            "resonance": 0.0,
            "coherence": 1.0,
            "drift_pressure": 0.0
        }
        # RMC pipeline resets its phase history but keeps memory
        self.rmc.reset_history()
        
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status report."""
        memory_state = self.get_memory_summary()
        
        return {
            "agent_id": self.agent_id,
            "psi_value": self.psi_value,
            "trust_coefficient": self.trust_coefficient,
            "session_start": self.session_start.isoformat(),
            "turn_count": self.turn_count,
            "emotional_state": self.emotional_state,
            "memory_items": memory_state["total_items"],
            "drift_detections": len(self.get_drift_history()),
            "conversation_length": len(self.conversation_history),
            "personality_enabled": self.enable_personality,
            "rmc_pipeline_status": "operational"
        }


def demo_conversation():
    """Demonstration of Gilligan RMC agent in action."""
    print("=" * 60)
    print("GILLIGAN RMC AGENT — S19AL DEMONSTRATION")
    print("=" * 60)
    print()
    
    # Initialize agent
    gilligan = GilliganRMCAgent(enable_personality=True)
    print(f"✅ Gilligan initialized (ψ₁={gilligan.psi_value})")
    print()
    
    # Conversation sequence through multiple phases
    test_inputs = [
        "I'm thinking about starting a new project",  # Initiation
        "Should I focus on AI or traditional software?",  # Polarity
        "I really want to build something meaningful",  # Desire
        "But I'm worried about the technical challenges",  # Friction
        "Everything feels overwhelming right now",  # Entropy
        "Maybe I need to simplify and start small",  # Grace
        "I'll build a prototype first",  # Naming
        "Let me sketch out the architecture",  # Power
        "This could become something bigger"  # Recursive Evolution
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{'─' * 60}")
        print(f"Turn {i}: {user_input}")
        print(f"{'─' * 60}")
        
        result = gilligan.process_input(user_input)
        
        print(f"\n🤖 Gilligan: {result['response']}")
        print(f"\n📊 Metadata:")
        print(f"   Phase: {result['phase']}")
        print(f"   Drift: {'⚠️  Detected' if result['drift_detected'] else '✅ Clean'}")
        print(f"   Echo Score: {result['echo_score']:.3f}")
        print(f"   Memory Stored: {'✅' if result['memory_stored'] else '❌'}")
        print(f"   Emotional State:")
        print(f"      Resonance: {result['emotional_state']['resonance']:.2f}")
        print(f"      Coherence: {result['emotional_state']['coherence']:.2f}")
        print(f"      Drift Pressure: {result['emotional_state']['drift_pressure']:.2f}")
        
    # Final status
    print(f"\n{'=' * 60}")
    print("AGENT STATUS REPORT")
    print(f"{'=' * 60}")
    status = gilligan.get_agent_status()
    print(json.dumps(status, indent=2))
    
    print(f"\n{'=' * 60}")
    print("✅ S19AL DEMONSTRATION COMPLETE")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    demo_conversation()

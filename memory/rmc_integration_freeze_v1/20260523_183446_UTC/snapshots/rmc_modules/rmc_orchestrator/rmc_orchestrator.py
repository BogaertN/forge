"""
RMC Pipeline Orchestrator — S19AK
"""
import sys
import os
from typing import Dict, List
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from phase_parser.phase_state_parser import PhaseStateParser
from ancestral_memory.ancestral_memory import AncestralMemory
from drift_detection.drift_detector import DriftArbitrator
from manifest_compiler.manifest_compiler import ManifestCompiler
from output_renderer.output_renderer import OutputRenderer
from echo_validator.echo_validator import EchoGate

PHASE_MAP = {
    "initiation_pulse": 1, "polarity": 2, "desire": 3,
    "friction": 4, "entropy": 5, "grace": 6,
    "naming": 7, "power": 8, "recursive_evolution": 9
}

class RMCResult:
    def __init__(self, input_text, phase, memory_records, drift_report,
                 manifest, render_result, echo_accepted, echo_score, output, metadata):
        self.input_text = input_text
        self.phase = phase
        self.memory_records = memory_records
        self.drift_report = drift_report
        self.manifest = manifest
        self.render_result = render_result
        self.echo_accepted = echo_accepted
        self.echo_score = echo_score
        self.output = output
        self.metadata = metadata
        self.timestamp = datetime.now(timezone.utc).isoformat()
        
    def to_dict(self) -> Dict:
        return {
            "input_text": self.input_text,
            "phase": self.phase,
            "drift_detected": self.drift_report.get("drift_detected", False),
            "echo_accepted": self.echo_accepted,
            "echo_score": self.echo_score,
            "output": self.output,
            "memory_stored": len(self.memory_records) > 0,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

class RMCOrchestrator:
    def __init__(self, agent_id: str = "rmc_agent", enable_memory: bool = True,
                 enable_drift: bool = True, enable_echo: bool = True):
        self.agent_id = agent_id
        self.enable_memory = enable_memory
        self.enable_drift = enable_drift
        self.enable_echo = enable_echo
        
        self.phase_parser = PhaseStateParser()
        self.memory = AncestralMemory()
        self.drift_detector = DriftArbitrator()
        self.manifest_compiler = ManifestCompiler()
        self.output_renderer = OutputRenderer()
        self.echo_gate = EchoGate()
        
        self.phase_history: List[str] = []
        self.phase_history_ints: List[int] = []
        self.processing_count = 0
        self.drift_events: List[Dict] = []
        
    def process(self, input_text: str, modality: str = "language") -> Dict:
        self.processing_count += 1
        
        phase_result = self.phase_parser.parse(input_text)
        phase_name = phase_result["phase"]
        self.phase_history.append(phase_name)
        phase_num = PHASE_MAP.get(phase_name, 1)
        self.phase_history_ints.append(phase_num)
        
        memory_records = []
        memory_records_dicts = []
        if self.enable_memory:
            memory_record = self.memory.store(
                content=input_text,
                phase=phase_num,
                source="user_input"
            )
            memory_records.append(memory_record)
            memory_records_dicts = [
                {
                    "id": memory_record.id,
                    "content": memory_record.content,
                    "phase": memory_record.phase,
                    "timestamp": memory_record.timestamp
                }
            ]
            context = self.memory.retrieve(query=input_text, limit=3)
        else:
            context = []
            
        drift_report = {"drift_detected": False}
        if self.enable_drift:
            drift_report = self.drift_detector.evaluate(
                text=input_text,
                current_phase=phase_num,
                phase_history=self.phase_history_ints
            )
            if drift_report.get("drift_detected"):
                self.drift_events.append({
                    "input": input_text,
                    "phase": phase_name,
                    "report": drift_report,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
        # Fixed: compile() returns Manifest directly, not dict
        manifest = self.manifest_compiler.compile(
            input_text=input_text,
            phase_state=phase_result,
            memory_records=memory_records_dicts,
            drift_report=drift_report,
            phase_history=self.phase_history_ints
        )
        
        render_result = self.output_renderer.render(
            manifest=manifest.to_dict(),
            modality=modality
        )
        output = render_result.content
        
        echo_accepted = True
        echo_score = 1.0
        if self.enable_echo:
            echo_accepted, echo_score, note = self.echo_gate.validate(
                manifest=manifest.to_dict(),
                rendered_output=output,
                modality=modality
            )
                
        result = RMCResult(
            input_text=input_text,
            phase=phase_name,
            memory_records=memory_records,
            drift_report=drift_report,
            manifest=manifest,
            render_result=render_result,
            echo_accepted=echo_accepted,
            echo_score=echo_score,
            output=output,
            metadata={
                "agent_id": self.agent_id,
                "processing_count": self.processing_count,
                "pipeline_enabled": {
                    "memory": self.enable_memory,
                    "drift": self.enable_drift,
                    "echo": self.enable_echo
                }
            }
        )
        
        return result.to_dict()
        
    def get_memory_state(self) -> Dict:
        mem_summary = self.memory.summary()
        if "total_items" not in mem_summary:
            mem_summary["total_items"] = sum(mem_summary.get("by_phase", {}).values())
        return mem_summary
        
    def get_drift_history(self) -> List[Dict]:
        return self.drift_events.copy()
        
    def get_phase_history(self) -> List[str]:
        return self.phase_history.copy()
        
    def reset_history(self) -> None:
        self.phase_history = []
        self.phase_history_ints = []
        self.processing_count = 0
        self.drift_events = []

if __name__ == "__main__":
    print("RMC PIPELINE — S19AK")
    rmc = RMCOrchestrator()
    for text in ["Starting", "Python", "AI"]:
        r = rmc.process(text)
        print(f"{text} → {r['phase']}")

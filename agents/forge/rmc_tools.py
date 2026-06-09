"""
Forge RMC Read-Only Tool Wrappers — Patch 211

This module exposes preview-only helpers around the AI.Web RMC runtime wrappers.
It is intentionally NOT registered into Forge's live tool dispatcher in Patch 211.

Boundary rules:
- No writes to RMC memory.
- No writes to Forge memory.
- No Identity Vault access.
- No Gilligan wiring.
- No tool registry mutation.

The functions here are designed to be imported and verified first. A later patch
may register selected functions into Forge's tool system after this wrapper passes
inspection and smoke testing on Nic's machine.
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

RMC_READ_ONLY = True
WRAPPER_VERSION = "patch211_read_only_v1"


class RMCReadOnlyError(RuntimeError):
    """Raised when a preview-only RMC wrapper cannot complete safely."""


def _home() -> Path:
    return Path.home()


def _runtime_wrappers_root() -> Path:
    return _home() / "aiweb" / "runtime_wrappers"


def _ensure_runtime_import_path() -> Path:
    root = _runtime_wrappers_root()
    if not root.exists():
        raise RMCReadOnlyError(f"RMC runtime wrappers root not found: {root}")
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root


def _safe_error(function_name: str, exc: BaseException) -> Dict[str, Any]:
    return {
        "ok": False,
        "function": function_name,
        "read_only": RMC_READ_ONLY,
        "error_type": type(exc).__name__,
        "error": str(exc),
        "traceback_tail": traceback.format_exc(limit=3).strip().splitlines()[-8:],
    }


def _to_plain(obj: Any) -> Any:
    """Convert dataclass/object/dict/list outputs into JSON-safe structures."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_to_plain(v) for v in obj]
    if hasattr(obj, "to_dict"):
        return _to_plain(obj.to_dict())
    if hasattr(obj, "__dict__"):
        return {str(k): _to_plain(v) for k, v in vars(obj).items() if not k.startswith("_")}
    return str(obj)


def _normalize_echo_result(result: Any) -> Dict[str, Any]:
    if isinstance(result, tuple):
        accepted = bool(result[0]) if len(result) > 0 else False
        score = float(result[1]) if len(result) > 1 else 0.0
        note = str(result[2]) if len(result) > 2 else ""
        return {"accepted": accepted, "score": score, "note": note}
    plain = _to_plain(result)
    if isinstance(plain, dict):
        return plain
    return {"accepted": bool(result), "score": 1.0 if result else 0.0, "note": str(result)}


def rmc_phase_parse_preview(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Parse supplied text into a phase-state preview without writing memory.

    Returns a JSON-safe dict that includes phase number/name, confidence, cues,
    routing, warnings, and the read-only wrapper metadata.
    """
    try:
        _ensure_runtime_import_path()
        from phase_parser.phase_state_parser import PhaseStateParser  # type: ignore

        parser = PhaseStateParser()
        result = parser.parse(text or "", context=context or {})
        return {
            "ok": True,
            "function": "rmc_phase_parse_preview",
            "read_only": RMC_READ_ONLY,
            "wrapper_version": WRAPPER_VERSION,
            "result": _to_plain(result),
        }
    except BaseException as exc:
        return _safe_error("rmc_phase_parse_preview", exc)


def rmc_drift_check_preview(
    text: str,
    current_phase: Optional[int] = None,
    phase_history: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Check supplied text/phase context for drift risk without applying correction
    or writing memory.
    """
    try:
        _ensure_runtime_import_path()
        from drift_detection.drift_detector import DriftArbitrator  # type: ignore
        from phase_parser.phase_state_parser import PhaseStateParser  # type: ignore

        if current_phase is None:
            parsed = PhaseStateParser().parse(text or "")
            current_phase = int(parsed.get("phase_number") or parsed.get("phase_id") or 1)

        detector = DriftArbitrator()
        result = detector.evaluate(
            text=text or "",
            current_phase=int(current_phase),
            phase_history=list(phase_history or []),
        )
        return {
            "ok": True,
            "function": "rmc_drift_check_preview",
            "read_only": RMC_READ_ONLY,
            "wrapper_version": WRAPPER_VERSION,
            "result": _to_plain(result),
        }
    except BaseException as exc:
        return _safe_error("rmc_drift_check_preview", exc)


def rmc_echo_validate_preview(
    rendered_output: str,
    manifest: Dict[str, Any],
    modality: str = "language",
) -> Dict[str, Any]:
    """
    Compare a rendered output against a manifest-like object without writing memory.
    """
    try:
        _ensure_runtime_import_path()
        from echo_validator.echo_validator import EchoGate  # type: ignore

        gate = EchoGate()
        result = gate.validate(
            manifest=dict(manifest or {}),
            rendered_output=rendered_output or "",
            modality=modality or "language",
        )
        return {
            "ok": True,
            "function": "rmc_echo_validate_preview",
            "read_only": RMC_READ_ONLY,
            "wrapper_version": WRAPPER_VERSION,
            "result": _normalize_echo_result(result),
        }
    except BaseException as exc:
        return _safe_error("rmc_echo_validate_preview", exc)


def rmc_pipeline_preview(
    input_text: str,
    modality: str = "language",
) -> Dict[str, Any]:
    """
    Run the full RMC pipeline as a preview without persistent memory writes.

    This uses RMCOrchestrator with enable_memory=False and store_to_memory=False,
    so it does not store the input in AncestralMemory. It is intended only for
    import and behavior verification before Forge live tool registration.
    """
    try:
        _ensure_runtime_import_path()
        from rmc_orchestrator.rmc_orchestrator import RMCOrchestrator  # type: ignore

        orchestrator = RMCOrchestrator(
            agent_id="forge_rmc_preview",
            modality=modality or "language",
            enable_memory=False,
            enable_drift=True,
            enable_echo=True,
        )
        result = orchestrator.process(
            input_text=input_text or "",
            modality=modality or "language",
            store_to_memory=False,
        )
        return {
            "ok": True,
            "function": "rmc_pipeline_preview",
            "read_only": RMC_READ_ONLY,
            "wrapper_version": WRAPPER_VERSION,
            "result": _to_plain(result),
        }
    except BaseException as exc:
        return _safe_error("rmc_pipeline_preview", exc)


RMC_PREVIEW_FUNCTIONS = {
    "rmc_phase_parse_preview": rmc_phase_parse_preview,
    "rmc_drift_check_preview": rmc_drift_check_preview,
    "rmc_echo_validate_preview": rmc_echo_validate_preview,
    "rmc_pipeline_preview": rmc_pipeline_preview,
}


if __name__ == "__main__":
    sample_manifest = {
        "id": "patch211-smoke",
        "phase": 6,
        "phase_name": "Grace",
        "conclusion": "Correct the loop before projection.",
        "confidence": 0.9,
        "novelty": 0.1,
        "drift_verdict": "ALLOW",
        "projection_status": "READY",
    }
    smoke = {
        "phase": rmc_phase_parse_preview("We need to verify this before wiring Gilligan."),
        "drift": rmc_drift_check_preview("This is drifting and trying to project now.", current_phase=5, phase_history=[1, 4, 5]),
        "echo": rmc_echo_validate_preview("Correct the loop before projection.", sample_manifest),
        "pipeline": rmc_pipeline_preview("Verify a read-only RMC preview trace."),
    }
    print(json.dumps(smoke, indent=2, sort_keys=True))

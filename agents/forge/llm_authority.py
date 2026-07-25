"""Deterministic removal boundary for legacy Forge LLM authority.

Forge may keep historical read-only records about former model lanes, but no
Forge command, provider function, or compatibility object may invoke a model,
select a model-produced route, dispatch a model-selected tool, or progress a
model-produced artifact.  EchoForge is the only explicit model-enabled surface
and its output remains advisory.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import re
from typing import Callable


FORGE_LLM_AUTHORITY_REMOVED = (
    "FORGE_LLM_AUTHORITY_REMOVED_USE_EXPLICIT_ECHOFORGE"
)
ECHOFORGE_ADVISORY_COMMAND = (
    "echoforge-advisory <role> :: <prompt>"
)

LEGACY_FORGE_LLM_COMMANDS = frozenset(
    {
        "llm-engine-review-model-test",
        "llm-engine-review-draft",
        "llm-engine-review-batch-next",
        "llm-engine-review-batch-run",
        "llm-live-draft",
        "generic-repair-llm",
        "generic-repair-candidate-build",
        "generic-repair-candidate-verify",
        "generic-repair-review-llm",
        "generic-repair-review-verify",
        "generic-repair-sandbox-plan",
        "generic-repair-sandbox-run",
        "generic-sandbox-dependency-plan",
        "generic-sandbox-dependency-run",
        "generic-revision-llm",
        "generic-revision-candidate-build",
        "generic-revision-candidate-verify",
        "generic-revision-sandbox-plan",
        "generic-revision-sandbox-run",
        "generic-revision-loop-llm",
        "generic-revision-loop-candidate",
        "forge-command-implement",
        "forge-command-implement-review",
        "forge-command-implement-write",
        "forge-command-implement-install",
        "forge-tool-wrap",
        "forge-tool-wrap-install",
        "forge-self-suggest",
    }
)

_SAFE_LABEL = re.compile(r"[^a-zA-Z0-9_.:/-]+")


def _safe_label(value: object, *, default: str, limit: int = 96) -> str:
    text = str(value or "").strip()
    text = _SAFE_LABEL.sub("_", text)
    return (text[:limit] or default)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def command_token(raw_command: object) -> str:
    """Return only the first normalized token; arguments are never retained."""
    text = str(raw_command or "").strip()
    if not text:
        return "unknown"
    return _safe_label(text.split(maxsplit=1)[0].lower(), default="unknown")


def is_legacy_forge_llm_command(raw_command: object) -> bool:
    return command_token(raw_command) in LEGACY_FORGE_LLM_COMMANDS


@dataclass(frozen=True, slots=True)
class ForgeLLMRefusalReceipt:
    schema: str
    code: str
    command: str
    surface: str
    session_id: str
    timestamp_utc: str
    advisory_command: str
    forge_llm_authority: bool = False
    model_called: bool = False
    tool_dispatched: bool = False
    protected_memory_written: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ForgeLLMAuthorityRefusal(RuntimeError):
    """Fail-closed exception used before any model or model-derived action."""

    def __init__(self, receipt: ForgeLLMRefusalReceipt):
        self.receipt = receipt
        super().__init__(
            f"{receipt.code}: {receipt.command} is not a Forge authority lane; "
            f"use {receipt.advisory_command}"
        )


def build_refusal_receipt(
    raw_command: object,
    *,
    surface: object,
    session_id: object = "",
    timestamp_factory: Callable[[], str] = utc_now,
) -> ForgeLLMRefusalReceipt:
    return ForgeLLMRefusalReceipt(
        schema="aiweb.forge-llm-refusal.v1",
        code=FORGE_LLM_AUTHORITY_REMOVED,
        command=command_token(raw_command),
        surface=_safe_label(surface, default="unknown_surface"),
        session_id=_safe_label(session_id, default="no_session"),
        timestamp_utc=timestamp_factory(),
        advisory_command=ECHOFORGE_ADVISORY_COMMAND,
    )


def raise_forge_llm_authority_removed(
    raw_command: object,
    *,
    surface: object,
    session_id: object = "",
) -> None:
    """Raise the immutable refusal before any provider or progression work."""
    raise ForgeLLMAuthorityRefusal(
        build_refusal_receipt(
            raw_command,
            surface=surface,
            session_id=session_id,
        )
    )


def audit_refusal(receipt: ForgeLLMRefusalReceipt) -> None:
    """Write privacy-safe refusal metadata without prompt or model content."""
    from .memory import write_audit_entry

    write_audit_entry(
        receipt.session_id,
        "FORGE_LLM_AUTHORITY_REFUSED",
        "-",
        receipt.command,
        f"{receipt.code}|surface={receipt.surface}",
    )


def format_refusal(receipt: ForgeLLMRefusalReceipt) -> str:
    return "\n".join(
        (
            "[forge] REFUSED",
            f"  Code    : {receipt.code}",
            f"  Command : {receipt.command}",
            f"  Surface : {receipt.surface}",
            "  Reason  : Forge has no LLM, model-routing, or model-tool authority.",
            f"  Advisory: {receipt.advisory_command}",
        )
    )

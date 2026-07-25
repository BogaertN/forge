"""Explicit EchoForge deliberation runtime with zero Forge authority."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Callable, Protocol

from .contracts import (
    AdvisoryRequest,
    AdvisoryResponse,
    EchoForgeAdvisoryError,
    ProviderResult,
)
from .provider import OllamaAdvisoryProvider, validate_provider_endpoint


_COMMON_BOUNDARY = (
    "You are operating only inside EchoForge as an advisory deliberation role. "
    "You may analyze, challenge, explain, or propose possibilities. You have no "
    "Forge tools and no authority to select meaning, route a command, grant "
    "permission, execute an action, apply or approve a patch, write protected "
    "memory, or claim proof. Do not emit tool calls. Clearly label conclusions "
    "as advisory."
)

ROLE_INSTRUCTIONS = {
    "debate": "Examine the strongest competing positions and their tradeoffs.",
    "reflection": "Reflect on assumptions, implications, and unresolved tensions.",
    "journal": "Produce a concise deliberative journal entry without granting authority.",
    "clarifier": "Clarify terms, ambiguities, missing evidence, and decision boundaries.",
    "proponent": "Present the strongest advisory case in favor of the proposal.",
    "opponent": "Present the strongest advisory case against the proposal.",
    "decider": "Recommend a decision and rationale, explicitly as non-binding advice.",
    "auditor": "Audit reasoning, evidence gaps, risks, and unsupported claims.",
    "specialist": "Analyze the request from the relevant technical specialty.",
    "discussion": "Conduct a balanced exploratory discussion of the request.",
}


class AdvisoryProvider(Protocol):
    def call(
        self,
        request: AdvisoryRequest,
        *,
        system_instruction: str,
    ) -> ProviderResult:
        ...


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_advisory(
    role: object,
    prompt: object,
    *,
    provider: AdvisoryProvider | None = None,
    timestamp_factory: Callable[[], str] = _utc_now,
) -> AdvisoryResponse:
    """Run one explicit advisory request and return a non-authoritative envelope."""
    request = AdvisoryRequest.create(role, prompt)
    role_instruction = ROLE_INSTRUCTIONS.get(request.role)
    if not role_instruction:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_ROLE_CONFIGURATION_MISSING",
            "role instruction is unavailable",
        )
    active_provider = provider or OllamaAdvisoryProvider()
    result = active_provider.call(
        request,
        system_instruction=f"{_COMMON_BOUNDARY} {role_instruction}",
    )
    if not isinstance(result, ProviderResult):
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_INVALID_PROVIDER_RESULT",
            "provider did not return a ProviderResult",
        )
    if result.tool_calls_present:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_TOOL_CALLS_REJECTED",
            "provider returned tool calls; nothing was dispatched",
        )
    validate_provider_endpoint(result.endpoint)
    content = result.content.strip()
    return AdvisoryResponse(
        role=request.role,
        content=content,
        provider=result.provider,
        model=result.model,
        provider_endpoint=result.endpoint,
        output_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        created_at_utc=timestamp_factory(),
        response_bytes=result.response_bytes,
    )

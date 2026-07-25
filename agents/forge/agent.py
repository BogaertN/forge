"""Compatibility boundary for the removed model-enabled Forge agent.

The historical ``ForgeAgent`` import remains available so older callers fail
closed with a precise migration error instead of falling back to model or tool
behavior.  Model-enabled deliberation now belongs only to the explicitly
invoked, advisory-only ``echoforge_advisory`` package.
"""

from __future__ import annotations

from typing import Any

from .llm_authority import raise_forge_llm_authority_removed


class ForgeAgent:
    """Fail-closed compatibility object; it has no model or tool capability."""

    def __init__(
        self,
        session_id: str = "",
        session_memory: object | None = None,
        *_: Any,
        **__: Any,
    ):
        self.session_id = str(session_id or "")
        self.active_diag_session_id: str | None = None
        # Retain no protected-memory object. The argument is accepted only so
        # an old constructor call receives the governed refusal at use time.
        del session_memory

    def set_diag_session(self, diag_session_id: str | None) -> None:
        self.active_diag_session_id = (
            str(diag_session_id) if diag_session_id else None
        )

    def _refuse(self, surface: str) -> None:
        raise_forge_llm_authority_removed(
            "legacy-forge-agent",
            surface=surface,
            session_id=self.session_id,
        )

    def _call_ollama(self, *_: Any, **__: Any) -> dict[str, object]:
        self._refuse("forge_agent_provider")

    def _execute_tool_call(self, *_: Any, **__: Any) -> str:
        self._refuse("forge_agent_tool_dispatch")

    def ask(self, _question: str) -> str:
        self._refuse("forge_agent_ask")

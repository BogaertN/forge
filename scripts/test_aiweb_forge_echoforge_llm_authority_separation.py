#!/usr/bin/env python3
"""Behavior tests for the Forge / EchoForge LLM authority separation."""

from __future__ import annotations

from contextlib import redirect_stdout
import inspect
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
from urllib import error as urllib_error


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agents.forge.agent import ForgeAgent
from agents.forge.llm_authority import (
    FORGE_LLM_AUTHORITY_REMOVED,
    LEGACY_FORGE_LLM_COMMANDS,
    ForgeLLMAuthorityRefusal,
    build_refusal_receipt,
    command_token,
    is_legacy_forge_llm_command,
)
from echoforge_advisory.contracts import (
    AdvisoryRequest,
    AdvisoryResponse,
    EchoForgeAdvisoryError,
    ProviderResult,
)
from echoforge_advisory.provider import (
    MAX_RESPONSE_BYTES,
    OllamaAdvisoryProvider,
)
from echoforge_advisory.runtime import run_advisory

with mock.patch("pathlib.Path.mkdir", return_value=None):
    import main as forge_main


COMMAND_FUNCTIONS = {
    "llm-engine-review-model-test": "cmd_llm_engine_review_model_test",
    "llm-engine-review-draft": "cmd_llm_engine_review_draft",
    "llm-engine-review-batch-next": "cmd_llm_engine_review_batch_next",
    "llm-engine-review-batch-run": "cmd_llm_engine_review_batch_run",
    "llm-live-draft": "cmd_llm_live_draft",
    "generic-repair-llm": "cmd_generic_repair_llm",
    "generic-repair-candidate-build": "cmd_generic_repair_candidate_build",
    "generic-repair-candidate-verify": "cmd_generic_repair_candidate_verify",
    "generic-repair-review-llm": "cmd_generic_repair_review_llm",
    "generic-repair-review-verify": "cmd_generic_repair_review_verify",
    "generic-repair-sandbox-plan": "cmd_generic_repair_sandbox_plan",
    "generic-repair-sandbox-run": "cmd_generic_repair_sandbox_run",
    "generic-sandbox-dependency-plan": "cmd_generic_sandbox_dependency_plan",
    "generic-sandbox-dependency-run": "cmd_generic_sandbox_dependency_run",
    "generic-revision-llm": "cmd_generic_revision_llm",
    "generic-revision-candidate-build": "cmd_generic_revision_candidate_build",
    "generic-revision-candidate-verify": "cmd_generic_revision_candidate_verify",
    "generic-revision-sandbox-plan": "cmd_generic_revision_sandbox_plan",
    "generic-revision-sandbox-run": "cmd_generic_revision_sandbox_run",
    "generic-revision-loop-llm": "cmd_generic_revision_loop_llm",
    "generic-revision-loop-candidate": "cmd_generic_revision_loop_candidate",
    "forge-command-implement": "cmd_forge_command_implement",
    "forge-command-implement-review": "cmd_forge_command_implement_review",
    "forge-command-implement-write": "cmd_forge_command_implement_write",
    "forge-command-implement-install": "cmd_forge_command_implement_install",
    "forge-tool-wrap": "cmd_forge_tool_wrap",
    "forge-tool-wrap-install": "cmd_forge_tool_wrap_install",
    "forge-self-suggest": "cmd_forge_self_suggest",
}

PROVIDER_FUNCTIONS = {
    "_patch98_call_local_llm_for_review",
    "_p137_call_llm",
    "_p138_call_ollama",
    "_p139_call_ollama",
    "_p140_call_ollama_for_candidate_plan",
    "_p141_call_ollama",
    "_p142_call_ollama",
    "_p187_call_ollama",
}


class _FakeHTTPResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, limit: int) -> bytes:
        return self.payload[:limit]


class _FakeOpener:
    def __init__(self, payload: bytes | None = None, error: Exception | None = None):
        self.payload = payload
        self.error = error
        self.last_request = None
        self.last_timeout = None

    def open(self, request, timeout):
        self.last_request = request
        self.last_timeout = timeout
        if self.error is not None:
            raise self.error
        return _FakeHTTPResponse(self.payload or b"")


class _FakeProvider:
    def __init__(self, content: str = "Advisory analysis only."):
        self.content = content
        self.calls = []

    def call(self, request, *, system_instruction):
        self.calls.append((request, system_instruction))
        return ProviderResult(
            provider="ollama",
            model="qwen3:8b",
            endpoint="http://127.0.0.1:11434/api/chat",
            content=self.content,
            response_bytes=128,
        )


def _call_with_safe_arguments(function):
    args = []
    for parameter in inspect.signature(function).parameters.values():
        if parameter.name == "session_id":
            args.append("test-session")
        elif parameter.name in {"binder", "source_report"}:
            args.append({})
        else:
            args.append("test-value")
    return function(*args)


class ForgeAuthorityTests(unittest.TestCase):
    def test_registry_exactly_matches_governed_command_functions(self):
        self.assertEqual(set(COMMAND_FUNCTIONS), set(LEGACY_FORGE_LLM_COMMANDS))

    def test_command_parser_keeps_no_arguments(self):
        self.assertEqual(
            command_token("generic-repair-llm secret prompt content"),
            "generic-repair-llm",
        )
        self.assertTrue(
            is_legacy_forge_llm_command(
                "forge-tool-wrap package-name private-argument"
            )
        )

    def test_refusal_receipt_contains_no_prompt_or_output(self):
        receipt = build_refusal_receipt(
            "generic-repair-llm private prompt body",
            surface="unit_test",
            session_id="session-1",
            timestamp_factory=lambda: "2026-07-25T00:00:00Z",
        )
        serialized = json.dumps(receipt.to_dict(), sort_keys=True)
        self.assertEqual(receipt.code, FORGE_LLM_AUTHORITY_REMOVED)
        self.assertNotIn("private prompt body", serialized)
        self.assertFalse(receipt.model_called)
        self.assertFalse(receipt.tool_dispatched)
        self.assertFalse(receipt.protected_memory_written)

    def test_every_legacy_command_function_refuses_direct_call(self):
        for command, function_name in sorted(COMMAND_FUNCTIONS.items()):
            with self.subTest(command=command):
                function = getattr(forge_main, function_name)
                with self.assertRaises(ForgeLLMAuthorityRefusal) as raised:
                    _call_with_safe_arguments(function)
                self.assertEqual(raised.exception.receipt.command, command)
                self.assertFalse(raised.exception.receipt.model_called)

    def test_every_remaining_main_provider_refuses_direct_call(self):
        for function_name in sorted(PROVIDER_FUNCTIONS):
            with self.subTest(function=function_name):
                function = getattr(forge_main, function_name)
                with self.assertRaises(ForgeLLMAuthorityRefusal):
                    _call_with_safe_arguments(function)

    def test_legacy_agent_has_no_model_or_tool_behavior(self):
        agent = ForgeAgent("test-session", object())
        for call in (
            lambda: agent.ask("private question"),
            lambda: agent._call_ollama([]),
            lambda: agent._execute_tool_call("read_file", {}),
        ):
            with self.assertRaises(ForgeLLMAuthorityRefusal):
                call()

    def test_orchestrator_map_excludes_removed_model_commands(self):
        dispatch = forge_main._p199_build_dispatch()
        self.assertFalse(set(dispatch).intersection(LEGACY_FORGE_LLM_COMMANDS))

    def test_cli_refusal_is_visible_and_auditable(self):
        stream = io.StringIO()
        with mock.patch.object(forge_main, "audit_refusal") as audit:
            with redirect_stdout(stream):
                handled = forge_main._handle_forge_llm_refusal(
                    "forge-self-suggest private content",
                    surface="test_cli",
                    session_id="test-session",
                )
        self.assertTrue(handled)
        audit.assert_called_once()
        output = stream.getvalue()
        self.assertIn(FORGE_LLM_AUTHORITY_REMOVED, output)
        self.assertNotIn("private content", output)

    def test_deterministic_run_has_no_agent_parameter_or_model_followup(self):
        self.assertNotIn(
            "agent",
            inspect.signature(forge_main.cmd_run).parameters,
        )
        result = {
            "ok": True,
            "exit_code": 0,
            "line_count": 1,
            "output_sha256": "a" * 64,
            "diag_path": "/tmp/test-diagnostic.txt",
            "output": "deterministic output",
        }
        stream = io.StringIO()
        previous = forge_main._active_diag_session_id
        forge_main._active_diag_session_id = None
        try:
            with mock.patch(
                "agents.forge.runner.run_safe_command",
                return_value=result,
            ):
                with redirect_stdout(stream):
                    forge_main.cmd_run("nvidia-smi", "test-session")
        finally:
            forge_main._active_diag_session_id = previous
        output = stream.getvalue()
        self.assertIn("Deterministic run complete", output)
        self.assertIn("deterministic output", output)

    def test_status_does_not_probe_a_model(self):
        stream = io.StringIO()
        patches = (
            mock.patch.object(forge_main, "get_approved_paths", return_value=[]),
            mock.patch.object(forge_main, "get_session_paths", return_value=[]),
            mock.patch(
                "agents.forge.permissions.get_current_trust_level",
                return_value=0.0,
            ),
            mock.patch(
                "agents.forge.memory.load_user_profile",
                return_value={},
            ),
            mock.patch(
                "agents.forge.memory.load_project_profile",
                return_value={},
            ),
            mock.patch(
                "echoforge_advisory.provider.OllamaAdvisoryProvider.call",
                side_effect=AssertionError("model provider must not be probed"),
            ),
        )
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            with redirect_stdout(stream):
                forge_main.cmd_status()
        self.assertIn("Forge Status", stream.getvalue())


class EchoForgeContractTests(unittest.TestCase):
    def test_invalid_role_empty_and_oversized_prompts_refuse(self):
        with self.assertRaises(EchoForgeAdvisoryError):
            AdvisoryRequest.create("authority", "text")
        with self.assertRaises(EchoForgeAdvisoryError):
            AdvisoryRequest.create("clarifier", "")
        with self.assertRaises(EchoForgeAdvisoryError):
            AdvisoryRequest.create("clarifier", "x" * 16_001)

    def test_non_loopback_and_credentials_refuse(self):
        for endpoint in (
            "https://example.com/api/chat",
            "http://192.168.1.10:11434/api/chat",
            "http://user:password@127.0.0.1:11434/api/chat",
            "http://127.0.0.1:11434/api/chat?token=secret",
        ):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(EchoForgeAdvisoryError):
                    OllamaAdvisoryProvider(endpoint=endpoint)

    def test_provider_request_sends_no_tools(self):
        payload = json.dumps(
            {"message": {"role": "assistant", "content": "Advisory only."}}
        ).encode("utf-8")
        opener = _FakeOpener(payload)
        provider = OllamaAdvisoryProvider(timeout_seconds=1)
        request = AdvisoryRequest.create("clarifier", "Clarify this.")
        with mock.patch(
            "echoforge_advisory.provider.urllib_request.build_opener",
            return_value=opener,
        ):
            result = provider.call(
                request,
                system_instruction="Advisory only. No tools.",
            )
        sent = json.loads(opener.last_request.data.decode("utf-8"))
        self.assertNotIn("tools", sent)
        self.assertEqual(result.content, "Advisory only.")
        self.assertFalse(result.tool_calls_present)

    def test_provider_returned_tool_calls_are_rejected(self):
        payload = json.dumps(
            {
                "message": {
                    "role": "assistant",
                    "content": "Attempted action",
                    "tool_calls": [{"function": {"name": "run_shell"}}],
                }
            }
        ).encode("utf-8")
        opener = _FakeOpener(payload)
        provider = OllamaAdvisoryProvider(timeout_seconds=1)
        with mock.patch(
            "echoforge_advisory.provider.urllib_request.build_opener",
            return_value=opener,
        ):
            with self.assertRaises(EchoForgeAdvisoryError) as raised:
                provider.call(
                    AdvisoryRequest.create("auditor", "Audit."),
                    system_instruction="Advisory only.",
                )
        self.assertEqual(raised.exception.code, "ECHOFORGE_TOOL_CALLS_REJECTED")

    def test_malformed_empty_oversized_and_offline_responses_refuse(self):
        cases = [
            (b"{malformed", "ECHOFORGE_PROVIDER_MALFORMED_JSON"),
            (
                json.dumps({"message": {"content": ""}}).encode("utf-8"),
                "ECHOFORGE_EMPTY_PROVIDER_OUTPUT",
            ),
            (b"x" * (MAX_RESPONSE_BYTES + 1), "ECHOFORGE_PROVIDER_RESPONSE_TOO_LARGE"),
        ]
        provider = OllamaAdvisoryProvider(timeout_seconds=1)
        request = AdvisoryRequest.create("auditor", "Audit.")
        for payload, code in cases:
            with self.subTest(code=code):
                opener = _FakeOpener(payload)
                with mock.patch(
                    "echoforge_advisory.provider.urllib_request.build_opener",
                    return_value=opener,
                ):
                    with self.assertRaises(EchoForgeAdvisoryError) as raised:
                        provider.call(
                            request,
                            system_instruction="Advisory only.",
                        )
                self.assertEqual(raised.exception.code, code)

        offline = _FakeOpener(error=urllib_error.URLError("offline"))
        with mock.patch(
            "echoforge_advisory.provider.urllib_request.build_opener",
            return_value=offline,
        ):
            with self.assertRaises(EchoForgeAdvisoryError) as raised:
                provider.call(request, system_instruction="Advisory only.")
        self.assertEqual(raised.exception.code, "ECHOFORGE_PROVIDER_UNAVAILABLE")

    def test_advisory_envelope_is_non_authoritative_and_replay_stable(self):
        first = run_advisory(
            "clarifier",
            "Clarify this.",
            provider=_FakeProvider("Same advisory."),
            timestamp_factory=lambda: "2026-07-25T00:00:00Z",
        )
        second = run_advisory(
            "clarifier",
            "Clarify this.",
            provider=_FakeProvider("Same advisory."),
            timestamp_factory=lambda: "2026-07-25T00:01:00Z",
        )
        self.assertEqual(
            first.to_dict(include_timestamp=False),
            second.to_dict(include_timestamp=False),
        )
        self.assertTrue(first.advisory_only)
        self.assertFalse(first.forge_authority)
        self.assertFalse(first.tool_calls_allowed)
        self.assertFalse(first.forge_action_executed)
        self.assertFalse(first.protected_memory_written)

    def test_cli_echo_output_is_visibly_advisory_and_audits_no_content(self):
        response = AdvisoryResponse(
            role="clarifier",
            content="Private advisory content.",
            provider="ollama",
            model="qwen3:8b",
            provider_endpoint="http://127.0.0.1:11434/api/chat",
            output_sha256="b" * 64,
            created_at_utc="2026-07-25T00:00:00Z",
            response_bytes=100,
        )
        stream = io.StringIO()
        with mock.patch.object(
            forge_main,
            "run_echoforge_advisory",
            return_value=response,
        ):
            with mock.patch(
                "agents.forge.memory.write_audit_entry"
            ) as audit:
                with redirect_stdout(stream):
                    forge_main.cmd_echoforge_advisory(
                        "clarifier :: private prompt",
                        "test-session",
                    )
        output = stream.getvalue()
        self.assertIn("Advisory only     : true", output)
        self.assertIn("Forge authority   : false", output)
        audit_text = repr(audit.call_args)
        self.assertNotIn("private prompt", audit_text)
        self.assertNotIn("Private advisory content", audit_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)

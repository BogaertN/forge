"""Loopback-only Ollama provider for explicit EchoForge advisory requests."""

from __future__ import annotations

import json
import os
import socket
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from .contracts import (
    AdvisoryRequest,
    EchoForgeAdvisoryError,
    ProviderResult,
    validate_model_name,
)


DEFAULT_ENDPOINT = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen3:8b"
DEFAULT_TIMEOUT_SECONDS = 120.0
MAX_TIMEOUT_SECONDS = 180.0
MAX_RESPONSE_BYTES = 1_048_576
MAX_JSON_DEPTH = 24
_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})


class _RejectRedirects(urllib_request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_PROVIDER_REDIRECT_REJECTED",
            "provider redirects are not allowed",
        )


def validate_provider_endpoint(endpoint: object) -> str:
    if not isinstance(endpoint, str):
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_INVALID_PROVIDER_ENDPOINT",
            "provider endpoint must be a string",
        )
    value = endpoint.strip()
    parsed = urllib_parse.urlsplit(value)
    if parsed.scheme != "http":
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_NON_LOOPBACK_PROVIDER_REJECTED",
            "provider endpoint must use loopback HTTP",
        )
    if parsed.username or parsed.password:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_PROVIDER_CREDENTIALS_REJECTED",
            "provider credentials are not allowed",
        )
    if (parsed.hostname or "").lower() not in _LOOPBACK_HOSTS:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_NON_LOOPBACK_PROVIDER_REJECTED",
            "provider endpoint is not loopback",
        )
    try:
        port = parsed.port
    except ValueError as exc:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_INVALID_PROVIDER_ENDPOINT",
            "provider port is invalid",
        ) from exc
    if port is not None and not (1 <= port <= 65535):
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_INVALID_PROVIDER_ENDPOINT",
            "provider port is outside the valid range",
        )
    if parsed.path != "/api/chat" or parsed.query or parsed.fragment:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_INVALID_PROVIDER_ENDPOINT",
            "provider endpoint must target /api/chat without query or fragment",
        )
    return value


def _json_depth(value: Any, depth: int = 0) -> int:
    if depth > MAX_JSON_DEPTH:
        return depth
    if isinstance(value, dict):
        return max(
            [_json_depth(item, depth + 1) for item in value.values()]
            or [depth]
        )
    if isinstance(value, list):
        return max(
            [_json_depth(item, depth + 1) for item in value]
            or [depth]
        )
    return depth


def _contains_tool_calls(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "tool_calls" and bool(item):
                return True
            if _contains_tool_calls(item):
                return True
    elif isinstance(value, list):
        return any(_contains_tool_calls(item) for item in value)
    return False


class OllamaAdvisoryProvider:
    """Bounded local provider. It exposes no tools and performs no writes."""

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        model: str | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.endpoint = validate_provider_endpoint(
            endpoint or os.environ.get("ECHOFORGE_OLLAMA_URL") or DEFAULT_ENDPOINT
        )
        self.model = validate_model_name(
            model or os.environ.get("ECHOFORGE_OLLAMA_MODEL") or DEFAULT_MODEL
        )
        try:
            timeout = float(timeout_seconds)
        except (TypeError, ValueError) as exc:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_TIMEOUT",
                "provider timeout must be numeric",
            ) from exc
        if not (0.1 <= timeout <= MAX_TIMEOUT_SECONDS):
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_TIMEOUT",
                f"provider timeout must be between 0.1 and {MAX_TIMEOUT_SECONDS} seconds",
            )
        self.timeout_seconds = timeout

    def call(
        self,
        request: AdvisoryRequest,
        *,
        system_instruction: str,
    ) -> ProviderResult:
        if not isinstance(request, AdvisoryRequest):
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_REQUEST",
                "provider requires an AdvisoryRequest",
            )
        if not isinstance(system_instruction, str) or not system_instruction.strip():
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_SYSTEM_INSTRUCTION",
                "role instruction must not be empty",
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction.strip()},
                {"role": "user", "content": request.prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 8192,
            },
        }
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        http_request = urllib_request.Request(
            self.endpoint,
            data=encoded,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        opener = urllib_request.build_opener(
            urllib_request.ProxyHandler({}),
            _RejectRedirects(),
        )

        try:
            with opener.open(
                http_request,
                timeout=self.timeout_seconds,
            ) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except EchoForgeAdvisoryError:
            raise
        except urllib_error.HTTPError as exc:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_PROVIDER_HTTP_ERROR",
                f"local provider returned HTTP {exc.code}",
                retriable=500 <= int(exc.code) < 600,
            ) from exc
        except urllib_error.URLError as exc:
            reason = getattr(exc, "reason", None)
            if isinstance(reason, (TimeoutError, socket.timeout)):
                code = "ECHOFORGE_PROVIDER_TIMEOUT"
                message = "local provider timed out"
            else:
                code = "ECHOFORGE_PROVIDER_UNAVAILABLE"
                message = "local provider is unavailable"
            raise EchoForgeAdvisoryError(code, message, retriable=True) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_PROVIDER_TIMEOUT",
                "local provider timed out",
                retriable=True,
            ) from exc
        except OSError as exc:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_PROVIDER_UNAVAILABLE",
                "local provider could not be reached",
                retriable=True,
            ) from exc

        if len(raw) > MAX_RESPONSE_BYTES:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_PROVIDER_RESPONSE_TOO_LARGE",
                f"provider response exceeds {MAX_RESPONSE_BYTES} bytes",
            )
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_PROVIDER_MALFORMED_JSON",
                "provider returned malformed JSON",
            ) from exc
        if not isinstance(decoded, dict) or _json_depth(decoded) > MAX_JSON_DEPTH:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_PROVIDER_INVALID_SHAPE",
                "provider response shape is invalid or too deeply nested",
            )
        if _contains_tool_calls(decoded):
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_TOOL_CALLS_REJECTED",
                "provider returned tool calls; nothing was dispatched",
            )
        message = decoded.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_EMPTY_PROVIDER_OUTPUT",
                "provider returned no advisory text",
            )

        return ProviderResult(
            provider="ollama",
            model=self.model,
            endpoint=self.endpoint,
            content=content.strip(),
            response_bytes=len(raw),
            tool_calls_present=False,
        )

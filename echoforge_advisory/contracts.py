"""Typed contracts for the explicit, advisory-only EchoForge model lane."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any


ALLOWED_ROLES = frozenset(
    {
        "debate",
        "reflection",
        "journal",
        "clarifier",
        "proponent",
        "opponent",
        "decider",
        "auditor",
        "specialist",
        "discussion",
    }
)
MAX_PROMPT_CHARACTERS = 16_000
MAX_PROMPT_BYTES = 64_000
MAX_MODEL_NAME_CHARACTERS = 128
_MODEL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class EchoForgeAdvisoryError(RuntimeError):
    """Structured, content-safe advisory failure."""

    def __init__(self, code: str, message: str, *, retriable: bool = False):
        self.code = str(code)
        self.safe_message = str(message)
        self.retriable = bool(retriable)
        super().__init__(f"{self.code}: {self.safe_message}")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "aiweb.echoforge-advisory-error.v1",
            "code": self.code,
            "message": self.safe_message,
            "retriable": self.retriable,
            "advisory_only": True,
            "forge_authority": False,
            "tool_calls_allowed": False,
        }


def validate_role(role: object) -> str:
    if not isinstance(role, str):
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_INVALID_ROLE_TYPE",
            "role must be a string",
        )
    normalized = role.strip().lower()
    if normalized not in ALLOWED_ROLES:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_ROLE_NOT_ALLOWED",
            "role is not in the advisory role registry",
        )
    return normalized


def validate_prompt(prompt: object) -> str:
    if not isinstance(prompt, str):
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_INVALID_PROMPT_TYPE",
            "prompt must be a string",
        )
    normalized = prompt.strip()
    if not normalized:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_EMPTY_PROMPT",
            "prompt must not be empty",
        )
    if len(normalized) > MAX_PROMPT_CHARACTERS:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_PROMPT_TOO_LARGE",
            f"prompt exceeds {MAX_PROMPT_CHARACTERS} characters",
        )
    if len(normalized.encode("utf-8")) > MAX_PROMPT_BYTES:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_PROMPT_TOO_LARGE",
            f"prompt exceeds {MAX_PROMPT_BYTES} UTF-8 bytes",
        )
    return normalized


def validate_model_name(model: object) -> str:
    if not isinstance(model, str) or not _MODEL_NAME.fullmatch(model.strip()):
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_INVALID_MODEL_NAME",
            "model name contains unsupported characters",
        )
    normalized = model.strip()
    if len(normalized) > MAX_MODEL_NAME_CHARACTERS:
        raise EchoForgeAdvisoryError(
            "ECHOFORGE_INVALID_MODEL_NAME",
            "model name is too long",
        )
    return normalized


@dataclass(frozen=True, slots=True)
class AdvisoryRequest:
    role: str
    prompt: str

    def __post_init__(self) -> None:
        if validate_role(self.role) != self.role:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_NONCANONICAL_ROLE",
                "role must use its canonical lowercase form",
            )
        if validate_prompt(self.prompt) != self.prompt:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_NONCANONICAL_PROMPT",
                "prompt must not contain surrounding whitespace",
            )

    @classmethod
    def create(cls, role: object, prompt: object) -> "AdvisoryRequest":
        return cls(role=validate_role(role), prompt=validate_prompt(prompt))


@dataclass(frozen=True, slots=True)
class ProviderResult:
    provider: str
    model: str
    endpoint: str
    content: str
    response_bytes: int
    tool_calls_present: bool = False

    def __post_init__(self) -> None:
        if self.provider != "ollama":
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_PROVIDER_NOT_ALLOWED",
                "only the local Ollama provider is allowed",
            )
        validate_model_name(self.model)
        if not isinstance(self.endpoint, str) or not self.endpoint.strip():
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_PROVIDER_RESULT",
                "provider endpoint is missing",
            )
        if not isinstance(self.content, str) or not self.content.strip():
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_EMPTY_PROVIDER_OUTPUT",
                "provider returned no advisory text",
            )
        if not isinstance(self.response_bytes, int) or self.response_bytes < 1:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_PROVIDER_RESULT",
                "provider response size is invalid",
            )
        if self.tool_calls_present:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_TOOL_CALLS_REJECTED",
                "provider returned tool calls; nothing was dispatched",
            )


@dataclass(frozen=True, slots=True)
class AdvisoryResponse:
    role: str
    content: str
    provider: str
    model: str
    provider_endpoint: str
    output_sha256: str
    created_at_utc: str
    response_bytes: int
    schema: str = "aiweb.echoforge-advisory-response.v1"
    advisory_only: bool = True
    forge_authority: bool = False
    tool_calls_allowed: bool = False
    tool_calls_present: bool = False
    forge_route_selected: bool = False
    forge_permission_granted: bool = False
    forge_action_executed: bool = False
    protected_memory_written: bool = False
    proof_claimed: bool = False

    def __post_init__(self) -> None:
        validate_role(self.role)
        validate_model_name(self.model)
        if self.schema != "aiweb.echoforge-advisory-response.v1":
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_RESPONSE_SCHEMA",
                "advisory response schema is invalid",
            )
        if self.provider != "ollama":
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_PROVIDER_NOT_ALLOWED",
                "only the local Ollama provider is allowed",
            )
        if not isinstance(self.provider_endpoint, str) or not self.provider_endpoint:
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_PROVIDER_RESULT",
                "provider endpoint is missing",
            )
        if not isinstance(self.output_sha256, str) or not _SHA256.fullmatch(
            self.output_sha256
        ):
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_OUTPUT_HASH",
                "advisory output SHA-256 is invalid",
            )
        if not isinstance(self.created_at_utc, str) or not self.created_at_utc.endswith("Z"):
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_TIMESTAMP",
                "advisory timestamp must be UTC",
            )
        if not isinstance(self.response_bytes, int) or not (
            1 <= self.response_bytes <= 1_048_576
        ):
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_INVALID_PROVIDER_RESULT",
                "provider response size is invalid",
            )
        if not isinstance(self.content, str) or not self.content.strip():
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_EMPTY_ADVISORY",
                "advisory response must contain text",
            )
        if (
            not self.advisory_only
            or self.forge_authority
            or self.tool_calls_allowed
            or self.tool_calls_present
            or self.forge_route_selected
            or self.forge_permission_granted
            or self.forge_action_executed
            or self.protected_memory_written
            or self.proof_claimed
        ):
            raise EchoForgeAdvisoryError(
                "ECHOFORGE_AUTHORITY_CONTRACT_VIOLATION",
                "advisory response attempted to claim Forge authority",
            )

    def to_dict(self, *, include_timestamp: bool = True) -> dict[str, Any]:
        payload = asdict(self)
        if not include_timestamp:
            payload.pop("created_at_utc", None)
        return payload

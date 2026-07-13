"""Closed import policy for the isolated bootstrap package."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .schema import (
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    issue,
    require_false,
    stable_record_id,
)

ALLOWED_RUNTIME_IMPORTS = (
    "__future__",
    "dataclasses",
    "typing",
    "hashlib",
    "json",
)

PROHIBITED_IMPORT_PREFIXES = (
    "main",
    "agents.forge",
    "rmc_engine_v1",
    "forge.rmc_engine_v1",
    "requests",
    "httpx",
    "urllib",
    "socket",
    "aiohttp",
    "grpc",
    "ollama",
    "qwen",
    "chromadb",
    "chroma",
    "langchain",
    "faiss",
    "transformers",
    "torch",
    "tensorflow",
    "sklearn",
)

PROHIBITED_AUTHORITY_TOKENS = (
    "llm",
    "large_language_model",
    "qwen",
    "ollama",
    "chroma",
    "vector",
    "embedding",
    "rag",
    "retrieval_augmented_generation",
    "learned_classifier",
    "neural_parser",
    "model_confidence",
    "opaque_fallback",
)


@dataclass(frozen=True, slots=True)
class ImportPolicyRecord:
    import_policy_id: str
    allowed_runtime_imports: tuple[str, ...]
    prohibited_import_prefixes: tuple[str, ...]
    prohibited_authority_tokens: tuple[str, ...]
    static_allowlist_required: bool
    dynamic_loading_allowed: bool
    plugin_discovery_allowed: bool
    environment_selected_backend: bool
    hidden_fallback_allowed: bool
    network_import_allowed: bool
    model_import_allowed: bool
    vector_import_allowed: bool
    retrieval_import_allowed: bool
    schema_version: str = SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("import_policy_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_import_policy", self.canonical_body())


def build_import_policy_record() -> ImportPolicyRecord:
    body = {
        "allowed_runtime_imports": ALLOWED_RUNTIME_IMPORTS,
        "prohibited_import_prefixes": PROHIBITED_IMPORT_PREFIXES,
        "prohibited_authority_tokens": PROHIBITED_AUTHORITY_TOKENS,
        "static_allowlist_required": True,
        "dynamic_loading_allowed": False,
        "plugin_discovery_allowed": False,
        "environment_selected_backend": False,
        "hidden_fallback_allowed": False,
        "network_import_allowed": False,
        "model_import_allowed": False,
        "vector_import_allowed": False,
        "retrieval_import_allowed": False,
        "schema_version": SCHEMA_VERSION,
    }
    return ImportPolicyRecord(
        import_policy_id=stable_record_id(
            "bootstrap_import_policy",
            body,
        ),
        **body,
    )


def validate_import_policy_record(
    record: ImportPolicyRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if record.schema_version != SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if tuple(record.allowed_runtime_imports) != ALLOWED_RUNTIME_IMPORTS:
        issues.append(
            issue(
                "allowed_runtime_imports",
                "runtime_import_allowlist_mismatch",
            )
        )
    if tuple(record.prohibited_import_prefixes) != PROHIBITED_IMPORT_PREFIXES:
        issues.append(
            issue(
                "prohibited_import_prefixes",
                "prohibited_import_prefix_mismatch",
            )
        )
    if tuple(record.prohibited_authority_tokens) != PROHIBITED_AUTHORITY_TOKENS:
        issues.append(
            issue(
                "prohibited_authority_tokens",
                "prohibited_authority_token_mismatch",
            )
        )
    if record.static_allowlist_required is not True:
        issues.append(issue("static_allowlist_required", "must_remain_true"))

    for field in (
        "dynamic_loading_allowed",
        "plugin_discovery_allowed",
        "environment_selected_backend",
        "hidden_fallback_allowed",
        "network_import_allowed",
        "model_import_allowed",
        "vector_import_allowed",
        "retrieval_import_allowed",
    ):
        require_false(
            field=field,
            value=getattr(record, field),
            issues=issues,
        )

    if record.import_policy_id != record.expected_id():
        issues.append(issue("import_policy_id", "stable_identifier_mismatch"))

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )

"""Optional LLM Renderer Boundary / L_t->R_t helper.

Patch 262J1R-Preflight-C16 adds a default-off LLM rendering helper for the
Output Renderer.  The deterministic renderer remains the default authority.
This module may call a local model endpoint only when the caller explicitly
sets the LLM renderer toggle and supplies an approved local HTTP endpoint.

Safety rules:
* default off
* local HTTP endpoint only
* no files, no shell, no Chroma, no DB, no Identity Vault, no memory writes
* LLM text is still constrained by sentence_plan and must pass Echo Validator
* deterministic fallback text is returned when the LLM renderer is skipped
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

ENGINE_VERSION = "rmc_llm_renderer_v1_patch262J1R_preflight_C16"
ENGINE_MODE = "optional_local_llm_renderer_boundary_default_off"

DEFAULT_TIMEOUT_SECONDS = 8.0
MAX_PROMPT_CHARS = 6000
MAX_RESPONSE_CHARS = 2600
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
TRUE_TOGGLE_VALUES = {"1", "true", "yes", "on", "enabled", "enable"}
FALSE_TOGGLE_VALUES = {"", "0", "false", "no", "off", "disabled", "disable", "none", "null"}


def _text(value: Any, limit: int = 1200) -> str:
    text = str(value or "").replace("\x00", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value or {}) if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, "", {}):
        return []
    return [value]


def normalize_llm_toggle(value: Any) -> bool:
    """Return True only for explicit affirmative toggle values."""
    if isinstance(value, bool):
        return value
    token = str(value or "").strip().lower()
    if token in TRUE_TOGGLE_VALUES:
        return True
    if token in FALSE_TOGGLE_VALUES:
        return False
    return False


def validate_model_endpoint(endpoint: Any) -> dict[str, Any]:
    """Approve only local HTTP endpoints.

    This prevents the renderer from becoming a general outbound network client
    or SSRF surface.  The first production target is a local model gateway such
    as a developer-controlled inference endpoint on localhost.
    """
    raw = _text(endpoint, 400)
    if not raw:
        return {
            "approved": False,
            "failure_code": "LLM_RENDERER_ENDPOINT_MISSING",
            "endpoint": None,
            "reason": "model_endpoint_required_when_llm_renderer_enabled",
        }
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme != "http":
        return {
            "approved": False,
            "failure_code": "LLM_RENDERER_ENDPOINT_SCHEME_REFUSED",
            "endpoint": raw,
            "reason": "only_plain_local_http_endpoints_are_allowed_at_C16",
        }
    host = (parsed.hostname or "").lower()
    if host not in LOCAL_HOSTS:
        return {
            "approved": False,
            "failure_code": "LLM_RENDERER_ENDPOINT_HOST_REFUSED",
            "endpoint": raw,
            "reason": "only_localhost_or_loopback_model_endpoints_are_allowed_at_C16",
        }
    if not parsed.path or parsed.path == "/":
        return {
            "approved": False,
            "failure_code": "LLM_RENDERER_ENDPOINT_PATH_REFUSED",
            "endpoint": raw,
            "reason": "model_endpoint_must_include_an_api_path",
        }
    return {
        "approved": True,
        "failure_code": None,
        "endpoint": raw,
        "scheme": parsed.scheme,
        "host": host,
        "port": parsed.port,
        "path": parsed.path,
        "reason": "approved_local_http_model_endpoint",
    }


def llm_renderer_boundary() -> dict[str, Any]:
    return {
        "engine_version": ENGINE_VERSION,
        "engine_mode": ENGINE_MODE,
        "engine_module_location": "forge/rmc_engine_v1/llm_renderer.py",
        "implements_rmc_stage": "Optional LLM Renderer Boundary for Output Renderer / R_t",
        "default_enabled": False,
        "toggle_required": True,
        "caller_must_supply_model_endpoint": True,
        "approved_endpoint_policy": "local_http_loopback_only_C16",
        "non_llm_renderer_remains_default": True,
        "sentence_plan_required": True,
        "echo_validation_required_after_llm_text": True,
        "llm_output_is_not_authority": True,
        "llm_may_not_create_manifest_meaning": True,
        "calls_llm_only_when_explicitly_enabled": True,
        "writes_files": False,
        "writes_rmc_memory": False,
        "writes_identity_vault": False,
        "queries_chroma": False,
        "reads_db_files": False,
        "executes_shell": False,
        "mutates_canonical_reference": False,
        "approved_output": False,
        "projection_allowed": False,
        "memory_write_allowed": False,
    }


def llm_renderer_schema_contract() -> dict[str, Any]:
    return {
        "llm_renderer_symbol": "R_t^LLM_optional",
        "formula": "R_t = ρ(μ_t, sentence_plan, mode) with optional LLM draft only iff toggle_on ∧ endpoint_approved ∧ text_mode",
        "default_path": "deterministic_template_renderer",
        "toggle_params": ["llm_renderer", "use_llm", "llm"],
        "endpoint_param": "model_endpoint",
        "model_param": "model",
        "required_sentence_plan_fields": [
            "core_claim",
            "required_qualifiers",
            "required_definitions",
            "forbidden_claims",
            "allowed_claim_scope",
            "audience",
            "mode",
        ],
        "required_attempt_fields": [
            "llm_renderer_requested",
            "llm_renderer_used",
            "endpoint_approved",
            "status",
            "failure_code",
            "sentence_plan_bound",
            "echo_validation_required",
        ],
        "safety": llm_renderer_boundary(),
    }


def _prompt_from_sentence_plan(mu: dict[str, Any], sentence_plan: dict[str, Any]) -> str:
    safe_mu = {
        "claim": _text(mu.get("claim"), 1400),
        "phase_path": _as_list(mu.get("phase_path")),
        "operator_path": _as_list(mu.get("operator_path")),
        "confidence": mu.get("confidence"),
        "novelty": mu.get("novelty"),
        "drift_status": _as_dict(mu.get("drift_status")),
        "projection_status": _as_dict(mu.get("projection_status")),
        "output_targets": _as_list(mu.get("output_targets")),
    }
    safe_plan = {
        "core_claim": _text(sentence_plan.get("core_claim"), 1400),
        "required_qualifiers": [_text(x, 240) for x in _as_list(sentence_plan.get("required_qualifiers"))],
        "required_definitions": [_text(x, 240) for x in _as_list(sentence_plan.get("required_definitions"))],
        "forbidden_claims": [_text(x, 240) for x in _as_list(sentence_plan.get("forbidden_claims"))],
        "allowed_claim_scope": _text(sentence_plan.get("allowed_claim_scope"), 240),
        "audience": _text(sentence_plan.get("audience"), 80),
        "mode": _text(sentence_plan.get("mode"), 80),
        "style": _text(sentence_plan.get("style"), 80),
    }
    prompt = (
        "You are an optional renderer inside AI.Web Forge RMC.\n"
        "You are NOT the authority. The manifest μ_t is authority.\n"
        "Render a concise text draft from the supplied sentence plan only.\n"
        "Do not add unsupported claims. Do not claim approval, projection, memory write, or final truth.\n"
        "Preserve phase path, confidence/novelty, drift status, and the Echo Validator qualifier.\n"
        "Return only the rendered text. No analysis, no markdown fence, no hidden reasoning.\n\n"
        f"SENTENCE_PLAN_JSON={json.dumps(safe_plan, ensure_ascii=False, sort_keys=True)}\n"
        f"MANIFEST_SUMMARY_JSON={json.dumps(safe_mu, ensure_ascii=False, sort_keys=True)}\n"
    )
    return prompt[:MAX_PROMPT_CHARS]


def _strip_reasoning(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"```[a-zA-Z0-9_-]*", "", text)
    text = text.replace("```", "")
    return _text(text, MAX_RESPONSE_CHARS)


def _extract_text_from_response(payload: Any) -> str:
    if isinstance(payload, str):
        return _strip_reasoning(payload)
    if not isinstance(payload, dict):
        return ""
    for key in ("response", "text", "content", "output"):
        if isinstance(payload.get(key), str) and payload.get(key).strip():
            return _strip_reasoning(payload.get(key, ""))
    message = payload.get("message")
    if isinstance(message, dict) and isinstance(message.get("content"), str):
        return _strip_reasoning(message.get("content", ""))
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            if isinstance(first.get("text"), str):
                return _strip_reasoning(first.get("text", ""))
            msg = first.get("message")
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return _strip_reasoning(msg.get("content", ""))
    return ""


def _call_local_model_endpoint(endpoint: str, model: str, prompt: str, timeout_seconds: float) -> dict[str, Any]:
    payload = {
        "model": model or "qwen3:8b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.8,
        },
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:  # nosec - endpoint is local-only validated before call
        body = response.read(1024 * 128).decode("utf-8", errors="replace")
    try:
        decoded: Any = json.loads(body)
    except json.JSONDecodeError:
        decoded = body
    return {
        "raw_response_kind": type(decoded).__name__,
        "rendered_text": _extract_text_from_response(decoded),
    }


def render_text_with_optional_llm(
    mu: dict[str, Any],
    sentence_plan: dict[str, Any],
    deterministic_text: str,
    llm_options: dict[str, Any] | None = None,
    llm_client: Callable[[dict[str, Any]], Any] | None = None,
) -> dict[str, Any]:
    """Return an LLM render attempt report.

    The caller decides whether to use the returned text.  This function never
    approves output and never writes anything.  Test code can pass llm_client to
    prove the path without network access.
    """
    options = _as_dict(llm_options)
    requested = normalize_llm_toggle(options.get("enabled"))
    base = {
        "engine_version": ENGINE_VERSION,
        "engine_mode": ENGINE_MODE,
        "llm_renderer_requested": requested,
        "llm_renderer_used": False,
        "endpoint_approved": False,
        "sentence_plan_bound": bool(sentence_plan),
        "echo_validation_required": True,
        "approved_output": False,
        "projection_allowed": False,
        "memory_write_allowed": False,
        "writes_files": False,
        "calls_llm": False,
    }
    if not requested:
        return {
            **base,
            "status": "SKIPPED",
            "failure_code": None,
            "reason": "llm_renderer_toggle_off_default_deterministic_renderer_used",
            "rendered_text": deterministic_text,
        }
    if _text(sentence_plan.get("mode"), 80) not in ("text", "formal_text", ""):
        return {
            **base,
            "status": "BLOCKED",
            "failure_code": "LLM_RENDERER_TEXT_MODE_ONLY",
            "reason": "optional_llm_renderer_only_renders_text_modes_at_C16",
            "rendered_text": deterministic_text,
        }
    endpoint_check = validate_model_endpoint(options.get("model_endpoint"))
    if not endpoint_check.get("approved"):
        return {
            **base,
            "status": "BLOCKED",
            "failure_code": endpoint_check.get("failure_code"),
            "reason": endpoint_check.get("reason"),
            "endpoint_check": endpoint_check,
            "rendered_text": deterministic_text,
        }
    prompt = _prompt_from_sentence_plan(mu, sentence_plan)
    model = _text(options.get("model") or "qwen3:8b", 120) or "qwen3:8b"
    timeout = options.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
    try:
        timeout_seconds = max(1.0, min(30.0, float(timeout)))
    except Exception:
        timeout_seconds = DEFAULT_TIMEOUT_SECONDS
    try:
        if llm_client is not None:
            raw = llm_client({"endpoint": endpoint_check.get("endpoint"), "model": model, "prompt": prompt, "timeout_seconds": timeout_seconds})
            rendered = _extract_text_from_response(raw)
            raw_kind = type(raw).__name__
        else:
            called = _call_local_model_endpoint(str(endpoint_check.get("endpoint")), model, prompt, timeout_seconds)
            rendered = called.get("rendered_text", "")
            raw_kind = str(called.get("raw_response_kind"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return {
            **base,
            "status": "BLOCKED",
            "failure_code": "LLM_RENDERER_CALL_FAILED",
            "reason": _text(exc, 300),
            "endpoint_check": endpoint_check,
            "calls_llm": True,
            "rendered_text": deterministic_text,
        }
    if not rendered:
        return {
            **base,
            "status": "BLOCKED",
            "failure_code": "LLM_RENDERER_EMPTY_RESPONSE",
            "reason": "model_endpoint_returned_no_renderable_text",
            "endpoint_check": endpoint_check,
            "calls_llm": True,
            "rendered_text": deterministic_text,
        }
    return {
        **base,
        "status": "OK",
        "failure_code": None,
        "reason": "llm_renderer_used_but_output_still_requires_sentence_guard_and_echo_validation",
        "endpoint_check": endpoint_check,
        "model": model,
        "prompt_bound_to_sentence_plan": True,
        "prompt_char_length": len(prompt),
        "raw_response_kind": raw_kind,
        "llm_renderer_used": True,
        "endpoint_approved": True,
        "calls_llm": True,
        "rendered_text": rendered,
    }

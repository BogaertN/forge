"""Bounded owner-only AF_UNIX request/response protocol."""
from __future__ import annotations

import json
import os
import socket
import uuid
from pathlib import Path
from typing import Any

from .authority import MAX_MESSAGE_BYTES, PROTOCOL_OPERATIONS, PROTOCOL_VERSION
from .canonical import canonical_json_bytes


class ProtocolFailure(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def request_id() -> str:
    return uuid.uuid4().hex


def encode_message(value: dict[str, Any]) -> bytes:
    data = canonical_json_bytes(value) + b"\n"
    if len(data) > MAX_MESSAGE_BYTES:
        raise ProtocolFailure("MESSAGE_TOO_LARGE", "encoded message exceeds the bounded protocol limit")
    return data


def decode_request(data: bytes) -> dict[str, Any]:
    if not data:
        raise ProtocolFailure("EMPTY_REQUEST", "request body is empty")
    if len(data) > MAX_MESSAGE_BYTES:
        raise ProtocolFailure("MESSAGE_TOO_LARGE", "request exceeds the bounded protocol limit")
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProtocolFailure("INVALID_JSON", f"request is not valid UTF-8 JSON: {type(error).__name__}") from error
    if not isinstance(value, dict):
        raise ProtocolFailure("REQUEST_NOT_OBJECT", "request must be a JSON object")
    allowed = {"protocol", "request_id", "operation", "control_token"}
    if set(value) - allowed:
        raise ProtocolFailure("UNKNOWN_REQUEST_FIELD", "request contains an unrecognized field")
    if value.get("protocol") != PROTOCOL_VERSION:
        raise ProtocolFailure("PROTOCOL_MISMATCH", "protocol version is not accepted")
    rid = value.get("request_id")
    if not isinstance(rid, str) or not rid or len(rid) > 128:
        raise ProtocolFailure("INVALID_REQUEST_ID", "request_id must be a bounded non-empty string")
    operation = value.get("operation")
    if operation not in PROTOCOL_OPERATIONS:
        raise ProtocolFailure("UNSUPPORTED_OPERATION", "operation is not admitted by Slice 48")
    token = value.get("control_token")
    if token is not None and (not isinstance(token, str) or len(token) > 256):
        raise ProtocolFailure("INVALID_CONTROL_TOKEN", "control_token must be null or a bounded string")
    return value


def response(request_id_value: str, *, ok: bool, code: str, lifecycle_state: str, data: dict[str, Any] | None = None, detail: str = "") -> dict[str, Any]:
    return {
        "protocol": PROTOCOL_VERSION,
        "request_id": request_id_value,
        "ok": bool(ok),
        "code": code,
        "lifecycle_state": lifecycle_state,
        "detail": detail,
        "data": data or {},
    }


def receive_bounded(connection: socket.socket) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = connection.recv(min(4096, MAX_MESSAGE_BYTES + 1 - total))
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > MAX_MESSAGE_BYTES:
            raise ProtocolFailure("MESSAGE_TOO_LARGE", "request exceeds the bounded protocol limit")
        if b"\n" in chunk:
            break
    return b"".join(chunks).split(b"\n", 1)[0]


def peer_uid(connection: socket.socket) -> int | None:
    option = getattr(socket, "SO_PEERCRED", None)
    if option is None:
        return None
    raw = connection.getsockopt(socket.SOL_SOCKET, option, 12)
    if len(raw) != 12:
        return None
    return int.from_bytes(raw[4:8], byteorder=os.sys.byteorder, signed=True)


def send_request(socket_path: Path, operation: str, *, control_token: str | None = None, timeout: float = 2.0) -> dict[str, Any]:
    payload = {
        "protocol": PROTOCOL_VERSION,
        "request_id": request_id(),
        "operation": operation,
        "control_token": control_token,
    }
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect(str(socket_path))
        client.sendall(encode_message(payload))
        data = receive_bounded(client)
    finally:
        client.close()
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProtocolFailure("INVALID_RESPONSE", f"service response is invalid: {type(error).__name__}") from error
    if not isinstance(value, dict):
        raise ProtocolFailure("INVALID_RESPONSE", "service response must be a JSON object")
    return value

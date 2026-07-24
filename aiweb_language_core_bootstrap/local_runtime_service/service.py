"""The isolated Slice 48 local-only service process."""
from __future__ import annotations

import hmac
import os
import signal
import socket
import threading
from pathlib import Path
from typing import Any

from .authority import (
    BUILD_BASE_HEAD,
    BUILD_BASE_SUBJECT,
    BUILD_BASE_TREE,
    BUILD_ID,
    PROTOCOL_VERSION,
    SCHEMA_VERSION,
    SERVICE_VERSION,
    TRANSPORT,
)
from .canonical import sha256_bytes
from .capabilities import build_capability_report
from .protocol import ProtocolFailure, decode_request, encode_message, peer_uid, receive_bounded, response
from .schema import ServiceIdentity
from .state import (
    StatePaths,
    atomic_write_json,
    cleanup_runtime_artifacts,
    current_process_record,
    exclusive_lock,
    make_paths,
    read_text,
)
from .validation import validate_service_identity


def _version_report() -> dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "service_version": SERVICE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "transport": TRANSPORT,
        "build_base_head": BUILD_BASE_HEAD,
        "build_base_tree": BUILD_BASE_TREE,
        "build_base_subject": BUILD_BASE_SUBJECT,
    }


def _identity(process, paths: StatePaths, repository_root: Path, entry_script: Path, token: str) -> ServiceIdentity:
    provisional = ServiceIdentity(
        schema_version=SCHEMA_VERSION,
        build_id=BUILD_ID,
        service_version=SERVICE_VERSION,
        protocol_version=PROTOCOL_VERSION,
        transport=TRANSPORT,
        socket_path=str(paths.socket),
        repository_root=str(repository_root.resolve()),
        state_root=str(paths.root),
        pid=process.pid,
        process_start_ticks=process.process_start_ticks,
        command_sha256=process.command_sha256,
        control_token_sha256=sha256_bytes(token.encode("utf-8")),
        build_base_head=BUILD_BASE_HEAD,
        build_base_tree=BUILD_BASE_TREE,
        build_base_subject=BUILD_BASE_SUBJECT,
    )
    value = ServiceIdentity(**{**provisional.to_dict(), "identity_id": provisional.expected_id()})
    issues = validate_service_identity(value)
    if issues:
        raise ValueError("service_identity_invalid:" + ",".join(issues))
    return value


def _handle_request(request: dict[str, Any], identity: ServiceIdentity, token: str, stop_event: threading.Event) -> dict[str, Any]:
    rid = request["request_id"]
    operation = request["operation"]
    if operation == "health":
        return response(
            rid,
            ok=True,
            code="HEALTHY",
            lifecycle_state="RUNNING",
            data={
                "healthy": True,
                "service_identity_id": identity.identity_id,
                "transport": TRANSPORT,
                "owner_uid": os.getuid(),
                "repository_write_authority": False,
                "network_authority": False,
            },
        )
    if operation == "version":
        return response(rid, ok=True, code="VERSION", lifecycle_state="RUNNING", data=_version_report())
    if operation == "capabilities":
        return response(rid, ok=True, code="CAPABILITY_STATE", lifecycle_state="RUNNING", data=build_capability_report(True))
    if operation == "status":
        return response(
            rid,
            ok=True,
            code="RUNNING",
            lifecycle_state="RUNNING",
            data={
                "identity": identity.to_dict(),
                "health": {"healthy": True},
                "transport": {"kind": TRANSPORT, "socket_path": identity.socket_path, "tcp_listener": False},
            },
        )
    if operation == "shutdown":
        supplied = request.get("control_token") or ""
        if not hmac.compare_digest(supplied, token):
            return response(
                rid,
                ok=False,
                code="UNAUTHORIZED",
                lifecycle_state="RUNNING",
                detail="shutdown requires the exact owner-only control token",
            )
        stop_event.set()
        return response(rid, ok=True, code="SHUTDOWN_ACCEPTED", lifecycle_state="STOPPING")
    return response(rid, ok=False, code="UNSUPPORTED_OPERATION", lifecycle_state="RUNNING")


def serve_forever(*, state_root: Path, repository_root: Path, entry_script: Path) -> int:
    expected_entry = repository_root.resolve() / "scripts" / "aiweb_slice48_local_runtime_service.py"
    if entry_script.resolve() != expected_entry or not expected_entry.is_file() or expected_entry.is_symlink():
        raise ValueError("entry_script_identity_mismatch")
    paths = make_paths(state_root)
    stop_event = threading.Event()

    def request_stop(_signum: int, _frame: object) -> None:
        stop_event.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    with exclusive_lock(paths.service_lock, nonblocking=True):
        token = read_text(paths.token).strip()
        if len(token) < 32:
            raise ValueError("control_token_invalid")
        if paths.socket.exists() or paths.socket.is_symlink():
            raise ValueError("socket_path_not_clean")

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.settimeout(0.25)
        try:
            server.bind(str(paths.socket))
            os.chmod(paths.socket, 0o600)
            server.listen(16)

            process = current_process_record(entry_script, repository_root, paths.root)
            identity = _identity(process, paths, repository_root, entry_script, token)
            atomic_write_json(paths.process, process.to_dict(), 0o600)
            atomic_write_json(paths.identity, identity.to_dict(), 0o600)

            while not stop_event.is_set():
                try:
                    connection, _address = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if stop_event.is_set():
                        break
                    raise
                with connection:
                    connection.settimeout(2.0)
                    rid = "unknown"
                    try:
                        uid = peer_uid(connection)
                        if uid is not None and uid != os.getuid():
                            reply = response(
                                rid,
                                ok=False,
                                code="PEER_UID_REJECTED",
                                lifecycle_state="RUNNING",
                                detail="peer uid does not own this service",
                            )
                        else:
                            request = decode_request(receive_bounded(connection))
                            rid = request["request_id"]
                            reply = _handle_request(request, identity, token, stop_event)
                    except ProtocolFailure as error:
                        reply = response(
                            rid,
                            ok=False,
                            code=error.code,
                            lifecycle_state="RUNNING",
                            detail=error.detail,
                        )
                    except Exception as error:
                        reply = response(
                            rid,
                            ok=False,
                            code="INTERNAL_ERROR",
                            lifecycle_state="RUNNING",
                            detail=type(error).__name__,
                        )
                    try:
                        connection.sendall(encode_message(reply))
                    except OSError:
                        pass
        finally:
            server.close()
            cleanup_runtime_artifacts(paths, include_token=True)
    return 0

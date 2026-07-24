"""Explicit lifecycle control and reporting for Slice 48."""
from __future__ import annotations

import argparse
import json
import os
import secrets
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence

from .authority import (
    BUILD_BASE_HEAD,
    BUILD_BASE_SUBJECT,
    BUILD_BASE_TREE,
    BUILD_ID,
    FALLBACK_TERM_TIMEOUT_SECONDS,
    PROTOCOL_VERSION,
    SCHEMA_VERSION,
    SERVICE_VERSION,
    SHUTDOWN_TIMEOUT_SECONDS,
    STARTUP_TIMEOUT_SECONDS,
    TRANSPORT,
)
from .capabilities import build_capability_report
from .protocol import ProtocolFailure, send_request
from .service import serve_forever
from .state import (
    atomic_write_text,
    cleanup_runtime_artifacts,
    default_state_root,
    ensure_state_root,
    exclusive_lock,
    file_mode,
    load_process_record,
    load_service_identity,
    lock_is_held,
    make_paths,
    process_alive,
    process_record_matches_live,
    read_text,
)

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_ALREADY_RUNNING = 3
EXIT_NOT_HEALTHY = 4
EXIT_IDENTITY_REFUSED = 5


def version_report() -> dict[str, Any]:
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


def _result(ok: bool, code: str, lifecycle_state: str, *, detail: str = "", data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "ok": bool(ok),
        "code": code,
        "lifecycle_state": lifecycle_state,
        "detail": detail,
        "data": data or {},
    }


def _status_unlocked(paths) -> dict[str, Any]:
    process = None
    identity = None
    process_error = None
    identity_error = None
    try:
        process = load_process_record(paths)
    except Exception as error:
        process_error = f"{type(error).__name__}:{error}"
    try:
        identity = load_service_identity(paths)
    except Exception as error:
        identity_error = f"{type(error).__name__}:{error}"

    service_lock_held = lock_is_held(paths.service_lock)
    artifacts = {
        "socket_exists": paths.socket.exists() or paths.socket.is_symlink(),
        "process_record_exists": paths.process.exists() or paths.process.is_symlink(),
        "identity_record_exists": paths.identity.exists() or paths.identity.is_symlink(),
        "token_exists": paths.token.exists() or paths.token.is_symlink(),
        "service_lock_held": service_lock_held,
    }
    if process is None:
        if service_lock_held:
            state = "STARTING"
        else:
            state = "STALE" if any(value for key, value in artifacts.items() if key != "service_lock_held") else "STOPPED"
        return _result(
            state == "STOPPED",
            state,
            state,
            detail=process_error or identity_error or "",
            data={"artifacts": artifacts, "transport": TRANSPORT},
        )

    matches, reason = process_record_matches_live(process)
    if not matches:
        if not process_alive(process.pid):
            state = "STALE"
        else:
            state = "FOREIGN_PROCESS"
        return _result(
            False,
            state,
            state,
            detail=reason,
            data={"process": process.to_dict(), "artifacts": artifacts, "identity_error": identity_error},
        )

    if identity is None:
        return _result(False, "STARTING", "STARTING", detail=identity_error or "identity record not ready", data={"process": process.to_dict(), "artifacts": artifacts})
    if identity.pid != process.pid or identity.process_start_ticks != process.process_start_ticks or identity.command_sha256 != process.command_sha256:
        return _result(False, "IDENTITY_MISMATCH", "FOREIGN_PROCESS", detail="service and process records disagree", data={"process": process.to_dict(), "identity": identity.to_dict()})
    try:
        health = send_request(paths.socket, "health", timeout=1.0)
    except Exception as error:
        return _result(False, "UNRESPONSIVE", "FAILED", detail=f"{type(error).__name__}:{error}", data={"process": process.to_dict(), "identity": identity.to_dict(), "artifacts": artifacts})
    return _result(bool(health.get("ok")), "RUNNING", "RUNNING", data={"process": process.to_dict(), "identity": identity.to_dict(), "health": health, "artifacts": artifacts})


def status_service(*, state_root: Path, repository_root: Path) -> tuple[int, dict[str, Any]]:
    paths = make_paths(state_root)
    ensure_state_root(paths, repository_root)
    with exclusive_lock(paths.control_lock):
        report = _status_unlocked(paths)
    return (EXIT_OK if report["lifecycle_state"] in {"RUNNING", "STOPPED"} else EXIT_NOT_HEALTHY), report


def _validate_entry_context(repository_root: Path, entry_script: Path) -> None:
    expected = repository_root.resolve() / "scripts" / "aiweb_slice48_local_runtime_service.py"
    if not repository_root.is_dir():
        raise ValueError("repository_root_missing")
    if entry_script.resolve() != expected:
        raise ValueError("entry_script_identity_mismatch")
    if not expected.is_file() or expected.is_symlink():
        raise ValueError("entry_script_missing_or_symlink")


def start_service(*, state_root: Path, repository_root: Path, entry_script: Path, python_executable: Path) -> tuple[int, dict[str, Any]]:
    _validate_entry_context(repository_root, entry_script)
    paths = make_paths(state_root)
    ensure_state_root(paths, repository_root)
    with exclusive_lock(paths.control_lock):
        status = _status_unlocked(paths)
        if status["lifecycle_state"] == "RUNNING":
            return EXIT_ALREADY_RUNNING, _result(False, "ALREADY_RUNNING", "RUNNING", detail="duplicate start refused", data=status["data"])
        if status["lifecycle_state"] == "FOREIGN_PROCESS":
            return EXIT_IDENTITY_REFUSED, _result(False, "FOREIGN_PROCESS", "FOREIGN_PROCESS", detail="live process identity does not match; no signal sent", data=status["data"])
        if status["lifecycle_state"] in {"STALE", "FAILED", "STARTING", "UNKNOWN"}:
            process = status.get("data", {}).get("process")
            if status["lifecycle_state"] == "STARTING" and process is None:
                return EXIT_IDENTITY_REFUSED, _result(False, "STARTING_IDENTITY_INCOMPLETE", "STARTING", detail="service lock is held but process identity is not yet complete")
            if process and process_alive(int(process.get("pid", 0))):
                return EXIT_IDENTITY_REFUSED, _result(False, "LIVE_STATE_NOT_OWNED", "FOREIGN_PROCESS", detail="refusing to clean artifacts for a live unverified process")
            cleanup_runtime_artifacts(paths, include_token=True)

        token = secrets.token_hex(32)
        atomic_write_text(paths.token, token + "\n", 0o600)
        command = [
            str(python_executable.absolute()),
            "-B",
            str(entry_script.resolve()),
            "--format",
            "json",
            "serve",
            "--state-root",
            str(paths.root),
            "--repository-root",
            str(repository_root.resolve()),
        ]
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"
        paths.log.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with paths.log.open("a", encoding="utf-8") as log:
            os.chmod(paths.log, 0o600)
            process = subprocess.Popen(
                command,
                cwd=str(repository_root.resolve()),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                close_fds=True,
            )

        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        last_error = ""
        while time.monotonic() < deadline:
            if process.poll() is not None:
                last_error = f"service exited during startup with code {process.returncode}"
                break
            try:
                health = send_request(paths.socket, "health", timeout=0.5)
                if health.get("ok") and health.get("code") == "HEALTHY":
                    report = _status_unlocked(paths)
                    return EXIT_OK, _result(True, "STARTED", "RUNNING", data={**report["data"], "startup_pid": process.pid})
            except Exception as error:
                last_error = f"{type(error).__name__}:{error}"
            time.sleep(0.1)

        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(timeout=FALLBACK_TERM_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                pass
        cleanup_runtime_artifacts(paths, include_token=True)
        return EXIT_FAILURE, _result(False, "START_FAILED", "FAILED", detail=last_error or "startup timeout")


def stop_service(*, state_root: Path, repository_root: Path) -> tuple[int, dict[str, Any]]:
    paths = make_paths(state_root)
    ensure_state_root(paths, repository_root)
    with exclusive_lock(paths.control_lock):
        status = _status_unlocked(paths)
        state = status["lifecycle_state"]
        if state == "STOPPED":
            return EXIT_OK, _result(True, "ALREADY_STOPPED", "STOPPED")
        process = None
        try:
            process = load_process_record(paths)
        except Exception as error:
            return EXIT_IDENTITY_REFUSED, _result(False, "PROCESS_RECORD_INVALID", state, detail=f"{type(error).__name__}:{error}")
        if process is None:
            if state == "STALE":
                cleanup_runtime_artifacts(paths, include_token=True)
                return EXIT_OK, _result(True, "STALE_STATE_CLEANED", "STOPPED")
            return EXIT_IDENTITY_REFUSED, _result(False, "PROCESS_RECORD_MISSING", state)

        matches, reason = process_record_matches_live(process)
        if not matches:
            if not process_alive(process.pid):
                cleanup_runtime_artifacts(paths, include_token=True)
                return EXIT_OK, _result(True, "STALE_STATE_CLEANED", "STOPPED", detail=reason)
            return EXIT_IDENTITY_REFUSED, _result(False, "FOREIGN_PROCESS", "FOREIGN_PROCESS", detail=reason)

        try:
            token = read_text(paths.token).strip()
            reply = send_request(paths.socket, "shutdown", control_token=token, timeout=2.0)
            if not reply.get("ok"):
                return EXIT_IDENTITY_REFUSED, _result(False, "SHUTDOWN_REJECTED", "RUNNING", detail=str(reply.get("code")))
        except Exception:
            os.kill(process.pid, signal.SIGTERM)

        deadline = time.monotonic() + SHUTDOWN_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            if not process_alive(process.pid):
                cleanup_runtime_artifacts(paths, include_token=True)
                return EXIT_OK, _result(True, "STOPPED", "STOPPED")
            time.sleep(0.1)

        matches_after, reason_after = process_record_matches_live(process)
        if matches_after:
            os.kill(process.pid, signal.SIGTERM)
            deadline = time.monotonic() + FALLBACK_TERM_TIMEOUT_SECONDS
            while time.monotonic() < deadline:
                if not process_alive(process.pid):
                    cleanup_runtime_artifacts(paths, include_token=True)
                    return EXIT_OK, _result(True, "STOPPED_AFTER_TERM", "STOPPED")
                time.sleep(0.1)
        return EXIT_FAILURE, _result(False, "STOP_TIMEOUT", "FAILED", detail=reason_after)


def health_service(*, state_root: Path, repository_root: Path) -> tuple[int, dict[str, Any]]:
    paths = make_paths(state_root)
    ensure_state_root(paths, repository_root)
    with exclusive_lock(paths.control_lock):
        status = _status_unlocked(paths)
        if status["lifecycle_state"] != "RUNNING":
            return EXIT_NOT_HEALTHY, _result(False, "NOT_HEALTHY", status["lifecycle_state"], detail=status.get("detail", ""), data=status.get("data", {}))
        try:
            reply = send_request(paths.socket, "health", timeout=2.0)
        except Exception as error:
            return EXIT_NOT_HEALTHY, _result(False, "HEALTH_REQUEST_FAILED", "FAILED", detail=f"{type(error).__name__}:{error}")
        return (EXIT_OK if reply.get("ok") else EXIT_NOT_HEALTHY), reply


def capabilities_service(*, state_root: Path, repository_root: Path) -> tuple[int, dict[str, Any]]:
    paths = make_paths(state_root)
    ensure_state_root(paths, repository_root)
    with exclusive_lock(paths.control_lock):
        status = _status_unlocked(paths)
        if status["lifecycle_state"] == "RUNNING":
            try:
                return EXIT_OK, send_request(paths.socket, "capabilities", timeout=2.0)
            except Exception as error:
                return EXIT_NOT_HEALTHY, _result(False, "CAPABILITY_REQUEST_FAILED", "FAILED", detail=f"{type(error).__name__}:{error}")
        return EXIT_OK, _result(True, "CAPABILITY_STATE", status["lifecycle_state"], data=build_capability_report(False))


def version_service(*, state_root: Path, repository_root: Path) -> tuple[int, dict[str, Any]]:
    paths = make_paths(state_root)
    ensure_state_root(paths, repository_root)
    with exclusive_lock(paths.control_lock):
        status = _status_unlocked(paths)
        if status["lifecycle_state"] == "RUNNING":
            try:
                return EXIT_OK, send_request(paths.socket, "version", timeout=2.0)
            except Exception as error:
                return EXIT_NOT_HEALTHY, _result(False, "VERSION_REQUEST_FAILED", "FAILED", detail=f"{type(error).__name__}:{error}")
        return EXIT_OK, _result(True, "VERSION", status["lifecycle_state"], data=version_report())


def _render(value: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(value, indent=2, sort_keys=True))
        return
    print("AI.Web Forge Local Runtime Service")
    print("──────────────────────────────────")
    print(f"Result: {value.get('code')}")
    print(f"State:  {value.get('lifecycle_state')}")
    print(f"OK:     {value.get('ok')}")
    if value.get("detail"):
        print(f"Detail: {value.get('detail')}")
    data = value.get("data") or {}
    if data:
        print("Data:")
        for key in sorted(data):
            rendered = json.dumps(data[key], sort_keys=True) if isinstance(data[key], (dict, list)) else str(data[key])
            print(f"  {key}: {rendered}")


def cli_main(argv: Sequence[str] | None = None, *, entry_script: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI.Web Forge Slice 48 local runtime service boundary")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("start", "stop", "status", "health", "version", "capabilities"):
        item = sub.add_parser(command)
        item.add_argument("--state-root", type=Path, default=default_state_root())
        item.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parents[2])
    serve_parser = sub.add_parser("serve", help=argparse.SUPPRESS)
    serve_parser.add_argument("--state-root", type=Path, required=True)
    serve_parser.add_argument("--repository-root", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)

    script = (entry_script or Path(sys.argv[0])).resolve()
    repository_root = args.repository_root.expanduser().resolve()
    state_root = args.state_root.expanduser().resolve()

    if args.command == "serve":
        return serve_forever(state_root=state_root, repository_root=repository_root, entry_script=script)
    if args.command == "start":
        code, result = start_service(state_root=state_root, repository_root=repository_root, entry_script=script, python_executable=Path(sys.executable))
    elif args.command == "stop":
        code, result = stop_service(state_root=state_root, repository_root=repository_root)
    elif args.command == "status":
        code, result = status_service(state_root=state_root, repository_root=repository_root)
    elif args.command == "health":
        code, result = health_service(state_root=state_root, repository_root=repository_root)
    elif args.command == "version":
        code, result = version_service(state_root=state_root, repository_root=repository_root)
    elif args.command == "capabilities":
        code, result = capabilities_service(state_root=state_root, repository_root=repository_root)
    else:
        code, result = EXIT_FAILURE, _result(False, "UNKNOWN_COMMAND", "UNKNOWN")
    _render(result, args.format)
    return code

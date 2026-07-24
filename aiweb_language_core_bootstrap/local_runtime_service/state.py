"""Owner-only runtime state and process-identity custody."""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from .authority import DEFAULT_STATE_DIRECTORY_NAME, SCHEMA_VERSION, SERVICE_VERSION
from .canonical import canonical_json_text, sha256_bytes
from .schema import ProcessRecord, ServiceIdentity
from .validation import validate_process_record, validate_service_identity


@dataclass(frozen=True, slots=True)
class StatePaths:
    root: Path
    socket: Path
    process: Path
    identity: Path
    token: Path
    control_lock: Path
    service_lock: Path
    log: Path


def default_state_root() -> Path:
    xdg = os.environ.get("XDG_STATE_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".local" / "state"
    return (base / "aiweb-forge" / DEFAULT_STATE_DIRECTORY_NAME).resolve()


def make_paths(root: Path) -> StatePaths:
    resolved = Path(os.path.abspath(root.expanduser()))
    return StatePaths(
        root=resolved,
        socket=resolved / "service.sock",
        process=resolved / "service.pid.json",
        identity=resolved / "service.identity.json",
        token=resolved / "control.token",
        control_lock=resolved / "control.lock",
        service_lock=resolved / "service.lock",
        log=resolved / "service.log",
    )


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def ensure_state_root(paths: StatePaths, repository_root: Path) -> None:
    if is_within(paths.root, repository_root):
        raise ValueError("state_root_inside_repository")
    if paths.root.exists() and paths.root.is_symlink():
        raise ValueError("state_root_is_symlink")
    paths.root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(paths.root, 0o700)
    if not paths.root.is_dir():
        raise ValueError("state_root_not_directory")


def _reject_symlink(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"runtime_state_symlink_rejected:{path.name}")


def atomic_write_text(path: Path, text: str, mode: int = 0o600) -> None:
    _reject_symlink(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary_name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=str(path.parent))
    temporary = Path(temporary_name)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8", closefd=True) as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        os.chmod(path, mode)
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_write_json(path: Path, value: Any, mode: int = 0o600) -> None:
    atomic_write_text(path, canonical_json_text(value) + "\n", mode)


def read_json(path: Path) -> Any:
    _reject_symlink(path)
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    _reject_symlink(path)
    return path.read_text(encoding="utf-8")


def process_alive(pid: int) -> bool:
    if pid <= 1:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def process_start_ticks(pid: int) -> int:
    raw = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    end = raw.rfind(")")
    if end < 0:
        raise ValueError("proc_stat_malformed")
    fields = raw[end + 2 :].split()
    if len(fields) <= 19:
        raise ValueError("proc_stat_too_short")
    return int(fields[19])


def process_cmdline_bytes(pid: int) -> bytes:
    return Path(f"/proc/{pid}/cmdline").read_bytes()


def process_cmdline_text(pid: int) -> str:
    return process_cmdline_bytes(pid).replace(b"\x00", b" ").decode("utf-8", errors="replace")


def process_command_sha256(pid: int) -> str:
    return sha256_bytes(process_cmdline_bytes(pid))


def current_process_record(entry_script: Path, repository_root: Path, state_root: Path) -> ProcessRecord:
    pid = os.getpid()
    return ProcessRecord(
        schema_version=SCHEMA_VERSION,
        service_version=SERVICE_VERSION,
        pid=pid,
        process_start_ticks=process_start_ticks(pid),
        command_sha256=process_command_sha256(pid),
        entry_script=str(entry_script.resolve()),
        repository_root=str(repository_root.resolve()),
        state_root=str(state_root.resolve()),
    )


def process_record_from_dict(value: dict[str, Any]) -> ProcessRecord:
    record = ProcessRecord(**value)
    issues = validate_process_record(record)
    if issues:
        raise ValueError("invalid_process_record:" + ",".join(issues))
    return record


def service_identity_from_dict(value: dict[str, Any]) -> ServiceIdentity:
    identity = ServiceIdentity(**value)
    issues = validate_service_identity(identity)
    if issues:
        raise ValueError("invalid_service_identity:" + ",".join(issues))
    return identity


def process_record_matches_live(record: ProcessRecord) -> tuple[bool, str]:
    if not process_alive(record.pid):
        return False, "PROCESS_NOT_ALIVE"
    try:
        if process_start_ticks(record.pid) != record.process_start_ticks:
            return False, "PROCESS_START_TICKS_MISMATCH"
        if process_command_sha256(record.pid) != record.command_sha256:
            return False, "PROCESS_COMMAND_DIGEST_MISMATCH"
        command = process_cmdline_text(record.pid)
    except (OSError, ValueError):
        return False, "PROCESS_IDENTITY_UNREADABLE"
    if record.entry_script not in command or " serve " not in f" {command} ":
        return False, "PROCESS_COMMAND_MARKER_MISMATCH"
    return True, "MATCH"


def load_process_record(paths: StatePaths) -> ProcessRecord | None:
    if not paths.process.exists():
        return None
    return process_record_from_dict(read_json(paths.process))


def load_service_identity(paths: StatePaths) -> ServiceIdentity | None:
    if not paths.identity.exists():
        return None
    return service_identity_from_dict(read_json(paths.identity))


def file_mode(path: Path) -> int | None:
    if not path.exists():
        return None
    return stat.S_IMODE(path.stat().st_mode)


def cleanup_runtime_artifacts(paths: StatePaths, *, include_token: bool = True) -> None:
    for path in (paths.socket, paths.process, paths.identity):
        _reject_symlink(path)
        path.unlink(missing_ok=True)
    if include_token:
        _reject_symlink(paths.token)
        paths.token.unlink(missing_ok=True)


def lock_is_held(path: Path) -> bool:
    _reject_symlink(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("a+", encoding="utf-8") as handle:
        os.chmod(path, 0o600)
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        else:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            return False


@contextlib.contextmanager
def exclusive_lock(path: Path, *, nonblocking: bool = False) -> Iterator[None]:
    _reject_symlink(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("a+", encoding="utf-8") as handle:
        os.chmod(path, 0o600)
        flags = fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0)
        fcntl.flock(handle.fileno(), flags)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

#!/usr/bin/env python3
"""Real behavior test for Slice 48 local runtime service boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path


class Ledger:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(label)
            print("FAIL - " + label)


def run(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=str(cwd), env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=40)


def parse_json_output(result: subprocess.CompletedProcess[str]) -> dict:
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError(f"command output is not JSON: {error}: {result.stdout[:500]}") from error
    if not isinstance(value, dict):
        raise AssertionError("command output is not a JSON object")
    return value


def process_socket_inodes(pid: int) -> set[str]:
    inodes: set[str] = set()
    fd_root = Path(f"/proc/{pid}/fd")
    for descriptor in fd_root.iterdir():
        try:
            target = os.readlink(descriptor)
        except OSError:
            continue
        if target.startswith("socket:[") and target.endswith("]"):
            inodes.add(target[8:-1])
    return inodes


def network_socket_inodes(paths: tuple[Path, ...]) -> set[str]:
    inodes: set[str] = set()
    for path in paths:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            fields = line.split()
            if len(fields) > 9:
                inodes.add(fields[9])
    return inodes


def unix_socket_inodes() -> set[str]:
    path = Path("/proc/net/unix")
    if not path.is_file():
        return set()
    inodes: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        fields = line.split()
        if len(fields) > 6:
            inodes.add(fields[6])
    return inodes


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    sys.path.insert(0, str(repo))
    ledger = Ledger()

    before_status = subprocess.run(["/usr/bin/git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=all"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False).stdout
    legacy_loaded_before = "main" in sys.modules

    from aiweb_language_core_bootstrap.local_runtime_service import (
        BUILD_BASE_HEAD,
        BUILD_ID,
        PROTOCOL_VERSION,
        SERVICE_VERSION,
        TRANSPORT,
        build_capability_report,
    )
    from aiweb_language_core_bootstrap.local_runtime_service.canonical import canonical_json_text
    from aiweb_language_core_bootstrap.local_runtime_service.protocol import encode_message, receive_bounded
    from aiweb_language_core_bootstrap.local_runtime_service.state import (
        atomic_write_json,
        atomic_write_text,
        make_paths,
        process_command_sha256,
        process_start_ticks,
    )

    ledger.check(not legacy_loaded_before, "main not loaded before import")
    ledger.check("main" not in sys.modules, "main not loaded by Slice 48 import")
    ledger.check(BUILD_BASE_HEAD == "1f9070065aad5df11627cbb16732430ca47ded11", "exact Slice 47 base")
    ledger.check(BUILD_ID == "AIWEB-SLICE48-LOCAL-RUNTIME-SERVICE-BOUNDARY-V1", "build identity")
    ledger.check(SERVICE_VERSION == "1.0.0", "service version")
    ledger.check(PROTOCOL_VERSION == "aiweb_local_runtime_service_v1", "protocol version")
    ledger.check(TRANSPORT == "unix_domain_socket", "AF_UNIX transport")

    first_caps = build_capability_report(False)
    second_caps = build_capability_report(False)
    ledger.check(first_caps == second_caps, "deterministic stopped capability report")
    ledger.check(canonical_json_text(first_caps) == canonical_json_text(second_caps), "canonical capability serialization")
    cap_map = {item["capability_id"]: item for item in first_caps["capabilities"]}
    ledger.check(cap_map["language.inspection_api"]["state"] == "DEFERRED", "Slice 49 inspection API deferred")
    ledger.check(cap_map["general_language.interpretation"]["authority"] is False, "no interpretation authority")
    ledger.check(cap_map["memory.write"]["authority"] is False, "no memory write authority")
    ledger.check(cap_map["tool_action_delivery.execution"]["authority"] is False, "no tool action delivery authority")
    ledger.check(cap_map["gp014.bounded_lane"]["state"] == "PRESERVED", "GP-014 preserved")
    ledger.check(all(value is False for value in first_caps["prohibited_authorities"].values()), "all prohibited authorities remain false")

    entry = repo / "scripts/aiweb_slice48_local_runtime_service.py"
    package_root = repo / "aiweb_language_core_bootstrap/local_runtime_service"
    source = "\n".join(path.read_text(encoding="utf-8") for path in sorted(package_root.glob("*.py")))
    ledger.check(entry.is_file(), "entrypoint exists")
    ledger.check("socket.AF_INET" not in source and "socket.AF_INET6" not in source, "no Internet socket family")
    ledger.check("HTTPServer" not in source and "TCPServer" not in source, "no HTTP or TCP server")
    ledger.check("main.py" not in source, "no main.py launch")
    ledger.check("aiweb_os_appctl" not in source, "no legacy appctl launch")
    ledger.check("uvicorn" not in source and "FastAPI" not in source and "Flask" not in source, "no web framework")
    ledger.check("SIGKILL" not in source, "no SIGKILL")
    ledger.check("shell=True" not in source, "no shell execution")

    py = str(repo / ".venv/bin/python3") if (repo / ".venv/bin/python3").is_file() else sys.executable
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONPATH"] = str(repo)

    with tempfile.TemporaryDirectory(prefix="aiweb-slice48-behavior-") as temp_name:
        temp = Path(temp_name)
        state_root = temp / "runtime-state"

        def command(name: str) -> list[str]:
            return [py, "-u", "-B", str(entry), "--format", "json", name, "--state-root", str(state_root), "--repository-root", str(repo)]

        stopped_status = run(command("status"), repo, env)
        stopped_value = parse_json_output(stopped_status)
        ledger.check(stopped_status.returncode == 0, "stopped status returns success")
        ledger.check(stopped_value["lifecycle_state"] == "STOPPED", "initially stopped")

        version_one = parse_json_output(run(command("version"), repo, env))
        version_two = parse_json_output(run(command("version"), repo, env))
        ledger.check(version_one == version_two, "deterministic version reporting")
        ledger.check(version_one["data"]["transport"] == "unix_domain_socket", "version reports AF_UNIX")

        stopped_caps = parse_json_output(run(command("capabilities"), repo, env))
        ledger.check(stopped_caps["ok"] is True, "capabilities available while stopped")
        ledger.check(stopped_caps["data"]["service_running"] is False, "stopped capability state")

        start_result = run(command("start"), repo, env)
        start_value = parse_json_output(start_result)
        ledger.check(start_result.returncode == 0, "start command succeeds")
        ledger.check(start_value["code"] == "STARTED", "explicit startup result")
        ledger.check(start_value["lifecycle_state"] == "RUNNING", "startup reaches running")

        paths = make_paths(state_root)
        ledger.check(paths.socket.exists(), "Unix socket exists")
        ledger.check(stat.S_ISSOCK(paths.socket.stat().st_mode), "transport file is a Unix socket")
        ledger.check(stat.S_IMODE(paths.root.stat().st_mode) == 0o700, "state root mode 0700")
        for controlled in (paths.socket, paths.process, paths.identity, paths.token, paths.control_lock, paths.service_lock):
            ledger.check(controlled.exists(), f"runtime artifact exists: {controlled.name}")
            if controlled.exists():
                ledger.check(stat.S_IMODE(controlled.stat().st_mode) == 0o600, f"runtime artifact mode 0600: {controlled.name}")

        running_status_result = run(command("status"), repo, env)
        running_status = parse_json_output(running_status_result)
        ledger.check(running_status_result.returncode == 0, "running status succeeds")
        ledger.check(running_status["lifecycle_state"] == "RUNNING", "running status reported")
        ledger.check(running_status["data"]["identity"]["transport"] == "unix_domain_socket", "identity reports Unix transport")

        health_result = run(command("health"), repo, env)
        health = parse_json_output(health_result)
        ledger.check(health_result.returncode == 0, "health succeeds")
        ledger.check(health["code"] == "HEALTHY", "healthy result")
        ledger.check(health["data"]["repository_write_authority"] is False, "health grants no repository write")
        ledger.check(health["data"]["network_authority"] is False, "health grants no network authority")

        live_caps_one = parse_json_output(run(command("capabilities"), repo, env))
        live_caps_two = parse_json_output(run(command("capabilities"), repo, env))
        ledger.check(live_caps_one["data"] == live_caps_two["data"], "deterministic live capability report")
        ledger.check(live_caps_one["data"]["service_running"] is True, "live capability state")

        duplicate = run(command("start"), repo, env)
        duplicate_value = parse_json_output(duplicate)
        ledger.check(duplicate.returncode == 3, "duplicate start refused with exact return code")
        ledger.check(duplicate_value["code"] == "ALREADY_RUNNING", "duplicate start refusal recorded")

        # Fail-closed malformed and unauthorized protocol cases.
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(2.0)
        client.connect(str(paths.socket))
        client.sendall(b"not-json\n")
        malformed = json.loads(receive_bounded(client).decode("utf-8"))
        client.close()
        ledger.check(malformed["code"] == "INVALID_JSON", "malformed JSON rejected")

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(2.0)
        client.connect(str(paths.socket))
        client.sendall(encode_message({"protocol": PROTOCOL_VERSION, "request_id": "bad-operation", "operation": "execute", "control_token": None}))
        unsupported = json.loads(receive_bounded(client).decode("utf-8"))
        client.close()
        ledger.check(unsupported["code"] == "UNSUPPORTED_OPERATION", "unknown operation rejected")

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(2.0)
        client.connect(str(paths.socket))
        client.sendall(encode_message({"protocol": PROTOCOL_VERSION, "request_id": "bad-token", "operation": "shutdown", "control_token": "wrong"}))
        wrong_token = json.loads(receive_bounded(client).decode("utf-8"))
        client.close()
        ledger.check(wrong_token["code"] == "UNAUTHORIZED", "wrong shutdown token rejected")
        ledger.check(parse_json_output(run(command("health"), repo, env))["code"] == "HEALTHY", "service survives unauthorized shutdown")

        service_pid = int(start_value["data"]["process"]["pid"])
        service_socket_inodes = process_socket_inodes(service_pid)
        internet_socket_inodes = network_socket_inodes((
            Path("/proc/net/tcp"),
            Path("/proc/net/tcp6"),
            Path("/proc/net/udp"),
            Path("/proc/net/udp6"),
        ))
        ledger.check(bool(service_socket_inodes), "service owns at least one socket")
        ledger.check(service_socket_inodes.isdisjoint(internet_socket_inodes), "service owns no TCP or UDP socket")
        ledger.check(bool(service_socket_inodes & unix_socket_inodes()), "service socket is present in AF_UNIX table")

        stop_result = run(command("stop"), repo, env)
        stop_value = parse_json_output(stop_result)
        ledger.check(stop_result.returncode == 0, "stop command succeeds")
        ledger.check(stop_value["lifecycle_state"] == "STOPPED", "explicit shutdown result")
        ledger.check(not paths.socket.exists(), "socket removed after stop")
        ledger.check(not paths.process.exists(), "process record removed after stop")
        ledger.check(not paths.identity.exists(), "identity record removed after stop")
        ledger.check(not paths.token.exists(), "control token removed after stop")

        stopped_health_result = run(command("health"), repo, env)
        stopped_health = parse_json_output(stopped_health_result)
        ledger.check(stopped_health_result.returncode == 4, "stopped health return code")
        ledger.check(stopped_health["code"] == "NOT_HEALTHY", "stopped health fail-closed")

        # Stale dead state is cleaned and replaced by a new exact service identity.
        paths.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        atomic_write_json(paths.process, {
            "schema_version": "aiweb_local_runtime_service_schema_v1",
            "service_version": "1.0.0",
            "pid": 99999999,
            "process_start_ticks": 1,
            "command_sha256": "0" * 64,
            "entry_script": str(entry),
            "repository_root": str(repo),
            "state_root": str(paths.root),
        })
        atomic_write_text(paths.socket, "stale\n")
        stale_start = run(command("start"), repo, env)
        stale_start_value = parse_json_output(stale_start)
        ledger.check(stale_start.returncode == 0, "stale state recovery start succeeds")
        ledger.check(stale_start_value["code"] == "STARTED", "stale state replaced")
        ledger.check(stat.S_ISSOCK(paths.socket.stat().st_mode), "stale socket replaced by Unix socket")
        ledger.check(run(command("stop"), repo, env).returncode == 0, "recovered service stops")

        # A live unrelated process referenced by forged state is never signaled.
        foreign_root = temp / "foreign-state"
        foreign_paths = make_paths(foreign_root)
        foreign_paths.root.mkdir(parents=True, mode=0o700)
        sleeper = subprocess.Popen([py, "-B", "-c", "import time; time.sleep(30)"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            ticks = process_start_ticks(sleeper.pid)
            digest = process_command_sha256(sleeper.pid)
            atomic_write_json(foreign_paths.process, {
                "schema_version": "aiweb_local_runtime_service_schema_v1",
                "service_version": "1.0.0",
                "pid": sleeper.pid,
                "process_start_ticks": ticks,
                "command_sha256": digest,
                "entry_script": str(entry),
                "repository_root": str(repo),
                "state_root": str(foreign_paths.root),
            })
            foreign_command = [py, "-u", "-B", str(entry), "--format", "json", "stop", "--state-root", str(foreign_root), "--repository-root", str(repo)]
            foreign_stop = run(foreign_command, repo, env)
            foreign_value = parse_json_output(foreign_stop)
            ledger.check(foreign_stop.returncode == 5, "foreign process stop refused")
            ledger.check(foreign_value["code"] == "FOREIGN_PROCESS", "foreign process classified")
            ledger.check(sleeper.poll() is None, "unrelated process remains alive")
        finally:
            sleeper.terminate()
            try:
                sleeper.wait(timeout=5)
            except subprocess.TimeoutExpired:
                sleeper.kill()
                sleeper.wait(timeout=5)

    after_status = subprocess.run(["/usr/bin/git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=all"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False).stdout
    ledger.check(after_status == before_status, "repository state unchanged")
    source_caches = []
    for cache in repo.rglob("__pycache__"):
        try:
            relative = cache.relative_to(repo)
        except ValueError:
            continue
        if relative.parts and relative.parts[0] in {".git", ".venv"}:
            continue
        if cache.is_dir():
            source_caches.append(relative.as_posix())
    ledger.check(not source_caches, "no source-tree Python caches")

    print("=== AI.WEB SLICE 48 LOCAL RUNTIME SERVICE SUMMARY ===")
    print("check_count=" + str(ledger.checks))
    print("failure_count=" + str(len(ledger.failures)))
    print("transport=unix_domain_socket")
    print("tcp_udp_http_listener=0")
    print("explicit_start_stop_status_health_version_capabilities=1")
    print("duplicate_start_refused=1")
    print("stale_state_recovery=1")
    print("unrelated_process_protected=1")
    print("main_py_started=0")
    print("legacy_appctl_started=0")
    print("language_inspection_api=0")
    print("memory_resource_tool_action_delivery_authority=0")
    print("gp014_superseded=0")
    print("next_lawful_slice=49")
    print("AI.WEB SLICE 48 BEHAVIOR TEST: " + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

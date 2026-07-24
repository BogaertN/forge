#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


EXPECTED_SOURCE_MARKERS = {
    "main.py": (
        'RUNTIME_STATE_ROOT = XDG_STATE_HOME / "aiweb-forge" / "legacy-workshop-v1"',
        'def _runtime_first_existing_file(',
        'FORGE_BUILD_SEQUENCE_SOURCE_DIR = MEMORY_DIR / "forge_build_sequence_v1"',
        'FORGE_BUILD_SEQUENCE_DIR = RUNTIME_MEMORY_DIR / "forge_build_sequence_v1"',
        '_P198_EXTRA_SEQUENCE_SOURCE_FILE = (',
        '_P198_EXTRA_SEQUENCE_FILE = (',
        'P239_PROTOFORGE_SOURCE_DIR = MEMORY_DIR / "aiweb_patch239_protoforge_connector_v1"',
        'RUNTIME_MEMORY_DIR / "aiweb_patch239_protoforge_connector_v1"',
        'def _p239_read_report_path(runtime_path: Path) -> Path:',
    ),
    "agents/forge/permissions.py": (
        'RUNTIME_STATE_ROOT = XDG_STATE_HOME / "aiweb-forge" / "legacy-workshop-v1"',
        'RUNTIME_APPROVED_PATHS_FILE = RUNTIME_STATE_ROOT / "approved_paths.json"',
        'RUNTIME_SESSION_SCOPE_FILE = RUNTIME_STATE_ROOT / "session_scope.json"',
        'def _paths_from_keys(',
        'def get_approved_paths() -> list[str]:',
    ),
    "scripts/aiweb_os_appctl.py": (
        'The forge> prompt is the authoritative readiness signal',
        'Open this URL manually:',
        'forge_child_startup_timeout',
        'PYTHONDONTWRITEBYTECODE',
    ),
}


def fail(message: str) -> None:
    print(f"FAIL - {message}")
    raise SystemExit(1)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"unable_to_load_module:{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_python(
    python: Path,
    program: str,
    *,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(python), "-B", "-c", program],
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=180,
    )


def test_static_source(repo: Path) -> int:
    checks = 0
    for relative_path, markers in EXPECTED_SOURCE_MARKERS.items():
        path = repo / relative_path
        if not path.is_file():
            fail(f"missing_source:{relative_path}")
        text = path.read_text(encoding="utf-8")
        compile(text, str(path), "exec")
        checks += 1
        for marker in markers:
            if marker not in text:
                fail(f"source_marker_missing:{relative_path}:{marker}")
            checks += 1

    main_text = (repo / "main.py").read_text(encoding="utf-8")
    forbidden_write_fragments = (
        '_P198_EXTRA_SEQUENCE_FILE = MEMORY_DIR / "forge_build_sequence_v1"',
        'P239_PROTOFORGE_CONNECTOR_DIR = MEMORY_DIR / "aiweb_patch239_protoforge_connector_v1"',
        '_p198_bsdir = MEMORY_DIR / "forge_build_sequence_v1"',
    )
    for fragment in forbidden_write_fragments:
        if fragment in main_text:
            fail(f"forbidden_source_runtime_write_marker:{fragment}")
        checks += 1
    return checks


def test_permissions(repo: Path) -> int:
    module = load_module(
        "aiweb_test_permissions_r2",
        repo / "agents" / "forge" / "permissions.py",
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="aiweb-permissions-r2-") as temp:
        root = Path(temp)
        project_a = root / "project-a"
        project_b = root / "project-b"
        project_a.mkdir()
        project_b.mkdir()

        baseline = root / "approved_paths.json"
        runtime_approved = root / "runtime-approved.json"
        runtime_scope = root / "runtime-scope.json"
        baseline_scope = root / "baseline-scope.json"

        baseline.write_text(
            json.dumps(
                {
                    "schema": "aiweb.approved_paths.slice0b.v1",
                    "approved_paths": [str(project_a)],
                    "allowed_paths": [str(project_a)],
                    "approved_roots": [str(project_a)],
                }
            ),
            encoding="utf-8",
        )
        runtime_approved.write_text(
            json.dumps({"paths": [str(project_b), str(project_a)]}),
            encoding="utf-8",
        )
        runtime_scope.write_text(
            json.dumps({"paths": [str(project_b)]}),
            encoding="utf-8",
        )
        baseline_scope.write_text(
            json.dumps({"approved_paths": [str(project_a)]}),
            encoding="utf-8",
        )

        module.APPROVED_PATHS_FILE = baseline
        module.RUNTIME_APPROVED_PATHS_FILE = runtime_approved
        module.RUNTIME_SESSION_SCOPE_FILE = runtime_scope
        module.SESSION_SCOPE_FILE = baseline_scope

        approved = module.get_approved_paths()
        if approved != [str(project_a.resolve()), str(project_b.resolve())]:
            fail(f"approved_path_union_mismatch:{approved}")
        checks += 1

        session = module.get_session_paths()
        if session != [str(project_b.resolve())]:
            fail(f"runtime_session_precedence_mismatch:{session}")
        checks += 1

        runtime_scope.unlink()
        session = module.get_session_paths()
        if session != [str(project_a.resolve())]:
            fail(f"baseline_session_fallback_mismatch:{session}")
        checks += 1
    return checks


def test_main_runtime_separation(repo: Path, python: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="aiweb-main-runtime-r2-") as temp:
        root = Path(temp)
        program = textwrap.dedent(
            f"""
            import json
            from pathlib import Path
            import main

            root = Path({str(root)!r})
            source_memory = root / "source-memory"
            runtime_memory = root / "runtime-memory"
            source_build = source_memory / "forge_build_sequence_v1"
            runtime_build = runtime_memory / "forge_build_sequence_v1"
            source_pf = source_memory / "aiweb_patch239_protoforge_connector_v1"
            runtime_pf = runtime_memory / "aiweb_patch239_protoforge_connector_v1"
            source_build.mkdir(parents=True)
            source_pf.mkdir(parents=True)

            baseline_sequence = source_build / "20260101_000000_forge_build_sequence_v1.json"
            baseline_sequence.write_text(
                json.dumps({{"build_sequence": []}}, indent=2) + "\\n",
                encoding="utf-8",
            )
            baseline_sequence_before = baseline_sequence.read_bytes()

            source_extra = source_build / "patch198_extra_sequence.json"
            source_extra.write_text(
                json.dumps({{"items": [{{"id": "S20A", "status": "DONE", "title": "Test"}}]}}),
                encoding="utf-8",
            )
            source_extra_before = source_extra.read_bytes()

            main.MEMORY_DIR = source_memory
            main.RUNTIME_MEMORY_DIR = runtime_memory
            main.FORGE_BUILD_SEQUENCE_SOURCE_DIR = source_build
            main.FORGE_BUILD_SEQUENCE_DIR = runtime_build
            main._P198_EXTRA_SEQUENCE_SOURCE_FILE = source_extra
            main._P198_EXTRA_SEQUENCE_FILE = runtime_build / "patch198_extra_sequence.json"

            main._p198_inject_into_build_sequence()
            runtime_sequences = list(runtime_build.glob("*_forge_build_sequence_v1.json"))
            assert len(runtime_sequences) == 1, runtime_sequences
            assert baseline_sequence.read_bytes() == baseline_sequence_before
            assert source_extra.read_bytes() == source_extra_before

            main._p198_save_extra_sequence({{"items": [{{"id": "R2", "status": "ACTIVE", "title": "Runtime"}}]}})
            assert main._P198_EXTRA_SEQUENCE_FILE.is_file()
            assert source_extra.read_bytes() == source_extra_before

            source_status = source_pf / "latest_protoforge_status.json"
            source_plan = source_pf / "latest_protoforge_simulation_plan.json"
            source_status.write_text(
                json.dumps({{"ok": True, "verdict": "SOURCE_STATUS"}}),
                encoding="utf-8",
            )
            source_plan.write_text(
                json.dumps({{"ok": True, "allowed_types": ["source-plan"]}}),
                encoding="utf-8",
            )
            source_status_before = source_status.read_bytes()
            source_plan_before = source_plan.read_bytes()

            runtime_pf.mkdir(parents=True)
            runtime_status = runtime_pf / "latest_protoforge_status.json"
            runtime_status.write_text(
                json.dumps({{"ok": True, "verdict": "RUNTIME_STATUS"}}),
                encoding="utf-8",
            )

            main.P239_PROTOFORGE_SOURCE_DIR = source_pf
            main.P239_PROTOFORGE_CONNECTOR_DIR = runtime_pf
            main.P239_PROTOFORGE_STATUS_JSON = runtime_status
            main.P239_PROTOFORGE_PLAN_JSON = runtime_pf / "latest_protoforge_simulation_plan.json"
            main.P239_PROTOFORGE_RUN_JSON = runtime_pf / "latest_protoforge_simulation_run.json"
            main.P239_PROTOFORGE_RESULT_JSON = runtime_pf / "latest_protoforge_result_show.json"

            assert main._p239_read_report_path(main.P239_PROTOFORGE_STATUS_JSON) == runtime_status
            assert main._p239_read_report_path(main.P239_PROTOFORGE_PLAN_JSON) == source_plan

            loaded = main._p245_protoforge_reports_v1()
            assert loaded["summary"]["service_verdict"] == "RUNTIME_STATUS"
            assert loaded["summary"]["allowed_types"] == ["source-plan"]

            runtime_result = runtime_pf / "latest_protoforge_result_show.json"
            main._p239_write_json(runtime_result, {{"ok": True, "verdict": "RUNTIME_RESULT"}})
            assert runtime_result.is_file()
            assert source_status.read_bytes() == source_status_before
            assert source_plan.read_bytes() == source_plan_before

            allowed_roots = [str(path) for path in main._p262a_allowed_roots()]
            assert str(runtime_pf) in allowed_roots
            assert str(source_pf) in allowed_roots

            assert str(main.RUNTIME_STATE_ROOT).startswith(str(root / "xdg-state"))
            assert not str(main.RUNTIME_STATE_ROOT).startswith(str(main.FORGE_ROOT))

            print("MAIN_RUNTIME_SEPARATION_R2: PASS")
            """
        )

        env = dict(os.environ)
        env["XDG_STATE_HOME"] = str(root / "xdg-state")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPATH"] = str(repo)

        result = run_python(
            python,
            program,
            cwd=repo,
            env=env,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            fail(f"main_runtime_separation_failed:{result.returncode}")
        if "MAIN_RUNTIME_SEPARATION_R2: PASS" not in result.stdout:
            fail("main_runtime_separation_pass_marker_missing")
    return 18


def configure_appctl_module(module, root: Path, fake_main: str):
    forge = root / "forge"
    logs = root / "logs"
    run = root / "run"
    forge.mkdir(parents=True)
    logs.mkdir()
    run.mkdir()

    main_path = forge / "main.py"
    main_path.write_text(fake_main, encoding="utf-8")

    module.FORGE_ROOT = forge
    module.FORGE_MAIN = main_path
    module.FORGE_VENV_PYTHON = Path(sys.executable)
    module.RUN_ROOT = run
    module.LOG_ROOT = logs
    module.SUPERVISOR_PID = run / "forge_supervisor.pid"
    module.FORGE_CHILD_PID = run / "forge_main.pid"
    module.WINDOW_PID = run / "operator_window.pid"
    module.TERMINUS_WINDOW_PID = run / "terminus_window.pid"
    module.STATE_FILE = run / "state.json"
    module.LOCK_FILE = run / "appctl.lock"
    module.SUPERVISOR_LOG = logs / "forge_supervisor.log"
    module.BUILD_LOG = logs / "react_build.log"
    module.LAUNCHER_LOG = logs / "launcher.log"
    return forge


def test_appctl_single_path(repo: Path) -> int:
    module = load_module(
        "aiweb_test_appctl_single_r2",
        repo / "scripts" / "aiweb_os_appctl.py",
    )
    with tempfile.TemporaryDirectory(prefix="aiweb-appctl-single-r2-") as temp:
        root = Path(temp)
        marker = root / "marker.txt"
        fake_main = textwrap.dedent(
            f"""
            from pathlib import Path
            print("[forge] Session scope set to: /tmp/project", flush=True)
            print("forge> ", end="", flush=True)
            command = input().strip()
            if command == "forge-ui-start":
                Path({str(marker)!r}).write_text(command, encoding="utf-8")
            """
        )
        configure_appctl_module(module, root, fake_main)
        return_code = module.supervise()
        if return_code != 0:
            fail(f"single_path_supervisor_return_code:{return_code}")
        if marker.read_text(encoding="utf-8") != "forge-ui-start":
            fail("single_path_start_command_not_injected")
    return 2


def test_appctl_multiple_path(repo: Path) -> int:
    module = load_module(
        "aiweb_test_appctl_multiple_r2",
        repo / "scripts" / "aiweb_os_appctl.py",
    )
    with tempfile.TemporaryDirectory(prefix="aiweb-appctl-multiple-r2-") as temp:
        root = Path(temp)
        marker = root / "marker.json"
        fake_main = textwrap.dedent(
            f"""
            import json
            from pathlib import Path
            print("[forge] Multiple approved paths.", flush=True)
            print("Choice [1-3]: ", end="", flush=True)
            choice = input().strip()
            print("forge> ", end="", flush=True)
            command = input().strip()
            Path({str(marker)!r}).write_text(
                json.dumps({{"choice": choice, "command": command}}),
                encoding="utf-8",
            )
            """
        )
        configure_appctl_module(module, root, fake_main)
        module.SCOPE_CHOICE = "2"
        return_code = module.supervise()
        if return_code != 0:
            fail(f"multiple_path_supervisor_return_code:{return_code}")
        result = json.loads(marker.read_text(encoding="utf-8"))
        if result != {"choice": "2", "command": "forge-ui-start"}:
            fail(f"multiple_path_injection_mismatch:{result}")
    return 2


def test_appctl_missing_browser(repo: Path) -> int:
    module = load_module(
        "aiweb_test_appctl_browser_r2",
        repo / "scripts" / "aiweb_os_appctl.py",
    )
    messages: list[str] = []
    module.ensure_dirs = lambda: None
    module.find_operator_window_pid = lambda: (None, None)
    module.chrome_bin = lambda: None
    module.command_path = lambda _name: None
    module.log_line = lambda _path, message: messages.append(message)
    result = module.open_operator_window()
    if result != 0:
        fail(f"missing_browser_return_value:{result}")
    if not any("backend remains available" in message for message in messages):
        fail("missing_browser_nonfatal_log_missing")
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    args = parser.parse_args()

    repo = Path(args.repository).resolve()
    python = repo / ".venv" / "bin" / "python"
    if not python.is_file():
        python = Path("/usr/bin/python3")

    checks = 0
    checks += test_static_source(repo)
    checks += test_permissions(repo)
    checks += test_main_runtime_separation(repo, python)
    checks += test_appctl_single_path(repo)
    checks += test_appctl_multiple_path(repo)
    checks += test_appctl_missing_browser(repo)

    print("FORGE WORKSHOP RUNTIME/LAUNCHER R2 BEHAVIOR: PASS")
    print(f"checks_passed={checks}")
    print("llm_calls=0")
    print("simulation_execution=0")
    print("source_runtime_separation=1")
    print("project_source_writes=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

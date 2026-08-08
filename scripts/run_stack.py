#!/usr/bin/env python3
"""Small process supervisor for Makefile-driven local and Pi development."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUN_DIRECTORY = PROJECT_ROOT / ".run"
REGISTRY_FILE = RUN_DIRECTORY / "stack.json"
STATE_DIRECTORY = PROJECT_ROOT / ".state"
RUNTIME_CONFIG_FILE = STATE_DIRECTORY / "backend.toml"


@dataclass(frozen=True, slots=True)
class Service:
    """One managed process in a local stack."""

    name: str
    command: tuple[str, ...]
    working_directory: Path
    marker: str


@dataclass(frozen=True, slots=True)
class ManagedProcess:
    """The recoverable subset of process metadata persisted for `make stop`."""

    name: str
    pid: int
    marker: str


def _service_definitions(mode: str, runtime_python: Path) -> list[Service]:
    backend_command = (
        str(runtime_python),
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    )
    if mode == "dev":
        backend_command += ("--reload",)
        return [
            Service(
                name="api",
                command=backend_command,
                working_directory=PROJECT_ROOT / "src/backend",
                marker="uvicorn main:app",
            ),
            Service(
                name="web",
                command=("npm", "run", "dev", "--", "--host", "0.0.0.0"),
                working_directory=PROJECT_ROOT / "src/frontend",
                marker="npm run dev",
            ),
        ]

    return [
        Service(
            name="api",
            command=backend_command,
            working_directory=PROJECT_ROOT / "src/backend",
            marker="uvicorn main:app",
        ),
        Service(
            name="web",
            command=(
                "npm",
                "run",
                "preview",
                "--",
                "--host",
                "0.0.0.0",
                "--port",
                "5173",
            ),
            working_directory=PROJECT_ROOT / "src/frontend",
            marker="npm run preview",
        ),
        Service(
            name="device",
            command=(str(runtime_python), "agent.py"),
            working_directory=PROJECT_ROOT / "src/raspi",
            marker="agent.py",
        ),
    ]


def _port_is_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(0.25)
        return connection.connect_ex(("127.0.0.1", port)) == 0


def _wait_for_url(url: str, timeout_seconds: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1.0) as response:  # noqa: S310 - local health check
                if 200 <= response.status < 400:
                    return True
        except (URLError, TimeoutError, ConnectionError):
            pass
        time.sleep(0.25)
    return False


def _process_command(pid: int) -> str | None:
    try:
        result = subprocess.run(
            ("ps", "-p", str(pid), "-o", "state=", "-o", "command="),
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    output = result.stdout.strip()
    if not output:
        return None
    state, _, command = output.partition(" ")
    if state.startswith("Z"):
        return None
    return command.strip() or None


def _process_matches(process: ManagedProcess) -> bool:
    command = _process_command(process.pid)
    return command is not None and process.marker in command


def _terminate(process: ManagedProcess) -> None:
    if not _process_matches(process):
        print(f"  {process.name}: not running")
        return

    try:
        process_group = os.getpgid(process.pid)
        os.killpg(process_group, signal.SIGTERM)
    except ProcessLookupError:
        print(f"  {process.name}: already stopped")
        return

    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        if _process_command(process.pid) is None:
            print(f"  {process.name}: stopped")
            return
        time.sleep(0.1)

    try:
        os.killpg(process_group, signal.SIGKILL)
        print(f"  {process.name}: forced to stop after timeout")
    except ProcessLookupError:
        print(f"  {process.name}: stopped")
    except PermissionError:
        print(f"  {process.name}: could not force stop; check process permissions")


def _read_registry() -> tuple[str, int | None, list[ManagedProcess]]:
    if not REGISTRY_FILE.exists():
        return "unknown", None, []
    try:
        payload: dict[str, Any] = json.loads(REGISTRY_FILE.read_text())
        processes = [ManagedProcess(**item) for item in payload.get("processes", [])]
        supervisor_pid = payload.get("supervisor_pid")
        return (
            str(payload.get("mode", "unknown")),
            int(supervisor_pid) if supervisor_pid is not None else None,
            processes,
        )
    except (OSError, ValueError, TypeError):
        return "unknown", None, []


def _write_registry(mode: str, processes: list[ManagedProcess]) -> None:
    RUN_DIRECTORY.mkdir(exist_ok=True)
    payload = {
        "mode": mode,
        "supervisor_pid": os.getpid(),
        "processes": [asdict(process) for process in processes],
    }
    REGISTRY_FILE.write_text(json.dumps(payload, indent=2) + "\n")


def stop_stack() -> int:
    mode, supervisor_pid, processes = _read_registry()
    if not processes:
        print("No Makefile-managed Flight Tracker stack is running.")
        return 0

    print(f"Stopping Flight Tracker {mode} stack...")
    supervisor_command = _process_command(supervisor_pid) if supervisor_pid else None
    if supervisor_pid and supervisor_command and "run_stack.py" in supervisor_command:
        try:
            os.kill(supervisor_pid, signal.SIGTERM)
            deadline = time.monotonic() + 12.0
            while time.monotonic() < deadline:
                if not REGISTRY_FILE.exists() or _process_command(supervisor_pid) is None:
                    print("  stack supervisor: stopped")
                    return 0
                time.sleep(0.1)
        except ProcessLookupError:
            pass

    for process in reversed(processes):
        _terminate(process)
    REGISTRY_FILE.unlink(missing_ok=True)
    return 0


def show_status() -> int:
    mode, _supervisor_pid, processes = _read_registry()
    if not processes:
        print("Flight Tracker stack: stopped")
        return 0

    print(f"Flight Tracker stack: {mode}")
    for process in processes:
        state = "running" if _process_matches(process) else "stopped"
        print(f"  {process.name:<8} {state:<7} pid={process.pid}")
    return 0


def _lan_address() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
            connection.connect(("192.0.2.1", 80))
            return str(connection.getsockname()[0])
    except OSError:
        return "localhost"


def run_stack(mode: str, runtime_python: Path) -> int:
    if not runtime_python.is_absolute():
        runtime_python = PROJECT_ROOT / runtime_python
    runtime_python = Path(os.path.abspath(runtime_python))
    if not runtime_python.is_file():
        print(f"Runtime is missing: {runtime_python}. Run `make install` first.")
        return 1
    occupied = [port for port in (8000, 5173) if _port_is_open(port)]
    if occupied:
        joined = ", ".join(str(port) for port in occupied)
        print(f"Cannot start: port(s) {joined} already in use. Try `make stop`.")
        return 1

    definitions = _service_definitions(mode, runtime_python)
    STATE_DIRECTORY.mkdir(exist_ok=True)
    if not RUNTIME_CONFIG_FILE.exists():
        shutil.copy2(PROJECT_ROOT / "src/backend/config.toml", RUNTIME_CONFIG_FILE)
    children: list[subprocess.Popen[bytes]] = []
    managed: list[ManagedProcess] = []
    stop_requested = False

    def request_stop(_signum: int, _frame: object) -> None:
        nonlocal stop_requested
        stop_requested = True

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    def wait_for_service(url: str, service_name: str) -> None:
        deadline = time.monotonic() + 30.0
        while time.monotonic() < deadline:
            if stop_requested:
                raise RuntimeError("startup cancelled")
            for child, service in zip(children, definitions, strict=False):
                return_code = child.poll()
                if return_code is not None:
                    raise RuntimeError(
                        f"{service.name} exited during startup with status {return_code}"
                    )
            if _wait_for_url(url, 0.5):
                return
        raise RuntimeError(f"{service_name} did not become healthy within 30 seconds")

    try:
        print(f"Starting Flight Tracker {mode} stack...")
        for service in definitions:
            environment = os.environ.copy()
            if service.name == "api":
                environment["FLIGHT_TRACKER_CONFIG_FILE"] = str(RUNTIME_CONFIG_FILE)
            child = subprocess.Popen(
                service.command,
                cwd=service.working_directory,
                env=environment,
                start_new_session=True,
            )
            children.append(child)
            managed.append(
                ManagedProcess(name=service.name, pid=child.pid, marker=service.marker)
            )
            _write_registry(mode, managed)
            print(f"  {service.name}: pid={child.pid}")

        wait_for_service("http://127.0.0.1:8000/api/health", "API")
        wait_for_service("http://127.0.0.1:5173", "web application")

        lan_address = _lan_address()
        print("\nFlight Tracker is ready")
        print("  Web:      http://localhost:5173")
        print("  Setup:    http://localhost:5173/setup")
        print("  API docs: http://localhost:8000/docs")
        if lan_address != "localhost":
            print(f"  Network:  http://{lan_address}:5173")
        print("\nPress Ctrl+C to stop the stack.")

        while not stop_requested:
            for child, service in zip(children, definitions, strict=True):
                return_code = child.poll()
                if return_code is not None:
                    raise RuntimeError(
                        f"{service.name} exited unexpectedly with status {return_code}"
                    )
            time.sleep(0.5)
        return 0
    except RuntimeError as error:
        print(f"\nStartup/runtime error: {error}", file=sys.stderr)
        return 1
    finally:
        for process in reversed(managed):
            _terminate(process)
        REGISTRY_FILE.unlink(missing_ok=True)


def doctor(runtime_python: Path) -> int:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("Python runtime", runtime_python.is_file(), str(runtime_python)))
    checks.append(
        ("Node.js", shutil.which("node") is not None, shutil.which("node") or "missing")
    )
    checks.append(
        ("npm", shutil.which("npm") is not None, shutil.which("npm") or "missing")
    )
    checks.append(
        ("API", _wait_for_url("http://127.0.0.1:8000/api/health", 2.0), "port 8000")
    )
    checks.append(("Web", _wait_for_url("http://127.0.0.1:5173", 2.0), "port 5173"))
    checks.append(
        (
            "Web → API proxy",
            _wait_for_url("http://127.0.0.1:5173/api/health", 2.0),
            "/api/health",
        )
    )

    mode, _supervisor_pid, processes = _read_registry()
    for process in processes:
        checks.append(
            (
                f"Managed {process.name}",
                _process_matches(process),
                f"{mode} pid={process.pid}",
            )
        )

    print("Flight Tracker doctor")
    for name, passed, detail in checks:
        marker = "PASS" if passed else "FAIL"
        print(f"  {marker:<4} {name:<18} {detail}")
    failures = sum(not passed for _, passed, _ in checks)
    if failures:
        print(f"\n{failures} check(s) failed.")
        return 1
    print("\nAll checks passed.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("dev", "pi", "stop", "status", "doctor"))
    parser.add_argument(
        "--python",
        type=Path,
        default=PROJECT_ROOT / ".venv/bin/python",
        help="Python executable used for managed services",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.action == "stop":
        return stop_stack()
    if args.action == "status":
        return show_status()
    if args.action == "doctor":
        return doctor(args.python)
    return run_stack(args.action, args.python)


if __name__ == "__main__":
    raise SystemExit(main())

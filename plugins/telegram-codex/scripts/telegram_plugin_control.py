#!/usr/bin/env python3
"""Start, stop, and inspect the Telegram Codex bridge daemon."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = PLUGIN_ROOT / ".run"
PID_FILE = RUN_DIR / "telegram_codex_bridge.pid"
LOG_FILE = RUN_DIR / "telegram_codex_bridge.log"
BRIDGE = PLUGIN_ROOT / "scripts" / "telegram_codex_bridge.py"


def read_pid() -> int | None:
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def is_running(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def status() -> int:
    pid = read_pid()
    if is_running(pid):
        print(f"Telegram Codex bridge is running. PID: {pid}")
        print(f"Log: {LOG_FILE}")
        return 0
    print("Telegram Codex bridge is stopped.")
    if LOG_FILE.exists():
        print(f"Last log: {LOG_FILE}")
    return 1


def start() -> int:
    pid = read_pid()
    if is_running(pid):
        print(f"Telegram Codex bridge is already running. PID: {pid}")
        return 0

    env_file = PLUGIN_ROOT / ".env"
    if not env_file.exists():
        template = PLUGIN_ROOT / "scripts" / "env.example"
        env_file.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Created {env_file}. Add TELEGRAM_BOT_HTTP_API_TOKEN, then run start again.")
        return 2

    RUN_DIR.mkdir(exist_ok=True)
    log = LOG_FILE.open("a", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, str(BRIDGE)],
        cwd=str(PLUGIN_ROOT),
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    PID_FILE.write_text(str(process.pid), encoding="utf-8")
    time.sleep(1)
    if not is_running(process.pid):
        print(f"Telegram Codex bridge failed to start. See {LOG_FILE}.")
        return 1
    print(f"Telegram Codex bridge started. PID: {process.pid}")
    print(f"Log: {LOG_FILE}")
    return 0


def stop() -> int:
    pid = read_pid()
    if not is_running(pid):
        print("Telegram Codex bridge is already stopped.")
        PID_FILE.unlink(missing_ok=True)
        return 0

    assert pid is not None
    os.kill(pid, signal.SIGTERM)
    for _ in range(30):
        if not is_running(pid):
            PID_FILE.unlink(missing_ok=True)
            print("Telegram Codex bridge stopped.")
            return 0
        time.sleep(0.2)

    os.kill(pid, signal.SIGKILL)
    PID_FILE.unlink(missing_ok=True)
    print("Telegram Codex bridge force-stopped.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "stop", "status"])
    args = parser.parse_args()
    if args.command == "start":
        return start()
    if args.command == "stop":
        return stop()
    return status()


if __name__ == "__main__":
    raise SystemExit(main())


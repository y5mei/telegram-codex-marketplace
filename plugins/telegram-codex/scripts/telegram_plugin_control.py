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
TOKEN_KEYS = ("TELEGRAM_BOT_HTTP_API_TOKEN", "TELEGRAM_BOT_TOKEN")
TOKEN_PLACEHOLDERS = {"", "123456789:replace_me", "your_botfather_token", "the_token_from_botfather"}


def read_pid() -> int | None:
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def process_args(pid: int) -> str | None:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "args="],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def is_running(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def is_bridge_process(pid: int | None) -> bool:
    if not is_running(pid):
        return False
    assert pid is not None
    args = process_args(pid)
    if not args:
        return False
    return str(BRIDGE) in args or "telegram_codex_bridge.py" in args


def clear_stale_pid() -> None:
    pid = read_pid()
    if pid is not None and not is_bridge_process(pid):
        PID_FILE.unlink(missing_ok=True)


def env_has_token(env_file: Path) -> bool:
    if not env_file.exists():
        return False
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        token = value.strip()
        if key.strip() in TOKEN_KEYS and token and token not in TOKEN_PLACEHOLDERS:
            return True
    return False


def status() -> int:
    clear_stale_pid()
    pid = read_pid()
    if is_bridge_process(pid):
        print(f"Telegram Codex bridge is running. PID: {pid}")
        print(f"Log: {LOG_FILE}")
        return 0
    print("Telegram Codex bridge is stopped.")
    if LOG_FILE.exists():
        print(f"Last log: {LOG_FILE}")
    return 1


def start() -> int:
    clear_stale_pid()
    pid = read_pid()
    if is_bridge_process(pid):
        print(f"Telegram Codex bridge is already running. PID: {pid}")
        print(f"Log: {LOG_FILE}")
        return 0

    env_file = PLUGIN_ROOT / ".env"
    if not env_file.exists():
        template = PLUGIN_ROOT / "scripts" / "env.example"
        env_file.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Created {env_file}. Add TELEGRAM_BOT_HTTP_API_TOKEN, then run start again.")
        return 2
    if not env_has_token(env_file):
        print(f"Telegram Codex bridge is not started. Add TELEGRAM_BOT_HTTP_API_TOKEN to {env_file}.")
        return 2

    RUN_DIR.mkdir(exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, str(BRIDGE)],
            cwd=str(PLUGIN_ROOT),
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    PID_FILE.write_text(str(process.pid), encoding="utf-8")
    time.sleep(1)
    if process.poll() is not None or not is_bridge_process(process.pid):
        PID_FILE.unlink(missing_ok=True)
        print(f"Telegram Codex bridge failed to start. See {LOG_FILE}.")
        return 1
    print(f"Telegram Codex bridge started. PID: {process.pid}")
    print(f"Log: {LOG_FILE}")
    return 0


def stop() -> int:
    clear_stale_pid()
    pid = read_pid()
    if not is_bridge_process(pid):
        print("Telegram Codex bridge is already stopped.")
        PID_FILE.unlink(missing_ok=True)
        return 0

    assert pid is not None
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        PID_FILE.unlink(missing_ok=True)
        print("Telegram Codex bridge is already stopped.")
        return 0
    for _ in range(30):
        if not is_bridge_process(pid):
            PID_FILE.unlink(missing_ok=True)
            print("Telegram Codex bridge stopped.")
            return 0
        time.sleep(0.2)

    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
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

#!/usr/bin/env python3
"""Start, stop, inspect, and read logs for the Telegram Codex bridge daemon."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path.home() / ".codex" / "telegram-codex"
ENV_FILE = CONFIG_DIR / ".env"
RUN_DIR = CONFIG_DIR / "run"
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


def read_env() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return values
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def env_token(values: dict[str, str]) -> str:
    for key in TOKEN_KEYS:
        token = values.get(key, "").strip()
        if token and token not in TOKEN_PLACEHOLDERS:
            return token
    return ""


def env_has_token() -> bool:
    return bool(env_token(read_env()))


def ensure_env() -> bool:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if ENV_FILE.exists():
        return False
    template = PLUGIN_ROOT / "scripts" / "env.example"
    ENV_FILE.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    return True


def api_call(token: str, method: str, payload: dict | None = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(payload or {}).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError:
        return curl_api_call(token, method, payload or {})


def curl_api_call(token: str, method: str, payload: dict) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    args = ["curl", "--silent", "--show-error", "--fail", "--max-time", "20", "-X", "POST", url]
    for key, value in payload.items():
        args.extend(["--data-urlencode", f"{key}={value}"])
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        return {"ok": False, "description": result.stderr.strip()}
    return json.loads(result.stdout)


def telegram_diagnostics(values: dict[str, str]) -> tuple[str, str, str]:
    token = env_token(values)
    if not token:
        return "no", "unknown", "unknown"

    me = api_call(token, "getMe")
    if not me.get("ok"):
        return "yes", "no", "unknown"

    username = me.get("result", {}).get("username", "unknown")
    webhook = api_call(token, "getWebhookInfo")
    if webhook.get("ok") and webhook.get("result", {}).get("url"):
        return "yes", f"yes (@{username})", "set"
    if webhook.get("ok"):
        return "yes", f"yes (@{username})", "clear"
    return "yes", f"yes (@{username})", "unknown"


def check_webhook_conflict(values: dict[str, str]) -> bool:
    token = env_token(values)
    if not token:
        return False
    webhook = api_call(token, "getWebhookInfo")
    return bool(webhook.get("ok") and webhook.get("result", {}).get("url"))


def print_status_details(running: bool) -> int:
    values = read_env()
    token_configured, api_reachable, webhook = telegram_diagnostics(values)
    allowed = "yes" if values.get("TELEGRAM_ALLOWED_CHAT_IDS", "").strip() else "no"
    watchdog = values.get("CODEX_WATCHDOG_ENABLED", "true") or "true"
    interval = values.get("CODEX_WATCHDOG_INTERVAL_SECONDS", "300") or "300"

    if running:
        pid = read_pid()
        print(f"Bridge: running (PID {pid})")
    else:
        print("Bridge: stopped")
    print(f"Config: {ENV_FILE}")
    print(f"Token configured: {token_configured}")
    print(f"Telegram API: {api_reachable}")
    print(f"Webhook: {webhook}")
    print(f"Allowed chat: {allowed}")
    print(f"Watchdog: {watchdog} ({interval}s)")
    print(f"Log: {LOG_FILE}")
    return 0 if running else 1


def status() -> int:
    clear_stale_pid()
    return print_status_details(is_bridge_process(read_pid()))


def start() -> int:
    clear_stale_pid()
    pid = read_pid()
    if is_bridge_process(pid):
        print(f"Telegram Codex bridge is already running. PID: {pid}")
        print(f"Log: {LOG_FILE}")
        return 0

    if ensure_env():
        print(f"Created config: {ENV_FILE}")
        print("Add TELEGRAM_BOT_HTTP_API_TOKEN, then run telegram-codex:start again.")
        return 2
    values = read_env()
    if not env_token(values):
        print(f"Add TELEGRAM_BOT_HTTP_API_TOKEN to {ENV_FILE}, then run telegram-codex:start again.")
        return 2
    if check_webhook_conflict(values):
        print("Telegram webhook is set. Clear it before using this long-polling bridge.")
        print("In Telegram Bot API, call deleteWebhook, then run telegram-codex:start again.")
        return 2

    RUN_DIR.mkdir(parents=True, exist_ok=True)
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


def logs(lines: int) -> int:
    if not LOG_FILE.exists():
        print(f"No log file yet: {LOG_FILE}")
        return 1
    content = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in content[-lines:]:
        print(line)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "stop", "status", "logs"])
    parser.add_argument("--lines", type=int, default=20)
    args = parser.parse_args()
    if args.command == "start":
        return start()
    if args.command == "stop":
        return stop()
    if args.command == "logs":
        return logs(max(1, args.lines))
    return status()


if __name__ == "__main__":
    raise SystemExit(main())

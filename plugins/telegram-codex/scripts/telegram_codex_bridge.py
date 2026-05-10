#!/usr/bin/env python3
"""Telegram long-polling bridge for local Codex CLI replies."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


TELEGRAM_LIMIT = 3900
ENV_PATH = Path(".env")
WELCOME_MESSAGE = "Hello world from Codex Telegram plugin."
OFFLINE_MESSAGE = (
    "Telegram Codex bridge is not running. In Codex, select telegram-codex:start "
    "or reopen Codex and ask it to start the Telegram plugin."
)
CODEX_WATCHDOG_ENABLED = "CODEX_WATCHDOG_ENABLED"
CODEX_WATCHDOG_INTERVAL_SECONDS = "CODEX_WATCHDOG_INTERVAL_SECONDS"
CODEX_WATCHDOG_PATTERNS = "CODEX_WATCHDOG_PATTERNS"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def telegram_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_HTTP_API_TOKEN", "").strip()
    if token:
        return token
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if token:
        return token
    raise SystemExit("Missing required environment variable: TELEGRAM_BOT_HTTP_API_TOKEN")


def save_allowed_chat_id(env_path: Path, chat_id: int) -> None:
    key = "TELEGRAM_ALLOWED_CHAT_IDS"
    lines = []
    found = False
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    for index, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[index] = f"{key}={chat_id}"
            found = True
            break

    if not found:
        lines.append(f"{key}={chat_id}")

    env_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    os.environ[key] = str(chat_id)


def api_call(token: str, method: str, payload: dict) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError:
        return curl_api_call(token, method, payload)
    return json.loads(body)


def curl_api_call(token: str, method: str, payload: dict) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    args = ["curl", "--silent", "--show-error", "--fail", "--max-time", "90", "-X", "POST", url]
    for key, value in payload.items():
        args.extend(["--data-urlencode", f"{key}={value}"])
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Telegram curl failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def send_message(token: str, chat_id: int, text: str) -> None:
    chunks = [text[i : i + TELEGRAM_LIMIT] for i in range(0, len(text), TELEGRAM_LIMIT)]
    for chunk in chunks or [""]:
        api_call(
            token,
            "sendMessage",
            {
                "chat_id": str(chat_id),
                "text": chunk,
                "disable_web_page_preview": "true",
            },
        )


def allowed_chat_ids() -> set[int]:
    raw = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").strip()
    if not raw:
        return set()
    return {int(part.strip()) for part in raw.split(",") if part.strip()}


def build_codex_command() -> list[str]:
    codex_bin = os.environ.get("CODEX_BIN", "codex")
    workdir = os.environ.get("CODEX_WORKDIR", os.getcwd())
    sandbox = os.environ.get("CODEX_SANDBOX", "workspace-write")
    model = os.environ.get("CODEX_MODEL", "").strip()

    cmd = [
        codex_bin,
        "exec",
        "--cd",
        workdir,
        "--sandbox",
        sandbox,
        "--skip-git-repo-check",
    ]
    if model:
        cmd.extend(["--model", model])
    cmd.append("-")
    return cmd


def run_codex(prompt: str) -> str:
    timeout = int(os.environ.get("CODEX_TIMEOUT_SECONDS", "600"))
    system_hint = (
        "You are replying to the user through Telegram. Keep the answer concise "
        "unless the user asks for detail. Do not mention Telegram unless relevant.\n\n"
    )
    with tempfile.NamedTemporaryFile("r+", encoding="utf-8", delete=True) as final_message:
        cmd = build_codex_command()
        cmd[2:2] = ["--output-last-message", final_message.name]
        result = subprocess.run(
            cmd,
            input=system_hint + prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        final_message.seek(0)
        output = final_message.read().strip()
    if result.returncode != 0:
        cli_output = result.stdout.strip()
        return f"Codex exited with status {result.returncode}.\n\n{cli_output[-1200:]}"
    return output or "Codex finished without a text reply."


def should_stop(text: str) -> bool:
    return text.strip().lower() in {"/stop", "/offline", "/pause"}


def bool_env(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw not in {"0", "false", "no", "off"}


def codex_process_patterns() -> list[str]:
    raw = os.environ.get(CODEX_WATCHDOG_PATTERNS, "").strip()
    if raw:
        return [part.strip().lower() for part in raw.split(",") if part.strip()]
    return [
        "/applications/codex.app/contents/macos/codex",
        "/applications/codex.app/contents/resources/codex app-server",
        "codex app-server",
    ]


def codex_is_alive() -> bool:
    result = subprocess.run(
        ["ps", "-axo", "pid,args"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return True

    self_pid = os.getpid()
    parent_pid = os.getppid()
    patterns = codex_process_patterns()
    for line in result.stdout.splitlines()[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        pid_text, _, args = stripped.partition(" ")
        try:
            pid = int(pid_text)
        except ValueError:
            continue
        if pid in {self_pid, parent_pid}:
            continue
        lowered = args.lower()
        if "telegram_codex_bridge.py" in lowered or "telegram_plugin_control.py" in lowered:
            continue
        if any(pattern in lowered for pattern in patterns):
            return True
    return False


def watchdog_interval_seconds() -> int:
    raw = os.environ.get(CODEX_WATCHDOG_INTERVAL_SECONDS, "300").strip()
    try:
        return max(30, int(raw))
    except ValueError:
        return 300


def extract_message(update: dict) -> tuple[int, str] | None:
    message = update.get("message") or update.get("edited_message")
    if not message:
        return None
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text")
    if chat_id is None or not text:
        return None
    return int(chat_id), text


def main() -> int:
    load_dotenv(ENV_PATH)
    token = telegram_token()
    allowlist = allowed_chat_ids()

    print("Telegram Codex bridge is running.", flush=True)
    if not allowlist:
        print("No TELEGRAM_ALLOWED_CHAT_IDS set. First incoming chat will be allowed.", flush=True)

    offset = None
    watchdog_enabled = bool_env(CODEX_WATCHDOG_ENABLED, True)
    watchdog_interval = watchdog_interval_seconds()
    next_watchdog_check = time.monotonic() + watchdog_interval
    while True:
        if watchdog_enabled and time.monotonic() >= next_watchdog_check:
            if not codex_is_alive():
                print("Codex is not running; Telegram Codex bridge is exiting.", flush=True)
                return 0
            next_watchdog_check = time.monotonic() + watchdog_interval

        payload = {"timeout": "60", "allowed_updates": json.dumps(["message", "edited_message"])}
        if offset is not None:
            payload["offset"] = str(offset)
        try:
            response = api_call(token, "getUpdates", payload)
            for update in response.get("result", []):
                offset = update["update_id"] + 1
                extracted = extract_message(update)
                if not extracted:
                    continue
                chat_id, text = extracted

                if not allowlist:
                    save_allowed_chat_id(ENV_PATH, chat_id)
                    allowlist = {chat_id}
                    send_message(token, chat_id, WELCOME_MESSAGE)
                    continue

                if chat_id not in allowlist:
                    send_message(token, chat_id, "This chat is not authorized for this bot.")
                    continue

                if should_stop(text):
                    send_message(token, chat_id, OFFLINE_MESSAGE)
                    return 0

                print(f"Running Codex for chat {chat_id}: {shlex.quote(text[:80])}", flush=True)
                send_message(token, chat_id, "Working on it...")
                reply = run_codex(text)
                send_message(token, chat_id, reply)
        except subprocess.TimeoutExpired:
            print("Codex request timed out.", file=sys.stderr, flush=True)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr, flush=True)
            time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())

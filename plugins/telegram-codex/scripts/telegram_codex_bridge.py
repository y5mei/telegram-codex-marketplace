#!/usr/bin/env python3
"""Telegram long-polling bridge for local Codex CLI replies."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


TELEGRAM_LIMIT = 3900


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
    return json.loads(body)


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
        "--ask-for-approval",
        "never",
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
    result = subprocess.run(
        build_codex_command(),
        input=system_hint + prompt,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )
    output = result.stdout.strip()
    if result.returncode != 0:
        return f"Codex exited with status {result.returncode}.\n\n{output[-3000:]}"
    return output or "Codex finished without a text reply."


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
    load_dotenv(Path(".env"))
    token = required_env("TELEGRAM_BOT_TOKEN")
    allowlist = allowed_chat_ids()

    print("Telegram Codex bridge is running.", flush=True)
    if not allowlist:
        print("No TELEGRAM_ALLOWED_CHAT_IDS set. Setup mode is active.", flush=True)

    offset = None
    while True:
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
                    send_message(
                        token,
                        chat_id,
                        f"Setup mode: your chat ID is {chat_id}. Add it to TELEGRAM_ALLOWED_CHAT_IDS.",
                    )
                    continue

                if chat_id not in allowlist:
                    send_message(token, chat_id, "This chat is not authorized for this bot.")
                    continue

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


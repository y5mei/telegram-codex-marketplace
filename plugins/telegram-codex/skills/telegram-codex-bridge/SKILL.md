---
name: telegram-codex-bridge
description: Set up and run a local Telegram Bot API bridge that forwards allowlisted Telegram messages to Codex CLI and sends replies back to Telegram.
---

# Telegram Codex Bridge

Use this skill when the user wants to chat with Codex through Telegram, configure the Telegram bridge, run it locally, or harden its security settings.

## What This Plugin Provides

- A long-polling Telegram bot service in `../../scripts/telegram_codex_bridge.py`.
- An environment template in `../../scripts/env.example`.
- A Codex CLI subprocess bridge using `codex exec`.
- A required Telegram chat allowlist.

## Setup Workflow

1. Resolve the plugin root from this skill directory: `../..`.
2. Copy `scripts/env.example` to `.env` in the plugin root if `.env` does not exist.
3. Ask the user to put their Telegram bot token in `.env` as `TELEGRAM_BOT_HTTP_API_TOKEN`.
4. Start the bridge with:

   ```sh
   cd <plugin-root>
   python3 scripts/telegram_codex_bridge.py
   ```

5. Tell the user to message the Telegram bot.
6. The first chat to message the bot is written to `.env` as `TELEGRAM_ALLOWED_CHAT_IDS`.

## Security Guidance

- Prefer `CODEX_SANDBOX=workspace-write` for normal use.
- Use `CODEX_SANDBOX=read-only` for Q&A-only bots.
- Use `CODEX_SANDBOX=danger-full-access` only when the user explicitly wants Telegram to drive broad local filesystem work.
- On first run, the bridge automatically writes the first incoming chat to `TELEGRAM_ALLOWED_CHAT_IDS`.
- For shared bot tokens, pre-fill `TELEGRAM_ALLOWED_CHAT_IDS` before starting the bridge.
- Do not ask the user to paste their bot token into chat; have them edit `.env` locally.

## Operation

Run:

```sh
cd <plugin-root>
python3 scripts/telegram_codex_bridge.py
```

The terminal must stay open while the user wants the bridge online.

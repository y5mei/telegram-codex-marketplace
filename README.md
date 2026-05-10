# Telegram Codex Marketplace

This repository is a Codex plugin marketplace containing `telegram-codex`, a local bridge that lets you send messages to Codex from Telegram and receive replies back in Telegram.

## Install

```sh
codex plugin marketplace add y5mei/telegram-codex-marketplace
```

After installing the marketplace, enable the `telegram-codex` plugin in Codex.

## Configure

Each user needs their own Telegram bot token from Telegram's `@BotFather`.

```sh
cd ~/.codex
```

Find the installed plugin directory, then copy the env template:

```sh
cp scripts/env.example .env
```

Set:

```sh
TELEGRAM_BOT_HTTP_API_TOKEN=your_bot_token
```

Start the bridge once, then message your Telegram bot. The first chat to message the bot is automatically written into `.env` as `TELEGRAM_ALLOWED_CHAT_IDS`.

## Run

```sh
python3 scripts/telegram_codex_bridge.py
```

Keep the terminal open while you want the bridge online.

## Security

- Never share or commit your Telegram bot token.
- The first chat to message a fresh bot claims the bridge and is saved to `TELEGRAM_ALLOWED_CHAT_IDS`.
- If the bot token was ever shared, pre-fill `TELEGRAM_ALLOWED_CHAT_IDS` before running the bridge.
- Use `CODEX_SANDBOX=read-only` for Q&A only.
- Use `CODEX_SANDBOX=workspace-write` for local workspace edits.
- Use `CODEX_SANDBOX=danger-full-access` only when you intentionally want Telegram prompts to drive broad local filesystem actions.

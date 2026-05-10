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
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ALLOWED_CHAT_IDS=
```

Start the bridge once, message your Telegram bot, then copy the chat ID it returns into `TELEGRAM_ALLOWED_CHAT_IDS`.

## Run

```sh
python3 scripts/telegram_codex_bridge.py
```

Keep the terminal open while you want the bridge online.

## Security

- Never share or commit your Telegram bot token.
- Keep `TELEGRAM_ALLOWED_CHAT_IDS` set before normal use.
- Use `CODEX_SANDBOX=read-only` for Q&A only.
- Use `CODEX_SANDBOX=workspace-write` for local workspace edits.
- Use `CODEX_SANDBOX=danger-full-access` only when you intentionally want Telegram prompts to drive broad local filesystem actions.


# Telegram Codex Plugin

This plugin packages a local bridge between Telegram Bot API and Codex CLI.

The bridge uses Telegram long polling, so it does not need a public webhook URL. Incoming text messages from allowlisted Telegram chats are passed to `codex exec`; the final Codex response is sent back to the same Telegram chat.

## Files

- `skills/telegram-codex-bridge/SKILL.md`: Codex-facing instructions for setup and operation.
- `scripts/telegram_codex_bridge.py`: The long-polling bridge service.
- `scripts/env.example`: Environment variable template.

## Quick Start

```sh
cd plugins/telegram-codex
cp scripts/env.example .env
python3 scripts/telegram_codex_bridge.py
```

On first run, set only `TELEGRAM_BOT_HTTP_API_TOKEN`, then send a message to your bot. The first chat to message the bot is written into `.env` as `TELEGRAM_ALLOWED_CHAT_IDS`.

## Security

Keep `CODEX_SANDBOX=workspace-write` or `CODEX_SANDBOX=read-only` unless you intentionally want Telegram prompts to drive broad local filesystem actions.

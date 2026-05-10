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

On first run, leave `TELEGRAM_ALLOWED_CHAT_IDS` empty, send a message to your bot, copy the chat ID from the reply into `.env`, then restart the bridge.

## Security

Keep `CODEX_SANDBOX=workspace-write` or `CODEX_SANDBOX=read-only` unless you intentionally want Telegram prompts to drive broad local filesystem actions.


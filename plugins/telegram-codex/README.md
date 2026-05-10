# Telegram Codex Plugin

This plugin packages a local bridge between Telegram Bot API and Codex CLI.

This README is for Codex agents helping a user set up the bridge. Stay with the user through bot creation, token placement, bridge startup, and the first message test.

## User Copy-Paste Prompt

Tell users to send this to Codex:

```text
Please read this link and install the Telegram Codex plugin, then guide me through setup: https://github.com/y5mei/telegram-codex-marketplace
```

## What The Bridge Does

The bridge uses Telegram long polling, so it does not need a public webhook URL. Incoming text messages from the user's allowed Telegram chat are passed to `codex exec`; the final Codex response is sent back to the same Telegram chat.

## Files

- `skills/telegram-codex-bridge/SKILL.md`: Codex-facing setup and operation instructions.
- `scripts/telegram_codex_bridge.py`: The long-polling bridge service.
- `scripts/env.example`: Environment variable template.

## Agent Setup Flow

1. Resolve the plugin root.
2. Ask the user to install or open Telegram.
3. Ask the user to open `@BotFather`.
4. Ask the user to send `/newbot`.
5. Have the user follow BotFather's prompts for bot display name and username.
6. BotFather will provide an HTTP API token. Tell the user it is secret.
7. Copy `scripts/env.example` to `.env`.
8. Help the user put the token into `.env`:

   ```env
   TELEGRAM_BOT_HTTP_API_TOKEN=the_token_from_botfather
   ```

9. Start the bridge:

   ```sh
   python3 scripts/telegram_codex_bridge.py
   ```

10. Ask the user to message their new Telegram bot.
11. Confirm the first message causes the bridge to write `TELEGRAM_ALLOWED_CHAT_IDS` into `.env` and reply `Hello world from Codex Telegram plugin.`
12. Ask the user to send a second message and verify that Codex replies.

## Security

Keep `CODEX_SANDBOX=workspace-write` or `CODEX_SANDBOX=read-only` unless the user intentionally wants Telegram prompts to drive broad local filesystem actions.

Do not commit `.env` or any Telegram token.

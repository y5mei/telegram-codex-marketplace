---
name: telegram-codex-bridge
description: Set up and run a local Telegram Bot API bridge that forwards allowlisted Telegram messages to Codex CLI and sends replies back to Telegram.
---

# Telegram Codex Bridge

Use this skill to set up Telegram Codex. Keep user-facing output short.

## Setup

1. Install or upgrade marketplace if needed:

   ```sh
   codex plugin marketplace add y5mei/telegram-codex-marketplace
   codex plugin marketplace upgrade telegram-codex-marketplace
   ```

2. Find plugin root:

   ```sh
   find ~/.codex -path '*/plugins/telegram-codex' -type d 2>/dev/null
   ```

3. Create `.env` if missing:

   ```sh
   cp -n scripts/env.example .env
   ```

4. Ask user to get the Telegram token:

   ```text
   Open Telegram, chat with @BotFather, send /newbot, choose a bot name and a username ending in bot, then copy the HTTP API token.
   ```

5. Help user put it in `.env`:

   ```env
   TELEGRAM_BOT_HTTP_API_TOKEN=the_token_from_botfather
   ```

6. Tell user to restart Codex so skills refresh.

7. Show controls:

   ```text
   telegram-codex:start
   telegram-codex:stop
   telegram-codex:status
   ```

8. Mention once: the bridge checks every 5 minutes whether Codex is still running and exits automatically if Codex is gone.

## First Test

After restart, tell the user to select `telegram-codex:start`, then message the Telegram bot.

Expected first Telegram reply:

```text
Hello world from Codex Telegram plugin.
```

## Guardrails

- Do not print the token.
- Do not over-explain.
- Prefer editing `.env` locally over asking the user to paste secrets into chat.
- Use `telegram-codex:start`, `telegram-codex:stop`, and `telegram-codex:status` instead of slash commands.

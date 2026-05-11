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

3. Create stable `.env` if missing:

   ```sh
   mkdir -p ~/.codex/telegram-codex
   cp -n scripts/env.example ~/.codex/telegram-codex/.env
   ```

4. Ask user to get the Telegram token:

   ```text
   Open Telegram, chat with @BotFather, send /newbot, choose a bot name and a username ending in bot, then copy the HTTP API token.
   ```

5. Help user put it in `.env`:

   ```env
   TELEGRAM_BOT_HTTP_API_TOKEN=the_token_from_botfather
   ```

6. Stop here. Ask the user to type `done` after they have updated `~/.codex/telegram-codex/.env`.

7. After the user types `done`, verify quietly that the token exists and looks valid.
   If it does not, ask the user to fix only the token and type `done` again.

8. Only after the token is verified, tell the user to restart Codex so skills refresh.

9. Show controls:

   ```text
   telegram-codex:start
   telegram-codex:stop
   telegram-codex:status
   telegram-codex:logs
   ```

10. Mention once: the bridge checks every 5 minutes whether Codex is still running and exits automatically if Codex is gone.
11. Mention once: Telegram messages are sent to local Codex and may trigger local file actions depending on `CODEX_SANDBOX`.

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
- Telegram replies must use Bot API HTML parse mode, not Markdown.
- Use only supported HTML tags such as `<b>`, `<i>`, `<u>`, `<s>`, `<a href="...">`, `<code>`, and `<pre>`.
- Escape literal `<`, `>`, and `&` in Telegram replies.
- Use `telegram-codex:start`, `telegram-codex:stop`, `telegram-codex:status`, and `telegram-codex:logs` instead of slash commands.

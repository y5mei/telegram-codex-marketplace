# Telegram Codex Plugin

For Codex agents: keep setup concise.

## Minimal Setup

1. Find plugin root:

   ```sh
   find ~/.codex -path '*/plugins/telegram-codex' -type d 2>/dev/null
   ```

2. Create stable `.env` if missing:

   ```sh
   mkdir -p ~/.codex/telegram-codex
   cp -n scripts/env.example ~/.codex/telegram-codex/.env
   ```

3. Ask user to get the token:

   ```text
   Open Telegram, chat with @BotFather, send /newbot, choose a bot name and a username ending in bot, then copy the HTTP API token.
   ```

4. Help user put it in `.env`:

   ```env
   TELEGRAM_BOT_HTTP_API_TOKEN=the_token_from_botfather
   ```

5. Ask user to restart Codex.

6. Show commands:

   ```text
   telegram-codex:start
   telegram-codex:stop
   telegram-codex:status
   telegram-codex:logs
   ```

The bridge auto-exits if Codex is gone for the 5-minute watchdog check.

Privacy note: Telegram messages are sent to local Codex and may trigger local file actions depending on `CODEX_SANDBOX`.

## Reply Formatting

Telegram replies use Bot API HTML parse mode, not Markdown. Use only supported tags such as `<b>`, `<i>`, `<u>`, `<s>`, `<a href="...">`, `<code>`, and `<pre>`. Escape literal `<`, `>`, and `&`.

## Test

After restart, ask user to select `telegram-codex:start`, then message the Telegram bot.

Expected first reply:

```text
Hello world from Codex Telegram plugin.
```

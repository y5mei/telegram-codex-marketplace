---
description: Start the Telegram Codex bridge in the background and show the user how to test it.
---

# /telegram-plugin-start

Start the long-running Telegram Codex bridge.

## Workflow

1. Resolve the plugin root by searching:

   ```sh
   find ~/.codex -path '*/plugins/telegram-codex' -type d 2>/dev/null
   ```

2. From the plugin root, run:

   ```sh
   python3 scripts/telegram_plugin_control.py start
   ```

3. If config was created and the command asks for `TELEGRAM_BOT_HTTP_API_TOKEN`, guide the user through `@BotFather` setup from the README, have them add the token to `~/.codex/telegram-codex/.env`, then run the start command again.
4. Tell the user to send a Telegram message to the bot.
5. On first claim, expect:

   ```text
   Hello world from Codex Telegram plugin.
   ```

6. Ask the user to send a second message to verify Codex replies.

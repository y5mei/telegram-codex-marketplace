---
name: start
description: Start the Telegram Codex bridge background process for the installed telegram-codex plugin.
---

# Start Telegram Codex

Use this skill when the user selects `telegram-codex:start` or asks to start the Telegram Codex bridge.

## Workflow

1. Resolve the plugin root from this skill directory: `../..`.
2. If `.env` does not exist in the plugin root, copy `scripts/env.example` to `.env` and ask the user to add `TELEGRAM_BOT_HTTP_API_TOKEN`.
3. Check whether `TELEGRAM_BOT_HTTP_API_TOKEN` is set without printing it.
4. Start the bridge:

   ```sh
   cd <plugin-root>
   python3 scripts/telegram_plugin_control.py start
   ```

5. If this is the first run, ask the user to send a message to their Telegram bot and expect:

   ```text
   Hello world from Codex Telegram plugin.
   ```

6. Ask the user to send a second message and verify Codex replies.

## Reply Formatting

When replying through Telegram, use Telegram Bot API HTML formatting, not Markdown. Use only supported tags such as `<b>`, `<i>`, `<u>`, `<s>`, `<a href="...">`, `<code>`, and `<pre>`.

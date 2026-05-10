---
name: stop
description: Stop the Telegram Codex bridge background process for the installed telegram-codex plugin.
---

# Stop Telegram Codex

Use this skill when the user selects `telegram-codex:stop` or asks to stop the Telegram Codex bridge.

## Workflow

1. Resolve the plugin root from this skill directory: `../..`.
2. Stop the bridge:

   ```sh
   cd <plugin-root>
   python3 scripts/telegram_plugin_control.py stop
   ```

3. Tell the user the bridge is stopped. Telegram messages will not be handled until they select `telegram-codex:start` or ask Codex to start the bridge again.

## Reply Formatting

When replying through Telegram, use Telegram Bot API HTML formatting, not Markdown.

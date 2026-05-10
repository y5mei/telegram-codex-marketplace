---
name: status
description: Check whether the Telegram Codex bridge background process is running.
---

# Telegram Codex Status

Use this skill when the user selects `telegram-codex:status` or asks whether the Telegram Codex bridge is running.

## Workflow

1. Resolve the plugin root from this skill directory: `../..`.
2. Check bridge status:

   ```sh
   cd <plugin-root>
   python3 scripts/telegram_plugin_control.py status
   ```

3. If stopped, offer to start it with `telegram-codex:start`.


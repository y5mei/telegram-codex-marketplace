---
name: logs
description: Show recent Telegram Codex bridge logs.
---

# Telegram Codex Logs

Use this skill when the user selects `telegram-codex:logs` or asks for Telegram Codex bridge logs.

## Workflow

1. Resolve plugin root from this skill directory: `../..`.
2. Show recent logs:

   ```sh
   cd <plugin-root>
   python3 scripts/telegram_plugin_control.py logs --lines 20
   ```

3. Keep the summary short and avoid printing secrets.

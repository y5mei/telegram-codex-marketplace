---
description: Show recent Telegram Codex bridge logs.
---

# /telegram-plugin-logs

Show recent Telegram Codex bridge logs.

## Workflow

1. Resolve the plugin root by searching:

   ```sh
   find ~/.codex -path '*/plugins/telegram-codex' -type d 2>/dev/null
   ```

2. From the plugin root, run:

   ```sh
   python3 scripts/telegram_plugin_control.py logs --lines 20
   ```

3. Keep the summary short and avoid printing secrets.


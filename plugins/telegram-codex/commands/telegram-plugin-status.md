---
description: Check whether the Telegram Codex bridge is running.
---

# /telegram-plugin-status

Check the long-running Telegram Codex bridge status.

## Workflow

1. Resolve the plugin root by searching:

   ```sh
   find ~/.codex -path '*/plugins/telegram-codex' -type d 2>/dev/null
   ```

2. From the plugin root, run:

   ```sh
   python3 scripts/telegram_plugin_control.py status
   ```

3. If stopped, offer to run `/telegram-plugin-start`.


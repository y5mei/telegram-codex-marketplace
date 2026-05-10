---
description: Stop the background Telegram Codex bridge.
---

# /telegram-plugin-stop

Stop the long-running Telegram Codex bridge.

## Workflow

1. Resolve the plugin root by searching:

   ```sh
   find ~/.codex -path '*/plugins/telegram-codex' -type d 2>/dev/null
   ```

2. From the plugin root, run:

   ```sh
   python3 scripts/telegram_plugin_control.py stop
   ```

3. Tell the user that Telegram messages will not be handled while the bridge is stopped. To start again, use `/telegram-plugin-start`.


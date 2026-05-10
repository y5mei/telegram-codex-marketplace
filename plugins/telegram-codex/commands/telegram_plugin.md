---
description: Start, stop, or inspect the Telegram Codex bridge. Usage: /telegram_plugin start|stop|status
---

# /telegram_plugin

Manage the long-running Telegram Codex bridge.

## Arguments

- `action`: `start`, `stop`, or `status`

## Workflow

1. Resolve the plugin root by searching:

   ```sh
   find ~/.codex -path '*/plugins/telegram-codex' -type d 2>/dev/null
   ```

2. If the user wrote `/telegram_plugin start`, run from the plugin root:

   ```sh
   python3 scripts/telegram_plugin_control.py start
   ```

3. If the user wrote `/telegram_plugin stop`, run from the plugin root:

   ```sh
   python3 scripts/telegram_plugin_control.py stop
   ```

4. If the user wrote `/telegram_plugin status`, run from the plugin root:

   ```sh
   python3 scripts/telegram_plugin_control.py status
   ```

5. If no action is provided, show the three supported actions and recommend `/telegram_plugin status`.


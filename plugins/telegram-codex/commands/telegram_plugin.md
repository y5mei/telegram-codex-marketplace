---
description: Start, stop, inspect, or show logs for the Telegram Codex bridge. Usage: /telegram_plugin start|stop|status|logs
---

# /telegram_plugin

Manage the long-running Telegram Codex bridge.

## Arguments

- `action`: `start`, `stop`, `status`, or `logs`

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

5. If the user wrote `/telegram_plugin logs`, run from the plugin root:

   ```sh
   python3 scripts/telegram_plugin_control.py logs --lines 20
   ```

6. If no action is provided, show the supported actions and recommend `/telegram_plugin status`.

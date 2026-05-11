# Telegram Codex Marketplace

This README is for Codex agents. Keep user-facing messages short. Do the setup; do not narrate every command.

## User Prompt

Tell users to send this to Codex:

```text
Please read this link and install the Telegram Codex plugin, then guide me through setup: https://github.com/y5mei/telegram-codex-marketplace
```

## Agent Setup

1. Install or upgrade the marketplace:

   ```sh
   codex plugin marketplace add y5mei/telegram-codex-marketplace
   ```

   If already installed:

   ```sh
   codex plugin marketplace upgrade telegram-codex-marketplace
   ```

2. Ensure the plugin is enabled in `~/.codex/config.toml`:

   ```toml
   [plugins."telegram-codex@telegram-codex-marketplace"]
   enabled = true
   ```

3. Find the installed plugin root:

   ```sh
   find ~/.codex -path '*/plugins/telegram-codex' -type d 2>/dev/null
   ```

4. Create stable `.env` if missing:

   ```sh
   mkdir -p ~/.codex/telegram-codex
   cp -n scripts/env.example ~/.codex/telegram-codex/.env
   ```

5. Ask the user to get a Telegram HTTP API token:

   ```text
   Open Telegram, chat with @BotFather, send /newbot, choose a bot name and a username ending in bot, then copy the HTTP API token.
   ```

6. Help the user put the token in `~/.codex/telegram-codex/.env`:

   ```env
   TELEGRAM_BOT_HTTP_API_TOKEN=the_token_from_botfather
   ```

7. Stop here.
   Ask the user to type `done` after they have put the token in `~/.codex/telegram-codex/.env`.

8. After the user types `done`, verify quietly that `TELEGRAM_BOT_HTTP_API_TOKEN` exists and looks valid.
   If it is missing or malformed, ask the user to fix only that and type `done` again.

9. Only after the token is verified, tell the user to restart Codex so plugin skills refresh.

10. After restart, show only these controls:

   ```text
   telegram-codex:start
   telegram-codex:stop
   telegram-codex:status
   telegram-codex:logs
   ```

11. Mention the watchdog once:

   ```text
   The bridge checks every 5 minutes whether Codex is still running and exits automatically if Codex is gone.
   ```

12. Mention privacy once:

   ```text
   Telegram messages will be sent to local Codex and may trigger local file actions depending on the configured sandbox.
   ```

## First Test

After restart and after the user has selected `telegram-codex:start`, ask them to message their Telegram bot.

Expected first Telegram reply:

```text
Hello world from Codex Telegram plugin.
```

Then ask them to send one normal message to confirm Codex replies.

## Agent Style

- Print only necessary next steps.
- Do not show long explanations unless the user asks.
- Do not print the Telegram token.
- Do not ask the user to paste the token into chat unless they explicitly want Codex to edit `.env`.
- Telegram replies must use Telegram Bot API HTML formatting, not Markdown.
- Supported HTML includes `<b>`, `<i>`, `<u>`, `<s>`, `<a href="...">`, `<code>`, and `<pre>`.
- Escape literal `<`, `>`, and `&` in Telegram replies.
- If config is missing, recreate `~/.codex/telegram-codex/.env` from `scripts/env.example`.
- If the bridge is stopped, use `telegram-codex:start`.

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

4. Create `.env` if missing:

   ```sh
   cp -n scripts/env.example .env
   ```

5. Ask the user to get a Telegram HTTP API token:

   ```text
   Open Telegram, chat with @BotFather, send /newbot, choose a bot name and a username ending in bot, then copy the HTTP API token.
   ```

6. Help the user put the token in `.env`:

   ```env
   TELEGRAM_BOT_HTTP_API_TOKEN=the_token_from_botfather
   ```

7. Tell the user to restart Codex so plugin skills refresh.

8. Show only these controls:

   ```text
   telegram-codex:start
   telegram-codex:stop
   telegram-codex:status
   ```

9. Mention the watchdog once:

   ```text
   The bridge checks every 5 minutes whether Codex is still running and exits automatically if Codex is gone.
   ```

## First Test

After restart, ask the user to select `telegram-codex:start`, then message their Telegram bot.

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
- If `.env` is missing, recreate it from `scripts/env.example`.
- If the bridge is stopped, use `telegram-codex:start`.

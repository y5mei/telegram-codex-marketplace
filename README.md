# Telegram Codex Marketplace

This repository is a Codex plugin marketplace containing `telegram-codex`, a local bridge that lets a user send messages to Codex from Telegram and receive replies back in Telegram.

This README is written for Codex agents. When a user asks to use this plugin, do not only point them at these instructions. Help them complete the setup.

## Agent Goal

Guide the user through:

1. Installing this Codex plugin marketplace.
2. Creating a Telegram bot with `@BotFather`.
3. Getting the bot HTTP API token.
4. Putting that token into the plugin `.env` file.
5. Starting the local bridge.
6. Testing the first Telegram message so the bridge can claim the user's chat.

## Install The Marketplace

If the marketplace is not installed yet, run:

```sh
codex plugin marketplace add y5mei/telegram-codex-marketplace
```

After installing the marketplace, help the user enable the `telegram-codex` plugin in Codex if needed.

## Help The User Create A Telegram Bot

Walk the user through this in normal language:

1. Ask the user to install or open the Telegram app.
2. Ask them to search for and open `@BotFather`.
3. Ask them to send:

   ```text
   /newbot
   ```

4. Ask them to follow BotFather's prompts:
   - Choose a display name for the bot.
   - Choose a username for the bot. Telegram requires bot usernames to end in `bot`, for example `my_codex_helper_bot`.
5. BotFather will return an HTTP API token. Tell the user this token is secret.

Do not ask the user to paste the token into chat unless they explicitly want you to write the config for them. Prefer guiding them to paste it into the local `.env` file.

## Configure The Plugin

Find the installed plugin root. If you are unsure where Codex placed it, search locally:

```sh
find ~/.codex -path '*/plugins/telegram-codex' -type d 2>/dev/null
```

From the plugin root:

```sh
cp scripts/env.example .env
```

Help the user set this value in `.env`:

```env
TELEGRAM_BOT_HTTP_API_TOKEN=the_token_from_botfather
```

The user should not need to set `TELEGRAM_ALLOWED_CHAT_IDS` manually. On first contact, the bridge writes the first Telegram chat ID into `.env` automatically.

## Start And Test

Start the bridge from the plugin root:

```sh
python3 scripts/telegram_codex_bridge.py
```

Then guide the user to:

1. Open the new bot in Telegram.
2. Send a first message, such as:

   ```text
   hello codex
   ```

3. Confirm the bridge replies that the chat is now allowed.
4. Ask the user to send a second message that should go through Codex, for example:

   ```text
   Reply with one short sentence confirming Telegram works.
   ```

If the second reply comes back from Codex, setup is complete.

## Security

- Never commit `.env`.
- Never commit or expose the Telegram bot token.
- The first chat to message a fresh bot claims the bridge and is saved to `TELEGRAM_ALLOWED_CHAT_IDS`.
- If the bot token was ever shared, pre-fill `TELEGRAM_ALLOWED_CHAT_IDS` before running the bridge.
- Use `CODEX_SANDBOX=read-only` for Q&A only.
- Use `CODEX_SANDBOX=workspace-write` for local workspace edits.
- Use `CODEX_SANDBOX=danger-full-access` only when the user explicitly wants Telegram prompts to drive broad local filesystem actions.

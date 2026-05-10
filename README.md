# Telegram Codex Marketplace

This repository is a Codex plugin marketplace containing `telegram-codex`, a local bridge that lets a user send messages to Codex from Telegram and receive replies back in Telegram.

This README is written for Codex agents. When a user asks to use this plugin, do not only point them at these instructions. Help them complete the setup.

## User Copy-Paste Prompt

Tell users to send this to Codex:

```text
Please read this link and install the Telegram Codex plugin, then guide me through setup: https://github.com/y5mei/telegram-codex-marketplace
```

Codex should then install the plugin, create the config file, guide the user through BotFather, start the bridge with `/telegram_plugin start`, and test the first Telegram message.

## Agent Goal

Guide the user through:

1. Installing this Codex plugin marketplace.
2. Creating a Telegram bot with `@BotFather`.
3. Getting the bot HTTP API token.
4. Putting that token into the plugin `.env` file.
5. Starting the local bridge.
6. Testing the first Telegram message so the bridge can claim the user's chat.
7. Teaching the user `/telegram_plugin start`, `/telegram_plugin stop`, and `/telegram_plugin status`.

## Install The Marketplace

If the marketplace is not installed yet, run:

```sh
codex plugin marketplace add y5mei/telegram-codex-marketplace
```

After installing the marketplace, ensure the plugin is enabled. If Codex has not added an enabled plugin entry automatically, add this to `~/.codex/config.toml`:

```toml
[plugins."telegram-codex@telegram-codex-marketplace"]
enabled = true
```

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

Find the installed plugin root:

```sh
find ~/.codex -path '*/plugins/telegram-codex' -type d 2>/dev/null
```

From the plugin root:

```sh
cp -n scripts/env.example .env
```

Help the user set this value in `.env`:

```env
TELEGRAM_BOT_HTTP_API_TOKEN=the_token_from_botfather
```

The user should not need to set `TELEGRAM_ALLOWED_CHAT_IDS` manually. On first contact, the bridge writes the first Telegram chat ID into `.env` automatically.

## Start And Test

Start the bridge with the plugin command:

```text
/telegram_plugin start
```

If executing manually, start it from the plugin root:

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
   The expected first reply is:

   ```text
   Hello world from Codex Telegram plugin.
   ```

4. Ask the user to send a second message that should go through Codex, for example:

   ```text
   Reply with one short sentence confirming Telegram works.
   ```

If the second reply comes back from Codex, setup is complete.

## Bridge Lifecycle

The bridge is a long-running local process. Installing the plugin does not automatically start it, and the current Codex plugin surface does not provide a reliable install-time or Codex-shutdown lifecycle hook for this kind of daemon.

Agents should start it during onboarding by running:

```text
/telegram_plugin start
```

Users can later control it with:

```text
/telegram_plugin status
/telegram_plugin stop
/telegram_plugin start
```

If the bridge is already running and the user sends `/stop` to the Telegram bot, the bridge sends:

```text
Telegram Codex bridge is not running. In Codex, type /telegram_plugin start or reopen Codex and ask it to start the Telegram plugin.
```

Then it stops itself. If the bridge is fully stopped or Codex/computer is offline, Telegram cannot receive a local reply because no process is polling Telegram. In that case the user should reopen Codex and type `/telegram_plugin start`.

## Troubleshooting For Agents

- If Python raises a certificate verification error when calling Telegram, the bridge falls back to `curl`.
- If Telegram receives huge Codex CLI logs, upgrade the marketplace and restart the bridge; replies should use only Codex's `--output-last-message` result.
- If Codex reports an unsupported CLI flag, upgrade the marketplace and restart the bridge.
- If `.env` is missing, recreate it from `scripts/env.example`.
- If the bridge is stopped, run `/telegram_plugin start`.

## Security

- Never commit `.env`.
- Never commit or expose the Telegram bot token.
- The first chat to message a fresh bot claims the bridge and is saved to `TELEGRAM_ALLOWED_CHAT_IDS`.
- If the bot token was ever shared, pre-fill `TELEGRAM_ALLOWED_CHAT_IDS` before running the bridge.
- Use `CODEX_SANDBOX=read-only` for Q&A only.
- Use `CODEX_SANDBOX=workspace-write` for local workspace edits.
- Use `CODEX_SANDBOX=danger-full-access` only when the user explicitly wants Telegram prompts to drive broad local filesystem actions.

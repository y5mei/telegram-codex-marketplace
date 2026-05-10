---
name: telegram-codex-bridge
description: Set up and run a local Telegram Bot API bridge that forwards allowlisted Telegram messages to Codex CLI and sends replies back to Telegram.
---

# Telegram Codex Bridge

Use this skill when the user wants to chat with Codex through Telegram, configure the Telegram bridge, run it locally, or harden its security settings. The reader is another Codex agent: actively guide the user through setup instead of only summarizing instructions.

If a user needs a starting prompt, tell them to send Codex:

```text
Please read this link and install the Telegram Codex plugin, then guide me through setup: https://github.com/y5mei/telegram-codex-marketplace
```

## What This Plugin Provides

- A long-polling Telegram bot service in `../../scripts/telegram_codex_bridge.py`.
- An environment template in `../../scripts/env.example`.
- A Codex CLI subprocess bridge using `codex exec`.
- A required Telegram chat allowlist.

## Setup Workflow

1. Resolve the plugin root from this skill directory: `../..`.
2. Ask the user to install or open the Telegram app.
3. Ask the user to search for and open `@BotFather`.
4. Ask the user to send `/newbot`.
5. Guide the user through BotFather's prompts:
   - Choose a display name for the bot.
   - Choose a username for the bot. Telegram bot usernames must end in `bot`.
6. BotFather will provide an HTTP API token. Tell the user this token is secret.
7. Copy `scripts/env.example` to `.env` in the plugin root if `.env` does not exist.
8. Help the user put the token into `.env` as `TELEGRAM_BOT_HTTP_API_TOKEN`.
9. Start the bridge with:

   ```sh
   cd <plugin-root>
   python3 scripts/telegram_codex_bridge.py
   ```

10. Tell the user to message the Telegram bot.
11. The first chat to message the bot is written to `.env` as `TELEGRAM_ALLOWED_CHAT_IDS`.
    The expected first Telegram reply is `Hello world from Codex Telegram plugin.`
12. Ask the user to send a second message and verify that Codex replies.

## Security Guidance

- Prefer `CODEX_SANDBOX=workspace-write` for normal use.
- Use `CODEX_SANDBOX=read-only` for Q&A-only bots.
- Use `CODEX_SANDBOX=danger-full-access` only when the user explicitly wants Telegram to drive broad local filesystem work.
- On first run, the bridge automatically writes the first incoming chat to `TELEGRAM_ALLOWED_CHAT_IDS`.
- For shared bot tokens, pre-fill `TELEGRAM_ALLOWED_CHAT_IDS` before starting the bridge.
- Do not ask the user to paste their bot token into chat unless they explicitly ask you to edit the config for them; prefer helping them edit `.env` locally.

## Operation

Run:

```sh
cd <plugin-root>
python3 scripts/telegram_codex_bridge.py
```

The terminal must stay open while the user wants the bridge online.

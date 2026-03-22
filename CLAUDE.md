# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the bot

```bash
cd bot
python main.py
```

Requires `bot/.env` with three variables: `BOT_TOKEN`, `REPLICATE_API_TOKEN`, `FIXED_PROMPT` (single line).

## Architecture

Telegram bot (aiogram 3) that receives photos and enhances them via Replicate API (`google/nano-banana-pro`).

**Request flow:**
1. User sends photo → `handlers/photo.py` downloads it via Telegram Bot API
2. `ThrottleMiddleware` blocks duplicate requests from the same user
3. `ReplicateService.process()` wraps the sync call in `asyncio.to_thread`
4. `_process_sync()` calls `self._client.run()` with `image_input: [io.BytesIO(bytes)]`, retries 3× with 2s delay
5. Result URL is validated (must be `https://replicate.delivery/...`), then downloaded and sent back as a document

**Dependency injection via aiogram:** `ReplicateService` is attached to the dispatcher as `dp["replicate"]` in `main.py` and injected into handler functions as a parameter.

**Photo vs document:** Handler prefers `message.document` (uncompressed) over `message.photo` (Telegram compresses). Sends result back as document.

## Key files

- `bot/services/replicate_api.py` — Replicate integration, model name, allowed result domains
- `bot/handlers/photo.py` — main handler logic, MIME whitelist, 120s timeout
- `bot/middlewares/throttle.py` — in-memory per-user lock (resets on restart)
- `bot/config.py` — env loading, all three vars are required except `FIXED_PROMPT` (defaults to empty string)

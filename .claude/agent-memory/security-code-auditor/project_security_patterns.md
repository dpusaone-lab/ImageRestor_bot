---
name: Upscale_bot security patterns
description: Known security findings and conventions for the Upscale_bot Telegram bot project
type: project
---

## Project: Upscale_bot (Telegram photo enhancement bot)

### Stack
- Python + aiogram 3.x
- Replicate API for image processing
- python-dotenv for secrets management

### Secret Management Convention
- Secrets stored in `bot/.env` (correctly excluded from git via `bot/.gitignore`)
- `.env.example` present with placeholder values — good practice
- Loaded via `python-dotenv` + `os.getenv()` in `config.py`

### CRITICAL: Real credentials found in .env (2026-03-21 audit)
- `BOT_TOKEN` line 1: real Telegram bot token (`8552894614:AAG...`)
- `REPLICATE_API_TOKEN` line 2: real Replicate token (`r8_Yg9ck...`)
- These appear to be live credentials. Rotation is required if `.env` was ever committed.
- Bot username confirmed in logs: `@pixelphotoup_bot`

### Known Vulnerability: Unvalidated URL fetch in replicate_api.py
- `urllib.request.urlopen(url)` fetches a URL returned by Replicate API response without any domain/scheme validation
- If Replicate response were ever spoofed or the URL manipulated, this could be a SSRF vector
- Mitigation: validate URL starts with `https://replicate.delivery/` before fetching

### Known Vulnerability: ReplicateService sets os.environ directly
- `os.environ["REPLICATE_API_TOKEN"] = api_token` in `__init__` exposes token to all child processes and any code in the same process that reads env vars
- Prefer passing token directly to the replicate client if the SDK supports it

### Log files contain sensitive operational data
- `bot/bot.log` and `bot.log` (root) log internal Replicate delivery URLs
- Log rotation is configured (RotatingFileHandler, 5MB x3) — good
- Log files should be excluded from version control

### ThrottleMiddleware: in-memory state, not persistent
- `processing_users: set[int]` is in-memory only
- On restart, all locks are cleared — acceptable for single-instance bot
- Not safe for multi-instance deployments

### No input sanitization needed (by design)
- The bot only processes binary image bytes — no SQL, no shell commands, no user-controlled strings passed to dangerous sinks
- MIME type whitelist is correctly applied: `{"image/jpeg", "image/png", "image/webp"}`
- File size limit: 20MB enforced

### Dependencies (requirements.txt) — no pinned versions
- All deps use `>=` ranges without upper bounds or hash pinning
- Risk: supply chain attack via dependency update

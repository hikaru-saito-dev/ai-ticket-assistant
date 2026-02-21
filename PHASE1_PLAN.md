# Phase 1 Implementation Plan: Foundation & Core Connectivity

## Overview
Build a minimal, stable skeleton proving the relay mechanism works between Discord bot and FastAPI backend. No business logic, no database, no AI - just message relay.

## Folder Structure
```
AI-ticket-assistant/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Bot entry point
│   ├── cogs/
│   │   ├── __init__.py
│   │   ├── setup.py         # /setup slash command
│   │   └── tickets.py       # /create-ticket slash command + message listener
│   ├── utils/
│   │   ├── __init__.py
│   │   └── http_client.py   # Async HTTP client for backend communication
│   └── config.py            # Bot configuration (env vars)
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── relay.py         # /relay endpoint
│   │   └── health.py        # /health endpoint
│   ├── models/
│   │   ├── __init__.py
│   │   └── relay.py         # Pydantic models for relay payload
│   └── config.py            # Backend configuration
├── shared/
│   └── __init__.py          # Placeholder for future shared code
├── docker-compose.yml       # Local development setup
├── Dockerfile.bot           # Bot container
├── Dockerfile.backend       # Backend container
├── requirements.txt         # Python dependencies
├── requirements-bot.txt     # Bot-specific dependencies
├── requirements-backend.txt # Backend-specific dependencies
├── .env.example            # Environment variables template
├── .gitignore
└── README.md               # Setup and run instructions
```

## Key Decisions

### 1. Discord Bot (discord.py)
- **Intents**: `discord.Intents.default()` + `messages=True`, `guilds=True`
- **Slash Commands**: 
  - `/setup` - Admin only, creates "Tickets" category if missing
  - `/create-ticket` - Creates private channel `ticket-{user_id}` in Tickets category
- **Message Filtering**: Only process messages in channels starting with `ticket-`
- **Permissions**: 
  - Bot needs: `manage_channels`, `send_messages`, `read_message_history`, `view_channel`
  - Ticket channels: User + support role (if exists) get access
- **Error Handling**: 
  - Try/except around HTTP calls with retries (max 2 retries, exponential backoff)
  - Log errors but don't crash bot
  - Send user-friendly error messages to channel on failure

### 2. Backend API (FastAPI)
- **Endpoints**:
  - `POST /relay` - Receives message payload, logs it, returns placeholder
  - `GET /health` - Health check endpoint
- **Payload Structure**:
  ```json
  {
    "guild_id": "string",
    "channel_id": "string",
    "user_id": "string",
    "content": "string",
    "message_id": "string" (optional)
  }
  ```
- **Response Structure**:
  ```json
  {
    "reply": "AI is thinking... (Phase 1 placeholder)"
  }
  ```
- **Error Handling**: 
  - Validate payload with Pydantic
  - Return 400 on invalid payload
  - Return 500 on unexpected errors (with logging)
  - Always return JSON

### 3. Communication
- **Bot → Backend**: Async HTTP POST using `aiohttp` or `httpx`
- **Backend URL**: From env var `BACKEND_URL` (default: `http://localhost:8000`)
- **Timeout**: 10 seconds for HTTP calls
- **Headers**: `Content-Type: application/json`

### 4. Logging
- **Bot**: Use Python `logging` module with INFO level, format: `[BOT] {level} - {message}`
- **Backend**: Use Python `logging` module with INFO level, format: `[API] {level} - {message}`
- **Log all**: Message receives, HTTP calls, errors, health checks

### 5. Docker Setup
- **Services**:
  - `bot`: Python 3.11-slim, installs bot requirements, runs `python bot/main.py`
  - `api`: Python 3.11-slim, installs backend requirements, runs `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
  - `postgres`: PostgreSQL 15 (for future phases, not used in Phase 1)
- **Networking**: Bot connects to `http://api:8000` when in Docker, `http://localhost:8000` when local
- **Environment**: Shared `.env` file, loaded via `python-dotenv`

### 6. Configuration
- **Bot Environment Variables**:
  - `DISCORD_TOKEN` - Bot token (required)
  - `BACKEND_URL` - Backend API URL (default: `http://localhost:8000`)
  - `LOG_LEVEL` - Logging level (default: `INFO`)
- **Backend Environment Variables**:
  - `LOG_LEVEL` - Logging level (default: `INFO`)
  - `HOST` - Bind host (default: `0.0.0.0`)
  - `PORT` - Bind port (default: `8000`)

## Files to Create

1. **Bot Files**:
   - `bot/main.py` - Bot initialization and run loop
   - `bot/config.py` - Configuration loader
   - `bot/cogs/setup.py` - Setup command
   - `bot/cogs/tickets.py` - Ticket creation and message relay
   - `bot/utils/http_client.py` - HTTP client wrapper

2. **Backend Files**:
   - `backend/main.py` - FastAPI app initialization
   - `backend/config.py` - Configuration loader
   - `backend/api/relay.py` - Relay endpoint
   - `backend/api/health.py` - Health endpoint
   - `backend/models/relay.py` - Pydantic models

3. **Infrastructure**:
   - `docker-compose.yml` - Multi-service setup
   - `Dockerfile.bot` - Bot container
   - `Dockerfile.backend` - Backend container
   - `.env.example` - Environment template
   - `.gitignore` - Git ignore rules

4. **Dependencies**:
   - `requirements.txt` - Common dependencies
   - `requirements-bot.txt` - Bot-specific
   - `requirements-backend.txt` - Backend-specific

5. **Documentation**:
   - `README.md` - Setup and run guide

## Implementation Order

1. Create folder structure
2. Write configuration files (config.py for both)
3. Write backend API (health + relay endpoints)
4. Write bot HTTP client utility
5. Write bot cogs (setup + tickets)
6. Write bot main entry point
7. Write Docker files
8. Write requirements files
9. Write .env.example and .gitignore
10. Write README.md

## Testing Strategy

1. **Local Testing**:
   - Run backend: `uvicorn backend.main:app --reload`
   - Run bot: `python bot/main.py`
   - Test `/health` endpoint: `curl http://localhost:8000/health`
   - Join bot to test server, run `/setup`, then `/create-ticket`
   - Send message in ticket channel, verify relay works

2. **Docker Testing**:
   - `docker-compose up --build`
   - Verify both services start
   - Test same flow as above

## Questions/Clarifications

1. **Ticket Channel Naming**: Use `ticket-{user_id}` or `ticket-{username}`? (Proposed: `ticket-{user_id}` for uniqueness)
2. **Support Role**: Should `/setup` create a "Support" role automatically, or assume it exists? (Proposed: Create if missing)
3. **Message History**: Should bot fetch recent messages for context? (Phase 1: No, just relay current message)
4. **Rate Limiting**: Add basic rate limiting in Phase 1? (Proposed: No, add in Phase 2)
5. **CORS**: Backend CORS settings? (Proposed: Allow all origins for MVP, restrict in production)

---

**Ready to proceed?** If approved, I'll implement all files following this plan exactly.


# Phase 2 - Run & Test Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)

## 1. Install Dependencies

```bash
pip install -r requirements-backend.txt
```

**Note:** `sentence-transformers` will download the model (~80MB) on first use.

## 2. Environment

```bash
cp .env.example .env
# Edit .env and ensure:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_ticket_assistant
# REDIS_URL=redis://localhost:6379/0
```

## 3. Start PostgreSQL & Redis (if not using Docker)

**Option A: Docker Compose (recommended)**

```bash
docker-compose up -d postgres redis
# Wait for health checks to pass
```

**Option B: Local install**

- Start PostgreSQL, create database `ai_ticket_assistant`
- Start Redis on port 6379

## 4. Run Migrations (manual, optional)

Migrations run automatically on API startup. To run manually:

```bash
alembic upgrade head
```

## 5. Start Backend

```bash
python run_backend.py
# OR: uvicorn backend.main:app --reload
```

Backend starts at `http://localhost:8000`. On startup it will:

- Connect to Redis
- Run Alembic migrations
- Start daily/monthly reset scheduler

## 6. Test Endpoints

### Health

```bash
curl http://localhost:8000/health
```

### Relay (simulates bot)

```bash
curl -X POST http://localhost:8000/relay \
  -H "Content-Type: application/json" \
  -d '{"guild_id":"123456","channel_id":"789","user_id":"111","content":"Hello"}'
```

Expected: `{"status":"ok","reply":"AI is thinking... (Phase 2 placeholder)","prompt_context":{...}}`

### Knowledge CRUD

```bash
# Create
curl -X POST http://localhost:8000/guilds/123456/knowledge \
  -H "Content-Type: application/json" \
  -d '{"title":"FAQ","content":"Our support hours are 9am-5pm UTC."}'

# List
curl http://localhost:8000/guilds/123456/knowledge

# Usage
curl http://localhost:8000/guilds/123456/usage
```

## 7. Full Stack with Docker

```bash
docker-compose up --build
```

Starts: postgres, redis, api, bot.

## 8. Limit Testing

- **Concurrent:** Send 2+ simultaneous relay requests for a Free-plan guild (limit 1)
- **Daily tickets:** Create 11 tickets in one day for Free plan (limit 10)
- **Knowledge:** Add 3 knowledge entries for Free plan (limit 2) – should get 403

## Troubleshooting

- **Redis connection failed:** Ensure Redis is running, check `REDIS_URL`
- **Database error:** Run migrations, check `DATABASE_URL`
- **Import error:** Run from project root, ensure `PYTHONPATH` includes project root

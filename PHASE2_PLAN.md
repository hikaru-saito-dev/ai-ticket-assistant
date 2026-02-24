# Phase 2 Implementation Plan: Backend Logic, Limits, Knowledge & Plan Enforcement

## Overview

Implement full backend logic for Phase 2: database models, subscription plans, limit enforcement, knowledge CRUD, usage tracking, and prompt building. **No bot changes. No AI calls. No dashboard.**

---

## 1. Folder Structure & New Files

```
backend/
├── main.py                    # UPDATE: lifespan (DB, Redis, Scheduler, migrations)
├── config.py                  # UPDATE: add DATABASE_URL, REDIS_URL
├── db/
│   ├── __init__.py            # NEW: export engine, session factory, get_session
│   ├── base.py                # NEW: declarative base, metadata
│   └── session.py             # NEW: async session factory, dependency
├── models/                    # SQLAlchemy ORM models
│   ├── __init__.py            # UPDATE: export all models
│   ├── relay.py               # KEEP: Pydantic schemas (move to schemas/)
│   ├── guild.py               # NEW: Guild ORM model
│   ├── knowledge.py            # NEW: Knowledge ORM model
│   ├── ticket.py               # NEW: Ticket ORM model
│   ├── usage_log.py            # NEW: UsageLog ORM model
│   └── message.py              # NEW: Message ORM model (conversation history)
├── schemas/                   # NEW: Pydantic v2 request/response schemas
│   ├── __init__.py
│   ├── relay.py               # MOVE from models/relay.py
│   ├── guild.py               # NEW: GuildCreate, GuildResponse, etc.
│   ├── knowledge.py           # NEW: KnowledgeCreate, KnowledgeUpdate, KnowledgeResponse
│   ├── usage.py               # NEW: UsageResponse
│   └── plans.py               # NEW: Plan limits constants
├── api/
│   ├── relay.py               # UPDATE: full Phase 2 flow
│   ├── health.py              # KEEP
│   ├── knowledge.py           # NEW: CRUD for /guilds/{guild_id}/knowledge
│   └── usage.py               # NEW: GET /guilds/{guild_id}/usage
├── services/
│   ├── __init__.py
│   ├── guild_service.py       # NEW: upsert guild, get guild
│   ├── knowledge_service.py   # NEW: CRUD, similarity search
│   ├── limit_service.py       # NEW: Redis atomic limit checks
│   ├── prompt_builder.py      # NEW: build prompt context
│   └── reset_service.py       # NEW: daily/monthly reset logic
├── utils/
│   ├── __init__.py
│   └── embeddings.py          # NEW: sentence-transformers wrapper
└── alembic/
    ├── env.py                 # NEW: async alembic env
    ├── script.py.mako
    └── versions/
        └── 001_initial.py     # NEW: initial migration

alembic.ini                    # NEW: Alembic config
```

---

## 2. Database Models (SQLAlchemy 2.0 async)

### Guild

| Column | Type | Notes |
|--------|------|------|
| id | BigInteger, PK | Discord guild ID |
| name | String(255) | Guild name |
| plan | Enum(Free, Pro, Business) | Default: Free |
| monthly_tokens_used | Integer | Default 0 |
| daily_ticket_count | Integer | Default 0 |
| concurrent_ai_sessions | Integer | Default 0 (managed in Redis, but we'll keep for consistency) |
| last_daily_reset | DateTime(timezone=True) | UTC |
| last_monthly_reset | DateTime(timezone=True) | UTC |
| system_prompt | Text | Per-guild system prompt |
| created_at | DateTime | |
| updated_at | DateTime | |

### Knowledge

| Column | Type | Notes |
|--------|------|------|
| id | UUID, PK | |
| guild_id | BigInteger, FK | |
| title | String(500) | |
| content | Text | |
| embedding | Vector(384) | pgvector - 384 for all-MiniLM-L6-v2 |
| created_at | DateTime | |
| updated_at | DateTime | |

**Note:** Use `pgvector` extension. If not available, store as `ARRAY(Float)` or JSONB. Fallback: store as `ARRAY(REAL)` in PostgreSQL.

### Ticket

| Column | Type | Notes |
|--------|------|------|
| id | UUID, PK | |
| guild_id | BigInteger, FK | |
| channel_id | BigInteger, unique per guild | Discord channel ID |
| status | Enum(open, closed) | Default: open |
| created_at | DateTime | |

### UsageLog

| Column | Type | Notes |
|--------|------|------|
| id | UUID, PK | |
| guild_id | BigInteger, FK | |
| tokens_used | Integer | 0 for Phase 2 |
| timestamp | DateTime | |
| request_type | String(50) | e.g. "relay" |

### Message

| Column | Type | Notes |
|--------|------|------|
| id | UUID, PK | |
| ticket_id | UUID, FK | |
| role | Enum(user, assistant) | |
| content | Text | |
| created_at | DateTime | |

---

## 3. Redis Key Design

| Key | Type | TTL | Purpose |
|-----|------|-----|---------|
| `g:{guild_id}:concurrent` | int | None | Atomic concurrent session count |
| `g:{guild_id}:daily_tickets:{date}` | int | 25h | Daily ticket count for date (YYYY-MM-DD) |
| `g:{guild_id}:monthly_tokens` | int | 32d | Monthly token usage (reset by scheduler) |
| `lock:g:{guild_id}:relay` | string | 30s | Optional: lock per guild during limit check |

**Operations:**
- `INCR g:{guild_id}:concurrent` before processing
- `DECR g:{guild_id}:concurrent` after response (or on error)
- `INCR g:{guild_id}:daily_tickets:{today}` when new ticket created
- `GET g:{guild_id}:concurrent` for limit check
- `GET g:{guild_id}:monthly_tokens` - actually monthly tokens come from DB (UsageLog aggregation) or we sync to Redis for fast checks. For atomicity, we'll use Redis as source of truth for concurrent; for monthly we can either (a) aggregate from UsageLog on each request (slow) or (b) store in Redis and increment on each AI call. Phase 2 has no AI, so we increment by 0. The check: `monthly_tokens_used + 0 < limit` - we're not adding tokens. So we just need to read from DB. Actually the spec says "Redis atomic" for limit checks. So we need Redis to have the monthly count. Option: Scheduler writes DB → Redis periodically, OR we use Redis INCR when we log usage. For Phase 2 we don't use tokens, so we'd never INCR. The monthly check would be: get from DB (sum UsageLog for this month) or from Redis. I'll use Redis: `g:{guild_id}:monthly_tokens` - scheduler sets it from DB at reset, and we INCR when we log token usage (Phase 3). For Phase 2, we just check the value (which might be 0 or synced from Guild.monthly_tokens_used at startup).

Simpler: Store all limits in Redis, sync from DB on startup and on reset.
- `g:{guild_id}:monthly_tokens` - current month usage (scheduler resets monthly)
- `g:{guild_id}:daily_tickets` - today's new tickets (scheduler resets daily)
- `g:{guild_id}:concurrent` - current active AI sessions (we manage)

---

## 4. Plan Limits (Hardcoded)

```python
PLAN_LIMITS = {
    "free": {
        "knowledge_entries": 2,
        "monthly_tokens": 50_000,
        "concurrent_tickets": 1,
        "daily_ticket_limit": 10,
    },
    "pro": {
        "knowledge_entries": 5,
        "monthly_tokens": 1_500_000,
        "concurrent_tickets": 3,
        "daily_ticket_limit": 50,
    },
    "business": {
        "knowledge_entries": 10,
        "monthly_tokens": 3_000_000,
        "concurrent_tickets": 3,  # same as Pro, "priority" is Phase 3
        "daily_ticket_limit": 100,
    },
}
```

---

## 5. Relay Flow (Updated)

1. **Upsert Guild** – if guild_id not in DB, create with plan=Free, default system_prompt
2. **Validate ticket channel** – channel name pattern `ticket-*` (we'll trust bot; or check Ticket exists for channel_id)
3. **Get or create Ticket** – if first message from this channel, create Ticket, INCR daily_tickets in Redis
4. **Limit checks (atomic)**:
   - `concurrent < plan_limit` → else reject
   - `daily_tickets < daily_limit` → else reject (only when creating NEW ticket)
   - `monthly_tokens < monthly_limit` → else reject
5. **INCR concurrent** in Redis
6. **Store user Message**
7. **Build prompt context** – system_prompt + top-3 knowledge (by cosine similarity) + last 8 messages
8. **Return** `{"status": "ok", "prompt_context": {...}, "reply": "AI is thinking... (Phase 2 placeholder)"}`
9. **Store assistant Message**
10. **DECR concurrent** in Redis
11. **On error**: ensure DECR concurrent

---

## 6. Knowledge Retrieval (MVP)

- Use `sentence-transformers` with `all-MiniLM-L6-v2` (384 dimensions)
- Store embeddings in Knowledge.embedding (pgvector or ARRAY)
- On query: embed the message content, cosine similarity with all guild knowledge, return top 3
- Lazy load model (singleton in lifespan)

---

## 7. Scheduler (APScheduler AsyncIOScheduler)

- **Daily reset** (00:00 UTC): For each guild, reset `daily_ticket_count`, sync Redis `daily_tickets`
- **Monthly reset** (1st 00:00 UTC): For each guild, reset `monthly_tokens_used`, sync Redis `monthly_tokens`
- Jobs run in asyncio event loop

---

## 8. Alembic Migration Strategy

- `alembic init alembic` (if not exists)
- `env.py` uses `run_async_migrations` with `create_async_engine`
- Migration creates: Guild, Knowledge, Ticket, UsageLog, Message tables
- **Run migrations in lifespan** on startup (optional, or document manual run)
- Spec says "run on startup via lifespan" – we'll add a startup check that runs pending migrations

---

## 9. Docker & Config Updates

**docker-compose.yml:**
- Add `redis` service with healthcheck
- Add `redis_data` volume
- `api` depends on `redis` with `condition: service_healthy`
- Add env: `DATABASE_URL`, `REDIS_URL` to api

**.env.example:**
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/ai_ticket_assistant
REDIS_URL=redis://redis:6379/0
```

---

## 10. Clarification Questions

1. **pgvector vs ARRAY**: PostgreSQL `vector` type requires pgvector extension. Prefer pgvector; fallback to `ARRAY(REAL)` if extension not available.
2. **Alembic on startup**: Run pending migrations automatically in lifespan?
3. **Ticket creation**: First relay from a channel = new ticket. Increment daily count only then.
4. **Daily ticket limit**: Not in spec; added: Free 10, Pro 50, Business 100.

---

## 11. Dependencies to Add

```
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
redis>=5.0.0
apscheduler>=3.10.0
structlog>=24.0.0
sentence-transformers>=2.2.0
pgvector>=0.2.0  # or omit if using ARRAY fallback
```

---

**Ready to implement.** Say "proceed" to start Phase 2 implementation.

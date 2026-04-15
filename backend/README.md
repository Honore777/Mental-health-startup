# Amahoro Backend (FastAPI)

## Features

- Modular FastAPI app with clear route/service/model boundaries.
- Async SQLAlchemy + PostgreSQL.
- Alembic migrations for schema lifecycle.
- HTTP-only cookie sessions (server-side session table).
- Agent orchestration with:
  - singleton LLM orchestrator,
  - `asyncio.wait_for` timeout control,
  - ChatGroq fallback,
  - exponential backoff retries.

## Quick Start

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set values.
3. Run migrations:

```bash
alembic upgrade head
```

4. Start API server:

```bash
uvicorn app.main:app --reload --port 8000
```

## API Surface

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `POST /api/chat`
- `POST /api/messages`
- `GET /api/chats`
- `GET /api/chats/{chat_id}/messages`

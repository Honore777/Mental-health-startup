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

## Render Deployment (Production)

Use Python 3.12 to avoid source-build failures for transitive packages on Python 3.14.

1. Service root directory: `backend`
2. Build command: `pip install -r requirements.txt && alembic upgrade head`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Python version: set `PYTHON_VERSION=3.12.8` in Render environment variables.

For Vercel frontend + Render backend authentication, also set:

- `CORS_ORIGINS=https://mental-health-awareai.vercel.app`
- `CORS_ORIGIN_REGEX=` (optional; use only if you need preview domains)
- `SESSION_COOKIE_SECURE=true`
- `SESSION_COOKIE_SAMESITE=none`

This repo also includes `.python-version` and `runtime.txt` in `backend/` for explicit runtime pinning.

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

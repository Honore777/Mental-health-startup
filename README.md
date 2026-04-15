# Amahoro Mental Wellness Monorepo

This project is now modularized into:

- `frontend`: Next.js (React + TypeScript) web client
- `backend`: FastAPI (Python) API service

## Architecture

- Frontend: Next.js app-router UI, cookie-based auth flow, calls backend APIs using `credentials: include`.
- Backend: FastAPI, async SQLAlchemy, Alembic migrations, server-side sessions with HTTP-only cookies.
- AI orchestration: singleton LLM orchestrator with timeout control (`asyncio.wait_for`), ChatGroq fallback, and exponential backoff retry.

## Local Development

### 1) Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend runs on `http://localhost:3000`.

### 2) Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Backend runs on `http://localhost:8000`.

## Deployment Notes

- Set production `CORS_ORIGINS` and `SESSION_COOKIE_SECURE=true`.
- Use strong managed Postgres credentials in `DATABASE_URL`.
- Run Alembic migrations during deploy (`alembic upgrade head`).
- Provide `GEMINI_API_KEY` and `CHATGROQ_API_KEY` through secret manager.

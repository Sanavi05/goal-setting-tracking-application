# Deployment

## Frontend on Vercel

1. Import the repository.
2. Set root directory to `frontend`.
3. Add `NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com`.
4. Build command: `npm run build`.
5. Output is handled by Next.js.

## Backend on Render

1. Create a Python Web Service with root directory `backend`.
2. Use Python 3.11. The repo includes `backend/.python-version` with `3.11.9`.
   Also set Render environment variable `PYTHON_VERSION=3.11.9` if the dashboard keeps defaulting to Python 3.14.
3. Add environment variables from `backend/.env.example`.
4. Set `DATABASE_URL` to your managed Postgres connection string.
5. Build command: `pip install -r requirements.txt`.
6. Start command: `alembic upgrade head && python -m app.db.init_db && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
7. The seed script is idempotent: it exits when users already exist.

You can also use the root `render.yaml` blueprint. Set these values in Render after creating the service:

- `DATABASE_URL`
- `BACKEND_CORS_ORIGINS=https://your-vercel-app.vercel.app`

## Database on Supabase

1. Create a Supabase project.
2. Copy the Postgres connection string.
3. Use the SQLAlchemy form as `DATABASE_URL`, usually `postgresql+psycopg2://...`.
4. Run migrations from the backend service shell.

## Architecture Diagram

Submit `docs/architecture-diagram.svg` alongside the repository and live URLs.

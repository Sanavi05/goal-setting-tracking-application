# goal-setting-tracking-application

GoalGrid is an audit-ready in-house goal setting and tracking portal for Employee, Manager L1, and Admin/HR workflows. It covers goal creation, manager approval, goal locking, quarterly check-ins, shared KPIs, reporting, audit logs, escalation rules, notifications, and analytics.

## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind CSS, shadcn-style local UI primitives, React Hook Form/Zod-ready forms, Recharts, TanStack Table, Axios
- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic, JWT auth, passlib/bcrypt, openpyxl
- Database: PostgreSQL

## Features

- JWT login with role-based access control
- Employee draft, submit, and check-in flow
- Manager approval, rework, inline target/weightage edits, and locking
- Admin cycle management, audit logs, reports, unlocks, users, and completion dashboards
- Shared departmental KPIs with readonly title/target for recipients
- CSV and Excel achievement exports
- Escalation rules and logs with mock notifications
- Microsoft Entra ID placeholder service and integration notes

## Local Setup

1. Start Postgres:

```bash
docker compose up -d
```

2. Start the backend:

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```

The local Docker database is published on host port `5433` to avoid clashing with any Postgres already running on your machine.

3. Start the frontend:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Demo Credentials

- Employee: `employee@goalgrid.demo` / `password123`
- Manager: `manager@goalgrid.demo` / `password123`
- Admin: `admin@goalgrid.demo` / `password123`

## API Overview

Main groups:

- Auth: `/api/auth/login`, `/api/auth/me`
- Employee: `/api/employee/dashboard`, `/api/goal-sheets/current`, `/api/goal-sheets`, `/api/check-ins`
- Manager: `/api/manager/dashboard`, `/api/manager/approvals`, `/api/manager/goal-sheets/{id}/approve`
- Admin: `/api/admin/dashboard`, `/api/admin/cycles`, `/api/admin/users`, `/api/admin/audit-logs`, report exports
- Analytics: `/api/analytics/qoq-trends`, `/api/analytics/goal-distribution`, `/api/analytics/manager-effectiveness`
- Escalations: `/api/admin/escalation-rules`, `/api/admin/escalation-logs`, `/api/admin/run-escalation-check`

Full endpoint notes are in [docs/api.md](docs/api.md).

## Deployment

- Frontend: Vercel, with `NEXT_PUBLIC_API_URL` pointed to the backend URL
- Backend: Render Web Service running `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Database: Supabase Postgres or Render Postgres

See [docs/deployment.md](docs/deployment.md) for details.

The architecture diagram deliverable is available at [docs/architecture-diagram.svg](docs/architecture-diagram.svg).

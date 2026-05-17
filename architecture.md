# Architecture

## High-Level Flow

The frontend is a Next.js app that calls FastAPI REST endpoints with a JWT bearer token. FastAPI validates roles, applies workflow rules in a service layer, persists state through SQLAlchemy ORM, and stores data in PostgreSQL.

```text
Browser -> Next.js UI -> FastAPI API -> Service layer -> SQLAlchemy -> PostgreSQL
```

## Role-Based Access Model

- Employee: own dashboard, own goal sheet, own check-ins
- Manager: assigned team, submitted approvals, manager comments, target/weightage edits before lock
- Admin/HR: cycles, users, reports, shared goals, audit logs, unlocks, escalation checks

## Workflow Guarantees

- Submission requires exactly 100% total weightage
- Minimum goal weightage is 10%
- Maximum 8 goals per sheet
- Approved sheets are locked
- Admin unlocks are audited
- Manager approvals are limited to direct reports
- Shared goal recipients cannot edit title or target

## Cost Optimization

The app uses a single FastAPI service and a managed PostgreSQL instance. Vercel can host the frontend on the free or low-cost tier, while Render and Supabase provide straightforward hackathon-friendly backend and database hosting. The system avoids background workers by making escalation checks an admin-triggered endpoint.

## Hosting Choices

- Vercel for Next.js because it gives fast CI/CD and CDN-backed frontend hosting
- Render for FastAPI because it supports Python web services with simple env var configuration
- Supabase Postgres because it is managed, familiar, and easy to inspect during demos

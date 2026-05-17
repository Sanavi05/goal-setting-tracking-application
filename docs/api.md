# API Documentation

All protected endpoints require `Authorization: Bearer <token>`.

## Auth

- `POST /api/auth/login` with `{ email, password }`
- `GET /api/auth/me`

## Employee

- `GET /api/employee/dashboard`
- `GET /api/goal-sheets/current`
- `POST /api/goal-sheets`
- `PATCH /api/goal-sheets/{id}`
- `POST /api/goal-sheets/{id}/submit`
- `POST /api/check-ins`

## Manager

- `GET /api/manager/dashboard`
- `GET /api/manager/team`
- `GET /api/manager/approvals`
- `GET /api/manager/goal-sheets/{id}`
- `PATCH /api/manager/goals/{id}`
- `POST /api/manager/goal-sheets/{id}/approve`
- `POST /api/manager/goal-sheets/{id}/return`
- `POST /api/manager/check-ins/{id}/comment`

## Admin

- `GET /api/admin/dashboard`
- `GET /api/admin/cycles`
- `POST /api/admin/cycles`
- `GET /api/admin/users`
- `POST /api/admin/users`
- `POST /api/admin/goals/{sheet_id}/unlock`
- `GET /api/admin/audit-logs`
- `GET /api/admin/completion-dashboard`
- `POST /api/admin/shared-goals`
- `POST /api/admin/shared-goals/{id}/assign`
- `GET /api/admin/reports/achievement/export/csv`
- `GET /api/admin/reports/achievement/export/xlsx`

## Analytics

- `GET /api/analytics/qoq-trends`
- `GET /api/analytics/goal-distribution`
- `GET /api/analytics/manager-effectiveness`
- `GET /api/analytics/completion-heatmap`

## Escalations

- `GET /api/admin/escalation-rules`
- `POST /api/admin/escalation-rules`
- `GET /api/admin/escalation-logs`
- `POST /api/admin/run-escalation-check`

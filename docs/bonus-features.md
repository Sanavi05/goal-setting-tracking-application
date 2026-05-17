# Bonus Features

## Analytics

The analytics endpoints and UI show QoQ achievement trends, goal distribution, completion patterns, and manager effectiveness. Charts are implemented with Recharts.

## Escalations

Admins can configure rules such as goals not submitted or manager approval delayed. The demo implementation runs checks on demand through `/api/admin/run-escalation-check`, creates escalation logs, and generates notification records.

## Notifications

The backend creates notification rows for submissions, approvals, returns, and escalations. `app/services/notifications.py` also includes a Teams adaptive card payload shape so Microsoft Graph delivery can be added later.

## Entra Placeholder

`app/services/entra.py` defines a future SSO service and group-to-role mapping. See `docs/entra-id-integration.md`.

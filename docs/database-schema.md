# Database Schema

## Tables

- `users`: employees, managers, and admins with self-referencing `manager_id`
- `cycles`: annual performance cycle and check-in window dates
- `goal_sheets`: employee cycle sheet, status, lock timestamps, return comments
- `goals`: weighted goals linked to a sheet
- `shared_goals`: departmental KPIs assignable to employees
- `check_ins`: quarterly achievements and computed progress scores
- `audit_logs`: workflow and sensitive change trail
- `escalation_rules`: configurable escalation triggers
- `escalation_logs`: generated escalation events
- `notifications`: mock in-app/email/Teams notification records

## Relationships

- User manager hierarchy: `users.manager_id -> users.id`
- Goal sheet owner: `goal_sheets.employee_id -> users.id`
- Goal sheet approver: `goal_sheets.manager_id -> users.id`
- Goal sheet cycle: `goal_sheets.cycle_id -> cycles.id`
- Goal to sheet: `goals.goal_sheet_id -> goal_sheets.id`
- Check-in to goal: `check_ins.goal_id -> goals.id`
- Shared goal to assigned goals: `goals.shared_goal_id -> shared_goals.id`

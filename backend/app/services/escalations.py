from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import EscalationLog, EscalationRule, GoalSheet, GoalSheetStatus, Notification, User


def run_escalation_check(db: Session) -> int:
    created = 0
    now = datetime.now(timezone.utc)
    rules = db.query(EscalationRule).filter(EscalationRule.active.is_(True)).all()
    for rule in rules:
        if rule.trigger_type == "GOALS_NOT_SUBMITTED":
            sheets = db.query(GoalSheet).filter(GoalSheet.status == GoalSheetStatus.DRAFT).all()
            for sheet in sheets:
                created += _create_log(db, rule, sheet.employee_id, sheet.id, "Goal sheet is still in draft")
        if rule.trigger_type == "MANAGER_APPROVAL_DELAY":
            sheets = db.query(GoalSheet).filter(GoalSheet.status == GoalSheetStatus.SUBMITTED).all()
            for sheet in sheets:
                if sheet.submitted_at and (now - sheet.submitted_at).days >= rule.threshold_days:
                    created += _create_log(db, rule, sheet.manager_id, sheet.id, "Submitted goal sheet is awaiting manager approval")
    return created


def _create_log(db: Session, rule: EscalationRule, user_id: int, sheet_id: int, message: str) -> int:
    exists = db.query(EscalationLog).filter_by(rule_id=rule.id, user_id=user_id, goal_sheet_id=sheet_id, status="OPEN").first()
    if exists:
        return 0
    db.add(EscalationLog(rule_id=rule.id, user_id=user_id, goal_sheet_id=sheet_id, message=message, level="WARN"))
    db.add(Notification(user_id=user_id, type="ESCALATION", title=rule.name, message=message))
    return 1

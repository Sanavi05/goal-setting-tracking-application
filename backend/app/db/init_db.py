from datetime import date, datetime, timedelta, timezone

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models import AuditLog, CheckIn, Cycle, EscalationLog, EscalationRule, Goal, GoalSheet, GoalSheetStatus, GoalStatus, Role, UomType, User
from app.services.goals import score_goal


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count():
            return
        admin = User(name="Asha HR", email="admin@goalgrid.demo", password_hash=hash_password("password123"), role=Role.ADMIN, department="HR")
        manager1 = User(name="Maya Rao", email="manager@goalgrid.demo", password_hash=hash_password("password123"), role=Role.MANAGER, department="Engineering")
        manager2 = User(name="Nikhil Shah", email="ops.manager@goalgrid.demo", password_hash=hash_password("password123"), role=Role.MANAGER, department="Operations")
        db.add_all([admin, manager1, manager2])
        db.flush()
        employees = [
            User(name="Evan Lee", email="employee@goalgrid.demo", password_hash=hash_password("password123"), role=Role.EMPLOYEE, department="Engineering", manager_id=manager1.id),
            User(name="Priya Menon", email="priya@goalgrid.demo", password_hash=hash_password("password123"), role=Role.EMPLOYEE, department="Engineering", manager_id=manager1.id),
            User(name="Carlos Vega", email="carlos@goalgrid.demo", password_hash=hash_password("password123"), role=Role.EMPLOYEE, department="Engineering", manager_id=manager1.id),
            User(name="Lina Chen", email="lina@goalgrid.demo", password_hash=hash_password("password123"), role=Role.EMPLOYEE, department="Sales", manager_id=manager1.id),
            User(name="Samir Khan", email="samir@goalgrid.demo", password_hash=hash_password("password123"), role=Role.EMPLOYEE, department="Operations", manager_id=manager2.id),
            User(name="Ana Silva", email="ana@goalgrid.demo", password_hash=hash_password("password123"), role=Role.EMPLOYEE, department="Operations", manager_id=manager2.id),
            User(name="Jon Bell", email="jon@goalgrid.demo", password_hash=hash_password("password123"), role=Role.EMPLOYEE, department="HR", manager_id=manager2.id),
            User(name="Fatima Noor", email="fatima@goalgrid.demo", password_hash=hash_password("password123"), role=Role.EMPLOYEE, department="Sales", manager_id=manager2.id),
        ]
        db.add_all(employees)
        cycle = Cycle(
            name="FY26 Performance Cycle",
            year=2026,
            status="ACTIVE",
            goal_setting_open_date=date(2026, 5, 1),
            q1_open_date=date(2026, 7, 1),
            q2_open_date=date(2026, 10, 1),
            q3_open_date=date(2027, 1, 1),
            q4_open_date=date(2027, 3, 15),
        )
        db.add(cycle)
        db.flush()
        statuses = [GoalSheetStatus.DRAFT, GoalSheetStatus.SUBMITTED, GoalSheetStatus.RETURNED, GoalSheetStatus.APPROVED]
        for index, employee in enumerate(employees):
            status = statuses[index % len(statuses)]
            sheet = GoalSheet(employee_id=employee.id, manager_id=employee.manager_id, cycle_id=cycle.id, status=status)
            if status in [GoalSheetStatus.SUBMITTED, GoalSheetStatus.APPROVED]:
                sheet.submitted_at = datetime.now(timezone.utc) - timedelta(days=2 + index)
            if status == GoalSheetStatus.APPROVED:
                sheet.approved_at = datetime.now(timezone.utc) - timedelta(days=1)
                sheet.locked_at = sheet.approved_at
            if status == GoalSheetStatus.RETURNED:
                sheet.return_comment = "Please sharpen the target and rebalance weightage."
            db.add(sheet)
            db.flush()
            goals = [
                Goal(goal_sheet_id=sheet.id, thrust_area="Delivery", title="Ship priority roadmap items", description="Complete planned delivery milestones", uom_type=UomType.PERCENT_MIN, target_value=95, weightage=40, status=GoalStatus.ON_TRACK),
                Goal(goal_sheet_id=sheet.id, thrust_area="Quality", title="Reduce escaped defects", description="Improve release quality", uom_type=UomType.NUMERIC_MAX, target_value=5, weightage=30, status=GoalStatus.NOT_STARTED),
                Goal(goal_sheet_id=sheet.id, thrust_area="People", title="Run knowledge sharing sessions", description="Host enablement sessions", uom_type=UomType.NUMERIC_MIN, target_value=4, weightage=30, status=GoalStatus.NOT_STARTED),
            ]
            db.add_all(goals)
            db.flush()
            if status == GoalSheetStatus.APPROVED:
                for goal in goals:
                    actual = 80 if goal.uom_type == UomType.PERCENT_MIN else 3
                    db.add(CheckIn(goal_id=goal.id, quarter="Q1", actual_value=actual, status=GoalStatus.ON_TRACK, computed_progress_score=score_goal(goal, actual, None), employee_comment="Progress is on track."))
        db.add_all(
            [
                EscalationRule(name="Goals not submitted after 7 days", trigger_type="GOALS_NOT_SUBMITTED", threshold_days=7, notify_employee=True, notify_manager=True, notify_hr=True),
                EscalationRule(name="Manager approval delay", trigger_type="MANAGER_APPROVAL_DELAY", threshold_days=3, notify_employee=False, notify_manager=True, notify_hr=True),
            ]
        )
        db.flush()
        db.add(AuditLog(entity_type="GoalSheet", entity_id=1, action="APPROVE_AND_LOCK", changed_by_id=manager1.id, old_value=None, new_value="APPROVED"))
        db.add(EscalationLog(rule_id=1, user_id=employees[3].id, goal_sheet_id=4, message="Goal sheet is still in draft", level="WARN", status="OPEN"))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()

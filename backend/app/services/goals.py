from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import CheckIn, Cycle, Goal, GoalSheet, GoalSheetStatus, GoalStatus, Role, SharedGoal, UomType, User
from app.schemas import GoalIn, GoalPatch
from app.services.audit import log_action
from app.services.notifications import notify


def active_cycle(db: Session) -> Cycle:
    cycle = db.query(Cycle).filter(Cycle.status == "ACTIVE").first()
    if not cycle:
        raise HTTPException(400, "No active cycle configured")
    return cycle


def current_sheet(db: Session, employee: User) -> GoalSheet:
    cycle = active_cycle(db)
    sheet = db.query(GoalSheet).filter_by(employee_id=employee.id, cycle_id=cycle.id).first()
    if not sheet:
        if not employee.manager_id:
            raise HTTPException(400, "Employee has no manager assigned")
        sheet = GoalSheet(employee_id=employee.id, manager_id=employee.manager_id, cycle_id=cycle.id)
        db.add(sheet)
        db.flush()
    return sheet


def validate_goals(goals: list[GoalIn | Goal]):
    if len(goals) > 8:
        raise HTTPException(422, "A goal sheet can contain at most 8 goals")
    if any(float(goal.weightage) < 10 for goal in goals):
        raise HTTPException(422, "Each goal must have at least 10% weightage")
    total = round(sum(float(goal.weightage) for goal in goals), 2)
    if total != 100:
        raise HTTPException(422, f"Total weightage must be exactly 100%; current total is {total}%")


def replace_goals(db: Session, user: User, sheet: GoalSheet, goals: list[GoalIn]) -> GoalSheet:
    if sheet.status == GoalSheetStatus.APPROVED or sheet.locked_at:
        raise HTTPException(409, "Approved goals are locked")
    validate_goals(goals)
    sheet.goals.clear()
    db.flush()
    for item in goals:
        sheet.goals.append(Goal(**item.model_dump()))
    sheet.status = GoalSheetStatus.DRAFT if sheet.status != GoalSheetStatus.RETURNED else GoalSheetStatus.RETURNED
    log_action(db, user, "GoalSheet", sheet.id, "SAVE_DRAFT", None, {"goals": len(goals)})
    return sheet


def submit_sheet(db: Session, user: User, sheet: GoalSheet):
    if sheet.employee_id != user.id:
        raise HTTPException(403, "You can submit only your own goal sheet")
    if sheet.locked_at:
        raise HTTPException(409, "Goal sheet is locked")
    validate_goals(sheet.goals)
    sheet.status = GoalSheetStatus.SUBMITTED
    sheet.submitted_at = datetime.now(timezone.utc)
    sheet.return_comment = None
    notify(db, sheet.manager_id, "Goal sheet submitted", f"{user.name} submitted goals for approval")
    log_action(db, user, "GoalSheet", sheet.id, "SUBMIT", None, "SUBMITTED")


def manager_update_goal(db: Session, manager: User, goal: Goal, patch: GoalPatch):
    sheet = goal.goal_sheet
    if manager.role != Role.MANAGER or sheet.manager_id != manager.id:
        raise HTTPException(403, "Only the assigned manager can edit this goal")
    if sheet.status not in [GoalSheetStatus.SUBMITTED, GoalSheetStatus.RETURNED]:
        raise HTTPException(409, "Manager edits are allowed only after submission or rework")
    old = {"target_value": goal.target_value, "weightage": goal.weightage}
    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        if key in {"target_value", "target_date", "weightage", "status"}:
            setattr(goal, key, value)
    if goal.weightage < 10:
        raise HTTPException(422, "Each goal must have at least 10% weightage")
    log_action(db, manager, "Goal", goal.id, "MANAGER_EDIT_AFTER_SUBMISSION", old, data)
    return goal


def approve_sheet(db: Session, manager: User, sheet: GoalSheet):
    if sheet.manager_id != manager.id:
        raise HTTPException(403, "Only the assigned manager can approve")
    if sheet.status != GoalSheetStatus.SUBMITTED:
        raise HTTPException(409, "Only submitted sheets can be approved")
    validate_goals(sheet.goals)
    now = datetime.now(timezone.utc)
    sheet.status = GoalSheetStatus.APPROVED
    sheet.approved_at = now
    sheet.locked_at = now
    notify(db, sheet.employee_id, "Goals approved", "Your goals have been approved and locked")
    log_action(db, manager, "GoalSheet", sheet.id, "APPROVE_AND_LOCK", None, "APPROVED")


def return_sheet(db: Session, manager: User, sheet: GoalSheet, comment: str):
    if sheet.manager_id != manager.id:
        raise HTTPException(403, "Only the assigned manager can return this sheet")
    sheet.status = GoalSheetStatus.RETURNED
    sheet.return_comment = comment
    notify(db, sheet.employee_id, "Goals returned for rework", comment)
    log_action(db, manager, "GoalSheet", sheet.id, "RETURN_FOR_REWORK", None, comment)


def unlock_sheet(db: Session, admin: User, sheet: GoalSheet):
    if admin.role != Role.ADMIN:
        raise HTTPException(403, "Only admins can unlock goals")
    old = {"locked_at": sheet.locked_at, "status": sheet.status}
    sheet.locked_at = None
    sheet.status = GoalSheetStatus.RETURNED
    log_action(db, admin, "GoalSheet", sheet.id, "ADMIN_UNLOCK", old, {"status": "RETURNED"})


def score_goal(goal: Goal, actual_value: float | None, completion_date: date | None) -> float:
    actual = actual_value or 0
    target = goal.target_value or 0
    if goal.uom_type in [UomType.NUMERIC_MIN, UomType.PERCENT_MIN]:
        return min(round((actual / target) * 100, 2), 200) if target else 0
    if goal.uom_type in [UomType.NUMERIC_MAX, UomType.PERCENT_MAX]:
        return min(round((target / actual) * 100, 2), 200) if actual else 100
    if goal.uom_type == UomType.ZERO_BASED:
        return 100 if actual == 0 else 0
    if goal.uom_type == UomType.TIMELINE:
        if completion_date and goal.target_date and completion_date <= goal.target_date:
            return 100
        if completion_date and goal.target_date:
            delay = (completion_date - goal.target_date).days
            return max(0, 100 - delay * 5)
        return 0
    return 0


def upsert_check_in(db: Session, user: User, goal: Goal, payload) -> CheckIn:
    sheet = goal.goal_sheet
    if sheet.employee_id != user.id:
        raise HTTPException(403, "You can check in only your own goals")
    if sheet.status != GoalSheetStatus.APPROVED:
        raise HTTPException(409, "Check-ins are available after goals are approved")
    check_in = db.query(CheckIn).filter_by(goal_id=goal.id, quarter=payload.quarter).first()
    if not check_in:
        check_in = CheckIn(goal_id=goal.id, quarter=payload.quarter)
        db.add(check_in)
    check_in.actual_value = payload.actual_value
    check_in.completion_date = payload.completion_date
    check_in.status = payload.status
    check_in.employee_comment = payload.employee_comment
    check_in.computed_progress_score = score_goal(goal, payload.actual_value, payload.completion_date)
    check_in.submitted_at = datetime.now(timezone.utc)
    goal.status = payload.status
    if goal.shared_goal_id:
        shared = db.get(SharedGoal, goal.shared_goal_id)
        if shared and shared.primary_owner_id == user.id:
            linked_goals = db.query(Goal).filter(Goal.shared_goal_id == shared.id, Goal.id != goal.id).all()
            for linked_goal in linked_goals:
                linked = db.query(CheckIn).filter_by(goal_id=linked_goal.id, quarter=payload.quarter).first()
                if not linked:
                    linked = CheckIn(goal_id=linked_goal.id, quarter=payload.quarter)
                    db.add(linked)
                linked.actual_value = payload.actual_value
                linked.completion_date = payload.completion_date
                linked.status = payload.status
                linked.employee_comment = "Synced from primary owner achievement"
                linked.computed_progress_score = score_goal(linked_goal, payload.actual_value, payload.completion_date)
                linked.submitted_at = datetime.now(timezone.utc)
    return check_in

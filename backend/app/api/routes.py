from datetime import datetime, timezone
from io import BytesIO, StringIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import (
    AuditLog,
    CheckIn,
    Cycle,
    EscalationLog,
    EscalationRule,
    Goal,
    GoalSheet,
    GoalSheetStatus,
    Notification,
    Role,
    SharedGoal,
    User,
)
from app.schemas import (
    CheckInComment,
    CheckInCreate,
    CycleIn,
    EscalationRuleIn,
    GoalPatch,
    GoalSheetOut,
    GoalSheetUpsert,
    LoginRequest,
    ReturnRequest,
    SharedGoalAssign,
    SharedGoalCreate,
    SharedGoalOut,
    TokenResponse,
    UserCreate,
    UserOut,
)
from app.services.audit import log_action
from app.services.escalations import run_escalation_check
from app.services.goals import approve_sheet, current_sheet, manager_update_goal, replace_goals, return_sheet, submit_sheet, unlock_sheet, upsert_check_in

router = APIRouter(prefix="/api")


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_access_token(user.email), "user": user}


@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/notifications")
def notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(20).all()


@router.get("/employee/dashboard")
def employee_dashboard(user: User = Depends(require_roles(Role.EMPLOYEE)), db: Session = Depends(get_db)):
    sheet = current_sheet(db, user)
    scores = [c.computed_progress_score for goal in sheet.goals for c in db.query(CheckIn).filter_by(goal_id=goal.id).all()]
    return {
        "cycle": sheet.cycle.name,
        "sheet_status": sheet.status,
        "goal_count": len(sheet.goals),
        "progress_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "reminders": ["Q1 check-in window is open"] if sheet.status == GoalSheetStatus.APPROVED else ["Submit goals for manager approval"],
    }


@router.get("/goal-sheets/current", response_model=GoalSheetOut)
def get_current_goal_sheet(user: User = Depends(require_roles(Role.EMPLOYEE)), db: Session = Depends(get_db)):
    sheet = current_sheet(db, user)
    db.commit()
    db.refresh(sheet)
    return sheet


@router.post("/goal-sheets", response_model=GoalSheetOut)
def save_goal_sheet(payload: GoalSheetUpsert, user: User = Depends(require_roles(Role.EMPLOYEE)), db: Session = Depends(get_db)):
    sheet = current_sheet(db, user)
    replace_goals(db, user, sheet, payload.goals)
    db.commit()
    db.refresh(sheet)
    return sheet


@router.patch("/goal-sheets/{sheet_id}", response_model=GoalSheetOut)
def patch_goal_sheet(sheet_id: int, payload: GoalSheetUpsert, user: User = Depends(require_roles(Role.EMPLOYEE)), db: Session = Depends(get_db)):
    sheet = db.get(GoalSheet, sheet_id)
    if not sheet or sheet.employee_id != user.id:
        raise HTTPException(404, "Goal sheet not found")
    replace_goals(db, user, sheet, payload.goals)
    db.commit()
    db.refresh(sheet)
    return sheet


@router.post("/goal-sheets/{sheet_id}/submit")
def submit(sheet_id: int, user: User = Depends(require_roles(Role.EMPLOYEE)), db: Session = Depends(get_db)):
    sheet = db.get(GoalSheet, sheet_id)
    if not sheet:
        raise HTTPException(404, "Goal sheet not found")
    submit_sheet(db, user, sheet)
    db.commit()
    return {"message": "Submitted to manager"}


@router.post("/check-ins")
def create_check_in(payload: CheckInCreate, user: User = Depends(require_roles(Role.EMPLOYEE)), db: Session = Depends(get_db)):
    goal = db.get(Goal, payload.goal_id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    check_in = upsert_check_in(db, user, goal, payload)
    db.commit()
    db.refresh(check_in)
    return check_in


@router.get("/manager/dashboard")
def manager_dashboard(user: User = Depends(require_roles(Role.MANAGER)), db: Session = Depends(get_db)):
    team_ids = [u.id for u in db.query(User).filter_by(manager_id=user.id).all()]
    sheets = db.query(GoalSheet).filter(GoalSheet.employee_id.in_(team_ids)).all() if team_ids else []
    return {
        "team_size": len(team_ids),
        "pending_approvals": len([s for s in sheets if s.status == GoalSheetStatus.SUBMITTED]),
        "approved": len([s for s in sheets if s.status == GoalSheetStatus.APPROVED]),
        "returned": len([s for s in sheets if s.status == GoalSheetStatus.RETURNED]),
    }


@router.get("/manager/team")
def manager_team(user: User = Depends(require_roles(Role.MANAGER)), db: Session = Depends(get_db)):
    return db.query(User).filter_by(manager_id=user.id).all()


@router.get("/manager/approvals", response_model=list[GoalSheetOut])
def manager_approvals(user: User = Depends(require_roles(Role.MANAGER)), db: Session = Depends(get_db)):
    return db.query(GoalSheet).filter_by(manager_id=user.id).order_by(GoalSheet.submitted_at.desc()).all()


@router.get("/manager/goal-sheets/{sheet_id}", response_model=GoalSheetOut)
def manager_sheet(sheet_id: int, user: User = Depends(require_roles(Role.MANAGER)), db: Session = Depends(get_db)):
    sheet = db.get(GoalSheet, sheet_id)
    if not sheet or sheet.manager_id != user.id:
        raise HTTPException(404, "Goal sheet not found")
    return sheet


@router.patch("/manager/goals/{goal_id}")
def manager_goal_patch(goal_id: int, payload: GoalPatch, user: User = Depends(require_roles(Role.MANAGER)), db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    manager_update_goal(db, user, goal, payload)
    db.commit()
    return goal


@router.post("/manager/goal-sheets/{sheet_id}/approve")
def manager_approve(sheet_id: int, user: User = Depends(require_roles(Role.MANAGER)), db: Session = Depends(get_db)):
    sheet = db.get(GoalSheet, sheet_id)
    if not sheet:
        raise HTTPException(404, "Goal sheet not found")
    approve_sheet(db, user, sheet)
    db.commit()
    return {"message": "Approved and locked"}


@router.post("/manager/goal-sheets/{sheet_id}/return")
def manager_return(sheet_id: int, payload: ReturnRequest, user: User = Depends(require_roles(Role.MANAGER)), db: Session = Depends(get_db)):
    sheet = db.get(GoalSheet, sheet_id)
    if not sheet:
        raise HTTPException(404, "Goal sheet not found")
    return_sheet(db, user, sheet, payload.comment)
    db.commit()
    return {"message": "Returned for rework"}


@router.post("/manager/check-ins/{check_in_id}/comment")
def manager_check_in_comment(check_in_id: int, payload: CheckInComment, user: User = Depends(require_roles(Role.MANAGER)), db: Session = Depends(get_db)):
    check_in = db.get(CheckIn, check_in_id)
    if not check_in or check_in.goal.goal_sheet.manager_id != user.id:
        raise HTTPException(404, "Check-in not found")
    check_in.manager_comment = payload.manager_comment
    check_in.manager_checked_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Manager comment saved"}


@router.get("/manager/check-ins")
def manager_check_ins(user: User = Depends(require_roles(Role.MANAGER)), db: Session = Depends(get_db)):
    sheets = db.query(GoalSheet).filter_by(manager_id=user.id, status=GoalSheetStatus.APPROVED).all()
    rows = []
    for sheet in sheets:
        for goal in sheet.goals:
            check_ins = db.query(CheckIn).filter_by(goal_id=goal.id).order_by(CheckIn.quarter).all()
            if not check_ins:
                rows.append(
                    {
                        "employee": sheet.employee.name,
                        "goal_id": goal.id,
                        "goal": goal.title,
                        "target": goal.target_value,
                        "quarter": "Q1",
                        "actual": None,
                        "score": 0,
                        "status": goal.status,
                        "check_in_id": None,
                        "manager_comment": None,
                    }
                )
            for check_in in check_ins:
                rows.append(
                    {
                        "employee": sheet.employee.name,
                        "goal_id": goal.id,
                        "goal": goal.title,
                        "target": goal.target_value,
                        "quarter": check_in.quarter,
                        "actual": check_in.actual_value,
                        "score": check_in.computed_progress_score,
                        "status": check_in.status,
                        "check_in_id": check_in.id,
                        "manager_comment": check_in.manager_comment,
                    }
                )
    return rows


@router.get("/admin/dashboard")
def admin_dashboard(user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    sheets = db.query(GoalSheet).all()
    return {
        "users": db.query(User).count(),
        "goal_sheets": len(sheets),
        "approved": len([s for s in sheets if s.status == GoalSheetStatus.APPROVED]),
        "submitted": len([s for s in sheets if s.status == GoalSheetStatus.SUBMITTED]),
        "audit_logs": db.query(AuditLog).count(),
        "escalations": db.query(EscalationLog).filter_by(status="OPEN").count(),
    }


@router.get("/admin/cycles")
def list_cycles(user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    return db.query(Cycle).order_by(Cycle.year.desc()).all()


@router.post("/admin/cycles")
def create_cycle(payload: CycleIn, user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    cycle = Cycle(**payload.model_dump())
    db.add(cycle)
    db.commit()
    return cycle


@router.patch("/admin/cycles/{cycle_id}")
def update_cycle(cycle_id: int, payload: CycleIn, user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    cycle = db.get(Cycle, cycle_id)
    if not cycle:
        raise HTTPException(404, "Cycle not found")
    for key, value in payload.model_dump().items():
        setattr(cycle, key, value)
    db.commit()
    return cycle


@router.delete("/admin/cycles/{cycle_id}")
def delete_cycle(cycle_id: int, user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    cycle = db.get(Cycle, cycle_id)
    if not cycle:
        raise HTTPException(404, "Cycle not found")
    db.delete(cycle)
    db.commit()
    return {"message": "Cycle deleted"}


@router.get("/admin/users")
def list_users(user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.role, User.name).all()


@router.post("/admin/users")
def create_user(payload: UserCreate, user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    created = User(**payload.model_dump(exclude={"password"}), password_hash=hash_password(payload.password))
    db.add(created)
    db.commit()
    return created


@router.patch("/admin/users/{user_id}")
def update_user(user_id: int, payload: UserCreate, user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found")
    data = payload.model_dump(exclude={"password"})
    for key, value in data.items():
        setattr(target, key, value)
    if payload.password:
        target.password_hash = hash_password(payload.password)
    db.commit()
    return target


@router.delete("/admin/users/{user_id}")
def delete_user(user_id: int, user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found")
    db.delete(target)
    db.commit()
    return {"message": "User deleted"}


@router.post("/admin/goals/{sheet_id}/unlock")
def admin_unlock(sheet_id: int, user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    sheet = db.get(GoalSheet, sheet_id)
    if not sheet:
        raise HTTPException(404, "Goal sheet not found")
    unlock_sheet(db, user, sheet)
    db.commit()
    return {"message": "Unlocked and returned for controlled edits"}


@router.get("/admin/audit-logs")
def audit_logs(user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()


@router.get("/admin/completion-dashboard")
def completion_dashboard(user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    rows = db.query(GoalSheet.status, func.count(GoalSheet.id)).group_by(GoalSheet.status).all()
    return [{"status": status, "count": count} for status, count in rows]


@router.post("/admin/shared-goals", response_model=SharedGoalOut)
def create_shared_goal(payload: SharedGoalCreate, user: User = Depends(require_roles(Role.ADMIN, Role.MANAGER)), db: Session = Depends(get_db)):
    shared = SharedGoal(**payload.model_dump(), created_by_id=user.id)
    db.add(shared)
    db.commit()
    db.refresh(shared)
    return shared


@router.post("/admin/shared-goals/{shared_id}/assign")
def assign_shared_goal(shared_id: int, payload: SharedGoalAssign, user: User = Depends(require_roles(Role.ADMIN, Role.MANAGER)), db: Session = Depends(get_db)):
    shared = db.get(SharedGoal, shared_id)
    if not shared:
        raise HTTPException(404, "Shared goal not found")
    for employee_id in payload.employee_ids:
        employee = db.get(User, employee_id)
        if not employee:
            continue
        sheet = current_sheet(db, employee)
        sheet.goals.append(
            Goal(
                thrust_area=shared.thrust_area,
                title=shared.title,
                description=shared.description,
                uom_type=shared.uom_type,
                target_value=shared.target_value,
                weightage=payload.weightage,
                is_shared=True,
                shared_goal_id=shared.id,
                is_readonly_title_target=True,
            )
        )
        log_action(db, user, "SharedGoal", shared.id, "ASSIGN_SHARED_GOAL", None, employee.email)
    db.commit()
    return {"message": "Shared goal assigned"}


@router.get("/admin/reports/achievement/export/csv")
def export_csv(user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    output = StringIO()
    output.write("employee,department,goal,quarter,target,actual,score,status\n")
    for check in db.query(CheckIn).join(Goal).join(GoalSheet).join(User, GoalSheet.employee_id == User.id).all():
        output.write(f"{check.goal.goal_sheet.employee.name},{check.goal.goal_sheet.employee.department},{check.goal.title},{check.quarter},{check.goal.target_value},{check.actual_value},{check.computed_progress_score},{check.status}\n")
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=achievement-report.csv"})


@router.get("/admin/reports/achievement/export/xlsx")
def export_xlsx(user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Achievement Report"
    sheet.append(["Employee", "Department", "Goal", "Quarter", "Target", "Actual", "Score", "Status"])
    for check in db.query(CheckIn).join(Goal).join(GoalSheet).join(User, GoalSheet.employee_id == User.id).all():
        sheet.append([check.goal.goal_sheet.employee.name, check.goal.goal_sheet.employee.department, check.goal.title, check.quarter.value, check.goal.target_value, check.actual_value, check.computed_progress_score, check.status.value])
    stream = BytesIO()
    workbook.save(stream)
    stream.seek(0)
    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=achievement-report.xlsx"})


@router.get("/analytics/qoq-trends")
def qoq_trends(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(CheckIn.quarter, func.avg(CheckIn.computed_progress_score)).group_by(CheckIn.quarter).all()
    return [{"quarter": quarter, "score": round(score or 0, 1)} for quarter, score in rows]


@router.get("/analytics/goal-distribution")
def goal_distribution(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    by_status = db.query(Goal.status, func.count(Goal.id)).group_by(Goal.status).all()
    by_uom = db.query(Goal.uom_type, func.count(Goal.id)).group_by(Goal.uom_type).all()
    return {"status": [{"name": k, "value": v} for k, v in by_status], "uom": [{"name": k, "value": v} for k, v in by_uom]}


@router.get("/analytics/manager-effectiveness")
def manager_effectiveness(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    managers = db.query(User).filter_by(role=Role.MANAGER).all()
    return [
        {
            "manager": manager.name,
            "team_size": db.query(User).filter_by(manager_id=manager.id).count(),
            "approved": db.query(GoalSheet).filter_by(manager_id=manager.id, status=GoalSheetStatus.APPROVED).count(),
        }
        for manager in managers
    ]


@router.get("/analytics/completion-heatmap")
def completion_heatmap(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(User.department, GoalSheet.status, func.count(GoalSheet.id)).join(GoalSheet, GoalSheet.employee_id == User.id).group_by(User.department, GoalSheet.status).all()
    return [{"department": department, "status": status, "count": count} for department, status, count in rows]


@router.get("/admin/escalation-rules")
def list_escalation_rules(user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    return db.query(EscalationRule).all()


@router.post("/admin/escalation-rules")
def create_escalation_rule(payload: EscalationRuleIn, user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    rule = EscalationRule(**payload.model_dump())
    db.add(rule)
    db.commit()
    return rule


@router.get("/admin/escalation-logs")
def list_escalation_logs(user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    return db.query(EscalationLog).order_by(EscalationLog.created_at.desc()).limit(100).all()


@router.post("/admin/run-escalation-check")
def run_escalations(user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    count = run_escalation_check(db)
    db.commit()
    return {"message": f"Created {count} escalation logs"}

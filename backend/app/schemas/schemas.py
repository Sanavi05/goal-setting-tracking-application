from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.entities import GoalSheetStatus, GoalStatus, Quarter, Role, UomType


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: Role
    department: str
    manager_id: int | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = "password123"
    role: Role
    department: str
    manager_id: int | None = None


class CycleIn(BaseModel):
    name: str
    year: int
    status: str = "ACTIVE"
    goal_setting_open_date: date
    q1_open_date: date
    q2_open_date: date
    q3_open_date: date
    q4_open_date: date


class CycleOut(CycleIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class GoalIn(BaseModel):
    thrust_area: str
    title: str
    description: str = ""
    uom_type: UomType
    target_value: float | None = None
    target_date: date | None = None
    weightage: float = Field(ge=10, le=100)


class GoalPatch(BaseModel):
    thrust_area: str | None = None
    title: str | None = None
    description: str | None = None
    uom_type: UomType | None = None
    target_value: float | None = None
    target_date: date | None = None
    weightage: float | None = Field(default=None, ge=10, le=100)
    status: GoalStatus | None = None


class GoalOut(GoalIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    goal_sheet_id: int
    status: GoalStatus
    is_shared: bool
    shared_goal_id: int | None
    is_readonly_title_target: bool


class GoalSheetUpsert(BaseModel):
    goals: list[GoalIn]


class GoalSheetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    manager_id: int
    cycle_id: int
    status: GoalSheetStatus
    submitted_at: datetime | None
    approved_at: datetime | None
    locked_at: datetime | None
    return_comment: str | None
    goals: list[GoalOut] = []


class ReturnRequest(BaseModel):
    comment: str


class CheckInCreate(BaseModel):
    goal_id: int
    quarter: Quarter
    actual_value: float | None = None
    completion_date: date | None = None
    status: GoalStatus
    employee_comment: str | None = None


class CheckInComment(BaseModel):
    manager_comment: str


class CheckInOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    goal_id: int
    quarter: Quarter
    actual_value: float | None
    completion_date: date | None
    status: GoalStatus
    computed_progress_score: float
    employee_comment: str | None
    manager_comment: str | None


class SharedGoalCreate(BaseModel):
    title: str
    description: str
    thrust_area: str
    uom_type: UomType
    target_value: float | None = None
    primary_owner_id: int


class SharedGoalOut(SharedGoalCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_by_id: int


class SharedGoalAssign(BaseModel):
    employee_ids: list[int]
    weightage: float = Field(ge=10, le=100)


class EscalationRuleIn(BaseModel):
    name: str
    trigger_type: str
    threshold_days: int
    notify_employee: bool = True
    notify_manager: bool = True
    notify_hr: bool = False
    active: bool = True


class GenericMessage(BaseModel):
    message: str

import enum
from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Role(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class CycleStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DRAFT = "DRAFT"


class GoalSheetStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    RETURNED = "RETURNED"


class UomType(str, enum.Enum):
    NUMERIC_MIN = "NUMERIC_MIN"
    NUMERIC_MAX = "NUMERIC_MAX"
    PERCENT_MIN = "PERCENT_MIN"
    PERCENT_MAX = "PERCENT_MAX"
    TIMELINE = "TIMELINE"
    ZERO_BASED = "ZERO_BASED"


class GoalStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    ON_TRACK = "ON_TRACK"
    COMPLETED = "COMPLETED"
    AT_RISK = "AT_RISK"


class Quarter(str, enum.Enum):
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role))
    department: Mapped[str] = mapped_column(String(80))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    manager = relationship("User", remote_side=[id])


class Cycle(Base):
    __tablename__ = "cycles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    year: Mapped[int] = mapped_column(Integer)
    status: Mapped[CycleStatus] = mapped_column(Enum(CycleStatus), default=CycleStatus.ACTIVE)
    goal_setting_open_date = mapped_column(Date)
    q1_open_date = mapped_column(Date)
    q2_open_date = mapped_column(Date)
    q3_open_date = mapped_column(Date)
    q4_open_date = mapped_column(Date)


class GoalSheet(Base):
    __tablename__ = "goal_sheets"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("cycles.id"), index=True)
    status: Mapped[GoalSheetStatus] = mapped_column(Enum(GoalSheetStatus), default=GoalSheetStatus.DRAFT)
    submitted_at = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at = mapped_column(DateTime(timezone=True), nullable=True)
    locked_at = mapped_column(DateTime(timezone=True), nullable=True)
    return_comment: Mapped[str | None] = mapped_column(Text)

    employee = relationship("User", foreign_keys=[employee_id])
    manager = relationship("User", foreign_keys=[manager_id])
    cycle = relationship("Cycle")
    goals = relationship("Goal", back_populates="goal_sheet", cascade="all, delete-orphan")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    goal_sheet_id: Mapped[int] = mapped_column(ForeignKey("goal_sheets.id"), index=True)
    thrust_area: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(220))
    description: Mapped[str] = mapped_column(Text)
    uom_type: Mapped[UomType] = mapped_column(Enum(UomType))
    target_value: Mapped[float | None] = mapped_column(Float)
    target_date = mapped_column(Date, nullable=True)
    weightage: Mapped[float] = mapped_column(Float)
    status: Mapped[GoalStatus] = mapped_column(Enum(GoalStatus), default=GoalStatus.NOT_STARTED)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    shared_goal_id: Mapped[int | None] = mapped_column(ForeignKey("shared_goals.id"))
    is_readonly_title_target: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    goal_sheet = relationship("GoalSheet", back_populates="goals")


class SharedGoal(Base):
    __tablename__ = "shared_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(220))
    description: Mapped[str] = mapped_column(Text)
    thrust_area: Mapped[str] = mapped_column(String(120))
    uom_type: Mapped[UomType] = mapped_column(Enum(UomType))
    target_value: Mapped[float | None] = mapped_column(Float)
    primary_owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class CheckIn(Base):
    __tablename__ = "check_ins"

    id: Mapped[int] = mapped_column(primary_key=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id"), index=True)
    quarter: Mapped[Quarter] = mapped_column(Enum(Quarter))
    actual_value: Mapped[float | None] = mapped_column(Float)
    completion_date = mapped_column(Date, nullable=True)
    status: Mapped[GoalStatus] = mapped_column(Enum(GoalStatus))
    computed_progress_score: Mapped[float] = mapped_column(Float, default=0)
    employee_comment: Mapped[str | None] = mapped_column(Text)
    manager_comment: Mapped[str | None] = mapped_column(Text)
    submitted_at = mapped_column(DateTime(timezone=True), nullable=True)
    manager_checked_at = mapped_column(DateTime(timezone=True), nullable=True)

    goal = relationship("Goal")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(160))
    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class EscalationRule(Base):
    __tablename__ = "escalation_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    trigger_type: Mapped[str] = mapped_column(String(80))
    threshold_days: Mapped[int] = mapped_column(Integer)
    notify_employee: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_manager: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_hr: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class EscalationLog(Base):
    __tablename__ = "escalation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("escalation_rules.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    goal_sheet_id: Mapped[int | None] = mapped_column(ForeignKey("goal_sheets.id"))
    message: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(40), default="INFO")
    status: Mapped[str] = mapped_column(String(40), default="OPEN")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(180))
    message: Mapped[str] = mapped_column(Text)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

from sqlalchemy.orm import Session

from app.models import AuditLog, User


def log_action(db: Session, user: User, entity_type: str, entity_id: int, action: str, old_value=None, new_value=None):
    db.add(
        AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            changed_by_id=user.id,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
        )
    )

from sqlalchemy.orm import Session

from app.models import Notification


def notify(db: Session, user_id: int, title: str, message: str, type_: str = "WORKFLOW"):
    db.add(Notification(user_id=user_id, title=title, message=message, type=type_))


def teams_adaptive_card(title: str, message: str) -> dict:
    return {
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": [
            {"type": "TextBlock", "text": title, "weight": "Bolder"},
            {"type": "TextBlock", "text": message, "wrap": True},
        ],
    }

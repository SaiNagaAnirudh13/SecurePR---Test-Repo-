import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Notification

logger = logging.getLogger(__name__)


def process_pending_notifications(db: Session, batch_size: int = 50) -> int:
    messages = db.scalars(
        select(Notification)
        .where(Notification.status == "pending")
        .order_by(Notification.created_at)
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    ).all()
    for message in messages:
        try:
            logger.info(
                "notification_dispatched",
                extra={"event_type": message.event_type, "recipient": message.recipient},
            )
            message.status = "sent"
            message.processed_at = datetime.now(UTC)
            message.attempts += 1
        except Exception as exc:
            message.status = "failed"
            message.last_error = str(exc)[:1000]
            message.attempts += 1
    db.commit()
    return len(messages)

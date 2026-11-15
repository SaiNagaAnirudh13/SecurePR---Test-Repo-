import logging
import signal
import time

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.logging import configure_logging
from app.services.notifications import process_pending_notifications

configure_logging()
logger = logging.getLogger(__name__)
running = True


def stop_worker(_signum: int, _frame: object) -> None:
    global running
    running = False


def run() -> None:
    signal.signal(signal.SIGTERM, stop_worker)
    signal.signal(signal.SIGINT, stop_worker)
    logger.info("notification_worker_started")
    while running:
        with SessionLocal() as db:
            processed = process_pending_notifications(db)
        if processed == 0:
            time.sleep(settings.worker_poll_seconds)
    logger.info("notification_worker_stopped")


if __name__ == "__main__":
    run()

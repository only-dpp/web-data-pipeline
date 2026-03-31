import logging

from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.subscriber_digest_service import (
    send_daily_digest_to_all_subscribers,
    send_welcome_email_to_subscriber,
)


logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.notification_tasks.send_welcome_email_task")
def send_welcome_email_task(subscriber_id: int):
    db = SessionLocal()
    try:
        return send_welcome_email_to_subscriber(db, subscriber_id)
    finally:
        db.close()


@celery_app.task(name="app.tasks.notification_tasks.send_daily_digest_task")
def send_daily_digest_task():
    db = SessionLocal()
    try:
        return send_daily_digest_to_all_subscribers(db)
    finally:
        db.close()

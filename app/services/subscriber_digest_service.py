import logging
from datetime import datetime, UTC
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_env, get_int_env
from app.models.digest_dispatch import DigestDispatch
from app.models.email_delivery import EmailDelivery
from app.models.subscriber import Subscriber
from app.services.digest_service import get_digest_preview_html
from app.services.digest_render_service import render_welcome_email_html
from app.services.email_service import send_html_email


logger = logging.getLogger(__name__)


def get_digest_timezone_name() -> str:
    return get_env("DIGEST_TIMEZONE", "America/Sao_Paulo")


def get_digest_schedule_config() -> dict:
    return {
        "hour": get_int_env("DIGEST_SEND_HOUR", 8),
        "minute": get_int_env("DIGEST_SEND_MINUTE", 0),
        "hours_window": get_int_env("DIGEST_LOOKBACK_HOURS", 24),
        "limit": get_int_env("DIGEST_ITEMS_LIMIT", 10),
    }


def get_digest_local_now() -> datetime:
    return datetime.now(ZoneInfo(get_digest_timezone_name()))


def list_active_subscribers(db: Session) -> list[Subscriber]:
    return (
        db.query(Subscriber)
        .filter(Subscriber.is_active.is_(True))
        .order_by(Subscriber.created_at.asc())
        .all()
    )


def create_daily_dispatch(
    db: Session,
    digest_date,
    hours: int,
    limit: int,
) -> tuple[DigestDispatch, bool]:
    existing_dispatch = (
        db.query(DigestDispatch)
        .filter(DigestDispatch.digest_date == digest_date)
        .first()
    )

    if existing_dispatch:
        return existing_dispatch, False

    dispatch = DigestDispatch(
        digest_date=digest_date,
        status="running",
        hours=hours,
        limit=limit,
    )
    db.add(dispatch)

    try:
        db.commit()
        db.refresh(dispatch)
        return dispatch, True
    except IntegrityError:
        db.rollback()
        recovered_dispatch = (
            db.query(DigestDispatch)
            .filter(DigestDispatch.digest_date == digest_date)
            .first()
        )
        if recovered_dispatch:
            return recovered_dispatch, False
        raise


def create_email_delivery(
    db: Session,
    *,
    subscriber: Subscriber,
    dispatch_id: int | None,
    email_type: str,
    subject: str,
    status: str,
    error_message: str | None = None,
):
    delivery = EmailDelivery(
        subscriber_id=subscriber.id,
        dispatch_id=dispatch_id,
        email=subscriber.email,
        email_type=email_type,
        subject=subject,
        status=status,
        error_message=error_message,
        sent_at=datetime.now(UTC) if status == "sent" else None,
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery


def send_welcome_email_to_subscriber(db: Session, subscriber_id: int) -> dict:
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()

    if not subscriber or not subscriber.is_active:
        return {"status": "skipped", "reason": "subscriber not active"}

    if subscriber.welcome_sent_at is not None:
        return {"status": "skipped", "reason": "welcome email already sent"}

    subject = "Bem-vindo ao seu digest diário de tecnologia"
    html_content = render_welcome_email_html(subscriber.email)

    try:
        send_html_email(
            to_email=subscriber.email,
            subject=subject,
            html_content=html_content,
        )
        subscriber.welcome_sent_at = datetime.now(UTC)
        db.commit()
        create_email_delivery(
            db,
            subscriber=subscriber,
            dispatch_id=None,
            email_type="welcome",
            subject=subject,
            status="sent",
        )
        logger.info("Welcome email sent to subscriber_id=%s", subscriber.id)
        return {"status": "sent", "subscriber_id": subscriber.id}
    except Exception as exc:
        db.rollback()
        create_email_delivery(
            db,
            subscriber=subscriber,
            dispatch_id=None,
            email_type="welcome",
            subject=subject,
            status="failed",
            error_message=str(exc)[:500],
        )
        logger.exception("Failed to send welcome email to subscriber_id=%s", subscriber.id)
        raise


def send_daily_digest_to_all_subscribers(
    db: Session,
    *,
    hours: int | None = None,
    limit: int | None = None,
) -> dict:
    config = get_digest_schedule_config()
    digest_hours = hours or config["hours_window"]
    digest_limit = limit or config["limit"]
    local_now = get_digest_local_now()
    digest_date = local_now.date()

    dispatch, created = create_daily_dispatch(
        db=db,
        digest_date=digest_date,
        hours=digest_hours,
        limit=digest_limit,
    )

    if not created:
        logger.info("Digest dispatch already exists for date=%s status=%s", digest_date, dispatch.status)
        return {
            "status": "skipped",
            "reason": "digest already dispatched for this date",
            "dispatch_id": dispatch.id,
            "digest_date": str(digest_date),
        }

    subscribers = list_active_subscribers(db)
    dispatch.subscribers_targeted = len(subscribers)
    db.commit()

    subject = f"Seu digest diário de tecnologia - {local_now.strftime('%d/%m/%Y')}"
    html_content = get_digest_preview_html(db=db, hours=digest_hours, limit=digest_limit)

    sent_count = 0
    failed_count = 0

    try:
        for subscriber in subscribers:
            try:
                send_html_email(
                    to_email=subscriber.email,
                    subject=subject,
                    html_content=html_content,
                )
                subscriber.last_digest_sent_at = datetime.now(UTC)
                db.commit()
                create_email_delivery(
                    db,
                    subscriber=subscriber,
                    dispatch_id=dispatch.id,
                    email_type="digest",
                    subject=subject,
                    status="sent",
                )
                sent_count += 1
            except Exception as exc:
                db.rollback()
                create_email_delivery(
                    db,
                    subscriber=subscriber,
                    dispatch_id=dispatch.id,
                    email_type="digest",
                    subject=subject,
                    status="failed",
                    error_message=str(exc)[:500],
                )
                failed_count += 1
                logger.exception("Failed to send daily digest to subscriber_id=%s", subscriber.id)

        dispatch.subscribers_sent = sent_count
        dispatch.subscribers_failed = failed_count
        dispatch.status = "finished" if failed_count == 0 else "partial_failed"
        dispatch.finished_at = datetime.now(UTC)
        db.commit()

        logger.info(
            "Daily digest dispatch completed dispatch_id=%s sent=%s failed=%s",
            dispatch.id,
            sent_count,
            failed_count,
        )
        return {
            "status": dispatch.status,
            "dispatch_id": dispatch.id,
            "digest_date": str(digest_date),
            "subscribers_targeted": dispatch.subscribers_targeted,
            "subscribers_sent": sent_count,
            "subscribers_failed": failed_count,
        }
    except Exception as exc:
        db.rollback()
        dispatch.status = "failed"
        dispatch.error_message = str(exc)[:500]
        dispatch.finished_at = datetime.now(UTC)
        db.commit()
        logger.exception("Daily digest dispatch failed dispatch_id=%s", dispatch.id)
        raise

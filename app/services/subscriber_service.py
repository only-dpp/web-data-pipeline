from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.source import Source
from app.models.subscriber import Subscriber


def subscribe_email(db: Session, email: str) -> tuple[Subscriber, str]:
    normalized_email = email.strip().lower()

    existing_subscriber = (
        db.query(Subscriber)
        .filter(Subscriber.email == normalized_email)
        .first()
    )

    if existing_subscriber:
        if not existing_subscriber.is_active:
            existing_subscriber.is_active = True
            db.commit()
            db.refresh(existing_subscriber)
            return existing_subscriber, "reactivated"

        return existing_subscriber, "existing"

    subscriber = Subscriber(
        email=normalized_email,
        is_active=True,
    )
    db.add(subscriber)

    try:
        db.commit()
        db.refresh(subscriber)
        return subscriber, "created"
    except IntegrityError:
        db.rollback()
        recovered_subscriber = (
            db.query(Subscriber)
            .filter(Subscriber.email == normalized_email)
            .first()
        )
        if recovered_subscriber:
            return recovered_subscriber, "existing"
        raise


def get_landing_stats(db: Session) -> dict:
    source_count = db.query(func.count(Source.id)).scalar() or 0
    article_count = db.query(func.count(Article.id)).scalar() or 0
    subscriber_count = (
        db.query(func.count(Subscriber.id))
        .filter(Subscriber.is_active.is_(True))
        .scalar()
        or 0
    )

    return {
        "source_count": source_count,
        "article_count": article_count,
        "subscriber_count": subscriber_count,
    }

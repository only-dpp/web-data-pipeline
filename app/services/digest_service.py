from datetime import datetime, UTC, timedelta
from sqlalchemy.orm import Session

from app.models.article import Article
from app.services.digest_ranking_service import rank_articles
from app.services.digest_selection_service import build_digest_sections
from app.services.digest_render_service import render_digest_html


def get_recent_articles(db: Session, hours: int = 24) -> list[Article]:
    cutoff = datetime.now(UTC) - timedelta(hours=hours)

    return (
        db.query(Article)
        .filter(Article.collected_at >= cutoff)
        .order_by(Article.collected_at.desc())
        .all()
    )


def get_digest_preview(db: Session, hours: int = 24, limit: int = 10) -> dict:
    articles = get_recent_articles(db, hours=hours)
    ranked_articles = rank_articles(articles)

    return build_digest_sections(
        ranked_articles=ranked_articles,
        total_limit=limit,
    )


def get_digest_preview_html(db: Session, hours: int = 24, limit: int = 10) -> str:
    digest_data = get_digest_preview(db=db, hours=hours, limit=limit)
    return render_digest_html(digest_data)
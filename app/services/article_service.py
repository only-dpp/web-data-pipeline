from sqlalchemy.orm import Session

from app.models.article import Article


def list_articles(db: Session, source_id: int | None = None) -> list[Article]:
    query = db.query(Article)

    if source_id is not None:
        query = query.filter(Article.source_id == source_id)

    return query.order_by(Article.id.desc()).all()
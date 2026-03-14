from sqlalchemy.orm import Session

from app.models.source import Source
from app.schemas.source import SourceCreate


def create_source(db: Session, source_data: SourceCreate) -> Source:
    source = Source(
        name=source_data.name,
        base_url=source_data.base_url,
        list_url=source_data.list_url,
        list_selector=source_data.list_selector,
        title_selector=source_data.title_selector,
        link_selector=source_data.link_selector,
        summary_selector=source_data.summary_selector,
        schedule_minutes=source_data.schedule_minutes,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


def list_sources(db: Session) -> list[Source]:
    return db.query(Source).all()
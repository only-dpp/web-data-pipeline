from sqlalchemy.orm import Session

from app.models.source import Source
from app.scrapers.html_scraper import scrape_source


def run_source_scraper(db: Session, source_id: int) -> list[dict]:
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise ValueError("Fonte não encontrada")

    return scrape_source(source)
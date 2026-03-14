from sqlalchemy.orm import Session

from app.models.source import Source
from app.models.run import Run
from app.models.record import Record
from app.scrapers.html_scraper import scrape_source


def run_source_scraper(db: Session, source_id: int) -> dict:
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise ValueError("Fonte não encontrada")

    run = Run(
        source_id=source.id,
        status="running"
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    scraped_records = scrape_source(source)

    for item in scraped_records:
        record = Record(
            source_id=source.id,
            title=item["title"],
            url=item["url"],
            summary=item["summary"],
            hash=None,
            published_at=None,
        )
        db.add(record)

    run.status = "finished"
    run.items_found = len(scraped_records)
    run.items_new = len(scraped_records)

    db.commit()
    db.refresh(run)

    return {
        "run_id": run.id,
        "source_id": source.id,
        "status": run.status,
        "items_found": run.items_found,
        "items_new": run.items_new,
    }
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.source import Source
from app.models.run import Run
from app.models.record import Record
from app.scrapers.html_scraper import scrape_source
from app.services.hash_service import generate_record_hash


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

    items_new = 0

    for item in scraped_records:
        record_hash = generate_record_hash(item["title"], item["url"])

        existing_record = db.query(Record).filter(Record.hash == record_hash).first()
        if existing_record:
            continue

        record = Record(
            source_id=source.id,
            title=item["title"],
            url=item["url"],
            summary=item["summary"],
            hash=record_hash,
            published_at=None,
        )
        db.add(record)
        items_new += 1

    run.status = "finished"
    run.items_found = len(scraped_records)
    run.items_new = items_new

    db.commit()
    db.refresh(run)

    return {
        "run_id": run.id,
        "source_id": source.id,
        "status": run.status,
        "items_found": run.items_found,
        "items_new": run.items_new,
    }
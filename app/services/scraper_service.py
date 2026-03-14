from datetime import datetime, UTC

from sqlalchemy.orm import Session

from app.models.source import Source
from app.models.run import Run
from app.models.article import Article
from app.scrapers.html_scraper import scrape_source
from app.services.hash_service import generate_record_hash
from app.services.article_excerpt_service import extract_article_excerpt


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

    try:
        scraped_records = scrape_source(source)

        items_new = 0
        seen_hashes = set()

        for item in scraped_records:
            article_hash = generate_record_hash(item["title"], item["url"])

            # evita duplicata dentro da mesma coleta
            if article_hash in seen_hashes:
                continue

            seen_hashes.add(article_hash)

            existing_article = db.query(Article).filter(Article.hash == article_hash).first()
            if existing_article:
                continue

            summary = item["summary"]
            if not summary:
                summary = extract_article_excerpt(item["url"])

            article = Article(
                source_id=source.id,
                title=item["title"],
                url=item["url"],
                summary=summary,
                hash=article_hash,
                published_at=None,
            )
            db.add(article)
            items_new += 1

        run.status = "finished"
        run.items_found = len(scraped_records)
        run.items_new = items_new
        run.finished_at = datetime.now(UTC)

        db.commit()
        db.refresh(run)

        return {
            "run_id": run.id,
            "source_id": source.id,
            "status": run.status,
            "items_found": run.items_found,
            "items_new": run.items_new,
            "finished_at": run.finished_at,
        }

    except Exception as e:
        db.rollback()  # importante
        run.status = "failed"
        run.finished_at = datetime.now(UTC)

        db.add(run)
        db.commit()

        raise e

from datetime import datetime, UTC
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.run import Run
from app.models.source import Source
from app.scrapers.html_scraper import scrape_source
from app.services.article_excerpt_service import extract_article_excerpt
from app.services.hash_service import generate_record_hash

logger = logging.getLogger(__name__)


def get_run_guard_window_minutes(schedule_minutes: int | None) -> int:
    return max(schedule_minutes or 0, 15)


def get_recent_running_run(
    db: Session,
    source_id: int,
    reference_time: datetime | None = None,
    guard_window_minutes: int = 15,
) -> Run | None:
    now = reference_time or datetime.now(UTC)

    running_run = (
        db.query(Run)
        .filter(Run.source_id == source_id, Run.status == "running")
        .order_by(Run.started_at.desc())
        .first()
    )

    if not running_run:
        return None

    if running_run.started_at is None:
        return running_run

    elapsed_minutes = (now - running_run.started_at).total_seconds() / 60

    if elapsed_minutes <= guard_window_minutes:
        return running_run

    return None


def run_source_scraper(db: Session, source_id: int) -> dict:
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise ValueError("Fonte não encontrada")

    now = datetime.now(UTC)
    running_run = get_recent_running_run(
        db=db,
        source_id=source.id,
        reference_time=now,
        guard_window_minutes=get_run_guard_window_minutes(source.schedule_minutes),
    )

    if running_run:
        logger.info("Skipping scraper run because source_id=%s is already running", source.id)
        return {
            "run_id": running_run.id,
            "source_id": source.id,
            "status": "skipped",
            "reason": "source already running",
            "started_at": running_run.started_at,
        }

    run = Run(
        source_id=source.id,
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    logger.info("Started scraper run run_id=%s source_id=%s", run.id, source.id)

    try:
        scraped_records = scrape_source(source)

        items_new = 0
        seen_hashes = set()

        for item in scraped_records:
            article_hash = generate_record_hash(item["title"], item["url"])

            # Evita duplicata dentro da mesma coleta.
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

            try:
                with db.begin_nested():
                    db.add(article)
                    db.flush()
                items_new += 1
            except IntegrityError:
                logger.info("Ignoring concurrent duplicate article for source_id=%s hash=%s", source.id, article_hash)
                continue

        run.status = "finished"
        run.items_found = len(scraped_records)
        run.items_new = items_new
        run.finished_at = datetime.now(UTC)

        db.commit()
        db.refresh(run)
        logger.info(
            "Finished scraper run run_id=%s source_id=%s items_found=%s items_new=%s",
            run.id,
            source.id,
            run.items_found,
            run.items_new,
        )

        return {
            "run_id": run.id,
            "source_id": source.id,
            "status": run.status,
            "items_found": run.items_found,
            "items_new": run.items_new,
            "finished_at": run.finished_at,
        }

    except Exception:
        db.rollback()
        run.status = "failed"
        run.finished_at = datetime.now(UTC)

        db.add(run)
        db.commit()
        logger.exception("Scraper run failed run_id=%s source_id=%s", run.id, source.id)

        raise

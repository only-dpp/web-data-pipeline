from datetime import datetime, UTC
import logging

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.run import Run
from app.models.source import Source
from app.services.scraper_service import get_recent_running_run, get_run_guard_window_minutes
from app.tasks.scraper_tasks import run_scraper_task

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.scheduler_tasks.check_scheduled_sources_task")
def check_scheduled_sources_task():
    db = SessionLocal()
    sources = []
    triggered_sources = []
    skipped_running_sources = []

    try:
        now = datetime.now(UTC)
        sources = db.query(Source).all()

        for source in sources:
            running_run = get_recent_running_run(
                db=db,
                source_id=source.id,
                reference_time=now,
                guard_window_minutes=get_run_guard_window_minutes(source.schedule_minutes),
            )

            if running_run:
                skipped_running_sources.append(source.id)
                continue

            last_run = (
                db.query(Run)
                .filter(Run.source_id == source.id, Run.status == "finished")
                .order_by(Run.finished_at.desc())
                .first()
            )

            if last_run is None:
                run_scraper_task.delay(source.id)
                triggered_sources.append(source.id)
                continue

            if last_run.finished_at is None:
                continue

            elapsed_minutes = (now - last_run.finished_at).total_seconds() / 60

            if elapsed_minutes >= source.schedule_minutes:
                run_scraper_task.delay(source.id)
                triggered_sources.append(source.id)

        return {
            "checked_sources": len(sources),
            "triggered_sources": triggered_sources,
            "skipped_running_sources": skipped_running_sources,
        }

    finally:
        logger.info(
            "Scheduler cycle completed checked=%s triggered=%s skipped_running=%s",
            len(sources),
            len(triggered_sources),
            len(skipped_running_sources),
        )
        db.close()

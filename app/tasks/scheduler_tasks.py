from datetime import datetime, UTC

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.source import Source
from app.models.run import Run
from app.tasks.scraper_tasks import run_scraper_task


@celery_app.task(name="app.tasks.scheduler_tasks.check_scheduled_sources_task")
def check_scheduled_sources_task():
    db = SessionLocal()

    try:
        now = datetime.now(UTC)
        sources = db.query(Source).all()

        triggered_sources = []

        for source in sources:
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
        }

    finally:
        db.close()
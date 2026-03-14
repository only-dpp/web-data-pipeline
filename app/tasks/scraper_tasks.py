from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.scraper_service import run_source_scraper


@celery_app.task(name="app.tasks.scraper_tasks.run_scraper_task")
def run_scraper_task(source_id: int):
    db = SessionLocal()
    try:
        return run_source_scraper(db, source_id)
    finally:
        db.close()
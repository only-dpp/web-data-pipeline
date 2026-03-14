from celery import Celery

celery_app = Celery(
    "web_data_pipeline",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks.scraper_tasks"],
)

celery_app.conf.task_routes = {
    "app.tasks.scraper_tasks.run_scraper_task": {"queue": "scrapers"}
}
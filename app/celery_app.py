from celery import Celery

celery_app = Celery(
    "web_data_pipeline",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=[
        "app.tasks.scraper_tasks",
        "app.tasks.scheduler_tasks",
    ],
)

celery_app.conf.task_routes = {
    "app.tasks.scraper_tasks.run_scraper_task": {"queue": "scrapers"},
    "app.tasks.scheduler_tasks.check_scheduled_sources_task": {"queue": "scheduler"},
}

celery_app.conf.beat_schedule = {
    "check-sources-every-5-minutes": {
        "task": "app.tasks.scheduler_tasks.check_scheduled_sources_task",
        "schedule": 300.0,
    },
}
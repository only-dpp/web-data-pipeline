import os

from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab

from app.core.config import get_env, get_int_env, get_redis_url

load_dotenv()

REDIS_URL = get_redis_url()
DIGEST_TIMEZONE = get_env("DIGEST_TIMEZONE", "America/Sao_Paulo")
DIGEST_SEND_HOUR = get_int_env("DIGEST_SEND_HOUR", 8)
DIGEST_SEND_MINUTE = get_int_env("DIGEST_SEND_MINUTE", 0)

celery_app = Celery(
    "web_data_pipeline",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.notification_tasks",
        "app.tasks.scraper_tasks",
        "app.tasks.scheduler_tasks",
    ],
)

celery_app.conf.timezone = DIGEST_TIMEZONE
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_routes = {
    "app.tasks.notification_tasks.send_daily_digest_task": {"queue": "notifications"},
    "app.tasks.notification_tasks.send_welcome_email_task": {"queue": "notifications"},
    "app.tasks.scraper_tasks.run_scraper_task": {"queue": "scrapers"},
    "app.tasks.scheduler_tasks.check_scheduled_sources_task": {"queue": "scheduler"},
}

celery_app.conf.beat_schedule = {
    "check-sources-every-5-minutes": {
        "task": "app.tasks.scheduler_tasks.check_scheduled_sources_task",
        "schedule": 300.0,
    },
    "send-daily-digest": {
        "task": "app.tasks.notification_tasks.send_daily_digest_task",
        "schedule": crontab(hour=DIGEST_SEND_HOUR, minute=DIGEST_SEND_MINUTE),
    },
}

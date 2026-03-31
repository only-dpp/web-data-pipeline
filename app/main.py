#env
import logging

import redis
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import get_redis_url, should_enable_docs, validate_runtime_config
from app.core.logging_config import setup_logging
from app.database import engine

load_dotenv()
setup_logging()

#api imports
from app.api.home import router as home_router
from app.api.source import router as source_router
from app.api.scraper import router as scraper_router
from app.api.run import router as run_router
from app.api.record import router as record_router
from app.api.digest import router as digest_router
from app.api.digest_send import router as digest_send_router
from app.api.article import router as article_router

logger = logging.getLogger(__name__)
docs_enabled = should_enable_docs()

app = FastAPI(
    title="Web Data Pipeline",
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)

app.include_router(home_router)
app.include_router(source_router)
app.include_router(scraper_router)
app.include_router(run_router)
app.include_router(record_router)
app.include_router(article_router)
app.include_router(digest_router)
app.include_router(digest_send_router)

@app.on_event("startup")
def on_startup() -> None:
    validate_runtime_config()
    logger.info("API startup completed docs_enabled=%s", docs_enabled)


@app.get("/health")
def healthcheck():
    checks = {
        "api": "ok",
        "database": "ok",
        "redis": "ok",
    }

    status_code = 200

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Database healthcheck failed")
        checks["database"] = "error"
        status_code = 503

    try:
        redis_client = redis.Redis.from_url(
            get_redis_url(),
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        redis_client.ping()
    except Exception:
        logger.exception("Redis healthcheck failed")
        checks["redis"] = "error"
        status_code = 503

    payload = {
        "status": "ok" if status_code == 200 else "degraded",
        "checks": checks,
    }
    return JSONResponse(status_code=status_code, content=payload)

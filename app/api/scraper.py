import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.url_security import URLSecurityError
from app.database import get_db
from app.dependencies.auth import require_internal_api_key
from app.services.scraper_service import run_source_scraper
from app.tasks.scraper_tasks import run_scraper_task

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scraper",
    tags=["scraper"],
    dependencies=[Depends(require_internal_api_key)],
)


@router.post("/run/{source_id}")
def run_scraper_route(source_id: int, db: Session = Depends(get_db)):
    try:
        return run_source_scraper(db, source_id)
    except URLSecurityError:
        raise HTTPException(status_code=400, detail="source URL blocked by security policy")
    except ValueError:
        raise HTTPException(status_code=404, detail="fonte não encontrada")
    except Exception:
        logger.exception("Unexpected error while running scraper for source_id=%s", source_id)
        raise HTTPException(status_code=500, detail="internal server error")
    
@router.post("/run_async/{source_id}")
def run_scraper_async(source_id: int):
    task = run_scraper_task.delay(source_id)

    return {
        "task_id": task.id,
        "status": "queued"
    }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.scraper_service import run_source_scraper
from app.tasks.scraper_tasks import run_scraper_task

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.post("/run/{source_id}")
def run_scraper_route(source_id: int, db: Session = Depends(get_db)):
    try:
        return run_source_scraper(db, source_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/run_async/{source_id}")
def run_scraper_async(source_id: int):
    task = run_scraper_task.delay(source_id)

    return {
        "task_id": task.id,
        "status": "queued"
    }
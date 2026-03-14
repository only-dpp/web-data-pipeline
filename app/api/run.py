from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.run_service import list_runs

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("")
def list_runs_route(db: Session = Depends(get_db)):
    return list_runs(db)
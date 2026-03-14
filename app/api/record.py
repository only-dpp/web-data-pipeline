from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.record_service import list_records

router = APIRouter(prefix="/records", tags=["records"])


@router.get("")
def list_records_route(
    source_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):
    return list_records(db, source_id=source_id)
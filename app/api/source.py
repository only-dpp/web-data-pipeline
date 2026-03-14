from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.source import SourceCreate, SourceResponse
from app.services.source_service import create_source

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("", response_model=SourceResponse)
def create_source_route(
    source_data: SourceCreate,
    db: Session = Depends(get_db)
):
    return create_source(db, source_data)
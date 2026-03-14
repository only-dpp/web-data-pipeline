from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.source import SourceCreate, SourceResponse
from app.services.source_service import create_source, list_sources

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("", response_model=SourceResponse)
def create_source_route(
    source_data: SourceCreate,
    db: Session = Depends(get_db)
):
    return create_source(db, source_data)


@router.get("", response_model=list[SourceResponse])
def list_sources_route(db: Session = Depends(get_db)):
    return list_sources(db)
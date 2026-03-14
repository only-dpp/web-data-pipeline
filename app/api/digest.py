from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.digest_service import get_digest_preview, get_digest_preview_html

router = APIRouter(prefix="/digest", tags=["digest"])


@router.get("/preview")
def digest_preview_route(
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return get_digest_preview(db, hours=hours, limit=limit)


@router.get("/preview/html", response_class=HTMLResponse)
def digest_preview_html_route(
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return get_digest_preview_html(db, hours=hours, limit=limit)
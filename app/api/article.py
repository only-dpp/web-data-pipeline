from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.article_service import list_articles

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
def list_articles_route(
    source_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):
    return list_articles(db, source_id=source_id)
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.digest import DigestSendRequest
from app.services.digest_service import get_digest_preview_html
from app.services.email_service import send_html_email

router = APIRouter(prefix="/digest", tags=["digest"])


@router.post("/send")
def send_digest_route(
    payload: DigestSendRequest,
    db: Session = Depends(get_db),
):
    html_content = get_digest_preview_html(
        db=db,
        hours=payload.hours,
        limit=payload.limit,
    )

    subject = f"Web Data Pipeline Digest - {datetime.now().strftime('%d/%m/%Y')}"

    send_html_email(
        to_email=payload.to_email,
        subject=subject,
        html_content=html_content,
    )

    return {
        "status": "sent",
        "to_email": payload.to_email,
        "subject": subject,
    }
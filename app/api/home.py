import logging
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.tasks.notification_tasks import send_welcome_email_task
from app.services.subscriber_service import get_landing_stats, subscribe_email


logger = logging.getLogger(__name__)
router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")
email_adapter = TypeAdapter(EmailStr)


@router.get("/", response_class=HTMLResponse)
def landing_page(
    request: Request,
    signup: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stats = get_landing_stats(db)
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={
            "request": request,
            "stats": stats,
            "signup": signup,
        },
    )


@router.post("/subscribe")
async def subscribe_route(
    request: Request,
    db: Session = Depends(get_db),
):
    raw_form = parse_qs((await request.body()).decode("utf-8"))
    email_value = raw_form.get("email", [""])[0].strip()

    try:
        validated_email = email_adapter.validate_python(email_value)
    except ValidationError:
        return RedirectResponse(url="/?signup=invalid#signup", status_code=303)

    try:
        subscriber, status = subscribe_email(db, str(validated_email))
        if status == "created":
            try:
                send_welcome_email_task.delay(subscriber.id)
            except Exception:
                logger.exception("Failed to enqueue welcome email for subscriber_id=%s", subscriber.id)
        logger.info("Subscriber form submitted status=%s", status)
        return RedirectResponse(url=f"/?signup={status}#signup", status_code=303)
    except Exception:
        logger.exception("Failed to persist subscriber signup")
        return RedirectResponse(url="/?signup=error#signup", status_code=303)

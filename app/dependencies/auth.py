import logging
import os
import secrets

from fastapi import Header, HTTPException, status


logger = logging.getLogger(__name__)


def require_internal_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    expected_api_key = os.getenv("INTERNAL_API_KEY")

    if not expected_api_key:
        logger.error("INTERNAL_API_KEY is not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, expected_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized",
        )

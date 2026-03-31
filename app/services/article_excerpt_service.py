import logging

import requests
from bs4 import BeautifulSoup

from app.core.http_client import DEFAULT_HEADERS, DEFAULT_TIMEOUT, get_http_session
from app.core.url_security import URLSecurityError, assert_safe_outbound_url


logger = logging.getLogger(__name__)
HEADERS = DEFAULT_HEADERS


def clean_text(text: str | None) -> str | None:
    if not text:
        return None

    cleaned = " ".join(text.split()).strip()

    if not cleaned:
        return None

    return cleaned


def truncate_text(text: str, max_length: int = 240) -> str:
    if len(text) <= max_length:
        return text

    return text[:max_length].rsplit(" ", 1)[0] + "..."


def extract_article_excerpt(url: str) -> str | None:
    session = get_http_session()

    try:
        safe_url = assert_safe_outbound_url(url)
        response = session.get(safe_url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except URLSecurityError:
        logger.warning("Blocked unsafe outbound article URL: %s", url)
        return None
    except requests.RequestException:
        logger.warning("Failed to fetch article excerpt from url=%s", url)
        return None

    try:
        soup = BeautifulSoup(response.text, "html.parser")

        meta_description = soup.find("meta", attrs={"name": "description"})
        if meta_description and meta_description.get("content"):
            text = clean_text(meta_description.get("content"))
            if text:
                return truncate_text(text)

        og_description = soup.find("meta", attrs={"property": "og:description"})
        if og_description and og_description.get("content"):
            text = clean_text(og_description.get("content"))
            if text:
                return truncate_text(text)

        paragraphs = soup.find_all("p")
        paragraph_texts = []

        for p in paragraphs:
            text = clean_text(p.get_text(" ", strip=True))
            if text and len(text) > 60:
                paragraph_texts.append(text)

            if len(paragraph_texts) >= 2:
                break

        if paragraph_texts:
            joined = " ".join(paragraph_texts)
            return truncate_text(joined)

        return None

    except Exception:
        logger.exception("Failed to parse article excerpt from url=%s", url)
        return None

import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.core.http_client import DEFAULT_TIMEOUT, get_http_session
from app.core.url_security import URLSecurityError, assert_safe_outbound_url, validate_source_url
from app.models.source import Source


logger = logging.getLogger(__name__)


def scrape_source(source: Source) -> list[dict]:
    safe_list_url = assert_safe_outbound_url(source.list_url)
    session = get_http_session()

    try:
        response = session.get(safe_list_url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to fetch source list for source_id=%s url=%s", source.id, safe_list_url)
        raise

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select(source.list_selector)
    logger.info("Fetched %s candidate items for source_id=%s", len(items), source.id)

    records = []

    for item in items:
        title_element = item.select_one(source.title_selector)
        link_element = item.select_one(source.link_selector)
        summary_element = None

        if source.summary_selector:
            summary_element = item.select_one(source.summary_selector)

        title = title_element.get_text(strip=True) if title_element else None
        link = link_element.get("href") if link_element else None
        summary = summary_element.get_text(strip=True) if summary_element else None

        if not title or not link:
            continue

        absolute_url = urljoin(source.base_url, link)

        try:
            validate_source_url(absolute_url)
        except URLSecurityError:
            logger.warning("Skipping blocked article URL for source_id=%s url=%s", source.id, absolute_url)
            continue

        records.append({
            "title": title,
            "url": absolute_url,
            "summary": summary,
        })

    logger.info("Prepared %s scrape records for source_id=%s", len(records), source.id)
    return records

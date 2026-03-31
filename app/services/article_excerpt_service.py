import logging
import re

import requests
from bs4 import BeautifulSoup

from app.core.http_client import DEFAULT_HEADERS, DEFAULT_TIMEOUT, get_http_session
from app.core.url_security import URLSecurityError, assert_safe_outbound_url


logger = logging.getLogger(__name__)
HEADERS = DEFAULT_HEADERS

BOILERPLATE_PATTERNS = (
    "subscribe",
    "sign up",
    "cookie",
    "all rights reserved",
    "newsletter",
    "advertisement",
    "advertising",
    "enable javascript",
)

SIGNAL_TERMS = (
    "release",
    "launched",
    "update",
    "security",
    "incident",
    "outage",
    "benchmark",
    "performance",
    "api",
    "database",
    "model",
    "ai",
    "llm",
    "open source",
    "tool",
    "framework",
    "cloud",
    "infrastructure",
)


def clean_text(text: str | None) -> str | None:
    if not text:
        return None

    cleaned = " ".join(text.split()).strip()
    if not cleaned:
        return None

    return cleaned


def truncate_text(text: str, max_length: int = 260) -> str:
    if len(text) <= max_length:
        return text

    return text[:max_length].rsplit(" ", 1)[0] + "..."


def looks_like_boilerplate(text: str) -> bool:
    lowered = text.lower()

    if len(text) < 70:
        return True

    return any(pattern in lowered for pattern in BOILERPLATE_PATTERNS)


def score_excerpt_candidate(text: str) -> int:
    lowered = text.lower()
    score = 0

    if 110 <= len(text) <= 360:
        score += 12
    elif len(text) > 360:
        score += 6

    for term in SIGNAL_TERMS:
        if term in lowered:
            score += 4

    if re.search(r"\b\d+(\.\d+)?%|\b\d+(ms|gb|tb|x)\b", lowered):
        score += 5

    if ":" in text:
        score += 2

    if text.count(".") >= 2:
        score += 2

    return score


def extract_meta_descriptions(soup: BeautifulSoup) -> list[str]:
    candidates = []
    meta_specs = [
        {"name": "description"},
        {"property": "og:description"},
        {"name": "twitter:description"},
    ]

    for attrs in meta_specs:
        element = soup.find("meta", attrs=attrs)
        if not element or not element.get("content"):
            continue

        text = clean_text(element.get("content"))
        if text:
            candidates.append(text)

    return candidates


def extract_paragraph_candidates(soup: BeautifulSoup) -> list[str]:
    candidates = []

    for paragraph in soup.find_all("p"):
        text = clean_text(paragraph.get_text(" ", strip=True))
        if not text or looks_like_boilerplate(text):
            continue

        candidates.append(text)

        if len(candidates) >= 12:
            break

    return candidates


def select_best_excerpt(candidates: list[str]) -> str | None:
    if not candidates:
        return None

    best = sorted(
        ((score_excerpt_candidate(text), text) for text in candidates),
        key=lambda item: (item[0], len(item[1])),
        reverse=True,
    )[0][1]

    return truncate_text(best)


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
        candidates = extract_meta_descriptions(soup)
        candidates.extend(extract_paragraph_candidates(soup))
        return select_best_excerpt(candidates)
    except Exception:
        logger.exception("Failed to parse article excerpt from url=%s", url)
        return None

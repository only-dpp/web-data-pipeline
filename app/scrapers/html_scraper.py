import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.models.source import Source


def scrape_source(source: Source) -> list[dict]:
    response = requests.get(source.list_url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select(source.list_selector)

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

        records.append({
            "title": title,
            "url": absolute_url,
            "summary": summary,
        })

    return records
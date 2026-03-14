import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}


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
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception:
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
        return None
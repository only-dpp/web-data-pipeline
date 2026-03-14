from collections import defaultdict
from urllib.parse import urlparse

from app.services.digest_ranking_service import DigestScore


CATEGORY_KEYWORDS = {
    "security": ["security", "secrets", "exposed", "keys", "vulnerability", "incident"],
    "ai": ["ai", "llm", "agent", "agents", "model", "inference", "context"],
    "backend": ["python", "fastapi", "backend", "api", "database", "postgres", "postgresql", "redis"],
    "infra_cloud": ["cloud", "docker", "kubernetes", "infra", "observability", "telemetry"],
    "open_source": ["open source", "github", "alternative"],
    "tooling": ["tool", "tooling", "debug", "benchmark", "automation", "monitoring"],
    "low_priority": ["show hn", "launch hn", "hiring", "job"],
}


def normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def classify_article(title: str, url: str) -> str:
    text = normalize_text(title)
    domain = get_domain(url)

    if domain == "github.com":
        return "open_source"

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category

    return "general_tech"


def build_digest_sections(
    ranked_articles: list[DigestScore],
    max_per_domain: int = 2,
    max_per_category: int = 3,
    total_limit: int = 10,
) -> dict:
    domain_counts = defaultdict(int)
    category_counts = defaultdict(int)

    selected = []

    for article in ranked_articles:
        domain = get_domain(article.url)
        category = classify_article(article.title, article.url)

        if domain_counts[domain] >= max_per_domain:
            continue

        if category_counts[category] >= max_per_category:
            continue

        selected.append({
            "article_id": article.article_id,
            "title": article.title,
            "url": article.url,
            "final_score": article.final_score,
            "category": category,
            "domain": domain,
            "reasons": article.reasons,
            "summary": getattr(article, "summary", None),
        })

        domain_counts[domain] += 1
        category_counts[category] += 1

        if len(selected) >= total_limit:
            break

    highlights = selected[:3]
    technical_radar = selected[3:7]
    quick_reads = selected[7:10]

    return {
        "highlights": highlights,
        "technical_radar": technical_radar,
        "quick_reads": quick_reads,
        "meta": {
            "selected_count": len(selected),
            "domain_distribution": {k: v for k, v in domain_counts.items() if v > 0},
            "category_distribution": {k: v for k, v in category_counts.items() if v > 0},
        }
    }
from collections import defaultdict

from app.services.digest_ranking_service import DigestScore


SECTION_LIMITS = {
    "highlights": 3,
    "technical_radar": 4,
    "quick_reads": 3,
}


def is_similar_story(current: DigestScore, selected: list[DigestScore]) -> bool:
    current_tokens = set(current.duplicate_key.split("|", 1)[-1].split())

    for item in selected:
        if current.url == item.url:
            return True

        if current.duplicate_key == item.duplicate_key:
            return True

        selected_tokens = set(item.duplicate_key.split("|", 1)[-1].split())
        if not current_tokens or not selected_tokens:
            continue

        intersection = len(current_tokens.intersection(selected_tokens))
        smallest_set = min(len(current_tokens), len(selected_tokens))

        if smallest_set and intersection / smallest_set >= 0.8:
            return True

    return False


def digest_summary_for_item(article: DigestScore) -> str | None:
    return article.why_it_matters or article.summary


def as_digest_item(article: DigestScore) -> dict:
    return {
        "article_id": article.article_id,
        "title": article.title,
        "url": article.url,
        "final_score": article.final_score,
        "category": article.category,
        "domain": article.domain,
        "urgency": article.urgency,
        "reasons": article.reasons,
        "summary": digest_summary_for_item(article),
    }


def fits_general_constraints(
    article: DigestScore,
    *,
    selected: list[DigestScore],
    domain_counts: defaultdict[str, int],
    category_counts: defaultdict[str, int],
    max_per_domain: int,
    max_per_category: int,
) -> bool:
    if domain_counts[article.domain] >= max_per_domain:
        return False

    if category_counts[article.category] >= max_per_category:
        return False

    if is_similar_story(article, selected):
        return False

    return True


def pick_section_items(
    ranked_articles: list[DigestScore],
    *,
    selected: list[DigestScore],
    domain_counts: defaultdict[str, int],
    category_counts: defaultdict[str, int],
    limit: int,
    predicate,
    max_per_domain: int,
    max_per_category: int,
) -> list[DigestScore]:
    items = []

    for article in ranked_articles:
        if article in selected:
            continue

        if not predicate(article):
            continue

        if not fits_general_constraints(
            article,
            selected=selected,
            domain_counts=domain_counts,
            category_counts=category_counts,
            max_per_domain=max_per_domain,
            max_per_category=max_per_category,
        ):
            continue

        selected.append(article)
        items.append(article)
        domain_counts[article.domain] += 1
        category_counts[article.category] += 1

        if len(items) >= limit:
            break

    return items


def fill_remaining_slots(
    ranked_articles: list[DigestScore],
    *,
    selected: list[DigestScore],
    domain_counts: defaultdict[str, int],
    category_counts: defaultdict[str, int],
    total_limit: int,
    max_per_domain: int,
    max_per_category: int,
) -> None:
    for article in ranked_articles:
        if len(selected) >= total_limit:
            break

        if article in selected:
            continue

        if not fits_general_constraints(
            article,
            selected=selected,
            domain_counts=domain_counts,
            category_counts=category_counts,
            max_per_domain=max_per_domain,
            max_per_category=max_per_category,
        ):
            continue

        selected.append(article)
        domain_counts[article.domain] += 1
        category_counts[article.category] += 1


def build_digest_sections(
    ranked_articles: list[DigestScore],
    max_per_domain: int = 2,
    max_per_category: int = 3,
    total_limit: int = 10,
) -> dict:
    domain_counts = defaultdict(int)
    category_counts = defaultdict(int)
    selected: list[DigestScore] = []

    highlights = pick_section_items(
        ranked_articles,
        selected=selected,
        domain_counts=domain_counts,
        category_counts=category_counts,
        limit=min(SECTION_LIMITS["highlights"], total_limit),
        predicate=lambda article: article.urgency in {"now", "watch"} or article.impact_score >= 70,
        max_per_domain=max_per_domain,
        max_per_category=max_per_category,
    )

    technical_radar = pick_section_items(
        ranked_articles,
        selected=selected,
        domain_counts=domain_counts,
        category_counts=category_counts,
        limit=min(SECTION_LIMITS["technical_radar"], max(total_limit - len(selected), 0)),
        predicate=lambda article: article.technical_depth_score >= 35 or article.utility_score >= 45,
        max_per_domain=max_per_domain,
        max_per_category=max_per_category,
    )

    fill_remaining_slots(
        ranked_articles,
        selected=selected,
        domain_counts=domain_counts,
        category_counts=category_counts,
        total_limit=total_limit,
        max_per_domain=max_per_domain,
        max_per_category=max_per_category,
    )

    if len(selected) > len(highlights) + len(technical_radar):
        quick_reads = selected[len(highlights) + len(technical_radar):total_limit]
    else:
        quick_reads = []

    return {
        "highlights": [as_digest_item(article) for article in highlights],
        "technical_radar": [as_digest_item(article) for article in technical_radar],
        "quick_reads": [as_digest_item(article) for article in quick_reads],
        "meta": {
            "selected_count": len(selected),
            "domain_distribution": {k: v for k, v in domain_counts.items() if v > 0},
            "category_distribution": {k: v for k, v in category_counts.items() if v > 0},
        },
    }

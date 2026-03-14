from dataclasses import dataclass
from datetime import datetime, UTC
from urllib.parse import urlparse
import re
from datetime import datetime, UTC

@dataclass
class DigestScore:
    article_id: int
    title: str
    url: str
    summary: str | None
    final_score: float
    relevance_score: float
    freshness_score: float
    credibility_score: float
    technical_depth_score: float
    utility_score: float
    novelty_score: float
    editorial_fit_score: float
    penalty_score: float
    reasons: list[str]


HIGH_PRIORITY_KEYWORDS = {
    "python": 14,
    "ai": 14,
    "llm": 14,
    "fastapi": 14,
    "redis": 12,
    "postgres": 12,
    "postgresql": 12,
    "docker": 12,
    "security": 14,
    "backend": 12,
    "database": 12,
    "open source": 12,
    "linux": 10,
    "webassembly": 12,
    "wasm": 12,
    "rust": 10,
    "devtools": 10,
    "observability": 12,
    "infra": 10,
    "kubernetes": 12,
    "cloud": 11,
    "telemetry": 10,
    "compiler": 10,
    "api": 8,
    "automation": 10,
    "optimization": 10,
    "engineering": 10,
    "secrets": 11,
    "documentation": 8,
    "exposed": 10,
    "local": 6,
    "types": 7,
    "management": 7,
}

MEDIUM_PRIORITY_KEYWORDS = {
    "framework": 6,
    "performance": 7,
    "browser": 5,
    "terminal": 5,
    "release": 7,
    "benchmark": 8,
    "tool": 6,
    "tooling": 6,
    "memory": 7,
    "kernel": 7,
    "inference": 7,
    "agent": 4,
    "agents": 4,
    "monitoring": 7,
    "scraping": 6,
    "queue": 6,
    "worker": 6,
    "cache": 6,
    "hardware": 4,
    "runtime": 6,
    "protocol": 6,
    "distributed": 7,
    "guide": 6,
    "tutorial": 7,
    "debug": 6,
    "migration": 6,
    "integration": 6,
}

LOW_SIGNAL_KEYWORDS = {
    "startup": 1,
    "essay": 1,
    "thoughts": 1,
    "story": 1,
}

NEGATIVE_KEYWORDS = {
    "show hn": 10,
    "launch hn": 12,
    "hiring": 16,
    "job": 12,
    "opinion": 8,
    "essay": 8,
    "rant": 10,
    "personal": 6,
    "gone again": 5,
}

SIDE_TOPIC_KEYWORDS = {
    "sega": 8,
    "mega drive": 8,
    "mouse": 4,
    "cable tv": 6,
    "cookie": 5,
    "philosoph": 8,
    "meteor crater": 6,
    "doctor who": 8,
}

HIGH_CREDIBILITY_DOMAINS = {
    "github.com": 78,
    "arstechnica.com": 92,
    "techcrunch.com": 88,
    "theverge.com": 84,
    "tomshardware.com": 82,
    "cloudflare.com": 94,
    "openai.com": 96,
    "python.org": 96,
    "postgresql.org": 96,
    "docker.com": 94,
    "microsoft.com": 90,
    "developer.mozilla.org": 94,
    "mozilla.org": 90,
    "news.ycombinator.com": 75,
    "claude.com": 90,
    "anthropic.com": 92,
    "ft.com": 85,
    "bbc.com": 80,
}

MEDIUM_CREDIBILITY_DOMAINS = {
    "substack.com": 60,
    "medium.com": 55,
    "wordpress.com": 50,
    "dev.to": 68,
    "macrumors.com": 60,
    "canirun.ai": 62,
}

TECHNICAL_TERMS = {
    "architecture": 8,
    "performance": 8,
    "database": 8,
    "compiler": 8,
    "memory": 8,
    "kernel": 8,
    "security": 8,
    "wasm": 8,
    "webassembly": 8,
    "inference": 7,
    "telemetry": 7,
    "protocol": 7,
    "runtime": 7,
    "engine": 6,
    "distributed": 7,
    "worker": 6,
    "queue": 6,
    "cache": 6,
    "optimization": 8,
    "types": 6,
    "management": 6,
    "engineering": 7,
    "documentation": 5,
    "hardware": 4,
    "local": 4,
    "secrets": 7,
    "cloud": 6,
    "api": 5,
    "benchmark": 7,
    "debug": 6,
}

UTILITY_TERMS = {
    "guide": 10,
    "tutorial": 10,
    "benchmark": 9,
    "release": 8,
    "incident": 8,
    "security": 10,
    "tool": 6,
    "open source": 8,
    "integration": 8,
    "api": 7,
    "migration": 8,
    "automation": 8,
    "debug": 8,
    "exposed": 9,
    "management": 7,
    "optimization": 8,
    "local": 6,
    "documentation": 7,
}

EDITORIAL_PRIORITY_TERMS = {
    "python": 14,
    "security": 14,
    "backend": 12,
    "database": 12,
    "postgres": 12,
    "postgresql": 12,
    "redis": 10,
    "docker": 10,
    "ai": 12,
    "llm": 12,
    "open source": 10,
    "cloud": 10,
    "observability": 10,
    "infra": 10,
    "fastapi": 12,
    "webassembly": 8,
    "wasm": 8,
    "automation": 10,
    "devtools": 8,
    "tooling": 8,
}

EDITORIAL_NEGATIVE_TERMS = {
    "hiring": 15,
    "job": 12,
    "show hn": 10,
    "launch hn": 10,
    "opinion": 7,
    "essay": 7,
    "personal": 5,
}

MUST_HAVE_TERMS = {
    "security": 10,
    "python": 9,
    "ai": 8,
    "llm": 8,
    "backend": 8,
    "database": 8,
    "postgres": 8,
    "postgresql": 8,
    "redis": 7,
    "fastapi": 8,
    "open source": 7,
    "cloud": 7,
    "observability": 7,
    "docker": 7,
    "automation": 7,
}


def normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def score_relevance(title: str) -> tuple[float, list[str]]:
    text = normalize_text(title)
    score = 0.0
    reasons = []

    for keyword, points in HIGH_PRIORITY_KEYWORDS.items():
        if keyword in text:
            score += points
            reasons.append(f"alta relevância: '{keyword}'")

    for keyword, points in MEDIUM_PRIORITY_KEYWORDS.items():
        if keyword in text:
            score += points
            reasons.append(f"relevância média: '{keyword}'")

    for keyword, points in LOW_SIGNAL_KEYWORDS.items():
        if keyword in text:
            score += points

    return clamp(score), reasons


def score_freshness(published_at, collected_at) -> tuple[float, list[str]]:
    now = datetime.now(UTC)
    reference_date = published_at or collected_at

    if reference_date is None:
        return 35.0, ["sem data confiável"]

    delta_hours = (now - reference_date).total_seconds() / 3600

    if delta_hours <= 6:
        return 100.0, ["muito recente"]
    if delta_hours <= 12:
        return 88.0, ["recente"]
    if delta_hours <= 24:
        return 72.0, ["publicado nas últimas 24h"]
    if delta_hours <= 48:
        return 45.0, ["artigo mais antigo"]
    return 15.0, ["artigo velho para digest diário"]


def score_credibility(url: str) -> tuple[float, list[str]]:
    domain = get_domain(url)

    if domain in HIGH_CREDIBILITY_DOMAINS:
        return float(HIGH_CREDIBILITY_DOMAINS[domain]), [f"domínio confiável: {domain}"]

    if domain in MEDIUM_CREDIBILITY_DOMAINS:
        return float(MEDIUM_CREDIBILITY_DOMAINS[domain]), [f"domínio médio: {domain}"]

    if domain.endswith(".gov") or domain.endswith(".edu"):
        return 82.0, [f"domínio institucional forte: {domain}"]

    if domain.endswith(".org"):
        return 72.0, [f"domínio institucional: {domain}"]

    if domain:
        return 55.0, [f"domínio desconhecido: {domain}"]

    return 20.0, ["url inválida ou sem domínio"]


def score_technical_depth(title: str) -> tuple[float, list[str]]:
    text = normalize_text(title)
    score = 0.0
    reasons = []

    for keyword, points in TECHNICAL_TERMS.items():
        if keyword in text:
            score += points
            reasons.append(f"densidade técnica: '{keyword}'")

    words = text.split()

    if len(words) >= 6:
        score += 10
        reasons.append("título mais descritivo")

    if ":" in text:
        score += 6
        reasons.append("estrutura de título técnico")

    if " for " in text or " in " in text or " with " in text:
        score += 4
        reasons.append("indício de contexto técnico")

    if len(words) <= 3:
        score -= 10
        reasons.append("título curto demais")

    return clamp(score), reasons


def score_utility(title: str) -> tuple[float, list[str]]:
    text = normalize_text(title)
    score = 18.0
    reasons = []

    for keyword, points in UTILITY_TERMS.items():
        if keyword in text:
            score += points
            reasons.append(f"utilidade prática: '{keyword}'")

    if "how to" in text or "guide" in text or "tutorial" in text:
        score += 10
        reasons.append("conteúdo acionável")

    if "alternative" in text:
        score += 6
        reasons.append("sugere solução prática")

    if "available" in text or "release" in text:
        score += 5
        reasons.append("indício de atualização relevante")

    return clamp(score), reasons


def score_novelty(title: str, all_titles: list[str]) -> tuple[float, list[str]]:
    text = normalize_text(title)
    reasons = []

    repeated_tokens = 0
    title_tokens = set(text.split())

    for other_title in all_titles:
        other = normalize_text(other_title)
        if other == text:
            continue

        overlap = len(title_tokens.intersection(set(other.split())))
        if overlap >= 4:
            repeated_tokens += 1

    if repeated_tokens == 0:
        return 90.0, ["tema pouco redundante"]

    if repeated_tokens == 1:
        return 65.0, ["tema parcialmente redundante"]

    return 35.0, ["tema muito repetido no lote"]


def score_editorial_fit(title: str) -> tuple[float, list[str]]:
    text = normalize_text(title)
    score = 45.0
    reasons = []

    for keyword, points in EDITORIAL_PRIORITY_TERMS.items():
        if keyword in text:
            score += points
            reasons.append(f"alinhamento editorial: '{keyword}'")

    for keyword, points in EDITORIAL_NEGATIVE_TERMS.items():
        if keyword in text:
            score -= points
            reasons.append(f"baixo alinhamento editorial: '{keyword}'")

    return clamp(score), reasons


def score_penalties(title: str, url: str) -> tuple[float, list[str]]:
    text = normalize_text(title)
    penalty = 0.0
    reasons = []

    for keyword, points in NEGATIVE_KEYWORDS.items():
        if keyword in text:
            penalty += points
            reasons.append(f"penalidade: '{keyword}'")

    for keyword, points in SIDE_TOPIC_KEYWORDS.items():
        if keyword in text:
            penalty += points
            reasons.append(f"tema lateral: '{keyword}'")

    if len(text) < 20:
        penalty += 8
        reasons.append("título muito curto")

    if get_domain(url) == "":
        penalty += 15
        reasons.append("url sem domínio válido")

    age_penalty, age_reasons = score_age_penalty(title)
    evergreen_penalty, evergreen_reasons = score_evergreen_penalty(title)

    penalty += age_penalty + evergreen_penalty
    reasons.extend(age_reasons)
    reasons.extend(evergreen_reasons)

    if "alternative" in text and any(keyword in text for keyword in SIDE_TOPIC_KEYWORDS):
        penalty += 4
        reasons.append("alternativa open source de tema lateral")

    return penalty, reasons


def score_must_have_boost(title: str) -> tuple[float, list[str]]:
    text = normalize_text(title)
    boost = 0.0
    reasons = []

    for keyword, points in MUST_HAVE_TERMS.items():
        if keyword in text:
            boost += points
            reasons.append(f"tema forte para destaque: '{keyword}'")

    return boost, reasons


def compute_final_score(article, all_titles: list[str]) -> DigestScore:
    relevance_score, relevance_reasons = score_relevance(article.title)
    freshness_score, freshness_reasons = score_freshness(article.published_at, article.collected_at)
    credibility_score, credibility_reasons = score_credibility(article.url)
    technical_depth_score, technical_reasons = score_technical_depth(article.title)
    utility_score, utility_reasons = score_utility(article.title)
    novelty_score, novelty_reasons = score_novelty(article.title, all_titles)
    editorial_fit_score, editorial_reasons = score_editorial_fit(article.title)
    penalty_score, penalty_reasons = score_penalties(article.title, article.url)
    must_have_boost, boost_reasons = score_must_have_boost(article.title)

    final_score = (
        relevance_score * 0.34
        + freshness_score * 0.08
        + credibility_score * 0.12
        + technical_depth_score * 0.18
        + utility_score * 0.14
        + novelty_score * 0.06
        + editorial_fit_score * 0.08
        + must_have_boost
        - penalty_score
    )

    final_score = round(clamp(final_score), 2)

    reasons = (
        relevance_reasons
        + freshness_reasons
        + credibility_reasons
        + technical_reasons
        + utility_reasons
        + novelty_reasons
        + editorial_reasons
        + boost_reasons
        + penalty_reasons
    )

    return DigestScore(
        article_id=article.id,
        title=article.title,
        url=article.url,
        summary=article.summary,
        final_score=final_score,
        relevance_score=round(relevance_score, 2),
        freshness_score=round(freshness_score, 2),
        credibility_score=round(credibility_score, 2),
        technical_depth_score=round(technical_depth_score, 2),
        utility_score=round(utility_score, 2),
        novelty_score=round(novelty_score, 2),
        editorial_fit_score=round(editorial_fit_score, 2),
        penalty_score=round(penalty_score, 2),
        reasons=reasons,
    )


def rank_articles(articles: list) -> list[DigestScore]:
    all_titles = [article.title for article in articles]

    ranked = [compute_final_score(article, all_titles) for article in articles]
    ranked.sort(key=lambda item: item.final_score, reverse=True)

    return ranked

def extract_year_from_title(title: str) -> int | None:
    match = re.search(r"\b(19\d{2}|20\d{2})\b", title)
    if not match:
        return None
    return int(match.group(1))


def score_age_penalty(title: str) -> tuple[float, list[str]]:
    current_year = datetime.now(UTC).year
    year = extract_year_from_title(title)

    if year is None:
        return 0.0, []

    if year <= current_year - 2:
        return 18.0, [f"conteúdo antigo detectado no título: {year}"]

    if year == current_year - 1:
        return 6.0, [f"conteúdo possivelmente antigo: {year}"]

    return 0.0, []


def score_evergreen_penalty(title: str) -> tuple[float, list[str]]:
    text = normalize_text(title)
    penalty = 0.0
    reasons = []

    evergreen_terms = ["guide", "tutorial", "how to", "survival guide"]
    news_terms = ["release", "available", "launched", "incident", "update", "security", "exposed"]

    has_evergreen = any(term in text for term in evergreen_terms)
    has_news_signal = any(term in text for term in news_terms)

    if has_evergreen and not has_news_signal:
        penalty += 8.0
        reasons.append("conteúdo evergreen com baixo sinal de notícia")

    return penalty, reasons
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
import re
from urllib.parse import urlparse


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
    category: str
    domain: str
    urgency: str
    impact_score: float
    why_it_matters: str | None
    duplicate_key: str
    reasons: list[str]


STOPWORDS = {
    "a", "an", "and", "as", "at", "be", "by", "for", "from", "how", "in", "into",
    "is", "it", "of", "on", "or", "that", "the", "this", "to", "up", "with",
    "um", "uma", "de", "do", "da", "dos", "das", "para", "com", "sem", "por",
    "em", "na", "no", "os", "as", "o", "e", "ou",
}

CATEGORY_SIGNALS = {
    "security": {
        "security", "vulnerability", "incident", "breach", "secrets", "exposed",
        "cve", "ransomware", "malware", "patch", "zero-day",
    },
    "ai": {
        "ai", "llm", "model", "models", "agent", "agents", "inference", "embedding",
        "prompt", "token", "multimodal", "fine-tuning",
    },
    "backend_data": {
        "backend", "api", "database", "postgres", "postgresql", "redis", "queue",
        "worker", "cache", "fastapi", "python", "sql", "orm",
    },
    "infra_cloud": {
        "docker", "kubernetes", "cloud", "infra", "infrastructure", "runtime",
        "observability", "telemetry", "deployment", "cluster", "container",
    },
    "developer_tools": {
        "tool", "tooling", "debug", "benchmark", "automation", "cli", "editor",
        "sdk", "testing", "devtools", "monitoring", "copilot",
    },
    "open_source": {
        "open source", "github", "repository", "repo", "oss", "self-hosted",
        "alternative",
    },
}

HIGH_SIGNAL_TERMS = {
    "security": 18,
    "incident": 16,
    "breach": 16,
    "vulnerability": 16,
    "patch": 12,
    "release": 12,
    "launch": 10,
    "available": 8,
    "benchmark": 11,
    "performance": 10,
    "api": 8,
    "postgres": 12,
    "postgresql": 12,
    "redis": 10,
    "python": 12,
    "fastapi": 12,
    "docker": 11,
    "kubernetes": 11,
    "cloud": 10,
    "open source": 10,
    "ai": 12,
    "llm": 12,
    "model": 8,
    "agent": 8,
    "agents": 8,
    "observability": 10,
    "automation": 9,
    "tooling": 8,
}

ACTIONABLE_TERMS = {
    "how to", "guide", "tutorial", "migration", "benchmark", "incident", "patch",
    "release", "available", "breaking", "deprecate", "deprecation", "upgrade",
    "fix", "fixed", "security", "api", "integration",
}

IMPACT_TERMS = {
    "launch", "launched", "release", "released", "ga", "general availability",
    "outage", "incident", "security", "breach", "pricing", "breaking", "deprecated",
    "acquisition", "funding", "partnership", "benchmark", "support", "shutdown",
}

LOW_SIGNAL_TERMS = {
    "show hn": 14,
    "launch hn": 14,
    "hiring": 18,
    "job": 15,
    "opinion": 10,
    "essay": 10,
    "personal": 8,
    "story": 6,
    "podcast": 6,
}

EVERGREEN_TERMS = {"guide", "tutorial", "how to", "tips", "best practices"}
NEWSY_TERMS = {"release", "incident", "security", "update", "launch", "available", "patch", "outage"}

HIGH_CREDIBILITY_DOMAINS = {
    "github.com": 84,
    "python.org": 96,
    "postgresql.org": 96,
    "docker.com": 94,
    "kubernetes.io": 95,
    "cloudflare.com": 94,
    "openai.com": 96,
    "anthropic.com": 94,
    "developer.mozilla.org": 94,
    "mozilla.org": 90,
    "microsoft.com": 90,
    "aws.amazon.com": 92,
    "cloud.google.com": 92,
    "arstechnica.com": 88,
    "theverge.com": 80,
    "techcrunch.com": 78,
}

MEDIUM_CREDIBILITY_DOMAINS = {
    "dev.to": 68,
    "medium.com": 58,
    "substack.com": 58,
    "news.ycombinator.com": 70,
}


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def build_article_text(title: str | None, summary: str | None) -> str:
    return normalize_text(" ".join(part for part in [title, summary] if part))


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9][a-z0-9\-\+\.#]{1,}", text.lower()) if token not in STOPWORDS]


def classify_article(title: str, summary: str | None, url: str) -> str:
    domain = get_domain(url)
    text = build_article_text(title, summary)

    if domain == "github.com":
        return "open_source"

    category_scores = {}
    for category, keywords in CATEGORY_SIGNALS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score:
            category_scores[category] = score

    if not category_scores:
        return "general_tech"

    return max(category_scores.items(), key=lambda item: item[1])[0]


def infer_urgency(text: str) -> str:
    urgent_terms = ("incident", "breach", "security", "outage", "breaking", "deprecated", "deprecation")
    watch_terms = ("release", "launched", "available", "pricing", "benchmark", "support")

    if any(term in text for term in urgent_terms):
        return "now"

    if any(term in text for term in watch_terms):
        return "watch"

    return "follow"


def build_duplicate_key(title: str, url: str) -> str:
    domain = get_domain(url)
    tokens = [token for token in tokenize(normalize_text(title)) if len(token) > 2]
    core_tokens = sorted(tokens[:8])
    return f"{domain}|{' '.join(core_tokens[:5])}"


def first_meaningful_sentence(summary: str | None) -> str | None:
    text = (summary or "").strip()
    if not text:
        return None

    sentences = re.split(r"(?<=[.!?])\s+", text)
    for sentence in sentences:
        cleaned = sentence.strip()
        if len(cleaned) >= 40:
            return cleaned

    return text


def build_reader_summary(title: str, summary: str | None, category: str, urgency: str) -> str | None:
    base = first_meaningful_sentence(summary)
    if base:
        return truncate(base, 220)

    category_phrases = {
        "security": "Vale atenção porque mexe com segurança, exposição de risco ou resposta operacional.",
        "ai": "Importa para quem acompanha produtos, modelos e mudanças práticas no ecossistema de IA.",
        "backend_data": "É relevante para backend, dados, APIs e a forma como sistemas são operados no dia a dia.",
        "infra_cloud": "Traz sinal importante para infraestrutura, cloud, deploy e operação de plataformas.",
        "developer_tools": "Tem utilidade prática para fluxo de trabalho, produtividade e ferramentas de desenvolvimento.",
        "open_source": "Merece radar porque pode virar alternativa real ou referência útil para times técnicos.",
        "general_tech": "Entra no digest porque ajuda a manter contexto sobre movimentos importantes do mercado tech.",
    }
    urgency_prefix = {
        "now": "Atenção agora: ",
        "watch": "Fique de olho: ",
        "follow": "",
    }
    return urgency_prefix[urgency] + category_phrases[category]


def truncate(text: str, max_length: int = 220) -> str:
    if len(text) <= max_length:
        return text

    return text[:max_length].rsplit(" ", 1)[0] + "..."


def score_relevance(text: str, category: str) -> tuple[float, list[str]]:
    score = 8.0
    reasons = []

    for keyword, points in HIGH_SIGNAL_TERMS.items():
        if keyword in text:
            score += points
            reasons.append(f"sinal forte: '{keyword}'")

    category_hits = sum(1 for keyword in CATEGORY_SIGNALS.get(category, set()) if keyword in text)
    if category_hits:
        score += category_hits * 5
        reasons.append(f"tema consistente em {category}")

    return clamp(score), reasons


def score_freshness(published_at, collected_at) -> tuple[float, list[str]]:
    reference_date = published_at or collected_at
    if reference_date is None:
        return 35.0, ["sem data confiável"]

    now = datetime.now(UTC)
    delta_hours = (now - reference_date).total_seconds() / 3600

    if delta_hours <= 6:
        return 100.0, ["muito recente"]
    if delta_hours <= 12:
        return 90.0, ["recente"]
    if delta_hours <= 24:
        return 78.0, ["ainda dentro da janela do dia"]
    if delta_hours <= 36:
        return 58.0, ["já começa a esfriar"]
    if delta_hours <= 48:
        return 40.0, ["mais antigo para digest diário"]

    return 18.0, ["velho para um digest diário"]


def score_credibility(url: str) -> tuple[float, list[str]]:
    domain = get_domain(url)

    if domain in HIGH_CREDIBILITY_DOMAINS:
        return float(HIGH_CREDIBILITY_DOMAINS[domain]), [f"fonte forte: {domain}"]

    if domain in MEDIUM_CREDIBILITY_DOMAINS:
        return float(MEDIUM_CREDIBILITY_DOMAINS[domain]), [f"fonte média: {domain}"]

    if domain.endswith(".gov") or domain.endswith(".edu"):
        return 86.0, [f"domínio institucional: {domain}"]

    if domain.endswith(".org"):
        return 74.0, [f"domínio organizacional: {domain}"]

    if domain:
        return 56.0, [f"fonte ainda não priorizada: {domain}"]

    return 20.0, ["url inválida ou sem domínio"]


def score_technical_depth(title: str, summary: str | None) -> tuple[float, list[str]]:
    text = build_article_text(title, summary)
    score = 10.0
    reasons = []

    technical_terms = {
        "api", "database", "postgres", "redis", "queue", "worker", "cache", "model",
        "runtime", "compiler", "benchmark", "latency", "throughput", "security",
        "incident", "migration", "docker", "kubernetes", "cloud", "telemetry",
    }

    hits = [term for term in technical_terms if term in text]
    if hits:
        score += min(40, len(hits) * 5)
        reasons.append(f"densidade técnica por {len(hits)} sinais")

    if len(tokenize(normalize_text(title))) >= 6:
        score += 10
        reasons.append("título mais descritivo")

    if summary and len(summary.split()) >= 18:
        score += 12
        reasons.append("resumo com contexto útil")

    if re.search(r"\b(v?\d+(\.\d+)+|cve-\d{4}-\d+)\b", text):
        score += 8
        reasons.append("versão ou identificador técnico detectado")

    return clamp(score), reasons


def score_utility(title: str, summary: str | None, urgency: str) -> tuple[float, list[str]]:
    text = build_article_text(title, summary)
    score = 16.0
    reasons = []

    for term in ACTIONABLE_TERMS:
        if term in text:
            score += 8
            reasons.append(f"utilidade prática: '{term}'")

    if urgency == "now":
        score += 12
        reasons.append("exige atenção mais imediata")
    elif urgency == "watch":
        score += 6
        reasons.append("vale acompanhar de perto")

    if summary and len(summary.split()) >= 14:
        score += 6
        reasons.append("resumo suficiente para decisão")

    return clamp(score), reasons


def score_novelty(text: str, token_frequency: Counter[str]) -> tuple[float, list[str]]:
    tokens = set(tokenize(text))
    if not tokens:
        return 30.0, ["texto com pouco sinal"]

    overlap_pressure = sum(max(token_frequency[token] - 1, 0) for token in tokens if len(token) > 3)
    if overlap_pressure <= 2:
        return 88.0, ["tema pouco redundante no lote"]
    if overlap_pressure <= 5:
        return 64.0, ["tema recorrente, mas ainda útil"]
    return 38.0, ["tema já apareceu bastante no lote"]


def score_editorial_fit(category: str, urgency: str, summary: str | None) -> tuple[float, list[str]]:
    base_scores = {
        "security": 88.0,
        "backend_data": 82.0,
        "infra_cloud": 80.0,
        "ai": 80.0,
        "developer_tools": 78.0,
        "open_source": 76.0,
        "general_tech": 64.0,
    }
    score = base_scores.get(category, 60.0)
    reasons = [f"alinhamento editorial com {category}"]

    if urgency == "now":
        score += 8
        reasons.append("sinal mais urgente")

    if not summary:
        score -= 8
        reasons.append("baixo contexto disponível")

    return clamp(score), reasons


def score_impact(text: str, category: str, domain: str) -> tuple[float, list[str]]:
    score = 20.0
    reasons = []

    for term in IMPACT_TERMS:
        if term in text:
            score += 8
            reasons.append(f"impacto potencial: '{term}'")

    if category in {"security", "backend_data", "infra_cloud", "ai"}:
        score += 10
        reasons.append("tema com impacto alto para times técnicos")

    if domain == "github.com":
        score += 6
        reasons.append("potencial de adoção ou referência prática")

    return clamp(score), reasons


def score_penalties(title: str, summary: str | None, url: str) -> tuple[float, list[str]]:
    text = build_article_text(title, summary)
    penalty = 0.0
    reasons = []

    for keyword, points in LOW_SIGNAL_TERMS.items():
        if keyword in text:
            penalty += points
            reasons.append(f"baixo sinal: '{keyword}'")

    if len(normalize_text(title)) < 18:
        penalty += 8
        reasons.append("título muito curto")

    if not summary:
        penalty += 10
        reasons.append("sem resumo extraído")

    if any(term in text for term in EVERGREEN_TERMS) and not any(term in text for term in NEWSY_TERMS):
        penalty += 10
        reasons.append("conteúdo evergreen com pouco sinal de novidade")

    year_penalty, year_reasons = score_age_penalty(text)
    penalty += year_penalty
    reasons.extend(year_reasons)

    if not get_domain(url):
        penalty += 15
        reasons.append("url sem domínio válido")

    return penalty, reasons


def score_age_penalty(text: str) -> tuple[float, list[str]]:
    current_year = datetime.now(UTC).year
    match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
    if not match:
        return 0.0, []

    year = int(match.group(1))
    if year <= current_year - 2:
        return 18.0, [f"conteúdo antigo detectado: {year}"]
    if year == current_year - 1:
        return 6.0, [f"conteúdo possivelmente antigo: {year}"]

    return 0.0, []


def compute_final_score(article, token_frequency: Counter[str]) -> DigestScore:
    text = build_article_text(article.title, article.summary)
    domain = get_domain(article.url)
    category = classify_article(article.title, article.summary, article.url)
    urgency = infer_urgency(text)

    relevance_score, relevance_reasons = score_relevance(text, category)
    freshness_score, freshness_reasons = score_freshness(article.published_at, article.collected_at)
    credibility_score, credibility_reasons = score_credibility(article.url)
    technical_depth_score, technical_reasons = score_technical_depth(article.title, article.summary)
    utility_score, utility_reasons = score_utility(article.title, article.summary, urgency)
    novelty_score, novelty_reasons = score_novelty(text, token_frequency)
    editorial_fit_score, editorial_reasons = score_editorial_fit(category, urgency, article.summary)
    impact_score, impact_reasons = score_impact(text, category, domain)
    penalty_score, penalty_reasons = score_penalties(article.title, article.summary, article.url)

    final_score = (
        relevance_score * 0.24
        + freshness_score * 0.10
        + credibility_score * 0.12
        + technical_depth_score * 0.14
        + utility_score * 0.14
        + novelty_score * 0.08
        + editorial_fit_score * 0.08
        + impact_score * 0.10
        - penalty_score
    )
    final_score = round(clamp(final_score), 2)

    why_it_matters = build_reader_summary(article.title, article.summary, category, urgency)

    reasons = (
        relevance_reasons
        + freshness_reasons
        + credibility_reasons
        + technical_reasons
        + utility_reasons
        + novelty_reasons
        + editorial_reasons
        + impact_reasons
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
        category=category,
        domain=domain,
        urgency=urgency,
        impact_score=round(impact_score, 2),
        why_it_matters=why_it_matters,
        duplicate_key=build_duplicate_key(article.title, article.url),
        reasons=reasons,
    )


def rank_articles(articles: list) -> list[DigestScore]:
    token_frequency: Counter[str] = Counter()
    for article in articles:
        text = build_article_text(article.title, article.summary)
        token_frequency.update(set(tokenize(text)))

    ranked = [compute_final_score(article, token_frequency) for article in articles]
    ranked.sort(
        key=lambda item: (
            item.final_score,
            item.impact_score,
            item.utility_score,
            item.freshness_score,
        ),
        reverse=True,
    )
    return ranked

# Web Data Pipeline

Pipeline automatizado para coleta, processamento, ranking e distribuição de notícias de tecnologia via digest por e-mail.

O projeto coleta artigos de múltiplas fontes, salva os dados em banco, aplica um sistema de ranking editorial, organiza os melhores conteúdos em seções e gera um digest em HTML pronto para envio por e-mail.

## Preview

### Digest HTML
![Digest Preview](docs/digest-preview.png)

### Swagger / API
![Swagger Preview](docs/swagger-preview.png)

---

## Features

- Coleta de notícias de múltiplas fontes
- Scrapers configuráveis por seletores CSS
- Persistência em PostgreSQL
- Fila assíncrona com Celery + Redis
- Deduplicação por hash
- Extração automática de resumo do artigo
- Ranking editorial com múltiplos critérios
- Seleção editorial por seções
- Geração de digest em HTML
- Envio de digest por e-mail via SMTP
- Agendamento automático com Celery Beat

---

## Fontes testadas

Atualmente o projeto foi testado com fontes como:

- Hacker News
- DEV Community
- Ars Technica
- TechCrunch

> Como cada fonte é configurável por seletores CSS, novas fontes podem ser adicionadas sem alterar a arquitetura principal do sistema.

---

## Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL

### Processamento assíncrono
- Celery
- Redis

### Scraping e parsing
- Requests
- BeautifulSoup

### Renderização
- Jinja2

### Infra local
- Docker

---

## Como funciona

O fluxo do pipeline é:

```text
Sources
   ↓
HTML Scraper
   ↓
Article Extraction
   ↓
PostgreSQL
   ↓
Ranking Engine
   ↓
Editorial Selection
   ↓
Digest HTML Renderer
   ↓
Email Delivery

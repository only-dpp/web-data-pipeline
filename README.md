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
```

## Etapas principais
1. Uma fonte é cadastrada com seus seletores CSS
2. O scraper coleta os itens da página
3. Os artigos são normalizados e deduplicados
4. O sistema tenta enriquecer cada item com resumo real da página
5. Os artigos são ranqueados por relevância
6. O digest organiza os conteúdos em seçôes editoriais
7. O HTML é gerado
8. O digest pode ser enviado por e-mail

## Estrutura do projeto

```bash
app/
├── api/
│   ├── digest.py
│   ├── digest_send.py
│   ├── scraper.py
│   └── sources.py
├── models/
│   ├── article.py
│   ├── run.py
│   └── source.py
├── schemas/
│   └── digest.py
├── services/
│   ├── article_excerpt_service.py
│   ├── digest_ranking_service.py
│   ├── digest_render_service.py
│   ├── digest_selection_service.py
│   ├── digest_service.py
│   ├── email_service.py
│   ├── hash_service.py
│   └── scraper_service.py
├── tasks/
│   ├── scheduler_tasks.py
│   └── scraper_tasks.py
├── templates/
│   └── digest_email.html
├── celery_app.py
├── database.py
└── main.py
```

## Ranking editorial 

O projeto não apenas coleta links.
Ele aplica um sistema de ranking para priorizar os artigos mais relevantes no digest

O score considera fatores como:
   relevância do tema
   recência
   credibilidade da fonte
   profundidade técnica
   utilidade prática
   novidade no lote
   alinhamento editorial
   penalidades para conteúdos lateral ou redundantes

Depois do ranking, uma segunda camada faz a seleção editorial, dividindo os conteúdos em:
   Destaques
   Radar técnico 
   leitura rápida

## Requisitos
   Python 3.11+
   Docker
   PostgrSQL
   Redis

## Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/SEU-USUARIO/web-data-pipeline.git
cd web-data-pipeline
```
### 2. Crie e ative um ambiente virtual

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
### 4. Configure as variáveis de ambiente 
Crie um arquivo `.env`  baseado no `.env.example`

Exemplo:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/web_pipeline
REDIS_URL=redis://localhost:6379/0

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
EMAIL_FROM=your_email@gmail.com
```

## Subindo os serviços locais

### PostgreSQL
```bash
docker run --name web-data-pg -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=web_pipeline -p 5432:5432 -d postgres:16
```
### Redis
```bash
docker run --name web-data-redis -p 6379:6379 -d redis:7
```

## Rodando a aplicação

### API
```bash
python -m uvicorn app.main:app --reload
```
### Worker do scraper
```bash
python -m celery -A app.celery_app worker --loglevel=info -Q scrapers -P solo
```
### Worker do scheduler
```bash
python -m celery -A app.celery_app worker --loglevel=info -Q scheduler -P solo
```
### Celery beat
```bash
python -m celery -A app.celery_app beat --loglevel=info
```

## Documentação da API

Com a aplicação rodando, acesse:
```bash
http://127.0.0.1:8000/docs
```

## Fluxo basico básico de uso

### 1. Cadastrar uma fonte
Exemplo de payload:
```bash
{
  "name": "Hacker News",
  "base_url": "https://news.ycombinator.com",
  "list_url": "https://news.ycombinator.com",
  "list_selector": ".athing",
  "title_selector": ".titleline a",
  "link_selector": ".titleline a",
  "summary_selector": null,
  "schedule_minutes": 30
}
```
### 2. Rodar o scraper manualmente:
```bash
POST /scraper/run/{source_id}
```
ou
```bash
POST /scraper/run_async/{source_id}
```

### 3. Visualizar os artigos coletados
```bash
Get /articles
```

### 4. Gerar preview do digest
**JSON**
```bash
GET /digest/preview
```
**HTML**
```bash
GET /digest/preview/html
```

### 5. Enviar digest por e-mail
```bash
POST /digest/send
```
payload:
```bash
{
  "to_email": "seuemail@exemplo.com",
  "hours": 24,
  "limit": 10
}
```

## Exemplo de seçôes do digest
O digest final organiza os artigos assim:
   **Destaques**
   Os conteúdos mais fortes do lote
   **Radar Técnico**
   Artigos relevantes com foco mais técnico
   **Leitura Rápida**
   Itens úteis que ainda merecem menção


## Limitações atuais
   Algumas fontes exigem ajuste fino de seletores CSS
   Sites com HTML muito dinâmico podem exigir manutenção mais frequente
   A deduplicação atual é baseada em hash de título + URL, não em similaridade semântica
   O ranking editorial é heurístico e pode ser calibrado com novas regras ao longo do tempo


## Motivação do projeto
Este projeto foi criado para praticar e consolidar conceitos de:
   scraping configurável
   filas assíncronas
   deduplicação de dados
   processamento editorial
   geração de conteúdo em HTML
   integração com e-mail
   organização de backend em serviços e tarefas

**Desenvolvido por:**
Dopplin

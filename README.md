# Web Data Pipeline

O **Web Data Pipeline** é um sistema de ingestão e processamento de dados que coleta noticias de tecnologia a partir de páginas HTML, processa essas informaçôes e armazena os dados de forma estruturada

O objetivo do projeto é estudar e implementar conceitos de **data ingestion**, **processamento assíncrono**, **scraping configurável**, e **papelines de dados**, utilizando Python e ferramentas comuns em arquiteturas backend modernas.

---

## Funcionalidades

- Cadastro de fontes de notícias
- Coleta automática de páginas HTML
- Scraping configurável via seletores CSS
- Processamento e normalização de dados
- Deduplicação de registros
- Históricos de execuções de pipeline
- Dashboard web para visualização dos dados
- Envio de digest por email com notícias coletadas

---

## Arquitetura

O sistema segue uma arquitetura baseada em **pipeline de insgestão de dados**
```bash
Sources
|
Scheduler
|
Workers
|
Processing
|
Database
|
API/Dashboard
```

## Fluxo de funcionamento:

1. Fontes de dados são cadastradas no sistema
2. O scheduler agenda execuções de pipeline
3. Workers realizam o scraping das páginas
4. Os dados coletados passam por processamento
5. Registros normalizados são armazenados no banco
6. Os dados podem ser visualizados via API ou dashboard
7. O sisterma pode gerar digest periódico por email

---

## Tecnologias utilizadas

- **Python**
- **FastAPI** - API  e backend do sistema
- **Celery** - processamento assíncrono
- **Redis** - broker de mensagens
- **PostgreSQL** - banco de dados
- **Jinja2** - renderização do dashboard
- **HTMX** - interatividade no frontend
- **Docker** - containerização do ambiente

---

## Estrutura do projeto

´´´bash
app/
  api/ # rotas da API
  models/ # modelos do banco de dados
  scrapers/ # lógica de scraping
  services/ # regras de negócio e processamento
  workers/ # tarefas assíncronas
  templates? # template HTML
´´´

---

## Objetivo do projeto

Este projeto foi criado como forma de estudar e praticar:

- pipelines de ingestão de dados
- scraping configurável
- processamento assícrono com Celery
- arquitetura de workers
- organização de sistemas backend em Python

---

## Status do projeto

Em andamento...

## Licença

Este projeto está sob a licença MIT





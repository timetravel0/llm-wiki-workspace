# llm-wiki-workspace Integration Plan

> Stato: aggiornato al modello HTTP locale.
> Il precedente piano file-based e il vecchio scaffold canonico sono storici.
> L'integrazione operativa corrente passa da `simple_rag` come orchestratore e
> da `wiki_service/service_api.py` come API interna localhost per storage
> Markdown.

## Sommario

`llm-wiki-workspace` partecipa alla piattaforma integrata come servizio interno
per documentazione, processi e knowledge base Markdown.

Il ruolo operativo corrente e' intenzionalmente limitato:

- conservare documenti Markdown e metadati;
- esporre CRUD locale via FastAPI;
- richiedere bearer token interno;
- validare path, estensioni e dimensione file;
- mantenere audit locale delle scritture;
- lasciare orchestrazione, retrieval, indexing e write policy a `simple_rag`.

`simple_rag` resta l'entry point pubblico e orchestra:

- ingest wiki via `POST /api/v1/ingest/wiki`;
- sync filesystem wiki via `POST /api/v1/ingest/wiki/sync`;
- query integrate via `POST /api/v1/query` con `mode: "integrated"` o
  `POST /api/v1/query/integrated`;
- write confermate verso wiki via `POST /api/v1/write/wiki`;
- export di query page e source notes.

## Architettura Corrente

```text
User / client
    |
    | HTTP, x-api-key
    v
simple_rag
127.0.0.1:8000
    |
    | HTTP, Authorization: Bearer INTERNAL_API_TOKEN
    v
llm-wiki-workspace Wiki Service
127.0.0.1:8200
    |
    v
local Markdown storage + index.json + audit.jsonl
```

Il servizio Wiki non parla direttamente con Qdrant e non genera risposte. Dopo
ogni create/update rilevante, `simple_rag` recupera il contenuto dal servizio,
esegue chunking/embedding e aggiorna la collection `documentation`.

## Componenti Implementati

### Wiki Service

File:

- `wiki_service/service_api.py`
- `.env.example`
- `requirements.txt`
- `.gitignore`

Endpoint:

- `GET /api/v1/health`
- `POST /api/v1/documents`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{doc_id}/content`
- `GET /api/v1/documents/{doc_id}/raw`
- `PUT /api/v1/documents/{doc_id}`
- `DELETE /api/v1/documents/{doc_id}`
- `GET /api/v1/sections`

Storage predefinito:

```text
docs/
  index.json
  audit.jsonl
  _store/<doc_id>/
    content.md
    meta.json
```

### Contratto Di Sicurezza

- bind su `127.0.0.1`;
- host locale richiesto;
- `Authorization: Bearer $INTERNAL_API_TOKEN` obbligatorio tranne health;
- Swagger UI, ReDoc e OpenAPI disabilitati;
- nessun secret hardcoded;
- path traversal bloccato;
- estensioni ammesse: `.md`, `.txt`;
- limite dimensione file configurabile con `WIKI_MAX_FILE_SIZE_BYTES`.

### Integrazione SimpleRAG

Lato `simple_rag`, la logica correlata alla wiki vive principalmente in:

- `rag_app/api/integrated_routes.py`
- `rag_app/services/internal_content.py`
- `rag_app/services/internal_indexing.py`
- `rag_app/services/integrated_query.py`
- `rag_app/services/wiki_loader.py`
- `rag_app/services/wiki_sync.py`
- `rag_app/services/wiki_export.py`
- `rag_app/services/write_agent.py`

## Flussi Operativi

### Ingest Wiki Via API

```text
POST simple_rag /api/v1/ingest/wiki
  -> validate payload
  -> POST Wiki Service /api/v1/documents
  -> GET Wiki Service /api/v1/documents/{doc_id}/content
  -> index into Qdrant collection documentation
```

### Sync Wiki Da File System

```text
POST simple_rag /api/v1/ingest/wiki/sync
  -> load Markdown pages from llm-wiki-workspace
  -> parse frontmatter
  -> index only pages with rag_index: true
  -> maintain incremental sync state
```

Questo flusso serve per indicizzare pagine Markdown gia' presenti nel workspace,
senza passare dal Wiki Service.

### Query Integrata

```text
POST simple_rag /api/v1/query mode="integrated"
  -> QueryRouterAgent selects codebase, documentation, or both
  -> retrieve from selected collections
  -> apply wiki metadata filters when present
  -> fuse results
  -> generate answer
  -> persist interaction history
```

Filtri wiki supportati nel testo query:

- `wiki:<slug>`
- `page_type:<type>`
- `rag_scope:<global|wiki-local|private>`
- `status:<active|stale|draft|archived>`

### Scrittura Wiki Confermata

```text
POST simple_rag /api/v1/write/wiki
  -> require confirmed: true
  -> PUT Wiki Service /api/v1/documents/{doc_id}
  -> GET updated content
  -> re-index into documentation
  -> audit write
```

### Export Query Page E Source Notes

```text
POST simple_rag /api/v1/write/wiki/query-page
POST simple_rag /api/v1/write/wiki/source-notes
  -> require confirmed: true
  -> read persisted interaction
  -> generate Markdown document(s)
  -> create documents through Wiki Service
  -> index generated pages
```

## Frontmatter RAG

Le pagine wiki indicizzabili dovrebbero usare un frontmatter coerente:

```yaml
---
title: "Page title"
type: concept
tags: ["example"]
related: []
status: active
confidence: medium
rag_index: true
rag_scope: wiki-local
last_reviewed: "2026-04-30"
created: "2026-04-30"
source: "manual"
---
```

Regole:

- `rag_index: true` abilita la pagina al sync filesystem;
- pagine draft o inbox dovrebbero restare `rag_index: false`;
- `type`, `status`, `rag_scope` devono usare valori stabili per supportare i filtri;
- le pagine generate da SimpleRAG devono essere revisionate prima di diventare knowledge base canonica.

## Stato Del Vecchio Scaffold Storico

Il contratto storico del workspace citava un vecchio scaffold canonico. Nel
working tree corrente quella directory non esiste piu'; il bootstrap reale
vive in:

```text
raw/new-wiki-bootstrap.md
raw/new-wiki-scaffold/
```

Decisione chiusa:

- usare `raw/new-wiki-bootstrap.md` e `raw/new-wiki-scaffold/` come fonti
  canoniche per il bootstrap dei nuovi wiki.
- mantenere `web-memory` come esempio attivo del contratto aggiornato.

## Backlog Residuo

| Priorita | Attivita | Motivazione |
|---|---|---|
| Alta | Aggiungere test minimi diretti per `wiki_service/service_api.py` nel repo wiki | Oggi i test passano da `simple_rag`; il servizio dovrebbe avere anche smoke test propri |
| Media | Uniformare helper interni tra Wiki Service e PE Service | I due microservizi sono volutamente simili ma duplicano validazione, audit e index JSON |
| Media | Documentare policy `.obsidian/` | Va deciso se versionare solo config condivise o ignorare tutta la directory |
| Media | Aggiungere esempi frontmatter aggiornati nei template scelti | Migliora coerenza tra sync filesystem e pagine generate |
| Bassa | Aggiungere endpoint di stats storage | Utile per diagnostica manuale, non necessario per il loop operativo |

## Criteri Di Validazione

Standalone Wiki Service:

- health risponde senza token;
- list/create/get/update/delete document richiedono token;
- token errato produce `401`;
- path traversal produce errore;
- estensioni non ammesse producono errore;
- file oltre limite produce errore;
- update scrive audit.

Integrato:

- `simple_rag` vede Wiki Service in `/api/v1/services/status`;
- `/api/v1/ingest/wiki` crea documento e indice in `documentation`;
- `/api/v1/ingest/wiki/sync` indicizza pagine con `rag_index: true`;
- query integrata recupera fonti wiki quando rilevanti;
- `/api/v1/interactions` persiste query e fonti;
- scritture wiki senza conferma falliscono;
- scritture wiki confermate aggiornano storage e indice;
- export query/source notes genera Markdown e lo reindicizza.

## Documenti Correnti Di Riferimento

Root workspace:

- `README.md`
- `README_MANUAL_TESTS.md`
- `INTEGRATED_PLATFORM_OVERVIEW.md`
- `TESTBOOK_INTEGRATED_PLATFORM.md`

Wiki workspace:

- `README.md`
- `AGENTS.md`
- `LLM Wiki Operating Model.md`
- `raw/new-wiki-bootstrap.md`
- `raw/new-wiki-scaffold/`

I documenti storici possono restare consultabili, ma non devono prevalere sul
contratto operativo corrente.

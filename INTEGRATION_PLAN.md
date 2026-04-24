# SimpleRAG <-> llm-wiki-workspace - Integration Plan

## Sommario esecutivo
SimpleRAG already has a usable local RAG core: it ingests files into Qdrant, retrieves with hybrid scoring, and answers through a FastAPI API and SSE stream. The wiki workspace now has a real scaffold as well: root navigation and logs exist, `wikis/index.md` exists, and `wikis/_template/` contains the canonical skeleton and RAG-oriented page templates.

The minimum practical bridge is still file-based and local. On the SimpleRAG side, add an opt-in wiki-aware Markdown connector that parses YAML frontmatter and emits RAG-ready payload metadata. On the wiki side, standardize frontmatter, add RAG-enriched page templates, and define a query-to-page workflow so durable retrieval results are written back into the wiki instead of staying only in chat.

This keeps the existing SimpleRAG pipeline backward compatible and avoids cloud-specific coupling. It also makes the wiki a first-class knowledge source for SimpleRAG without forcing a rewrite of the current ingestion and query stack.

The workspace scaffold side of the contract is now partially implemented in this checkout: `index.md`, `log.md`, `wikis/index.md`, `wikis/_template/`, `manifest.md`, `AGENTS.md`, `wiki/overview.md`, `wiki/templates/README.md`, `rag-frontmatter.md`, `rag-enriched.md`, `query-page.md`, and `source-page.md` exist and encode the intended shape. The remaining work is to create a concrete first wiki instance and wire SimpleRAG to consume these pages.

## Stato attuale

### SimpleRAG - punti chiave
- Stack: Python, FastAPI, Qdrant local via `qdrant-client`, OpenAI SDK for embeddings and chat, pytest for tests, React/Vite frontend served by the backend.
- Entrypoints: `api.py` is the compatibility bootstrap, `rag_project/src/rag_app/api/http.py` is the main FastAPI app, and `rag_project/run_local.py` is the local launcher.
- Ingestion: `rag_project/src/rag_app/services/ingestion_pipeline.py` discovers sources, loads documents, normalizes text, chunks, embeds, and upserts into Qdrant.
- Supported inputs: local files via `local_folder`, plus `web` and `notion` connectors; file loading supports text, PDF, DOCX, XLSX/XLS, PPTX, and images through MarkItDown-first loading with legacy fallbacks.
- Retrieval: `rag_project/src/rag_app/services/retriever.py` uses query expansion, hybrid lexical reranking, namespace filtering, ext filtering, and path filtering.
- Query flow: `rag_project/src/rag_app/services/query_service.py` resolves cache, retrieves hits, builds context, generates an answer, persists session turns, and schedules inline evaluation.
- Outputs: JSON API responses, SSE token streaming, session history in SQLite-backed storage, ingestion jobs in JSON, audit logs, token usage tracking, and report exports to PDF/DOCX.
- Persistence: Qdrant local storage in `qdrant_data`, runtime settings in `admin_settings.json`, data sources in `data_sources.yaml`, search profiles in `search_profiles.json`, sessions in SQLite through `database.py`, and job state in `ingestion_jobs.json`.
- Config: `.env`, `admin_settings.json`, and runtime settings expose models, namespace, collection, chunking, cache, agent, and web fallback controls.
- Technical debt: legacy wrappers remain at repo root, state is split across JSON/SQLite/Qdrant, and the current loader path does not understand wiki frontmatter as a first-class schema.

### llm-wiki-workspace - punti chiave
- Operating contract exists at the workspace root in `AGENTS.md`, `README.md`, `LLM Wiki Operating Model.md`, `Guida Codex Wiki.md`, and `Decision Log.md`.
- The workspace model is clear: `raw/` is intake, each wiki should live under `wikis/<wiki-slug>/`, and the lifecycle should move from raw -> sources -> wiki -> archive.
- Canonical page types already exist in the contract: `overview`, `topic`, `concept`, `entity`, `tool`, `query`, `comparison`, `source`, `archive`, `inbox`.
- The workspace scaffold is now bootstrapped: root `index.md` / `log.md` exist, `wikis/index.md` exists, and `wikis/_template/` contains the canonical skeleton and page templates.
- The remaining gap is not the contract shape but the lack of at least one concrete wiki instance under `wikis/<wiki-slug>/`.
- Missing second-brain elements now shift from structure to usage: live index population, explicit backlinking at page level, query-page automation in a concrete wiki, and a review queue for durable answers.

## Gap di integrazione

| Gap | Impatto | Priorita |
|---|---|---|
| Wiki Markdown is treated as plain text in SimpleRAG | Frontmatter is ignored, so page type, tags, status, and `rag_index` are not filterable | High |
| No bidirectional write-back from SimpleRAG into the wiki | Queries stay ephemeral and do not become durable knowledge | High |
| No canonical frontmatter schema for RAG-indexable wiki pages | Metadata cannot be used consistently across pages and retrieval | High |
| No concrete wiki instance exists yet under `wikis/<wiki-slug>/` | Query/source page workflows have no live target wiki to operate on | High |
| Incremental sync only knows file path/hash/mtime, not wiki semantics | Renames, moves, and source-page updates may drift from retrieval state | Medium |
| Retrieval filters currently target source/file metadata, not wiki page metadata | Search quality for wiki content will be coarse unless metadata mapping is added | Medium |
| No explicit durable-answer policy for query pages | The wiki can become noisy if every chat answer is persisted blindly | Medium |

## Architettura dell'integrazione

```text
External document (PDF, MD, URL)
         |
         v
  llm-wiki-workspace/raw/
         |
         | [workspace ingest workflow]
         v
  wikis/<slug>/raw/
         |
         | [wiki ingest workflow]
         v
  wikis/<slug>/wiki/sources/
         |
         | [wiki update workflow]
         v
  wikis/<slug>/wiki/*.md  <-------------------------------+
         |                                                |
         | [SimpleRAG wiki connector / loader]           |
         v                                                |
  Qdrant local collection + namespace                     |
         |                                                |
         | [SimpleRAG query / retrieval / agent]         |
         v                                                |
  Answer + retrieved chunks + citations                   |
         |                                                |
         | [RAG -> wiki query-page workflow]              |
         v                                                |
  wikis/<slug>/wiki/queries/<query-slug>.md --------------+
```

## Implementazioni su SimpleRAG

### [INT-SR-01] Wiki Markdown Loader
- **Descrizione**: add an opt-in wiki-aware connector that discovers `wikis/<slug>/wiki/**/*.md`, parses YAML frontmatter, and emits metadata-rich payloads for Qdrant.
- **File da creare/modificare**:
  - create `rag_project/src/rag_app/connectors/wiki_workspace.py`
  - optionally create `rag_project/loaders_wiki.py` for frontmatter parsing helpers
  - modify `rag_project/src/rag_app/connectors/__init__.py` to register the new connector
  - update `rag_project/data_sources.yaml` example to allow a `wiki_workspace` source
- **Codice / pseudocodice**:
  - read file text
  - split frontmatter from body using the first `---` block
  - parse YAML with `yaml.safe_load`
  - default `rag_index=False` when frontmatter is missing or invalid
  - only emit chunks for pages where `rag_index: true`
  - attach payload fields such as `wiki_slug`, `page_type`, `tags`, `related`, `status`, `confidence`, `rag_scope`, `last_reviewed`, `created`, `source`, `path`, `file_hash`, `file_mtime`
- **Dipendenze**: `pyyaml` already exists; no new cloud dependency is required.

### [INT-SR-02] Frontmatter Metadata Filter
- **Descrizione**: extend query parsing and retrieval filtering so wiki metadata can be used at search time.
- **File da creare/modificare**:
  - modify `rag_project/query_parser.py`
  - modify `rag_project/src/rag_app/services/retriever.py`
  - modify `rag_project/src/rag_app/core/vector_store.py` if a richer Qdrant filter builder is needed
  - update tests under `rag_project/tests/`
- **Codice / pseudocodice**:
  - accept query hints like `wiki:<slug>`, `page_type:<type>`, `status:<value>`, `rag_scope:<scope>`, and `tag:<value>`
  - map parsed filters to Qdrant `FieldCondition` objects on payload keys
  - preserve existing `source:`, `type:`, `ext:`, and `path:` syntax for backward compatibility
  - keep namespace filtering intact so wiki data can be isolated from other corpora
- **Dipendenze**: retrieval and vector store internals already exist; the change is additive.

### [INT-SR-03] Incremental Index Sync
- **Descrizione**: add a wiki sync path that updates only changed pages, deletes stale paths, and keeps Qdrant aligned with the wiki tree.
- **File da creare/modificare**:
  - modify `rag_project/src/rag_app/services/indexer.py`
  - modify `rag_project/src/rag_app/services/ingestion_pipeline.py`
  - optionally create `rag_project/sync_wiki_workspace.py` or a dedicated CLI wrapper
  - update `rag_project/schedule_reindex.py` if scheduled sync should cover the wiki source
- **Codice / pseudocodice**:
  - compute file identity with path + mtime + checksum
  - compare indexed metadata against the current wiki file list
  - delete points for paths removed or renamed
  - re-ingest only pages whose checksum or mtime changed
  - keep `rag_index: false` pages out of the index entirely
- **Dipendenze**: uses existing `get_indexed_file_metadata`, `delete_points_by_path`, and `delete_points_by_paths` logic.

## Implementazioni su llm-wiki-workspace

### [INT-WK-01] Frontmatter Standard Schema
- **Descrizione**: standardize the wiki frontmatter schema so SimpleRAG can index pages consistently.
- **File da creare/modificare**:
  - modify workspace root `AGENTS.md`
  - create `wikis/_template/wiki/templates/rag-frontmatter.md`
  - optionally create `wikis/_template/wiki/templates/rag-page-template.md`
- **Stato attuale**: scaffold implemented in the workspace template; next step is to apply the schema to the first concrete wiki instance.
- **Contenuto proposto**:
  - required fields: `title`, `type`, `tags`, `related`, `status`, `confidence`, `rag_index`, `rag_scope`, `last_reviewed`, `created`, `source`
  - canonical page type values: `concept`, `entity`, `tool`, `query`, `topic`, `comparison`, `source`, `moc`
  - default rule: only `rag_index: true` pages are eligible for SimpleRAG indexing
  - explicit status values: `active`, `stale`, `draft`, `archived`

### [INT-WK-02] Template pagina wiki RAG-enriched
- **Descrizione**: provide a reusable page template for wiki pages that should be queryable by SimpleRAG.
- **File da creare/modificare**:
  - create `wikis/_template/wiki/templates/rag-enriched.md`
  - optionally create per-wiki template copies once a wiki is bootstrapped
- **Stato attuale**: template implemented in the workspace scaffold.
- **Contenuto proposto**:
  - frontmatter block using the standard schema
  - body sections for summary, evidence, claims, related pages, open questions, and next actions
  - backlinks section that links to parent topic pages and source notes
  - an explicit note that `rag_index` should stay `false` for drafts and staging notes

### [INT-WK-03] Workflow RAG Query -> Query Page
- **Descrizione**: turn repeated or durable SimpleRAG answers into wiki query pages.
- **File da creare/modificare**:
  - create `wikis/<wiki-slug>/wiki/queries/<query-slug>.md`
  - optionally create `wikis/_template/wiki/templates/query-page.md`
  - update wiki-local `index.md` and `log.md` once a wiki exists
- **Stato attuale**: template implemented in the workspace scaffold; concrete pages still need to be created inside a live wiki.
- **Contenuto proposto**:
  - question text
  - short answer
  - retrieved evidence and citations
  - linked source pages
  - follow-up questions or gaps
  - `rag_index: true` if the query page is meant to be searchable later

### [INT-WK-04] Aggiornamento AGENTS.md con workflow rag-ingest
- **Descrizione**: document the ingest flow that converts SimpleRAG outputs into maintained wiki knowledge.
- **File da creare/modificare**:
  - modify workspace root `AGENTS.md`
  - optionally mirror the same section into wiki-local `AGENTS.md` files once wiki instances exist
- **Stato attuale**: workspace contract updated; the wiki-local mirror still needs to be instantiated in a real wiki.
- **Contenuto proposto**:
  - receive the query text and the top-k retrieved chunks from SimpleRAG
  - check whether a query page already exists in `wiki/queries/`
  - create or update a query page with evidence and synthesis
  - identify source pages for novel claims and update them
  - set `rag_index: true` on updated durable pages
  - update `index.md` and `log.md`
  - run lint on affected pages before closing the session

## Ciclo completo end-to-end

1. An external document enters `llm-wiki-workspace/raw/` or a wiki-local `raw/` folder.
2. A workspace ingest workflow assigns it to a wiki slug and moves it into `wikis/<slug>/raw/`.
3. The wiki ingest workflow extracts claims and sources, then writes source notes and maintained pages under `wikis/<slug>/wiki/`.
4. Pages that should be searchable are written with the standard frontmatter and `rag_index: true`.
5. SimpleRAG ingests the wiki tree through the new wiki-aware connector, storing metadata-rich chunks in Qdrant.
6. A user asks a question in SimpleRAG; retrieval pulls from both regular corpus sources and wiki pages, depending on configured source selection.
7. If the answer is durable, the RAG output is converted into a wiki query page under `wiki/queries/`.
8. The query page and any affected source or concept pages are reindexed by SimpleRAG on the next incremental sync.

## Ordine di implementazione consigliato

| Step | Cosa fare | Stima effort | Dipendenze |
|---|---|---:|---|
| 1 | Bootstrap the first concrete wiki instance from the scaffold | 0.5-1 day | workspace scaffold |
| 2 | Apply the frontmatter schema and page templates to the first wiki instance | 0.5 day | Step 1 |
| 3 | Implement the wiki-aware connector and frontmatter parser in SimpleRAG | 1 day | Step 2 |
| 4 | Add retrieval filters for wiki metadata and keep existing filters backward compatible | 0.5 day | Step 3 |
| 5 | Add incremental sync for wiki pages, including stale path cleanup | 0.5-1 day | Step 3 |
| 6 | Add query-page write-back workflow and durable-answer policy | 0.5 day | Steps 2-5 |
| 7 | Run an end-to-end test with one real wiki page, one query, and one query-page round trip | 0.5 day | Steps 1-6 |

## Rischi e trade-off

- The workspace scaffold exists, but no concrete wiki instance is live yet, so the integration cannot be exercised end-to-end until a first wiki is bootstrapped.
- Frontmatter parsing must fail closed for invalid YAML, but it must not break existing non-wiki Markdown ingestion.
- If every query becomes a wiki page, the workspace will accumulate noise; a durable-answer policy is needed to decide what deserves persistence.
- Path-based incremental sync is simple and fast, but it needs explicit stale-path deletion to handle renames and moves correctly.
- Over-indexing all wiki pages would reduce retrieval quality; `rag_index: true` should remain a hard gate.
- SimpleRAG still depends on the current model provider and local Qdrant storage; a fully offline variant would require separate model work and is out of scope for this bridge.
- The wiki and SimpleRAG must keep their contracts stable together; changes to page types or payload metadata should be treated as cross-repo contract changes, not local implementation details.

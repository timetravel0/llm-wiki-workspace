# LLM Wiki Workspace

Multi-wiki workspace for Codex-driven knowledge bases.

This repository hosts a persistent set of markdown wikis maintained by
LLM-assisted workflows for:

- ingesting new source material
- updating existing wiki pages
- answering durable questions as query pages
- linting for contradictions, gaps, and broken links
- archiving processed originals and obsolete pages

## Workspace Layout

- `AGENTS.md` - global operating contract
- `README.md` - workspace overview
- `raw/` - intake area for unassigned material
- `wikis/` - independent wiki instances
- `wikis/index.md` - registry of all wiki instances

Active wiki examples:

- `nova-payment-runbook`
- `airasca`
- `web-memory`

## Working Model

- `raw/` is the workspace intake area for unassigned source material.
- `wikis/<wiki-slug>/` contains one independent wiki instance.
- Each wiki keeps its own `manifest.md`, `AGENTS.md`, `index.md`, `log.md`,
  `raw/`, and `wiki/` tree.
- The workspace root documents the operating model, prompt cookbook, and
  decision log for the whole solution.
- `web-memory` is the current example wiki for curated web acquisition before
  selective publication to `simple_rag`.

## Bootstrap And Update Flow

The current bootstrap references live in:

- `raw/new-wiki-bootstrap.md`
- `raw/new-wiki-scaffold/`

Use those files when creating a new wiki from workspace intake material.

Typical workflows:

- create a new wiki from material in `raw/`
- update an existing wiki with new sources
- query the wiki and save durable answers as query pages
- lint the wiki for missing links, contradictions, and coverage gaps

## Internal Wiki Service

`wiki_service/service_api.py` exposes a minimal localhost-only FastAPI service
for Markdown document storage used by `simple_rag`.

Run locally:

```powershell
$env:INTERNAL_API_TOKEN="change_me_use_a_long_random_secret"
$env:WIKI_DOCS_DIR="./docs"
python wiki_service/service_api.py
```

Standalone mode is the default: the service reads the local project `.env` and
does not read the root `.env.shared` unless `WIKI_LOAD_SHARED_ENV=true` is set.
When enabled, `WIKI_SHARED_ENV_PATH` defaults to `../.env.shared`.

For integrated platform runs, keep shared values such as `INTERNAL_API_TOKEN`,
`WIKI_DOCS_DIR`, `WIKI_SERVICE_PORT`, and `WIKI_MAX_FILE_SIZE_BYTES` in the
root workspace `.env.shared` to avoid drift across projects.

Endpoints:

- `GET /api/v1/health`
- `POST /api/v1/documents`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{doc_id}/content`
- `GET /api/v1/documents/{doc_id}/raw`
- `PUT /api/v1/documents/{doc_id}`
- `DELETE /api/v1/documents/{doc_id}`
- `GET /api/v1/sections`

All endpoints except health require `Authorization: Bearer $INTERNAL_API_TOKEN`.
Swagger and ReDoc are disabled.

Storage defaults to:

```text
docs/
  index.json
  audit.jsonl
  _store/
    <doc_id>/
      content.md
      meta.json
```

`simple_rag` can also index the existing wiki filesystem directly through
`POST /api/v1/ingest/wiki/sync`. That path reads
`wikis/<slug>/wiki/**/*.md`, parses YAML frontmatter, indexes only pages with
`rag_index: true`, and skips unchanged pages using a local hash state file in
`simple_rag`.

## Native Wiki Publishing To simple_rag

The preferred integrated workflow keeps wiki creation and updates native to
this workspace:

1. Place source material in `raw/` or `wikis/<wiki-slug>/raw/`.
2. Ask Codex to create or update the wiki according to `AGENTS.md`.
3. Codex writes durable pages under `wikis/<wiki-slug>/wiki/`.
4. Codex marks reusable pages with `rag_index: true`.
5. Codex runs the publisher:

```powershell
python scripts/publish_to_integrated_platform.py --wiki-slug <wiki-slug> --require-simple-rag-sync
```

The publisher:

- scans `wikis/<wiki-slug>/wiki/**/*.md`;
- selects only active pages with `rag_index: true`;
- publishes them to `wiki_service/service_api.py`;
- replaces changed documents by path;
- calls `simple_rag /api/v1/sync/wiki-service` so the `documentation`
  collection is updated immediately.

In the integrated platform, these curated wiki pages are also a first-class
knowledge source for `simple_rag` and its Coordinator. The documentation pages
published from this workspace can be indexed directly or consumed through the
internal wiki service, while the workspace remains the source of truth for the
curated markdown tree.

Dry run:

```powershell
python scripts/publish_to_integrated_platform.py --wiki-slug <wiki-slug> --dry-run
```

Required integrated env:

```env
WIKI_LOAD_SHARED_ENV=true
WIKI_SHARED_ENV_PATH=../.env.shared
INTERNAL_API_TOKEN=<shared internal token>
API_AUTH_TOKEN=<simple_rag API token>
WIKI_SERVICE_URL=http://127.0.0.1:8200
SIMPLE_RAG_URL=http://127.0.0.1:8000
```

## License

See [LICENSE](LICENSE).

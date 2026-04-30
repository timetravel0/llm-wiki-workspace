# LLM Wiki Workspace

Multi-wiki workspace for Codex-driven knowledge bases.

This repository hosts a persistent set of markdown wikis maintained by LLM-assisted workflows for:

- ingesting new source material
- updating existing wiki pages
- answering durable questions as query pages
- linting for contradictions, gaps, and broken links
- archiving processed originals and obsolete pages

## Repository Layout

```text
.
├── AGENTS.md
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── Decision Log.md
├── Guida Codex Wiki.md
├── LLM Wiki Operating Model.md
├── raw/
├── wikis/
└── ...
```

## Working Model

- `raw/` is the workspace intake area for unassigned source material.
- `wikis/<wiki-slug>/` contains one independent wiki instance.
- Each wiki keeps its own `manifest.md`, `AGENTS.md`, `index.md`, `log.md`, `raw/`, and `wiki/` tree.
- The workspace root documents the operating model, prompt cookbook, and decision log for the whole solution.

## Typical Workflows

- `create` a new wiki from material in `raw/`
- `update` an existing wiki with new sources
- `query` the wiki and save durable answers as query pages
- `lint` the wiki for missing links, contradictions, and coverage gaps

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
`WIKI_DOCS_DIR`, `WIKI_SERVICE_PORT`, and `WIKI_MAX_FILE_SIZE_BYTES` in the root
workspace `.env.shared` to avoid drift across projects.

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

## License

See [LICENSE](LICENSE).

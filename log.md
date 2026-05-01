# Workspace Log

Append-only record of workspace-level events.

## 2026-04-23 - workspace bootstrap for RAG integration

- Added the workspace home page.
- Added the workspace log page.
- Added the wiki registry page.
- Added the canonical wiki scaffold under `wikis/_template/`.
- Standardized the RAG-compatible frontmatter contract in `AGENTS.md`.

## 2026-04-24 - existing wikis aligned to new scaffold

- Propagated the RAG-oriented templates into the four existing wiki instances.
- Aligned each wiki-local `AGENTS.md`, `manifest.md`, `wiki/templates/README.md`, and `wiki/overview.md` with the new scaffold contract.
- Migrated the main query and source pages to the new frontmatter schema where applicable.

## 2026-05-01 - bootstrap nova-payment-runbook wiki

- Created the `nova-payment-runbook` wiki from `raw/nova-payment-runbook.md`.
- Registered the wiki in `wikis/index.md`.
- Added initial maintained pages for the overview, controls query, and source notes.
- Archived the processed original under `wikis/nova-payment-runbook/wiki/sources/raw/`.

# Manifest

## Identity

- `slug`: `<wiki-slug>`
- `title`: `<wiki title>`
- `status`: `active`
- `owner`: `Codex`

## Purpose

State why this wiki exists as a separate knowledge base.

## Domain Boundary

Describe the subject area this wiki owns.

## In Scope

- Core concepts, entities, tools, or topics that belong here
- Durable queries that should become query pages
- Source notes and evidence that support maintained pages

## Out of Scope

- Material that belongs in another wiki
- Temporary chat output that should not become a page
- Secrets, credentials, or private keys

## Primary Sources

- `raw/` material assigned to this wiki
- `wiki/sources/` extracted evidence and source notes
- External source types if they are explicitly part of the wiki boundary

## Canonical Page Types

- `overview`
- `topic`
- `concept`
- `entity`
- `tool`
- `query`
- `comparison`
- `source`
- `archive`
- `inbox`

## Update Criteria

- Add or update pages when new evidence changes the durable understanding.
- Prefer updating an existing page over creating a duplicate.
- Create a query page when a question recurs or deserves a durable answer.
- Archive obsolete content instead of deleting it when historical context matters.

## Navigation Contract

- `index.md` is the catalog.
- `log.md` is the chronology.
- `wiki/overview.md` is the top-level synthesis.
- `wiki/templates/` contains reusable page templates.

## Evidence Rules

- Keep contradiction traces visible.
- Prefer explicit backlinks over hidden context.
- Record uncertainty with `confidence` and `status`.
- Keep source pages close to the claims they support.

## Maintenance Notes

- Update this manifest when the wiki boundary changes.
- Keep the scope narrow enough that the wiki stays coherent.
- Treat this file as the local operating contract for the wiki instance.


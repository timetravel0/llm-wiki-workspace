# Workspace Decision Log

Append-only record of structural decisions for the LLM Wiki workspace.

## [2026-04-22] multi-wiki workspace adopted

- The vault was restructured to support multiple independent wiki instances.
- The workspace root became the orchestration layer.
- Each wiki got its own `raw/`, `index.md`, `log.md`, and `AGENTS.md`.

## [2026-04-22] workspace raw intake established

- The root `raw/` folder was designated as the staging area for unassigned material.
- New wiki creation now starts by triaging the workspace raw corpus.

## [2026-04-22] manifest-first wiki model adopted

- Every wiki should have a `manifest.md` describing scope and boundaries.
- `AGENTS.md` should carry workflow and operating rules, not domain knowledge.
- `index.md` should remain a catalog, and `log.md` should remain a chronology.

## [2026-04-22] scaffold template introduced

- The canonical bootstrap scaffold now lives under `wikis/_template/`.
- New wiki creation should copy from the scaffold rather than improvising structure.


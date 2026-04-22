# LLM Wiki Operating Model

This workspace implements a persistent, multi-wiki knowledge system maintained by Codex.

## What This Is

Each wiki is a durable knowledge base that compiles raw sources into structured markdown pages.
The workspace can hold several independent wikis at once.

## Core Idea

- `raw/` is where unassigned source material lands.
- A wiki owns its own `raw/`, `index.md`, `log.md`, `AGENTS.md`, and `wiki/` tree.
- Codex reads sources, writes or updates pages, and keeps the wiki consistent over time.
- The wiki is the maintained artifact; raw files are only evidence.

## Main Workflows

### Create

Use this when the material in workspace `raw/` should become a new wiki.

1. Decide whether the corpus justifies its own wiki.
2. Choose a stable slug.
3. Bootstrap the wiki structure.
4. Register it in `wikis/index.md`.
5. Move the source files into the wiki-local `raw/`.
6. Ingest the corpus.
7. Record the creation in the log.

### Update

Use this when a wiki receives new material or needs deeper coverage.

1. Read the new source material.
2. Update source notes and related pages.
3. Keep the taxonomy consistent.
4. Archive processed originals.
5. Refresh the index and log.

### Query

Use this when you want an answer from the wiki.

1. Read the wiki index first.
2. Open the relevant pages.
3. Synthesize a durable answer.
4. Save the answer as a query page if it is worth keeping.

### Lint

Use this when you want quality control.

1. Check links, orphans, stale claims, and missing concepts.
2. Look for contradictions and underlinked pages.
3. Propose concrete fixes.

## Documentation Layers

- Workspace docs describe how the whole system is run.
- Wiki-local docs describe how one wiki is structured.
- Prompt cookbook docs show the exact commands to use with Codex.
- Decision logs capture durable architectural or strategic choices when a wiki needs them.
- The scaffold template under `wikis/_template/` is the canonical starting point for new wikis.

## Stability Rules

- Keep files single-purpose.
- Prefer linking over duplicating.
- Archive rather than delete when historical context matters.
- Make source ownership explicit.
- Keep the operational contract close to the files it governs.

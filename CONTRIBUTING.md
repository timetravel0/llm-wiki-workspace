# Contributing

This repository is a multi-wiki workspace. Contributions should preserve the separation between workspace-level docs and wiki-local knowledge.

## Before You Edit

- Identify the target wiki.
- Decide whether the change is `create`, `update`, `query`, `lint`, or `archive`.
- Read the relevant `index.md`, `log.md`, and `AGENTS.md` first.
- Keep raw sources untouched until they are ingested and archived.

## Editing Rules

- Prefer small, coherent changes.
- Prefer updating existing pages over creating duplicates.
- Use lowercase kebab-case for filenames and folders.
- Keep pages single-purpose.
- Do not store secrets, credentials, tokens, or private keys in the repo.
- Mark inferred conclusions explicitly.

## Ingest Rules

- Create or update the source note first.
- Update dependent entity, concept, topic, tool, comparison, and query pages.
- Refresh the wiki index and log in the same session.
- Move processed originals into `wiki/sources/raw/`.
- Preserve contradictions when sources disagree.

## Query Rules

- Answer from the wiki, not directly from raw material unless necessary.
- Read the wiki index first.
- Save durable answers as query pages.
- Cite the pages consulted in the answer or page content.

## Lint Rules

- Check for broken links.
- Check for orphan or weakly linked pages.
- Check for stale claims and unresolved contradictions.
- Check for concepts or recurring questions that still lack pages.

## Pull Requests

- Keep changes scoped to one wiki or one workspace concern when possible.
- Mention any source files that were moved or archived.
- Mention any pages that were created, updated, or marked obsolete.


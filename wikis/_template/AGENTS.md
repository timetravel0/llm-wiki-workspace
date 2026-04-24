# Wiki Agent Contract

This file defines the local operating rules for a single wiki instance.

## Scope

- Keep the wiki focused on a single boundary.
- Use the workspace contract for cross-wiki behavior.
- Prefer small, coherent edits over broad rewrites.
- Preserve evidence traces when updating pages.

## Local Lifecycle

- `raw/` holds wiki-local intake material.
- `wiki/sources/` stores source notes and extracted evidence.
- `wiki/` stores maintained knowledge pages.
- `wiki/archive/` stores obsolete content that should remain searchable.

## Local Rules

- Keep page slugs lowercase and kebab-case.
- Use one canonical page per durable topic when possible.
- Update `index.md` and `log.md` with substantive content changes.
- Mark contradictions and uncertainty explicitly.

## RAG Support

- Use the workspace frontmatter schema for RAG-indexable pages.
- Keep `rag_index: true` only for pages that are ready to be indexed.
- Prefer query pages for durable answers that recur.


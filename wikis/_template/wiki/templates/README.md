# Wiki Templates

This folder stores reusable page templates for new wiki instances and for recurring page patterns inside an existing wiki.

## Available Templates

- `rag-frontmatter.md` - canonical frontmatter block for RAG-indexable pages
- `rag-enriched.md` - maintained page template with evidence, claims, and maintenance notes
- `query-page.md` - durable answer template for recurring questions
- `source-page.md` - source note template for extracted evidence and claims

## When To Use Them

- Use `rag-frontmatter.md` when starting a page that should be indexed by SimpleRAG.
- Use `rag-enriched.md` when writing a maintained concept, entity, tool, or topic page that may later become searchable.
- Use `query-page.md` when turning a recurring answer into durable knowledge.
- Use `source-page.md` when documenting the evidence path for an original artifact or a source note.

## Working Rules

- Copy templates into the wiki-local `wiki/` tree rather than editing them in place when creating new content.
- Keep page titles, slugs, and frontmatter consistent with the local wiki manifest.
- Set `rag_index: true` only when the page is ready to be searchable.
- Prefer updating an existing page over creating a duplicate when a template already maps to the subject.

## Maintenance Notes

- Keep templates small and explicit.
- Update this folder when the canonical page structure changes.
- Treat these files as the source of truth for page shape in new wiki instances.


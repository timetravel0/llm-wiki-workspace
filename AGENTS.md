# Workspace Operating Schema

This vault is a multi-wiki workspace. The workspace layer coordinates independent wiki instances, but does not own domain knowledge itself.

## Purpose

- Keep multiple LLM-maintained wikis isolated inside one vault.
- Provide one consistent operating contract for create, update, query, lint, and archive workflows.
- Make `raw/` the intake area for unassigned material and `wikis/<wiki-slug>/raw/` the intake area for a specific wiki.

## Layer Model

### Workspace layer

- `AGENTS.md` defines the global operating contract.
- `wikis/index.md` is the registry of all wiki instances.
- `index.md` is the workspace home and navigation entry point.
- `log.md` records workspace-level events such as bootstrap, refactor, and registry changes.
- `raw/` holds source material that has not yet been assigned to a wiki.
- `wikis/_template/` is the canonical scaffold source for new wiki instances.

### Wiki layer

- `wikis/<wiki-slug>/AGENTS.md` defines wiki-local behavior.
- `wikis/<wiki-slug>/manifest.md` states the wiki scope and boundaries.
- `wikis/<wiki-slug>/index.md` catalogs the wiki.
- `wikis/<wiki-slug>/log.md` records wiki-local chronology.
- `wikis/<wiki-slug>/raw/` is the wiki-local intake area.
- `wikis/<wiki-slug>/wiki/` contains the maintained knowledge pages.

### Content lifecycle

- `raw/` -> unassigned intake
- `wikis/<wiki-slug>/raw/` -> wiki-local intake
- `wiki/sources/` -> source notes and extracted evidence
- `wiki/sources/raw/` -> archived originals after ingest
- `wiki/inbox/` -> drafted but not yet consolidated pages
- `wiki/archive/` -> obsolete but preserved pages
- `wiki/` -> active maintained knowledge

## Global Rules

- Keep wikis isolated unless the user explicitly requests a cross-wiki change.
- Never move, rename, or refactor wiki folders without a clear reason or user request.
- Use stable slugs and lowercase kebab-case filenames.
- Do not store secrets, credentials, tokens, or private keys in wiki pages.
- Prefer small, coherent changes over broad rewrites.
- Preserve contradictions rather than hiding them when evidence disagrees.
- Update `index.md` and `log.md` in the same session as substantive content changes.
- When a source is assigned to a wiki, move it out of workspace `raw/` before or after ingest according to the workflow described below, but never leave the canonical source ambiguous.

## Registry Rules

- Every wiki must be listed in `wikis/index.md`.
- Registry entries should remain small and explicit.
- Keep `slug`, `title`, `status`, `default`, `path`, and `purpose` in the registry.
- Only one wiki should be the default unless the user explicitly needs multiple defaults for a special workflow.
- If a request is ambiguous, resolve it using the default wiki or recent context.

## Naming Rules

- Use lowercase kebab-case for filenames and folder names.
- Prefer one canonical page per entity, concept, topic, tool, comparison, query, or source.
- Use page titles in frontmatter for human-readable labels.
- When a page naturally spans more than one category, choose the dominant type and link the others.

## Canonical Page Types

- `overview` for the top-level synthesis of a wiki.
- `topic` for domain-level syntheses that combine multiple sources.
- `concept` for recurring ideas, frameworks, or methods.
- `entity` for named people, systems, organizations, hosts, or projects.
- `tool` for software, services, or products.
- `query` for durable answers to recurring questions.
- `comparison` for tradeoffs and side-by-side evaluations.
- `source` for source-by-source notes and extraction.
- `archive` for obsolete content that should be retained.
- `inbox` for temporary holding pages.

## RAG-Compatible Frontmatter

Use this schema for pages that should be indexed by SimpleRAG.

```yaml
---
title: "Page title"
type: concept
tags: []
related: []
status: active
confidence: high
rag_index: true
rag_scope: global
last_reviewed: ""
created: ""
source: ""
---
```

### Field Rules

- `title` should match the page title and remain human-readable.
- `type` should use the canonical page types listed above.
- `tags` should stay short and semantic.
- `related` should contain explicit page slugs or page names used for backlinks.
- `status` should be one of `active`, `stale`, `draft`, or `archived`.
- `confidence` should be one of `high`, `medium`, `low`, or `inferred`.
- `rag_index` should be `true` only when the page is ready for RAG indexing.
- `rag_scope` should be `global`, `wiki-local`, or `private`.
- `last_reviewed` and `created` should use `YYYY-MM-DD`.
- `source` should point to the originating source page when the page is derived from another page.

## RAG Ingest Workflow

Use this when SimpleRAG results or retrieved chunks should become wiki knowledge.

1. Receive the query text and the top-k retrieved chunks from SimpleRAG.
2. Check whether a query page already exists in `wiki/queries/`.
3. If yes, update it with new evidence; if no, create a new query page.
4. For each retrieved chunk that contains novel claims:
   1. Identify the source page it belongs to in `wiki/sources/`.
   2. If the source page does not exist, create it.
   3. Update affected concept, entity, topic, comparison, or tool pages with the new claims.
5. Set `rag_index: true` in the frontmatter of all updated durable pages.
6. Update `index.md` and `log.md`.
7. Run lint on affected pages before closing the session.

## Query Page Standard

Query pages should capture durable answers, not transient chat output.

Recommended body sections:

- Question
- Answer
- Evidence
- Related pages
- Open gaps
- Next actions

Query pages should default to `type: query` and `rag_index: true` when the answer is meant to be reusable.

## Template Contract

- Keep `wikis/_template/` as the canonical scaffold for new wiki instances.
- Keep template files small, explicit, and copyable.
- Prefer templates that can be reused without editing the operating contract.
- Treat templates as source files for new wiki bootstraps, not as archived examples.

## Required Wiki Skeleton

When a new wiki is created, it should include:

- `manifest.md`
- `AGENTS.md`
- `Benvenuto.md`
- `index.md`
- `log.md`
- `Decision Log.md`
- `raw/README.md`
- `wiki/overview.md`
- `wiki/sources/raw/README.md`
- `wiki/templates/README.md`

Additional folders such as `entities/`, `concepts/`, `topics/`, `tools/`, `queries/`, `comparisons/`, `inbox/`, and `archive/` should be created when the corpus needs them.

## Bootstrap Workflow

Use this when the workspace `raw/` folder contains material that should become a new wiki.

1. Read the raw corpus and decide whether it is coherent enough for a standalone wiki.
2. Choose a stable wiki slug and a clear domain boundary.
3. Create `wikis/<wiki-slug>/` with the standard skeleton.
4. Copy the standard files from `wikis/_template/`.
5. Register the new wiki in `wikis/index.md`.
6. Move the relevant source files from workspace `raw/` into `wikis/<wiki-slug>/raw/`.
7. Ingest the sources and create the initial wiki pages.
8. Update the wiki-local `index.md`, `log.md`, and `overview.md`.
9. Record the bootstrap in the workspace `log.md`.

## Ingest Workflow

Use this when a wiki receives new material.

1. Read the source carefully.
2. Extract claims, entities, concepts, dependencies, and uncertainties.
3. Create or update source notes in `wiki/sources/`.
4. Update affected entity, concept, topic, comparison, and tool pages.
5. Add backlinks where they improve navigation.
6. Update the wiki-local `index.md`.
7. Record the ingest in the wiki-local `log.md`.
8. Move processed originals into `wiki/sources/raw/`.
9. Mark contradictions, gaps, and inferences explicitly.

## Update Workflow

Use this when existing wiki pages need refinement or expansion.

1. Identify the wiki and the pages that need attention.
2. Read the relevant pages before editing.
3. Prefer updating existing pages over creating duplicates.
4. Adjust adjacent pages if the change affects navigation or taxonomy.
5. Update `index.md` and `log.md`.
6. Keep the original evidence path traceable.

## Query Workflow

Use this when answering a question against a wiki.

1. Read the wiki `index.md` first.
2. Open the most relevant pages.
3. Synthesize from the wiki, not directly from raw files unless necessary.
4. Cite the pages consulted.
5. If the answer is durable, save it as a query page.

## Lint Workflow

Use this for periodic quality control.

Check for:

- broken links
- orphan pages
- weakly connected pages
- duplicate or redundant pages
- stale claims
- unresolved contradictions
- concepts without a dedicated page
- missing query pages for recurring questions
- raw files that were not archived after ingest

Return lint findings ordered by priority and propose concrete corrections.

## Archive Workflow

Use this when content is obsolete but still worth keeping.

1. Move the page to `wiki/archive/` or mark it archived if the wiki uses an archive convention.
2. Update links so active pages point to the current canonical page.
3. Preserve history in `log.md` if the archive move is meaningful.

## Documentation Contract

- Every wiki should have a manifest, a catalog, a log, and an overview.
- Every wiki should also have a `Decision Log.md` if the domain benefits from explicit architectural choices over time.
- Every wiki should document its own lifecycle and page taxonomy.
- Every recurring operator task should be documented either in `AGENTS.md` or in the workspace prompt cookbook.
- The prompt cookbook should show practical prompts for create, update, query, and lint workflows.
- The operating model page should explain how the whole solution fits together.

## Quality Bar

- A page should be short enough to read quickly and specific enough to be useful later.
- A durable answer should become a page, not stay only in chat.
- A wiki should remain navigable at moderate scale without requiring external tooling.
- If a concept is recurring, give it a dedicated page.
- If a question recurs, give it a durable query page.

## Default Resolution

- If a wiki is marked default in `wikis/index.md`, use it for ambiguous requests.
- If the request clearly matches an existing wiki by subject, use that wiki.
- If neither is clear, ask a concise clarification.

## Workspace Editing Policy

- Do not cross-edit two wikis in one change unless the user explicitly asks for a cross-wiki refactor.
- Preserve wiki-local histories during refactors.
- If a refactor moves wiki-local files, update the wiki-local `AGENTS.md`, `index.md`, and `log.md`.
- Keep workspace-level changes focused on workspace structure and registry behavior.

## Privacy and Safety

- Treat local IPs, endpoints, and service URLs as sensitive configuration.
- Do not invent public exposure that is not documented in the source.
- Do not write secrets to the vault.

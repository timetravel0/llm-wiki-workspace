---
title: "Page title"
type: concept
tags: []
related: []
status: draft
confidence: medium
rag_index: false
rag_scope: wiki-local
last_reviewed: ""
created: ""
source: ""
---

# Page Title

This template is for maintained pages that may later become durable RAG sources.

## Summary

Write the maintained summary here in a form that can survive later review.

## Scope

- What this page covers
- What this page does not cover
- Which pages are the canonical neighbors

## Evidence

| Claim | Evidence | Status |
|---|---|---|
| Claim that should remain durable | Source note, linked page, or excerpt | confirmed / inferred / disputed |

## Claims

- Claim that is supported by current evidence
- Claim that should remain explicit in the page body
- Claim that links to a source page or related page

## Related Pages

- Related concept page
- Related entity page
- Related source page
- Related query page

## Open Questions

- Question that still needs evidence
- Ambiguity that should not be hidden
- Missing source page or backlink

## Next Actions

- Update source notes if new evidence appears
- Add backlinks to adjacent pages
- Re-run lint if the page becomes central to navigation

## Maintenance Notes

- Keep `status` accurate when the page becomes stale or archived.
- Keep `confidence` aligned with the quality of evidence.
- Set `rag_index: true` only when the page is ready to be indexed by SimpleRAG.
- Use `rag_scope` to control whether the page should be indexed globally, only inside the wiki, or kept private.

---
title: "Source title"
type: source
tags: []
related: []
status: active
confidence: medium
rag_index: true
rag_scope: wiki-local
last_reviewed: ""
created: ""
source: ""
---

# Source Title

This template is for source notes and extracted evidence tied to an original artifact.

## Source Summary

- What the source is
- Why it matters
- What claim set it supports

## Extracted Evidence

| Claim | Evidence | Confidence |
|---|---|---|
| Claim extracted from the source | Supporting excerpt or paraphrase | high / medium / low / inferred |

## Claims

- Claim that should be retained in maintained pages
- Claim that may need cross-checking
- Claim that should link to a query or concept page

## Related Pages

- Canonical query page
- Canonical concept page
- Canonical entity or tool page

## Open Questions

- Missing context
- Ambiguous claim
- Contradiction with another source

## Next Actions

- Update affected maintained pages
- Add backlinks from the pages that use this source
- Archive the original artifact after ingest if the workflow requires it

## Maintenance Notes

- Keep the evidence path traceable.
- Do not over-summarize away disagreements.
- Set `rag_index: true` only if the source note should remain searchable.

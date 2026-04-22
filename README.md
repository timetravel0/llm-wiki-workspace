# LLM Wiki Workspace

Multi-wiki workspace for Codex-driven knowledge bases.

This repository hosts a persistent set of markdown wikis maintained by LLM-assisted workflows for:

- ingesting new source material
- updating existing wiki pages
- answering durable questions as query pages
- linting for contradictions, gaps, and broken links
- archiving processed originals and obsolete pages

## Repository Layout

```text
.
├── AGENTS.md
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── Decision Log.md
├── Guida Codex Wiki.md
├── LLM Wiki Operating Model.md
├── raw/
├── wikis/
└── ...
```

## Working Model

- `raw/` is the workspace intake area for unassigned source material.
- `wikis/<wiki-slug>/` contains one independent wiki instance.
- Each wiki keeps its own `manifest.md`, `AGENTS.md`, `index.md`, `log.md`, `raw/`, and `wiki/` tree.
- The workspace root documents the operating model, prompt cookbook, and decision log for the whole solution.

## Typical Workflows

- `create` a new wiki from material in `raw/`
- `update` an existing wiki with new sources
- `query` the wiki and save durable answers as query pages
- `lint` the wiki for missing links, contradictions, and coverage gaps

## License

See [LICENSE](LICENSE).


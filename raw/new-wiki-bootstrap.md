# New Wiki Bootstrap

Use this when source material in the workspace `raw/` folder should become a new wiki.
In normal use, the user deposits material in `raw/` and asks the agent to create the new wiki from it.

## Decision Checklist

- Is the subject broad enough to justify its own wiki?
- Does it have a stable name or slug?
- Will the new wiki stay conceptually isolated from the existing ones?
- Do the source files form a coherent corpus?

## Bootstrap Steps

1. Choose the wiki slug.
2. Create `wikis/<wiki-slug>/`.
3. Copy the standard wiki files from `wikis/_template/`.
4. Add `Decision Log.md` if the wiki needs a durable decision history.
5. Register the wiki in `wikis/index.md`.
6. Move the source files from workspace `raw/` into `wikis/<wiki-slug>/raw/`.
7. Ingest the sources and create the initial synthesis pages.
8. Record the creation in the workspace log.

## Standard Wiki Files

- `AGENTS.md`
- `Benvenuto.md`
- `index.md`
- `log.md`
- `raw/README.md`
- `wiki/overview.md`
- `wiki/sources/raw/README.md`
- `wiki/templates/README.md`

## Suggested Initial Pages

- `wiki/overview.md`
- `wiki/topics/<subject>.md`
- `wiki/concepts/<core-concept>.md`
- `wiki/comparisons/<core-comparison>.md`
- `wiki/queries/<first-recurring-question>.md`

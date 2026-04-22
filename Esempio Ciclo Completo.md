# Esempio Ciclo Completo

Questo esempio mostra il flusso completo per una wiki: deposito del materiale, richiesta a Codex, ingest, interrogazione e archiviazione.

## Scenario

Hai un pacchetto di documenti su un tema nuovo e vuoi trasformarlo in una wiki autonoma.

Per esempio:

- materiale in `raw/`
- tema: `wayout`
- obiettivo: creare una wiki nuova e poi interrogarla

## 1. Deposito Raw

Tu depositi i file nel `raw/` del workspace.

Esempio:

- `raw/Startup - Experiments.csv`
- `raw/Startup - Decision Log.csv`
- `raw/Company Profile.md`

## 2. Request A Codex

Chiedi a Codex di creare una nuova wiki dal materiale depositato.

### Prompt

```text
crea un nuovo wiki dal materiale in raw
proponi tu lo slug se non è evidente
bootstrap della wiki con index, log, AGENTS, raw e wiki
ingesta il materiale iniziale e archivia gli originali
```

### Atteso

- Codex identifica il perimetro del corpus
- Codex propone o conferma lo slug
- Codex crea `wikis/<wiki-slug>/`
- Codex crea `AGENTS.md`, `index.md`, `log.md`, `raw/` e `wiki/`
- Codex crea le prime pagine di sintesi
- Codex sposta i raw originali in `wiki/sources/raw/`

## 3. Ingest

Durante l’ingest Codex:

1. legge le fonti
2. crea le source note
3. aggiorna topic, concept, entity, use case o comparison
4. aggiorna index e log
5. archivia gli originali

### Output atteso

- una `overview`
- una `entity page`
- una `topic page`
- una o più `concept page`
- una o più `query page`
- gli originali in `wiki/sources/raw/2026/`

## 4. Query

Dopo l’ingest puoi interrogare la wiki.

### Prompt

```text
interroga il wiki wayout su quali sono i bet principali e come si distingue il portfolio dall operating system
```

### Atteso

- Codex legge `index.md`
- Codex apre le pagine più rilevanti
- Codex risponde con sintesi e riferimenti
- se la risposta è durevole, Codex la salva anche come query page

## 5. Archiviazione

La chiusura del ciclo avviene quando:

- i raw originali sono archiviati nella wiki
- il log registra l’ingest
- l’indice punta alle nuove pagine
- la risposta utile è stata trasformata in una pagina persistente

## Esempio Concreto

### Caso

Il corpus `Wayout` contiene:

- home export
- company profile
- knowledge database
- decision log
- experiments
- projects
- tasks

### Risultato

La wiki risultante contiene:

- [overview](wikis/wayout/wiki/overview.md)
- [entity](wikis/wayout/wiki/entities/wayout.md)
- [topic](wikis/wayout/wiki/topics/wayout-portfolio.md)
- [concepts](wikis/wayout/wiki/concepts/)
- [use cases](wikis/wayout/wiki/use-cases/)
- [query](wikis/wayout/wiki/queries/what-is-wayout.md)

## Variante Update

Se la wiki esiste già, il ciclo cambia solo nella parte iniziale.

### Prompt

```text
aggiorna il wiki imdatatech con il materiale depositato in raw
leggi il nuovo materiale, aggiorna le source note, rafforza le pagine collegate e archivia gli originali dopo l'ingest
```

## Variante Lint

Per manutenzione periodica:

```text
fai un lint del wiki digital-thread
```

## Regola Finale

Se il contenuto merita di essere ritrovato o riusato, deve finire nel wiki.
Non deve restare solo nella chat.

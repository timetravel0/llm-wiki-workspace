# Prompt Cookbook

Questa guida raccoglie i prompt da usare con Codex per creare, aggiornare, interrogare e fare lint delle istanze wiki del vault.

## Come Leggerla

- Usa questi prompt come base.
- Sostituisci `<wiki-slug>`, `<tema>`, `<domanda>` e `<cartella>` con il tuo caso.
- Se il materiale sta in `raw/`, Codex deve prima capire se appartiene a una wiki esistente o se deve diventare una wiki nuova.

## Principio Operativo

Codex lavora meglio quando il comando indica chiaramente:

- il tipo di azione
- il wiki target
- il materiale da leggere
- il livello di profondità desiderato
- se gli originali vanno archiviati dopo l'ingest

## Create

Usa `create` quando il materiale deve diventare una nuova wiki.

### Prompt Base

```text
crea un nuovo wiki dal materiale in raw
```

### Prompt Guidato

```text
crea un nuovo wiki dal materiale in raw
proponi tu lo slug se non è evidente
bootstrap della wiki con index, log, AGENTS, raw e wiki
ingesta il materiale iniziale e archivia gli originali
```

### Prompt Completo

```text
Ho depositato un corpus in raw.
Valuta se merita una wiki autonoma.
Se sì, crea il wiki, scegli uno slug stabile, aggiorna il registry, ingesta il materiale iniziale e archivia gli originali nella wiki.
Se il corpus non è abbastanza ampio, proponi invece come inserirlo in una wiki già esistente.
```

### Quando Usarlo

- il corpus è tematicamente isolato
- vuoi un indice e un log dedicati
- il materiale è abbastanza ampio da giustificare una knowledge base autonoma

## Update

Usa `update` quando una wiki esistente deve assorbire nuovo materiale.

### Prompt Base

```text
aggiorna il wiki <wiki-slug> con il materiale in raw
```

### Prompt Guidato

```text
aggiorna il wiki <wiki-slug> con il materiale depositato in raw
leggi il nuovo materiale, aggiorna le source note, rafforza le pagine collegate e archivia gli originali dopo l'ingest
```

### Prompt Completo

```text
Ingesta il nuovo materiale nel wiki <wiki-slug>.
Aggiorna source note, entity page, concept pages, topic pages, comparison pages e query page se utile.
Archivia gli originali nel wiki dopo l'ingest.
Aggiorna anche index e log.
```

### Quando Usarlo

- hai nuovi file in `raw/` del workspace o del wiki
- vuoi consolidare concetti già presenti
- vuoi aggiungere use case, confronti o tassonomia

## Query

Usa `query` quando vuoi una risposta basata sulla wiki.

### Prompt Base

```text
interroga il wiki <wiki-slug> su <domanda>
```

### Prompt Guidato

```text
interroga il wiki <wiki-slug> su <domanda>
usa prima index e poi le pagine rilevanti
rispondi con sintesi e riferimenti
se la risposta è durevole, salvala come query page
```

### Prompt Completo

```text
Interroga il wiki <wiki-slug> su <domanda>.
Leggi prima l'index del wiki, poi le pagine più pertinenti.
Rispondi in modo sintetico ma con i riferimenti necessari.
Se la risposta è utile nel tempo, scrivila anche come pagina query nel wiki.
```

### Quando Usarlo

- vuoi una sintesi navigabile
- vuoi una comparazione o una spiegazione
- vuoi trasformare una risposta utile in conoscenza persistente

## Lint

Usa `lint` per la manutenzione periodica delle wiki.

### Prompt Base

```text
fai un lint del wiki <wiki-slug>
```

### Prompt Guidato

```text
fai un lint del wiki <wiki-slug>
cerca contraddizioni, claim obsoleti, pagine orfane, concetti importanti senza pagina, link mancanti e gap di tassonomia
proponi anche nuove query o nuovi source pack da investigare
```

### Prompt Completo

```text
Esegui un lint del wiki <wiki-slug>.
Controlla:
- contraddizioni tra pagine
- claim superati da fonti più recenti
- pagine orfane o poco collegate
- concetti rilevanti senza una pagina dedicata
- link rotti o riferimenti incoerenti
- gap che richiedono nuove fonti o query
Restituisci i problemi ordinati per priorità e proponi le correzioni concrete.
```

### Quando Usarlo

- una wiki è cresciuta abbastanza da richiedere controllo qualità
- vuoi allineare index, log e tassonomia
- vuoi scoprire buchi di copertura o incoerenze

## Prompt Rapidi

### Nuovo wiki

```text
crea un nuovo wiki dal materiale in raw
```

### Aggiornamento wiki esistente

```text
aggiorna il wiki imdatatech con i file in raw
```

### Interrogazione

```text
interroga il wiki wayout su cosa distingue portfolio e operating system
```

### Lint

```text
fai un lint del wiki digital-thread
```

## Cosa Specificare Sempre

Per evitare ambiguità, specifica quando puoi:

- il wiki target
- il tipo di azione: create, update, query, lint
- il materiale da usare
- l'ampiezza del lavoro
- se gli originali vanno archiviati

## Come Deve Rispondere Codex

Una buona risposta dovrebbe dirti chiaramente:

- quale wiki è stato toccato
- quali file sono stati creati o aggiornati
- dove sono finiti gli originali
- quali pagine sono state collegate
- quali dubbi o contraddizioni restano aperti

Se la risposta è durevole, salvala come pagina nel wiki invece di lasciarla solo in chat.

## Dove Trovare Le Cose

- [Workspace home](Benvenuto.md)
- [Workspace schema](AGENTS.md)
- [LLM Wiki Operating Model](LLM Wiki Operating Model.md)
- [Decision Log](Decision Log.md)
- [Esempio Ciclo Completo](Esempio Ciclo Completo.md)
- [Wiki registry](wikis/index.md)
- [Workspace raw](raw/README.md)

## Flusso Standard

### Create

1. Identifica il corpus.
2. Decidi se merita una wiki nuova.
3. Crea `wikis/<slug>/`.
4. Copia lo scaffold standard.
5. Registra il wiki in `wikis/index.md`.
6. Ingesta i raw.
7. Archivia gli originali in `wiki/sources/raw/`.
8. Aggiorna `log.md`.

### Update

1. Identifica il wiki target.
2. Leggi il materiale nuovo.
3. Aggiorna le source note e le pagine collegate.
4. Rafforza o correggi la tassonomia.
5. Archivia gli originali.
6. Aggiorna `index.md` e `log.md`.

### Query

1. Identifica il wiki target.
2. Leggi `index.md` e le pagine rilevanti.
3. Rispondi con sintesi e riferimenti.
4. Se la risposta è durevole, salva una query page.

### Lint

1. Leggi `index.md`, `log.md` e le aree tematiche principali.
2. Cerca incoerenze, orfani e lacune.
3. Proponi correzioni concrete.
4. Se serve, apri nuove pagine o nuove query.

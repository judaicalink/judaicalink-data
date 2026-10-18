# ls-wikidata: generator

Every record of ours that is a Wikidata item, linked to our record of the item (decision 0029). Replaces
ls-yivo-wikidata; the drafts ls-nli-wikidata, ls-bhr-wikidata and ls-rujen-wikidata (never versions) are not needed.

## History

- 2026-10-18 (Kai Eckert): new dataset.

## Inputs

- The dataset `wikidata` (`authority`; the stable version, or the run given with `jl generate --use`).
- Our datasets and the other authority datasets (`jl.authorities.linking_inputs`), among them yivo, bhr, rujen and
  dbpedia-persons; the crawl `rujen.jsonl.gz` of the stable rujen version.

## Rules

1. Identity statements (`owl:sameAs` and the like, Wikidata IRIs in any form, our records `data/wikidata/<Q>`),
   resolved through the replacements of `wikidata` (`jl.linksets`).
2. Identifiers of our sources stated by the current items: YIVO P8569 (article name, matched as in ls-yivo-wikidata),
   BHR P10405 (the id of the portal page in `jl:describedAt`), Encyclopedia of Russian Jewry P10278 (page id or page
   name of the crawl, the IRI rule of the rujen generator). The NLI J9U ID (P8189) is not used: nli-records states no
   J9U numbers (its export has none).
3. DBpedia: a dbpedia-persons record `data/dbpedia/<name>` and the item whose English Wikipedia article has the title
   `<name>` (percent-decoded, underscores as spaces).

In 2 and 3 a link is made only if it is unique in both directions; the rest is left out and named in the log. Links
of 2 and 3 that name another item than the record's identity statements are logged; both are kept.

## Reproduction

**Reproducible** from the inputs.

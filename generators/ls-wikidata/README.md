# ls-wikidata: generator

Every record of ours that is a Wikidata item, linked (`jl:sameAs`) to our record of the item, `data/wikidata/<Q>` in
the dataset `wikidata` (decision 0029). Replaces ls-yivo-wikidata.

## History

- 2026-10-18 (Kai Eckert): new linkset (run only).
- 2026-10-19 (Kai Eckert): first version: declared identity, link quality, classes; the records of dbpedia link their
  items themselves.

## Inputs

- `wikidata/2026-10-19` (`authority`): the current items, the replacements of merged items, and the identifiers of
  our sources the items state.
- Our datasets and the other authority datasets (`jl.authorities.linking_inputs`: the stable versions, or the runs
  given with `--use`; all but wikidata itself, the linksets made from authority datasets, ep and the datasets without
  links to records), among them yivo, bhr, rujen and dbpedia; the crawl `rujen.jsonl.gz` of the stable rujen version.

## Rules

1. Identity statements, as the catalogue entry of each dataset declares them (field `identity`, decision 0032):
   Wikidata IRIs in any form, our records `data/wikidata/<Q>`; resolved through the replacements of `wikidata`, with
   the rules of every linkset (`jl.linksets`: link quality below the threshold of `catalog/link-quality.toml` left
   out, deprecated items and items not in `wikidata` left out, contradicting classes left out, several items and hubs
   listed in the log). The records of dbpedia name the item of their article (`owl:sameAs`, from Wikipedia's page
   properties), so the Wikipedia articles are linked here.
2. Identifiers of our sources stated by the current items: YIVO P8569 (article name, matched as in ls-yivo-wikidata:
   without case and accents, spaces, commas and hyphens as underscores), BHR P10405 (the id of the portal page in
   `jl:describedAt`, leading zeros ignored), Encyclopedia of Russian Jewry P10278 (page id or page name of the crawl,
   the IRI rule of the rujen generator). A link is made only if it is unique in both directions: the value leads to
   one item and that item to no other record of the dataset, and the item is not another one than the record's
   identity statements (1) name; the others are left out and named in the log. The NLI
   J9U ID (P8189) is not used: nli-records states no J9U numbers (its export has none).

## Version 2026-10-19

203,139 links in all. Identity statements: 200,633 links of 200,435 records to 77,171 items (190 records with
several); by dataset: dbpedia 73,155, gnd 60,825, viaf 59,069, cm-entities 4,848, geonames 2,681, interlinks 238,
lc 2; 916 references resolved through a replacement; left out: deprecated 18, not in wikidata 282; hubs 44.
Identifiers of our sources: yivo 1,436 (left out: 5 records with several items, 2 items of several records), bhr
1,042 (4 with several items), rujen 28. About four minutes.

## Reproduction

**Reproducible** from the inputs; a new version of any input gives a new version. Made together with the authority
datasets (`docs/process.md`, 2a).

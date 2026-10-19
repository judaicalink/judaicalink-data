# dbpedia: generator

The English and German Wikipedia articles (DBpedia resources) JudaicaLink uses (decisions 0029, 0031), from answers of
Wikipedia kept in the inputs area. Replaces dbpedia-persons (2018-10-24).

## History

- 2026-10-19 (Kai Eckert): new dataset.

## Inputs

- `inputs:cascade/2026-10-19`, written by `lookup.py` in the cascade: `dbpedia-selection.tsv.gz` (the selection) and
  `titles-en.jsonl`, `titles-de.jsonl`: the Wikipedia API (`action=query`, redirects followed, page property
  `wikibase_item`; 50 titles per request), one line per title asked: the current article (title, page id) or that it
  is missing, the title redirected from, and the Wikidata item of the article.
- `dbpedia-persons/2018-10-24`: the records the dataset replaces.

`lookup.py` asks online, with a cache per title in the work dir (`work/dbpedia-query/`), so a later cascade asks only
for new titles: resolve (the current article of a title, or none: missing, invalid, or not an article, e.g. a category
or template), links (the Wikidata item of the article), and as seeds every English or German article the records of
dbpedia-persons name by their declared identity (their own article and that in the other language).

## Selection

Per language one source (decision 0031): the article `https://<lang>.wikipedia.org/wiki/<title>` and the resource
`http://dbpedia.org/resource/<title>` (en) or `http://de.dbpedia.org/resource/<title>` (de) are one identifier.
`dbpedia-selection.tsv.gz`, one row per source (`wikipedia-en`, `wikipedia-de`), title and reason, with the current
title (empty if the article does not exist):

| Reason | Rule |
|---|---|
| `linked` | an article or resource named by one of our datasets (any statement) or by a declared identity statement of another authority dataset (decision 0032); detail: the dataset |
| `previous` | an article a record of dbpedia-persons names; detail: `dbpedia-persons/2018-10-24` |
| `replaces` | the current title of a selected title that redirects; detail: the selected title |

## Data

1. Per language and current article a record `data/dbpedia/<lang>/<title>` (the title escaped where an IRI needs it,
   `jl.identifiers.title_iri_part`): `owl:sameAs` the DBpedia resource and the Wikidata item of the article,
   `foaf:isPrimaryTopicOf` the article, `skos:prefLabel` the title (with spaces, in the language of the article).
2. The records of dbpedia-persons (`data/dbpedia/<name>`, the English article where the name is one, else the German
   one): their statements go to the record of the current article, and `data/dbpedia/<name> dcterms:isReplacedBy`
   that record (`owl:deprecated true` if the article no longer exists).
3. Redirects (decision 0031, as GND numbers in 0029): a title that redirects, `<resource of the old title>
   dcterms:isReplacedBy <resource of the current one>`, and the same for the articles; a title that does not exist,
   `<resource> owl:deprecated true`.

## Version 2026-10-19

38,572 English and 34,556 German records, 400,712 triples; 177,839 selection rows. Titles replaced: en 1,052,
de 260; missing: en 143, de 255. dbpedia-persons: 5,230 records moved to their current article, 64 without an
article (deprecated). About seven seconds (the queries are made by the cascade).

## Reproduction

**Reproducible** from the inputs. A new cascade gives a new input and a new version (`docs/process.md`, 2a).

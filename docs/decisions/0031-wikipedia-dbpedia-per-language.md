# 0031 Wikipedia and DBpedia: one source per language

Status: accepted · Date: 2026-10-18

## Context

dbpedia-persons (2018) mixes the English and the German DBpedia: its records are `data/dbpedia/<name>` with names of
both (`Osias_Thon` and `Ozjasz_Thon`, `Hans_Kohn` and `Hans_Kohn_(Historiker)`), so one person can be two records of
the same dataset; it links the DBpedias of many languages (`cs.`, `es.`, `fr.`, `ja.dbpedia.org` …). A DBpedia resource
is made from one Wikipedia article: `dbpedia.org/resource/X` is the English article `X`, `de.dbpedia.org/resource/Y`
the German article `Y`. The entity pages treated an English article, its DBpedia resource and the German ones as
different identifiers.

## Decision

- Per language, Wikipedia and DBpedia are one source: the article `https://en.wikipedia.org/wiki/X` and the resource
  `http://dbpedia.org/resource/X` are the same identifier, as are `https://de.wikipedia.org/wiki/Y` and
  `http://de.dbpedia.org/resource/Y`.
- One dataset `dbpedia` (replacing dbpedia-persons), with a namespace per language: `data/dbpedia/en/<title>` and
  `data/dbpedia/de/<title>`; records only for English and German for now.
- Other languages are links, not records: from the interlanguage links of the articles (or the DBpedia/Wikidata
  sitelinks).
- The identifiers `wikipedia-en` and `wikipedia-de` are known to the framework (jl.iris, jl.identifiers) in both
  forms.

## Consequences

- A new dataset `dbpedia`: its generator, the records of dbpedia-persons replaced by the records per language
  (`data/dbpedia/<name>` `dcterms:isReplacedBy` `data/dbpedia/en/<name>` or `…/de/<name>`).
- The entity pages and the linksets read both forms as one identifier; two records of `dbpedia` in one entity are
  then two languages, not a duplicate.

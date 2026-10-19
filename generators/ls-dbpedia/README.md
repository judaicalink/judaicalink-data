# ls-dbpedia: generator

Every record of ours that refers to an English or German Wikipedia article (or its DBpedia resource), linked
(`jl:sameAs`) to our record of the current article, `data/dbpedia/en/<title>` or `data/dbpedia/de/<title>` in the
dataset `dbpedia` (decisions 0029, 0031).

## History

- 2026-10-19 (Kai Eckert): new linkset.

## Inputs

- `dbpedia/2026-10-19` (`authority`): the current articles and the replacements of old titles.
- Our datasets and the other authority datasets (`jl.authorities.linking_inputs`: the stable versions, or the runs
  given with `--use`; all but dbpedia itself, the linksets made from authority datasets, ep and the datasets without
  links to records): the references, Wikipedia articles and DBpedia resources in any form (`jl.identifiers`:
  `wikipedia-en`, `wikipedia-de`).

## Rules (`jl.linksets`, one pass per language)

- Only identity statements count, as the catalogue entry of each dataset declares them (field `identity`, decision
  0032).
- Link quality (0032): a unit (dataset, property, target source) measured below the threshold in
  `catalog/link-quality.toml` (accuracy at least 0.95 and, when only a sample was checked, the lower bound of its 95%
  interval at least 0.90) is left out; the statement stays in its dataset.
- An old title is followed to the current article through the replacements of dbpedia (Wikipedia's redirects). A
  title that no longer exists or that dbpedia does not have, and references by blank nodes or by records of dbpedia
  itself, are left out and listed in the log.
- Classes: a link whose two sides are of contradicting kinds (a person and a work, a person or a work and a place) is
  left out.
- A record that refers to several articles of one language is linked to each and listed in the log for review; so is
  every article that three or more records of one dataset refer to (hubs).
- Titles are escaped in our record IRIs where an IRI needs it (`jl.identifiers.iri_part`:
  `Barbara_%22BJ%22_Gallagher_Hateley`).

Each link: `<record> jl:sameAs <data/dbpedia/<lang>/<title>>`.

## Version 2026-10-19

164,173 links. English: 101,378 links of 101,263 records to 38,572 articles (106 records with several); by dataset:
wikidata 38,698, gnd 37,811, viaf 31,226, dbp-wiki-geo-linking 5,710, ubffm-persons 627, interlinks 238; 1,407
references resolved through a replacement; left out: 2014links below the threshold 1,403, deprecated 111, not in
dbpedia 400; hubs 31. German: 62,795 links of 62,774 records to 34,556 articles (20 with several); by dataset:
wikidata 34,655, gnd 27,996, interlinks 173, dbp-wiki-geo-linking 46; 244 resolved through a replacement; left out:
deprecated 17, not in dbpedia 2; hubs 16. About five minutes.

## Reproduction

**Reproducible** from the inputs; a new version of any input gives a new version. Made together with the authority
datasets (`docs/process.md`, 2a).

# dbpedia-persons: generator history

Persons from DBpedia (rabbis and Jewish persons) with GND numbers and EntityFacts links, by Maral Dadvar.

## History

- 2017-03: person generator querying DBpedia (`dbp-person-occupation.py`, loader `328c5ef` … `758a68d`, renamed
  `person_generator_DBPedia.py` 2017-04-21) and GND numbers via Wikidata (`gndid-generator.py`, last change
  `e1add33`, 2017-03-23).
- 2017-12-11: clean-up and GND steps (`person_generator_DBPedia_modify.py`, `_modify_gnd.py`, loader `05c5248`).
- 2018-04-03: enrichment from a local Fuseki with the GND (`generated_persons_DBPedia_enrich.py`, loader `8668321`).
- 2018-07-24 moved to judaicalink-generators; 2018-10-24 EntityFacts links (`Entityfacts-01.py`, `abe8e67`).
- 2025-06 path fixes, 2025-11 moved to `legacy/dbpedia-persons/`.
- The very first version (2017-03-23, `generated_person.ttl`) is byte-identical to loader `a146288`
  `generators/generated-person/generated_person.rdf`; it is not kept.

## Kept version 2018-10-24

- `generated_persons_DBPedia_enriched_02.ttl.gz`: **exact**, identical to the output in loader `8668321`.
- `persons-gndid.ttl.gz`: **exact**, identical to `generated_gndid.rdf` in loader `40cd64b` (2017-03-23); script
  `gndid-generator.py` at `e1add33`.
- `Entityfacts-dbpedia-sameas.ttl.gz`: **probable**, a modified, uncommitted copy of `Entityfacts-01.py`
  (`abe8e67`; the committed state names no dbpedia graph).

## Inputs

- On file: the whole intermediate chain in the loader repository and the occupation ontology.
- External: DBpedia and Wikidata SPARQL of 2017, the GND in a local Fuseki, EntityFacts.

## Reproduction

**Not reproducible**: the live services have changed, the local GND is not on file; local paths and Python 2.
The enrichment script overwrites its own input when run repeatedly.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`generators/Datasets/Persons_DBPedia/scripts/person_generator_DBPedia.py`](https://github.com/judaicalink/judaicalink-loader/blob/8668321129189c664e6e44ee0b745d99a000643a/generators/Datasets/Persons_DBPedia/scripts/person_generator_DBPedia.py) | judaicalink-loader | `8668321` (2018-04-03, Maral Dadvar) | file last changed in `54bae32` (2017-04-21) |
| [`generators/Datasets/Persons_DBPedia/scripts/person_generator_DBPedia_modify.py`](https://github.com/judaicalink/judaicalink-loader/blob/8668321129189c664e6e44ee0b745d99a000643a/generators/Datasets/Persons_DBPedia/scripts/person_generator_DBPedia_modify.py) | judaicalink-loader | `8668321` (2018-04-03, Maral Dadvar) | file last changed in `05c5248` (2017-12-11) |
| [`generators/Datasets/Persons_DBPedia/scripts/person_generator_DBPedia_modify_gnd.py`](https://github.com/judaicalink/judaicalink-loader/blob/8668321129189c664e6e44ee0b745d99a000643a/generators/Datasets/Persons_DBPedia/scripts/person_generator_DBPedia_modify_gnd.py) | judaicalink-loader | `8668321` (2018-04-03, Maral Dadvar) | file last changed in `05c5248` (2017-12-11) |
| [`generators/Datasets/Persons_DBPedia/scripts/generated_persons_DBPedia_enrich.py`](https://github.com/judaicalink/judaicalink-loader/blob/8668321129189c664e6e44ee0b745d99a000643a/generators/Datasets/Persons_DBPedia/scripts/generated_persons_DBPedia_enrich.py) | judaicalink-loader | `8668321` (2018-04-03, Maral Dadvar) |  |
| [`generators/Datasets/Persons_DBPedia/scripts/gndid_generator.py`](https://github.com/judaicalink/judaicalink-loader/blob/8668321129189c664e6e44ee0b745d99a000643a/generators/Datasets/Persons_DBPedia/scripts/gndid_generator.py) | judaicalink-loader | `8668321` (2018-04-03, Maral Dadvar) | file last changed in `e88a64e` (2017-04-21) |
| [`generators/gndid-generator.py`](https://github.com/judaicalink/judaicalink-loader/blob/e1add334e0e47767a4e61bd98fa67429f7f00ae7/generators/gndid-generator.py) | judaicalink-loader | `e1add33` (2017-03-23, Maral Dadvar) |  |
| [`dbpedia-persons/scripts/Entityfacts-01.py`](https://github.com/judaicalink/judaicalink-generators/blob/abe8e67e1114cb00b8ada5b964fbdf828014f2e2/dbpedia-persons/scripts/Entityfacts-01.py) | judaicalink-generators | `abe8e67` (2018-10-24, Maral Dadvar) |  |

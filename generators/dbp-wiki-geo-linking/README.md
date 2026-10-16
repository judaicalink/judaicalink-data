# dbp-wiki-geo-linking: generator history

Links from JudaicaLink places to DBpedia and Wikipedia, via GeoNames, by Marco Rovera.

## History

- 2021-01-13: notebook `dbp-wiki-geo-linking.ipynb` (judaicalink-generators `de8480d`). Marco Rovera's working
  folder (labs VM `/data/cm/scripts/jl/scripts/dbp_wiki_geo_links/`, copied into the workflow repository) has the
  same code, its output and its inputs.
- 2025-06-05 ported to a Python script (not used to regenerate); 2025-11 moved to `legacy/dbp-wiki-geo-linking/`.
- A later variant via GeoNames `about.rdf` (`geo_interlinks_wiki_generator.ipynb`, output `geo_wiki_dbpedia.ttl`)
  exists in the working folder; it was never catalogued.

## Kept version 2021-01-13

**Probable** `de8480d`: the working copy of the notebook has identical code cells, and its output is identical to the
kept file. Every subject of the dump is in the set to be enriched computed from the inputs on file.

## Inputs

- On file (identical hashes): geo-coordinates 2018-08-08 (`city-geocoor-05.ttl`) and the seven files of
  geo-enriched 2019-12-18.
- External: the GeoNames mirror `http://www.lotico.com:3030/lotico/sparql`, which now answers 401.

## Reproduction

2021: **not reproducible**: the endpoint is closed and its 2021 state unknown. Note: the GeoNames IRIs from geo-enriched
end with a slash and never match in this notebook, so that route contributed nothing. Since 2026-10-15:
**reproducible** from the cached Wikidata answers (framework generator, below).

## Framework generator (2026-10-15)

`generate.py` makes the dataset again (decision 0024), offline and deterministically, from the answers of the
Wikidata Query Service (`inputs:web-caches/wikidata-geonames-2026-10-15`, fetched by `fetch_wikidata.py`): the items
with the GND numbers (P227) and the GeoNames ids (P1566) of the 2,701 places of `geo-coordinates` 2026-10-12, and
their English, German and Russian Wikipedia articles. The GND route decides (the places are GND records): a place gets
its only item by GND (2,451 places; GeoNames gives the same item for 1,065 of them, another for 929, none for 457),
with several items by GND the one GeoNames also gives (10), without an item by GND its only item by GeoNames (145).
GeoNames ids in Wikidata often sit on a second item for the settlement beside the item of the town or municipality
(Ansbach: Q117751859 "main settlement of Ansbach" beside Q14859), hence the 929. Left out: 85 without an item, 10 with
several items (named in the log).

For each of the 2,606 linked places: `owl:sameAs` the Wikidata item and the DBpedia resource of its English article
(2,449), `foaf:isPrimaryTopicOf` the articles themselves (en 2,449, de 2,561, ru 2,364; documents about the place, so
not `owl:sameAs` as in 2021, and as cm-entities states them). 35 items are the item of two or more places, all the
same place under two names (Bromberg and Bydgoszcz, Czernowitz in four spellings), which the entity pages join.
Output `dbp-wiki-geo-linking.ttl.gz`, 12,429 triples. Subjects are the new IRIs of geo-coordinates only: the places
that geo-enriched links by their GeoNames IRI are not records, and Wikidata states their items itself (P1566).

Against 2021 (7,023 triples, 2,835 subjects: 2,150 old geo-coordinates IRIs, 685 `data/geonames/<id>`): of the 2,150
places with a DBpedia link, 2,032 have the same, 92 another (2021 errors such as `Altenkirchen_(disambiguation)`,
`Battenberg_family`, `Blaubeuren_Abbey`, `Bolesławice,_Bolesławiec_County`, `Old_Delhi`, and renamed articles), 26
none now.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`dbp-wiki-geo-linking/dbp-wiki-geo-linking.ipynb`](https://github.com/judaicalink/judaicalink-generators/blob/de8480d8da80d423d9dbbb25d14318af70706da7/dbp-wiki-geo-linking/dbp-wiki-geo-linking.ipynb) | judaicalink-generators | `de8480d` (2021-01-13, marcorovera) |  |
| [`dbp-wiki-geo-linking/readme.md`](https://github.com/judaicalink/judaicalink-generators/blob/de8480d8da80d423d9dbbb25d14318af70706da7/dbp-wiki-geo-linking/readme.md) | judaicalink-generators | `de8480d` (2021-01-13, marcorovera) |  |

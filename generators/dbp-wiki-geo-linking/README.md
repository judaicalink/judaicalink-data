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

**Not reproducible**: the endpoint is closed and its 2021 state unknown. Note: the GeoNames IRIs from geo-enriched
end with a slash and never match in this notebook, so that route contributed nothing.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`dbp-wiki-geo-linking/dbp-wiki-geo-linking.ipynb`](https://github.com/judaicalink/judaicalink-generators/blob/de8480d8da80d423d9dbbb25d14318af70706da7/dbp-wiki-geo-linking/dbp-wiki-geo-linking.ipynb) | judaicalink-generators | `de8480d` (2021-01-13, marcorovera) |  |
| [`dbp-wiki-geo-linking/readme.md`](https://github.com/judaicalink/judaicalink-generators/blob/de8480d8da80d423d9dbbb25d14318af70706da7/dbp-wiki-geo-linking/readme.md) | judaicalink-generators | `de8480d` (2021-01-13, marcorovera) |  |

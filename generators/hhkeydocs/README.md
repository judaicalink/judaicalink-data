# hhkeydocs: generator history

Hamburger Schlüsseldokumente zur deutsch-jüdischen Geschichte: persons, places, organisations, by Christian
Deuschle; generator rewritten by Benjamin Schnabel.

## History

- 2023-11 … 2024-05: `HHKeyDocs/generator.py` by Christian Deuschle (renamed `hhkeydocs/` 2024-03-07); its output of
  2024-01-23 (`ea1a4ca`) is the state in the dumps repository of 2025-01 (not kept).
- 2025-03-21: rewrite by Benjamin Schnabel (`033bd4a`, "Generator updated": Google Translate removed, Wikidata
  professions added).
- 2025-11: `hhkeydocs/scripts/generator.py` (same code) plus `build.py`.

## Kept version 2025-03-21

**Probable** `033bd4a`: the run started 7 minutes after the commit; the malformed VIAF URIs
(`https://viaf.org/viaf/http://viaf.org/viaf/…`) match this code. 1,824 resources.

## Inputs

- 2025-03-21: live only (schluesseldokumente.net, lobid GND, Wikidata SPARQL); not on file.
- Framework generator: `inputs:hhkeydocs/jsonld-2026-10-15`, made by `harvest.py` (see below).

## Reproduction

2025-03-21: **partly** (the sources are online, but the output drifts with them; the 2025-11 output differs by about
700 lines). From 2026-10-15 on: **reproducible** from the harvest in the inputs area.

## Framework generator (2026-10-15)

`harvest.py` fetches what the site lists: the two BEACON files (persons and organisations by GND number), the sitemaps
of persons, organisations and places and the place list `/ort`, and the JSON-LD (`<address>.jsonld`, schema.org) of
every person, organisation and place, one request per second (about 45 minutes). `--bundle` writes the input: the
index files unchanged and `jsonld.jsonl.gz` (per address the HTTP status and the page text unchanged).

`generate.py` makes the dataset from that input, true to the source (decision 0026), not from 2025-03-21 (decision
0024: the systematic errors are in the IRIs and the lookups):

- **IRIs from the site's addresses:** `data/hhkeydocs/person/gnd/<GND>`, `data/hhkeydocs/person/<number>` (persons
  without a GND number, mostly the authors of the site's articles), `data/hhkeydocs/organisation/gnd/<GND>`,
  `data/hhkeydocs/ort/tgn/<TGN>`. Every place named in a record (birth and death places and the places they are
  contained in) is a place record, with the data of its own page where it has one.
- **The name IRIs of 2025-03-21** are stated `dcterms:isReplacedBy` the records their `jl:describedAt` addresses name
  (decision 0022). Ten of them held two records each (two persons of the same name: David Frankel, Kurt Singer, Otto
  Warburg, …; two places: Cambridge, Kleve, …); their entity pages split.
- **Per record**, as the JSON-LD gives it: name, page of the site, `owl:sameAs` the GND and TGN IRIs the site states
  and `gndo:gndIdentifier` the GND number; persons with given and family name, gender, dates, birth and death place
  as name (`jl:birthLocation`) and record (`jl:birthLocationURI`), description; organisations with dates of
  establishment and termination, homepage, description; places with coordinates and the place they are contained in
  (an IRI; 2025-03-21 gave a name).
- **Not taken over:** the VIAF links of 2025-03-21 (looked up in lobid, not in the source; all 1,049 malformed,
  `viaf.org/viaf/http://viaf.org/viaf/…`), `dcterms:created` (the time of that run). The legacy generator read the
  BEACON numbers with `int()` and so left out every GND number with a hyphen or a check digit X: most organisations
  and about 90 persons.
- **Not included:** the site's 189 source documents (their texts are for personal use only), 151 articles and 820
  bibliography entries; they could be added as records later.

Run of 2026-10-16 (input of 2026-10-15): 32,088 triples, deterministic. 1,191 persons (1,152 by GND number, 39 by
the site's number; 2025-03-21: 1,049), 751 organisations (67), 1,111 places (708; 717 with a page of their own, the
others named in records: regions, countries, continents). 1,903 GND numbers (1,119; none lost, 770 of the 784 new
ones with a hyphen or X). Birth places 868, death places 776, all linked to a place record; every place has a TGN
number. Of the 1,824 records of 2025-03-21, 1,814 are replaced by one record and 10 by two; 13 place IRIs of
2025-03-21 that were only named as birth or death places, never described, get no replacement. About 0.3 seconds.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`hhkeydocs/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/033bd4a63656c847756c8f6e39035a288c411a91/hhkeydocs/generator.py) | judaicalink-generators | `033bd4a` (2025-03-21, bsesic) |  |

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

Live only: schluesseldokumente.net (still online), lobid GND, Wikidata SPARQL.

## Reproduction

**Partly**: the sources are online, but the output drifts with them (the 2025-11 output differs by about 700 lines).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`hhkeydocs/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/033bd4a63656c847756c8f6e39035a288c411a91/hhkeydocs/generator.py) | judaicalink-generators | `033bd4a` (2025-03-21, bsesic) |  |

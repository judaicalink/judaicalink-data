# haskala: generator history

The Library of Haskala (persons from the haskala-library.net database of UB Frankfurt), by Maral Dadvar; regenerated
by Benjamin Schnabel.

## History

- 2019-07-01 (Maral Dadvar, `8f1538a`): `CSV-to-RDF-Haskala.py` (scrapes the person pages), `CSV-to-RDF-Haskalanet.py`,
  `GND-enrich-02.py` (export from a local Fuseki); the README documents manual SPARQL INSERTs against the local GND
  between the steps. A copy with outputs is in `fid-judaica/haskala/` (`965a481`, 2021-06-28).
- 2025-03-24 (Benjamin Schnabel): `f9b8215` (relative paths, endpoint changed to the published SPARQL endpoint),
  `7124d29` (outputs), later the same day `ba26673` (occupation split, `Haskala_net` deleted).
- 2025-11 moved to `legacy/haskala/`.

## Kept versions

- **2019-07-01** (stable): output **exact** (identical to `fid-judaica/haskala/Haskala_enriched.ttl` in `965a481` and to
  the original upload); scripts **probable** `8f1538a` (committed after the upload). It contains all triples of
  `Haskala.ttl`, 288 of the 320 of `Haskala_net`, and 1,871 enrichment triples.
- **2025-03-24**: **exact** (`7124d29` outputs, `f9b8215` scripts). `Haskala.ttl` has exactly the triples of the
  un-enriched `Haskala.ttl` of 2019, so this version is the 2019 state before enrichment, not new data.

## Inputs

On file: the source CSVs (`legacy/haskala/sources/`, `legacy/fid-judaica/haskala/sources/`). External: the
haskala-library.net website, the GND of 2019 in a local Fuseki.

## Reproduction

2019: **not reproducible** (manual updates, local GND), but the output is on file. 2025: `Haskala_net` is
**reproducible** offline, `Haskala.ttl` needs the live website.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`haskala/scripts/CSV-to-RDF-Haskala.py`](https://github.com/judaicalink/judaicalink-generators/blob/8f1538a1f255e49fa329ef8eb9d35c62f7bb37e3/haskala/scripts/CSV-to-RDF-Haskala.py) | judaicalink-generators | `8f1538a` (2019-07-01, Maral Dadvar) |  |
| [`haskala/scripts/CSV-to-RDF-Haskalanet.py`](https://github.com/judaicalink/judaicalink-generators/blob/8f1538a1f255e49fa329ef8eb9d35c62f7bb37e3/haskala/scripts/CSV-to-RDF-Haskalanet.py) | judaicalink-generators | `8f1538a` (2019-07-01, Maral Dadvar) |  |
| [`haskala/scripts/GND-enrich-02.py`](https://github.com/judaicalink/judaicalink-generators/blob/8f1538a1f255e49fa329ef8eb9d35c62f7bb37e3/haskala/scripts/GND-enrich-02.py) | judaicalink-generators | `8f1538a` (2019-07-01, Maral Dadvar) |  |
| [`haskala/scripts/CSV-to-RDF-Haskala.py`](https://github.com/judaicalink/judaicalink-generators/blob/f9b8215519166a50438e3269b3e016a773b5367b/haskala/scripts/CSV-to-RDF-Haskala.py) | judaicalink-generators | `f9b8215` (2025-03-24, bsesic) |  |
| [`haskala/scripts/CSV-to-RDF-Haskalanet.py`](https://github.com/judaicalink/judaicalink-generators/blob/f9b8215519166a50438e3269b3e016a773b5367b/haskala/scripts/CSV-to-RDF-Haskalanet.py) | judaicalink-generators | `f9b8215` (2025-03-24, bsesic) |  |
| [`haskala/scripts/GND-enrich-02.py`](https://github.com/judaicalink/judaicalink-generators/blob/f9b8215519166a50438e3269b3e016a773b5367b/haskala/scripts/GND-enrich-02.py) | judaicalink-generators | `f9b8215` (2025-03-24, bsesic) |  |

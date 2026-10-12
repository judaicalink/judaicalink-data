# gnd-persons-entityfacts: generator

GND records for the persons of hhkeydocs, nrwbibdjg and gba that gnd-persons lacks (new dataset, decision 0020).

## History

- 2026-10-06 (Kai Eckert): `gnd_persons_entityfacts` in kg-complements (`datasets_algorithmic.py`); DNB EntityFacts was
  queried by GND number and the answers cached; output in `dumps-additions/`, never published.

## Framework generator

`generate.py` (2026-10-12): a port without changes to its logic. Inputs: `gnd-persons/2018-11-29` (the GND numbers it
has), `hhkeydocs/2025-03-21`, `nrwbibdjg/2024-05-24`, `gba/2025-03-21` (the GND numbers of their persons) and the API
cache `inputs:web-caches/api-cache-2026-10-06` (a missing answer is an error, not a live request). With
`--param fix_self_links=false` it gives exactly the 20,003 triples of the kg-complements output (1,269 GND numbers,
960 persons, 309 without an EntityFacts person record).

The fix (default, open issue of 2026-10-10): EntityFacts gives JudaicaLink IRIs in the `https` form (taken from our
BEACON); they are normalised to `http`. 950 of them were links of a record to itself and are dropped, 3 link two GND
records that EntityFacts gives as the same person (e.g. `gnd/1055404759` and `gnd/138712468`): 19,053 triples.

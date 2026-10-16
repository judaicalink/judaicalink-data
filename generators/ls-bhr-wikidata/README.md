# ls-bhr-wikidata: generator

The persons of the Biographisches Handbuch der Rabbiner (bhr) linked to their Wikidata items.

## History

- 2026-10-15 (Kai Eckert): new, like ls-yivo-wikidata (decision 0025).

## Inputs

- `bhr/2026-10-12`: the records and their BHR ids, from their links to the BHR pages (`owl:sameAs` the page of the
  BHR database of 2018; from the next bhr version on, `jl:describedAt` the page of the Biographisches Portal der
  Rabbiner; both are read).
- `inputs:web-caches/wikidata-bhr-2026-10-15/p10405.tsv`: every Wikidata item with a Biographisches Portal der
  Rabbiner ID (P10405) and its GND numbers, from the Wikidata Query Service on 2026-10-15 (the query is `p10405.rq`
  next to it). The values are the BHR ids without leading zeros (formatter `bhr?id=$1`), the same ids as ours.

## Framework generator

`generate.py`: a record gets `owl:sameAs` an item when its ids lead to exactly one item and that item's ids to no
other record. Of 2,532 records with a BHR id, 976 are linked (1,049 items with P10405, 1,045 ids). Left out, named
in the log:

- two pairs of bhr records sharing a BHR id (Auerbach Hirsch / Auerbach Benjamin-Hirsch, id 71; Pollak Markus /
  Pollak Markus-1, id 1413), probably duplicates of the 2018 integration;
- three ids with two Wikidata items each (2245, 2401, 2443: duplicates in Wikidata);
- 64 ids name no bhr record (entries of the portal not in the 2018 data, mostly ids above 2,450).

For 21 linked records the GND number of the item differs from ours; all were checked in lobid on 2026-10-15: our
number redirects to the item's (merged GND records, 9), our number does not answer in lobid (8, probably merged or
deleted), or both are current records with the same name and birth year (GND duplicates, 4: Bondi 1830, Eller 1801,
Fuld 1790, Zivi 1865). No conflation was found. Under 0.5 seconds.

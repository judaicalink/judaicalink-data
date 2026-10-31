# 0039 Occupations: the GND's headings, described in one dataset

Status: accepted · Date: 2026-10-31

## Context

The datasets of 2018 made occupation IRIs from names (`data/occupation/Rabbiner` from the GND's German names,
`data/occupation/musician` from English DBpedia categories). records-normalized, bhr, sosy and dbpedia still state 484
of them, and the entity pages carry them on; nothing describes them, so they have no label and do not resolve.
Benjamin Schnabel's `occupations` of 2025 (no dump found) would have made other IRIs again, lowercase, from the
literals. Meanwhile `gnd` left out the GND's occupations: the GND lists them in an `rdf:Seq`, a blank node, and the
generator skipped blank nodes. The GND has 50,944 of our records with an occupation, in one vocabulary with a
hierarchy, against 16,729 entity pages with an older occupation IRI.

## Decision

- **The GND's subject headings are the occupations.** `gnd` states the occupations of its records as
  `jl:occupationURI` with the heading's IRI (`https://d-nb.info/gnd/<n>`), beside the GND's own
  `gndo:professionOrOccupation`; it states no names of them.
- **All statements about occupations are in the dataset `occupations`** (kind `vocabulary`): the headings used as
  occupations and their broader headings (`skos:Concept`, names, `skos:broader`, subject categories), and the older
  IRIs with their names and `skos:exactMatch` to their heading. Links to other vocabularies, normalisations (e.g. female
  forms, English names) and other improvements for the views and showcases go there too, not into the datasets that
  use the occupations.
- **No IRIs of our own for the headings.** The dataset describes the GND's IRIs; so no entity pages are made for
  occupations (entity pages are made only for records in our namespaces). The older IRIs stay as they are and are only
  described.
- **English names by hand:** matched by name, English names find false friends in the GND (its "Artist" is a circus or
  variety artiste, its "Rabbi" the sages of the Talmudic period); the generator has a table chosen by hand.

## Consequences

- The entity pages get the GND occupations from `gnd` with the next version of `ep`; the views show their names from
  `occupations`.
- `records-normalized` keeps matching literals to the older IRIs; whether it should match them to the GND headings
  instead is open.

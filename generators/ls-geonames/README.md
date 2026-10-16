# ls-geonames: generator

Every record of ours that refers to a GeoNames entry, linked (`owl:sameAs`) to our record of the current entry,
`data/geonames/<id>` in the dataset `geonames` (decision 0029: one linkset per authority dataset).

## History

- 2026-10-16 (Kai Eckert): new linkset.

## Inputs

- `geonames/2026-10-16`: the current entries and the replacements and deprecations of identifiers.
- The stable versions of our datasets (`stable_inputs`, all but geonames itself, ep and the datasets without links to
  records): the references, GeoNames ids (sws.geonames.org/<id> in any form, our records data/geonames/<id>).

## Rule (`jl.linksets`)

Only identity statements count (`owl:sameAs`, `skos:exactMatch`, `madsrdf:hasExactExternalAuthority`, identifier
literals), not a place of birth or an occupation that is an authority entry. A reference is resolved to the current entry through the replacements of the identifiers; references to deprecated
identifiers or to identifiers not in `geonames`, and references by blank nodes or by records of the authority itself,
are left out and listed in the run log. A record that refers to several current entries is linked to each (the entity
pages join them, as before) and listed in the run log for review. The source's identifier statements are taken as
given (decision 0029); the character of the source is described in the entry of `geonames`.

## Reproduction

**Reproducible** from the inputs; a new version of any input gives a new version.

# ls-geonames: generator

Every record of ours that refers to a GeoNames feature, linked (`jl:sameAs`) to our record of the current entry,
`data/geonames/<id>` in the dataset `geonames` (decision 0029: one linkset per authority dataset).

## History

- 2026-10-16 (Kai Eckert): new linkset (run only).
- 2026-10-19 (Kai Eckert): first version: declared identity, link quality, classes; the other authority datasets
  as inputs.

## Inputs

- `geonames/2026-10-19` (`authority`): the current entries and the replacements and deprecations of identifiers.
- Our datasets and the other authority datasets (`jl.authorities.linking_inputs`: the stable versions, or the runs
  given with `--use`; all but geonames itself, the linksets made from authority datasets, ep and the datasets without
  links to records): the references, GeoNames ids (sws.geonames.org/<id> in any form, our records data/geonames/<id>).

## Rules (`jl.linksets`)

- Only identity statements count, as the catalogue entry of each dataset declares them (field `identity`, decision
  0032): a place of birth or an occupation that is an authority entry does not make the record that entry.
- Link quality (0032): a unit (dataset, property, target source) measured below the threshold in
  `catalog/link-quality.toml` (accuracy at least 0.95 and, when only a sample was checked, the lower bound of its 95%
  interval at least 0.90) is left out; the statement stays in its dataset.
- A reference is resolved to the current entry through the replacements of geonames. References to deprecated
  identifiers or to identifiers not in geonames, and references by blank nodes or by records of the authority itself,
  are left out and listed in the log.
- Classes: a link whose two sides are of contradicting kinds (a person and a work, a person or a work and a place) is
  left out; an organisation can be a place or a person's firm.
- A record that refers to several current entries is linked to each (the entity pages join them) and listed in the
  log for review; so is every target that three or more records of one dataset refer to (hubs).

Each link: `<record> jl:sameAs <data/geonames/<id>>`. The source's identifier statements are taken as given (decision 0029);
the character of the source is described in the entry of `geonames`.

## Version 2026-10-19

15,362 links of 14,944 records to 8,688 geonames records (393 records with several); by dataset: wikidata 8,372,
gnd 4,359, geo-coordinates 2,630, lc 1. Left out: 2014links below the threshold 109, not in geonames 40. Hubs: 15.
About three minutes.

## Reproduction

**Reproducible** from the inputs; a new version of any input gives a new version. Made together with the authority
datasets (`docs/process.md`, 2a).

# ls-gnd: generator

Every record of ours that refers to a GND entry, linked (`jl:sameAs`) to our record of the current entry,
`data/gnd/<n>` in the dataset `gnd` (decision 0029: one linkset per authority dataset).

## History

- 2026-10-16 (Kai Eckert): new linkset (run only).
- 2026-10-19 (Kai Eckert): first version: declared identity, link quality, classes; the other authority datasets
  as inputs.

## Inputs

- `gnd/2026-10-19` (`authority`): the current entries and the replacements and deprecations of identifiers.
- Our datasets and the other authority datasets (`jl.authorities.linking_inputs`: the stable versions, or the runs
  given with `--use`; all but gnd itself, the linksets made from authority datasets, ep and the datasets without
  links to records): the references, GND numbers (any IRI form of d-nb.info/gnd, our records data/gnd/<n>, gndo:gndIdentifier).

## Rules (`jl.linksets`)

- Only identity statements count, as the catalogue entry of each dataset declares them (field `identity`, decision
  0032): a place of birth or an occupation that is an authority entry does not make the record that entry.
- Link quality (0032): a unit (dataset, property, target source) measured below the threshold in
  `catalog/link-quality.toml` (accuracy at least 0.95 and, when only a sample was checked, the lower bound of its 95%
  interval at least 0.90) is left out; the statement stays in its dataset.
- A reference is resolved to the current entry through the replacements of gnd. References to deprecated
  identifiers or to identifiers not in gnd, and references by blank nodes or by records of the authority itself,
  are left out and listed in the log.
- Classes: a link whose two sides are of contradicting kinds (a person and a work, a person or a work and a place) is
  left out; an organisation can be a place or a person's firm.
- A record that refers to several current entries is linked to each (the entity pages join them) and listed in the
  log for review; so is every target that three or more records of one dataset refer to (hubs).

Each link: `<record> jl:sameAs <data/gnd/<n>>`. The source's identifier statements are taken as given (decision 0029);
the character of the source is described in the entry of `gnd`.

## Version 2026-10-19

138,571 links of 138,209 records to 68,583 gnd records (310 records with several); by dataset: viaf 66,183,
wikidata 61,418, ubffm-persons 9,402, geo-coordinates 5,218, hhkeydocs 4,169, bhr 790, interlinks 592, nrwbibdjg 579,
lc 201, haskala 189, epidat 76, gba 20. 4,845 references resolved through a replacement. Left out: footprints below
the threshold 951, not in gnd 2,518, deprecated 12, the subject an authority record 146. Hubs: 19. About two
minutes.

## Reproduction

**Reproducible** from the inputs; a new version of any input gives a new version. Made together with the authority
datasets (`docs/process.md`, 2a).

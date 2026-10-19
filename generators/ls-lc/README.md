# ls-lc: generator

Every record of ours that refers to an LC Name Authority File entry, linked (`jl:sameAs`) to our record of the current entry,
`data/lc/<id>` in the dataset `lc` (decision 0029: one linkset per authority dataset).

## History

- 2026-10-16 (Kai Eckert): new linkset (run only).
- 2026-10-19 (Kai Eckert): first version: declared identity, link quality, classes; the other authority datasets
  as inputs.

## Inputs

- `lc/2026-10-19` (`authority`): the current entries and the replacements and deprecations of identifiers.
- Our datasets and the other authority datasets (`jl.authorities.linking_inputs`: the stable versions, or the runs
  given with `--use`; all but lc itself, the linksets made from authority datasets, ep and the datasets without
  links to records): the references, LC identifiers (id.loc.gov/authorities/names/<id> and the Real World Object id.loc.gov/rwo/agents/<id>, our
  records data/lc/<id>).

## Rules (`jl.linksets`)

- Only identity statements count, as the catalogue entry of each dataset declares them (field `identity`, decision
  0032): a place of birth or an occupation that is an authority entry does not make the record that entry.
- Link quality (0032): a unit (dataset, property, target source) measured below the threshold in
  `catalog/link-quality.toml` (accuracy at least 0.95 and, when only a sample was checked, the lower bound of its 95%
  interval at least 0.90) is left out; the statement stays in its dataset.
- A reference is resolved to the current entry through the replacements of lc. References to deprecated
  identifiers or to identifiers not in lc, and references by blank nodes or by records of the authority itself,
  are left out and listed in the log.
- Classes: a link whose two sides are of contradicting kinds (a person and a work, a person or a work and a place) is
  left out; an organisation can be a place or a person's firm.
- A record that refers to several current entries is linked to each (the entity pages join them) and listed in the
  log for review; so is every target that three or more records of one dataset refer to (hubs).

Each link: `<record> jl:sameAs <data/lc/<id>>`. The source's identifier statements are taken as given (decision 0029);
the character of the source is described in the entry of `lc`.

## Version 2026-10-19

313,533 links of 312,937 records to 91,935 lc records (494 records with several); by dataset: viaf 89,052,
wikidata 60,662, gnd 56,185, nli-records 53,833, ls-nli-legacy 53,801. Left out: classes contradict 28 (e.g. Wikidata
gives a person the LC number of a book), deprecated 333, not in lc 552, footprints below the threshold 1.
Hubs: 63. About three minutes.

## Reproduction

**Reproducible** from the inputs; a new version of any input gives a new version. Made together with the authority
datasets (`docs/process.md`, 2a).

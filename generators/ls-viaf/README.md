# ls-viaf: generator

Every record of ours that refers to a VIAF cluster, linked (`jl:sameAs`) to our record of the cluster, `data/viaf/<n>`
in the dataset `viaf` (decision 0029: one linkset per authority dataset).

## History

- 2026-10-19 (Kai Eckert): new linkset.

## Inputs

- `viaf/2026-10-19` (`authority`): the clusters of the dump.
- Our datasets and the other authority datasets (`jl.authorities.linking_inputs`: the stable versions, or the runs
  given with `--use`; all but viaf itself, the linksets made from authority datasets, ep and the datasets without
  links to records): the references, VIAF numbers (viaf.org/viaf/<n> in any form, our records data/viaf/<n>), and the
  life dates and classes of the records.

## Rules (`jl.linksets`, `generate.py`)

- Only identity statements count, as the catalogue entry of each dataset declares them (field `identity`, decision
  0032). haskala declares no VIAF identity: its VIAF links are matches by name (37% correct in the sample).
- Link quality (0032): a unit (dataset, property, target source) measured below the threshold in
  `catalog/link-quality.toml` (accuracy at least 0.95 and, when only a sample was checked, the lower bound of its 95%
  interval at least 0.90) is left out; the statement stays in its dataset.
- The dump states no successors of merged clusters, so a number not in viaf is left out; so are references by blank
  nodes or by records of the authority itself. All are listed in the log.
- VIAF gets the benefit of the doubt (0029); a link is left out when the life dates contradict: the record and the
  cluster both give a year of birth (or of death), and no two of these years are within one year of each other. A
  difference of one year is kept and counted (calendars and conversions often differ by a year). The years are the
  first three- or four-digit numbers of `jl:birthDate`/`jl:deathDate` and `jl:birthDateNormalized`/
  `jl:deathDateNormalized` (records-normalized), of the record and of the cluster.
- Classes: a link whose two sides are of contradicting kinds (a person and a work, a person or a work and a place) is
  left out: cm-entities takes every VIAF number of a Wikidata item, which can include the cluster of a work.
- A record that refers to several clusters is linked to each (the entity pages join them) and listed in the log for
  review; so is every cluster that three or more records of one dataset refer to (hubs).

Each link: `<record> jl:sameAs <data/viaf/<n>>`. The character of VIAF (clusters formed by an algorithm from the
records of many libraries) is described in the entry of `viaf`.

## Version 2026-10-19

485,579 links of 482,142 records to 212,045 clusters (2,557 records with several); by dataset: nli-records 167,341,
ls-nli-legacy 163,816, wikidata 84,729, gnd 65,827, ubffm-persons 3,520, jre 280, interlinks 117, lc 2. Left out:
birth years contradict 3,260, death years 1,015, classes 37, footprints below the threshold 1,478, geo-coordinates
below the threshold 2,701, not in viaf 31,762. Kept with years one apart: birth 2,104, death 887. Hubs: 81. About
five minutes.

## Reproduction

**Reproducible** from the inputs; a new version of any input gives a new version. Made together with the authority
datasets (`docs/process.md`, 2a).

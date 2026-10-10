# Generators

One folder per dataset of the catalogue (`generators/<slug>/`), the place where it is documented and later
generated how a dataset version came about.

## Contents of a folder

- `README.md`: the history of the generator (who wrote what, when, in which repository), which code made each
  kept version and with what evidence, the inputs and whether we still have them, whether the version can be
  reproduced, and the list of original files with links pinned to their commits.
- `original/`: copies of the files that made the kept versions, under `<repository>@<commit>/<path>`, unchanged
  unless the README notes otherwise (one access token was redacted). They are the record of what was used, from
  judaicalink-generators, judaicalink-loader, judaicalink-labs, judaicalink-ontology, workflow and
  kaiec/judaicalink-crawler, and the Silk link specifications of 2014links from the labs VM. They are not run from
  here.
- Later: the migrated generator (one or more Python scripts in the common framework), with a header stating that it
  is a faithful migration of the named originals, not the code that was run, and how far it reproduces the kept
  version.

`originals.json` lists every original file with repository, commit, path, date and author (machine-readable source
of the tables in the READMEs).

## Evidence and reproduction

Evidence that a given code made a kept version: **exact** (a recorded commit was confirmed, a committed output is
identical, or re-running the code gives the same file or graph), **probable** (nearest commit by date and output
shape), **unknown**. The research behind this (2026-10-09/10) compared the kept dumps with every file in the
history of the repositories and re-ran the original code where its inputs are on file.

| Dataset | Evidence | Reproducible from files on hand |
|---|---|---|
| 2014links | raw Silk output (specs for 8 of 12 files) | no |
| bhr | final step exact, EntityFacts probable | final step only |
| cm-tagme | exact | from intermediates (private backup) |
| compact-memory | exact | from intermediates (private backup) |
| compact-memory-supp | same content as the workflow copy | probably |
| date-enriched | exact (by content) | yes |
| dbp-wiki-geo-linking | probable | no |
| dbpedia-persons | 2 files exact, 1 probable | no |
| djh | 2016 step probable, 2018 step unknown | partly |
| ep | 2 files exact, 4 probable | 2 files from intermediates |
| epidat | probable, plus an unknown hand repair | no |
| footprints | 2024 exact, 2025 probable | no |
| gba | probable, confirmed by content | yes |
| geo-coordinates | probable | no |
| geo-enriched | unknown (original not found) | no |
| gnd-persons | 4 of 8 files exact | no |
| haskala | 2019 output exact, 2025 exact | 2025 `Haskala_net` only |
| hhkeydocs | probable | partly (live source) |
| hirsch-family | exact (re-run) | yes |
| interlinks | n3 reconstructed, -09 not exact | n3 only |
| jre | unknown (no generator found) | no |
| nli-persons | exact (re-run) | yes |
| nrwbibdjg | exact | no (source down) |
| occupations | no version | – |
| ontology | exact | yes |
| rujen | exact | yes (from the crawl) |
| rujen-translation | exact | from the caches (private backup) |
| sosy | probable | no |
| stolpersteine | 2020 exact, 2018 probable | 2020 yes |
| ubffm-persons | unknown (no generator found) | no |
| yivo | exact | yes (from the crawl) |

"Private backup" refers to the backup of the labs VM (inputs and intermediates that are not part of the dumps).

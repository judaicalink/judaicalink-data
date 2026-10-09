# judaicalink-data

Generation, organisation and description of the JudaicaLink data: the scripts that produce datasets,
the complete catalogue of our version of the knowledge graph, and the decisions and processes behind it.

This repository is universal: it is about proper data and its documentation, not about a particular
platform. mannheim.judaicalink.org and web.judaicalink.org present (parts of) its catalogue and data;
Frankfurt (the FID portal, production) can take datasets and catalogue entries from here.

## Contents (planned structure, being set up)

| Path | What |
|---|---|
| `docs/decisions/` | decision records, one file per decision (numbered, dated) |
| `docs/process.md` | how a dataset moves from development to our catalogue, to mannheim.judaicalink.org/dumps, to Frankfurt and to the archive |
| `docs/open-issues.md` | known problems and open questions |
| `catalog/` | the complete catalogue of our data version, one entry per dataset (taken over from `judaicalink-site`; old format documented in `catalog/README.md`, new format in decisions 0013 and 0014, migration pending) |
| `catalog.py` | catalogue tooling: `python3 catalog.py check [--dumps DIR [--complete]]` checks the entries (format of 0013) and, with `--dumps`, sizes and checksums against local copies (`--complete`: the directory holds exactly the catalogued files); `collect` builds a dumps tree `<slug>/<version>/<path>` from local files by checksum (0015); `index`, `sync` (0014) to do |
| `generators/` | one folder per dataset: history of its generators, the original files that made the kept versions, later the migrated generator (`generators/README.md`) |

Data files are not stored in the repository: dumps are published on archive.judaicalink.org (long-term,
the state identical to Frankfurt) and mannheim.judaicalink.org/dumps (newer versions).

Repository: <https://github.com/judaicalink/judaicalink-data>.

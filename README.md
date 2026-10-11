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
| `docs/process.md` | how a dataset moves from development to our catalogue, to the dumps locations and to Frankfurt |
| `docs/open-issues.md` | known problems and open questions |
| `catalog/` | the complete catalogue of our data version, one entry per dataset (taken over from `judaicalink-site`; old format documented in `catalog/README.md`, new format in decisions 0013 and 0014, migrated 2026-10-09) |
| `jl`, `src/jl/` | the framework and its command line (decision 0018): `./jl --help`; read access (`list-datasets`, `show-dataset`, `list-versions`, `show-version`, `list-runs`, `show-run`, `list-agents`, all with `--json`), `generate <slug>` (runs `generators/<slug>/generate.py` into the build area; `list-runs`, `show-run`), `show-version --count` (triples per file and in the graph), `compare <a> <b>` and `show-canonical` (versions, runs or files, on the canonical form), `add-version <slug>/<run-id>` (header comments, `-meta`, run record, catalogue, store; `--dry-run`), `render-meta <slug>/<version>`, `check-catalog [--store] [--complete]`, `collect-store`; `import-files` and `render-meta --all` follow. RDF reader, Turtle writer, canonical form, the in-memory index, running generators, versions, `-meta` and the agents registry in `src/jl/` (`rdf.py`, `turtle.py`, `canonical.py`, `graph.py`, `generator.py`, `versions.py`, `meta.py`, `agents.py`); tests: `python3 -m unittest discover -s tests`. Local settings in `local.toml` (template `local.example.toml`) |
| `generators/` | one folder per dataset: history of its generators, the original files that made the kept versions, later the migrated generator (`generators/README.md`) |

Data files are not stored in the repository. They are published at dumps locations of equal standing,
archive.judaicalink.org (linked from web.judaicalink.org) and mannheim.judaicalink.org/dumps, each with the
structure `<slug>/<version>/<path>`; none of them promises completeness or permanence. The permanent record of
what existed and how it was made is the git history of this repository (decision 0019).

Repository: <https://github.com/judaicalink/judaicalink-data>.

# 0003 One universal repository: judaicalink-data

Status: accepted, amended by [0016](0016-data-access-outside.md) (`qlever/` stays outside) · Date: 2026-10-07

## Context

The work of October 2026 produced generators (`kg-complements`, `ep_generator.py`, `nli_records.py`),
the QLever setup, a dashboard and a demonstrator in loose folders. The catalogue of the archived data is
in `judaicalink-site` (state `81b42a5`) and in the Frankfurt portal; the legacy generators are in
`judaicalink-generators`.

## Decision

- `judaicalink-data` (to be created as `github.com/judaicalink/judaicalink-data`) holds the data
  generation, the organisation and description of the resulting data files, the complete catalogue, the
  decisions and the process documentation.
- It is universal: mannheim.judaicalink.org is only the platform where things are presented. Platform code
  (demonstrators, dashboard, deployment of the VM) does not belong into `judaicalink-data`.
- The catalogue is presented on mannheim.judaicalink.org and/or web.judaicalink.org by copying (parts of)
  it; web.judaicalink.org can thus show a curated selection while the repository keeps the full catalogue.

## Consequences

- `kg-complements/` and `qlever/` move into `judaicalink-data`; the provenance links in the `-meta` files
  (currently a placeholder pointing to `judaicalink-generators/…/kg-complements/`) are changed to
  `judaicalink-data` before anything is published.
- Where the platform code lives (own repository, e.g. for mannheim.judaicalink.org) is still to be decided.

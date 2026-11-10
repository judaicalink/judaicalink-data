# 0043 Generators read the stable versions of other datasets

Status: accepted · Date: 2026-11-10 · Amends [0018](0018-generator-framework.md)

## Context

Generators named their inputs by version. When a dataset got a new stable version, the generators that read it kept
reading the old one, and nothing said so. records-normalized 2026-10-12 read geo-enriched 2019 after geo-enriched
2026-10-16 had replaced its first-hit links; its own README said that records-normalized had to be made again, and
the entity pages of 2026-10-31 linked 84 persons born in Bonn to Cologne Bonn Airport (0042).

## Decision

- **Inputs of other datasets are their stable versions** (`stable_inputs`), so a generator follows the catalogue.
  The stable version, not the newest: `stable` is the version chosen on purpose.
- **A fixed version is declared:** `PINNED = {input name: reason}` in the generator; the run record names the pins.
  Not counted as outdated: the dataset's own versions and those of the datasets it replaces (a generator may make its
  dataset again from an earlier version or the original dump), files of the repository and of the inputs area.
- **Outdated** is an input that reads another dataset at a version other than its stable one, or a replaced or
  withdrawn dataset, without a pin. `jl generate` warns and names it in the run record; `jl add-version` refuses the
  run unless `--allow-old-inputs` is given, and the run record of the version then names the inputs.
- **`jl check-catalog` warns** about the outdated inputs of every generator, and about every stable version made from
  inputs that are outdated now: it must be made again. Moving `stable` is an edit of the catalogue, so this is where
  the datasets that depend on it show up.
- Datasets that read each other (gnd takes seeds from geo-enriched, geo-enriched evidence from gnd): an input whose
  stable version was made from this dataset's stable version is newer than it, not outdated.

## Consequences

- First check (2026-11-10): records-normalized, nrwbibdjg and record-classes read the stable versions now;
  ls-nli-legacy (the legacy URIs of nli-persons), ls-footprints-viaf (verdicts on footprints 2026-10-26) and
  quality-annotations (the problems of nrwbibdjg 2024-05-24) pin with reasons. Open: corrections-links (its
  corrections name triples of replaced versions) and cm-entities (reads the replaced dbpedia-persons).
- 13 stable versions were made from inputs that are outdated now, the linksets of 2026-10-26 among them (gnd and
  footprints have newer stable versions).

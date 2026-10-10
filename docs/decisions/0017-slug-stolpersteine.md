# 0017 Slugs name the dataset; stolperstein becomes stolpersteine

Status: accepted · Date: 2026-10-10

## Context

The catalogue entry of the Stolpersteine in Mainz was `stolperstein.md` (judaicalink-site since 2018), so the
migration ([0013](0013-catalogue-format.md)) gave it the slug `stolperstein`. The data itself says otherwise:
the generator of 2020 described the dataset as `http://data.judaicalink.org/datasets/stolpersteine`
(`stolpersteine-metadata.ttl.gz`), the dump directory was `stolpersteine/`, and the URIs are coined in the
namespace `data/stolpersteine/`. The dataset IRI `datasets/stolperstein` appeared only in our unpublished `-meta`
file and in the local QLever index.

## Decision

- The slug names the dataset as a whole (a collection reads as plural: `stolpersteine`). The namespace names
  where the URIs of its resources are coined and is chosen on its own; it may differ from the slug.
- The slug `stolperstein` is renamed to `stolpersteine` (entry, generator folder `generators/stolpersteine`, dumps
  path `stolpersteine/<version>/`). The namespace stays `stolpersteine`. The former page `/datasets/stolperstein/`
  is kept as an alias.
- Once a dataset IRI has been published, its slug is not changed. This rename is possible because the published
  IRI already was `datasets/stolpersteine`.

## Consequences

- The `-meta` file of the dataset is regenerated with the new IRI.
- Code that still reads Frankfurt's catalogue names the graph `datasets/stolperstein` until it switches to this
  catalogue ([open issues](../open-issues.md)).
- Frankfurt's entry is `stolperstein.md` (page `…/dataset/stolperstein/`); to be offered with the catalogue.

# 0011 Generators are deterministic and independent of their earlier output

Status: accepted · Date: 2026-10-06

## Context

Datasets are rebuilt often while they are developed. A rebuild of `places-linked` once counted its own
earlier output in the index as existing links and shrank from 49,638 to 2,272 triples. Web lookups
(Wikidata, DNB entityfacts) change over time.

## Decision

- The same input gives the same output (sorted iteration, deterministic tie-breaking).
- A generator ignores its own graph when it reads from the endpoint.
- Answers of web services are cached (`work/api-cache`), so that a rebuild gives the same result without
  querying the services again; the `-meta` states when they were queried.
- Large builds run with a log; the order of builds and index rebuilds is documented (`kg-complements/README.md`).

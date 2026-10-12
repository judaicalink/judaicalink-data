+++
slug = "ls-nli-legacy"
title = "Legacy nli-persons URIs linked to the NLI authority records"
author = "Kai Eckert"
date = "2026-10-12"
example = "http://data.judaicalink.org/data/nli/Abner_"
kind = "linkset"
method = ["deterministic"]
namespaces = ["ls-nli-legacy"]
inputs = ["nli-persons"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/ls-nli-legacy"
+++

For everyone who holds a URI of the superseded nli-persons: every legacy URI linked to the NLI authority records of
nli-records it was made from.

<!--more-->

For every URI of nli-persons, the records it was made from (`prov:wasDerivedFrom`), found by re-running the URI
assignment of the legacy generator on its input: all 182,445 legacy URIs are reproduced exactly. `owl:sameAs` is added
where the legacy URI stands for exactly one person record with its own name and dates, or, for URIs made only from
works or subject headings, to the one person record these name (same heading, compatible dates); then the record's
VIAF and Library of Congress numbers are added to the legacy URI as `owl:sameAs` as well. DQV quality annotations
(`http://data.judaicalink.org/data/ls-nli-legacy/annotation/…`) name the faulty legacy URIs: conflated records, wrong
name or dates, works or subject headings as persons. The records themselves are in nli-records (decision 0010).

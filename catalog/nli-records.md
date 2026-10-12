+++
slug = "nli-records"
title = "NLI authority records (persons and works)"
author = "Kai Eckert"
date = "2026-10-12"
website = "https://www.nli.org.il/"
example = "http://data.judaicalink.org/data/nli/record/viaf-7652270"
kind = "records"
method = ["converted"]
namespaces = ["nli/record"]
replaces = ["nli-persons"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/nli-records"
+++

The person and work records of the authority export of the National Library of Israel that nli-persons was made
from, one resource per record, with the identifiers of the export. It supersedes nli-persons.

<!--more-->

nli-persons (2019) coined its URIs from the name headings and dropped the record identifiers: different people with
the same name share a URI, one person has several URIs, works and subject headings became persons. This dataset
takes the same export again and keeps one resource per record: the VIAF number (field 901) and the Library of
Congress number (010) as `owl:sameAs`, the headings in all scripts (Latin without language tag; Hebrew script `he`,
Cyrillic `und-Cyrl`, Arabic `und-Arab`), variant names (400, 700), birth and death dates (046, else the dates of the
heading), places of birth and death (370), occupations (374), gender (375) and notes (678). Name/title records are
works (`jl:Work`), linked to their creator (`dcterms:creator`) where the heading matches exactly one person record,
else with the creator's name (`dc:creator`). Subject headings (name -- subdivision) are left out.

IRIs: `http://data.judaicalink.org/data/nli/record/viaf-<VIAF number>`, or `…/h-<hash of the headings>` for records
without a unique VIAF number. The links from the legacy nli-persons URIs to the records are in ls-nli-legacy
(decision 0010).

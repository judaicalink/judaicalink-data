+++
slug = "ep"
title = "Entity Pages - Judaicalink"
author = "Kai Eckert"
date = "2021-01-22"
example = "http://data.judaicalink.org/data/ep/1000037"
namespaces = ["ep"]
stable = "2021-05-28"
kind = "entity-pages"
method = ["rule-based"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/ep"

[files]
"entity_pages.ttl.gz" = "Entity Pages RDF data (2098149 triples)."
"ep_labels.ttl.gz" = "preferred and alternative labels for entity pages. See `label_selector.ipynb` in the repository."
"ep_locations.ttl" = "Entity Pages type classification - locations."
"ep_persons.ttl" = "Entity Pages type classification - persons."
"ep_birth_death_date_loc.ttl" = "Birth/death dates and locations for Entity Pages."
"subcategorization.ttl.gz" = "Subcategorization dataset for local Judaicalink resources."
"ep.ttl.gz" = "The entity pages: class, names, life dates and places, occupations, descriptions, coordinates, the records they represent (jl:represents) and their external identifiers (owl:sameAs)."
"ep-history.ttl.gz" = "IRIs that are no longer entity pages, one statement per event with its date: merged (jl:mergedInto), split (jl:splitInto), retired (jl:retiredDate); the history of earlier versions unchanged."

[[versions]]
version = "2021-05-28"
issued = "2021-05-28"
author = "Marco Rovera"
description = "Data files of the catalogue state judaicalink-site 81b42a5 (the state Frankfurt loaded)."

  [[versions.files]]
  path = "entity_pages.ttl.gz"
  bytes = 25813822
  sha256 = "06e4fc3e870e565b4c97db5f4d38ae97cba3c9fc5b15ba81264fda86a42420ea"

  [[versions.files]]
  path = "ep_labels.ttl.gz"
  bytes = 6962357
  sha256 = "44e5dec550100dbd5356033a128e2698488e43bb8cb99cef90be040f97590210"

  [[versions.files]]
  path = "ep_locations.ttl"
  bytes = 183635
  sha256 = "b035b3b2198b7ab304c5ebbf8c8eecda951b263563b295e02116516fa7ade718"

  [[versions.files]]
  path = "ep_persons.ttl"
  bytes = 14948404
  sha256 = "c5c8053f54ab758531eb1be05d0c7da7a7926da9e405bff98550c39c76cf3519"

  [[versions.files]]
  path = "ep_birth_death_date_loc.ttl"
  bytes = 7708440
  sha256 = "e2364f9703a864a9a9c2e80e3550d43ccd93c33aed1f48d0b9e1b2b0af5785e2"

  [[versions.files]]
  path = "subcategorization.ttl.gz"
  bytes = 19243049
  sha256 = "8b1d205a7d5a27ee2605afb8fc0e2d8cbf334ee702b55f48915838b02ec4935c"

  [[versions.files]]
  path = "ep-meta.ttl.gz"
  bytes = 2447
  sha256 = "8cab0f3ce80b0a504c4c85b8e04cda1c6240f1e0dca3486c1916683e9cf83994"
  triples = 124

[[changelog]]
date = "2025-06-05"
author = "Benjamin Schnabel"
text = "Generator ported from Jupyter notebooks to Python scripts (judaicalink-generators); the published version was not regenerated."

[[changelog]]
date = "2021-03-11"
author = "Marco Rovera"
text = "Birth and death dates and locations added (ep_birth_death_date_loc.ttl)."

[[changelog]]
date = "2021-02-19"
author = "Marco Rovera"
text = "Person and location classification added (ep_persons.ttl, ep_locations.ttl)."

[[changelog]]
date = "2021-02-15"
author = "Marco Rovera"
text = "Preferred and alternative labels added (ep_labels.ttl.gz)."

[[changelog]]
date = "2021-01-22"
author = "Marco Rovera"
text = "First version (entity_pages.ttl.gz)."
+++

The entity pages of JudaicaLink: one page for each person, place, organisation, work or subject, bringing together
the records that the datasets have about it. The page IRIs (`http://data.judaicalink.org/data/ep/<number>`) stay
stable from version to version.

<!--more-->

From the version 2026-10-12 on (decision 0022), each version is made from the previous one and the records of all
datasets: records are grouped by the transitive closure of their identity links (`owl:sameAs`, GND numbers; the same
identifier joins), computed fresh in every version, and the groups are compared with the pages of the previous
version. A page whose records stay together keeps its IRI; pages that turn out to be the same are merged, the oldest
IRI is kept and the others point to it (`jl:mergedInto`, can be redirected); a page that turns out to stand for
several entities is split (`jl:splitInto`, one statement per part); a page that no longer stands for a person, place,
organisation, work or subject is retired (`jl:retiredDate`). IRIs are never used again. Mistakes in the identity links
are corrected in the datasets (new versions, correction datasets), not in the entity pages.

Facts on a page (names, dates, places, occupations, descriptions, coordinates) are chosen from its records by a fixed
precedence of the datasets (GND, libraries and bibliographies, curated reference works, general knowledge bases,
automatically derived data) and of the languages (English, German, Hebrew).

The version 2021-05-28 is the legacy set by Marco Rovera (a page for every IRI of the knowledge graph of 2021,
including the mentions and pages of Compact Memory); see the generator folder.

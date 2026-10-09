+++
slug = "dbpedia-persons"
title = "Persons from DBPedia"
author = "Kai Eckert"
date = "2018-11-02"
example = "http://data.judaicalink.org/data/dbpedia/Aaron_Alfandari"
namespaces = ["dbpedia"]
stable = "2026-09-26"

[license]
name = "CC-BY-SA-3.0"
uri = "https://creativecommons.org/licenses/by-sa/3.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-sa.png"

[files]
"persons-gndid.ttl.gz" = "GND links for all persons in this dataset."
"Entityfacts-dbpedia-sameas.ttl.gz" = "EntityFacts links for all persons with an GND-id in this dataset."

[[versions]]
version = "2026-09-26"
issued = "2018-11-02"
author = "Maral Dadvar"
graph = "http://data.judaicalink.org/data/dbpedia-persons"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "generated_persons_DBPedia_enriched_02.ttl.gz"
  bytes = 710023
  sha256 = "34e353fd9b7bf20e8c53a673503eeeb400e4bef4c14a6f532041fde3191c96b3"

  [[versions.files]]
  path = "persons-gndid.ttl.gz"
  bytes = 30570
  sha256 = "e8d8cdab643f0b98840c5181299b7c6a00ea0274331ffd3420b2fe9ff68392f8"

  [[versions.files]]
  path = "Entityfacts-dbpedia-sameas.ttl.gz"
  bytes = 135800
  sha256 = "c1ff0f22f44f0c244aec4f609822cccc5710b706ca1b4b21e8c68ab750844105"

[[changelog]]
date = "2026-10-09"
text = "Migrated to the entry format of decision 0013: one version 2026-09-26 with the files of the archived catalogue state (judaicalink-site 81b42a5)."
refs = ["0013"]
+++

List of persons from DBpedia.
<!--more-->

Currently, this dataset contains a set of Rabbis extracted from DBpedia. This was done using an iterative process to identify classes that are associated with Rabbis and consequently all Rabbis associated with these classes.

In a second step, we created links to persons in the common authority file (Gemeinsame Normdatei, GND) of the German National Library.

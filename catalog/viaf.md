+++
slug = "viaf"
title = "VIAF: the clusters JudaicaLink uses"
author = "Kai Eckert"
date = "2026-10-18"
website = "https://viaf.org/en/viaf/data"
example = "http://data.judaicalink.org/data/viaf/54984961"
kind = "authority"
method = ["converted"]
namespaces = ["viaf"]

[license]
name = "ODC-By 1.0"
uri = "https://opendatacommons.org/licenses/by/1-0/"
statement = "https://viaf.org/en/viaf/data"
attribution = "VIAF (Virtual International Authority File), OCLC"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/viaf"
+++

The clusters of the Virtual International Authority File (VIAF, OCLC) that JudaicaLink uses: every cluster our
datasets or the other authority datasets link, with its names, life dates, class and the records of the libraries and
knowledge bases it brings together (GND, Library of Congress, Wikidata, ISNI, BnF and others). Made from the yearly
VIAF dump.
<!--more-->

VIAF clusters the authority records of national libraries and other sources that describe the same person,
organisation, place or work. The clustering is automated and, as a whole, reliable; individual clusters can join
records of different entities or split one entity into several clusters. JudaicaLink links its records to VIAF in the
linkset `ls-viaf`, unless the life dates contradict (decision 0029).

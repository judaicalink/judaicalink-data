+++
slug = "record-classes"
title = "Classes of untyped records"
author = "Kai Eckert"
date = "2026-10-12"
example = "http://data.judaicalink.org/data/yivo/abramovich_rafail"
kind = "complement"
method = ["lookup", "rule-based"]
inputs = ["yivo"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/record-classes"
+++

The class (person, place, organisation, work, subject) of records that their datasets state no type for, so that
they appear on the entity pages.

<!--more-->

The articles of the YIVO Encyclopedia (dataset yivo) have no `rdf:type`. Their class is taken from the Wikidata item
of the article (property P8569, the classes of its instance-of statements): humans are persons; geographic
locations, administrative territorial entities and settlements places; organisations organisations; written works,
periodicals and creative works works. Articles without such an item are persons if their abstract starts with life
dates, "(1880–1963), revolutionary and publicist", and subjects otherwise. The classes are assigned automatically
and not checked one by one.

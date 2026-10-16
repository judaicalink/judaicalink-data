+++
slug = "ls-gnd"
title = "Links to the GND records"
author = "Kai Eckert"
date = "2026-10-16"
example = "http://data.judaicalink.org/data/bhr/1"
kind = "linkset"
method = ["deterministic"]
inputs = ["gnd"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/ls-gnd"
+++

Every JudaicaLink record that refers to a GND entry, linked to the JudaicaLink record of the current entry in the
dataset gnd.

<!--more-->

The links rely on the identifiers our datasets state, as their sources give them, and on the replacements of
identifiers that the GND itself states (dataset `gnd`, whose description says how its records are made). A
reference to a deprecated identifier, or to one the dataset `gnd` does not have, is left out. These links are what
joins the records of different datasets on the entity pages (decision 0029).

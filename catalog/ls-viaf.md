+++
slug = "ls-viaf"
title = "Links to the VIAF clusters"
author = "Kai Eckert"
date = "2026-10-18"
example = "http://data.judaicalink.org/data/nli/record/viaf-54984961"
kind = "linkset"
method = ["deterministic"]
inputs = ["viaf"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/ls-viaf"
+++

Every JudaicaLink record that refers to a VIAF cluster, linked to the JudaicaLink record of the cluster in the
dataset viaf, unless the life dates or the classes of the two contradict.

<!--more-->

The links rely on the VIAF numbers our datasets and the other authority datasets state. VIAF clusters the records of
many libraries automatically; JudaicaLink gives it the benefit of the doubt and leaves a link out only when the record
and the cluster both give a year of birth (or of death) more than one year apart, or when one is a person and the
other a work (decision 0029). A number the dataset viaf does not have (a cluster merged or made after the dump) is left
out. These links are what joins the records of different datasets on the entity pages.

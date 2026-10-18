+++
slug = "dbpedia"
title = "Wikipedia and DBpedia: the English and German articles JudaicaLink uses"
author = "Kai Eckert"
date = "2026-10-18"
website = "https://www.dbpedia.org"
example = "http://data.judaicalink.org/data/dbpedia/en/Moses_Mendelssohn"
kind = "authority"
method = ["converted", "lookup"]
namespaces = ["dbpedia"]
replaces = ["dbpedia-persons"]

[identity]   # the properties that state identity, and towards which sources (decision 0032)
"owl:sameAs" = ["wikidata"]

[license]
name = "CC-BY-SA-3.0"
uri = "https://creativecommons.org/licenses/by-sa/3.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-sa.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/dbpedia"
+++

The English and German Wikipedia articles, and their DBpedia resources, that JudaicaLink uses: every article our
datasets or the other authority datasets name, with its current title, the Wikidata item of the article, and the
facts the former dataset dbpedia-persons had about persons.
<!--more-->

Per language, an article and its DBpedia resource are one identifier (decision 0031): `data/dbpedia/en/<title>` and
`data/dbpedia/de/<title>`. Wikipedia renames articles; an old title is followed to the current article and recorded
as replaced by it, a title that no longer exists as deprecated. Other languages are linked, not described. The
records of dbpedia-persons (2018) are replaced by the records of their articles.

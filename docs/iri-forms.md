# Canonical forms of IRIs and coordinates

The same identifier or term can be written in several forms: `http` or `https`, with or without a final slash, or
the address of the description document instead of the thing (`…/about`, `…/about.rdf`, `….html`). We write each in
one form: the one the publisher of the data or the ontology uses. The forms are in `src/jl/iris.py` (`FORMS`,
`canonical()`); generators write external IRIs through `canonical()`.

A canonical form only fixes the spelling. It never replaces one identifier by another: that an identifier is
deprecated, replaced or deleted is data, stated in the source datasets (`dcterms:isReplacedBy`, `owl:deprecated`,
[decision 0029](decisions/0029-identity-from-our-linksets.md)).

| Source | Canonical form | Where the source states it | Variants brought to it |
|---|---|---|---|
| JudaicaLink | `http://data.judaicalink.org/…` | our own IRIs ([0002](decisions/0002-uris.md)) | `https` |
| GND | `https://d-nb.info/gnd/<number>` | the GND Linked Data Service dumps, data.dnb.de/opendata | `http`, `/about`, `/about/<format>`, final slash |
| VIAF | `https://viaf.org/viaf/<number>` | viaf.org/en/viaf/data ("canonical structure of a VIAF URI") | `http`, `www.`, final slash |
| Wikidata | `http://www.wikidata.org/entity/<Q…>` | the concept URIs of the Wikidata RDF dumps | `https`, no `www.` |
| GeoNames | `https://sws.geonames.org/<number>/` | GeoNames RDF (`rdf:about` in `sws.geonames.org/<number>/about.rdf`) | `http`, `www.geonames.org`, no final slash, `about.rdf` |
| LC Name Authority File | `http://id.loc.gov/authorities/names/<id>` | the LC dumps, id.loc.gov/download | `https`, `.html`, `.rdf`, `.json` |
| LC Real World Object | `http://id.loc.gov/rwo/agents/<id>` | the LC dumps (`madsrdf:identifiesRWO`): the person, organisation … that the name authority `<id>` identifies; the same identifier for linking | `https`, `.html`, `.rdf`, `.json` |
| ISNI | `https://isni.org/isni/<16 characters>` | isni.org | `http`, `www.`, without `isni/` |
| DBpedia | `http://dbpedia.org/resource/<name>` | the DBpedia resource IRIs | `https` |
| Getty TGN | `http://vocab.getty.edu/tgn/<number>` | vocab.getty.edu | `https`, `-place` |

## Vocabulary terms

The terms of a vocabulary in the namespace its publisher uses in its own files (`VOCABULARIES` in `src/jl/iris.py`):

| Vocabulary | Canonical namespace | Variant brought to it |
|---|---|---|
| GND ontology | `https://d-nb.info/standards/elementset/gnd#` | `http://d-nb.info/standards/elementset/gnd#` |
| GeoNames ontology | `https://www.geonames.org/ontology#` | `http://www.geonames.org/ontology#` |
| MADS/RDF | `http://www.loc.gov/mads/rdf/v1#` | `http://www.loc.gov/standards/mads/rdf/v1#` |

## Coordinates

A point is written `"POINT(<longitude> <latitude>)"^^geosparql:wktLiteral` (GeoSPARQL; decided 2026-10-16), the
numbers exactly as the source gives them, only without `+` and leading zeros: the GND's `"Point ( +035.216329
+031.769040 )"` becomes `"POINT(35.216329 31.769040)"`. Without the datatype a value is only a string for GeoSPARQL
functions, and different spellings of the same point look like different values. `canonical_wkt()` in
`src/jl/iris.py` converts; generators write `geosparql:asWKT` through it.

## The check

Every `jl generate` counts the subjects, predicates and IRI objects of the files it writes that are not in canonical
form, by source, and the `geosparql:asWKT` values not in canonical form or without the datatype (`wkt`), with examples: in the run log, in the run record (`files[].noncanonical`) and in the summary the command
prints. It warns; it does not stop a run, because the record datasets keep the forms of their sources until their
generators are made again.

## What is fixed where

- Our linksets and the source datasets (decision 0029) write canonical forms from their first version.
- Record datasets get them with their next version, when their generator writes through `canonical()`; there is no
  separate wave of new versions only for the forms (the entity pages do not depend on them: `key()` in the ep
  generator treats all forms as one key).
- To add a source: a row in `FORMS` (pattern, form, where the source states it) and in the table above.

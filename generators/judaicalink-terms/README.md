# judaicalink-terms: generator

A label (`jl:label`, English and German) for every class and property used in the JudaicaLink datasets.

## History

- 2026-10-17 (Kai Eckert): new dataset.

## Inputs

- The stable versions of all datasets with RDF data (`stable_inputs`), and the run `run-20261016T210958Z` of
  wikidata (until wikidata is a version): the terms used (predicates and classes) and the labels datasets give their
  own terms.
- `inputs:vocabularies/<name>-2026-10-17`: the official files of the vocabularies our data uses (GND, agrelon, MADS/RDF,
  SKOS, DCMI terms and elements, FOAF, schema.org, RDF, RDFS, OWL, GeoNames, Web Annotation, PROV-O, BIBFRAME, BFLC, LC
  identifiers, GeoSPARQL 1.0, DQV), each with its address in `input.toml`.
- `inputs:vocabularies/judaicalink-ontology-common-layer-b039648`: the Turtle of the ontology branch `common-layer`
  (until it is merged); the ontology version of the catalogue is read as well.
- `inputs:web-caches/wikidata-properties-2026-10-17`: the labels of the Wikidata properties used.

## Rule

Per term and language, the first source with a label: the dataset that coins the term, the ontology (`jl:label` of
foreign terms, `rdfs:label` of own terms), the term's own vocabulary (`rdfs:label`, `skos:prefLabel`,
`madsrdf:authoritativeLabel`, also as attributes in RDF/XML), Wikidata. A label without language tag only if the term
has neither English nor German. Terms of the GND ontology and of GeoNames are looked up under `http` and `https`, MADS/RDF
under both of its namespaces.

## Run of 2026-10-17

627 terms, 616 labelled (by the first source: datasets 221, GND 175, ontology 102, MADS/RDF 41, Wikidata 12, others
65); 890 triples; about two minutes. Without a label (listed in the log): eight `gndo:` terms that the GND ontology does
not have, used by gba (`gndo:birthDate`, `deathDate`, `occupation`, `hasAbstract`, `hasPublication`, `relation`,
`alternativeName`) and nrwbibdjg (`gndo:forname`); `jl:Person` (rujen, not defined); `jl:grandparent` (pull request
#22); `madsrdf:hasCharacteristic` (not in MADS/RDF 1.x).

## Reproduction

**Reproducible** from the inputs. New vocabulary files or new datasets give a new version.

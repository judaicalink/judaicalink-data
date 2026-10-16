# gnd: generator

The GND records JudaicaLink uses (decision 0029), made from the dumps of the DNB. Replaces gnd-persons (2018) and
gnd-persons-entityfacts (2026-10-12, removed before anyone used it).

## History

- 2026-10-16 (Kai Eckert): new dataset; the selection rules of gnd-persons kept as rules of this one.

## Inputs

- `inputs:gnd/lds-2026-02-17`: the complete GND (Linked Data Service, N-Triples, state 2026-02-17).
- `inputs:gnd/entityfacts-2026-10-13`: DNB EntityFacts (NDJSON): the links of each GND entity to other files.
- `inputs:gnd/redirects-2026-10-13`: the redirected (609,888) and deleted (32,219) GND numbers.
- `inputs:gnd/ubffm-lists-2018`: the Freimann list and the GND numbers of the UB Frankfurt person records.
- `gnd-persons/2018-11-29` (rule `previous`) and the stable versions of the datasets that link GND records (rule
  `linked`; the list `LINKED` in `generate.py`).

## Selection

`gnd-selection.tsv.gz`, one row per GND number and reason, with the current number (empty if the number is deleted or
not in the GND any more). A record is included if any row names it; the data has each record once.

| Reason | Rule |
|---|---|
| `linked` | an IRI `d-nb.info/gnd/<n>` or `data/gnd/<n>` as object, or a `gndo:gndIdentifier`, in a stable version of one of our datasets; detail: the dataset. A `data/gnd/<n>` as subject is a statement about the record (e.g. records-normalized), not a link |
| `area-occupation` | **off** (parameter `area_rule`, default `off`, decided 2026-10-16): a differentiated person with the geographic area code XB-IL (Israel) or XY (Jews) and at least one occupation, the rule of gnd-persons 2017 applied to the current GND. The occupation ontology of 2017, which limited the occupations, is on file only for DBpedia, so the rule would take any occupation: 18,102 persons, 15,258 of them reached by no other reason, with a weaker rule than the original. The 4,020 persons of 2017 stay through `previous`; whether such a broad selection belongs in the graph is a question of content, to be decided with a defined rule; detail: the area code |
| `freimann` | the Freimann list of UB Frankfurt |
| `ubffm-authors` | the person records of UB Frankfurt; detail: the PPN |
| `previous` | every record of gnd-persons 2018, so that no `data/gnd/` IRI loses its description |

## Data

Each record `data/gnd/<n>` keeps the GND's statements (IRIs in canonical form, `docs/iri-forms.md`) and gets
`owl:sameAs <https://d-nb.info/gnd/<n>>`, the classes the entity pages know (`foaf:Person`, `foaf:Organization`,
`jl:Place`, `jl:Work`), `skos:prefLabel`/`altLabel`, `jl:birthDate`/`deathDate`, `jl:birthLocation(URI)`/
`deathLocation(URI)` (the name of the GND place), `jl:occupation` (the name of the GND subject heading), the geometry
as `geosparql:asWKT`, and the links of EntityFacts (without the GND itself and without our own IRIs, which
EntityFacts takes from our BEACON). Left out: the description document (`…/about`: licence, dates of change), the
qualified relations (`gndo:hasRelation`, blank nodes) and the qualified variant names (blank nodes).

Replacements (decision 0029): every former number of an included record as `<https://d-nb.info/gnd/<old>>
dcterms:isReplacedBy <https://d-nb.info/gnd/<n>>` (the GND states them as `owl:sameAs` and `dnb:deprecatedUri`);
where our own record exists for the old number, also `data/gnd/<old> dcterms:isReplacedBy data/gnd/<n>`; deleted
numbers that our data cites as `owl:deprecated true`.

## Run of 2026-10-16

41,346 records, 1,390,614 triples; numbers by reason (in brackets: not reached by a reason above): linked 19,489,
freimann 587 (343), ubffm-authors 33,161 (25,446), previous 35,301 (1,915: mostly the persons of the 2017 rule).
18,914 former numbers replaced (3 of them our own records); 5 cited numbers deleted; 1,371 cited numbers are in
neither the dump nor the redirect file (mostly from ubffm-persons, presumably former undifferentiated name records).
Coordinates in canonical form (docs/iri-forms.md). About four minutes.

## Reproduction

**Reproducible** from the inputs. A newer dump is a new input and gives a new version.

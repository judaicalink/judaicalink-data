# 0034 footprints made from the Footprints API, true to the API

Status: accepted · Date: 2026-10-25

## Context

`footprints` 2026-10-12 is the version of 2024-03-18 with its systematic errors fixed (0024): books, persons and places
from the 2024 crawl, IRIs hashed from names (one IRI for all persons of the same name), GND numbers of places from a
name search, relations and identifiers written as text. The API, behind a bot challenge in 2025, answers again to the
User-Agent of the framework (0028): a complete harvest was made on 2026-10-19/20 (`generators/footprints/harvest.py`,
`harvest_driver.py`): 3,765 works, 6,860 imprints, 10,998 copies, 24,482 footprints (the evidence that a copy was at a
place at a time: owner signatures, catalogues, censors' marks), 11,642 persons and 1,027 places. The API gives the
VIAF numbers of 1,556 persons and the identifiers of imprints (Bibliography of the Hebrew Book 5,736, WorldCat 996,
NLI, ISTC, USTC, Vinograd), but not the GeoNames ids of its places, which Footprints makes from GeoNames records.

## Decision

- **Source:** the harvest of 2026-10-19/20 (`inputs:footprints/api-2026-10-20`: the pages of every list endpoint as
  the API sent them, the records referred to but missed by the paging, the records by id) and the GeoNames ids of the
  places as confirmed by Footprints (`inputs:footprints/geonames-<date>`, `generators/footprints/geonames.py`:
  candidates from the GeoNames dump, confirmed by the API's `altname` endpoint, which answers with the place that has
  a GeoNames id). The generator reads only these inputs; it makes no requests.
- **True to the API, without the bookkeeping:** all four levels (work, imprint, copy, footprint) and the persons,
  places, roles and languages, with every field, except: the editors' bookkeeping (`created_by`, `last_modified_by`,
  names of Columbia staff; `created_at`, `modified_at`, `verified_modified_at`), the `description` fields (HTML
  rendered by the site from the other fields) and `narrative` (a sentence the site makes from the fields of a
  footprint). Kept as data of the source: `verified`, `percent_complete` and the editorial flags (e.g. "Imprint has no
  BHB number"). Notes in HTML as `rdf:HTML`.
- **Images are linked, not copied:** the digital objects of the footprints (photographs of bookplates, signatures,
  catalogue entries on Footprints' storage) as `foaf:depiction`; their licence is not stated.
- **Terms in the dataset namespace** (as for haskala, 0026): the classes and properties of the API in
  `data/footprints/vocab/`, defined in `footprints-vocabulary.ttl.gz` of the version; JudaicaLink and standard terms in
  addition where they exist (`skos:prefLabel`, `jl:birthDate`, `gndo:author`, `gndo:editor`, `dcterms:publisher`,
  `dcterms:issued`, `geosparql:asWKT`, `owl:sameAs`).
- **Role-qualified agents:** Footprints links persons through actor records (person, role, and the name in the
  source, e.g. "Yehoshuʻa Falḳ *as* יהושע בן אלכסנדר"); they are resources of their own (no blank nodes). Each record
  also links its persons directly, one property per role (`vocab:owner`, `vocab:printer`, …; `gndo:author`,
  `gndo:editor`, `dcterms:publisher` for these three roles), so that the persons of a record can be found without the
  actor records.
- **Which records are entities:** works and imprints `schema:CreativeWork`, places `schema:Place`. Persons are
  `foaf:Agent` and `vocab:Person`: the API does not tell persons from organisations (libraries, booksellers, printing
  houses, congregations are "persons"); their class is stated in `record-classes` (0025), from the VIAF record (person
  or organisation) where there is one, else by a rule on the name, else person. Copies and footprints are records,
  not entities (no entity pages). The dates of a person stay as the API names them (birth and death, also for the
  founding of an institution), since the dataset cannot tell which persons are institutions.
- **IRIs from the API ids, with the API's names:** `data/footprints/<endpoint>/<id>` for `writtenwork`, `imprint`,
  `book` (the copy), `footprint`, `person`, `place` (the canonical place), `actor`, `role`, `language`.
- **The IRIs of 2024** (hashes of names, `uuid5(OID, sha256(name))`) are `dcterms:isReplacedBy` the records they stood
  for, within the same level: a person by the API addresses it names (`jl:describedAt`), else by its name; a work by
  the title of the work; a place by the first part of the canonical name. Where the hash of a name stands for several
  records (one IRI for all of the same name), it is replaced by all of them, and the entity pages split the page (ep
  follows replacements; several targets make a split, 0022). An IRI of 2024 that matches nothing (a name changed since,
  the regions and countries of 2024) is not stated; its page keeps its other records or is retired.
- **Identity** (0032): persons `owl:sameAs` VIAF and LC as given by the API; places `owl:sameAs` GeoNames where
  Footprints confirmed the id. The identifiers of works and imprints are `dcterms:identifier` (`<slug> <id>`, the
  slugs of the API's identifier types), not identity. No lookups (the GND numbers come through the VIAF linkset).
- **Dates:** the text as the API displays it and the normalised value of the API's EDTF form (0035).
- A new version of `footprints`, stable in place of 2026-10-12; licence CC BY-SA 4.0 as stated by Footprints; method
  `converted` (no machine translation).

## Consequences

- `generators/footprints/generate.py` makes the version from the inputs; the generator of 2026-10-12 (from the 2024
  file) is in the git history (commit of that version).
- `record-classes` gets a part for the footprints persons; ls-viaf and ls-geonames, the link quality of the new
  identity links (0032) and ep are made again.
- Not in the API, to ask Footprints: the GeoNames ids (they would replace the confirmation step), the digital objects
  of persons, imprints and copies.
- The Atlas showcase can show the footprints (copies at places in time).

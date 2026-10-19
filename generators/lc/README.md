# lc: generator

The records of the LC Name Authority File (LCNAF) that JudaicaLink uses (decision 0029), made from the bulk export of
id.loc.gov.

## History

- 2026-10-16 (Kai Eckert): new dataset (82,806 records).
- 2026-10-19 (Kai Eckert): the selection comes from the cascade of the authority datasets (`jl cascade`,
  decision 0029), with the LC identifiers of VIAF and Wikidata.

## Inputs

- `inputs:cascade/2026-10-19`: `lc-selection.tsv.gz`, the selection of the cascade (`jl cascade` with `lookup.py`).
- `inputs:lc/names-2026-09-27`: the complete LCNAF in MADS/RDF, N-Triples (issued 2026-09-27, modified 2026-09-13),
  one block per authority record between `# BEGIN /authorities/names/<id>` and `# END …`, with the record's Real
  World Object (`id.loc.gov/rwo/agents/<id>`: dates, places, occupations) and its blank nodes (variants, sources,
  element lists, administrative metadata). The SHA-1 stated in the export's description file does not match the
  file; the archive is intact.

`lookup.py` gives the cascade LC's part: an index of the export (built once per dump, in `<build>/_index/`) with the
record identifiers, the deprecated ones, and the `madsrdf:hasExactExternalAuthority` targets of each record as the
dataset writes them. Most of these targets are LC's own records in VIAF (`viaf.org/en/viaf/LC|<id>`), which identify
no cluster, so LC selects few records of other authorities.

## Selection

`lc-selection.tsv.gz`, one row per LC identifier and dataset that links it (`linked`): one of our datasets (any
statement) or another authority dataset (its declared identity, decision 0032), with the current identifier (empty if
LC has deprecated the record or the dump does not have it). Our data links LC both as the authority record
(`id.loc.gov/authorities/names/<id>`: nli-records, ls-nli-legacy, VIAF, Wikidata) and as its Real World Object
(`id.loc.gov/rwo/agents/<id>`: EntityFacts in gnd); both count.

## Data

Each record `data/lc/<id>` keeps the statements of the authority and of its Real World Object (IRIs in canonical form,
`docs/iri-forms.md`; occupations and fields of activity flattened from their blank nodes to the LCSH IRI) and gets
`owl:sameAs <http://id.loc.gov/authorities/names/<id>>`, the classes the entity pages know (`foaf:Person` for personal
names, `foaf:Organization` for corporate names, `schema:Place` for geographic names, `schema:CreativeWork` for titles;
conference names get none, as in gnd), `skos:prefLabel` (LC gives one authoritative label per script,
language-tagged), `skos:altLabel` (the variant labels), `jl:birthDate`/`deathDate`, `jl:birthLocation(URI)`/
`deathLocation(URI)` (an IRI of a place authority with its name, or the label of a blank node), and `owl:sameAs` for
the exact external authorities that are identifiers of a known source (GND, VIAF clusters, ISNI, Wikidata, TGN; LC's
Wikidata links, written as pages `wikidata.org/wiki/Q…`, are taken as the item). LC's own record in VIAF
(`viaf.org/en/viaf/LC|<id>`), present on almost every record, is not a VIAF cluster: kept as LC states it, no
`owl:sameAs`. Left out: administrative metadata, sources, element lists, affiliations (blank nodes), and links to
JudaicaLink.

LC marks a withdrawn record as `madsrdf:DeprecatedAuthority` and names no successor in the export;
`madsrdf:hasLaterEstablishedForm` links a heading to a later, different one (e.g. a renamed conference) and is no
replacement. So there are no replacements: a deprecated identifier our data cites is stated as
`<http://id.loc.gov/authorities/names/<id>> owl:deprecated true`.

## Version 2026-10-19

91,943 records of 92,479 linked identifiers (viaf 89,161, wikidata 60,828, gnd 56,087, nli-records 54,079,
ls-nli-legacy 53,182, footprints 1), 1,986,497 triples; 165 cited identifiers deprecated, 371 not in the dump. About
five minutes.

## Reproduction

**Reproducible** from the inputs. A newer export, or a new cascade, is a new input and gives a new version
(`docs/process.md`, 2a).

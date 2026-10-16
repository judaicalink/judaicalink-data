# lc: generator

The records of the LC Name Authority File (LCNAF) that JudaicaLink uses (decision 0029), made from the bulk export of
id.loc.gov.

## History

- 2026-10-16 (Kai Eckert): new dataset.

## Inputs

- `inputs:lc/names-2026-09-27`: the complete LCNAF in MADS/RDF, N-Triples (issued 2026-09-27, modified 2026-09-13),
  one block per authority record between `# BEGIN /authorities/names/<id>` and `# END …`, with the record's Real
  World Object (`id.loc.gov/rwo/agents/<id>`: dates, places, occupations) and its blank nodes (variants, sources,
  element lists, administrative metadata). The SHA-1 stated in the export's description file does not match the
  file; the archive is intact.
- The stable versions of the datasets that link LC records (`stable_inputs`), and the run of gnd named in
  `GND_RUN` (EntityFacts links GND records to LC); it becomes the gnd version once that is made.

## Selection

`lc-selection.tsv.gz`, one row per LC identifier and dataset that links it (`linked`), with the current identifier
(empty if LC has deprecated the record or the dump does not have it). Our data links LC both as the authority record
(`id.loc.gov/authorities/names/<id>`: nli-records, ls-nli-legacy) and as its Real World Object
(`id.loc.gov/rwo/agents/<id>`: EntityFacts in gnd, nrwbibdjg); both count.

## Data

Each record `data/lc/<id>` keeps the statements of the authority and of its Real World Object (IRIs in canonical form,
`docs/iri-forms.md`; occupations and fields of activity flattened from their blank nodes to the LCSH IRI) and gets
`owl:sameAs <http://id.loc.gov/authorities/names/<id>>`, the classes the entity pages know (`foaf:Person` for personal
names, `foaf:Organization` for corporate names, `jl:Place` for geographic names, `jl:Work` for titles; conference names
get none, as in gnd), `skos:prefLabel` (LC gives one authoritative label per script, language-tagged),
`skos:altLabel` (the variant labels), `jl:birthDate`/`deathDate`, `jl:birthLocation(URI)`/`deathLocation(URI)` (an IRI
of a place authority with its name, or the label of a blank node), and `owl:sameAs` for the exact external authorities
that are identifiers of a known source (GND, VIAF clusters, ISNI, Wikidata, TGN; LC's Wikidata links, written as pages
`wikidata.org/wiki/Q…`, are taken as the item). The other external authority, present on almost every record, is
LC's own record in VIAF (`viaf.org/en/viaf/LC|<id>`), not a VIAF cluster: kept as LC states it, no `owl:sameAs`.
Left out: administrative metadata, sources, element lists, affiliations (blank nodes), and links to JudaicaLink.

LC marks a withdrawn record as `madsrdf:DeprecatedAuthority` and names no successor in the export;
`madsrdf:hasLaterEstablishedForm` links a heading to a later, different one (e.g. a renamed conference) and is no
replacement. So there are no replacements: a deprecated identifier our data cites is stated as
`<http://id.loc.gov/authorities/names/<id>> owl:deprecated true`.

## Run of 2026-10-16

82,806 records of 83,089 linked identifiers (nli-records 54,079, ls-nli-legacy 53,182, gnd 40,451, nrwbibdjg 458,
footprints 1), 1,791,761 triples; 120 cited identifiers deprecated, 163 not in the dump. About six minutes.

## Reproduction

**Reproducible** from the inputs. A newer export is a new input and gives a new version.

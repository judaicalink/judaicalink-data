# Open issues

State 2026-10-16. Remove an item when it is solved (with a reference to the decision, version or commit); what was
solved is in the decisions, the changelogs of the versions and the git history.

## Identity and authority data (decision 0029, in progress)

- **Authority datasets:** `gnd`, `lc`, `geonames` are versions (2026-10-16). To do: `wikidata` (lookup running:
  102,865 items; identifier statements whose reference cites JudaicaLink left out), `viaf` (dump of 2024-08-04
  downloading; check its structure: source records per cluster, redirects of merged clusters, NLI J9U numbers).
  dbpedia-persons: rename or replace by a `dbpedia` dataset, and a complement from Wikidata (GND, dates, places).
- **Linksets per authority:** `ls-gnd`, `ls-lc`, `ls-geonames` exist as runs (2026-10-16); to do `ls-wikidata`
  (also the source identifiers Wikidata states: BHR, YIVO, rujen, NLI; DBpedia through the sitelinks) and `ls-viaf`
  (linked unless the life dates contradict). Versions of all five together, after the entity pages have been tried.
- **Entity pages with `identity = linksets`:** the identity report (ep generator) shows what still splits; with
  ls-gnd, ls-lc, ls-geonames 3,799 groups (of 14,343 with today's linksets alone). Open: about 90 groups joined only
  by GND numbers the GND no longer has (1,371 such numbers, mostly from ubffm-persons); the 5 direct links between
  our records (e.g. bhr → djh) need a small linkset; `KNOWN_DISTINCT` must name the new bhr and hhkeydocs IRIs.
- **Replaced or dropped when ls-wikidata exists:** ls-yivo-wikidata and dbp-wiki-geo-linking (replaced); the drafts
  ls-nli-wikidata, ls-bhr-wikidata, ls-rujen-wikidata (never published; delete).
- **Made again on the new versions:** records-normalized and quality-annotations (they still read the versions of
  2026-10-12); corrections-links reads gnd-persons (now deprecated): check whether its corrections still apply.
- **gnd selection:** whether a broader selection (e.g. persons by GND area code, the rule of 2017, which `gnd` keeps
  off) belongs in the graph is a question of content, to be decided with a defined rule.
- **Wikidata property P13183** ("JudaicaLink person (GND) ID", 31,231 uses) has an `https` formatter URL, which spreads
  the `https` form of our IRIs: propose `http://data.judaicalink.org/data/gnd/$1` on Wikidata.

## Ontology and application profile

- **Application profile:** the ontology defines our terms and also describes foreign terms (`skos:prefLabel`,
  `owl:sameAs`, `geo:asWKT`, …), so the extracted Turtle states things about terms of others. Proposal: the ontology
  defines only `jl:` terms; a Dublin Core application profile (DCTAP: one row per property per kind of resource,
  with value types, cardinality, usage notes and the canonical forms) describes which terms we use; documentation and
  SHACL shapes are generated from it, and the framework checks every run against them. To decide with it: our classes
  `jl:Place`, `jl:Work`, `jl:Subject` against standard classes.
- **Coordinates:** we keep `geo:asWKT` directly on the place (decided 2026-10-17). To try: a complement
  (e.g. `geometries`) that adds the GeoSPARQL form for every place with a point: `<place> geo:hasGeometry
  <geometry>`, `<geometry> a geo:Geometry ; geo:asWKT "POINT(…)"^^geo:wktLiteral`, the geometry IRI coined in the
  complement's namespace from the place IRI (e.g. `data/geometries/geonames/281184`), generated from all stable
  datasets; then test GeoSPARQL queries (distance, within) in Fuseki and QLever on the platform.
- **rujen** types its records `jl:Person`, which the ontology does not define: the next rujen version uses
  `foaf:Person`, like all other datasets (the entity pages read both).
- **Pull requests prepared** (branches, not pushed): `common-layer-terms` (terms used by several datasets, from
  `reports/2026-10-17-terms-in-use.md`) and `dcterms-only` (decision 0030); merge in this order.
- In Frankfurt, ontology term IRIs do not resolve (`data.judaicalink.org/ontology/<term>` → a 404 page): suggest a
  redirect to ontology.judaicalink.org.
- The catalogue names ontology version 2025-11-27 (in `lokal/dumps-additions/ontology/2025-11-27/`, not published);
  `ontology-complements` redefines six terms of it (`belongsToIssue`, `belongsToJournal`, `birthLocationURI`,
  `deathLocationURI`, `gitCommit`, `gitWeb`): rebuild it and load both in an endpoint (with the platform, 0016).

## Data

- **Footprints:** API harvest running (works and imprints done; copies, footprints, persons; the API throttles per
  worker, the harvest waits and tries again); then the gap fill (374 imprints missed by the paging), the GeoNames
  confirmations of the places, and the generator (four levels, IRIs from the Footprints ids, the name IRIs of 2024
  replaced). To ask Footprints: the GeoNames ids and the digital objects of persons, imprints and copies in the API.
- **geo-coordinates:** a new version with canonical IRIs and points (the check reports 2,643 GeoNames and 5,218 GND
  IRIs and the points); Berlin is missing; some of its GND→GeoNames links are wrong (Ostrzeszów → Golenice, Bad
  Bramstedt 115 km off).
- **epidat:** about 6,200 gravestones of cemeteries that are not in the GitLab repository are available from the
  harvesting interface (Epidat: 322 editions, 54,243 gravestones; we have 268 cemeteries); the withdrawn cemeteries of
  2023 are online again (their 451 persons can come back); the cemetery table (GND, coordinates) is not used yet.
- **yivo:** the encyclopedia has a new JSON API (same ids): 63 entries missing in our crawl, 279 cross-references as
  alternative names, authors, dates of change; and the IRIs lower-cased since 2020, which break the yivo links of
  2014links and interlinks.
- **stolpersteine:** the Wikipedia lists now hold about 382 stones (we have 223) with address, coordinates and date;
  first the licence (Wikipedia CC BY-SA, our entry CC0; or base it on Wikidata, CC0).
- **occupations:** never a version; records-normalized uses 484 occupation IRIs that nothing describes; licence in
  the entry CC BY 4.0, the rest CC0.
- **nrwbibdjg:** reachable again; stable work IRIs from the bibliography's ids instead of title collisions, about 800
  undefined IRIs, copied GND triples. **jre:** the wiki's API is open; licence not stated.
- **hhkeydocs:** the documents, articles and bibliography of the site as records (later).
- **Fuseki warnings** (test load 2026-10-13): 13 impossible dates typed `xsd:date` (e.g. `1902-02-29`; 7 in
  records-normalized, 6 carried into ep), which records-normalized should not type as dates; 57 legacy `data/nli/`
  IRIs with characters not allowed in IRIs (47 in ls-nli-legacy, 1 in date-enriched).
- **Dates beyond xsd** (intervals "1663/1711", decades "182X", circa): EDTF (ISO 8601-2, the LC datatype
  `http://id.loc.gov/datatypes/edtf/EDTF`) as the normalised value where `xsd:date`/`gYear` cannot express it; with
  records-normalized and Footprints (which writes EDTF). HeidelTime for dates in running text (biographies) and
  OWL-Time (intervals, Hebrew calendar) noted, not planned.
- **cm-entities** takes all VIAF numbers of a Wikidata item, which can include a work's (Sahula); `ls-viaf` must
  not follow these.
- **YIVO subsections** (346 `skos:Concept`) are taken by ep as subjects; ep must read both yivo and record-classes.
- **gba** uses the GND namespace for its own fields (`gndo:birthDate`, `deathDate`, `occupation`, `hasAbstract`,
  `hasPublication`, `relation`, `alternativeName`; not in the GND ontology); **nrwbibdjg** writes `gndo:forname`
  (for `gndo:forename`). Both for their next versions (found by judaicalink-terms, 2026-10-17).
- **DC Elements** (decision 0030): the generators of nli-records (`dc:creator`), hirsch-family and stolpersteine
  fail until they write `dcterms:`; with their next versions. hirsch-family states source documents (PDF, scans)
  as `dc:subject` strings of the person: IRIs with `rdfs:seeAlso`; stolpersteine the photo of the stone:
  `foaf:depiction`. Footprints: `dcterms:` in the new generator.
- **lc 2026-10-16** types 1,495 records with `http://www.loc.gov/standards/mads/rdf/v1#Geographic` (made before
  the canonical-form check); the next run writes the canonical namespace.
- **gba** IRIs changed in 2025 (`JecheskelEzechielLandau` → `Jecheskel__Ezechiel__Landau`): check whether anything
  links to the old ones. **djh** 2018 has non-ASCII characters in IRIs.
- **The `-meta` of epidat 2023-07-14**, rendered again, would get the namespace and example of the entry, which fit
  only the later versions (the old version uses `data/epi/`); not rendered.

## Licences

- **Evidence** (0013): where the source states the licence publicly, `license.statement` (an archived capture; done
  for footprints, gnd, lc, geonames); where we have a written permission, the document. yivo, rujen and djh are CC0
  by written permission (yivo and djh publish only the beginning of each article), on paper only: scan them, keep the
  files privately, record a file name and SHA-256 in the catalogue (field still to define in 0013). Then the entries
  whose licence the source does not state publicly: stolpersteine, haskala, sosy, jre, hirsch-family, ubffm-persons;
  hhkeydocs: its terms of use put the articles and source interpretations under CC BY-NC-ND 4.0 but say nothing about
  the index of persons, places and organisations that the dataset holds; to ask the IGdJ.

## Catalogue, site and publication

- **Catalogue, open questions** (0013): DOIs for versions (would need a location that promises permanence, e.g.
  Zenodo; 0019); redirects for the paths of the old `archive.judaicalink.org/dumps/` (deleted 2026-10-16).
- **Site:** show the changelog and the derived contributors on the dataset pages (0013); the finder page
  `/dataindex/`; deploy (the state of 2026-10-16 is built, not deployed).
- **Process details:** which versions each dumps location offers; when to prune historical versions (0019).
- **The store and the inputs area** (0019, 0021): where they live in the long run (now `lokal/` on Kai's machine;
  later the platform VM?) and their backup. Inputs still outside the inputs area: what the labs VM backup holds
  (`../BACKUP-PLAN-2026-10-10.md`).
- **Labs VM:** keep the backups 2025-02-06 and 2025-12-19 of `labs:/data/dumps` offline and delete the rest there;
  nothing else on the VM is deleted before the backup in `../BACKUP-PLAN-2026-10-10.md` exists.

## Frankfurt

- Hand over the catalogue and its documentation.
- They can drop `cmtest`, `ep-supp`, `cm-tagme-supp`, `rujen-translation-supp` and `beacon-persons` (0015); their
  catalogue has `stolperstein.md` (now `stolpersteine`, 0017) and the `https` examples fixed in ours.
- Stable access URLs on data.judaicalink.org instead of web.judaicalink.org (0014); their catalogue pages could link
  to our finder; they adopt `<slug>/<version>/<path>` when they next take over files; their named graphs `data/<x>`
  become the dataset IRIs `datasets/<slug>` (0018); their loader expects `<slug>.meta.ttl` in one shared metadata
  graph (0006); their pubby takes the graph from `dataslug` (sometimes a namespace, e.g. `epi`).
- The BEACON `#TARGET` is `https://data.judaicalink.org/data/gnd/{ID}`, so DNB EntityFacts spreads our IRIs in the
  `https` form: ask for `http://`.
- The datasets of 2026-10-16: authority datasets and linksets (0029), kind `authority`.

## Other threads

- mannheim.judaicalink.org: the platform and its decisions are in `../judaicalink-mannheim/` (`docs/decisions/`, not
  on GitHub yet); engine comparison (QLever, Fuseki) in `../endpoints/`.
- Compact Memory full-text index for the portal (handover to Frankfurt): `../NOTES-2026-10-05-cm-fulltext-portal.md`.
- Further items of the data improvement plan: `../PLAN-2026-10-05-data-improvements.md`.

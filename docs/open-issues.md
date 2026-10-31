# Open issues

State 2026-10-19. Remove an item when it is solved (with a reference to the decision, version or commit); what was
solved is in the decisions, the changelogs of the versions and the git history.

## Identity and authority data (decisions 0029, 0032)

- **Below the quality threshold** (`catalog/link-quality.toml`): the VIAF numbers of footprints (0.94, lower bound
  0.87; judged one by one, the correct ones in ls-footprints-viaf, decision 0037) and the links of the withdrawn
  2014links stay in their datasets but join nothing.
- **ls-footprints-viaf** (0037): judged by an LLM only. To do: a sample checked by people, to know how good the
  judgements are.
- **GND duplicates kept apart:** hhkeydocs `person/gnd/118989316` (Yaʿaqov Emden) and `person/gnd/1089985185`
  (Jacob-Israel Hirschel, 1696–1776) are two GND records of one person (both VIAF 82152450).
- **Entity pages with `identity = linksets`** (the default since 195586e): groups joined only by GND numbers the GND
  no longer has (2026-10-16: about 90; gnd 2026-10-19 has 1,422 such numbers, mostly from ubffm-persons); the 5 direct links between our
  records (e.g. bhr → djh) need a small linkset.
- **Place rule:** GeoNames features of one place are joined through pairs of the same name within 25 km; the exact
  parents (`gn:parentADM2`–`4`, not yet in `geonames`) would be a better rule.
- **Link quality of the new units:** dbpedia (its Wikidata links) and the linksets (`jl:sameAs` of ls-gnd, …,
  ls-dbpedia) are not measured yet.
- **Made again on the new versions:** records-normalized and quality-annotations (they still read the versions of
  2026-10-12), judaicalink-terms; corrections-links reads gnd-persons (deprecated): check whether its corrections still
  apply.
- **Intermediate inputs of 2026-10-18** that no version uses: `web-caches/wikidata-2026-10-18*`,
  `web-caches/dbpedia-2026-10-18*`, `cascade/2026-10-18` (the first cascade attempts); to remove or keep.
- **gnd selection:** whether a broader selection (e.g. persons by GND area code, the rule of 2017, which `gnd` keeps
  off) belongs in the graph is a question of content, to be decided with a defined rule.
- **Wikidata property P13183** ("JudaicaLink person (GND) ID", 31,231 uses) has an `https` formatter URL, which spreads
  the `https` form of our IRIs: propose `http://data.judaicalink.org/data/gnd/$1` on Wikidata.

- **Impossible dates** in the normalised person dates (records-normalized and the sources): 1884-11-31, 1941-02-30,
  1912-06-31, 1921-06-31, 1902-02-29 (ep 2026-10-26-2 leaves them out); to fix where they are made.

- **Kinds: the real sources** (seen in the dataset cloud on web.judaicalink.org, 2026-10-26): `records` mixes the
  data contributed to us, the actual basis of the graph (encyclopedias, library and research data), with datasets
  that make resources of their own from our data or the authorities. geo-coordinates is a gazetteer derived in 2018
  (one place resource per place name, coordinates and GND numbers looked up in the GND; not reproducible; input of
  geo-enriched; its links to VIAF below the threshold); ubffm-persons is a source (the authors of the Judaica
  collection of UB Frankfurt) whose records were enriched with facts copied from the GND in 2019. To discuss: a kind
  for derived datasets that make resources (or a marker for the contributed sources); geo-coordinates as support or
  withdrawn (geo-enriched looking place names up in gnd and geonames directly; count first which entity pages and
  Atlas places only it gives); a new ubffm-persons that keeps what UB Frankfurt states and leaves the GND facts to
  `gnd`. Note: `kind` selects inputs in geo-enriched (`stable_inputs(kinds=…)`).

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
- The catalogue names ontology version 2025-11-27 (in `lokal/dumps-additions/ontology/2025-11-27/`, not published);
  `ontology-complements` redefines six terms of it (`belongsToIssue`, `belongsToJournal`, `birthLocationURI`,
  `deathLocationURI`, `gitCommit`, `gitWeb`): rebuild it and load both in an endpoint (with the platform, 0016).

## Data

- **Footprints** (decision 0034): versions footprints and record-classes 2026-10-26 (from the API; GeoNames ids
  confirmed by the API for 983 of 1,027 places), the cascade and the authority datasets and linksets of 2026-10-26.
  Link quality (`docs/reports/2026-10-26-link-quality-footprints.md`): GeoNames 100%, joins; VIAF 94% (lower bound
  87%), below the threshold; every VIAF link judged, 1,185 correct in ls-footprints-viaf (0037). Site pages (checked
  2026-10-26 in a browser; the site answers scripts with a challenge of its firewall): works and footprints have one
  (linked since footprints 2026-10-26-2), imprints, copies, persons and places none. To tell Footprints: the GeoNames ids and the
  digital objects of persons, imprints and copies in the API; the 16 places whose GeoNames id the API gives to
  another place record (second records, e.g. "Wien" and Vienna, "Vilna" and Vilnius), and the places of which it has
  two records (city and administrative unit; joined on the entity pages since 0036); the 140 VIAF numbers judged
  wrong (`ls-footprints-viaf-decisions.tsv.gz`: presses and firms linked to a person, fathers and sons, namesakes,
  libraries linked to their institution, clusters that mix persons), the Footprints persons that mix persons, and
  the 23 pairs of Footprints persons that share a VIAF cluster (ep 2026-10-26 refuses the second: duplicates or a wrong
  number).
- **Places without coordinates** (found by the Atlas showcase, jlma-atlas, 2026-10-25, ep 2026-10-19): the burial
  places of 18,650 Epidat people are Getty TGN IRIs (about 200 cemeteries; Bechhofen alone 2,195) without coordinates
  in any dataset; about 15,100 birth and 6,000 death places are Wikidata, GND and LC places outside the GeoNames and
  GND selections (or without coordinates there). Remedy: TGN (or the GeoNames of the cemeteries) and the places of
  people into the cascade. Also: an ep page "Hamburg" known only by TGN 7003673 (the state; 45 people), 98 people with
  a life of more than 110 years (e.g. born "1054", buried 1894).
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
- **occupations:** never a version; records-normalized uses 484 occupation IRIs that nothing describes (the portal
  links them from every person, and they answer 404); licence in
  the entry CC BY 4.0, the rest CC0.
- **jre:** the wiki's API is open; licence not stated.
- **nrwbibdjg** (2026-10-18) reaches about 2,250 of the about 7,500 titles (search by GND number only); two GND
  numbers look wrong in the source (121918424, 128477008).
- **yivo and rujen links:** with 2014links withdrawn (0033), about 1,400 records lost their only link to Wikipedia
  and GeoNames (places and persons by name); a new matching with disambiguation, as a linkset of its own.
- **hhkeydocs:** the documents, articles and bibliography of the site as records (later).
- **Fuseki warnings** (test load 2026-10-13): 13 impossible dates typed `xsd:date` (e.g. `1902-02-29`; 7 in
  records-normalized, 6 carried into ep), which records-normalized should not type as dates; 57 legacy `data/nli/`
  IRIs with characters not allowed in IRIs (47 in ls-nli-legacy, 1 in date-enriched).
- **Dates beyond xsd** (intervals "1663/1711", decades "182X", circa): EDTF (ISO 8601-2, the LC datatype
  `http://id.loc.gov/datatypes/edtf/EDTF`) as the normalised value where `xsd:date`/`gYear` cannot express it; with
  records-normalized and Footprints (which writes EDTF). HeidelTime for dates in running text (biographies) and
  OWL-Time (intervals, Hebrew calendar) noted, not planned.
- **YIVO subsections** (346 `skos:Concept`) are taken by ep as subjects; ep must read both yivo and record-classes.
- **DC Elements** (decision 0030): the generators of nli-records (`dc:creator`), hirsch-family and stolpersteine
  fail until they write `dcterms:`; with their next versions. hirsch-family states source documents (PDF, scans)
  as `dc:subject` strings of the person: IRIs with `rdfs:seeAlso`; stolpersteine the photo of the stone:
  `foaf:depiction`. Footprints: `dcterms:` in the new generator.
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
- **Logos in descriptions:** djh, rujen, rujen-translation and yivo show logos by paths relative to
  web.judaicalink.org (`/img/…`), which are missing wherever else the catalogue is shown (the portal): absolute URLs.
- **Site:** show the changelog and the derived contributors on the dataset pages (0013); the finder page
  `/dataindex/`; deploy (the state of 2026-10-16 is built, not deployed).
- **Process details:** which versions each dumps location offers; when to prune historical versions (0019).
- **The store and the inputs area** (0019, 0021): where they live in the long run (now `lokal/` on Kai's machine;
  later the platform VM?) and their backup. Inputs still outside the inputs area: what the labs VM backup holds
  (`../BACKUP-PLAN-2026-10-10.md`).
- **Labs VM:** keep the backups 2025-02-06 and 2025-12-19 of `labs:/data/dumps` offline and delete the rest there;
  nothing else on the VM is deleted before the backup in `../BACKUP-PLAN-2026-10-10.md` exists.

## Frankfurt

The portal branch `judaicalink-vibe` (GitLab `wagtail-common-base`; not merged or deployed yet; review notes for Aaron:
<https://claude.ai/artifact/F6dDpsHoCM7LVmHbosWaYM>) takes over what was listed here: the catalogue (identical to
`catalog/`, so `cmtest`, the `-supp` datasets, `beacon-persons` and `stolperstein.md` are gone and the examples are
`http`), the data finder link on the dataset pages, loading the stable versions from the store
(`<slug>/<version>/<path>`) into the graphs `datasets/<slug>` and `datasets/<slug>/meta` (`load_fuseki`, also the
authority datasets and linksets), data views instead of pubby (IRIs with capitals, dataset and ontology IRIs resolve;
data.judaicalink.org already forwards every path), the search indexes made from the graph and the CM full-text loader.
Left:

- Merge and deploy the branch; what is left before and after is in the review notes.
- BEACON: `generate_beacon` queries the `http` form of gndo and finds 6,112 of about 63,000 persons; its `#TARGET` is
  `https://data.judaicalink.org/data/gnd/{ID}`, so DNB EntityFacts spreads the `https` form of our IRIs. Fix on the
  branch, then ask the DNB to take the `http` target.
- Files: the dataset pages link them at `LABS_DUMPS_WEBROOT`; stable access URLs on data.judaicalink.org (`/dumps/`
  is served there) once Frankfurt has copied the store (0014).
- Compact Memory: copy the bundle `cm_meta_2026-10-05-v2` to Frankfurt for `load_cm_fulltext`.

## Other threads

- mannheim.judaicalink.org: the platform and its decisions are in `../judaicalink-mannheim/` (`docs/decisions/`, not
  on GitHub yet); engine comparison (QLever, Fuseki) in `../endpoints/`.
- Compact Memory full-text index for the portal (handover to Frankfurt): `../NOTES-2026-10-05-cm-fulltext-portal.md`;
  the loader is now `load_cm_fulltext` in the portal (judaicalink-vibe).
- Further items of the data improvement plan: `../PLAN-2026-10-05-data-improvements.md`.

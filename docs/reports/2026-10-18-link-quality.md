# Link quality

State 2026-10-18. The identity links of every dataset, per property and target source, measured on a random sample
(`jl sample-links`, seed 2026; 100 links per unit, all links of a unit with up to 150), on the stable versions and the
final runs of the authority datasets (gnd, lc, geonames, viaf, wikidata of 2026-10-18). Each link shows the facts of
the record that states it and of our record of the target (names, dates, places, classes, description). Each was
judged by an agent (six in parallel, one instruction): correct, wrong (different entities: a namesake, a family
member, a work instead of a person, a different place), or undecidable (no record of the target in our data, or too
few facts: a common name and nothing else). A place and its administrative unit of the same name count as correct.
Accuracy = correct / (correct + wrong), with its 95% interval (Wilson). The samples, evidence and verdicts are in
`lokal/work/link-quality-2026-10-18/` (`<unit>.jsonl`, `<unit>.verdicts.jsonl`).

Limits: 100 links tell a good source from a bad one, not 97% from 99%. Some units check little: the source copies the
target (cm-entities copies Wikidata's labels; ubffm-persons and geo-coordinates copy the GND; a Wikidata record and
its own article); some sources have only a name (ls-nli-legacy, interlinks, nrwbibdjg, dbp-wiki-geo-linking), so
common names stay undecidable. The verdicts are a model's judgement on the evidence shown, not checked by hand.

| Dataset | Property | Target | Links | Sample | Correct | Wrong | Undecidable | Accuracy (95% interval) |
|---|---|---|--:|--:|--:|--:|--:|--- |
| 2014links | sameAs | wikipedia-en | 1,403 | 100 | 86 | 9 | 5 | 91% (83%–95%) |
| 2014links | sameAs | geonames | 109 | 109 | 100 | 9 | 0 | 92% (85%–96%) |
| bhr | sameAs | gnd | 805 | 100 | 95 | 1 | 4 | 99% (94%–100%) |
| cm-entities | sameAs | viaf | 5,318 | 100 | 85 | 1 | 14 | 99% (94%–100%) |
| cm-entities | sameAs | gnd | 4,951 | 100 | 96 | 3 | 1 | 97% (91%–99%) |
| cm-entities | sameAs | wikidata | 4,848 | 100 | 99 | 1 | 0 | 99% (95%–100%) |
| cm-entities | isPrimaryTopicOf | wikipedia-de | 4,848 | 100 | 93 | 0 | 7 | 100% (96%–100%) |
| cm-entities | sameAs | geonames | 1,504 | 100 | 100 | 0 | 0 | 100% (96%–100%) |
| dbp-wiki-geo-linking | sameAs | wikipedia-en | 5,710 | 100 | 71 | 1 | 28 | 99% (93%–100%) |
| dbp-wiki-geo-linking | sameAs | wikipedia-de | 46 | 46 | 34 | 1 | 11 | 97% (85%–99%) |
| dbpedia-persons | sameAs | wikidata | 6,954 | 100 | 98 | 0 | 2 | 100% (96%–100%) |
| dbpedia-persons | sameAs | wikipedia-en | 6,951 | 100 | 94 | 0 | 6 | 100% (96%–100%) |
| dbpedia-persons | gndIdentifier | gnd | 3,626 | 100 | 98 | 1 | 1 | 99% (94%–100%) |
| dbpedia-persons | sameAs | gnd | 3,596 | 100 | 99 | 0 | 1 | 100% (96%–100%) |
| dbpedia-persons | sameAs | wikipedia-de | 3,505 | 100 | 95 | 3 | 2 | 97% (91%–99%) |
| dbpedia-persons | sameAs | viaf | 3,146 | 100 | 90 | 0 | 10 | 100% (96%–100%) |
| epidat | sameAs | gnd | 77 | 77 | 70 | 3 | 4 | 96% (89%–99%) |
| footprints | sameAs | viaf | 1,478 | 100 | 78 | 10 | 12 | 89% (80%–94%) |
| footprints | sameAs | gnd | 812 | 100 | 88 | 8 | 4 | 92% (84%–96%) |
| footprints | gndIdentifier | gnd | 139 | 139 | 68 | 66 | 5 | 51% (42%–59%) |
| footprints | sameAs | lc-names | 1 | 1 | 0 | 1 | 0 | 0% (0%–79%) |
| gba | sameAs | gnd | 10 | 10 | 10 | 0 | 0 | 100% (72%–100%) |
| gba | gndIdentifier | gnd | 10 | 10 | 10 | 0 | 0 | 100% (72%–100%) |
| geo-coordinates | gndIdentifier | gnd | 2,705 | 100 | 100 | 0 | 0 | 100% (96%–100%) |
| geo-coordinates | sameAs | viaf | 2,701 | 100 | 67 | 4 | 29 | 94% (86%–98%) |
| geo-coordinates | sameAs | geonames | 2,643 | 100 | 97 | 0 | 3 | 100% (96%–100%) |
| geo-coordinates | sameAs | gnd | 2,513 | 100 | 100 | 0 | 0 | 100% (96%–100%) |
| geonames | isPrimaryTopicOf | wikipedia-en | 6,762 | 100 | 89 | 0 | 11 | 100% (96%–100%) |
| geonames | sameAs | wikidata | 2,660 | 100 | 95 | 0 | 5 | 100% (96%–100%) |
| geonames | isPrimaryTopicOf | wikipedia-de | 69 | 69 | 55 | 1 | 13 | 98% (91%–100%) |
| gnd | sameAs | viaf | 68,173 | 100 | 92 | 0 | 8 | 100% (96%–100%) |
| gnd | sameAs | wikidata | 60,923 | 100 | 98 | 0 | 2 | 100% (96%–100%) |
| gnd | sameAs | lc-names | 56,177 | 100 | 92 | 2 | 6 | 98% (93%–99%) |
| gnd | sameAs | wikipedia-en | 38,212 | 100 | 97 | 2 | 1 | 98% (93%–99%) |
| gnd | sameAs | wikipedia-de | 27,977 | 100 | 99 | 0 | 1 | 100% (96%–100%) |
| gnd | page | wikipedia-de | 27,956 | 100 | 96 | 0 | 4 | 100% (96%–100%) |
| gnd | sameAs | geonames | 4,358 | 100 | 94 | 1 | 5 | 99% (94%–100%) |
| gnd | exactMatch | lc-names | 1 | 1 | 1 | 0 | 0 | 100% (21%–100%) |
| haskala | sameAs | viaf | 581 | 100 | 18 | 31 | 51 | 37% (25%–51%) |
| haskala | sameAs | gnd | 157 | 100 | 98 | 0 | 2 | 100% (96%–100%) |
| haskala | gndIdentifier | gnd | 32 | 32 | 32 | 0 | 0 | 100% (89%–100%) |
| hhkeydocs | sameAs | gnd | 2,274 | 100 | 96 | 0 | 4 | 100% (96%–100%) |
| hhkeydocs | gndIdentifier | gnd | 1,903 | 100 | 99 | 1 | 0 | 99% (95%–100%) |
| interlinks | sameAs | gnd | 738 | 100 | 99 | 0 | 1 | 100% (96%–100%) |
| interlinks | sameAs | wikidata | 238 | 100 | 89 | 0 | 11 | 100% (96%–100%) |
| interlinks | sameAs | wikipedia-en | 238 | 100 | 94 | 1 | 5 | 99% (94%–100%) |
| interlinks | sameAs | wikipedia-de | 173 | 100 | 91 | 0 | 9 | 100% (96%–100%) |
| interlinks | sameAs | viaf | 121 | 121 | 109 | 0 | 12 | 100% (97%–100%) |
| jre | sameAs | viaf | 313 | 100 | 77 | 2 | 21 | 97% (91%–99%) |
| lc | hasExactExternalAuthority | gnd | 201 | 100 | 100 | 0 | 0 | 100% (96%–100%) |
| lc | sameAs | gnd | 201 | 100 | 98 | 0 | 2 | 100% (96%–100%) |
| lc | hasExactExternalAuthority | viaf | 2 | 2 | 2 | 0 | 0 | 100% (34%–100%) |
| lc | hasExactExternalAuthority | wikidata | 2 | 2 | 2 | 0 | 0 | 100% (34%–100%) |
| lc | sameAs | viaf | 2 | 2 | 2 | 0 | 0 | 100% (34%–100%) |
| lc | sameAs | wikidata | 2 | 2 | 2 | 0 | 0 | 100% (34%–100%) |
| lc | hasExactExternalAuthority | geonames | 1 | 1 | 1 | 0 | 0 | 100% (21%–100%) |
| ls-nli-legacy | sameAs | viaf | 177,815 | 100 | 55 | 0 | 45 | 100% (93%–100%) |
| ls-nli-legacy | sameAs | lc-names | 54,056 | 100 | 74 | 0 | 26 | 100% (95%–100%) |
| nli-records | sameAs | viaf | 182,552 | 100 | 67 | 0 | 33 | 100% (95%–100%) |
| nli-records | sameAs | lc-names | 54,117 | 100 | 95 | 1 | 4 | 99% (94%–100%) |
| nrwbibdjg | sameAs | gnd | 806 | 100 | 69 | 0 | 31 | 100% (95%–100%) |
| ubffm-persons | sameAs | gnd | 6,568 | 100 | 76 | 0 | 24 | 100% (95%–100%) |
| ubffm-persons | gndIdentifier | gnd | 5,018 | 100 | 71 | 0 | 29 | 100% (95%–100%) |
| ubffm-persons | sameAs | viaf | 3,856 | 100 | 88 | 0 | 12 | 100% (96%–100%) |
| ubffm-persons | sameAs | wikipedia-en | 628 | 100 | 93 | 0 | 7 | 100% (96%–100%) |
| viaf | sameAs | lc-names | 89,121 | 100 | 95 | 0 | 5 | 100% (96%–100%) |
| viaf | sameAs | gnd | 66,169 | 100 | 96 | 0 | 4 | 100% (96%–100%) |
| viaf | sameAs | wikidata | 59,038 | 100 | 95 | 0 | 5 | 100% (96%–100%) |
| viaf | sameAs | wikipedia-en | 31,266 | 100 | 93 | 2 | 5 | 98% (93%–99%) |
| wikidata | P214 | viaf | 88,706 | 100 | 90 | 3 | 7 | 97% (91%–99%) |
| wikidata | P227 | gnd | 61,409 | 100 | 98 | 0 | 2 | 100% (96%–100%) |
| wikidata | P244 | lc-names | 60,845 | 100 | 89 | 3 | 8 | 97% (91%–99%) |
| wikidata | isPrimaryTopicOf | wikipedia-en | 38,451 | 100 | 100 | 0 | 0 | 100% (96%–100%) |
| wikidata | isPrimaryTopicOf | wikipedia-de | 34,334 | 100 | 100 | 0 | 0 | 100% (96%–100%) |
| wikidata | P1566 | geonames | 8,296 | 100 | 97 | 0 | 3 | 100% (96%–100%) |

## Systematic problems

- **haskala → VIAF (37%):** matched by name. Nine persons "Zvi Hirsch" link the cluster of the work "Derishat
  Tsiyon"; organisations (Eschwege → Sannyas Verlag); the son named in a patronymic; unrelated modern people
  (Levin Salomon → Vered Levin-Salomon, born 1978). haskala → GND is clean (100%).
- **footprints → GND by `gndIdentifier` (51%):** places matched to any GND record with the label, without type or
  country: Spain → Port of Spain, Poland → Poland (Md.), Halle → a synagogue in Halle. Its persons (`owl:sameAs` → GND
  92%, → VIAF 89%): family members (Adolph Lewisohn → his son Sam), namesakes (Isaac Aboab the elder → Aboab da
  Fonseca), imprints naming several printers linked to one of them.
- **2014links (91%, 92%):** matched by name: YIVO's Galicia → Galicia (Spain), Brest → Brest (France); disambiguation
  pages; YIVO article sections linked to the place (Assimilation/Poland → Poland).
- **VIAF clusters that mix entities** (seen through several units): Japheth ben Ali with his son Levi ben Japheth,
  Hermann Baratz with his son Léon, Chalkis with Chalcis (Aeolis), the book of Nehemiah with 4 Ezra; a VIAF
  link NICE (the institute) → Nizza (Turin Metro).
- **Wikidata:** a person given the LC number of one of her works (Ilana Pardes); single wrong numbers.
- **cm-entities → GND:** links to pseudonym records instead of the person (Manfred Hausmann → "Tsuno, Toyotama").
- **Smaller ones:** epidat links a gravestone to a family record; geo-coordinates → VIAF links a town to its
  concentration camp or city council; gnd → Wikipedia links Slonim to a disambiguation page.

# Properties and classes in use

State 2026-10-17: the stable versions of the catalogue (40 datasets; datasets replaced by another entry left out), data files only (no `-meta`); the ontology and `judaicalink-terms` left out. `compact-memory-supp` and `corrections-links` have no RDF data. Runs that are not versions yet (gba, nrwbibdjg, rujen, wikidata, linksets) are not counted.

**Statements:** triples with the property; for a class, `rdf:type` triples with it. **Datasets:** how many datasets use it (all are listed when four or fewer). **Ontology:** described in ontology 2026-10-17 (`yes`; `yes (other form)`: described in its canonical form, e.g. `https` for GND terms, docs/iri-forms.md; `deprecated`; `no`).

542 properties and 69 classes, 23,330,531 statements.

## Classes

| Term | Statements | Datasets | Ontology | Used by |
|---|--:|--:|---|---|
| `jl:Page` | 846,499 | 1 | yes | compact-memory |
| `jl:Reference` | 749,446 | 1 | yes | cm-tagme |
| `foaf:Person` | 677,827 | 22 | yes |  |
| `jl:EntityPage` | 310,214 | 1 | deprecated | ep |
| `madsrdf:Authority` | 79,683 | 1 | no | lc |
| `madsrdf:RWO` | 79,468 | 1 | no | lc |
| `bf:Person` | 77,549 | 1 | no | lc |
| `madsrdf:PersonalName` | 77,549 | 1 | no | lc |
| `schema:PublicationIssue` | 46,620 | 1 | no | compact-memory |
| `gndo:DifferentiatedPerson` | 38,242 | 1 | no | gnd |
| `jl:Place` | 34,631 | 9 | deprecated |  |
| `schema:Article` | 24,463 | 1 | no | compact-memory |
| `skos:Concept` | 17,165 | 5 | yes |  |
| `jl:Work` | 10,017 | 6 | deprecated |  |
| `jl:Person` | 8,283 | 1 | no | rujen |
| `jl:CorpusPresence` | 5,445 | 1 | yes | cm-entities |
| `dqv:QualityAnnotation` | 5,026 | 2 | yes | ls-nli-legacy, quality-annotations |
| `oa:Annotation` | 5,026 | 2 | yes | ls-nli-legacy, quality-annotations |
| `gndo-http:Work` | 4,830 | 2 | yes (other form) | footprints, nrwbibdjg |
| `gndo:TerritorialCorporateBodyOrAdministrativeUnit` | 3,121 | 1 | no | gnd |
| `schema:PublicationVolume` | 2,741 | 1 | no | compact-memory |
| `foaf:Organization` | 2,170 | 6 | yes |  |
| `haskala:Person` | 1,980 | 1 | no | haskala |
| `haskala:Mention` | 1,867 | 1 | no | haskala |
| `madsrdf:Geographic` | 1,495 | 1 | no | lc |
| `madsrdf-old:Geographic` | 1,495 | 1 | no | lc |
| `gndo-http:PlaceOrGeographicName` | 1,263 | 2 | yes (other form) | footprints, hhkeydocs |
| `jl:Subject` | 1,186 | 2 | deprecated | ep, record-classes |
| `haskala:Production` | 667 | 1 | no | haskala |
| `gndo:CorporateBody` | 582 | 1 | no | gnd |
| `haskala:Book` | 525 | 1 | no | haskala |
| `bf:Organization` | 422 | 1 | no | lc |
| `madsrdf:CorporateName` | 422 | 1 | no | lc |
| `schema:Periodical` | 336 | 1 | no | compact-memory |
| `haskala:Edition` | 327 | 1 | no | haskala |
| `haskala:Preface` | 272 | 1 | no | haskala |
| `rdf:Property` | 227 | 2 | no | bhr, haskala |
| `haskala:FieldInstance` | 218 | 1 | no | haskala |
| `madsrdf:NameTitle` | 213 | 1 | no | lc |
| `gndo:OrganOfCorporateBody` | 97 | 1 | no | gnd |
| `gndo:MemberState` | 38 | 1 | no | gnd |
| `gndo:RoyalOrMemberOfARoyalHouse` | 38 | 1 | no | gnd |
| `gndo:Company` | 33 | 1 | no | gnd |
| `gndo:Country` | 26 | 1 | no | gnd |
| `haskala:Section` | 22 | 1 | no | haskala |
| `skos:ConceptScheme` | 21 | 2 | no | haskala, judaicalink-vocabulary |
| `gndo:BuildingOrMemorial` | 20 | 1 | no | gnd |
| `haskala:Translation` | 19 | 1 | no | haskala |
| `gndo:AdministrativeUnit` | 19 | 1 | no | gnd |
| `gndo:ReligiousCorporateBody` | 16 | 1 | no | gnd |
| `gndo:CollectivePseudonym` | 11 | 1 | no | gnd |
| `gndo:NaturalGeographicUnit` | 10 | 1 | no | gnd |
| `gndo:SubjectHeadingSensoStricto` | 10 | 1 | no | gnd |
| `rdfs:Class` | 9 | 1 | no | haskala |
| `gndo:PlaceOrGeographicName` | 9 | 1 | yes | gnd |
| `prov:Person` | 8 | 1 | no | judaicalink-agents |
| `gndo:MusicalCorporateBody` | 8 | 1 | no | gnd |
| `gndo:LiteraryOrLegendaryCharacter` | 5 | 1 | no | gnd |
| `gndo:ReligiousTerritory` | 3 | 1 | no | gnd |
| `gndo:Work` | 3 | 1 | yes | gnd |
| `bf:Meeting` | 2 | 1 | no | lc |
| `madsrdf:ConferenceName` | 2 | 1 | no | lc |
| `madsrdf:Title` | 2 | 1 | no | lc |
| `gndo:NameOfSmallGeographicUnitLyingWithinAnotherGeographicUnit` | 2 | 1 | no | gnd |
| `gndo:ReligiousAdministrativeUnit` | 2 | 1 | no | gnd |
| `schema:Collection` | 1 | 1 | no | compact-memory |
| `prov:SoftwareAgent` | 1 | 1 | no | judaicalink-agents |
| `gndo:Family` | 1 | 1 | no | gnd |
| `gndo:HistoricSingleEventOrEra` | 1 | 1 | no | gnd |

## Properties

| Term | Statements | Datasets | Ontology | Used by |
|---|--:|--:|---|---|
| `rdf:type` | 3,119,951 | 31 | yes |  |
| `owl:sameAs` | 1,862,723 | 22 | yes |  |
| `jl:retiredDate` | 1,454,491 | 1 | yes | ep |
| `skos:altLabel` | 1,283,204 | 13 | yes |  |
| `skos:prefLabel` | 1,152,252 | 25 | yes |  |
| `jl:belongsToIssue` | 846,499 | 1 | yes | compact-memory |
| `jl:hasVisualRepresentation` | 846,499 | 1 | yes | compact-memory |
| `jl:ocrKnownWordShare` | 846,499 | 1 | yes | cm-ocr-quality |
| `jl:pageSequence` | 846,499 | 1 | yes | compact-memory |
| `jl:hasEnd` | 749,446 | 1 | yes | cm-tagme |
| `jl:hasLinkProb` | 749,446 | 1 | yes | cm-tagme |
| `jl:hasReference` | 749,446 | 1 | yes | cm-tagme |
| `jl:hasRho` | 749,446 | 1 | yes | cm-tagme |
| `jl:hasSpot` | 749,446 | 1 | yes | cm-tagme |
| `jl:hasStart` | 749,446 | 1 | yes | cm-tagme |
| `jl:isOnPage` | 749,446 | 1 | yes | cm-tagme |
| `rdfs:label` | 658,704 | 5 | yes |  |
| `jl:represents` | 332,875 | 1 | deprecated | ep |
| `jl:birthDate` | 220,375 | 15 | yes |  |
| `foaf:gender` | 196,822 | 3 | yes | epidat, hhkeydocs, nli-records |
| `jl:deathDate` | 189,377 | 15 | yes |  |
| `jl:birthDateNormalized` | 186,405 | 2 | yes | ep, records-normalized |
| `dcterms:source` | 185,189 | 1 | no | nli-records |
| `prov:wasDerivedFrom` | 185,189 | 1 | yes | ls-nli-legacy |
| `jl:deathDateNormalized` | 169,893 | 2 | yes | ep, records-normalized |
| `madsrdf:isMemberOfMADSCollection` | 159,692 | 1 | no | lc |
| `gndo:variantNameForThePerson` | 142,317 | 1 | no | gnd |
| `jl:deathLocation` | 126,773 | 13 | yes |  |
| `jl:deathLocationURI` | 126,307 | 8 | yes |  |
| `bflc:marcKey` | 121,048 | 1 | no | lc |
| `madsrdf:authoritativeLabel` | 121,048 | 1 | no | lc |
| `foaf:page` | 106,272 | 2 | no | compact-memory, gnd |
| `jl:hasAbstract` | 104,204 | 11 | yes |  |
| `skos:note` | 97,014 | 1 | no | nli-records |
| `jl:birthLocation` | 94,814 | 12 | yes |  |
| `dcterms:type` | 89,672 | 3 | yes | compact-memory, ls-nli-legacy, quality-annotations |
| `jl:describedAt` | 89,229 | 11 | yes |  |
| `dcterms:isPartOf` | 89,034 | 2 | no | compact-memory, haskala |
| `jl:belongsToJournal` | 88,691 | 1 | yes | compact-memory |
| `dcterms:date` | 88,545 | 2 | no | compact-memory, nli-records |
| `gndo:oldAuthorityNumber` | 85,431 | 1 | no | gnd |
| `jl:birthLocationURI` | 82,849 | 7 | yes |  |
| `rdfs:seeAlso` | 82,448 | 3 | yes | compact-memory, ep, epidat |
| `madsrdf:hasExactExternalAuthority` | 80,335 | 1 | no | lc |
| `identifiers:lccn` | 79,683 | 1 | no | lc |
| `madsrdf:isMemberOfMADSScheme` | 79,683 | 1 | no | lc |
| `madsrdf:editorialNote` | 71,490 | 1 | no | lc |
| `dcterms:isReplacedBy` | 64,499 | 6 | yes |  |
| `jl:occupation` | 63,621 | 7 | yes |  |
| `skos:related` | 59,592 | 3 | yes | djh, rujen, yivo |
| `foaf:name` | 53,130 | 6 | yes |  |
| `gndo:geographicAreaCode` | 52,500 | 1 | no | gnd |
| `gndo:publication` | 49,724 | 1 | no | gnd |
| `jl:occupationURI` | 43,747 | 4 | yes | bhr, ep, records-normalized, sosy |
| `gndo:gndIdentifier` | 42,207 | 1 | yes | gnd |
| `gndo:gender` | 38,296 | 1 | no | gnd |
| `gndo:preferredNameForThePerson` | 38,296 | 1 | no | gnd |
| `madsrdf:occupation` | 34,499 | 1 | no | lc |
| `gndo:dateOfBirth` | 33,438 | 1 | no | gnd |
| `dcterms:identifier` | 31,588 | 4 | yes | compact-memory, haskala, rujen, ubffm-persons |
| `gndo:biographicalOrHistoricalInformation` | 31,028 | 1 | no | gnd |
| `madsrdf:birthDate` | 28,161 | 1 | no | lc |
| `gndo:gndSubjectCategory` | 23,321 | 1 | no | gnd |
| `madsrdf:fieldOfActivity` | 21,307 | 1 | no | lc |
| `madsrdf:associatedLanguage` | 20,383 | 1 | no | lc |
| `bhrv:literature` | 17,245 | 1 | no | bhr |
| `gndo:placeOfBirth` | 16,954 | 1 | no | gnd |
| `gndo:dateOfDeath` | 16,784 | 1 | no | gnd |
| `gndo:placeOfActivity` | 16,072 | 1 | no | gnd |
| `jl:hasPublication` | 15,190 | 2 | yes | bhr, sosy |
| `bhrv:publication` | 15,156 | 1 | no | bhr |
| `madsrdf:deathDate` | 14,941 | 1 | no | lc |
| `jl:mergeDate` | 14,917 | 1 | yes | ep |
| `jl:mergedInto` | 14,917 | 1 | yes | ep |
| `geosparql:asWKT` | 14,912 | 7 | yes |  |
| `gndo-http:gndIdentifier` | 14,242 | 8 | yes (other form) |  |
| `gndo:affiliation` | 13,517 | 1 | no | gnd |
| `gndo-http:formerOwner` | 12,801 | 1 | no | footprints |
| `madsrdf:birthPlace` | 11,752 | 1 | no | lc |
| `foaf:isPrimaryTopicOf` | 11,474 | 2 | yes | cm-entities, geonames |
| `gndo:familialRelationship` | 10,139 | 1 | no | gnd |
| `gndo:variantNameForThePlaceOrGeographicName` | 9,414 | 1 | no | gnd |
| `gndo:placeOfDeath` | 8,818 | 1 | no | gnd |
| `gndo:academicDegree` | 8,551 | 1 | no | gnd |
| `madsrdf:associatedLocale` | 8,277 | 1 | no | lc |
| `dcterms:subject` | 6,829 | 1 | yes | dbpedia-persons |
| `schema:parent` | 6,685 | 1 | no | epidat |
| `gn-http:featureClass` | 6,622 | 1 | no | geonames |
| `gn-http:featureCode` | 6,622 | 1 | no | geonames |
| `gn-http:countryCode` | 6,618 | 1 | no | geonames |
| `gn-http:parentADM1` | 6,459 | 1 | no | geonames |
| `gn-http:population` | 5,773 | 1 | no | geonames |
| `schema:spouse` | 5,702 | 1 | no | epidat |
| `jl:corpus` | 5,445 | 1 | yes | cm-entities |
| `jl:entity` | 5,445 | 1 | yes | cm-entities |
| `jl:mentionCount` | 5,445 | 1 | yes | cm-entities |
| `jl:pageCount` | 5,445 | 1 | yes | cm-entities |
| `jl:firstMentionYear` | 5,443 | 1 | yes | cm-entities |
| `jl:journalCount` | 5,443 | 1 | yes | cm-entities |
| `jl:lastMentionYear` | 5,443 | 1 | yes | cm-entities |
| `jl:mostFrequentJournal` | 5,443 | 1 | yes | cm-entities |
| `gndo-http:author` | 5,256 | 2 | yes (other form) | footprints, nrwbibdjg |
| `gndo-http:associatedPlace` | 5,140 | 1 | no | footprints |
| `oa:bodyValue` | 5,026 | 2 | yes | ls-nli-legacy, quality-annotations |
| `oa:hasTarget` | 5,026 | 2 | yes | ls-nli-legacy, quality-annotations |
| `oa:motivatedBy` | 5,026 | 2 | yes | ls-nli-legacy, quality-annotations |
| `dc:title` | 4,846 | 2 | yes | footprints, nrwbibdjg |
| `gndo-http:owner` | 4,765 | 1 | no | footprints |
| `gndo:originalScriptNameOfThePerson` | 4,178 | 1 | no | gnd |
| `gndo-http:dateOfPublication` | 4,140 | 1 | no | footprints |
| `gndo:languageCode` | 4,122 | 1 | no | gnd |
| `dcterms:title` | 3,960 | 2 | no | compact-memory, nli-records |
| `gndo:fieldOfStudy` | 3,862 | 1 | no | gnd |
| `jl:splitInto` | 3,460 | 1 | yes | ep |
| `gndo:variantNameForTheCorporateBody` | 3,381 | 1 | no | gnd |
| `gndo:preferredNameForThePlaceOrGeographicName` | 3,160 | 1 | no | gnd |
| `haskala:book` | 3,152 | 1 | no | haskala |
| `dcterms:created` | 3,135 | 3 | yes | gba, nrwbibdjg, sosy |
| `schema:sibling` | 2,750 | 1 | no | epidat |
| `dcterms:bibliographicCitation` | 2,703 | 1 | no | bhr |
| `agrelon:hasChild` | 2,451 | 1 | no | gnd |
| `gndo:periodOfActivity` | 2,451 | 1 | no | gnd |
| `dc:publisher` | 2,407 | 1 | no | footprints |
| `gndo:professionOrOccupationAsLiteral` | 2,209 | 1 | no | gnd |
| `gndo:homepage` | 2,163 | 1 | no | gnd |
| `agrelon:hasParent` | 2,031 | 1 | no | gnd |
| `identifiers:local` | 2,022 | 1 | no | lc |
| `gndo-http:language` | 1,901 | 1 | no | footprints |
| `haskala:mentionee_description` | 1,875 | 1 | no | haskala |
| `haskala:mentionee` | 1,867 | 1 | no | haskala |
| `jl:title` | 1,798 | 1 | yes | yivo |
| `jl:referTo` | 1,795 | 1 | yes | rujen |
| `dcterms:creator` | 1,788 | 1 | no | nli-records |
| `madsrdf:entityDescriptor` | 1,763 | 1 | no | lc |
| `madsrdf:hasRelatedAuthority` | 1,733 | 1 | no | lc |
| `madsrdf:classification` | 1,670 | 1 | no | lc |
| `agrelon:hasSpouse` | 1,660 | 1 | no | gnd |
| `gndo-http:oldAuthorityNumber` | 1,639 | 1 | no | nrwbibdjg |
| `haskala:german_name` | 1,616 | 1 | no | haskala |
| `bhrv:document` | 1,590 | 1 | no | bhr |
| `haskala:hebrew_name` | 1,580 | 1 | no | haskala |
| `gndo-http:forename` | 1,505 | 1 | no | nrwbibdjg |
| `jl:splitDate` | 1,492 | 1 | yes | ep |
| `madsrdf:code` | 1,492 | 1 | no | lc |
| `gndo:placeOfBirthAsLiteral` | 1,410 | 1 | no | gnd |
| `gndo:acquaintanceshipOrFriendship` | 1,379 | 1 | no | gnd |
| `agrelon:hasSibling` | 1,375 | 1 | no | gnd |
| `haskala:mentionee_city` | 1,309 | 1 | no | haskala |
| `gndo-http:hierarchicalSuperiorOfPlaceOrGeographicName` | 1,244 | 2 | yes (other form) | footprints, hhkeydocs |
| `gndo-http:surname` | 1,242 | 1 | no | nrwbibdjg |
| `madsrdf:hasReciprocalAuthority` | 1,229 | 1 | no | lc |
| `foaf:givenName` | 1,187 | 1 | no | hhkeydocs |
| `foaf:familyName` | 1,161 | 1 | no | hhkeydocs |
| `gndo:placeOfExile` | 1,114 | 1 | no | gnd |
| `haskala:topic` | 1,106 | 1 | no | haskala |
| `haskala:weight` | 1,049 | 1 | no | haskala |
| `haskala:fonts` | 1,048 | 1 | no | haskala |
| `gndo-http:variantNameEntityForThePerson` | 1,045 | 1 | no | nrwbibdjg |
| `bhrv:image` | 1,043 | 1 | no | bhr |
| `gndo-http:variantNameForThePerson` | 1,035 | 1 | no | nrwbibdjg |
| `madsrdf:activityStartDate` | 998 | 1 | no | lc |
| `haskala:role` | 976 | 1 | no | haskala |
| `madsrdf:see` | 961 | 1 | no | lc |
| `gndo:dateOfEstablishment` | 953 | 1 | yes | gnd |
| `gndo:relatedDdcWithDegreeOfDeterminacy2` | 883 | 1 | no | gnd |
| `skos:inScheme` | 827 | 2 | no | haskala, judaicalink-vocabulary |
| `gndo-http:descriptionLevel` | 805 | 1 | no | nrwbibdjg |
| `gndo:broaderTermInstantial` | 791 | 1 | no | gnd |
| `gndo-http:preferredNameEntityForThePerson` | 790 | 1 | no | nrwbibdjg |
| `gndo-http:preferredNameForThePerson` | 790 | 1 | no | nrwbibdjg |
| `madsrdf:note` | 757 | 1 | no | lc |
| `gndo:preferredNameForTheCorporateBody` | 736 | 1 | no | gnd |
| `gndo:usingInstructions` | 736 | 1 | no | gnd |
| `gndo-http:geographicAreaCode` | 698 | 1 | no | nrwbibdjg |
| `gndo-http:printer` | 698 | 1 | no | footprints |
| `gndo:dateOfTermination` | 675 | 1 | yes | gnd |
| `gndo:professionalRelationship` | 672 | 1 | no | gnd |
| `haskala:producer` | 667 | 1 | no | haskala |
| `haskala:target_audience` | 661 | 1 | no | haskala |
| `haskala:language` | 649 | 1 | no | haskala |
| `gndo:placeOfBusiness` | 639 | 1 | no | gnd |
| `gndo:pseudonym` | 630 | 1 | no | gnd |
| `haskala:main_textual_models` | 624 | 1 | no | haskala |
| `madsrdf:useFor` | 598 | 1 | no | lc |
| `bhrv:manuscript` | 586 | 1 | no | bhr |
| `haskala:viaf_id` | 583 | 1 | no | haskala |
| `gndo:dateOfBirthAndDeath` | 569 | 1 | no | gnd |
| `gndo-http:gender` | 564 | 1 | no | nrwbibdjg |
| `gndo-http:professionOrOccupation` | 526 | 1 | no | nrwbibdjg |
| `haskala:full_title` | 525 | 1 | no | haskala |
| `haskala:typography` | 519 | 1 | no | haskala |
| `gndo-http:dateOfBirth` | 517 | 1 | no | nrwbibdjg |
| `gndo:playedInstrument` | 514 | 1 | no | gnd |
| `haskala:pages_number` | 503 | 1 | no | haskala |
| `bhrv:epigraphy` | 499 | 1 | no | bhr |
| `gndo-http:gndSubjectCategory` | 498 | 1 | no | nrwbibdjg |
| `haskala:languages_number` | 479 | 1 | no | haskala |
| `gndo:spatialAreaOfActivity` | 479 | 1 | no | gnd |
| `dc:subject` | 476 | 2 | yes | hirsch-family, stolpersteine |
| `haskala:preface` | 474 | 1 | no | haskala |
| `haskala:epilogue` | 469 | 1 | no | haskala |
| `haskala:table_of_conten` | 467 | 1 | no | haskala |
| `gndo:precedingPlaceOrGeographicName` | 458 | 1 | no | gnd |
| `haskala:alignment` | 454 | 1 | no | haskala |
| `haskala:format_of_publication_date` | 443 | 1 | no | haskala |
| `haskala:illustrations_diagrams` | 439 | 1 | no | haskala |
| `gndo-http:biographicalOrHistoricalInformation` | 436 | 1 | no | nrwbibdjg |
| `haskala:publication_place` | 435 | 1 | no | haskala |
| `haskala:copy_of_book_used` | 427 | 1 | no | haskala |
| `haskala:rabbinical_approbations` | 426 | 1 | no | haskala |
| `haskala:references_notes` | 426 | 1 | no | haskala |
| `jl:publicationPeriod` | 426 | 1 | yes | compact-memory |
| `haskala:secondary_textual_models` | 421 | 1 | no | haskala |
| `haskala:subscribers` | 421 | 1 | no | haskala |
| `haskala:dedications` | 414 | 1 | no | haskala |
| `haskala:title_in_latin_characters` | 414 | 1 | no | haskala |
| `gndo-http:dateOfEstablishment` | 412 | 2 | yes (other form) | hhkeydocs, nrwbibdjg |
| `gndo-http:publication` | 412 | 1 | no | nrwbibdjg |
| `haskala:publication_year_in_book` | 411 | 1 | no | haskala |
| `haskala:recommendations` | 411 | 1 | no | haskala |
| `haskala:publisher_name` | 406 | 1 | no | haskala |
| `haskala:subscription_appeal` | 406 | 1 | no | haskala |
| `haskala:printers` | 403 | 1 | no | haskala |
| `haskala:thanks` | 403 | 1 | no | haskala |
| `gndo:affiliationAsLiteral` | 402 | 1 | no | gnd |
| `haskala:funders` | 401 | 1 | no | haskala |
| `haskala:sellers` | 399 | 1 | no | haskala |
| `haskala:proofreaders` | 398 | 1 | no | haskala |
| `haskala:personal_address` | 395 | 1 | no | haskala |
| `gndo:succeedingPlaceOrGeographicName` | 394 | 1 | no | gnd |
| `skos:broader` | 392 | 3 | yes | haskala, judaicalink-vocabulary, yivo |
| `haskala:huji_library_id` | 384 | 1 | no | haskala |
| `gndo:relatedWork` | 360 | 1 | no | gnd |
| `skos:narrower` | 350 | 2 | yes | judaicalink-vocabulary, yivo |
| `dcterms:language` | 347 | 1 | no | compact-memory |
| `gndo:relatedDdcWithDegreeOfDeterminacy4` | 346 | 1 | no | gnd |
| `gndo:placeOfDeathAsLiteral` | 343 | 1 | no | gnd |
| `jl:indexedPages` | 336 | 1 | yes | compact-memory |
| `gndo-http:placeOfActivity` | 332 | 1 | no | nrwbibdjg |
| `gndo:abbreviatedNameForTheCorporateBody` | 325 | 1 | no | gnd |
| `gndo-http:placeOfBirth` | 324 | 1 | no | nrwbibdjg |
| `jl:placeOfPublication` | 324 | 1 | yes | compact-memory |
| `haskala:presented_as_original` | 323 | 1 | no | haskala |
| `haskala:edition_year` | 321 | 1 | no | haskala |
| `haskala:edition_city` | 316 | 1 | no | haskala |
| `gndo-http:affiliation` | 313 | 1 | no | nrwbibdjg |
| `jl:meanOcrKnownWordShare` | 309 | 1 | yes | cm-ocr-quality |
| `haskala:height` | 307 | 1 | no | haskala |
| `gndo:relatedSubjectHeading` | 306 | 1 | no | gnd |
| `haskala:width` | 295 | 1 | no | haskala |
| `haskala:occupation` | 286 | 1 | no | haskala |
| `gndo:relatedDdcWithDegreeOfDeterminacy3` | 286 | 1 | no | gnd |
| `gndo:titleOfNobility` | 262 | 1 | no | gnd |
| `haskala:edition_references` | 259 | 1 | no | haskala |
| `gndo:precedingCorporateBody` | 254 | 1 | no | gnd |
| `haskala:preface_writer` | 250 | 1 | no | haskala |
| `owl:deprecated` | 247 | 3 | yes | bhr, gnd, lc |
| `gndo:hierarchicalSuperiorOfTheCorporateBody` | 247 | 1 | no | gnd |
| `gndo:hierarchicalSuperiorOfPlaceOrGeographicName` | 245 | 1 | yes | gnd |
| `haskala:preface_number` | 244 | 1 | no | haskala |
| `dcterms:publisher` | 243 | 1 | no | compact-memory |
| `haskala:preface_title` | 242 | 1 | no | haskala |
| `haskala:printing_press_notes` | 240 | 1 | no | haskala |
| `madsrdf:activityEndDate` | 237 | 1 | no | lc |
| `gndo-http:dateOfDeath` | 232 | 1 | no | nrwbibdjg |
| `skos:exactMatch` | 232 | 1 | no | gnd |
| `agrelon:hasGrandChild` | 232 | 1 | no | gnd |
| `agrelon:hasGrandParent` | 230 | 1 | no | gnd |
| `haskala:occasional_words_languages` | 226 | 1 | no | haskala |
| `foaf:primaryTopic` | 223 | 1 | yes | stolpersteine |
| `jl:grandparent` | 221 | 1 | yes | epidat |
| `gndo-http:dateOfTermination` | 218 | 2 | yes (other form) | hhkeydocs, nrwbibdjg |
| `haskala:contentType` | 218 | 1 | no | haskala |
| `haskala:field` | 218 | 1 | no | haskala |
| `haskala:hidden` | 218 | 1 | no | haskala |
| `haskala:required` | 218 | 1 | no | haskala |
| `gndo-http:academicDegree` | 213 | 1 | no | nrwbibdjg |
| `foaf:homepage` | 211 | 2 | no | hhkeydocs, judaicalink-agents |
| `gndo:realIdentity` | 211 | 1 | no | gnd |
| `haskala:language_of_footnotes` | 205 | 1 | no | haskala |
| `dcterms:issued` | 205 | 1 | no | compact-memory |
| `haskala:cardinality` | 204 | 1 | no | haskala |
| `haskala:drupalField` | 204 | 1 | no | haskala |
| `haskala:drupalFieldType` | 204 | 1 | no | haskala |
| `dc:creator` | 199 | 1 | no | nli-records |
| `gndo:succeedingCorporateBody` | 198 | 1 | no | gnd |
| `agrelon:hasNieceNephew` | 191 | 1 | no | gnd |
| `haskala:topics_notes` | 187 | 1 | no | haskala |
| `haskala:gregorian_year` | 182 | 1 | no | haskala |
| `haskala:location_of_footnotes` | 182 | 1 | no | haskala |
| `madsrdf:hasEarlierEstablishedForm` | 178 | 1 | no | lc |
| `haskala:target_audience_notes` | 176 | 1 | no | haskala |
| `agrelon:hasAuntUncle` | 170 | 1 | no | gnd |
| `jl:subtitle` | 169 | 1 | yes | compact-memory |
| `gndo-http:familialRelationship` | 163 | 1 | no | nrwbibdjg |
| `haskala:section` | 159 | 1 | no | haskala |
| `haskala:book_structure_notes` | 153 | 1 | no | haskala |
| `haskala:hebrew_year_of_publication` | 153 | 1 | no | haskala |
| `gndo:broaderTermPartitive` | 151 | 1 | no | gnd |
| `gndo-http:placeOfDeath` | 149 | 1 | no | nrwbibdjg |
| `haskala:textual_models_notes` | 147 | 1 | no | haskala |
| `dc:contributor` | 145 | 1 | no | footprints |
| `haskala:edition_changes` | 138 | 1 | no | haskala |
| `gndo:relatedCorporateBody` | 125 | 1 | no | gnd |
| `jl:deathDateUncertain` | 124 | 1 | yes | records-normalized |
| `gndo:relatedPlaceOrGeographicName` | 122 | 1 | no | gnd |
| `agrelon:hasFriend` | 116 | 1 | no | gnd |
| `haskala:presented_new_edition` | 115 | 1 | no | haskala |
| `haskala:secondary_sources` | 112 | 1 | no | haskala |
| `gndo-http:personalName` | 109 | 1 | no | nrwbibdjg |
| `gndo:topic` | 108 | 1 | no | gnd |
| `gndo-http:fieldOfStudy` | 106 | 1 | no | nrwbibdjg |
| `haskala:series_part` | 105 | 1 | no | haskala |
| `haskala:name_of_series` | 102 | 1 | no | haskala |
| `haskala:examined_volume_number` | 97 | 1 | no | haskala |
| `haskala:preface_notes` | 97 | 1 | no | haskala |
| `haskala:volumes_published_number` | 97 | 1 | no | haskala |
| `gndo:relatedTerm` | 95 | 1 | no | gnd |
| `haskala:structure_preface_notes` | 94 | 1 | no | haskala |
| `gndo-http:editor` | 93 | 1 | no | footprints |
| `haskala:contents_table_notes` | 93 | 1 | no | haskala |
| `haskala:book_studies` | 91 | 1 | no | haskala |
| `haskala:diagrams_book_pages` | 90 | 1 | no | haskala |
| `haskala:presented_as_translation` | 89 | 1 | no | haskala |
| `haskala:sources_exist` | 88 | 1 | no | haskala |
| `haskala:target_general_notes` | 87 | 1 | no | haskala |
| `haskala:total_number_of_editions` | 87 | 1 | no | haskala |
| `haskala:tel_aviv_library_id` | 86 | 1 | no | haskala |
| `agrelon:hasTeacher` | 83 | 1 | no | gnd |
| `haskala:production_evidence` | 82 | 1 | no | haskala |
| `haskala:publication_place_other` | 79 | 1 | no | haskala |
| `gndo:memberOfTheFamily` | 79 | 1 | no | gnd |
| `haskala:sources_list` | 77 | 1 | no | haskala |
| `haskala:publication_year_in_other` | 72 | 1 | no | haskala |
| `gndo:abbreviatedNameForThePlaceOrGeographicName` | 71 | 1 | no | gnd |
| `gndo:temporaryNameOfThePlaceOrGeographicName` | 70 | 1 | no | gnd |
| `haskala:link_to_digital_book` | 69 | 1 | no | haskala |
| `gndo:relatedPerson` | 69 | 1 | no | gnd |
| `haskala:references_for_editions` | 68 | 1 | no | haskala |
| `haskala:bar_ilan_library_id` | 66 | 1 | no | haskala |
| `haskala:new_edition_type_in_text` | 66 | 1 | no | haskala |
| `haskala:rabbinical_appro_notes` | 64 | 1 | no | haskala |
| `haskala:diagrams_notes` | 61 | 1 | no | haskala |
| `haskala:allowedValue` | 60 | 1 | no | haskala |
| `haskala:volumes_notes` | 60 | 1 | no | haskala |
| `madsrdf:hasLaterEstablishedForm` | 60 | 1 | no | lc |
| `gndo-http:compiler` | 59 | 1 | no | footprints |
| `haskala:frankfurt_library_id` | 59 | 1 | no | haskala |
| `haskala:dedications_notes` | 58 | 1 | no | haskala |
| `haskala:last_known_edition` | 57 | 1 | no | haskala |
| `haskala:sources_references` | 56 | 1 | no | haskala |
| `gndo:udkCode` | 56 | 1 | no | gnd |
| `haskala:other_volumes` | 53 | 1 | no | haskala |
| `haskala:subscribers_notes` | 52 | 1 | no | haskala |
| `haskala:epilogue_notes` | 51 | 1 | no | haskala |
| `haskala:price` | 50 | 1 | no | haskala |
| `jl:birthDateUncertain` | 49 | 1 | yes | records-normalized |
| `haskala:editions_notes` | 40 | 1 | no | haskala |
| `madsrdf:creationDateStart` | 40 | 1 | no | lc |
| `gndo-http:placeOfExile` | 39 | 1 | no | nrwbibdjg |
| `gndo-http:professionOrOccupationAsLiteral` | 39 | 1 | no | nrwbibdjg |
| `haskala:translation_type` | 39 | 1 | no | haskala |
| `gndo-http:forname` | 37 | 1 | no | nrwbibdjg |
| `gndo-http:translator` | 36 | 1 | no | footprints |
| `haskala:motto` | 36 | 1 | no | haskala |
| `haskala:printed_originally` | 36 | 1 | no | haskala |
| `haskala:original_type` | 35 | 1 | no | haskala |
| `gndo-http:sponsorOrPatron` | 34 | 1 | no | footprints |
| `haskala:targetScheme` | 34 | 1 | no | haskala |
| `haskala:gender` | 33 | 1 | no | haskala |
| `gndo:titleOfNobilityAsLiteral` | 33 | 1 | no | gnd |
| `haskala:contacts_other_people` | 32 | 1 | no | haskala |
| `haskala:jewish_sources_quotes` | 32 | 1 | no | haskala |
| `haskala:recommendations_notes` | 31 | 1 | no | haskala |
| `gndo-http:variantNameForTheCorporateBody` | 30 | 1 | no | nrwbibdjg |
| `gndo-http:languageCode` | 29 | 1 | no | nrwbibdjg |
| `haskala:mention_general_notes` | 29 | 1 | no | haskala |
| `gndo:temporaryNameOfTheCorporateBody` | 29 | 1 | no | gnd |
| `haskala:other_books_names` | 27 | 1 | no | haskala |
| `haskala:translation_notes` | 27 | 1 | no | haskala |
| `haskala:catalog_numbers_notes` | 26 | 1 | no | haskala |
| `haskala:old_name_in_book` | 26 | 1 | no | haskala |
| `haskala:thanks_notes` | 26 | 1 | no | haskala |
| `rdfs:comment` | 26 | 2 | yes | bhr, haskala |
| `haskala:printers_notes` | 25 | 1 | no | haskala |
| `haskala:sources_not_mentioned` | 25 | 1 | no | haskala |
| `gndo-http:placeOfBirthAsLiteral` | 24 | 1 | no | nrwbibdjg |
| `haskala:mentions_in_reviews` | 24 | 1 | no | haskala |
| `haskala:new_edition_general_notes` | 24 | 1 | no | haskala |
| `haskala:old_text` | 24 | 1 | no | haskala |
| `haskala:planned_volumes` | 24 | 1 | no | haskala |
| `gndo:place` | 24 | 1 | no | gnd |
| `haskala:personal_addresse_notes` | 23 | 1 | no | haskala |
| `gndo-http:dedicatee` | 22 | 1 | no | footprints |
| `haskala:original_language` | 22 | 1 | no | haskala |
| `madsrdf:deathPlace` | 22 | 1 | no | lc |
| `gndo-http:homepage` | 21 | 1 | no | nrwbibdjg |
| `haskala:contemporary_references` | 21 | 1 | no | haskala |
| `haskala:original_title` | 21 | 1 | no | haskala |
| `gndo:founder` | 21 | 1 | no | gnd |
| `gndo-http:hasPublication` | 20 | 1 | no | gba |
| `gndo-http:occupation` | 20 | 1 | no | gba |
| `haskala:subscription_appeal_notes` | 20 | 1 | no | haskala |
| `madsrdf:establishDate` | 20 | 1 | no | lc |
| `skos:definition` | 20 | 1 | no | judaicalink-vocabulary |
| `gndo-http:birthDate` | 19 | 1 | no | gba |
| `gndo-http:deathDate` | 19 | 1 | no | gba |
| `haskala:berlin_library_id` | 19 | 1 | no | haskala |
| `haskala:book_type_general_notes` | 19 | 1 | no | haskala |
| `haskala:drupalVocabulary` | 19 | 1 | no | haskala |
| `haskala:later_references` | 19 | 1 | no | haskala |
| `haskala:printing_press_references` | 19 | 1 | no | haskala |
| `haskala:sources_not_mentioned_ref` | 19 | 1 | no | haskala |
| `haskala:founders_notes` | 18 | 1 | no | haskala |
| `haskala:sources_not_mentioned_list` | 18 | 1 | no | haskala |
| `skos:notation` | 18 | 1 | no | judaicalink-vocabulary |
| `gndo-http:broaderTermInstantial` | 15 | 1 | no | nrwbibdjg |
| `haskala:old_text_author_in_book` | 15 | 1 | no | haskala |
| `haskala:censorship` | 14 | 1 | no | haskala |
| `haskala:old_text_author` | 14 | 1 | no | haskala |
| `skos:hasTopConcept` | 14 | 1 | no | judaicalink-vocabulary |
| `skos:topConceptOf` | 14 | 1 | no | judaicalink-vocabulary |
| `gndo-http:originalScriptNameOfThePerson` | 13 | 1 | no | nrwbibdjg |
| `gndo-http:placeOfBusiness` | 13 | 1 | no | nrwbibdjg |
| `gndo-http:prefix` | 13 | 1 | no | nrwbibdjg |
| `haskala:contemporary_disputes` | 13 | 1 | no | haskala |
| `haskala:translation_references` | 13 | 1 | no | haskala |
| `haskala:translation_year` | 13 | 1 | no | haskala |
| `skos:closeMatch` | 13 | 1 | no | gnd |
| `gndo-http:periodOfActivity` | 12 | 1 | no | nrwbibdjg |
| `haskala:original_author` | 12 | 1 | no | haskala |
| `gndo:correspondent` | 12 | 1 | no | gnd |
| `gndo:dateOfProduction` | 12 | 1 | no | gnd |
| `gndo-http:nameAddition` | 11 | 1 | no | nrwbibdjg |
| `gndo-http:variantNameForThePlaceOrGeographicName` | 11 | 1 | no | nrwbibdjg |
| `haskala:original_publication_year` | 11 | 1 | no | haskala |
| `madsrdf:terminateDate` | 11 | 1 | no | lc |
| `gndo:preferredNameForTheSubjectHeading` | 11 | 1 | no | gnd |
| `gndo:variantNameForTheSubjectHeading` | 11 | 1 | no | gnd |
| `gndo-http:preferredNameForTheCorporateBody` | 10 | 1 | no | nrwbibdjg |
| `gndo-http:relation` | 10 | 1 | no | gba |
| `gndo-http:spatialAreaOfActivity` | 10 | 1 | no | nrwbibdjg |
| `haskala:contradict_new_edition` | 10 | 1 | no | haskala |
| `haskala:new_edition_type_notes` | 10 | 1 | no | haskala |
| `haskala:proofreaders_notes` | 10 | 1 | no | haskala |
| `gndo:contributingPerson` | 10 | 1 | no | gnd |
| `gndo-http:hasAbstract` | 9 | 1 | no | gba |
| `haskala:presented_new_edition_refe` | 9 | 1 | no | haskala |
| `haskala:sellers_notes` | 9 | 1 | no | haskala |
| `madsrdf:creationDateEnd` | 9 | 1 | no | lc |
| `haskala:targetClass` | 8 | 1 | no | haskala |
| `haskala:translation_city` | 8 | 1 | no | haskala |
| `gndo-http:acquaintanceshipOrFriendship` | 7 | 1 | no | nrwbibdjg |
| `gndo-http:pseudonym` | 7 | 1 | no | nrwbibdjg |
| `haskala:drupalBundle` | 7 | 1 | no | haskala |
| `haskala:heb_year_publication_other` | 7 | 1 | no | haskala |
| `haskala:new_edition_type_reference` | 7 | 1 | no | haskala |
| `haskala:non_jewish_sources_quotes` | 7 | 1 | no | haskala |
| `haskala:original_publication_place` | 7 | 1 | no | haskala |
| `haskala:other_libraries` | 7 | 1 | no | haskala |
| `haskala:presented_new_edition_note` | 7 | 1 | no | haskala |
| `haskala:titleLabel` | 7 | 1 | no | haskala |
| `haskala:translator` | 7 | 1 | no | haskala |
| `rdfs:domain` | 7 | 1 | no | bhr |
| `rdfs:range` | 7 | 1 | no | bhr |
| `gndo-http:affiliationAsLiteral` | 6 | 1 | no | nrwbibdjg |
| `gndo-http:professionalRelationship` | 6 | 1 | no | nrwbibdjg |
| `gndo-http:usingInstructions` | 6 | 1 | no | nrwbibdjg |
| `haskala:british_library_id` | 6 | 1 | no | haskala |
| `haskala:contradict_original` | 6 | 1 | no | haskala |
| `haskala:gregorian_year_pub_other` | 6 | 1 | no | haskala |
| `haskala:original_title_elsewhere` | 6 | 1 | no | haskala |
| `haskala:shownInSection` | 6 | 1 | no | haskala |
| `madsrdf:honoraryTitle` | 6 | 1 | no | lc |
| `gndo:architect` | 6 | 1 | no | gnd |
| `gndo-http:preferredNameForThePlaceOrGeographicName` | 5 | 1 | no | nrwbibdjg |
| `haskala:expanded_in_edition` | 5 | 1 | no | haskala |
| `haskala:original_text_name` | 5 | 1 | no | haskala |
| `haskala:presented_translatio_notes` | 5 | 1 | no | haskala |
| `haskala:presented_translation_refe` | 5 | 1 | no | haskala |
| `gndo:broaderTermGeneral` | 5 | 1 | no | gnd |
| `gndo-http:hierarchicalSuperiorOfTheCorporateBody` | 4 | 1 | no | nrwbibdjg |
| `gndo-http:place` | 4 | 1 | no | nrwbibdjg |
| `gndo-http:relatedSubjectHeading` | 4 | 1 | no | nrwbibdjg |
| `haskala:original_author_elsewhere` | 4 | 1 | no | haskala |
| `haskala:original_title_else_refer` | 4 | 1 | no | haskala |
| `haskala:partial_publication_other` | 4 | 1 | no | haskala |
| `haskala:place_of_death` | 4 | 1 | no | haskala |
| `gndo:definition` | 4 | 1 | no | gnd |
| `gndo-http:alternativeName` | 3 | 1 | no | gba |
| `gndo-http:placeOfDeathAsLiteral` | 3 | 1 | no | nrwbibdjg |
| `gndo-http:relatedTerm` | 3 | 1 | no | nrwbibdjg |
| `gndo-http:topic` | 3 | 1 | no | nrwbibdjg |
| `haskala:bans` | 3 | 1 | no | haskala |
| `haskala:book_not_available` | 3 | 1 | no | haskala |
| `haskala:date_of_birth` | 3 | 1 | no | haskala |
| `haskala:date_of_death` | 3 | 1 | no | haskala |
| `haskala:expanded_in_translations` | 3 | 1 | no | haskala |
| `haskala:original_author_else_refer` | 3 | 1 | no | haskala |
| `haskala:original_publisher` | 3 | 1 | no | haskala |
| `haskala:original_text_author` | 3 | 1 | no | haskala |
| `haskala:place_of_birth` | 3 | 1 | no | haskala |
| `haskala:presented_original_referen` | 3 | 1 | no | haskala |
| `agrelon:hasStudent` | 3 | 1 | no | gnd |
| `gndo:complexSeeReferenceSubject` | 3 | 1 | no | gnd |
| `gndo:dateOfEstablishmentAndTermination` | 3 | 1 | no | gnd |
| `gndo:preferredNameForTheWork` | 3 | 1 | no | gnd |
| `gndo:variantNameForTheWork` | 3 | 1 | no | gnd |
| `gndo-http:architect` | 2 | 1 | no | nrwbibdjg |
| `gndo-http:dateOfProduction` | 2 | 1 | no | nrwbibdjg |
| `gndo-http:memberOfTheFamily` | 2 | 1 | no | nrwbibdjg |
| `gndo-http:relatedPlaceOrGeographicName` | 2 | 1 | no | nrwbibdjg |
| `gndo-http:relatedWork` | 2 | 1 | no | nrwbibdjg |
| `haskala:contacts_official_agents` | 2 | 1 | no | haskala |
| `haskala:new_edition_type_else_note` | 2 | 1 | no | haskala |
| `haskala:new_edition_type_else_ref` | 2 | 1 | no | haskala |
| `haskala:pseudonym` | 2 | 1 | no | haskala |
| `madsrdf:hasCharacteristic` | 2 | 1 | no | lc |
| `skos:scopeNote` | 2 | 2 | yes | judaicalink-vocabulary, rujen |
| `gndo:associatedDate` | 2 | 1 | no | gnd |
| `gndo:dateOfPublication` | 2 | 1 | no | gnd |
| `gndo-http:broaderTermPartitive` | 1 | 1 | no | nrwbibdjg |
| `gndo-http:playedInstrument` | 1 | 1 | no | nrwbibdjg |
| `gndo-http:precedingCorporateBody` | 1 | 1 | no | nrwbibdjg |
| `gndo-http:relatedDdcWithDegreeOfDeterminacy2` | 1 | 1 | no | nrwbibdjg |
| `haskala:bibliographical_citations` | 1 | 1 | no | haskala |
| `haskala:book_availability_notes` | 1 | 1 | no | haskala |
| `haskala:name_in_book` | 1 | 1 | no | haskala |
| `haskala:new_edition_type_elsewhere` | 1 | 1 | no | haskala |
| `haskala:new_york_library_id` | 1 | 1 | no | haskala |
| `haskala:old_author_addition_names` | 1 | 1 | no | haskala |
| `haskala:original_author_other_name` | 1 | 1 | no | haskala |
| `haskala:original_sources_mention` | 1 | 1 | no | haskala |
| `haskala:person_name_appear` | 1 | 1 | no | haskala |
| `haskala:presented_original_notes` | 1 | 1 | no | haskala |
| `haskala:preservation_references` | 1 | 1 | no | haskala |
| `dcterms:description` | 1 | 1 | no | compact-memory |
| `madsrdf:fullerName` | 1 | 1 | no | lc |
| `madsrdf:workOrigin` | 1 | 1 | no | lc |
| `gndo:contributingCorporateBody` | 1 | 1 | no | gnd |
| `gndo:firstAuthor` | 1 | 1 | no | gnd |
| `gndo:preferredNameForTheFamily` | 1 | 1 | no | gnd |

## Prefixes

- `agrelon:` https://d-nb.info/standards/elementset/agrelon#
- `bf:` http://id.loc.gov/ontologies/bibframe/
- `bflc:` http://id.loc.gov/ontologies/bflc/
- `bhrv:` http://data.judaicalink.org/data/bhr/vocab/
- `dc:` http://purl.org/dc/elements/1.1/
- `dcterms:` http://purl.org/dc/terms/
- `dqv:` http://www.w3.org/ns/dqv#
- `foaf:` http://xmlns.com/foaf/0.1/
- `geosparql:` http://www.opengis.net/ont/geosparql#
- `gn-http:` http://www.geonames.org/ontology#
- `gndo:` https://d-nb.info/standards/elementset/gnd#
- `gndo-http:` http://d-nb.info/standards/elementset/gnd#
- `haskala:` http://data.judaicalink.org/data/haskala/vocab/
- `identifiers:` http://id.loc.gov/vocabulary/identifiers/
- `jl:` http://data.judaicalink.org/ontology/
- `madsrdf:` http://www.loc.gov/mads/rdf/v1#
- `madsrdf-old:` http://www.loc.gov/standards/mads/rdf/v1#
- `oa:` http://www.w3.org/ns/oa#
- `owl:` http://www.w3.org/2002/07/owl#
- `prov:` http://www.w3.org/ns/prov#
- `rdf:` http://www.w3.org/1999/02/22-rdf-syntax-ns#
- `rdfs:` http://www.w3.org/2000/01/rdf-schema#
- `schema:` http://schema.org/
- `skos:` http://www.w3.org/2004/02/skos/core#

## Versions counted

2014links 2026-10-12, bhr 2026-10-16, cm-entities 2026-10-12, cm-ocr-quality 2026-10-12, cm-tagme 2021-01-18, compact-memory 2026-10-12, compact-memory-supp 2021-01-19, corrections-links 2026-10-12-2, dbp-wiki-geo-linking 2021-01-13, dbpedia-persons 2018-10-24, djh 2018-10-22, ep 2026-10-12, epidat 2026-10-16, footprints 2026-10-12, gba 2025-03-21, geo-coordinates 2026-10-12, geo-enriched 2026-10-16, geonames 2026-10-16, gnd 2026-10-16, haskala 2026-10-12, hhkeydocs 2026-10-16, hirsch-family 2018-10-30, interlinks 2018-07-18, jre 2019-11-29, judaicalink-agents 2026-10-11, judaicalink-vocabulary 2026-10-12, lc 2026-10-16, ls-nli-legacy 2026-10-12, ls-yivo-wikidata 2026-10-12, nli-records 2026-10-12, nrwbibdjg 2024-05-24, quality-annotations 2026-10-12, record-classes 2026-10-12, records-normalized 2026-10-12, rujen 2026-10-16, rujen-translation 2026-10-12, sosy 2026-10-12, stolpersteine 2020-10-06, ubffm-persons 2019-01-24, yivo 2020-09-30

# conflicts: generator

Records of one person that state different years or places of birth or death (new dataset, decision 0045).

## Framework generator (2026-11-10)

`generate.py` reads the stable ep (which records are one person), the stable record and authority datasets (their
facts), the normalised dates of records-normalized and the feature classes of geonames. About 80 seconds. The rules
are in the docstring; one annotation per person and property, its IRI a hash of the property and the records, so a
conflict keeps its IRI while its records stay the same.

First run (ep 2026-11-10): 3,285 conflicts, 1,896 birth years, 684 death years, 477 places of birth, 228 places of
death. 2,823 are between different sources (GND and Wikidata most of all), 154 within one record (Wikidata items with
two values), 308 between two records of one authority on one page (two GND or two Wikidata records): duplicates in the
authority, or pages that join two persons (Wikidata Q2253, died 183 BCE, and Q7434013, died 1720, on one page).
Requiring settlements left out 393 place conflicts of a country or region against a place in it.

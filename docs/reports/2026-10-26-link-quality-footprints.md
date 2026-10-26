# Link quality: footprints 2026-10-26

The identity links of footprints 2026-10-26 (from the API, decision 0034), measured as in
`2026-10-18-link-quality.md`: `jl sample-links --dataset footprints --seed 2026`, 100 links per unit, on the runs of
the authority datasets of 2026-10-26; judged by an agent per unit with the instruction of 2026-10-18. The samples,
evidence and verdicts are in `lokal/work/link-quality-2026-10-26/`. They replace the units of footprints 2026-10-12
(GND by `gndo:gndIdentifier`, GND, VIAF and LC by `owl:sameAs`), whose links the version no longer has.

| Dataset | Property | Target | Links | Sample | Correct | Wrong | Undecidable | Accuracy (95% interval) |
|---|---|---|--:|--:|--:|--:|--:|---|
| footprints | sameAs | viaf | 1,556 | 100 | 79 | 5 | 16 | 94% (87%–97%) |
| footprints | sameAs | geonames | 983 | 100 | 93 | 0 | 7 | 100% (96%–100%) |

VIAF (the identifiers Footprints gives) stays below the threshold (0032): linked, joins nothing. Wrong: a person
linked to a work (2: Baruch ben Isaac to "Terumah", Bahya ibn Paquda to his "Hidayah"), a firm to a person (2: Frères
Chatelain, the press of Ephraim Heckscher), one cluster that mixes unrelated names. Undecidable: 4 numbers not in the
VIAF dump, 11 name-only matches of common names or patronymics, one target without a name.

GeoNames (confirmed by the API, `inputs:footprints/geonames-2026-10-26`) joins. The 7 undecidable are common names
whose target gives no region; 6 links go to the administrative unit of the same name (correct by the rule of 0032),
two of them of a larger scale: Salzburg to the state, Paris to the département, as Footprints has them.

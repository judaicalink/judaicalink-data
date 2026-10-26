# ls-footprints-viaf: generator

The VIAF numbers Footprints gives its persons, linked (`jl:sameAs`) to our record of the cluster, `data/viaf/<n>` in
the dataset `viaf`, where rules and an LLM judged them correct (decision 0037). The unit footprints → VIAF is below the
quality threshold (0032: 94% on a sample, lower bound 87%), so ls-viaf leaves these links out.

## History

- 2026-10-26 (Kai Eckert): first version.

## Inputs

- `footprints/2026-10-26`: the persons and their VIAF numbers (`owl:sameAs`).
- `record-classes/2026-10-26`, `viaf/2026-10-26`: the classes of both sides; the clusters.
- `inputs:footprints/viaf-verdicts-2026-10-26/verdicts.tsv`: the verdict per link.

## Rules

1. The cluster is in the dataset viaf (99 of 1,556 are not: merged or made after the dump).
2. The classes do not contradict: the cluster is no work or place (10 are works), and `jl.linksets` finds no contradiction.
3. The verdict is "correct".

## The judging

`evidence.py` gathers what both sides say: of the Footprints person its names (label, the aliases of its actor
records), its class and up to 15 records that name it (role, title, date, place; of a work its earliest imprint); of
the cluster its class, names and life dates, with the biographical note and places of its GND record and the labels
and dates of its Wikidata item. The 1,447 links left by rules 1 and 2 were judged by ten agents (Claude Opus 5.5 in
Claude Code), one chunk each, by `instruction.md`: correct, wrong or undecidable, with a short reason. The judges
decided some kinds of cases differently (a label naming several printers, a press, an institution and its library,
activity outside the cluster's lifetime, a Footprints person that mixes persons); a second pass judged the 115 links
of the first pass's "correct" in these cases again by `instruction-review.md`, one agent for all. The evidence,
instructions and verdicts of both passes are the input `inputs:footprints/viaf-verdicts-2026-10-26`.

Result: 1,185 correct, 140 wrong, 122 undecidable. The judgements were not checked by people; the decisions file of
each version (`ls-footprints-viaf-decisions.tsv.gz`) gives the outcome and reason of every link.

## Reproduction

`./jl generate ls-footprints-viaf` makes the version again from its inputs. The judging itself cannot be repeated
exactly (`evidence.py` can, the verdicts of a model cannot).

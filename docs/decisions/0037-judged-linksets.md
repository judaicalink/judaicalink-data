# 0037 Links below the threshold: every link judged, the correct ones in a linkset of their own

Status: accepted · Date: 2026-10-26 · Amends [0032](0032-identity-declarations.md)

## Context

The threshold of 0032 is applied per unit (dataset, property, target): a unit whose measured accuracy is below it
joins nothing. That throws away the correct links of a mostly good unit. The VIAF numbers Footprints gives its persons
(footprints 2026-10-26) are 94% correct on a sample of 100 (87–97%): below the threshold, so 1,556 links, most of
them right, join nothing, and the Footprints persons get pages of their own beside the pages of the same persons.

## Decision

- The threshold stays. For a unit below it, every link may be judged: rules first (the target exists in our
  authority dataset, the classes do not contradict), then an LLM reads the evidence of both sides (names, classes,
  dates, roles, places; the target's linked authority records) and judges the link correct, wrong or undecidable,
  with one instruction for all links. Where several judges share the work, a second pass judges again the cases they
  decided differently, with added rules, so that the same rules hold for all links.
- The links judged correct form a **linkset of their own** (`ls-<dataset>-<target>`, kind `linkset`), with the
  methods `rule-based` and `llm-judged` (new value: automated; the judgements can be wrong and were not checked by
  people). It is our statement (`jl:sameAs`) and joins like the other linksets; it is not measured again by the
  same kind of judgement. Wrong and undecidable links are left out.
- The judgements are an input (inputs area: the evidence, the instruction, the verdicts with their reasons), so the
  generator is deterministic; the version holds a decisions file with the outcome and reason of every link.
- The linkset is not a linking input of the authority datasets or of the linksets per authority (it only links what
  these already have).
- First: `ls-footprints-viaf`.

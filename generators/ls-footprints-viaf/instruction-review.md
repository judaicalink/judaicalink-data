# Second pass: the same rules for all judges

The first pass (instruction.md, ten judges on ten chunks) judged some kinds of cases differently. Each line of
review.jsonl is a link the first pass judged correct, with the evidence (as in the first pass), the first verdict and
why it is reviewed (`flags`). Judge each link again by instruction.md together with these rules, which settle the
cases the judges treated differently:

1. **Several persons or firms in the Footprints label** ("X and Y", "X & Y", "X; Y", "X ṿe-Y", "X and his son"):
   wrong if the cluster is one of them; correct only if the cluster is the partnership or firm itself (its names are
   the joint names or the firm).
2. **A press, firm, heirs or widow in the Footprints label** ("press of X", "Bi-defus X", "Stamperia X", "X's heirs",
   "Erben"): wrong if the cluster is the person X; correct if the cluster is the press or firm (its names are the press
   forms or the firm). A person's name as the label with a press form only among the aliases is the person.
3. **Institutions:** a library, department, special collection or college linked to its parent university or
   institution, or the reverse, or a sub-unit to the whole, is wrong: they are different organisations. Correct only
   if both name the same body (allow language forms and former names).
4. **Dates:** if the person's dated activity in Footprints (not the "printed" dates of an author's works) lies clearly
   outside the cluster's lifetime (more than about 10 years before the birth, or more than about 15 years after the
   death for a printer, publisher, seller, censor or approbator), the link is undecidable, unless another source of
   the cluster (its GND record or Wikidata item) gives dates that fit, or the Footprints label itself gives life or
   activity dates that agree with the cluster (then Footprints itself names that person). Decades written "186x" mean
   the 1860s.
5. **A Footprints person that mixes persons** (the label names one person, the aliases or works belong to another):
   undecidable.

Otherwise keep the first verdict unless it is plainly mistaken. Read every line and judge it yourself; do not write a
program that decides. Write one JSON object per line, in the order of review.jsonl, to review.verdicts.jsonl:
`{"i": <i>, "verdict": "correct" | "wrong" | "undecidable", "rule": <1–5 or null>, "reason": "..."}` (reason at most
about 15 words).

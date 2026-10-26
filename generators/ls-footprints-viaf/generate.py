"""ls-footprints-viaf: the VIAF numbers of the Footprints persons that rules and an LLM judged correct (decision 0037).

Footprints gives 1,556 of its persons a VIAF number (owl:sameAs in footprints). Measured on a sample, these links are
below the quality threshold (0032), so ls-viaf leaves them out. This linkset takes every one of them and links the
person to our record of the cluster (jl:sameAs, as ls-viaf) if
- the cluster is in the dataset viaf (the dump states no successors of merged clusters),
- the classes do not contradict (jl.linksets: a person and a work or place),
- and the verdict of the judging (inputs:footprints/viaf-verdicts-2026-10-26: an LLM read the evidence of both
  sides, made by evidence.py, and judged each link with instruction.md) is "correct"; "wrong" and "undecidable" are
  left out.
Writes the links and ls-footprints-viaf-decisions.tsv.gz: for every link of footprints the outcome and why (the rule,
or the verdict with its reason).
"""

import csv
import gzip
import io
import re
from collections import Counter

from jl.generator import GeneratorError
from jl.linksets import JLSAME, contradict, kinds
from jl.rdf import IRI
from jl.turtle import PREFIXES

INPUTS = {
    "footprints": "footprints/2026-10-26",
    "record_classes": "record-classes/2026-10-26",
    "viaf": "viaf/2026-10-26",
    "verdicts": "inputs:footprints/viaf-verdicts-2026-10-26/verdicts.tsv",
}
PARAMS = {}

JL = "http://data.judaicalink.org/data/"
FP, VIAF = JL + "footprints/person/", JL + "viaf/"
SAME = PREFIXES["owl"] + "sameAs"
VIAF_IRI = re.compile(r"https?://(?:www\.)?viaf\.org/viaf/([0-9]+)/?$")


def generate(run):
    links = sorted({(str(s), m.group(1)) for s, p, o in run.triples("footprints")
                    if p == SAME and str(s).startswith(FP) and (m := VIAF_IRI.match(str(o)))})
    clusters = {str(s) for s, p, o in run.triples("viaf") if p == SAME and str(s).startswith(VIAF)}
    kind_of = kinds(run, ["record_classes", "viaf"])
    with open(run.input("verdicts"), encoding="utf-8", newline="") as f:
        verdicts = {(r["person"], r["viaf"]): (r["verdict"], r["reason"]) for r in csv.DictReader(f, delimiter="\t")}
    out, rows, c = set(), [], Counter()
    for s, n in links:
        v = VIAF + n
        if v not in clusters:
            outcome, why = "left out", "cluster not in the dataset viaf"
        elif contradict(kind_of.get(s, set()), kind_of.get(v, set())):
            outcome, why = "left out", "classes contradict"
        elif (s, n) not in verdicts:
            raise GeneratorError(f"no verdict for {s} viaf {n}")
        else:
            verdict, reason = verdicts[(s, n)]
            outcome, why = ("linked" if verdict == "correct" else "left out"), f"judged {verdict}: {reason}"
            if outcome == "linked":
                out.add((IRI(s), IRI(JLSAME), IRI(v)))
        c[f"{outcome}: {why.split(':')[0]}"] += 1
        rows.append((s, n, outcome, why))
    unused = set(verdicts) - set(links)
    if unused:
        raise GeneratorError(f"{len(unused)} verdicts for links footprints does not have, e.g. {min(unused)}")
    with gzip.GzipFile(run.path("ls-footprints-viaf-decisions.tsv.gz"), "wb", mtime=0) as g, \
            io.TextIOWrapper(g, encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["person", "viaf", "outcome", "why"])
        w.writerows(rows)
    run.note(f"{len(out):,} links of {len(links):,} VIAF numbers of footprints; "
             + ", ".join(f"{k} {v:,}" for k, v in sorted(c.items())) + ".")
    run.write_turtle("ls-footprints-viaf.ttl.gz", out)

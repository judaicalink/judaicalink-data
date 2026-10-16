"""ls-nli-wikidata: the records of nli-records linked to their Wikidata items.

nli-records links its records to VIAF (owl:sameAs viaf.org/viaf/<n>, from field 901 of the NLI export) and to the
LC name authority file (id.loc.gov/authorities/names/<n>, from 010). Wikidata states the same numbers with P214 (VIAF
ID) and P244 (Library of Congress authority ID); the answers for all numbers of nli-records are the input
inputs:web-caches/wikidata-nli-2026-10-15 (made by query.py). The export has no NLI control number, so the NLI J9U ID
(P8189) cannot be used.

A record is linked (owl:sameAs <item>) only when the match is unique in both directions: its VIAF and LC numbers lead
to exactly one item, and no other record leads to that item. Records with several items (a VIAF or LC number on
several items, or VIAF and LC pointing to different items) and items reached from several records are left out and
named in the log.
"""

import csv
from collections import defaultdict

from jl.rdf import IRI
from jl.turtle import PREFIXES

INPUTS = {"nli": "nli-records/2026-10-12",
          "viaf": "inputs:web-caches/wikidata-nli-2026-10-15/p214.tsv",
          "lc": "inputs:web-caches/wikidata-nli-2026-10-15/p244.tsv"}
PARAMS = {}

SAME = PREFIXES["owl"] + "sameAs"
WD = "http://www.wikidata.org/entity/"
KEYS = {"viaf": "http://viaf.org/viaf/", "lc": "http://id.loc.gov/authorities/names/"}


def items(path):
    out = defaultdict(set)
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            out[row["id"]].add(row["item"])
    return out


def generate(run):
    found = {k: items(run.input(k)) for k in KEYS}
    numbers = defaultdict(lambda: {k: set() for k in KEYS})
    for s, p, o in run.triples("nli"):
        if p == SAME:
            for k, prefix in KEYS.items():
                if o.startswith(prefix):
                    numbers[s][k].add(o[len(prefix):])
    cand = {}   # record -> {item: keys}
    for s, nums in numbers.items():
        c = defaultdict(set)
        for k, vals in nums.items():
            for v in vals:
                for q in found[k].get(v, ()):
                    c[q].add(k)
        if c:
            cand[s] = c
    by_item = defaultdict(set)
    for s, c in cand.items():
        for q in c:
            by_item[q].add(s)
    t, several, shared, keys = set(), [], set(), defaultdict(int)
    for s in sorted(cand):
        c = cand[s]
        if len(c) > 1:
            several.append(f"{s}: {', '.join(f'{q} ({'+'.join(sorted(k))})' for q, k in sorted(c.items()))}")
            continue
        q = next(iter(c))
        if len(by_item[q]) > 1:
            shared.add(q)
            continue
        t.add((IRI(s), IRI(SAME), IRI(WD + q)))
        keys["+".join(sorted(c[q]))] += 1
    for line in several:
        run.log("several items, left out:", line)
    for q in sorted(shared):
        run.log("item of several records, left out:", q, " ".join(sorted(by_item[q])))
    run.note(f"{len(numbers):,} records with a VIAF or LC number; {len(cand):,} with a Wikidata item; "
             f"{len(t):,} linked ({', '.join(f'{k}: {n:,}' for k, n in sorted(keys.items()))}); "
             f"{len(several):,} with several items and {sum(len(by_item[q]) for q in shared):,} records sharing "
             f"{len(shared):,} items left out.")
    run.write_turtle("ls-nli-wikidata.ttl.gz", t)

"""ls-bhr-wikidata: the persons of the Biographisches Handbuch der Rabbiner linked to their Wikidata items.

Wikidata states the entry of an item in the Biographisches Portal der Rabbiner with the property P10405 (the BHR id,
without leading zeros, the id of bhr?id=N); the snapshot of the query is inputs:web-caches/wikidata-bhr-2026-10-15. A
bhr record knows its ids from its links to the BHR pages (the database of 2018, or the portal). A record gets
owl:sameAs an item when its ids lead to exactly one item and that item's ids to no other record; ids held by two
records and records whose ids lead to several items are left out (named in the log).
"""

import csv

from jl.rdf import IRI
from jl.turtle import PREFIXES

INPUTS = {"bhr": "bhr/2026-10-12", "wikidata": "inputs:web-caches/wikidata-bhr-2026-10-15/p10405.tsv"}
PARAMS = {}

SAME = PREFIXES["owl"] + "sameAs"
DESCRIBED = PREFIXES["jl"] + "describedAt"
WD = "http://www.wikidata.org/entity/"
PAGES = ("http://steinheim-institut.de:50580/cgi-bin/bhr?id=", "https://www.steinheim-institut.de/cgi-bin/bhr?id=")


def generate(run):
    record_ids, id_records = {}, {}
    for s, p, o in run.triples("bhr"):
        if p in (SAME, DESCRIBED) and isinstance(o, IRI):
            for prefix in PAGES:
                if o.startswith(prefix):
                    i = o[len(prefix):].lstrip("0")
                    record_ids.setdefault(s, set()).add(i)
                    id_records.setdefault(i, set()).add(s)
    id_items, item_ids = {}, {}
    with open(run.input("wikidata"), encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            q, i = row["?item"].strip("<>").removeprefix(WD), row["?bhr"].strip('"').lstrip("0")
            id_items.setdefault(i, set()).add(q)
            item_ids.setdefault(q, set()).add(i)
    t, stats = set(), {}

    def count(k):
        stats[k] = stats.get(k, 0) + 1

    for s in sorted(record_ids):
        items = set().union(*(id_items.get(i, set()) for i in record_ids[s]))
        if not items:
            count("no item")
            continue
        if len(items) > 1:
            count("several items, left out")
            run.log("several items, left out:", f"{s}: {', '.join(sorted(items))}")
            continue
        q = next(iter(items))
        others = set().union(*(id_records.get(i, set()) for i in item_ids[q])) - {s}
        if others:
            count("item shared with another record, left out")
            run.log("shared, left out:", f"{q}: {s}, {', '.join(sorted(others))}")
            continue
        count("linked")
        t.add((IRI(s), IRI(SAME), IRI(WD + q)))
    unmatched = sorted(set(id_items) - set(id_records), key=lambda x: int(x) if x.isdigit() else 0)
    run.note(f"{len(record_ids):,} records with a BHR id; {dict(sorted(stats.items()))}; {len(item_ids):,} items with "
             f"P10405, {len(unmatched)} ids name no bhr record ({', '.join(unmatched)}).")
    run.write_turtle("ls-bhr-wikidata.ttl.gz", t)

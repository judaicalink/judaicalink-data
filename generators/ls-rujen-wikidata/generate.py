"""ls-rujen-wikidata: the articles of the Encyclopedia of Russian Jewry (rujen.ru) linked to their Wikidata items.

Wikidata states the article of an item with the property P10278 (Encyclopedia of Russian Jewry ID); the snapshot of
the query is inputs:web-caches/wikidata-rujen-2026-10-15. The value is mostly the page id of the wiki (the "id" of
the crawl, rujen.ru/index.php?curid=<id>), sometimes the page name. The record IRI of a page is made from the crawl
as rujen's generator makes it. Every record with exactly one item gets owl:sameAs that item; values naming no page
of the crawl, records with several items and items naming several records are left out (named in the log).
"""

import csv
import gzip
import json
from urllib.parse import unquote

from jl.generator import load_shared
from jl.rdf import IRI
from jl.turtle import PREFIXES

rujen = load_shared("rujen", "generate")

INPUTS = {"crawl": "rujen/2020-09-28/rujen.jsonl.gz",
          "wikidata": "inputs:web-caches/wikidata-rujen-2026-10-15/p10278.tsv"}
PARAMS = {}

SAME = PREFIXES["owl"] + "sameAs"
WD = "http://www.wikidata.org/entity/"


def generate(run):
    by_id, by_name = {}, {}
    with gzip.open(run.input("crawl"), "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["title"] == rujen.MAIN_PAGE:
                continue
            s = rujen.local(d["uri"])
            by_id[d["id"]] = s
            by_name[unquote(d["uri"]).replace("/index.php/", "").lower()] = s
    items = {}   # record IRI -> items
    records = {}   # item -> record IRIs
    unknown = []
    with open(run.input("wikidata"), encoding="utf-8", newline="") as f:
        rows = csv.reader(f, delimiter="\t")
        next(rows)
        for item, value in rows:
            qid = item.strip("<>").removeprefix(WD)
            value = value.strip('"')
            s = by_id.get(value) or by_name.get(value.replace(" ", "_").lower())
            if s is None:
                unknown.append(f"{qid} {value}")
                continue
            items.setdefault(s, set()).add(qid)
            records.setdefault(qid, set()).add(s)
    t = set()
    for s, qids in sorted(items.items()):
        if len(qids) == 1 and len(records[next(iter(qids))]) == 1:
            t.add((IRI(s), IRI(SAME), IRI(WD + next(iter(qids)))))
        else:
            run.log("several, left out:", s, ", ".join(sorted(qids)))
    for line in sorted(unknown):
        run.log("names no page of the crawl:", line)
    run.note(f"{sum(len(v) for v in records.values()) + len(unknown)} P10278 values; {len(t)} records linked to "
             f"their Wikidata item; {len(items) - len(t)} left out (several); {len(unknown)} name no page.")
    run.write_turtle("ls-rujen-wikidata.ttl.gz", t)

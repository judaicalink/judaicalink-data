"""ls-yivo-wikidata: the articles of the YIVO Encyclopedia linked to their Wikidata items.

Wikidata states the article of an item with the property P8569 (YIVO Encyclopedia of Jews in Eastern Europe ID, the
article name); the snapshot of the query is inputs:web-caches/wikidata-yivo-2026-10-12. Every yivo record whose article
has exactly one item gets owl:sameAs that item; articles with several items are left out (named in the log).
"""

from jl.generator import load_shared
from jl.rdf import IRI
from jl.turtle import PREFIXES

yw = load_shared("ls-yivo-wikidata", "yivo_wikidata")

INPUTS = {"yivo": "yivo/2020-09-30", "wikidata": "inputs:web-caches/wikidata-yivo-2026-10-12/p8569.tsv"}
PARAMS = {}

SAME = PREFIXES["owl"] + "sameAs"


def generate(run):
    arts = yw.articles(run.triples("yivo"))
    by_name, _classes = yw.items(run.input("wikidata"))
    t, several = set(), []
    for name, s in arts.items():
        qids = by_name.get(name, set())
        if len(qids) == 1:
            t.add((IRI(s), IRI(SAME), IRI(yw.WD + next(iter(qids)))))
        elif qids:
            several.append(f"{name}: {', '.join(sorted(qids))}")
    for line in sorted(several):
        run.log("several items, left out:", line)
    unmatched = sorted(set(by_name) - set(arts))
    run.note(f"{len(arts):,} articles; {len(t):,} linked to their Wikidata item; {len(several)} with several items "
             f"left out; {len(unmatched)} P8569 values name no article ({', '.join(unmatched)}).")
    run.write_turtle("ls-yivo-wikidata.ttl.gz", t)

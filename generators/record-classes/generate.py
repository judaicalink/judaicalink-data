"""record-classes: the class of records that their datasets do not type (complement, rule-based).

YIVO articles (yivo states no rdf:type for its 1,798 articles, so they were on no entity page): the class from the
Wikidata item of the article (P8569, inputs:web-caches/wikidata-yivo-2026-10-12; shared code of ls-yivo-wikidata):
human (Q5) foaf:Person; a subclass of geographic location, administrative territorial entity or human settlement
jl:Place; of organization foaf:Organization; of written work, periodical or creative work jl:Work. Without an item
(or a class among these): life dates in parentheses at the start of the abstract, "(1880–1963), revolutionary…",
foaf:Person; every other article jl:Subject. The article subsections (skos:Concept in yivo) are not typed here.
"""

import re
from collections import Counter

from jl import classes
from jl.generator import load_shared
from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES

yw = load_shared("ls-yivo-wikidata", "yivo_wikidata")

INPUTS = {
    "yivo": "yivo/2020-09-30",
    "items": "inputs:web-caches/wikidata-yivo-2026-10-12/p8569.tsv",
    "classes": "inputs:web-caches/wikidata-yivo-2026-10-12/classes-top.tsv",
}
PARAMS = {}

JLO, FOAF = PREFIXES["jl"], PREFIXES["foaf"]
CLASS_IRI = {"Person": classes.PERSON, "Place": classes.PLACE, "Organization": classes.ORGANISATION,
             "Work": classes.WORK, "Subject": classes.SUBJECT}
DATES = re.compile(r"\b\d{3,4}\b|\b\d{1,2}(st|nd|rd|th)\b|centur|\b[bd]\.\s|–\s*$|\?")


def opening_parenthesis(text):
    """The text of the parenthesis the abstract starts with (nested ones included), or None."""
    if not text.startswith("("):
        return None
    depth = 0
    for i, ch in enumerate(text):
        depth += (ch == "(") - (ch == ")")
        if depth == 0:
            return text[1:i]
    return None


def life_dates(abstract):
    p = opening_parenthesis(abstract.strip())
    return p is not None and bool(DATES.search(p))


def generate(run):
    triples = list(run.triples("yivo"))
    arts = yw.articles(triples)
    abstract = {s: o.value for s, p, o in triples if p == JLO + "hasAbstract" and isinstance(o, Literal)}
    by_name, classes = yw.items(run.input("items"))
    upper = yw.uppers(run.input("classes"))
    t, n = set(), Counter()
    for name, s in arts.items():
        c = yw.wikidata_class(by_name.get(name, ()), classes, upper)
        how = "Wikidata"
        if c is None:
            c, how = ("Person", "life dates") if life_dates(abstract.get(s, "")) else ("Subject", "other")
        n[(c, how)] += 1
        t.add((IRI(s), IRI(RDF_TYPE), IRI(CLASS_IRI[c])))
    run.note("yivo: " + "; ".join(f"{c} by {how} {k:,}" for (c, how), k in sorted(n.items())) + ".")
    run.write_turtle("record-classes.ttl.gz", t)

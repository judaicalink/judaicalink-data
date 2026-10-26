"""record-classes: the class of records that their datasets do not type (complement, rule-based).

YIVO articles (yivo states no rdf:type for its 1,798 articles, so they were on no entity page): the class from the
Wikidata item of the article (P8569, inputs:web-caches/wikidata-yivo-2026-10-12; shared code of ls-yivo-wikidata):
human (Q5) foaf:Person; a subclass of geographic location, administrative territorial entity or human settlement
jl:Place; of organization foaf:Organization; of written work, periodical or creative work jl:Work. Without an item
(or a class among these): life dates in parentheses at the start of the abstract, "(1880–1963), revolutionary…",
foaf:Person; every other article jl:Subject. The article subsections (skos:Concept in yivo) are not typed here.

Footprints persons (the API does not tell persons from organisations, decision 0034): foaf:Organization where the
VIAF record of the person is an organisation (viaf, the VIAF number given by Footprints) or the name names an
institution, a firm or a group (ORGANISATION: libraries, universities, seminaries, congregations, booksellers,
printing houses, heirs and partners, "&", in the languages of the data); every other one foaf:Person. A VIAF record
that is a place or a work gives no class (the name decides).
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
    "footprints": "footprints/run-20261026T072438Z",
    "viaf": "viaf/2026-10-19",
    "items": "inputs:web-caches/wikidata-yivo-2026-10-12/p8569.tsv",
    "classes": "inputs:web-caches/wikidata-yivo-2026-10-12/classes-top.tsv",
}
PARAMS = {}

JLO, FOAF = PREFIXES["jl"], PREFIXES["foaf"]
CLASS_IRI = {"Person": classes.PERSON, "Place": classes.PLACE, "Organization": classes.ORGANISATION,
             "Work": classes.WORK, "Subject": classes.SUBJECT}
FP = "http://data.judaicalink.org/data/footprints/"
VIAF_RECORD = re.compile(r"http://data\.judaicalink\.org/data/viaf/([0-9]+)$")
VIAF_IRI = re.compile(r"https?://(?:www\.)?viaf\.org/viaf/([0-9]+)/?$")
ORGANISATION = re.compile(r"""\b(librar(y|ies)|bibliot(h)?e(k|ca|que|ka)|universit(y|ies|à|ät|é|at)|college|collegio|colegio
 |seminar(y|ium|s|io)?|instituut|institut(e|o|ion)?|lehranstalt|hochschule|society|soci[eé]t[eé]|verein|gesellschaft
 |congregatio(n)?|(kultus|cultus)?gemeinde|comunit[àa]|communit(y|a)|synagog(ue|e|a)|tempio|temple|museum|archive(s)?
 |press|verlag|buchhandlung|antiquariat|librairie|imprimerie|stamperia|stamparia|typographia|officina|booksellers?
 |books|galleries|company|firm|printers|erben|h(a)?eredes|fils|brothers|fr[eè]res|gebr(ü|ue)der|sons|beth\s+din
 |yeshiva(h)?|school|acad[eé]m(y|ie)|akademie|foundation|stiftung|cent(er|re)|church|convent|monaster(y|ium)|abbey
 |jesuit\w*|reconstruction|trust|auction(s|eers)?|sotheby'?s?|christie'?s|kestenbaum|parke-bernet|swann|ministry
 |department|committee|council|association|federation|union|club|lodge|order|kloster|stift|bureau|office|agency
 |ḥevrat|ḥevra|hevrat|aḥim|ahim|yetome|ha-madpis|madpis|kehal|ḳehal|ḳehilat|kehilat)\b
 |&|\(firm|ספרי(י)?ה|ספרית|חברת|ישיבת|קהל|קהילת|אחים|יתומי|בית\s+(הספרים|המדרש|מדרש|דפוס)""", re.I | re.X)
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
    t |= footprints_persons(run)
    run.write_turtle("record-classes.ttl.gz", t)


def footprints_persons(run):
    viaf_class = {}
    for s, p, o in run.triples("viaf"):
        if p == RDF_TYPE and (m := VIAF_RECORD.match(str(s))):
            viaf_class[m.group(1)] = classes.kind(str(o))
    name, viaf = {}, {}
    for s, p, o in run.triples("footprints"):
        if not str(s).startswith(FP + "person/"):
            continue
        if p == RDF_TYPE:
            name.setdefault(str(s), "")
        elif p == PREFIXES["skos"] + "prefLabel":
            name[str(s)] = o.value
        elif p == PREFIXES["owl"] + "sameAs" and (m := VIAF_IRI.match(str(o))):
            viaf[str(s)] = m.group(1)
    t, n = set(), Counter()
    for s in sorted(name):
        by_viaf = viaf_class.get(viaf.get(s))
        by_name = bool(ORGANISATION.search(name[s]))
        if by_viaf == "Organization" or by_name:
            c = "Organization"
            how = " and ".join(k for k, v in (("VIAF", by_viaf == "Organization"), ("name", by_name)) if v)
        else:
            c, how = "Person", "VIAF" if by_viaf == "Person" else "default"
        n[(c, how)] += 1
        t.add((IRI(s), IRI(RDF_TYPE), IRI(CLASS_IRI[c])))
    run.note("footprints persons: " + "; ".join(f"{c} by {how} {k:,}" for (c, how), k in sorted(n.items())) + ".")
    return t

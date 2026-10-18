"""wikidata: the Wikidata items JudaicaLink uses (decision 0029), from answers of Wikidata kept in the inputs area.

1. The selection list (wikidata-selection.tsv.gz): one row per item and reason, with the current item (the one a
   merged item redirects to; empty if the item is deleted).
   - linked: an item named as object in one of our datasets (ids.DATASETS); the detail is the dataset.
   - by-gnd, by-viaf, by-lc, by-geonames, by-isni: an item that states an identifier our data names (P227, P214,
     P244, P1566, P213); the detail is the identifier. A statement whose reference cites JudaicaLink (stated in or
     imported from JudaicaLink, Q132858785, or a reference URL in judaicalink.org) does not count: links to
     JudaicaLink are never evidence (decision 0029); such statements are also left out of the data.
   - by-dbpedia: the item of the English Wikipedia article of a DBpedia resource our data names; the detail is the
     resource name.
2. The data (wikidata.ttl.gz), for every current item named by the list, from the answers of the Wikidata API (the
   best-ranked statements: preferred, else normal): data/wikidata/<Q> owl:sameAs the item; skos:prefLabel (en, de,
   he, mul); the classes (wdt:P31) and foaf:Person for humans (Q5), schema:Place for items with a GeoNames ID (P1566);
   jl:birthDate/deathDate in the precision Wikidata gives (year, month or day; coarser values are left out);
   wdt:P19/P20 and jl:birthLocationURI/deathLocationURI (the Wikidata items of the places); the identifiers: GND,
   VIAF, LC, GeoNames, ISNI as IRIs in canonical form with Wikidata's normalized properties (wdtn:), NLI J9U, YIVO,
   BHR and Encyclopedia of Russian Jewry as literals (wdt:); the Wikipedia articles (en, de, he) as
   foaf:isPrimaryTopicOf. Never a JudaicaLink property or IRI.
3. Replacements: a named item that was merged: <old> dcterms:isReplacedBy <new> (Wikidata's IRIs); a named item
   that does not exist any more: <item> owl:deprecated true.
"""

import csv
import gzip
import json
import urllib.parse
from collections import defaultdict

from jl import identifiers
from jl import classes
from jl.generator import load_shared
from jl.iris import canonical
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

ids = load_shared("wikidata", "ids")

CACHE = "inputs:web-caches/wikidata-2026-10-18/"
INPUTS = {"entities": CACHE + "entities.jsonl.gz", "articles": CACHE + "articles.tsv",
          **{f"find_{p}": CACHE + f"find-{p}.tsv" for p in ids.PROPERTIES.values()},
          **ids.DATASETS}
PARAMS = {}

JL = "http://data.judaicalink.org/data/"
WD, WDT, WDTN = ("http://www.wikidata.org/entity/", "http://www.wikidata.org/prop/direct/",
                 "http://www.wikidata.org/prop/direct-normalized/")
JUDAICALINK = "Q132858785"
JLO, SKOS, OWL, FOAF, DCT = (PREFIXES[p] for p in ("jl", "skos", "owl", "foaf", "dcterms"))
SAME = OWL + "sameAs"
REASON_OF = {"gnd": "by-gnd", "viaf": "by-viaf", "lc-names": "by-lc", "geonames": "by-geonames", "isni": "by-isni"}
REASONS = ["linked", "by-gnd", "by-viaf", "by-lc", "by-geonames", "by-isni", "by-dbpedia"]
# identifier properties: as IRIs (canonical form) or as literals
AS_IRI = {"P227": "https://d-nb.info/gnd/{}", "P214": "https://viaf.org/viaf/{}",
          "P244": "http://id.loc.gov/authorities/names/{}", "P1566": "https://sws.geonames.org/{}/",
          "P213": "https://isni.org/isni/{}"}
AS_LITERAL = ["P8189", "P8569", "P10405", "P10278"]
WIKIS = {"enwiki": "en", "dewiki": "de", "hewiki": "he"}


def cites_judaicalink(statement):
    for ref in statement.get("references", []):
        for p in ("P248", "P143"):
            if any(isinstance(v, dict) and v.get("id") == JUDAICALINK for v in ref.get(p, [])):
                return True
        if any(isinstance(v, str) and "judaicalink" in v.lower() for v in ref.get("P854", [])):
            return True
    return False


def best(statements):
    """The best-ranked statements (Wikidata's truthy statements), without those citing JudaicaLink."""
    ok = [s for s in statements if s.get("rank") != "deprecated" and s.get("value") is not None]
    preferred = [s for s in ok if s.get("rank") == "preferred"]
    return [s for s in (preferred or ok) if not cites_judaicalink(s)]


def date(value):
    """The date in the precision Wikidata gives it: YYYY, YYYY-MM or YYYY-MM-DD; None if coarser than a year."""
    p, t = value.get("precision"), value.get("time", "")
    if p is None or p < 9 or len(t) < 11:
        return None
    sign = "-" if t.startswith("-") else ""
    y, m, d = t[1:].split("T")[0].split("-")
    y = y.lstrip("0").rjust(4, "0")
    return sign + (y if p == 9 else f"{y}-{m}" if p == 10 else f"{y}-{m}-{d}")


def article(wiki, title):
    lang = WIKIS[wiki]
    return f"https://{lang}.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=";:@$!*(),/~")


def norm_value(prop, v):
    return str(v).strip().upper() if prop == "P227" else str(v).replace(" ", "") if prop == "P213" else str(v).strip()


def generate(run):
    found = identifiers_named(run)
    entities = {}
    with gzip.open(run.input("entities"), "rt", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            entities[row["id"]] = row

    def current(q):
        row = entities.get(q)
        if not row or "entity" not in row:
            return ""
        return row.get("redirect", q)

    rows = set()
    for q, slugs in found["wikidata"].items():
        for slug in slugs:
            rows.add((q, "linked", slug))
    dropped = 0
    for source, prop in ids.PROPERTIES.items():
        named = {norm_value(prop, v if source != "isni" else ids.isni_value(v)): v for v in found[source]}
        with open(run.input(f"find_{prop}"), encoding="utf-8") as f:
            for line in list(f)[1:]:
                cells = line.rstrip("\n").split("\t")
                if len(cells) < 2:
                    continue
                value = norm_value(prop, cells[0].strip('"'))
                q = cells[1].strip("<>").rsplit("/", 1)[-1]
                if value not in named:
                    continue
                e = entities.get(q, {}).get("entity") or {}
                statements = [s for s in e.get("claims", {}).get(prop, []) if norm_value(prop, s.get("value")) == value]
                if statements and all(cites_judaicalink(s) for s in statements):
                    dropped += 1
                    run.log(f"left out (cites JudaicaLink): {q} {prop} {value}")
                    continue
                rows.add((q, REASON_OF[source], named[value]))
    by_name = defaultdict(set)
    for n in found["dbpedia"]:
        by_name[ids.article_name(n)].add(n)
    with open(run.input("articles"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            for n in by_name.get(r["title"], ()):
                rows.add((r["item"], "by-dbpedia", n))

    selected = sorted({current(q) for q, _r, _d in rows} - {""}, key=lambda x: int(x[1:]))
    t = set()
    for q in selected:
        e = entities[q]["entity"] if q in entities and "entity" in entities[q] else \
            next(r["entity"] for r in entities.values() if r.get("redirect") == q and "entity" in r)
        rec, item = IRI(JL + "wikidata/" + q), IRI(WD + q)
        t.add((rec, IRI(SAME), item))
        for lang, label in sorted(e.get("labels", {}).items()):
            t.add((rec, IRI(SKOS + "prefLabel"), Literal(label, None, lang)))
        claims = e.get("claims", {})
        p31 = {s["value"].get("id") for s in best(claims.get("P31", [])) if isinstance(s["value"], dict)}
        for c in sorted(x for x in p31 if x):
            t.add((rec, IRI(WDT + "P31"), IRI(WD + c)))
        if "Q5" in p31:
            t.add((rec, IRI(RDF_TYPE), IRI(FOAF + "Person")))
        elif best(claims.get("P1566", [])):
            t.add((rec, IRI(RDF_TYPE), IRI(classes.PLACE)))
        for prop, term in (("P569", "birthDate"), ("P570", "deathDate")):
            for s in best(claims.get(prop, [])):
                d = date(s["value"]) if isinstance(s["value"], dict) else None
                if d:
                    t.add((rec, IRI(JLO + term), Literal(d)))
        for prop, term in (("P19", "birthLocationURI"), ("P20", "deathLocationURI")):
            for s in best(claims.get(prop, [])):
                if isinstance(s["value"], dict) and s["value"].get("id"):
                    t.add((rec, IRI(WDT + prop), IRI(WD + s["value"]["id"])))
                    t.add((rec, IRI(JLO + term), IRI(WD + s["value"]["id"])))
        for prop, form in AS_IRI.items():
            for s in best(claims.get(prop, [])):
                v = norm_value(prop, s["value"])
                iri = canonical(form.format(v))
                if not identifiers.is_ours(iri):
                    t.add((rec, IRI(WDTN + prop), IRI(iri)))
        for prop in AS_LITERAL:
            for s in best(claims.get(prop, [])):
                t.add((rec, IRI(WDT + prop), Literal(str(s["value"]))))
        for wiki, title in sorted(e.get("sitelinks", {}).items()):
            if wiki in WIKIS:
                t.add((rec, IRI(FOAF + "isPrimaryTopicOf"), IRI(article(wiki, title))))
    merged = deleted = 0
    for q in sorted(found["wikidata"], key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
        row = entities.get(q)
        if row and row.get("redirect") and row["redirect"] != q:
            t.add((IRI(WD + q), IRI(DCT + "isReplacedBy"), IRI(WD + row["redirect"])))
            merged += 1
        elif not row or "entity" not in row:
            t.add((IRI(WD + q), IRI(OWL + "deprecated"), Literal("true", XSD + "boolean")))
            deleted += 1

    with gzip.open(run.path("wikidata-selection.tsv.gz"), "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["item", "current", "reason", "detail"])
        for q, reason, detail in sorted(rows, key=lambda r: (int(r[0][1:]) if r[0][1:].isdigit() else 0, r[0],
                                                               REASONS.index(r[1]), r[2])):
            w.writerow([q, current(q), reason, detail])
    by = defaultdict(set)
    for q, reason, _d in rows:
        by[reason].add(current(q) or q)
    only = {r: len(by[r] - set().union(*(by[x] for x in REASONS[:REASONS.index(r)]))) for r in REASONS}
    run.note(f"{len(selected):,} items; by reason: "
             + ", ".join(f"{r} {len(by[r]):,} ({only[r]:,} not in the reasons before)" for r in REASONS)
             + f"; {merged:,} named items merged, {deleted:,} named items deleted; {dropped:,} identifier "
             f"statements left out because they cite JudaicaLink.")
    run.write_turtle("wikidata.ttl.gz", t)


def identifiers_named(run):
    return ids.collect((ref.split("/", 1)[0], run.triples(name)) for name, ref in ids.DATASETS.items())

"""dbp-wiki-geo-linking: the places of geo-coordinates linked to Wikidata, DBpedia and Wikipedia.

Made again (decision 0024), offline and deterministically, from the answers of the Wikidata Query Service in
inputs:web-caches/wikidata-geonames-2026-10-15 (fetch_wikidata.py); the version of 2021 asked a GeoNames mirror that
is closed (lotico.com) and linked the old IRIs of geo-coordinates (data/<name>) and of geo-enriched (data/geonames/N).

For every place of geo-coordinates (records of the GND): the Wikidata items that have one of its GND numbers (P227,
from gndo:gndIdentifier and owl:sameAs), and those that have one of its GeoNames ids (P1566). The GND route comes
first: the place is linked to its only item by GND; with several items by GND, to the one of them that GeoNames
also gives; without an item by GND, to its only item by GeoNames. GeoNames ids in Wikidata often sit on a second item
for the settlement beside the item of the town or municipality that the GND, Wikipedia and the other datasets use
(Ansbach: Q117751859 "main settlement of Ansbach" beside Q14859), so the GND route decides; where GeoNames gives
another item, both are named in the log. Places with several items are left out (named in the log).
For a linked place:
- owl:sameAs the Wikidata item, and the DBpedia resource of its English Wikipedia article;
- foaf:isPrimaryTopicOf its English, German and Russian Wikipedia articles (documents about the place, not the place;
  the 2021 version stated owl:sameAs for them).
Only places of geo-coordinates, the records of places: the places that geo-enriched links only by their GeoNames IRI
are no records, and their Wikidata items are stated by Wikidata itself (P1566).
"""

import re
import urllib.parse
from collections import Counter, defaultdict

from jl.rdf import IRI
from jl.turtle import PREFIXES

INPUTS = {"geo_coordinates": "geo-coordinates/2026-10-12", "wikidata": "inputs:web-caches/wikidata-geonames-2026-10-15"}
PARAMS = {}

SAME = PREFIXES["owl"] + "sameAs"
TOPIC = PREFIXES["foaf"] + "isPrimaryTopicOf"
WD = "http://www.wikidata.org/entity/"
WIKIS = ("en", "de", "ru")
_IRI_BAD = re.compile(r'[<>"{}|^`\\\s]')


def iri(value):
    return IRI(_IRI_BAD.sub(lambda m: "%{:02X}".format(ord(m.group(0))), value))


def tsv(path):
    lines = path.read_text(encoding="utf-8").rstrip("\n").split("\n")[1:]
    return [[c.strip('"<>') for c in line.split("\t")] for line in lines if line]


def generate(run):
    files = {p.name: p for p in run.inputs("wikidata")}
    by_geonames, by_gnd = defaultdict(set), defaultdict(set)
    for gid, item in tsv(files["p1566.tsv"]):
        by_geonames[gid].add(item[len(WD):])
    for gnd, item in tsv(files["p227.tsv"]):
        by_gnd[gnd].add(item[len(WD):])
    articles = defaultdict(dict)
    for item, article in tsv(files["sitelinks.tsv"]):
        m = re.match(r"^https://([a-z]+)\.wikipedia\.org/wiki/(.+)$", article)
        if m and m.group(1) in WIKIS:
            articles[item[len(WD):]][m.group(1)] = urllib.parse.unquote(m.group(2))

    places, geonames, gnd = set(), defaultdict(set), defaultdict(set)
    for s, p, o in run.triples("geo_coordinates"):
        if p == PREFIXES["rdf"] + "type":
            places.add(str(s))
        m = re.match(r"^https?://(?:sws\.)?geonames\.org/([0-9]+)/?$", str(o))
        if m and p == SAME:
            geonames[str(s)].add(m.group(1))
        m = re.match(r"^https?://d-nb\.info/gnd/([0-9]+[0-9X-]*)$", str(o))
        if m and (p == SAME or p.endswith("/gnd#gndIdentifier")):
            gnd[str(s)].add(m.group(1))

    t, stats, item_of = set(), Counter(), {}
    for place in sorted(places):
        a = set().union(*(by_geonames.get(g, set()) for g in geonames[place])) if geonames[place] else set()
        b = set().union(*(by_gnd.get(g, set()) for g in gnd[place])) if gnd[place] else set()
        both = a & b
        if len(b) == 1:
            item = next(iter(b))
            how = "by GND" + ("" if not a else ", GeoNames agrees" if both else ", GeoNames gives another item")
        elif len(b) > 1 and len(both) == 1:
            item, how = next(iter(both)), "by GND and GeoNames (several items by GND)"
        elif not b and len(a) == 1:
            item, how = next(iter(a)), "by GeoNames"
        else:
            why = "several items by GND" if b else "several items by GeoNames" if a else "no item"
            stats[why] += 1
            if why != "no item":
                run.log(f"  {place}: {why}: GeoNames {sorted(a)}, GND {sorted(b)}")
            continue
        if how.endswith("another item"):
            run.log(f"  {place}: GND {item}, GeoNames {sorted(a)}")
        stats[how] += 1
        item_of[place] = item
        s = IRI(place)
        t.add((s, IRI(SAME), IRI(WD + item)))
        arts = articles.get(item, {})
        if "en" in arts:
            t.add((s, IRI(SAME), iri("http://dbpedia.org/resource/" + arts["en"])))
        for lang, title in sorted(arts.items()):
            t.add((s, IRI(TOPIC), iri(f"https://{lang}.wikipedia.org/wiki/{title}")))
    shared = Counter(item_of.values())
    for item, n in sorted(shared.items()):
        if n > 1:
            places_of = ", ".join(p for p, i in sorted(item_of.items()) if i == item)
            run.log(f"  {item} is the item of {n} places: {places_of}")
    run.note(f"{len(places):,} places of geo-coordinates; " + ", ".join(f"{k} {v:,}" for k, v in sorted(stats.items()))
             + f"; {sum(1 for n in shared.values() if n > 1)} items are the item of several places.")
    run.write_turtle("dbp-wiki-geo-linking.ttl.gz", t)

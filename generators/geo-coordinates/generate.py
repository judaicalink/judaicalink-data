"""geo-coordinates: a new version made from the version 2018-08-08 with its systematic errors fixed (decision 0024).

The 2018 lookups cannot be run again (README), so this generator transforms the previous version. Fixes (parameters,
default on):
- namespace_iris: the places had IRIs without a namespace (data/Aachen), which no dataset may coin; they get
  data/geo-coordinates/<the same name>, and every old IRI is stated dcterms:isReplacedBy its new IRI (one each, so
  entity pages and the links of other datasets to the old IRIs stay valid, decision 0022);
- place_type: jl:Place instead of skos:Concept;
- drop_lat_lon: jl:lat/jl:lon of three places (Glogau, Naugard, Rheydt) have the values swapped and repeat their
  geo:asWKT; they are dropped.
Everything else is unchanged. With the fixes off, the output has the same triples as 2018-08-08.
"""

from jl.rdf import IRI, RDF_TYPE
from jl.turtle import PREFIXES

INPUTS = {"previous": "geo-coordinates/2018-08-08"}
PARAMS = {"namespace_iris": True, "place_type": True, "drop_lat_lon": True}

JLO, SKOS, DCT = PREFIXES["jl"], PREFIXES["skos"], PREFIXES["dcterms"]
DATA = "http://data.judaicalink.org/data/"
NS = DATA + "geo-coordinates/"


def generate(run):
    prm = run.params
    out, places, n = set(), set(), {"type": 0, "latlon": 0}
    for s, p, o in run.triples("previous", file="city-geocoor-05.ttl.gz"):
        if not s.startswith(DATA) or "/" in s[len(DATA):]:
            raise ValueError(f"unexpected subject {s}")
        if prm["drop_lat_lon"] and p in (JLO + "lat", JLO + "lon"):
            n["latlon"] += 1
            continue
        if prm["place_type"] and p == RDF_TYPE and o == SKOS + "Concept":
            o = IRI(JLO + "Place")
            n["type"] += 1
        if prm["namespace_iris"]:
            places.add(s)
            s = IRI(NS + s[len(DATA):])
        out.add((s, p, o))
    for s in places:
        out.add((s, IRI(DCT + "isReplacedBy"), IRI(NS + s[len(DATA):])))
    run.note(f"{len(places):,} places moved to {NS} (old IRIs dcterms:isReplacedBy the new ones); "
             f"{n['type']:,} typed jl:Place; {n['latlon']} jl:lat/jl:lon dropped.")
    run.write_turtle("geo-coordinates.ttl.gz", out)

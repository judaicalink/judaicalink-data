"""conflicts: records of one person that state different years or places of birth or death (decision 0045).

The persons are the entity pages (the stable ep: a page and the records it brings together); the facts are those the
sources state, in the stable record and authority datasets, with the normalised dates of records-normalized (the
record's own text, normalised). Place links derived from the text of a place (geo-enriched, records-normalized) are
not facts of the sources and are not compared (decision 0044: a wrong one is fixed in its generator).

A conflict, for one person and one of jl:birthDate, jl:deathDate, jl:birthLocationURI, jl:deathLocationURI:
- years: two years more than one apart (a year apart: calendar conversions, Hebrew years); a record that marks its
  date as uncertain (jl:birthDateUncertain) is left out, and values that are not a plain year, month or day (EDTF
  with X, ~, ?, ranges) too;
- places: two places of the entity pages more than PLACE_KM apart, both settlements (a GeoNames record of feature
  class P among the records of the place page): a country or region against a place in it is no conflict.
One record may conflict with itself (Wikidata with two values).

Each conflict is a dqv:QualityAnnotation and oa:Annotation, data/conflicts/<hash of property and records>:
dcterms:type "conflict", jl:onProperty the property, oa:hasTarget every record of the person that states a value
for it, oa:bodyValue the values per record. The values themselves are in the records; the annotation is about
records, never about the entity page.
"""

import hashlib
import math
import re
from collections import Counter, defaultdict

from jl.generator import slug_of, stable_inputs
from jl.rdf import IRI, Literal, RDF_TYPE
from jl.turtle import PREFIXES

_STABLE = stable_inputs()
SOURCES = stable_inputs(kinds={"records", "authority"})
INPUTS = {**SOURCES,
          "ep": _STABLE["ep"] + "/ep.ttl.gz",
          "dates": _STABLE["records_normalized"] + "/records-normalized-dates.ttl.gz"}
PARAMS = {}

JLO, OWL, SKOS, DCT = PREFIXES["jl"], PREFIXES["owl"], PREFIXES["skos"], PREFIXES["dcterms"]
FOAF = PREFIXES["foaf"]
OA = "http://www.w3.org/ns/oa#"
DQV = "http://www.w3.org/ns/dqv#"
GN = "https://www.geonames.org/ontology#"
JL = "http://data.judaicalink.org/data/"
NS = JL + "conflicts/"
PLACE_KM = 25
KINDS = {"birth": "birth", "death": "death"}
YEAR = re.compile(r"^(-?\d{1,4})(?:-\d{2}(?:-\d{2})?)?$")


def km(a, b):
    (lo1, la1), (lo2, la2) = a, b
    h = (math.sin(math.radians(la2 - la1) / 2) ** 2
         + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(math.radians(lo2 - lo1) / 2) ** 2)
    return 12742 * math.asin(math.sqrt(min(1.0, h)))


def short(record):
    return record[len(JL):] if record.startswith(JL) else record


def generate(run):
    # the entity pages: persons and their records, places and their coordinates, labels and GeoNames records
    members, page_of, wkt, label, persons, gn_members = defaultdict(set), {}, {}, {}, set(), defaultdict(set)
    for s, p, o in run.triples("ep"):
        s = str(s)
        if p in (JLO + "sameAs", OWL + "sameAs"):
            members[s].add(str(o))
            page_of[str(o)] = s
            m = re.match(re.escape(JL) + r"geonames/(\d+)$", str(o))
            if m:
                gn_members[s].add(m.group(1))
        elif p == RDF_TYPE and str(o) == FOAF + "Person":
            persons.add(s)
        elif p.endswith("asWKT") and isinstance(o, Literal):
            m = re.search(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)", o.value)
            if m:
                wkt[s] = (float(m.group(1)), float(m.group(2)))
        elif p == SKOS + "prefLabel" and isinstance(o, Literal) and (s not in label or not o.lang):
            label[s] = o.value
    run.log(f"ep: {len(members):,} pages, {len(persons):,} persons")

    # the facts: years and place IRIs per record
    years, places, uncertain, settlement = defaultdict(set), defaultdict(set), set(), set()
    for name in [*SOURCES, "dates"]:
        for s, p, o in run.triples(name):
            if not p.startswith(JLO):
                if name == "geonames" and p == GN + "featureClass" and str(o).endswith("#P"):
                    settlement.add(str(s).rsplit("/", 1)[-1])
                continue
            local = p[len(JLO):]
            for kind in KINDS:
                if local == kind + "DateUncertain" and isinstance(o, Literal) and o.value == "true":
                    uncertain.add((str(s), kind))
                elif (local == kind + "DateNormalized" or (local == kind + "Date" and slug_of(SOURCES.get(name, ""))
                                                              == "wikidata")) and isinstance(o, Literal):
                    m = YEAR.match(o.value.strip())
                    if m:
                        years[(str(s), kind)].add(int(m.group(1)))
                elif local == kind + "LocationURI" and not isinstance(o, Literal) and name != "dates":
                    places[(str(s), kind)].add(str(o))
    run.log(f"facts: {len(years):,} record years, {len(places):,} record places, {len(uncertain):,} uncertain")

    def is_settlement(page):
        return page in wkt and bool(gn_members.get(page, set()) & settlement)

    t, stats = set(), Counter()
    for page in sorted(persons):
        recs = sorted(r for r in members[page] if r.startswith(JL))
        for kind in KINDS:
            # years
            vals = {r: years[(r, kind)] for r in recs if years.get((r, kind)) and (r, kind) not in uncertain}
            allv = sorted({y for v in vals.values() for y in v})
            if allv and allv[-1] - allv[0] > 1:
                text = "; ".join(f"{short(r)}: {', '.join(map(str, sorted(v)))}" for r, v in sorted(vals.items()))
                annotate(t, JLO + f"{kind}Date", sorted(vals),
                         f"The records of one person state years of {kind} more than a year apart: {text}.")
                stats[f"{kind} year"] += 1
            # places
            pv = {}
            for r in recs:
                pages = {page_of.get(i) for i in places.get((r, kind), ())}
                pages = {x for x in pages if x and is_settlement(x)}
                if pages:
                    pv[r] = pages
            allp = sorted({x for v in pv.values() for x in v})
            far = max((km(wkt[a], wkt[b]) for a in allp for b in allp if a < b), default=0)
            if far > PLACE_KM:
                text = "; ".join(f"{short(r)}: {', '.join(label.get(x, short(x)) for x in sorted(v))}"
                                 for r, v in sorted(pv.items()))
                annotate(t, JLO + f"{kind}LocationURI", sorted(pv),
                         f"The records of one person state places of {kind} up to {far:,.0f} km apart: {text}.")
                stats[f"{kind} place"] += 1
    run.note("Conflicts: " + ", ".join(f"{k} {v:,}" for k, v in sorted(stats.items())) + f"; {len(t):,} triples.")
    run.write_turtle("conflicts.ttl.gz", t)


def annotate(t, prop, records, text):
    h = hashlib.sha1((prop + "\n" + "\n".join(records)).encode("utf-8")).hexdigest()[:16]
    a = IRI(NS + h)
    t.add((a, IRI(RDF_TYPE), IRI(DQV + "QualityAnnotation")))
    t.add((a, IRI(RDF_TYPE), IRI(OA + "Annotation")))
    t.add((a, IRI(DCT + "type"), Literal("conflict")))
    t.add((a, IRI(OA + "motivatedBy"), IRI(DQV + "qualityAssessment")))
    t.add((a, IRI(JLO + "onProperty"), IRI(prop)))
    for r in records:
        t.add((a, IRI(OA + "hasTarget"), IRI(r)))
    t.add((a, IRI(OA + "bodyValue"), Literal(text, lang="en")))

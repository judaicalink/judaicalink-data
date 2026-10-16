"""hhkeydocs: the persons, organisations and places of the Hamburger Schlüsseldokumente zur deutsch-jüdischen
Geschichte (schluesseldokumente.net), from the JSON-LD of the site, true to the source (decision 0026).

Source: inputs:hhkeydocs/jsonld-2026-10-15 (harvest.py): the JSON-LD (schema.org) of every person (by GND number or by
the site's own number), organisation (by GND number) and place (by TGN number) the site lists in its BEACON files,
sitemaps and place list.

IRIs from the site's addresses: data/hhkeydocs/person/gnd/<GND>, data/hhkeydocs/person/<number>,
data/hhkeydocs/organisation/gnd/<GND>, data/hhkeydocs/ort/tgn/<TGN>; every place named in a record (birth and death
places, the places they are contained in) is a place record, by its TGN number. The IRIs of 2025-03-21 were made from
the names; each record of that version is stated dcterms:isReplacedBy the records its jl:describedAt address names
(decision 0022: entity pages keep or split).

Per record, as the JSON-LD gives it: skos:prefLabel and foaf:name; jl:describedAt the page of the site;
owl:sameAs the GND and TGN IRIs the site states, and gndo:gndIdentifier the GND number (as 2025-03-21; gnd-persons-
entityfacts reads it). Persons: foaf:givenName, foaf:familyName, foaf:gender, jl:birthDate and jl:deathDate as given,
jl:birthLocation / jl:deathLocation the name of the place and jl:birthLocationURI / jl:deathLocationURI its record,
jl:hasAbstract the description. Organisations: gndo:dateOfEstablishment / gndo:dateOfTermination, foaf:homepage,
jl:hasAbstract. Places: geosparql:asWKT, gndo:hierarchicalSuperiorOfPlaceOrGeographicName the place it is contained
in (an IRI; 2025-03-21 gave a name). Not taken over (they were not in the source): the VIAF links of 2025-03-21 (looked
up in lobid, all malformed), dcterms:created (the time of that run).
"""

import gzip
import json
import re
from collections import Counter, defaultdict

from jl.iris import canonical_triples
from jl.generator import GeneratorError
from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES

INPUTS = {
    "harvest": "inputs:hhkeydocs/jsonld-2026-10-15/jsonld.jsonl.gz",
    "previous": "hhkeydocs/2025-03-21",
}
PARAMS = {}

NS = "http://data.judaicalink.org/data/hhkeydocs"
SITE = "https://schluesseldokumente.net"
GND = "http://d-nb.info/gnd/"
TGN = "http://vocab.getty.edu/tgn/"
GNDO = "http://d-nb.info/standards/elementset/gnd#"   # as in 2025-03-21 and the other datasets
WKT = "http://www.opengis.net/ont/geosparql#asWKT"
JLO, FOAF, SKOS, OWL, DCT = (PREFIXES[p] for p in ("jl", "foaf", "skos", "owl", "dcterms"))
GENDER = {"http://schema.org/Male": "male", "http://schema.org/Female": "female"}
GND_NUMBER = re.compile(r"^https?://d-nb\.info/gnd/([0-9]+[0-9X-]*)$")
TGN_NUMBER = re.compile(r"^https?://vocab\.getty\.edu/tgn/([0-9]+)$")


def as_list(v):
    return v if isinstance(v, list) else [] if v is None else [v]


def same_as(d):
    """{"gnd": [...], "tgn": [...], "other": [...]} of the sameAs values of a JSON-LD node."""
    out = defaultdict(list)
    for v in as_list(d.get("sameAs")):
        v = str(v).strip()
        if m := GND_NUMBER.match(v):
            out["gnd"].append(m.group(1))
        elif m := TGN_NUMBER.match(v):
            out["tgn"].append(m.group(1))
        elif v:
            out["other"].append(v)
    return out


def text(v):
    v = re.sub(r"\s+", " ", str(v or "")).strip()
    return v or None


def wkt(geo):
    """'Point ( +lng +lat)' from the coordinates as given (the form of 2025-03-21 and geo-coordinates)."""
    if not isinstance(geo, dict) or geo.get("latitude") in (None, "") or geo.get("longitude") in (None, ""):
        return None
    s = lambda x: str(x).strip() if str(x).strip().startswith("-") else "+" + str(x).strip()
    return f"Point ( {s(geo['longitude'])} {s(geo['latitude'])})"


class Places:
    """The places named anywhere, by TGN number: the data of the place's own page, else of its first mention."""

    def __init__(self):
        self.data, self.own, self.conflicts, self.no_tgn = {}, set(), Counter(), Counter()

    def add(self, d, own=False):
        """The IRI of a place node (and of the places it is contained in), or None if it has no TGN number."""
        if not isinstance(d, dict):
            return None
        tgns = same_as(d)["tgn"]
        if len(tgns) != 1:
            self.no_tgn["several TGN numbers" if tgns else "no TGN number"] += 1
            return None
        n = tgns[0]
        parent = self.add(d.get("containedInPlace"))
        rec = {"name": text(d.get("name")), "wkt": wkt(d.get("geo")), "gnd": sorted(set(same_as(d)["gnd"])),
               "parent": parent, "other": same_as(d)["other"]}
        if own or n not in self.data:
            self.data[n] = rec
            if own:
                self.own.add(n)
        elif n not in self.own and self.data[n] != rec:
            self.conflicts["different data for the same place in two mentions"] += 1
        return IRI(f"{NS}/ort/tgn/{n}")


def generate(run):
    pages = {}
    status = Counter()
    with gzip.open(run.input("harvest"), "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            status[r["status"]] += 1
            if r["status"] == 200:
                pages[r["address"]] = json.loads(r["text"])
            else:
                run.log("no page:", r["address"], r["status"])
    run.log("pages by HTTP status:", dict(status))

    places = Places()
    for a in sorted(pages):   # the places' own pages first, so that their data is taken
        if a.startswith("/ort/tgn/"):
            n = a.rsplit("/", 1)[1]
            if same_as(pages[a])["tgn"] != [n]:
                run.log("place page whose TGN number differs from its address:", a, same_as(pages[a])["tgn"])
            places.add(pages[a], own=True)

    t = set()
    add = lambda s, p, o: o is not None and t.add((s, IRI(p), o))
    stats = Counter()
    others = Counter()

    def common(s, d, a, gnd_from_address=None):
        name = text(d.get("name"))
        add(s, SKOS + "prefLabel", Literal(name) if name else None)
        add(s, FOAF + "name", Literal(name) if name else None)
        add(s, JLO + "describedAt", IRI(SITE + a))
        sa = same_as(d)
        gnds = sorted(set(sa["gnd"]) | ({gnd_from_address} if gnd_from_address else set()))
        if gnd_from_address and gnd_from_address not in sa["gnd"]:
            stats["GND number of the address not in sameAs"] += 1
        for g in gnds:
            add(s, OWL + "sameAs", IRI(GND + g))
            add(s, GNDO + "gndIdentifier", Literal(g))
        for v in sa["tgn"]:
            add(s, OWL + "sameAs", IRI(TGN + v))
        for v in sa["other"]:
            others[re.sub(r"^(https?://[^/]+).*", r"\1", v)] += 1
            if re.match(r"^https?://\S+$", v):
                add(s, OWL + "sameAs", IRI(v))
        desc = text(d.get("description"))
        add(s, JLO + "hasAbstract", Literal(desc) if desc else None)

    for a, d in sorted(pages.items()):
        if a.startswith("/person/"):
            s = IRI(NS + a)
            m = re.match(r"^/person/gnd/(.+)$", a)
            t.add((s, IRI(RDF_TYPE), IRI(FOAF + "Person")))
            common(s, d, a, m.group(1) if m else None)
            stats["persons" + (" (GND)" if m else " (site number)")] += 1
            for k, p in (("givenName", "givenName"), ("familyName", "familyName")):
                v = text(d.get(k))
                add(s, FOAF + p, Literal(v) if v else None)
            if d.get("gender") in GENDER:
                add(s, FOAF + "gender", Literal(GENDER[d["gender"]]))
            elif d.get("gender"):
                stats["unknown gender value"] += 1
            for k, p in (("birthDate", "birthDate"), ("deathDate", "deathDate")):
                v = text(d.get(k))
                add(s, JLO + p, Literal(v) if v else None)
            for k, p in (("birthPlace", "birth"), ("deathPlace", "death")):
                pl = d.get(k)
                if not isinstance(pl, dict):
                    continue
                name = text(pl.get("name"))
                add(s, JLO + p + "Location", Literal(name) if name else None)
                u = places.add(pl)
                add(s, JLO + p + "LocationURI", u)
                stats[f"{p} places" + ("" if u else " without TGN number")] += 1
        elif a.startswith("/organisation/gnd/"):
            s = IRI(NS + a)
            t.add((s, IRI(RDF_TYPE), IRI(FOAF + "Organization")))
            common(s, d, a, a.rsplit("/", 1)[1])
            stats["organisations"] += 1
            for k, p in (("foundingDate", "dateOfEstablishment"), ("dissolutionDate", "dateOfTermination")):
                v = text(d.get(k))
                add(s, GNDO + p, Literal(v) if v else None)
            url = text(d.get("url"))
            if url and re.match(r"^https?://\S+$", url):
                add(s, FOAF + "homepage", IRI(url))
            for k in d:
                if k not in {"@context", "@type", "name", "description", "sameAs", "foundingDate",
                             "dissolutionDate", "url"}:
                    stats[f"organisation key not taken over: {k}"] += 1
        elif not a.startswith("/ort/tgn/"):
            raise GeneratorError(f"unknown address {a}")

    for n, rec in sorted(places.data.items()):
        s = IRI(f"{NS}/ort/tgn/{n}")
        t.add((s, IRI(RDF_TYPE), IRI(GNDO + "PlaceOrGeographicName")))
        if rec["name"]:
            add(s, SKOS + "prefLabel", Literal(rec["name"]))
            add(s, FOAF + "name", Literal(rec["name"]))
        add(s, OWL + "sameAs", IRI(TGN + n))
        for g in rec["gnd"]:
            add(s, OWL + "sameAs", IRI(GND + g))
        add(s, WKT, Literal(rec["wkt"]) if rec["wkt"] else None)
        add(s, GNDO + "hierarchicalSuperiorOfPlaceOrGeographicName", rec["parent"])
        if n in places.own:
            add(s, JLO + "describedAt", IRI(f"{SITE}/ort/tgn/{n}"))
    stats["places"] = len(places.data)
    stats["places with a page of their own"] = len(places.own)

    # the records of the previous version, replaced by the records their jl:describedAt addresses name
    records = {str(s) for s in {s for s, p, o in t if p == RDF_TYPE}}
    old_types, old_pages = defaultdict(set), defaultdict(set)
    for s, p, o in run.triples("previous"):
        if p == RDF_TYPE:
            old_types[str(s)].add(str(o))
        elif p == JLO + "describedAt":
            m = re.match(r"^https?://schluesseldokumente\.net(/.+?)(\.jsonld)?$", str(o.value if isinstance(o, Literal)
                                                                                     else o))
            if m:
                old_pages[str(s)].add(NS + m.group(1))
    rep = Counter()
    for s in sorted(old_types):
        new = sorted(x for x in old_pages.get(s, ()) if x in records)
        missing = sorted(x for x in old_pages.get(s, ()) if x not in records)
        for x in new:
            t.add((IRI(s), IRI(DCT + "isReplacedBy"), IRI(x)))
        rep["replaced by one record" if len(new) == 1 else "replaced by several records" if new
            else "replaced by none"] += 1
        if len(new) != 1:
            run.log("previous record replaced by", len(new), "records:", s, new, "not found:", missing)
        elif missing:
            run.log("previous record: part of its addresses not found:", s, missing)

    for k, v in sorted(places.conflicts.items()) + sorted(places.no_tgn.items()):
        stats[f"places: {k}"] = v
    run.note(f"{dict(sorted(stats.items()))}; previous records: {dict(sorted(rep.items()))}; sameAs targets other "
             f"than GND and TGN: {dict(sorted(others.items())) or 'none'}.")
    run.write_turtle("hhkeydocs.ttl.gz", set(canonical_triples(t)))   # docs/iri-forms.md

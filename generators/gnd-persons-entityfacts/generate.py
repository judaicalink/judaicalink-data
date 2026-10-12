"""gnd-persons-entityfacts: GND records (DNB EntityFacts) for the persons of hhkeydocs, nrwbibdjg and gba that
gnd-persons lacks.

Transformation only, a port of gnd_persons_entityfacts of kg-complements (datasets_algorithmic.py, 2026-10-06; decision
0020) without changes to its logic, with one fix (parameter fix_self_links, default on): EntityFacts gives JudaicaLink
IRIs in the https form (https://data.judaicalink.org/data/gnd/<n>, from our BEACON); they are normalised to http, and
a link of a record to itself is dropped. The EntityFacts answers come from the cache of 2026-10-06; an answer missing
there is an error, never a live request.
"""

import hashlib
import json
import re
from collections import Counter, defaultdict

from jl.generator import GeneratorError
from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES

INPUTS = {
    "gnd_persons": "gnd-persons/2018-11-29",
    "hhkeydocs": "hhkeydocs/2025-03-21",
    "nrwbibdjg": "nrwbibdjg/2024-05-24",
    "gba": "gba/2025-03-21",
    "cache": "inputs:web-caches/api-cache-2026-10-06/",
}
PARAMS = {"fix_self_links": True}

JLO = PREFIXES["jl"]
OWL = PREFIXES["owl"]
FOAF = PREFIXES["foaf"]
SKOS = PREFIXES["skos"]
GNDO = "http://d-nb.info/standards/elementset/gnd#"
DATA = "http://data.judaicalink.org/data/"
ENTITYFACTS = "https://hub.culturegraph.org/entityfacts/"


def cached(files, url):
    key = hashlib.sha1((url + "?" + json.dumps(None, sort_keys=True)).encode()).hexdigest()
    p = files.get(f"{key}.json")
    if p is None:
        raise GeneratorError(f"no cached answer for {url} (an acquisition step would have to query it)")
    return json.loads(p.read_text())


def generate(run):
    have = {str(s).rsplit("/", 1)[-1] for s, p, o in run.triples("gnd_persons")}
    numbers = defaultdict(set)   # GND number -> datasets
    for ds in ("hhkeydocs", "nrwbibdjg", "gba"):
        for s, p, o in run.triples(ds):
            if p == GNDO + "gndIdentifier" and isinstance(o, Literal):
                gnd = o.value.strip()
                if re.fullmatch(r"[0-9X-]+", gnd) and gnd not in have:
                    numbers[gnd].add(ds)
    files = {p.name: p for p in run.inputs("cache")}
    t = set()
    stats = Counter()
    for gnd in sorted(numbers):
        ef = cached(files, ENTITYFACTS + gnd)
        if not ef or ef.get("@type") not in ("person", "Person"):
            stats["no entityfacts person record"] += 1
            continue
        x = IRI(DATA + f"gnd/{gnd}")
        stats["persons"] += 1
        t |= {(x, IRI(RDF_TYPE), IRI(FOAF + "Person")), (x, IRI(OWL + "sameAs"), IRI(f"http://d-nb.info/gnd/{gnd}")),
              (x, IRI(GNDO + "gndIdentifier"), Literal(gnd))}
        if ef.get("preferredName"):
            t.add((x, IRI(SKOS + "prefLabel"), Literal(ef["preferredName"])))
        for v in ef.get("variantName", []) or []:
            t.add((x, IRI(SKOS + "altLabel"), Literal(v)))
        if ef.get("dateOfBirth"):
            t.add((x, IRI(JLO + "birthDate"), Literal(ef["dateOfBirth"])))
        if ef.get("dateOfDeath"):
            t.add((x, IRI(JLO + "deathDate"), Literal(ef["dateOfDeath"])))
        for key, prop in (("placeOfBirth", "birthLocation"), ("placeOfDeath", "deathLocation")):
            for place in ef.get(key, []) or []:
                if place.get("preferredName"):
                    t.add((x, IRI(JLO + prop), Literal(place["preferredName"])))
        for occ in ef.get("professionOrOccupation", []) or []:
            if occ.get("preferredName"):
                t.add((x, IRI(JLO + "occupation"), Literal(occ["preferredName"])))
        if ef.get("biographicalOrHistoricalInformation"):
            t.add((x, IRI(JLO + "hasAbstract"), Literal(ef["biographicalOrHistoricalInformation"], lang="de")))
        for same in ef.get("sameAs", []) or []:
            sid = same.get("@id", "")
            if sid.startswith("http") and "d-nb.info/gnd" not in sid:
                if run.params["fix_self_links"] and sid.startswith("https://data.judaicalink.org/"):
                    sid = "http://" + sid[len("https://"):]
                    if sid == x:
                        stats["self links dropped"] += 1
                        continue
                    stats["https links normalised"] += 1
                t.add((x, IRI(OWL + "sameAs"), IRI(sid)))
    run.note(f"GND numbers of hhkeydocs, nrwbibdjg and gba not in gnd-persons: {len(numbers):,}; "
             f"{dict(sorted(stats.items()))}.")
    run.write_turtle("gnd-persons-entityfacts.ttl.gz", sorted(t))

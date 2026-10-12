"""footprints: a new version made from the version 2024-03-18 with its systematic errors fixed (decision 0024).

The Footprints API is behind a bot challenge since 2025, so this generator transforms the previous version (the
generator of 2024 cannot be run again; the persons-only version 2025-03-21 lacks the books and places). Fixes
(parameters, default on):
- identifier_iris: owl:sameAs states VIAF, GND and LOC as text (all 2,971); they become IRIs, and the 673 values
  "None" (a VIAF record without a GND number) are dropped;
- relation_iris: authors, publishers, printers, editors, ... of the books are the IRIs of footprints resources
  written as text; they become IRIs; gndo:ditor (a typo) becomes gndo:editor;
- dict_dates: the book loop wrote the dates of its persons as the text of a Python dictionary, and the birth date
  as jl:deathDate ({'id': 996, 'edtf_format': '1663/1711', ...}); where the person loop states the same EDTF value
  for the person, the duplicate is dropped; otherwise the EDTF value is stated, the earlier of two as jl:birthDate;
- nameless: the resource named "" (the hash of the empty name) joins the books whose author or publisher has no
  name; it is dropped with the links to it;
- run_times: dcterms:created is the time of the 2024 run for each resource, not data; dropped;
- empty_values: empty abstracts and the value "None" (jl:describedAt, gndo:associatedPlace) are dropped; two
  jl:describedAt with the address prefix doubled are repaired;
- wkt: geosparql:asWKT starts with a stray quote ("Point ( +9.87 +53.57)) and writes negative numbers as "+-";
  both repaired, in the form of geo-coordinates ("Point ( +9.87 +53.57)").
Everything else is unchanged. With the fixes off, the output has the same triples as 2024-03-18.
"""

import ast
import re
from collections import Counter, defaultdict

from jl.generator import GeneratorError
from jl.rdf import IRI, Literal

INPUTS = {"previous": "footprints/2024-03-18"}
PARAMS = {"identifier_iris": True, "relation_iris": True, "dict_dates": True, "nameless": True,
          "run_times": True, "empty_values": True, "wkt": True}

NS = "http://data.judaicalink.org/data/footprints/"
NAMELESS = NS + "601d1428-1903-5260-9b76-515a93e2930c"   # uuid5(NAMESPACE_OID, sha256("")), the 2024 IRI rule
JLO = "http://data.judaicalink.org/ontology/"
GNDO = "http://d-nb.info/standards/elementset/gnd#"      # as in the 2024 file
SAME = "http://www.w3.org/2002/07/owl#sameAs"
CREATED = "http://purl.org/dc/terms/created"
WKT = "http://www.opengis.net/ont/geosparql#asWKT"
BIRTH, DEATH = JLO + "birthDate", JLO + "deathDate"
DESCRIBED = JLO + "describedAt"
IDENTIFIER = re.compile(r"https?://(viaf\.org/viaf|d-nb\.info/gnd|id\.loc\.gov/authorities/names)/[0-9A-Za-z-]+/?")
DOUBLED = re.compile(r"^(https://[^/]+/[a-z]+/)\1")


def text(o):
    return o.value if isinstance(o, Literal) else None


def generate(run):
    prm = run.params
    n = Counter()
    dicts = defaultdict(list)                     # person -> [(edtf, triple)] of the dictionary dates
    plain = defaultdict(set)                      # person -> EDTF values stated by the person loop
    out = set()
    for s, p, o in run.triples("previous", file="footprints.ttl.gz"):
        v = text(o)
        if prm["nameless"] and NAMELESS in (s, v):
            n["nameless, own" if s == NAMELESS else "nameless, links"] += 1
            continue
        if prm["run_times"] and p == CREATED:
            n["run times"] += 1
            continue
        if prm["empty_values"] and v is not None:
            if v.strip() == "" or (v == "None" and p != SAME):
                n["empty values"] += 1
                continue
            if p == DESCRIBED and DOUBLED.match(v):
                o = Literal(DOUBLED.sub(r"\1", v), o.datatype, o.lang)
                n["describedAt repaired"] += 1
        if prm["identifier_iris"] and p == SAME and v is not None:
            if v == "None":
                n["sameAs None"] += 1
                continue
            if not IDENTIFIER.fullmatch(v):
                raise GeneratorError(f"{s}: owl:sameAs {v!r} is no VIAF, GND or LOC address")
            o = IRI(v)
            n["sameAs as IRI"] += 1
        if prm["relation_iris"] and v is not None and p != DESCRIBED and v.startswith(NS):
            o = IRI(v)
            n["relations as IRI"] += 1
        if prm["relation_iris"] and p == GNDO + "ditor":
            p = IRI(GNDO + "editor")
            n["ditor"] += 1
        if prm["wkt"] and p == WKT and v is not None:
            o = Literal(v.lstrip('"').replace("+-", "-"), o.datatype, o.lang)
            n["wkt"] += 1
        if prm["dict_dates"] and p in (BIRTH, DEATH) and v is not None:
            if v.startswith("{"):
                dicts[s].append((ast.literal_eval(v)["edtf_format"], (s, p, o)))
                continue
            plain[s].add(v)
        out.add((s, p, o))

    for s, ds in dicts.items():
        rest = sorted(e for e, _t in ds if e not in plain[s])
        n["dictionary dates, same as the person loop"] += len(ds) - len(rest)
        if not rest:
            continue
        if len(rest) != 2 or len(ds) != 2:
            raise GeneratorError(f"{s}: dictionary dates {[e for e, _t in ds]} next to {sorted(plain[s])}")
        out.add((s, IRI(BIRTH), Literal(rest[0])))
        out.add((s, IRI(DEATH), Literal(rest[1])))
        n["dictionary dates, as EDTF"] += 2

    for k, c in sorted(n.items()):
        run.log(f"{k}: {c:,}")
    if any(prm.values()):
        run.note(f"{n['sameAs as IRI']:,} owl:sameAs as IRIs, {n['sameAs None']} 'None' dropped; "
                 f"{n['relations as IRI']:,} relations as IRIs ({n['ditor']} gndo:ditor as gndo:editor); "
                 f"{n['dictionary dates, same as the person loop']} dictionary dates dropped as duplicates, "
                 f"{n['dictionary dates, as EDTF']} stated as EDTF; the nameless resource and its "
                 f"{n['nameless, links']} links dropped; {n['run times']:,} run times dropped; "
                 f"{n['empty values']} empty or 'None' values dropped, {n['describedAt repaired']} addresses "
                 f"repaired; {n['wkt']} WKT points repaired.")
    run.write_turtle("footprints.ttl.gz", out)

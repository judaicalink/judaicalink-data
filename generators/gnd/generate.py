"""gnd: the records of the GND that JudaicaLink uses (decision 0029), made from the dumps of the DNB.

1. The selection list (gnd-selection.tsv.gz): one row per GND number and reason, with the current number the GND
   gives for it.
   - linked, replaces, …: the selection of the cascade (jl.cascade): every GND number our datasets link (every
     statement) or another authority dataset links (its declared identity), with the dataset as detail; the static
     lists below are its seeds (lookup.py).
   - area-occupation (parameter area_rule): the rule of gnd-persons 2017, applied to the current GND: a
     differentiated person (gndo:DifferentiatedPerson) with the geographic area code XB-IL (Israel) or XY (Jews) and at
     least one occupation (gndo:professionOrOccupation). The occupation ontology that limited the occupations in 2017
     is not on file for the GND (only its DBpedia part), so the rule takes any occupation.
   - freimann, ubffm-authors: the lists of UB Frankfurt that selected persons for gnd-persons (input
     gnd/ubffm-lists-2018); the detail of ubffm-authors is the PPN of the UB record.
   - previous: every record of gnd-persons 2018-11-29, so that no data/gnd/ IRI loses its description.
   A number the GND has redirected is resolved to its current number (redirect file and dnb:deprecatedUri); a deleted
   number has no current number.
2. The data (gnd.ttl.gz): every current record named by the list, read from the GND dump in one pass. Each record
   data/gnd/<n> keeps the GND's statements (subject replaced by the record IRI, IRIs in canonical form, jl.iris) and
   gets owl:sameAs <https://d-nb.info/gnd/<n>>, the standard and JudaicaLink terms the other datasets use (classes,
   skos:prefLabel/altLabel, jl:birthDate/deathDate, jl:birthLocation(URI)/deathLocation(URI), jl:occupationURI: the GND lists
   occupations in an rdf:Seq; their names and links are in the dataset occupations), the
   geometry as geo:asWKT, and the links of EntityFacts to other authority files. Left out: the description document
   (…/about, licence, dates of change), the qualified relations (gndo:hasRelation, blank nodes) and the GND's
   owl:sameAs and dnb:deprecatedUri to its own former numbers, which become:
3. Replacements (decision 0029): <https://d-nb.info/gnd/<old>> dcterms:isReplacedBy <https://d-nb.info/gnd/<n>> for
   every former number of an included record; where we have our own entity for the old number (data/gnd/<old> in
   gnd-persons 2018 or in a linked dataset), also data/gnd/<old> dcterms:isReplacedBy data/gnd/<n>; and
   <https://d-nb.info/gnd/<old>> owl:deprecated true for deleted numbers that our data cites.
"""

import csv
import gzip
import io
import json
import re
from collections import Counter, defaultdict

from jl import authorities, cascade, classes, identifiers
from jl.generator import GeneratorError
from jl.iris import WKT, canonical, canonical_wkt
from jl.rdf import IRI, RDF_TYPE, XSD, BNode, Literal, parse_ntriples, unescape_string
from jl.turtle import PREFIXES

# the datasets whose GND links are the core: our datasets and the other authority datasets (jl.authorities)
LINKED = authorities.linking_inputs("gnd")
INPUTS = {
    "lds": "inputs:gnd/lds-2026-02-17/authorities-gnd_lds_20260217.nt.gz",
    "entityfacts": "inputs:gnd/entityfacts-2026-10-13/authorities-gnd_entityfacts_20261013.ndjson.gz",
    "redirects": "inputs:gnd/redirects-2026-10-13/authorities-gnd_umlenk_loesch_20261013.jsonld.gz",
    "freimann": "inputs:gnd/ubffm-lists-2018/Freimann-GND-03.rdf",
    "ubffm_authors": "inputs:gnd/ubffm-lists-2018/tp-records_gnd-ids.csv",
    "previous": "gnd-persons/2018-11-29",
    "selection": cascade.selection_input("gnd"),   # the selection of the cascade (jl cascade)
    **LINKED,   # for our own records data/gnd/<n> (replacements of our IRIs)
}
# area_rule: "occupation" (the 2017 rule with any occupation) or "off"
PARAMS = {"area_rule": "off",   # decided 2026-10-16: off (see README)
          "drop_placeholders": True}   # EntityFacts links with an unfilled "[ID]" (2026-10-18; off: as 2026-10-16)
REASONS = ["linked", "replaces", "area-occupation", "freimann", "ubffm-authors", "previous"]   # replaces: the current number of a selected one (jl.cascade)

JL = "http://data.judaicalink.org/data/"
GND = "https://d-nb.info/gnd/"
GNDO = "https://d-nb.info/standards/elementset/gnd#"
DNB = "https://d-nb.info/standards/elementset/dnb#"
JLO, SKOS, OWL, FOAF, DCT, GEO = (PREFIXES[p] for p in ("jl", "skos", "owl", "foaf", "dcterms", "geosparql"))
SAME, REPLACED = OWL + "sameAs", DCT + "isReplacedBy"
RDF = RDF_TYPE[:-len("type")]

NUMBER = r"[0-9]+[0-9X-]*"
GND_IRI = re.compile(r"^https?://d-nb\.info/gnd/(" + NUMBER + r")(?:/about.*)?/?$", re.I)
JL_GND = re.compile("^" + re.escape(JL) + r"gnd/(" + NUMBER + ")$")
SUBJECT = re.compile(r"^<https://d-nb\.info/gnd/(" + NUMBER + r")(?:/about)?>")
DEPRECATED = re.compile(r'dnb#deprecatedUri> "https://d-nb\.info/gnd/(' + NUMBER + ')"')
FORMER = re.compile(r'owl#sameAs> <https://d-nb\.info/gnd/(' + NUMBER + ')>')
NAME_OF = re.compile(r'<https://d-nb\.info/gnd/(' + NUMBER + r')> <https://d-nb\.info/standards/elementset/gnd#'
                     r'preferredNameForThePlaceOrGeographicName> "((?:[^"\\]|\\.)*)"')

# GND classes and the classes the entity pages know (ep CLASS_OF_TYPE); the GND's own classes stay as given
PERSON = {"DifferentiatedPerson", "UndifferentiatedPerson", "Pseudonym", "RoyalOrMemberOfARoyalHouse",
          "CollectivePseudonym"}
ORGANISATION = {"CorporateBody", "Company", "FictiveCorporateBody", "MusicalCorporateBody", "OrganOfCorporateBody",
                "ProjectOrProgram", "ReligiousAdministrativeUnit", "ReligiousCorporateBody"}
PLACE = {"PlaceOrGeographicName", "AdministrativeUnit", "BuildingOrMemorial", "Country", "ExtraterrestrialTerritory",
         "MemberState", "NameOfSmallGeographicUnitLyingWithinAnotherGeographicUnit", "NaturalGeographicUnit",
         "ReligiousTerritory", "TerritorialCorporateBodyOrAdministrativeUnit", "WayBorderOrLine"}
WORK = {"Work", "Collection", "CollectiveManuscript", "Expression", "Manuscript", "MusicalWork",
        "ProvenanceCharacteristic", "VersionOfAMusicalWork"}
BAD_IRI = re.compile(r'[<>"{}|^`\\\s]')
LEFT_OUT = {"http://www.w3.org/2007/05/powder-s#describedby", DNB + "deprecatedUri", GNDO + "hasRelation",
            GEO + "hasGeometry"}


def number(s):
    return s.strip().upper()


def gnd_number(term):
    """The GND number of an IRI (d-nb.info/gnd/<n> in any form, or our record data/gnd/<n>), else None."""
    m = GND_IRI.match(term) or JL_GND.match(term)
    return number(m.group(1)) if m else None


def select(run):
    """The selection rows [(number, reason, detail)] from the cascade (jl cascade: the numbers our datasets and the
    other authority datasets link, and the static lists of lookup.py: freimann, ubffm-authors, previous); except
    area-occupation, which is decided while reading the dump; and our own entities data/gnd/<n> (numbers)."""
    rows, own = set(), set()
    for _src, n, _cur, reason, detail in cascade.selection_rows(run.input("selection")):
        rows.add((n, reason, detail))
    for name in LINKED:   # our own records data/gnd/<n> (for the replacements of our IRIs)
        for s, _p, o in run.triples(name):
            for term in (s, o):
                if isinstance(term, str) and term.startswith(JL + "gnd/"):
                    n = gnd_number(term)
                    if n:
                        own.add(n)
    for s, _p, _o in run.triples("previous"):
        n = gnd_number(s) if s.startswith(JL) else None
        if n:
            own.add(n)
    return rows, own


def redirects(run):
    """{old: current} and {deleted} from the redirect file (chains followed)."""
    to, deleted = {}, set()
    with gzip.open(run.input("redirects"), "rt", encoding="utf-8") as f:
        for o in json.load(f):
            n = gnd_number(o["@id"])
            if "http://www.w3.org/2002/07/owl#sameAs" in o:
                to[n] = gnd_number(o["http://www.w3.org/2002/07/owl#sameAs"][0]["@id"])
            elif DNB + "DeletedResource" in o.get("@type", []):
                deleted.add(n)
    for n in list(to):   # follow chains (at most a few steps)
        seen = {n}
        while to[n] in to and to[n] not in seen:
            seen.add(to[n])
            to[n] = to[to[n]]
    return to, deleted


def blocks(path):
    """The records of the dump: (number, lines), the lines of the record, its description and its blank nodes."""
    current, lines = None, []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            m = SUBJECT.match(line)
            n = m.group(1) if m else current   # blank nodes belong to the record before them
            if n != current:
                if current is not None:
                    yield current, lines
                current, lines = n, []
            lines.append(line)
    if current is not None:
        yield current, lines


def area_rule(text):
    if GNDO + "DifferentiatedPerson>" not in text or GNDO + "professionOrOccupation>" not in text:
        return None
    for code in ("XB-IL", "XY"):
        if f"geographic-area-code#{code}>" in text:
            return code
    return None


def entityfacts(run, wanted):
    """{number: [IRIs]}: the links of EntityFacts for the wanted numbers."""
    out = {}
    first_id = re.compile(r'"@id"\s*:\s*"https://d-nb\.info/gnd/(' + NUMBER + ')"')
    with gzip.open(run.input("entityfacts"), "rt", encoding="utf-8") as f:
        for line in f:
            m = first_id.search(line)
            if not m or number(m.group(1)) not in wanted:
                continue
            d = json.loads(line)
            out[number(m.group(1))] = sorted({x["@id"] for x in d.get("sameAs", []) if "@id" in x})
    return out


def literal(o):
    return Literal(o.value, None, o.lang) if isinstance(o, Literal) else None


def generate(run):
    if run.params["area_rule"] not in ("occupation", "off"):
        raise GeneratorError(f"area_rule must be 'occupation' or 'off', not {run.params['area_rule']!r}")
    rows, own = select(run)
    to, deleted = redirects(run)
    listed = {n for n, _r, _d in rows}
    wanted = {to.get(n, n) for n in listed if n not in deleted}
    run.log(f"listed {len(listed):,} numbers; {sum(1 for n in listed if n in to):,} redirected, "
            f"{sum(1 for n in listed if n in deleted):,} deleted")

    # the dump: select the records, keep their lines; names of places for the literals
    kept, names, former_of, area = {}, {}, defaultdict(set), {}
    for n, lines in blocks(run.input("lds")):
        text = "".join(lines)
        if "preferredNameForThePlaceOrGeographicName" in text:
            for m in NAME_OF.finditer(text):
                names[number(m.group(1))] = unescape_string(m.group(2))
        formers = set(DEPRECATED.findall(text)) | set(FORMER.findall(text))
        code = area_rule(text) if run.params["area_rule"] == "occupation" else None
        if n in wanted or formers & listed or code:
            kept[n] = text
            former_of[n] = {number(x) for x in formers}
            if code:
                area[n] = code
    for n, code in area.items():
        rows.add((n, "area-occupation", code))
    found = set(kept)
    # numbers listed whose current record is not in the dump (and not reached through a former number)
    reached = {x for n in found for x in former_of[n]} | found
    missing = sorted(n for n in listed if n not in reached and to.get(n) not in found and n not in deleted)
    run.log(f"dump: {len(found):,} records kept ({len(area):,} by the area rule); {len(names):,} names; "
            f"{len(missing):,} listed numbers in neither dump nor redirect file")
    for n in missing[:200]:
        run.log("unknown number:", n)

    links = entityfacts(run, found)
    placeholders = Counter()
    t, rec_of = set(), {}
    for n in sorted(found):
        rec = IRI(JL + "gnd/" + n)
        rec_of[n] = rec
        t.add((rec, IRI(SAME), IRI(GND + n)))
        triples = list(parse_ntriples(kept[n].splitlines()))
        # the GND gives the occupations as a list (an rdf:Seq, a blank node): its members as statements of the record
        members = defaultdict(list)
        for s, p, o in triples:
            if isinstance(s, BNode) and p.startswith(RDF + "_") and p[len(RDF) + 1:].isdigit():
                members[s].append((int(p[len(RDF) + 1:]), o))
        expanded = []
        for s, p, o in triples:
            if isinstance(o, BNode) and o in members:
                expanded += [(s, p, m) for _i, m in sorted(members[o])]
            else:
                expanded.append((s, p, o))
        for s, p, o in dict.fromkeys(expanded):
            if not s.startswith(GND) or s.endswith("/about") or p in LEFT_OUT:
                if p == GEO + "hasGeometry":
                    continue
                if p == GEO + "asWKT" and not s.startswith(GND):   # the geometry (a blank node) of the record
                    t.add((rec, IRI(p), Literal(canonical_wkt(o.value), WKT)))
                continue
            if isinstance(o, BNode):
                continue   # qualified variant names and the like (blank nodes): left out
            if p == SAME and isinstance(o, str) and gnd_number(o) in former_of[n]:
                continue   # a former number: stated as a replacement below
            if isinstance(o, str) and not isinstance(o, Literal):
                o = IRI(canonical(o))
            t.add((rec, IRI(p), o))
            local = p[len(GNDO):] if p.startswith(GNDO) else None
            if p == RDF_TYPE and o.startswith(GNDO):
                c = o[len(GNDO):]
                for group, cls in ((PERSON, FOAF + "Person"), (ORGANISATION, FOAF + "Organization"),
                                   (PLACE, classes.PLACE), (WORK, classes.WORK)):
                    if c in group:
                        t.add((rec, IRI(RDF_TYPE), IRI(cls)))
            elif local and local.startswith("preferredNameFor"):
                t.add((rec, IRI(SKOS + "prefLabel"), literal(o)))
            elif local and local.startswith("variantNameFor") and isinstance(o, Literal):
                t.add((rec, IRI(SKOS + "altLabel"), literal(o)))
            elif local in ("dateOfBirth", "dateOfDeath") and isinstance(o, Literal):
                t.add((rec, IRI(JLO + ("birthDate" if local == "dateOfBirth" else "deathDate")), Literal(o.value)))
            elif local in ("placeOfBirth", "placeOfDeath") and not isinstance(o, Literal):
                which = "birth" if local == "placeOfBirth" else "death"
                t.add((rec, IRI(JLO + which + "LocationURI"), o))
                name = names.get(gnd_number(o))
                if name:
                    t.add((rec, IRI(JLO + which + "Location"), Literal(name)))
            elif local == "professionOrOccupation" and not isinstance(o, Literal):
                t.add((rec, IRI(JLO + "occupationURI"), o))   # its names and links: the dataset occupations
        for x in links.get(n, []):
            if run.params["drop_placeholders"] and "[ID]" in x:
                placeholders[x] += 1   # a BEACON link template, the same IRI for every record (e.g. epidat)
                continue
            x = BAD_IRI.sub(lambda m: "%{:02X}".format(ord(m.group(0))), x.strip().strip('"'))
            if gnd_number(x) is None and re.match(r"^https?://[^/]+/", x) and not identifiers.is_ours(x):
                # not the GND itself (record, description, former numbers), not JudaicaLink (from our BEACON, 0029)
                t.add((rec, IRI(SAME), IRI(canonical(x))))

    # replacements and deletions (decision 0029)
    current_of = {}
    for n in found:
        for old in former_of[n]:
            current_of[old] = n
    for old, n in to.items():
        if n in found:
            current_of.setdefault(old, n)
    for old, n in sorted(current_of.items()):
        if old == n:
            continue
        t.add((IRI(GND + old), IRI(REPLACED), IRI(GND + n)))
        if old in own:
            t.add((IRI(JL + "gnd/" + old), IRI(REPLACED), IRI(JL + "gnd/" + n)))
    for n in sorted(listed & deleted):
        t.add((IRI(GND + n), IRI(OWL + "deprecated"), Literal("true", XSD + "boolean")))

    # the selection list
    with gzip.open(run.path("gnd-selection.tsv.gz"), "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["gnd", "current", "reason", "detail"])
        for n, reason, detail in sorted(rows, key=lambda r: (r[0], REASONS.index(r[1]), r[2])):
            cur = n if n in found else current_of.get(n) or to.get(n, "")
            w.writerow([n, cur if cur in found else "", reason, detail])
    by_reason = defaultdict(set)
    for n, reason, _d in rows:
        by_reason[reason].add(n)
    only = {r: len(by_reason[r] - set().union(*(by_reason[x] for x in REASONS[:REASONS.index(r)])))
            for r in REASONS}
    for x, k in placeholders.items():
        run.log(f"EntityFacts link with a placeholder left out: {x} ({k:,} records)")
    run.note(f"{len(found):,} records; numbers by reason: "
             + ", ".join(f"{r} {len(by_reason[r]):,} ({only[r]:,} not in the reasons before)" for r in REASONS)
             + f"; {len(current_of):,} former numbers replaced; {len(listed & deleted):,} cited numbers deleted; "
             f"{len(missing):,} unknown.")
    run.write_turtle("gnd.ttl.gz", t)

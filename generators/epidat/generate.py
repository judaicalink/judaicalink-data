"""epidat: the persons of Epidat, from the TEI/EpiDoc files of its research data repository, one resource per person.

Source: the repository named by Epidat's harvesting page (inputs:epidat/data-2026-08-13, commit 61046f3), the same
TEI files the 2022 generator read through the older harvesting interface. Each gravestone file lists its persons
(<person xml:id="hha-2512-1" sex="1"> with persName and death/@when); the cemetery is the settlement of origPlace.

IRIs: data/epidat/<Epidat person id>, one per person. The IRIs of 2023-07-14 were made from the names and conflated
persons of the same name; each of them is stated as dcterms:isReplacedBy the persons it described (its
jl:describedAt links name the person ids), so entity pages keep or split (decision 0022).

Per person: foaf:Person; the name before the spouse (⚭) and without the civil name in final parentheses as
skos:prefLabel and foaf:name, the civil name as skos:altLabel (editorial brackets kept as given); foaf:gender;
jl:deathDate as given (records-normalized reads it); the settlement of the cemetery (before a comma, as 2023) as
jl:deathLocation and its TGN IRI (GeoNames for five cemeteries) as jl:deathLocationURI (as 2023: Epidat gives the
place of burial); owl:sameAs the GND where Epidat links one and Epidat's own URI (lod.academy); jl:describedAt the
Epidat page. Not taken over: the family relations (no ontology terms yet), occupations and birth years (2023 found
them with spaCy in the commentaries).

63 files are not well-formed XML: 30 have a doubled quote in a link target, which is repaired; of the others the
person list is parsed alone, where there is one.
"""

import re
import tarfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES

INPUTS = {
    "tei": "inputs:epidat/data-2026-08-13/epidat-tei.tar.gz",
    "previous": "epidat/2023-07-14",
}
PARAMS = {}

T = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
NS = "http://data.judaicalink.org/data/epidat/"
PAGE = "http://www.steinheim-institut.de/cgi-bin/epidat?id="
LOD = "https://lod.academy/epidat/id/"
JLO, FOAF, SKOS, OWL, DCT = (PREFIXES[p] for p in ("jl", "foaf", "skos", "owl", "dcterms"))
GENDER = {"1": "male", "2": "female"}   # ISO 5218, as in the TEI; 0 = not known
NO_DATE = {"", "-", "--"}

TARGET_FIX = re.compile(r'target="http://"([^"]*)""')
LIST_PERSON = re.compile(r"<listPerson\b.*?</listPerson>", re.S)
SETTLEMENT = re.compile(r"<settlement\b([^>]*)>\s*([^<]*?)\s*<", re.S)
PLACE_KEY = {"tgn": "http://vocab.getty.edu/tgn/", "geoNames": "http://sws.geonames.org/"}
CIVIL_NAME = re.compile(r"\s\(((?:[^()]|\([^()]*\))*)\)$")


def parse(data, counts):
    """The root of a TEI file, or of its person list alone; None if neither parses."""
    try:
        return ET.fromstring(data)
    except ET.ParseError:
        pass
    fixed = TARGET_FIX.sub(r'target="\1"', data)
    try:
        root = ET.fromstring(fixed)
        counts["files repaired (link target)"] += 1
        return root
    except ET.ParseError:
        pass
    m = LIST_PERSON.search(fixed)
    if m:
        try:
            root = ET.fromstring(m.group(0).replace("<listPerson", f'<listPerson xmlns="{T[1:-1]}"', 1))
            counts["files with only the person list parsed"] += 1
            return root
        except ET.ParseError:
            pass
    counts["files not parsed (no person list)"] += 1
    return None


def names(raw):
    """(name, civil name or None) of a persName: the spouse after ⚭ dropped, the civil name in final parentheses."""
    s = " ".join(raw.split())
    civil = None
    m = CIVIL_NAME.search(s)
    if m:
        civil, s = m.group(1).strip() or None, s[:m.start()]
    s = s.split("⚭")[0].strip()
    if not s:
        s, civil = civil or "", None
    return s, (civil if civil != s else None)


def read_tei(path, counts):
    """{person id: person data}, {cemetery code: Counter of (settlement, TGN or GeoNames IRI or None)}."""
    persons, places = {}, defaultdict(Counter)
    with tarfile.open(path) as tf:
        for m in tf:
            if not m.name.endswith(".xml"):
                continue
            counts["files"] += 1
            code = m.name.split("/xml/tei/")[1].split("/")[0]
            data = tf.extractfile(m).read().decode("utf-8")
            s = SETTLEMENT.search(data)
            if s:
                k = re.search(r"\bkey=['\"](tgn|geoNames):([0-9]+)['\"]", s.group(1))
                places[code][(s.group(2).split(",")[0].strip(), PLACE_KEY[k.group(1)] + k.group(2) if k else None)] += 1
            root = parse(data, counts)
            if root is None:
                continue
            for p in root.iter(T + "person"):
                pid = p.get(XML_ID)
                if pid in persons:
                    raise ValueError(f"person id {pid} twice")
                pn = p.find(T + "persName")
                d = p.find(T + "death")
                persons[pid] = {
                    "code": code,
                    "sex": p.get("sex"),
                    "name": "".join(pn.itertext()) if pn is not None else "",
                    "ref": pn.get("ref") if pn is not None else None,
                    "death": (d.get("when") or "").strip() if d is not None else "",
                }
    return persons, places


def generate(run):
    counts = Counter()
    persons, places = read_tei(run.input("tei"), counts)
    place = {}
    for code, c in places.items():
        if len(c) > 1:
            run.note(f"cemetery {code}: several settlements {dict(c)}; the most frequent is used.")
        place[code] = c.most_common(1)[0][0]

    t = set()
    for pid, p in persons.items():
        s = IRI(NS + pid)
        t.add((s, IRI(RDF_TYPE), IRI(FOAF + "Person")))
        name, civil = names(p["name"])
        if name:
            t.add((s, IRI(SKOS + "prefLabel"), Literal(name)))
            t.add((s, IRI(FOAF + "name"), Literal(name)))
        else:
            counts["persons without a name"] += 1
        if civil:
            t.add((s, IRI(SKOS + "altLabel"), Literal(civil)))
        if p["sex"] in GENDER:
            t.add((s, IRI(FOAF + "gender"), Literal(GENDER[p["sex"]])))
        if p["death"] not in NO_DATE:
            t.add((s, IRI(JLO + "deathDate"), Literal(p["death"])))
        if p["code"] in place:
            settlement, uri = place[p["code"]]
            t.add((s, IRI(JLO + "deathLocation"), Literal(settlement)))
            if uri:
                t.add((s, IRI(JLO + "deathLocationURI"), IRI(uri)))
        else:
            counts["persons without a cemetery place"] += 1
        ref = p["ref"] or ""
        if re.fullmatch(r"https?://d-nb\.info/gnd/[0-9]+[0-9X-]*", ref):
            t.add((s, IRI(OWL + "sameAs"), IRI("http://d-nb.info/gnd/" + ref.rsplit("/", 1)[1])))
            counts["GND links"] += 1
        elif ref:
            run.note(f"{pid}: persName ref not a GND IRI, left out: {ref}")
        t.add((s, IRI(OWL + "sameAs"), IRI(LOD + pid)))
        t.add((s, IRI(JLO + "describedAt"), Literal(PAGE + pid)))

    # the IRIs of 2023-07-14: replaced by the persons they described
    described = defaultdict(set)
    for s, p, o in run.triples("previous", file="epidat-final-01.ttl.gz"):
        if p == JLO + "describedAt":
            described[s].add(o.value.split("?id=", 1)[1])
    replaced = Counter()
    withdrawn = set()
    for s, ids in described.items():
        kept = sorted(i for i in ids if i in persons)
        withdrawn.update(i for i in ids if i not in persons)
        replaced[min(len(kept), 2)] += 1
        for i in kept:
            t.add((IRI(s), IRI(DCT + "isReplacedBy"), IRI(NS + i)))

    run.note(f"{counts['files']:,} TEI files, {len(persons):,} persons in {len(place)} cemeteries; "
             f"{counts['files repaired (link target)']} files repaired, "
             f"{counts['files with only the person list parsed']} with only the person list parsed, "
             f"{counts['files not parsed (no person list)']} not parsed (no person list).")
    run.note(f"{counts['persons without a name']} persons without a name, {counts['GND links']} GND links.")
    run.note(f"2023-07-14: {len(described):,} IRIs; {replaced[1]:,} replaced by one person, {replaced[2]:,} by several, "
             f"{replaced[0]} by none; {len(withdrawn)} of its person ids are not in the TEI files "
             f"(cemeteries {', '.join(sorted({i.split('-')[0] for i in withdrawn}))}: "
             f"Epidat answers 'not yet published').")
    run.write_turtle("epidat.ttl.gz", t)

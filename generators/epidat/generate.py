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
jl:burialLocation and its TGN IRI (GeoNames for five cemeteries) as jl:burialLocationURI (parameter burial_terms;
before: jl:deathLocation/jl:deathLocationURI, which is not true for everyone); owl:sameAs the GND where Epidat links one and Epidat's own URI (lod.academy); jl:describedAt the
Epidat page. Not taken over: occupations (2023 found them with spaCy in the commentaries).

Added 2026-10-15, each a parameter with the addition as default (with all off, the triples of 2026-10-12):
- birth_dates: jl:birthDate as given by the person table of the repository (inputs:epidat/persdata-2026-08-13,
  tsv/epidat_persdata.tsv at the same commit; the TEI files have no birth dates), only in the forms YYYY,
  YYYY-MM, YYYY-MM-DD and YYYY/YY; the others are listed in the log.
- memorial_links: rdfs:seeAlso the entry of the person in the Gedenkbuch of the Bundesarchiv
  (https://www.bundesarchiv.de/gedenkbuch/de<id>, the form Epidat uses in its commentaries) and in the Yad Vashem
  names database (https://collections.yadvashem.org/en/names/<id>), from the gedenkbuchID and yadvashemID columns.
- family_relations: the relations of the TEI files (listRelation, by person id): schema:parent (child to parent),
  jl:grandparent (grandchild to grandparent; schema.org has no term, judaicalink-ontology), schema:spouse and
  schema:sibling (both ways). Relations to persons not in the files are left out. The person table gives parents and
  spouses only as names; not used.
- canonical_forms: the GND and GeoNames IRIs and the points in canonical form (docs/iri-forms.md).

63 files are not well-formed XML: 30 have a doubled quote in a link target, which is repaired; of the others the
person list is parsed alone, where there is one.
"""

import csv
import re
import tarfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

from jl.rdf import IRI, RDF_TYPE, Literal
from jl.iris import canonical_triples
from jl.turtle import PREFIXES

INPUTS = {
    "tei": "inputs:epidat/data-2026-08-13/epidat-tei.tar.gz",
    "persdata": "inputs:epidat/persdata-2026-08-13/epidat_persdata.tsv",
    "previous": "epidat/2023-07-14",
}
PARAMS = {"birth_dates": True, "memorial_links": True, "family_relations": True, "canonical_forms": True, "burial_terms": True}

T = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
NS = "http://data.judaicalink.org/data/epidat/"
PAGE = "http://www.steinheim-institut.de/cgi-bin/epidat?id="
LOD = "https://lod.academy/epidat/id/"
JLO, FOAF, SKOS, OWL, DCT, RDFS, SDO = (PREFIXES[p] for p in ("jl", "foaf", "skos", "owl", "dcterms", "rdfs",
                                                                "schema"))
GEDENKBUCH = "https://www.bundesarchiv.de/gedenkbuch/de"
YAD_VASHEM = "https://collections.yadvashem.org/en/names/"
BIRTH_FORM = re.compile(r"[0-9]{4}(-[0-9]{2}(-[0-9]{2})?|/[0-9]{2})?")
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
    """{person id: person data}, {cemetery code: Counter of (settlement, TGN or GeoNames IRI or None)}, the set of
    relations (name, active ids, passive ids, mutual ids)."""
    persons, places, relations = {}, defaultdict(Counter), set()
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
            for r in root.iter(T + "relation"):
                ids = [tuple(sorted(x.lstrip("#") for x in (r.get(a) or "").split())) for a in
                       ("active", "passive", "mutual")]
                relations.add((r.get("name"), *ids))
    return persons, places, relations


def read_persdata(path):
    """{person id: row} of the person table."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {r["persid"]: r for r in csv.DictReader(f, delimiter="\t")}


def generate(run):
    counts = Counter()
    persons, places, relations = read_tei(run.input("tei"), counts)
    prm = run.params
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
            which = "burial" if run.params["burial_terms"] else "death"
            t.add((s, IRI(JLO + which + "Location"), Literal(settlement)))
            if uri:
                t.add((s, IRI(JLO + which + "LocationURI"), IRI(uri)))
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

    if prm["birth_dates"] or prm["memorial_links"]:
        add_persdata(run, t, persons, read_persdata(run.input("persdata")))
    if prm["family_relations"]:
        add_relations(run, t, persons, relations)

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
    if run.params["canonical_forms"]:   # GND and GeoNames IRIs and points in canonical form (docs/iri-forms.md)
        t = set(canonical_triples(t))
    run.write_turtle("epidat.ttl.gz", t)


def add_persdata(run, t, persons, rows):
    """Birth dates and memorial links of the person table, for the persons of the TEI files."""
    prm, c, odd = run.params, Counter(), []
    absent = Counter(pid.split("-")[0] for pid in rows if pid not in persons)
    for pid in sorted(rows):
        if pid not in persons:
            continue
        r, s = rows[pid], IRI(NS + pid)
        birth = r["dateofbirth"].strip()
        if prm["birth_dates"] and birth:
            if BIRTH_FORM.fullmatch(birth):
                t.add((s, IRI(JLO + "birthDate"), Literal(birth)))
                c["birth dates"] += 1
            else:
                odd.append(f"{pid}: dateofbirth {birth!r}")
        if prm["memorial_links"]:
            for col, base, digits in (("gedenkbuchID", GEDENKBUCH, 5), ("yadvashemID", YAD_VASHEM, 6)):
                v = r[col].strip()
                if re.fullmatch(f"[0-9]{{{digits},}}", v):
                    t.add((s, IRI(RDFS + "seeAlso"), IRI(base + v)))
                    c[col] += 1
                elif v:
                    odd.append(f"{pid}: {col} {v!r}")
    for line in odd:
        run.log("person table, value left out:", line)
    run.note(f"person table: {len(rows):,} rows, {len(rows) - sum(absent.values()):,} of them persons of the TEI "
             f"files; {c['birth dates']:,} birth dates, {c['gedenkbuchID']} Gedenkbuch and {c['yadvashemID']} Yad "
             f"Vashem links; {len(odd)} values in other forms left out (log).")
    run.note(f"person table: {sum(absent.values()):,} persons not in the TEI files, by cemetery: "
             + ", ".join(f"{k} {v}" for k, v in sorted(absent.items(), key=lambda kv: (-kv[1], kv[0]))) + ".")


RELATION = {"parent": SDO + "parent", "grandparent": PREFIXES["jl"] + "grandparent", "spouse": SDO + "spouse",
            "sibling": SDO + "sibling"}


def add_relations(run, t, persons, relations):
    """The family relations of the TEI files between persons of the files."""
    c, pairs = Counter(), set()
    for name, active, passive, mutual in sorted(relations, key=lambda r: tuple(map(str, r))):
        ids = set(active) | set(passive) | set(mutual)
        if not ids <= set(persons):
            c["relations with a person not in the files"] += 1
            continue
        if name in ("parent", "grandparent"):
            pairs.update((child, name, parent) for parent in active for child in passive)
        elif name in ("spouse", "sibling"):
            pairs.update((a, name, b) for a in mutual for b in mutual if a != b)
        else:
            c[f"{name} relations (no term)"] += 1
    for a, name, b in pairs:
        t.add((IRI(NS + a), IRI(RELATION[name]), IRI(NS + b)))
        c[name] += 1
    run.note(f"family relations: {len(relations):,} distinct relations in the TEI files; stated "
             f"{c['parent']:,} schema:parent, {c['grandparent']:,} jl:grandparent, {c['spouse']:,} schema:spouse, "
             f"{c['sibling']:,} schema:sibling; left out {c['relations with a person not in the files']} with a person "
             f"not in the files" + "".join(f", {n} {k}" for k, n in sorted(c.items()) if k.endswith("(no term)")) + ".")

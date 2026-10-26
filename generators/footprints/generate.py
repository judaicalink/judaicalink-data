"""footprints: Footprints (Jewish books through time and place), made from the complete harvest of its API, true to
the API (decision 0034).

Source: inputs:footprints/api-2026-10-20 (harvest.py, harvest_driver.py), the GeoNames ids of the places as confirmed
by Footprints (geonames.py), and the version 2026-10-12 for its IRIs.

Every record of the four levels is stated with every field: works (writtenwork), imprints, copies (book) and
footprints (the evidence that a copy was at a place at a time), and the persons, canonical places, actor records,
roles and languages. Left out: the editors' bookkeeping (created_by, last_modified_by, created_at, modified_at,
verified_modified_at), the description fields (HTML the site renders from the other fields), the narrative of a
footprint (a sentence the site makes from its fields) and the titles of the imprint and work repeated on a footprint.
Terms of the API are coined in data/footprints/vocab/ (footprints-vocabulary.ttl.gz). Notes with HTML markup are
rdf:HTML. Dates: the display text and the normalised value of the EDTF form (decision 0035; jl.dates).

IRIs: data/footprints/<endpoint>/<id> (writtenwork, imprint, book, footprint, person, place, actor, role, language).
JudaicaLink terms in addition: works and imprints schema:CreativeWork, places schema:Place with geosparql:asWKT and
owl:sameAs GeoNames (where Footprints confirmed the id), persons foaf:Agent (their class is in record-classes) with
owl:sameAs VIAF and LC, jl:birthDate/jl:deathDate and their normalised values; skos:prefLabel for these. The persons
of a record are linked directly as well, one property per role (gndo:author, gndo:editor, dcterms:publisher, else
vocab:<role>); the owners of a copy as vocab:owner and vocab:currentOwner. The digital objects of the footprints are
linked as foaf:depiction. Works and footprints link their page on the site (jl:describedAt; imprints, copies,
persons and places have no page of their own). The identifiers of works and imprints are dcterms:identifier "<slug> <identifier>".

The IRIs of 2024 (uuid5 of the SHA-256 of a name) are dcterms:isReplacedBy the records of the same level they stood
for: a person by the API addresses it names (jl:describedAt), else by the name; a work by its title; a place by the
first part of the canonical name. A name of several records gives several replacements (the entity pages split).
"""

import csv
import gzip
import hashlib
import json
import re
import uuid
from collections import Counter, defaultdict

from jl import classes
from jl.dates import normalised
from jl.generator import GeneratorError
from jl.iris import canonical_wkt
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

INPUTS = {
    "api": "inputs:footprints/api-2026-10-20",
    "previous": "footprints/2026-10-12",
    "geonames": "inputs:footprints/geonames-2026-10-26/places.tsv",
}
PARAMS = {}

NS = "http://data.judaicalink.org/data/footprints/"
V = NS + "vocab/"
SITE = "https://footprints.ctl.columbia.edu/"
JLO, SKOS, RDFS, FOAF, OWL, DCT, GNDO, RDF = (PREFIXES[p] for p in
                                             ("jl", "skos", "rdfs", "foaf", "owl", "dcterms", "gndo", "rdf"))
GEOSPARQL = PREFIXES["geosparql"]
HTML = RDF + "HTML"
TAG = re.compile(r"<(p|br|em|strong|i|b|u|a|ul|ol|li|span|div|blockquote|sup|sub)\b[^>]*>", re.I)
# the roles with a standard term; the others get a property of the vocabulary
STANDARD_ROLE = {"Author": GNDO + "author", "Editor": GNDO + "editor", "Publisher": DCT + "publisher"}
# the pages of the site that the data links to (checked 2026-10-26: imprints, copies, persons and places have none)
PAGES = {"footprint": "footprint/{}/", "writtenwork": "writtenwork/{}/"}

CLASSES = [
    ("WrittenWork", "Work", "A literary work, independent of its editions (Footprints: written work)."),
    ("Imprint", "Imprint", "An edition of a work: printed at a place and time by its printers and publishers."),
    ("BookCopy", "Copy", "A copy of an imprint, as held by a library or owner (Footprints API: book)."),
    ("Footprint", "Footprint", "The evidence that a copy was at a place at a time, e.g. an owner's signature, a "
                               "censor's mark, an entry in a catalogue or an inventory."),
    ("Person", "Person", "A person or an organisation as Footprints records it (the API does not tell them apart)."),
    ("Place", "Place", "A place of Footprints (its canonical place, made from a GeoNames record)."),
    ("Actor", "Actor", "A person in a role for a record, with the name the source uses for the person there."),
]
PROPERTIES = [
    ("title", "Title", "The title of a work or imprint, or the title a footprint records."),
    ("work", "Work", "The work of an imprint."),
    ("imprint", "Imprint", "The imprint of a copy."),
    ("copy", "Copy", "The copy a footprint is evidence of."),
    ("place", "Place", "The place of publication of an imprint, or the place of a footprint."),
    ("language", "Language", "A language of an imprint or of the evidence of a footprint."),
    ("actor", "Actor", "An actor record of a work, imprint or footprint."),
    ("owners", "Owners", "An actor record of an owner of a copy, former or current."),
    ("currentOwners", "Current owners", "An actor record of a current owner of a copy."),
    ("currentOwner", "Current owner", "A current owner of a copy (from its actor records)."),
    ("person", "Person", "The person of an actor record."),
    ("role", "Role", "The role of an actor record."),
    ("alias", "Alias", "The name of the person as the source of the record gives it."),
    ("publicationDate", "Date of publication", "The date of publication of an imprint, normalised from its EDTF "
                                               "form (xsd:gYear, xsd:gYearMonth, xsd:date or EDTF)."),
    ("associatedDate", "Date", "The date of a footprint, normalised from its EDTF form (xsd:gYear, "
                               "xsd:gYearMonth, xsd:date or EDTF)."),
    ("callNumber", "Call number", "The call number of a copy or of the evidence of a footprint."),
    ("medium", "Evidence type", "The kind of evidence of a footprint (e.g. owner signature in extant copy, "
                                "library catalog, reference in another text)."),
    ("mediumDescription", "Evidence description", "The source of the evidence of a footprint, as text."),
    ("provenance", "Evidence location", "Where the evidence of a footprint is held."),
    ("notes", "Notes", "Notes of the record."),
    ("verified", "Verified", "Whether the editors of Footprints verified the footprint."),
    ("percentComplete", "Percent complete", "How complete the editors of Footprints consider the footprint."),
    ("flag", "Flag", "An editorial flag of Footprints on the footprint (e.g. the imprint has no BHB number)."),
]


def old_iri(name):
    """The IRI the generator of 2024 coined for a name or title."""
    return NS + str(uuid.uuid5(uuid.NAMESPACE_OID, hashlib.sha256(name.encode()).hexdigest()))


def camel(name):
    words = re.findall(r"[A-Za-z]+", name)
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])


def text(v):
    return v.strip() if isinstance(v, str) and v.strip() else None


def records(run, endpoint):
    path = next((p for p in run.inputs("api") if p.name == f"{endpoint}.jsonl.gz"), None)
    if path is None:
        raise GeneratorError(f"no {endpoint}.jsonl.gz in the harvest")
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return {r["id"]: r for r in map(json.loads, f)}


def generate(run):
    n = Counter()
    data, vocab = set(), set()

    def add(s, p, o, out=data):
        out.add((IRI(s), IRI(p), o if isinstance(o, Literal) else IRI(o)))

    def lit(v, dt=None):
        return Literal(str(v), dt)

    api = {ep: records(run, ep) for ep in ("writtenwork", "imprint", "book", "footprint", "person", "place",
                                           "role", "language", "identifiertype")}
    iri = lambda ep, i: f"{NS}{ep}/{i}"
    slug_of_type = {r["id"]: r["slug"] for r in api["identifiertype"].values()}

    # --- vocabulary, roles, languages ---------------------------------------------------------------------
    role_prop = {}
    for r in api["role"].values():
        role_prop[r["name"]] = STANDARD_ROLE.get(r["name"], V + camel(r["name"]))
    props = list(PROPERTIES) + [(camel(name), name, f"A person in the role '{name}' for the record (from its actor "
                                                    "records).") for name in sorted(role_prop)
                                if name not in STANDARD_ROLE]
    for local, label, comment in CLASSES:
        add(V + local, RDF_TYPE, RDFS + "Class", vocab)
        add(V + local, RDFS + "label", lit(label), vocab)
        add(V + local, RDFS + "comment", lit(comment), vocab)
    seen = set()
    for local, label, comment in props:
        if local in seen:   # owner: a role and the owners of a copy
            continue
        seen.add(local)
        add(V + local, RDF_TYPE, RDF + "Property", vocab)
        add(V + local, RDFS + "label", lit(label), vocab)
        add(V + local, RDFS + "comment", lit(comment), vocab)
    for ep, label in (("role", "Roles of Footprints"), ("language", "Languages of Footprints")):
        add(NS + ep, RDF_TYPE, SKOS + "ConceptScheme", vocab)
        add(NS + ep, RDFS + "label", lit(label), vocab)
        for r in api[ep].values():
            s = iri(ep, r["id"])
            add(s, RDF_TYPE, SKOS + "Concept")
            add(s, SKOS + "prefLabel", lit(r["name"]))
            add(s, RDFS + "label", lit(r["name"]))
            add(s, SKOS + "inScheme", NS + ep)

    def common(s, cls, label, entity=None):
        add(s, RDF_TYPE, V + cls)
        if entity:
            add(s, RDF_TYPE, entity)
        if label:
            add(s, RDFS + "label", lit(label))
            if entity:
                add(s, SKOS + "prefLabel", lit(label))

    def notes(s, v):
        v = text(v)
        if v:
            add(s, V + "notes", lit(v, HTML if TAG.search(v) else None))

    def date(s, d, shown, norm):
        if not d or not text(d.get("display")):
            return
        if d["display"].strip() == "invalid":   # the API's display of a value it cannot read
            run.log(f"{s}: date {d.get('edtf_format')!r} displayed as 'invalid', left out")
            n["dates displayed as invalid"] += 1
            return
        add(s, shown, lit(d["display"].strip()))
        v = normalised(d.get("edtf_format"))
        if v:
            add(s, norm, v)
            n["dates " + v.datatype.rsplit("/", 1)[-1].rsplit("#", 1)[-1]] += 1
        else:
            n["dates without a normalised value"] += 1
            run.log(f"{s}: EDTF {d.get('edtf_format')!r} ({d['display']!r}) is no date")

    # --- persons ----------------------------------------------------------------------------------------
    persons = dict(api["person"])

    def person_of(p):
        if p["id"] not in persons:
            raise GeneratorError(f"person {p['id']} is referred to but not in the harvest")
        return iri("person", p["id"])

    for p in persons.values():
        s = iri("person", p["id"])
        common(s, "Person", text(p.get("name")))
        add(s, RDF_TYPE, FOAF + "Agent")
        if text(p.get("name")):
            add(s, SKOS + "prefLabel", lit(p["name"].strip()))
        date(s, p.get("birth_date"), JLO + "birthDate", JLO + "birthDateNormalized")
        date(s, p.get("death_date"), JLO + "deathDate", JLO + "deathDateNormalized")
        si = p.get("standardized_identifier")
        if si:
            ident = si["identifier"].strip()
            if si["authority"] == "VIAF Identifier" and re.fullmatch(r"[0-9]+", ident):
                add(s, OWL + "sameAs", f"https://viaf.org/viaf/{ident}")
                n["persons with VIAF"] += 1
            elif si["authority"] == "Library of Congress" and (m := re.fullmatch(
                    r"(?:https?://id\.loc\.gov/authorities/names/)?([a-z]+[0-9]+)(?:\.html)?", ident)):
                add(s, OWL + "sameAs", f"http://id.loc.gov/authorities/names/{m.group(1)}")
                n["persons with LC"] += 1
            elif si["authority"] == "Library of Congress":   # not a name authority (e.g. a bibliographic LCCN)
                add(s, DCT + "identifier", lit(f"LOC {re.sub(r'^LOC\s+', '', ident)}"))
                run.log(f"{s}: LC identifier {ident!r} is no name authority, stated as dcterms:identifier")
                n["persons with another LC identifier"] += 1
            else:
                raise GeneratorError(f"person {p['id']}: identifier {si['authority']} {ident!r}")
        n["persons"] += 1

    # --- actor records ---------------------------------------------------------------------------------
    actors = {}

    def actor(a):
        """The IRI of an actor record (stated once) and (role, person IRI)."""
        s = iri("actor", a["id"])
        if a["id"] not in actors:
            actors[a["id"]] = a
            add(s, RDF_TYPE, V + "Actor")
            if text(a.get("display_title")):
                add(s, RDFS + "label", lit(a["display_title"].strip()))
            add(s, V + "person", person_of(a["person"]))
            add(s, V + "role", iri("role", a["role"]["id"]))
            if text(a.get("alias")):
                add(s, V + "alias", lit(a["alias"].strip()))
        return s, a["role"]["name"], person_of(a["person"])

    def actors_of(s, rs, field="actor"):
        for a in rs or []:
            a_iri, role, person = actor(a)
            add(s, V + field, a_iri)
            add(s, role_prop[role], person)

    def identifiers(s, ids):
        for i in ids or []:
            if not i.get("identifier_type") or not text(i.get("identifier")):
                run.log(f"{s}: identifier without type or value left out: {i}")
                n["identifiers without type or value"] += 1
                continue
            tid = int(re.search(r"/identifiertype/([0-9]+)/", i["identifier_type"]).group(1))
            add(s, DCT + "identifier", lit(f"{slug_of_type[tid]} {i['identifier'].strip()}"))
            n["identifiers " + slug_of_type[tid]] += 1

    # --- places ----------------------------------------------------------------------------------------
    places = {}

    def place(p):
        cp = p.get("canonical_place") if "canonical_place" in p else p
        if not cp or cp.get("id") is None:
            return None
        if cp["id"] in places:
            if places[cp["id"]] != cp:
                raise GeneratorError(f"place {cp['id']} differs between records: {places[cp['id']]} / {cp}")
        else:
            places[cp["id"]] = cp
        return iri("place", cp["id"])

    for p in api["place"].values():
        place(p)

    # --- works, imprints, copies, footprints -------------------------------------------------------------
    for w in api["writtenwork"].values():
        s = iri("writtenwork", w["id"])
        common(s, "WrittenWork", text(w.get("title")), classes.WORK)
        if text(w.get("title")):
            add(s, V + "title", lit(w["title"].strip()))
        add(s, JLO + "describedAt", lit(SITE + PAGES["writtenwork"].format(w["id"])))
        actors_of(s, w.get("actor"))
        identifiers(s, w.get("standardized_identifier"))
        notes(s, w.get("notes"))
        n["works"] += 1
    for i in api["imprint"].values():
        s = iri("imprint", i["id"])
        common(s, "Imprint", text(i.get("title")), classes.WORK)
        if text(i.get("title")):
            add(s, V + "title", lit(i["title"].strip()))
        if i["work"]["id"] not in api["writtenwork"]:
            raise GeneratorError(f"imprint {i['id']}: work {i['work']['id']} not in the harvest")
        add(s, V + "work", iri("writtenwork", i["work"]["id"]))
        date(s, i.get("publication_date"), DCT + "issued", V + "publicationDate")
        if i.get("place"):
            add(s, V + "place", place(i["place"]))
        for lang in i.get("language") or []:
            add(s, V + "language", iri("language", lang["id"]))
        actors_of(s, i.get("actor"))
        identifiers(s, i.get("standardized_identifier"))
        notes(s, i.get("notes"))
        n["imprints"] += 1
    for b in api["book"].values():
        s = iri("book", b["id"])
        common(s, "BookCopy", text(b.get("identifier")))
        if text(b.get("identifier")):
            add(s, DCT + "identifier", lit(b["identifier"].strip()))
        if b["imprint"]["id"] not in api["imprint"]:
            raise GeneratorError(f"copy {b['id']}: imprint {b['imprint']['id']} not in the harvest")
        add(s, V + "imprint", iri("imprint", b["imprint"]["id"]))
        if text(b.get("call_number")):
            add(s, V + "callNumber", lit(b["call_number"].strip()))
        for a in b.get("owners") or []:
            a_iri, _role, person = actor(a)
            add(s, V + "owners", a_iri)
            add(s, V + "owner", person)
        for a in b.get("current_owners") or []:
            a_iri, _role, person = actor(a)
            add(s, V + "currentOwners", a_iri)
            add(s, V + "currentOwner", person)
        notes(s, b.get("notes"))
        n["copies"] += 1
    for f in api["footprint"].values():
        s = iri("footprint", f["id"])
        common(s, "Footprint", text(f.get("title")))
        add(s, JLO + "describedAt", lit(SITE + PAGES["footprint"].format(f["id"])))
        if text(f.get("title")):
            add(s, V + "title", lit(f["title"].strip()))
        _work, _imprint, copy = (int(x) for x in f["book_copy_identifier"].split("-"))
        if copy not in api["book"]:
            raise GeneratorError(f"footprint {f['id']}: copy {copy} not in the harvest")
        add(s, V + "copy", iri("book", copy))
        for k, p in (("medium", "medium"), ("medium_description", "mediumDescription"),
                     ("provenance", "provenance"), ("call_number", "callNumber")):
            if text(f.get(k)):
                add(s, V + p, lit(f[k].strip()))
        if f.get("place"):
            add(s, V + "place", place(f["place"]))
        date(s, f.get("associated_date"), DCT + "date", V + "associatedDate")
        for lang in f.get("language") or []:
            add(s, V + "language", iri("language", lang["id"]))
        actors_of(s, f.get("actor"))
        for d in f.get("digital_object") or []:
            if text(d.get("url")):
                add(s, FOAF + "depiction", d["url"].strip().replace(" ", "%20"))
                n["depictions"] += 1
        add(s, V + "verified", lit("true" if f.get("verified") else "false", XSD + "boolean"))
        if f.get("percent_complete") is not None:
            add(s, V + "percentComplete", lit(int(f["percent_complete"]), XSD + "integer"))
        for _code, message in f.get("flags") or []:
            add(s, V + "flag", lit(message))
        notes(s, f.get("notes"))
        n["footprints"] += 1

    # --- places, with the GeoNames ids Footprints confirmed -----------------------------------------------
    confirmed = {}
    if "geonames" in INPUTS:
        with open(run.input("geonames"), encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["how"] == "confirmed":
                    confirmed[int(r["place"])] = r["geonames"]
    for pid, cp in places.items():
        s = iri("place", pid)
        common(s, "Place", text(cp.get("canonical_name")), classes.PLACE)
        if cp.get("latitude") is not None and cp.get("longitude") is not None:
            add(s, GEOSPARQL + "asWKT",
                lit(canonical_wkt(f"POINT({cp['longitude']} {cp['latitude']})"), GEOSPARQL + "wktLiteral"))
        if pid in confirmed:
            add(s, OWL + "sameAs", f"https://sws.geonames.org/{confirmed[pid]}/")
            n["places with GeoNames"] += 1
        n["places"] += 1
    n["actor records"] = len(actors)

    # --- the IRIs of 2024 ----------------------------------------------------------------------------------
    level = {}                            # old IRI -> person, work or place (its class in 2024)
    api_ids = defaultdict(set)            # old person IRI -> the API person ids it names
    for s, p, o in run.triples("previous", file="footprints.ttl.gz"):
        if p == RDF_TYPE:
            k = {"Person": "person", "Work": "work", "PlaceOrGeographicName": "place"}.get(
                re.split(r"[/#]", str(o))[-1])
            if k:
                level.setdefault(str(s), set()).add(k)
        elif p == JLO + "describedAt" and (m := re.search(r"/api/person/([0-9]+)", str(o.value if isinstance(
                o, Literal) else o))):
            api_ids[str(s)].add(int(m.group(1)))
    by_name = {"person": defaultdict(set), "work": defaultdict(set), "place": defaultdict(set)}
    for p in persons.values():
        if text(p.get("name")):
            by_name["person"][old_iri(p["name"].strip())].add(iri("person", p["id"]))
    for w in api["writtenwork"].values():
        if text(w.get("title")):
            by_name["work"][old_iri(w["title"].strip())].add(iri("writtenwork", w["id"]))
    for pid, cp in places.items():
        if text(cp.get("canonical_name")):
            by_name["place"][old_iri(cp["canonical_name"].split(",")[0].strip())].add(iri("place", pid))
    for old, ks in sorted(level.items()):
        for k in sorted(ks):
            targets = {iri("person", i) for i in api_ids.get(old, ()) if i in persons} if k == "person" else set()
            how = "API address" if targets else "name"
            targets = targets or by_name[k].get(old, set())
            n[f"2024 {k}s: " + ("none" if not targets else "one" if len(targets) == 1 else "several")
              + (f" (by {how})" if targets else "")] += 1
            for t in sorted(targets):
                add(old, DCT + "isReplacedBy", t)

    for k, c in sorted(n.items()):
        run.log(f"{k}: {c:,}")
    olds = {k: sum(c for key, c in n.items() if key.startswith(f"2024 {k}s: ") and "none" not in key)
            for k in ("person", "work", "place")}
    run.note(f"{n['works']:,} works, {n['imprints']:,} imprints, {n['copies']:,} copies, {n['footprints']:,} "
             f"footprints, {n['persons']:,} persons ({n['persons with VIAF']:,} with VIAF), {n['places']:,} places "
             f"({n['places with GeoNames']:,} with GeoNames), {n['actor records']:,} actor records. IRIs of 2024 "
             f"replaced: {olds['person']:,} persons, {olds['work']:,} works, {olds['place']:,} places.")
    run.write_turtle("footprints.ttl.gz", data)
    run.write_turtle("footprints-vocabulary.ttl.gz", vocab)

"""ls-nli-legacy: the legacy nli-persons URIs linked to the NLI authority records they were made from.

Transformation only, a port of ls_nli_legacy of kg-complements (nli_records.py, 2026-10-06; decisions 0010, 0020)
without changes to its logic; the reading of the export and the reproduction of the legacy URI assignment are in
nli_export.py of nli-records (shared code, decision 0018). For every legacy URI: prov:wasDerivedFrom the records it was
made from; owl:sameAs where it stands for exactly one person record with its own name and dates (or, for URIs made
only from works or subject headings, the one person record these name), plus that record's VIAF and LC identifiers;
DQV quality annotations for the faulty URIs. The reproduction is checked against nli-persons: every legacy URI.

One fix (parameter data_annotation_iris, default on): the annotations get IRIs in the namespace of this dataset,
data/ls-nli-legacy/annotation/<hash> (decision 0002), not datasets/ls-nli-legacy/a/<hash>, which is the space of the
dataset's versions and metadata (0018).
"""

import hashlib
import re
from collections import Counter, defaultdict

from jl.generator import GeneratorError, load_shared
from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES

nli = load_shared("nli-records", "nli_export")

INPUTS = {"export": "inputs:nli/authority-export-2019/auth.json.gz", "legacy": "nli-persons/2019-01-25"}
PARAMS = {"data_annotation_iris": True}

DCT = PREFIXES["dcterms"]
OWL = PREFIXES["owl"]
PROV = PREFIXES["prov"]
DQV = PREFIXES["dqv"]
OA = PREFIXES["oa"]
NLI_PERSONS = "http://data.judaicalink.org/datasets/nli-persons"


_IRI_BAD = re.compile(r'[<>"{}|^`\\\s]')


def iri(value):
    """An IRI; characters not allowed in IRIs (from source data given as text) are percent-encoded, as in
    kg-complements."""
    return IRI(_IRI_BAD.sub(lambda m: "%{:02X}".format(ord(m.group(0))), value))


def generate(run):
    records = nli.read_records(run.input("export"))
    viaf_count = Counter(a for _n, r in records for x in r.get("901", []) for a in x.get("a", []))
    ids_of = {nli.record_iri(n, r, viaf_count): nli.identifiers(r) for n, r in records if nli.kind(r) == "person"}
    legacy = nli.legacy_assignment(records)
    index = nli.person_index(records, viaf_count)
    present = {str(s) for s, p, o in run.triples("legacy") if p == RDF_TYPE}
    produced = {x["uri"] for x in legacy}
    if produced != present:
        raise GeneratorError(f"legacy reproduction differs: {len(produced - present)} not in nli-persons, "
                             f"{len(present - produced)} missing")
    run.log(f"legacy URIs reproduced exactly: {len(produced):,}")
    by_uri = defaultdict(list)
    for (n, r), x in zip(records, legacy):
        by_uri[x["uri"]].append((n, r, x))
    t = set()
    counts = Counter()
    base = ("http://data.judaicalink.org/data/ls-nli-legacy/annotation/" if run.params["data_annotation_iris"]
            else "http://data.judaicalink.org/datasets/ls-nli-legacy/a/")

    def add(s, p, o):
        t.add((iri(s), iri(p), o if isinstance(o, Literal) else iri(o)))

    def note(target, kind_, text):
        aid = base + hashlib.sha1(f"{target}|{kind_}".encode()).hexdigest()[:16]
        add(aid, RDF_TYPE, DQV + "QualityAnnotation")
        add(aid, RDF_TYPE, OA + "Annotation")
        add(aid, OA + "hasTarget", target)
        add(aid, OA + "motivatedBy", DQV + "qualityAssessment")
        add(aid, OA + "bodyValue", Literal(text, lang="en"))
        add(aid, DCT + "type", Literal(kind_))
        counts["annotation: " + kind_] += 1

    for uri in sorted(by_uri):
        members = by_uri[uri]
        persons, works, subjects = [], [], []
        for n, r, x in members:
            k = nli.kind(r)
            rec = nli.record_iri(n, r, viaf_count) if k != "subject-heading" else None
            if rec:
                add(uri, PROV + "wasDerivedFrom", rec)
            (persons if k == "person" else works if k == "work" else subjects).append((rec, r, x))
        counts["legacy URIs"] += 1
        good_persons = [p for p in persons if not p[2]["stale_label"]]
        if len(persons) == 1 and good_persons and not persons[0][2]["stale_dates"]:
            add(uri, OWL + "sameAs", persons[0][0])
            counts["owl:sameAs (one person record)"] += 1
            for x in ids_of[persons[0][0]]:   # the record's identifiers directly on the legacy URI
                add(uri, OWL + "sameAs", x)
                counts["identifiers on legacy URIs"] += 1
        if len(persons) > 1:
            note(uri, "conflated records",
                 f"This URI was made from {len(persons)} different NLI person records with the same heading "
                 "(possibly different people); see prov:wasDerivedFrom for the records.")
        if any(p[2]["stale_label"] for p in persons + works + subjects):
            note(uri, "wrong name",
                 "At least one record of this URI has no Latin-script heading; the legacy generator gave it the "
                 "name (and URI) of the record before it in the export. The name does not belong to that record.")
        if any(p[2]["stale_dates"] for p in persons + works + subjects):
            note(uri, "wrong dates",
                 "At least one record of this URI has a date without a hyphen; the legacy generator gave it the "
                 "birth and death dates of an earlier record.")
        if works:
            note(uri, "works as person",
                 f"{len(works)} name/title record(s) (works) were turned into this person; their titles became "
                 "jl:hasTitle. The works are separate resources (jl:Work) in nli-records.")
        if subjects and not persons:
            note(uri, "subject heading as person",
                 "This URI was made only from subject headings (name -- subdivision, e.g. '-- Archives'), "
                 "not from a person record.")
        if not persons:
            counts["legacy URIs without person record"] += 1
            # made only from works or subject headings: the person they name, if it is one record
            named = {nli.named_person(r, index) for _rec, r, _x in works + subjects}
            if len(named) == 1 and None not in named:
                add(uri, OWL + "sameAs", next(iter(named)))
                counts["owl:sameAs (person named by the works or subject headings)"] += 1
                for x in ids_of[next(iter(named))]:
                    add(uri, OWL + "sameAs", x)
                    counts["identifiers on legacy URIs"] += 1
    note(NLI_PERSONS, "generator errors",
         "The legacy generator (NLI-persons-03.py) builds URIs from the heading text and drops the record "
         "identifiers; records with the same heading and dates are merged, the same person gets several URIs "
         "when the date strings differ, works and subject headings become persons, records without a Latin "
         "heading get the name of the record before, and open life dates give empty jl:deathDate literals. "
         "nli-records has the records with identifiers, ls-nli-legacy links each legacy URI to them.")
    run.note(f"{dict(sorted(counts.items()))}.")
    run.write_turtle("ls-nli-legacy.ttl.gz", t)

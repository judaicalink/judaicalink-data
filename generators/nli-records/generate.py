"""nli-records: the person and work records of the NLI authority export behind nli-persons, one resource per record.

Transformation only, a port of nli_records of kg-complements (nli_records.py, 2026-10-06; decisions 0010, 0020)
without changes to its logic; the reading and matching of the export is in nli_export.py, shared with ls-nli-legacy.
Each record keeps the identifiers of the export (VIAF from 901, LC from 010, owl:sameAs), its headings in all scripts,
variant names (400, 700), dates (046, else the heading's dates), places (370), occupations (374), gender (375) and
notes (678). Name/title records are works (jl:Work) linked to their creator where the heading matches exactly one
person record. Subject headings are left out. IRIs: data/nli/record/viaf-<VIAF>, or h-<hash of the headings> for
records without a unique VIAF number.
"""

import re
from collections import Counter

from nli_export import (REC, SCRIPT_LANG, TITLE_CODES, clean, dates, heading, kind, named_person, names,
                        person_index, read_records, record_iri, sub)
from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES

INPUTS = {"export": "inputs:nli/authority-export-2019/auth.json.gz"}
PARAMS = {}

JLO = PREFIXES["jl"]
DCT = PREFIXES["dcterms"]
DC = PREFIXES["dc"]
FOAF = PREFIXES["foaf"]
OWL = PREFIXES["owl"]
SKOS = PREFIXES["skos"]
NLI_PERSONS = "http://data.judaicalink.org/datasets/nli-persons"


_IRI_BAD = re.compile(r'[<>"{}|^`\\\s]')


def iri(value):
    """An IRI; characters not allowed in IRIs (from source data given as text) are percent-encoded, as in
    kg-complements."""
    return IRI(_IRI_BAD.sub(lambda m: "%{:02X}".format(ord(m.group(0))), value))


def generate(run):
    records = read_records(run.input("export"))
    viaf_count = Counter(a for _n, r in records for x in r.get("901", []) for a in x.get("a", []))
    t = set()

    def add(s, p, o):
        t.add((iri(s), iri(p), o if isinstance(o, Literal) else iri(o)))

    def lit(text, lang=None):
        return Literal(text, lang=lang)

    counts = Counter()
    iri_of = {}
    index = person_index(records, viaf_count)
    for n, r in records:
        k = kind(r)
        counts[k] += 1
        if k != "subject-heading":
            iri_of[n] = record_iri(n, r, viaf_count)
    for n, r in records:
        s = iri_of.get(n)
        if not s:
            continue
        k = kind(r)
        viaf = [a for x in r.get("901", []) for a in x.get("a", [])]
        if viaf:
            add(s, OWL + "sameAs", "http://viaf.org/viaf/" + viaf[0])
            counts[k + " with VIAF"] += 1
        for f in r.get("010", []):
            for a in sub(f, "a"):
                add(s, OWL + "sameAs", "http://id.loc.gov/authorities/names/" + a.replace(" ", ""))
                counts[k + " with LC"] += 1
        add(s, DCT + "source", NLI_PERSONS)
        if k == "person":
            add(s, RDF_TYPE, FOAF + "Person")
            ns = names(r["100"])
            pref_done = set()
            for text, tag, script in ns:
                key = tag or ""
                if key not in pref_done:
                    add(s, SKOS + "prefLabel", lit(text, tag))
                    pref_done.add(key)
                else:
                    add(s, SKOS + "altLabel", lit(text, tag))
            shown = {x for x, _l, _s in ns}
            for f in r.get("400", []) + r.get("700", []):
                if set(f) & TITLE_CODES and "t" in f:
                    continue
                text = heading(f)
                script = f.get("9", ["lat"])[0]
                if text and text not in shown:
                    shown.add(text)
                    add(s, SKOS + "altLabel", lit(text, SCRIPT_LANG.get(script)))
            birth, death = dates(r)
            if birth:
                add(s, JLO + "birthDate", lit(birth))
            if death:
                add(s, JLO + "deathDate", lit(death))
            for f in r.get("370", []):
                for code, p in (("a", JLO + "birthLocation"), ("b", JLO + "deathLocation")):
                    for v in sub(f, code):
                        add(s, p, lit(clean(v)))
            for f in r.get("374", []):
                for v in sub(f, "a"):
                    add(s, JLO + "occupation", lit(clean(v)))
            for f in r.get("375", []):
                for v in sub(f, "a"):
                    if v.lower() in ("male", "female"):
                        add(s, FOAF + "gender", lit(v.lower()))
            for f in r.get("678", []):
                for v in sub(f, "a") + sub(f, "b"):
                    add(s, SKOS + "note", lit(v))
        else:  # work: name/title heading
            add(s, RDF_TYPE, JLO + "Work")
            for f in r["100"]:
                title = clean(" ".join(v for c in "tnpklmor" for v in sub(f, c)))
                script = f.get("9", ["lat"])[0]
                if title:
                    add(s, DCT + "title", lit(title, SCRIPT_LANG.get(script)))
                    add(s, SKOS + "prefLabel" if script == "lat" or len(r["100"]) == 1 else SKOS + "altLabel",
                        lit(f"{heading(f)}: {title}", SCRIPT_LANG.get(script)))
                for v in sub(f, "f"):
                    add(s, DCT + "date", lit(clean(v).strip("()")))
            creator = named_person(r, index)
            if creator:
                add(s, DCT + "creator", creator)
                counts["work with creator"] += 1
            else:
                for f in r["100"]:
                    add(s, DC + "creator", lit(heading(f), SCRIPT_LANG.get(f.get("9", ["lat"])[0])))
    run.note(f"Records of the export: {dict(sorted(counts.items()))}.")
    run.write_turtle("nli-records.ttl.gz", t)

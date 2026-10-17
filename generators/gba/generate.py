"""gba: persons of the Gidal-Bildarchiv (photo archive of the Steinheim-Institut), from the hand-made table gidal.csv.

The logic of judaicalink-generators `6fce1cd` (original/judaicalink-generators@6fce1cd/gidal/scripts/generator.py),
ported to the framework, reading the CSV with the csv module instead of pandas (an empty field is no value). IRIs
from the name by its `clean_url_string` (the IRIs of 2025-03-21, kept).

Fixes (decision 0024), parameters with the fix as default; with all off the output has the triples of 2025-03-21:
- common_terms: the fields were written in the GND namespace with terms the GND ontology does not have
  (gndo:birthDate, deathDate, occupation, hasPublication, hasAbstract, alternativeName); now jl:birthDate,
  jl:deathDate, jl:occupation, jl:hasPublication, jl:hasAbstract, skos:altLabel.
- dates_as_text: the years were xsd:integer; jl:birthDate and jl:deathDate are the date as written (text).
- relation_links: the relation was the name of another person of the table as text (gndo:relation, not a GND term);
  now gndo:relatedPerson with the IRI of that person.
- whitespace: names and texts as given, with spaces at the ends ("Max Liebermann ") and doubled inside ("Betty  Geb.
  Van Geldern"); now trimmed and single.
- gnd_links: the GND number only as gndo:gndIdentifier; now also owl:sameAs the GND entry (the source states it).
- described_at: no link to the source; now jl:describedAt the archive's page of the entry (by GND number).
- drop_created: dcterms:created was the time of the run, not a fact of the source; left out (off: taken from the
  previous version, which the code cannot make again).
- canonical_forms: the IRIs in canonical form (the GND ontology in https, docs/iri-forms.md).
"""

import csv
import re

from jl import classes
from jl.iris import canonical_triples
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES, Namespace

INPUTS = {"csv": "inputs:gba/gidal-csv-2022-07-08/gidal.csv", "previous": "gba/2025-03-21"}
PARAMS = {"common_terms": True, "dates_as_text": True, "relation_links": True, "whitespace": True, "gnd_links": True,
          "described_at": True, "drop_created": True, "canonical_forms": True}

BASE = "http://data.judaicalink.org/data/gba/"
# the target of the archive's BEACON (http://www.steinheim-institut.de/gidal-bildarchiv/query.html?…) answers 404
DESCRIBED_AT = "https://www.steinheim-institut.de/gba/query.html?text1={0}&kategorie1=GND"

JLO = Namespace(PREFIXES["jl"])
SKOS = Namespace(PREFIXES["skos"])
FOAF = Namespace(PREFIXES["foaf"])
OWL = Namespace(PREFIXES["owl"])
DCTERMS = Namespace(PREFIXES["dcterms"])
GNDO = Namespace("http://d-nb.info/standards/elementset/gnd#")   # as written in 2025; canonical_forms gives https
TYPE = IRI(RDF_TYPE)
CREATED = IRI(DCTERMS.created)


def clean_url_string(string):
    string = string.strip()
    for char in ["'", '"', ',', '<', '>', '|', ' ', '.', '[', ']', '(', ')', '{', '}']:
        string = string.replace(char, '_')
    return string


def subject(name):
    return IRI(BASE + clean_url_string(name))


def generate(run):
    prm = run.params
    with open(run.input("csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    def text(value):
        return re.sub(r"\s+", " ", value).strip() if prm["whitespace"] else value

    by_name = {r["name"].strip(): subject(r["name"]) for r in rows}
    t = []
    for r in rows:
        s = subject(r["name"])
        if r["gnd"]:
            t.append((s, GNDO.gndIdentifier, Literal(r["gnd"])))
            if prm["gnd_links"]:
                t.append((s, OWL.sameAs, IRI("https://d-nb.info/gnd/" + r["gnd"])))
            if prm["described_at"]:
                t.append((s, JLO.describedAt, IRI(DESCRIBED_AT.format(r["gnd"]))))
        if r["type"] == "person":
            t.append((s, TYPE, IRI(classes.PERSON)))
        elif r["type"] == "organisation":
            t.append((s, TYPE, IRI(classes.ORGANISATION)))
        else:
            run.log("unknown type:", r["type"], r["name"])
        t.append((s, FOAF.name, Literal(text(r["name"]))))
        t.append((s, SKOS.prefLabel, Literal(text(r["name"]))))
        for field in ("birthDate", "deathDate"):
            if r[field]:
                o = Literal(r[field].strip()) if prm["dates_as_text"] else Literal(str(int(r[field])), XSD + "integer")
                t.append((s, JLO[field] if prm["common_terms"] else GNDO[field], o))
        for field in ("occupation", "hasPublication"):
            for value in r[field].split(";") if r[field] else []:
                if value.strip():
                    t.append((s, JLO[field] if prm["common_terms"] else GNDO[field], Literal(text(value.strip()))))
        if r["relation"]:
            name = r["relation"].strip()
            if not prm["relation_links"]:
                t.append((s, GNDO.relation, Literal(name)))
            elif name in by_name:
                t.append((s, GNDO.relatedPerson, by_name[name]))
            else:
                run.log("relation not in the table, left out:", r["name"], "->", name)
        if r["alternativeName"]:
            t.append((s, SKOS.altLabel if prm["common_terms"] else GNDO.alternativeName,
                      Literal(text(r["alternativeName"].strip()))))
        if r["hasAbstract"]:
            t.append((s, JLO.hasAbstract if prm["common_terms"] else GNDO.hasAbstract,
                      Literal(text(r["hasAbstract"].strip()))))
    if not prm["drop_created"]:
        t += [(s, p, o) for s, p, o in run.triples("previous") if p == CREATED]

    links = sum(1 for _s, p, _o in t if p == GNDO.relatedPerson)
    run.note(f"{len(rows)} rows; {sum(1 for r in rows if r['gnd'])} with a GND number"
             + (f"; {links} relations linked" if prm["relation_links"] else "") + ".")
    run.write_turtle("gba.ttl.gz", set(canonical_triples(t)) if prm["canonical_forms"] else set(t))

"""hirsch-family: the Hirsch family of Aschaffenburg, from the CSV export of "Jüdisches Leben in Unterfranken".

Transformation only: `CSV-to-RDF.py` of judaicalink-generators `40f7c98` (Maral Dadvar, 2018-10-30; copy in
original/), ported to the framework without changes to its logic. Two things the original left implicit:
the CSV is read as Latin-1 (it was written on Windows), and its header row is skipped (the kept version
2018-10-30 has no triples for it; the original script would have made a person `hirsch/IdNr`).
"""

import csv

from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES, Namespace

INPUTS = {"csv": {
    "sha256": "d7e37b236019a48a422d860c69eea0b391ee8b458a17dbadcd036dd880ff968b", "bytes": 97122,
    "origin": "https://github.com/judaicalink/judaicalink-generators/blob/"
              "40f7c98aa2157f9a533c160f80d678643c1509fd/HirschFamily/input/hirsch_fam_davinci.csv",
    "description": "The Hirsch family of Aschaffenburg from the database \"Jüdisches Leben in Unterfranken\": "
                   "CSV (semicolons, Latin-1, one German header row), one row per person and source (IdNr, name, "
                   "birth and death, biography link, source, source link); the input of CSV-to-RDF.py, "
                   "committed with it by Maral Dadvar (2019-08-05)."}}
PARAMS = {}

JL = Namespace(PREFIXES["jl"])
FOAF = Namespace(PREFIXES["foaf"])
SKOS = Namespace(PREFIXES["skos"])
DC = Namespace(PREFIXES["dc"])


def row_triples(row):
    uri = IRI("http://data.judaicalink.org/data/hirsch/" + row[0])
    t = [(uri, IRI(RDF_TYPE), FOAF.Person)]
    names = row[2].replace("°", "").strip()
    name = names.split(" ", 1)
    if len(name) > 1:
        t.append((uri, SKOS.prefLabel, Literal(name[0] + ", " + name[1])))
    for col, prop in ((3, JL.birthDate), (4, JL.birthLocation), (5, JL.deathDate), (6, JL.deathLocation)):
        if row[col] != "":
            t.append((uri, prop, Literal(row[col])))
    t.append((uri, JL.describedAt, IRI(row[11])))
    t.append((uri, DC.subject, Literal(row[13])))
    return t


def generate(run):
    triples = []
    with open(run.input("csv"), newline="", encoding="latin-1") as f:
        rows = csv.reader(f, delimiter=";")
        header = next(rows)
        run.log("header skipped:", header)
        for row in rows:
            triples += row_triples(row)
    run.write_turtle("hirsch-family.ttl.gz", triples)

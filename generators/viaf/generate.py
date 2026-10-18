"""viaf: the VIAF clusters JudaicaLink uses (decision 0029), made from the yearly VIAF dump.

1. The selection list (viaf-selection.tsv.gz): the selection of the cascade (jl.cascade: one row per VIAF number and
   reason, e.g. the dataset that links it), with the current number: the number itself if the cluster is in the dump,
   empty if it is not. The dump
   states no merged or withdrawn clusters, and a cluster made after the dump is not in it either, so a missing
   number gets no successor and is not marked deprecated.
2. The data (viaf.ttl.gz): every selected cluster of the dump as a record data/viaf/<n>: owl:sameAs
   <https://viaf.org/viaf/<n>> (the canonical form, viaf.org/en/viaf/data); the class of the common layer for
   schema:Person, schema:Organization, schema:Place and schema:CreativeWork (jl.classes); skos:prefLabel the
   preferred names as VIAF gives them (one per source library, with its language tag); skos:altLabel the
   schema:alternateName; jl:birthDate and jl:deathDate as given (schema:birthDate, schema:deathDate); owl:sameAs the
   records of the sources VIAF names (schema:sameAs: GND, LC, Wikidata, ISNI, BnF, …; canonical forms, jl.iris;
   left out: IRIs without a path, which name no record, e.g. http://data.bnf.fr/#foaf:Person for 8,141 clusters);
   owl:differentFrom as given. The source records of the cluster (VIAF's sourceID nodes) and the works of the
   cluster are not taken over.

The dump is read in one pass; its lines are not grouped by cluster, so the triples of the selected clusters are
collected in memory. Lines that are not valid N-Triples are left out and listed in the log.
"""

import csv
import gzip
import re
from collections import defaultdict

from jl import cascade, classes, identifiers
from jl.iris import canonical
from jl.rdf import IRI, RDF_TYPE, Literal, ParseError, parse_ntriples
from jl.turtle import PREFIXES

INPUTS = {"dump": "inputs:viaf/clusters-2024-08-04/viaf-20240804-clusters-rdf.nt.gz",
          "selection": cascade.selection_input("viaf")}   # the selection of the cascade (jl cascade)
PARAMS = {}

JL = "http://data.judaicalink.org/data/viaf/"
CLUSTER = "http://viaf.org/viaf/"
SCHEMA = "http://schema.org/"
JLO, SKOS, OWL = PREFIXES["jl"], PREFIXES["skos"], PREFIXES["owl"]
CLASSES = {SCHEMA + "Person": classes.PERSON, SCHEMA + "Organization": classes.ORGANISATION,
           SCHEMA + "Place": classes.PLACE, SCHEMA + "CreativeWork": classes.WORK}
KEEP = {RDF_TYPE, SKOS + "prefLabel", SCHEMA + "alternateName", SCHEMA + "birthDate", SCHEMA + "deathDate",
        SCHEMA + "sameAs", OWL + "differentFrom"}
SUBJECT = re.compile(r"^<http://viaf\.org/viaf/([0-9]+)> <([^>]+)>")
NO_PATH = re.compile(r"^https?://[^/]+/?(#.*)?$")   # names no record (VIAF: http://data.bnf.fr/#foaf:Person)


def generate(run):
    rows = cascade.selection_rows(run.input("selection"))
    wanted = {i for _s, i, _c, _r, _d in rows}
    run.log(f"selected: {len(wanted):,} VIAF numbers")

    lines = defaultdict(list)
    n = 0
    with gzip.open(run.input("dump"), "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            n += 1
            m = SUBJECT.match(line)
            if m and m.group(1) in wanted and m.group(2) in KEEP:
                lines[m.group(1)].append(line)
    run.log(f"dump: {n:,} lines, {len(lines):,} of the selected clusters")

    t, stats = set(), defaultdict(int)
    for num in sorted(lines):
        rec = IRI(JL + num)
        t.add((rec, IRI(OWL + "sameAs"), IRI(canonical(CLUSTER + num))))
        triples = []
        for line in lines[num]:   # a line that is not valid N-Triples is left out and listed in the log
            try:
                triples.extend(parse_ntriples([line]))
            except ParseError:
                stats["lines that are not valid N-Triples, left out"] += 1
                run.log("not valid N-Triples:", line.rstrip()[:300])
        for _s, p, o in triples:
            if p == RDF_TYPE:
                if o in CLASSES:
                    t.add((rec, IRI(RDF_TYPE), IRI(CLASSES[o])))
            elif p == SKOS + "prefLabel" and isinstance(o, Literal):
                t.add((rec, IRI(SKOS + "prefLabel"), Literal(o.value, None, o.lang)))
            elif p == SCHEMA + "alternateName" and isinstance(o, Literal):
                t.add((rec, IRI(SKOS + "altLabel"), Literal(o.value, None, o.lang)))
            elif p in (SCHEMA + "birthDate", SCHEMA + "deathDate") and isinstance(o, Literal):
                t.add((rec, IRI(JLO + ("birthDate" if p.endswith("birthDate") else "deathDate")), Literal(o.value)))
            elif p == SCHEMA + "sameAs" and not isinstance(o, Literal):
                x = canonical(o)
                if NO_PATH.match(x):
                    stats["links without an identifier left out (e.g. http://data.bnf.fr/#foaf:Person)"] += 1
                    continue
                if identifiers.is_ours(x):
                    stats["links to JudaicaLink left out"] += 1   # never evidence (0029)
                    continue
                t.add((rec, IRI(OWL + "sameAs"), IRI(x)))
            elif p == OWL + "differentFrom" and not isinstance(o, Literal):
                t.add((rec, IRI(OWL + "differentFrom"), IRI(canonical(o))))

    with gzip.open(run.path("viaf-selection.tsv.gz"), "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["source", "identifier", "current", "reason", "detail"])
        for s, num, _c, reason, detail in sorted(rows, key=lambda r: (len(r[1]), r[1], r[3], r[4])):
            w.writerow([s, num, num if num in lines else "", reason, detail])
    missing = len(wanted - set(lines))
    run.note(f"{len(lines):,} clusters of {len(wanted):,} linked VIAF numbers; {missing:,} not in the dump"
             + "".join(f"; {k} {v:,}" for k, v in sorted(stats.items())) + ".")
    run.write_turtle("viaf.ttl.gz", t)

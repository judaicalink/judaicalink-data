"""haskala: a new version made from the version 2019-07-01 with the occupations of the persons of haskala.net added
and empty values dropped (decision 0024).

The 2019 version is the enriched one (GND names, dates and places, added by hand against a local GND); it cannot be
made again, and the regenerated version 2025-03-24 lacks the enrichment. The 2019 enrichment dropped exactly one part
of the haskala.net persons: their occupations (32, under the misspelt property jl:Occupation). They are taken from
Haskala_net.ttl of 2025-03-24 (the same source file; its other triples are in 2019-07-01). Parameters, default on:
- occupations: the occupations as jl:occupation; split_occupations: one value per occupation (the source lists them
  separated by commas, "Rabbiner, Schriftsteller, Arzt"), as the generator commit ba26673 of 2025 did;
- empty_values: 12 empty dates and places dropped.
Everything else is unchanged. With the parameters off, the output has the same triples as 2019-07-01.
"""

from collections import Counter

from jl.rdf import IRI, Literal

INPUTS = {
    "previous": "haskala/2019-07-01",
    "net": "haskala/2025-03-24/Haskala_net.ttl.gz",
}
PARAMS = {"occupations": True, "split_occupations": True, "empty_values": True}

JLO = "http://data.judaicalink.org/ontology/"


def generate(run):
    prm = run.params
    n = Counter()
    out = set()
    persons = set()
    for s, p, o in run.triples("previous", file="Haskala_enriched.ttl.gz"):
        persons.add(s)
        if prm["empty_values"] and isinstance(o, Literal) and not o.value.strip():
            n["empty values"] += 1
            continue
        out.add((s, p, o))
    if prm["occupations"]:
        for s, p, o in run.triples("net"):
            if p != JLO + "Occupation":
                continue
            if s not in persons:
                raise ValueError(f"{s}: a haskala.net person not in 2019-07-01")
            values = o.value.split(",") if prm["split_occupations"] else [o.value]
            values = [v.strip() for v in values if v.strip()]
            n["persons with occupations"] += bool(values)
            n["persons without"] += not values
            for v in values:
                out.add((s, IRI(JLO + "occupation"), Literal(v)))
                n["occupations"] += 1
    for k, c in sorted(n.items()):
        run.log(f"{k}: {c:,}")
    if any(prm.values()):
        run.note(f"{n['occupations']} occupations of {n['persons with occupations']} haskala.net persons added from "
                 f"2025-03-24 ({n['persons without']} without); {n['empty values']} empty values dropped.")
    run.write_turtle("haskala.ttl.gz", out)

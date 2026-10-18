"""The identifiers by which our data reaches Wikidata items (shared by query.py and generate.py).

DATASETS: our datasets and the other authority datasets (jl.authorities.linking_inputs: the stable versions, or the
runs of jl generate --use), and in RUNS the runs of linksets that are no versions yet. collect() lists, per source and identifier,
the datasets that name it as object (jl.identifiers): Wikidata items themselves, and the identifiers Wikidata
states for items (GND, VIAF, LC, GeoNames, ISNI) and English DBpedia resources (an English Wikipedia article).
"""

from collections import defaultdict
from urllib.parse import unquote

from jl import authorities, identifiers

RUNS = {
        "ls-nli-wikidata": "run-20261015T210917Z", "ls-bhr-wikidata": "run-20261015T210838Z",
        "ls-rujen-wikidata": "run-20261016T114653Z"}
DATASETS = authorities.linking_inputs("wikidata", add=RUNS)   # with the other authority datasets (jl.authorities)
# the sources and the Wikidata properties that state them
PROPERTIES = {"gnd": "P227", "viaf": "P214", "lc-names": "P244", "geonames": "P1566", "isni": "P213"}
SOURCES = {"wikidata", "dbpedia", *PROPERTIES}


def collect(triples_of):
    """triples_of: [(dataset, triples)] -> {source: {identifier: {dataset}}}."""
    found = defaultdict(lambda: defaultdict(set))
    for slug, triples in triples_of:
        for _s, p, o in triples:
            if not identifiers.selects(slug, p):   # authority datasets: identity statements only (0029)
                continue
            x = identifiers.identify(o, p)
            if x and x[0] in SOURCES:
                found[x[0]][x[1]].add(slug)
    return found


def isni_value(n):
    """ISNI as Wikidata states it: 16 characters without spaces (checked 2026-10-16)."""
    return n.replace(" ", "")


def article_name(resource):
    """The English Wikipedia title of a DBpedia resource name (as in its IRI)."""
    return unquote(resource).replace("_", " ")

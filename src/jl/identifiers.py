"""The identifiers of external sources in our data (decision 0029): which dataset names which identifier.

identify(term) gives (source, identifier) for an IRI of a known source in any of its forms (jl.iris), for our
records in an authority namespace (data/gnd/<n> is GND n, data/geonames/<n> is GeoNames n), and for a literal of an
identifier property (gndo:gndIdentifier). scan(run, inputs) lists, per source and identifier, the datasets that
name it as object; a subject is a statement about a record, not a link to it.
"""

import re
from collections import defaultdict

from . import iris
from .rdf import BNode, Literal

JL = "http://data.judaicalink.org/data/"
# our records that are the identifier of a source
AUTHORITY_NAMESPACES = [("gnd", re.compile(re.escape(JL) + r"gnd/([0-9]+[0-9X-]*)$")),
                        ("geonames", re.compile(re.escape(JL) + r"geonames/([0-9]+)$")),
                        ("lc-names", re.compile(re.escape(JL) + r"lc/([a-z]+[0-9]+)$")),
                        ("wikidata", re.compile(re.escape(JL) + r"wikidata/(Q[0-9]+)$")),
                        ("viaf", re.compile(re.escape(JL) + r"viaf/([0-9]+)$"))]
# properties whose literal value is an identifier
LITERAL_PROPERTIES = {"http://d-nb.info/standards/elementset/gnd#gndIdentifier": "gnd",
                      "https://d-nb.info/standards/elementset/gnd#gndIdentifier": "gnd"}
# IRI forms that name the same identifier (the LC Real World Object is the person of the authority record)
SAME_IDENTIFIER = {"lc-rwo": "lc-names"}
SYNTAX = {"gnd": re.compile(r"[0-9]+[0-9X-]*$", re.I)}


def normal(source, identifier):
    return identifier.strip().upper() if source == "gnd" else identifier.strip()


def identify(term, predicate=None):
    """(source, identifier) or None."""
    if isinstance(term, Literal):
        source = LITERAL_PROPERTIES.get(predicate)
        if source and SYNTAX[source].match(term.value.strip()):
            return source, normal(source, term.value)
        return None
    if not isinstance(term, str) or isinstance(term, BNode):
        return None
    for source, pattern in AUTHORITY_NAMESPACES:
        m = pattern.match(term)
        if m:
            return source, normal(source, m.group(1))
    for name, pattern, _form, _src in iris.FORMS:
        if name == "judaicalink":
            continue
        m = pattern.match(term)
        if m:
            name = SAME_IDENTIFIER.get(name, name)
            return name, normal(name, m.group(1))
    return None


def scan(run, inputs, sources=None):
    """{source: {identifier: {dataset}}} for the identifiers the inputs name as objects. inputs: {input name:
    "<slug>/<version>"} (e.g. jl.generator.stable_inputs); sources: only these sources."""
    found = defaultdict(lambda: defaultdict(set))
    for name, ref in inputs.items():
        slug = ref.split("/", 1)[0]
        for _s, p, o in run.triples(name):
            x = identify(o, p)
            if x and (sources is None or x[0] in sources):
                found[x[0]][x[1]].add(slug)
    return found


def is_ours(term):
    """An IRI of JudaicaLink (any form): never evidence when it comes from an external source (decision 0029)."""
    return isinstance(term, str) and not isinstance(term, BNode) and iris.kind(term) == "judaicalink"

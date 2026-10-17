"""Canonical forms of the IRIs we link to and of coordinates (docs/iri-forms.md).

The same thing can be written in several forms (http or https, with or without a final slash, the address of the
description document instead of the thing). canonical(iri) gives the one form we write; it changes only the
spelling of an identifier, never which identifier it is (deprecated identifiers are data: dcterms:isReplacedBy,
owl:deprecated, decision 0029). Generators write external IRIs through canonical(); every run reports the IRIs of
its output that are not in canonical form (Run.write_turtle, jl generate).
"""

import re

# (name, pattern of the variants, the canonical form, where the source states it)
FORMS = [
    ("judaicalink", re.compile(r"^https?://data\.judaicalink\.org/(.+)$"),
     "http://data.judaicalink.org/{0}", "our own IRIs (decision 0002)"),
    ("gnd", re.compile(r"^https?://d-nb\.info/gnd/([0-9]+[0-9X-]*)(?:/about(?:/[a-z]+)?)?/?$", re.I),
     "https://d-nb.info/gnd/{0}", "the GND Linked Data Service dumps (data.dnb.de/opendata)"),
    ("viaf", re.compile(r"^https?://(?:www\.)?viaf\.org/viaf/([0-9]+)/?$"),
     "https://viaf.org/viaf/{0}", "VIAF, viaf.org/en/viaf/data: 'The canonical structure of a VIAF URI'"),
    ("wikidata", re.compile(r"^https?://(?:www\.)?wikidata\.org/entity/([QPL][0-9]+)$"),
     "http://www.wikidata.org/entity/{0}", "the concept URIs of the Wikidata RDF dumps"),
    ("geonames", re.compile(r"^https?://(?:sws\.|www\.)?geonames\.org/([0-9]+)(?:/|/about\.rdf)?$"),
     "https://sws.geonames.org/{0}/", "GeoNames RDF (rdf:about of sws.geonames.org/<id>/about.rdf)"),
    ("lc-names", re.compile(r"^https?://id\.loc\.gov/authorities/names/([a-z]+[0-9]+)(?:\.html|\.rdf|\.json)?$"),
     "http://id.loc.gov/authorities/names/{0}", "the LC Name Authority File dumps (id.loc.gov/download)"),
    ("lc-rwo", re.compile(r"^https?://id\.loc\.gov/rwo/agents/([a-z]+[0-9]+)(?:\.html|\.rdf|\.json)?$"),
     "http://id.loc.gov/rwo/agents/{0}", "the LC dumps: the Real World Object (the person) of a name authority"),
    ("isni", re.compile(r"^https?://(?:www\.)?isni\.org/(?:isni/)?([0-9]{15}[0-9X])$"),
     "https://isni.org/isni/{0}", "ISNI (isni.org)"),
    ("dbpedia", re.compile(r"^https?://dbpedia\.org/resource/(.+)$"),
     "http://dbpedia.org/resource/{0}", "the DBpedia resource IRIs"),
    ("tgn", re.compile(r"^https?://vocab\.getty\.edu/tgn/([0-9]+)(?:-place)?$"),
     "http://vocab.getty.edu/tgn/{0}", "the Getty vocabularies (vocab.getty.edu)"),
]


WKT = "http://www.opengis.net/ont/geosparql#wktLiteral"
AS_WKT = "http://www.opengis.net/ont/geosparql#asWKT"
_POINT = re.compile(r"^\s*POINT\s*\(\s*([+-]?[0-9]*\.?[0-9]+)\s+([+-]?[0-9]*\.?[0-9]+)\s*\)\s*$", re.I)


def _number(x):
    sign = "-" if x.startswith("-") else ""
    x = x.lstrip("+-").lstrip("0")
    return sign + ("0" + x if not x or x.startswith(".") else x)


def canonical_wkt(value):
    """The canonical form of a point: "POINT(<lon> <lat>)" (GeoSPARQL; the numbers as given, without "+" and
    leading zeros); other values unchanged. Written with the datatype geosparql:wktLiteral."""
    m = _POINT.match(value)
    return f"POINT({_number(m.group(1))} {_number(m.group(2))})" if m else value


# vocabulary namespaces in the form their publisher uses (old prefix, canonical prefix, where the publisher states it)
VOCABULARIES = [
    ("http://d-nb.info/standards/elementset/gnd#", "https://d-nb.info/standards/elementset/gnd#", "the GND ontology"),
    ("http://www.geonames.org/ontology#", "https://www.geonames.org/ontology#", "the GeoNames ontology"),
    ("http://www.loc.gov/standards/mads/rdf/v1#", "http://www.loc.gov/mads/rdf/v1#", "MADS/RDF"),
]


def canonical(iri):
    """The canonical form of an IRI we know (identifiers and vocabulary terms), else the IRI unchanged."""
    s = str(iri)
    for old, new, _source in VOCABULARIES:
        if s.startswith(old):
            return new + s[len(old):]
    for _name, pattern, form, _source in FORMS:
        m = pattern.match(s)
        if m:
            return form.format(*m.groups())
    return s


def canonical_triples(triples):
    """The triples with every known IRI (subject and object) and every point (geosparql:asWKT) in canonical form."""
    from .rdf import IRI, BNode, Literal
    for s, p, o in triples:
        if isinstance(o, Literal):
            if p == AS_WKT:
                o = Literal(canonical_wkt(o.value), WKT, None)
        elif not isinstance(o, BNode):
            o = IRI(canonical(o))
        yield (s if isinstance(s, BNode) else IRI(canonical(s))), IRI(canonical(p)), o


# vocabularies we do not write, with the namespace to use instead (docs/iri-forms.md); a run that writes one fails
NOT_USED = [
    ("http://purl.org/dc/elements/1.1/", "http://purl.org/dc/terms/", "DC Elements: dcterms: only (decision 0030)"),
]


def instead(iri):
    """For a term of a vocabulary we do not write, the term to use instead, else None."""
    s = str(iri)
    for ns, new, _reason in NOT_USED:
        if s.startswith(ns):
            return new + s[len(ns):]
    return None


def kind(iri):
    for old, _new, _source in VOCABULARIES:
        if str(iri).startswith(old):
            return "vocabulary"
    for name, pattern, _form, _source in FORMS:
        if pattern.match(str(iri)):
            return name
    return None


class Check:
    """Counts the IRIs that are not in canonical form, by kind, with a few examples, and the properties and classes
    of vocabularies we do not write (not_used: {term: count})."""

    def __init__(self):
        self.counts, self.examples, self.not_used = {}, {}, {}

    def watch(self, triples):
        """Pass the triples through and note the subjects, predicates and IRI objects that are not canonical."""
        from .rdf import RDF_TYPE, BNode, Literal
        for t in triples:
            o = t[2]
            for term in (t[1], o if t[1] == RDF_TYPE and not isinstance(o, Literal) else None):
                if term is not None and instead(term):
                    self.not_used[str(term)] = self.not_used.get(str(term), 0) + 1
            if isinstance(o, Literal) and t[1] == AS_WKT and (canonical_wkt(o.value) != o.value or o.datatype != WKT):
                self.counts["wkt"] = self.counts.get("wkt", 0) + 1
                ex = self.examples.setdefault("wkt", [])
                if len(ex) < 3:
                    ex.append(f"{o.value} ({o.datatype or 'no datatype'})")
            for x in (t[0], t[1], t[2]):
                if not isinstance(x, str) or isinstance(x, BNode):
                    continue
                c = canonical(x)
                if c != x:
                    k = kind(x)
                    self.counts[k] = self.counts.get(k, 0) + 1
                    ex = self.examples.setdefault(k, [])
                    if len(ex) < 3 and x not in ex:
                        ex.append(x)
            yield t

    def summary(self):
        return {k: {"count": n, "examples": self.examples[k]} for k, n in sorted(self.counts.items())}
